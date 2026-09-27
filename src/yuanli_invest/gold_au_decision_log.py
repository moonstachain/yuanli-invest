"""Local, append-only 08:30 AU decision evidence; never order authority.

Every timely invocation stores the *whole* live-snapshot result: actionable
entry, non-actionable research signal, or explicit SKIPPED reason. The source
request and complete result are separately hashed. Local SQLite and the host
clock cannot prove independent publication time; the readback is deliberately
incompatible with the gateway's externally attested signal registry.
"""

from __future__ import annotations

from contextlib import closing
from datetime import date, datetime, time, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
from typing import Any, Callable, Mapping
from zoneinfo import ZoneInfo

from .gold_au_live_snapshot import prepare_live_snapshot
from .receipts import canonical_bytes, canonical_hash


SHANGHAI = ZoneInfo("Asia/Shanghai")
SCHEMA_VERSION = "gold-au-decision-log.v1"
LOCAL_KIND = "LOCAL_CANDIDATE"
ZERO_HASH = "sha256:" + "0" * 64
MAX_RECORD_BYTES = 20_000_000
RECORD_KEYS = frozenset({
    "schema_version", "log_id", "record_id", "decision_date", "decision_at",
    "started_at", "recorded_at", "request", "request_sha256", "snapshot", "snapshot_sha256",
    "outcome_status", "outcome_reason", "action_block", "actionable_entry",
})


class DecisionLogDenied(ValueError):
    """Fail-closed decision-log error with a stable, non-sensitive code."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _instant(value: Any, field: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise DecisionLogDenied("INVALID_" + field.upper())
    return value.astimezone(timezone.utc)


def _canonical(value: Any, field: str) -> bytes:
    try:
        raw = canonical_bytes(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise DecisionLogDenied("INVALID_" + field.upper()) from exc
    if len(raw) > MAX_RECORD_BYTES:
        raise DecisionLogDenied("OVERSIZED_" + field.upper())
    return raw


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _day(value: Any) -> date:
    if not isinstance(value, str):
        raise DecisionLogDenied("INVALID_DECISION_DATE")
    try:
        day = date.fromisoformat(value)
    except ValueError as exc:
        raise DecisionLogDenied("INVALID_DECISION_DATE") from exc
    if day.isoformat() != value or day.weekday() >= 5:
        raise DecisionLogDenied("INVALID_DECISION_DATE")
    return day


def _decision(day: date) -> datetime:
    return datetime.combine(day, time(8, 30), SHANGHAI).astimezone(timezone.utc)


def _within_minute(value: datetime, decision: datetime) -> bool:
    return decision <= value < decision.replace(minute=31)


def _result(snapshot: Mapping[str, Any], decision: datetime) -> tuple[str, str, str | None, bool]:
    if snapshot.get("schema_version") != "gold-au-live-snapshot.v1" or snapshot.get("broker_action_authorized") is not False:
        raise DecisionLogDenied("INVALID_SNAPSHOT_RESULT")
    status = snapshot.get("status")
    if status == "SKIPPED":
        reason = snapshot.get("reason")
        if not isinstance(reason, str) or not reason:
            raise DecisionLogDenied("SKIP_REASON_MISSING")
        return status, reason, None, False
    if status != "READY_STRICT_RESEARCH_SIGNAL":
        raise DecisionLogDenied("INCOMPLETE_SNAPSHOT_RESULT")
    signal = snapshot.get("signal")
    dataset = snapshot.get("dataset")
    if (not isinstance(signal, Mapping) or not isinstance(dataset, Mapping)
            or snapshot.get("decision_at") != decision.isoformat()
            or snapshot.get("as_of") != decision.isoformat()
            or signal.get("as_of") != decision.isoformat()
            or signal.get("pit_mode") != "strict"
            or signal.get("broker_order_authorized") is not False):
        raise DecisionLogDenied("READY_SNAPSHOT_MISMATCH")
    if snapshot.get("dataset_sha256") != canonical_hash(dataset):
        raise DecisionLogDenied("DATASET_HASH_MISMATCH")
    reason = signal.get("reason")
    if not isinstance(reason, str) or not reason or type(signal.get("actionable_entry")) is not bool:
        raise DecisionLogDenied("SIGNAL_RESULT_INCOMPLETE")
    block = signal.get("action_block")
    if block is not None and (not isinstance(block, str) or not block):
        raise DecisionLogDenied("INVALID_ACTION_BLOCK")
    return status, reason, block, signal["actionable_entry"]


class LocalDecisionLog:
    """One decision per Shanghai date, even when signal is skipped or flat."""

    def __init__(self, path: str | Path, *, log_id: str = "GOLD2-AU-0830-LOCAL",
                 clock: Callable[[], datetime] | None = None):
        self.path = Path(path)
        self.log_id = log_id
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        if (not self.path.is_absolute() or not self.path.parent.is_dir()
                or self.path.is_symlink() or not isinstance(log_id, str) or not log_id.strip()):
            raise DecisionLogDenied("INVALID_LOG_PATH_OR_ID")
        if not self.path.exists():
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                pass
            else:
                os.close(fd)
        file_stat = self.path.stat()
        if (self.path.is_symlink() or not stat.S_ISREG(file_stat.st_mode)
                or stat.S_IMODE(file_stat.st_mode) != 0o600
                or file_stat.st_uid != os.getuid()):
            raise DecisionLogDenied("INSECURE_LOG_PATH")
        with closing(self._connect()) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS decision_records ("
                         "seq INTEGER PRIMARY KEY, decision_date TEXT NOT NULL UNIQUE, "
                         "record_id TEXT NOT NULL UNIQUE, record_json TEXT NOT NULL, "
                         "record_sha256 TEXT NOT NULL, previous_root_sha256 TEXT NOT NULL, "
                         "root_sha256 TEXT NOT NULL, committed_at TEXT NOT NULL)")
            conn.execute("CREATE TRIGGER IF NOT EXISTS decision_records_no_update "
                         "BEFORE UPDATE ON decision_records BEGIN SELECT RAISE(ABORT, 'append_only'); END")
            conn.execute("CREATE TRIGGER IF NOT EXISTS decision_records_no_delete "
                         "BEFORE DELETE ON decision_records BEGIN SELECT RAISE(ABORT, 'append_only'); END")
        self.verify_chain()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _now(self) -> datetime:
        return _instant(self.clock(), "host_clock")

    @staticmethod
    def _rows(conn: sqlite3.Connection) -> list[tuple[Any, ...]]:
        return conn.execute("SELECT seq, decision_date, record_id, record_json, record_sha256, "
                            "previous_root_sha256, root_sha256, committed_at "
                            "FROM decision_records ORDER BY seq").fetchall()

    @staticmethod
    def _verify_rows(rows: list[tuple[Any, ...]]) -> str:
        previous = ZERO_HASH
        for expected_seq, row in enumerate(rows, 1):
            seq, decision_date, record_id, encoded, record_hash, prior, root, committed_at = row
            if seq != expected_seq or prior != previous:
                raise DecisionLogDenied("DECISION_CHAIN_BROKEN")
            try:
                material = json.loads(encoded)
            except (TypeError, ValueError) as exc:
                raise DecisionLogDenied("DECISION_RECORD_CORRUPT") from exc
            if (not isinstance(material, dict) or set(material) != RECORD_KEYS
                    or _canonical(material, "record").decode("utf-8") != encoded
                    or material["record_id"] != record_id
                    or material["decision_date"] != decision_date
                    or _digest(material) != record_hash
                    or _digest(material["request"]) != material["request_sha256"]
                    or _digest(material["snapshot"]) != material["snapshot_sha256"]):
                raise DecisionLogDenied("DECISION_RECORD_CORRUPT")
            day = _day(decision_date)
            decision = _decision(day)
            try:
                started = _instant(datetime.fromisoformat(material["started_at"]), "started_at")
                recorded = _instant(datetime.fromisoformat(material["recorded_at"]), "recorded_at")
                committed = _instant(datetime.fromisoformat(committed_at), "committed_at")
            except (TypeError, ValueError, KeyError) as exc:
                raise DecisionLogDenied("DECISION_TIME_INVALID") from exc
            if (material["decision_at"] != decision.isoformat()
                    or not _within_minute(started, decision)
                    or not _within_minute(recorded, decision)
                    or not _within_minute(committed, decision)
                    or not started <= recorded <= committed):
                raise DecisionLogDenied("DECISION_TIME_INVALID")
            status, reason, block, actionable = _result(material["snapshot"], decision)
            if (material["outcome_status"] != status or material["outcome_reason"] != reason
                    or material["action_block"] != block or material["actionable_entry"] is not actionable):
                raise DecisionLogDenied("DECISION_RECORD_CORRUPT")
            expected_root = _digest({"seq": seq, "previous_root_sha256": prior,
                                     "record_sha256": record_hash, "committed_at": committed_at})
            if root != expected_root:
                raise DecisionLogDenied("DECISION_CHAIN_BROKEN")
            previous = root
        return previous

    @staticmethod
    def _verify_triggers(conn: sqlite3.Connection) -> None:
        names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='trigger' "
                                               "AND tbl_name='decision_records'")}
        if not {"decision_records_no_update", "decision_records_no_delete"} <= names:
            raise DecisionLogDenied("APPEND_ONLY_TRIGGERS_MISSING")

    def verify_chain(self) -> dict[str, Any]:
        with closing(self._connect()) as conn:
            if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise DecisionLogDenied("DECISION_SQLITE_CORRUPT")
            self._verify_triggers(conn)
            rows = self._rows(conn)
            root = self._verify_rows(rows)
        return {"record_count": len(rows), "root_sha256": root,
                "authenticity": "LOCAL_CANDIDATE_NO_EXTERNAL_TIME_ANCHOR"}

    def capture(self, request: Mapping[str, Any]) -> dict[str, Any]:
        """Compute and commit the complete 08:30 result atomically, or fail closed."""
        if not isinstance(request, Mapping):
            raise DecisionLogDenied("INVALID_REQUEST")
        started = self._now()
        day = _day(request.get("decision_date"))
        decision = _decision(day)
        if not _within_minute(started, decision):
            raise DecisionLogDenied("OUTSIDE_0830_DECISION_MINUTE")
        request_copy = json.loads(_canonical(dict(request), "request"))
        try:
            snapshot = prepare_live_snapshot(request_copy, as_of=decision)
        except Exception as exc:
            raise DecisionLogDenied("SNAPSHOT_EVALUATION_FAILED") from exc
        if not isinstance(snapshot, Mapping):
            raise DecisionLogDenied("INVALID_SNAPSHOT_RESULT")
        snapshot_copy = json.loads(_canonical(dict(snapshot), "snapshot"))
        status, reason, block, actionable = _result(snapshot_copy, decision)
        after_snapshot = self._now()
        if not _within_minute(after_snapshot, decision) or after_snapshot < started:
            raise DecisionLogDenied("LATE_SNAPSHOT_RESULT")
        request_hash = _digest(request_copy)
        snapshot_hash = _digest(snapshot_copy)
        record_id = "GOLD2-AU-DEC-" + hashlib.sha256(
            (self.log_id + "|" + day.isoformat() + "|" + request_hash + "|" + snapshot_hash).encode("utf-8")
        ).hexdigest()[:24].upper()
        record = {"schema_version": SCHEMA_VERSION, "log_id": self.log_id,
                  "record_id": record_id, "decision_date": day.isoformat(),
                  "decision_at": decision.isoformat(), "started_at": started.isoformat(),
                  "recorded_at": after_snapshot.isoformat(),
                  "request": request_copy, "request_sha256": request_hash,
                  "snapshot": snapshot_copy, "snapshot_sha256": snapshot_hash,
                  "outcome_status": status, "outcome_reason": reason,
                  "action_block": block, "actionable_entry": actionable}
        encoded = _canonical(record, "record").decode("utf-8")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._verify_triggers(conn)
            rows = self._rows(conn)
            prior = self._verify_rows(rows)
            seq = len(rows) + 1
            record_hash = _digest(record)
            committed = self._now()
            if not _within_minute(committed, decision) or committed < after_snapshot:
                raise DecisionLogDenied("LATE_DECISION_COMMIT")
            root = _digest({"seq": seq, "previous_root_sha256": prior,
                            "record_sha256": record_hash, "committed_at": committed.isoformat()})
            conn.execute("INSERT INTO decision_records VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         (seq, day.isoformat(), record_id, encoded, record_hash, prior, root,
                          committed.isoformat()))
            if not _within_minute(self._now(), decision):
                raise DecisionLogDenied("LATE_DECISION_COMMIT")
            conn.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise DecisionLogDenied("DUPLICATE_DECISION_DATE") from exc
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()
        return {"status": LOCAL_KIND, "record_id": record_id,
                "decision_date": day.isoformat(), "outcome_status": status,
                "outcome_reason": reason, "actionable_entry": actionable,
                "record_sha256": record_hash, "root_sha256": root,
                "external_anchor_required": True, "broker_action_authorized": False}

    def local_readback(self, decision_date: str) -> dict[str, Any]:
        """Read full hash-checked local evidence; explicitly unfit for orders."""
        day = _day(decision_date)
        with closing(self._connect()) as conn:
            self._verify_triggers(conn)
            rows = self._rows(conn)
            self._verify_rows(rows)
        for row in rows:
            if row[1] == day.isoformat():
                return {"status": LOCAL_KIND, "source": "local_gold_au_decision_log",
                        "registry_kind": LOCAL_KIND, "append_only_verified": False,
                        "independent_readback_verified": False,
                        "record": json.loads(row[3]), "record_sha256": row[4],
                        "root_sha256": row[6], "external_anchor_required": True,
                        "broker_action_authorized": False}
        raise DecisionLogDenied("UNKNOWN_DECISION_DATE")
