"""Durable 08:30 GOLD2 AU signal preregistration candidate.

This local SQLite file is useful for atomic deduplication and audit, but is
*not* an independent timestamp authority.  A gateway-valid readback is only
available through an injected, separately operated anchor/host-attestation
verifier which proves the exact record/root arrived during the 08:30 minute.
Neither this module nor its local file authorizes a paper order.
"""

from __future__ import annotations

from contextlib import closing
from datetime import date, datetime, time, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
from typing import Any, Callable, Mapping

from .gold_au_forward_settlement import _validate_decision
from .gold_au_strategy import DEFAULT_CONFIG, replay_frozen_signal
from .gold_paper import SHANGHAI
from .receipts import canonical_bytes


SCHEMA_VERSION = "gold-au-signal-registration.v1"
LOCAL_KIND = "LOCAL_CANDIDATE"
ANCHOR_STATUS = "VERIFIED_EXTERNAL_TIME_AND_INCLUSION"
RECORD_FIELDS = (
    "registry_id", "record_id", "source_ref", "recorded_at", "decision_at",
    "signal_id", "signal_sha256", "frozen_dataset_sha256", "parameters_sha256",
    "forward_decision_id", "forward_decision_sha256", "outcome_contracts",
)
SHA = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")


class RegistryDenied(ValueError):
    """Fail-closed reason without exposing private market or account data."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _instant(value: Any, field: str) -> datetime:
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str):
        try:
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise RegistryDenied("INVALID_" + field.upper()) from exc
    else:
        raise RegistryDenied("INVALID_" + field.upper())
    if result.tzinfo is None or result.utcoffset() is None:
        raise RegistryDenied("NAIVE_" + field.upper())
    return result.astimezone(timezone.utc)


def _identity(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise RegistryDenied("INVALID_" + field.upper())
    return value


def _hash(value: Any, field: str) -> str:
    if not isinstance(value, str) or SHA.fullmatch(value) is None:
        raise RegistryDenied("INVALID_" + field.upper())
    return value


def _in_decision_minute(instant: datetime, decision: datetime) -> bool:
    local = instant.astimezone(SHANGHAI)
    decided = decision.astimezone(SHANGHAI)
    return (local.date() == decided.date() and time(8, 30) <= local.time() < time(8, 31)
            and instant >= decision)


def _calendar_days(calendar: Mapping[str, Any], decision: datetime,
                   signal: Mapping[str, Any]) -> list[date]:
    if (calendar.get("source") != "SHFE_OFFICIAL_CALENDAR"
            or calendar.get("verified") is not True
            or calendar.get("exchange") != "SHFE"
            or calendar.get("source_ref") != signal.get("exchange_calendar_ref")):
        raise RegistryDenied("UNVERIFIED_EXCHANGE_CALENDAR")
    _hash(calendar.get("raw_sha256"), "calendar_hash")
    if (_instant(calendar.get("published_at"), "calendar_published_at") > decision
            or _instant(calendar.get("retrieved_at"), "calendar_retrieved_at") > decision):
        raise RegistryDenied("CALENDAR_NOT_KNOWN_AT_DECISION")
    raw = calendar.get("sessions")
    if not isinstance(raw, list):
        raise RegistryDenied("MISSING_EXCHANGE_SESSIONS")
    try:
        days = [date.fromisoformat(value) for value in raw]
    except (TypeError, ValueError) as exc:
        raise RegistryDenied("INVALID_EXCHANGE_SESSIONS") from exc
    if days != sorted(set(days)) or any(day.weekday() >= 5 for day in days):
        raise RegistryDenied("INVALID_EXCHANGE_SESSIONS")
    today = decision.astimezone(SHANGHAI).date()
    if today not in days or days.index(today) + 20 >= len(days):
        raise RegistryDenied("MISSING_20_FUTURE_SESSIONS")
    return days


def _frozen_input(dataset: Mapping[str, Any], days: list[date], decision: datetime) -> None:
    today = decision.astimezone(SHANGHAI).date()
    raw_sessions = dataset.get("exchange_sessions")
    if not isinstance(raw_sessions, list):
        raise RegistryDenied("DATASET_CALENDAR_MISSING")
    try:
        input_days = [date.fromisoformat(value) for value in raw_sessions]
    except (TypeError, ValueError) as exc:
        raise RegistryDenied("DATASET_CALENDAR_MISMATCH") from exc
    if (input_days != sorted(set(input_days)) or not input_days or input_days[-1] != today
            or input_days != [day for day in days if input_days[0] <= day <= today]):
        raise RegistryDenied("DATASET_CALENDAR_MISMATCH")
    bars = dataset.get("bars")
    observations = dataset.get("observations")
    if not isinstance(bars, list) or not isinstance(observations, list):
        raise RegistryDenied("DATASET_SHAPE")
    bar_days: set[date] = set()
    for row in bars:
        if not isinstance(row, Mapping):
            raise RegistryDenied("DATASET_SHAPE")
        try:
            bar_day = date.fromisoformat(row.get("date"))
        except (TypeError, ValueError) as exc:
            raise RegistryDenied("DATASET_SHAPE") from exc
        if bar_day not in input_days or bar_day >= today:
            raise RegistryDenied("POSTDECISION_BAR")
        bar_days.add(bar_day)
        for field in ("first_published_at", "retrieved_at", "available_at"):
            if _instant(row.get(field), "bar_" + field) > decision:
                raise RegistryDenied("POSTDECISION_INPUT")
    minimum = DEFAULT_CONFIG["atr_lookback"] + DEFAULT_CONFIG["volatility_reference_days"] + 1
    base = days.index(today)
    if base < minimum or any(day not in bar_days for day in days[base - minimum:base]):
        raise RegistryDenied("MISSING_PREREQUISITE_BARS")
    for row in observations:
        if not isinstance(row, Mapping):
            raise RegistryDenied("DATASET_SHAPE")
        for field in ("released_at", "retrieved_at", "available_at"):
            if _instant(row.get(field), "observation_" + field) > decision:
                raise RegistryDenied("POSTDECISION_INPUT")


def _material(*, registry_id: str, source_ref: str, signal: Mapping[str, Any],
              dataset: Mapping[str, Any], forward_decision: Mapping[str, Any],
              days: list[date], recorded_at: datetime) -> dict[str, Any]:
    decision = _instant(signal.get("as_of"), "decision_at")
    local = decision.astimezone(SHANGHAI)
    if local.time() != time(8, 30) or local.weekday() >= 5:
        raise RegistryDenied("DECISION_NOT_0830_SESSION")
    if not _in_decision_minute(recorded_at, decision):
        raise RegistryDenied("LATE_SIGNAL_REGISTRATION")
    if (signal.get("pit_mode") != "strict" or signal.get("entry") is not True
            or signal.get("actionable_entry") is not True):
        raise RegistryDenied("NONACTIONABLE_SIGNAL")
    signal_id = _hash(signal.get("signal_id"), "signal_id")
    _frozen_input(dataset, days, decision)
    try:
        replay = replay_frozen_signal(dataset, local.date().isoformat())
    except (TypeError, ValueError) as exc:
        raise RegistryDenied("SIGNAL_REPLAY_FAILED") from exc
    if dict(signal) != replay:
        raise RegistryDenied("SIGNAL_REPLAY_MISMATCH")
    try:
        _validate_decision(forward_decision)
    except (TypeError, ValueError) as exc:
        raise RegistryDenied("INVALID_FORWARD_DECISION") from exc
    parameter_hash = _digest(DEFAULT_CONFIG)
    if (forward_decision.get("strategy_version") != DEFAULT_CONFIG["schema_version"]
            or forward_decision.get("baseline_id") != "CASH"
            or forward_decision.get("decision_at") != signal["as_of"]
            or forward_decision.get("signal_id") != signal_id
            or forward_decision.get("contract") != signal.get("contract")
            or forward_decision.get("evidence_sha256") != signal.get("evidence_sha256")
            or forward_decision.get("parameters_sha256") != parameter_hash.removeprefix("sha256:")):
        raise RegistryDenied("FORWARD_DECISION_SIGNAL_MISMATCH")
    decision_id = _identity(forward_decision.get("decision_id"), "forward_decision_id")
    decision_hash = _digest(dict(forward_decision))
    record_id = "GOLD2-AU-SIGREG-" + hashlib.sha256((signal["as_of"] + "|" + signal_id).encode()).hexdigest()[:24].upper()
    base = days.index(local.date())
    contracts = []
    for horizon in (5, 20):
        session_date = days[base + horizon].isoformat()
        contract_id = "GOLD2-AU-OUT-" + hashlib.sha256(
            (decision_id + "|" + decision_hash + "|" + str(horizon) + "|" + session_date).encode()
        ).hexdigest()[:24].upper()
        contracts.append({"horizon_trading_days": horizon, "session_date": session_date,
                          "decision_id": decision_id, "outcome_contract_id": contract_id})
    return {
        "registry_id": registry_id, "record_id": record_id, "source_ref": source_ref,
        "recorded_at": recorded_at.astimezone(SHANGHAI).replace(microsecond=0).isoformat(),
        "decision_at": signal["as_of"], "signal_id": signal_id,
        "signal_sha256": _digest(dict(signal)),
        "frozen_dataset_sha256": _digest(dict(dataset)),
        "parameters_sha256": parameter_hash,
        "forward_decision_id": decision_id,
        "forward_decision_sha256": decision_hash,
        "outcome_contracts": contracts,
    }


class LocalSignalRegistry:
    """Single-writer-per-decision SQLite candidate with an inspected hash chain."""

    def __init__(self, path: str | Path, *, registry_id: str = "GOLD2-AU-PREREG-LOCAL",
                 clock: Callable[[], datetime] | None = None):
        self.path = Path(path)
        self.registry_id = _identity(registry_id, "registry_id")
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        if not self.path.is_absolute() or not self.path.parent.is_dir() or self.path.is_symlink():
            raise RegistryDenied("INVALID_REGISTRY_PATH")
        if not self.path.exists():
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                pass
            else:
                os.close(fd)
        if self.path.is_symlink() or (self.path.stat().st_mode & 0o077):
            raise RegistryDenied("INSECURE_REGISTRY_PATH")
        with closing(self._connect()) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS signal_records ("
                         "seq INTEGER PRIMARY KEY, decision_at TEXT NOT NULL UNIQUE, "
                         "signal_id TEXT NOT NULL UNIQUE, record_id TEXT NOT NULL UNIQUE, "
                         "record_json TEXT NOT NULL, raw_sha256 TEXT NOT NULL, "
                         "previous_root_sha256 TEXT NOT NULL, registry_root_sha256 TEXT NOT NULL, "
                         "committed_at TEXT NOT NULL)")
            conn.execute("CREATE TRIGGER IF NOT EXISTS signal_records_no_update "
                         "BEFORE UPDATE ON signal_records BEGIN SELECT RAISE(ABORT, 'append_only'); END")
            conn.execute("CREATE TRIGGER IF NOT EXISTS signal_records_no_delete "
                         "BEFORE DELETE ON signal_records BEGIN SELECT RAISE(ABORT, 'append_only'); END")
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
        return conn.execute("SELECT seq, decision_at, signal_id, record_id, record_json, "
                            "raw_sha256, previous_root_sha256, registry_root_sha256, committed_at "
                            "FROM signal_records ORDER BY seq").fetchall()

    @staticmethod
    def _verify_rows(rows: list[tuple[Any, ...]]) -> str:
        previous = "sha256:" + "0" * 64
        for expected_seq, row in enumerate(rows, 1):
            seq, decision_at, signal_id, record_id, encoded, raw_hash, prior, root, committed_at = row
            if seq != expected_seq or prior != previous:
                raise RegistryDenied("REGISTRY_HASH_CHAIN_BROKEN")
            try:
                material = json.loads(encoded)
            except (TypeError, ValueError) as exc:
                raise RegistryDenied("REGISTRY_RECORD_CORRUPT") from exc
            if (set(material) != set(RECORD_FIELDS) or encoded != canonical_bytes(material).decode("utf-8")
                    or material["decision_at"] != decision_at
                    or material["signal_id"] != signal_id
                    or material["record_id"] != record_id
                    or _digest(material) != raw_hash):
                raise RegistryDenied("REGISTRY_RECORD_CORRUPT")
            expected_root = _digest({"seq": seq, "previous_root_sha256": prior,
                                     "record_sha256": raw_hash})
            if root != expected_root:
                raise RegistryDenied("REGISTRY_HASH_CHAIN_BROKEN")
            if not _in_decision_minute(_instant(committed_at, "committed_at"),
                                       _instant(decision_at, "decision_at")):
                raise RegistryDenied("REGISTRY_LATE_COMMIT")
            previous = root
        return previous

    def verify_chain(self) -> dict[str, Any]:
        with closing(self._connect()) as conn:
            if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise RegistryDenied("REGISTRY_SQLITE_CORRUPT")
            rows = self._rows(conn)
            root = self._verify_rows(rows)
        return {"record_count": len(rows), "registry_root_sha256": root,
                "authenticity": "LOCAL_CANDIDATE_NEEDS_EXTERNAL_ANCHOR"}

    def register(self, *, signal: Mapping[str, Any], frozen_dataset: Mapping[str, Any],
                 forward_decision: Mapping[str, Any], exchange_calendar: Mapping[str, Any],
                 source_ref: str = "LOCAL_SQLITE_PREREGISTRATION_CANDIDATE") -> dict[str, Any]:
        """Commit one 08:30 signal and both outcome IDs; never return an order grant."""
        if any(not isinstance(value, Mapping) for value in
               (signal, frozen_dataset, forward_decision, exchange_calendar)):
            raise RegistryDenied("INVALID_REGISTRATION_INPUT")
        recorded = self._now()
        decision = _instant(signal.get("as_of"), "decision_at")
        if not _in_decision_minute(recorded, decision):
            raise RegistryDenied("LATE_SIGNAL_REGISTRATION")
        days = _calendar_days(exchange_calendar, decision, signal)
        material = _material(registry_id=self.registry_id, source_ref=_identity(source_ref, "source_ref"),
                             signal=signal, dataset=frozen_dataset, forward_decision=forward_decision,
                             days=days, recorded_at=recorded)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            rows = self._rows(conn)
            previous = self._verify_rows(rows)
            seq = len(rows) + 1
            raw_hash = _digest(material)
            root = _digest({"seq": seq, "previous_root_sha256": previous,
                            "record_sha256": raw_hash})
            committed = self._now()
            if not _in_decision_minute(committed, decision) or committed < recorded:
                raise RegistryDenied("LATE_SIGNAL_REGISTRATION")
            conn.execute("INSERT INTO signal_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (seq, material["decision_at"], material["signal_id"], material["record_id"],
                          canonical_bytes(material).decode("utf-8"), raw_hash, previous, root,
                          committed.isoformat()))
            if not _in_decision_minute(self._now(), decision):
                raise RegistryDenied("LATE_SIGNAL_REGISTRATION")
            conn.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise RegistryDenied("DUPLICATE_DECISION_OR_SIGNAL") from exc
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()
        return {"status": LOCAL_KIND, "record_id": material["record_id"],
                "raw_sha256": raw_hash, "registry_root_sha256": root,
                "recorded_at": material["recorded_at"],
                "outcome_contracts": material["outcome_contracts"],
                "external_anchor_required": True, "broker_action_authorized": False}

    def _load(self, record_id: str) -> tuple[dict[str, Any], str, str]:
        with closing(self._connect()) as conn:
            rows = self._rows(conn)
            self._verify_rows(rows)
        for row in rows:
            if row[3] == record_id:
                return json.loads(row[4]), row[5], row[7]
        raise RegistryDenied("UNKNOWN_RECORD")

    def local_readback(self, record_id: str) -> dict[str, Any]:
        """Return a hash-checked local candidate; gateway must reject it."""
        material, raw_hash, root = self._load(record_id)
        return {"schema_version": SCHEMA_VERSION,
                "source": "local_sqlite_registry_readback",
                "registry_kind": LOCAL_KIND,
                "append_only_verified": False,
                "independent_readback_verified": False,
                **material, "raw_sha256": raw_hash, "registry_root_sha256": root,
                "read_back_at": self._now().astimezone(SHANGHAI).isoformat(),
                "external_anchor_required": True}

    def gateway_adapter(self, record_id: str, *,
                        anchor_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any]]
                        ) -> tuple[dict[str, Any], Callable[[Mapping[str, Any]], dict[str, Any]]]:
        """Adapt only an independently attested inclusion for gateway readback.

        ``anchor_verifier`` must itself consult an independent append-only
        system or host attestation. Merely reading this SQLite file cannot
        satisfy the trust boundary; a fabricated callback is not production
        evidence. The callback returns a proof binding exact record/root and
        its external receipt time, all within the frozen decision minute.
        """
        if not callable(anchor_verifier):
            raise RegistryDenied("EXTERNAL_ANCHOR_REQUIRED")
        candidate = self.local_readback(record_id)
        read_back = self._now().astimezone(SHANGHAI).isoformat()
        candidate["read_back_at"] = read_back
        proof = self._anchor_proof(candidate, anchor_verifier)
        promoted = {**candidate, "source": "independent_append_only_registry_readback",
                    "registry_kind": "EXTERNAL_APPEND_ONLY", "append_only_verified": True,
                    "independent_readback_verified": True,
                    "external_anchor_required": False,
                    "anchor_received_at": proof["anchor_received_at"],
                    "anchor_proof_sha256": proof["proof_sha256"]}

        def verify(receipt: Mapping[str, Any]) -> dict[str, Any]:
            if not isinstance(receipt, Mapping) or dict(receipt) != promoted:
                raise RegistryDenied("REGISTRATION_READBACK_MISMATCH")
            current, raw_hash, root = self._load(record_id)
            if (current != {key: promoted[key] for key in RECORD_FIELDS}
                    or raw_hash != promoted["raw_sha256"] or root != promoted["registry_root_sha256"]):
                raise RegistryDenied("REGISTRY_RECORD_CHANGED")
            fresh = self._anchor_proof(candidate, anchor_verifier)
            if (fresh["proof_sha256"] != proof["proof_sha256"]
                    or fresh["anchor_received_at"] != proof["anchor_received_at"]):
                raise RegistryDenied("ANCHOR_PROOF_CHANGED")
            return {"status": "VERIFIED_APPEND_ONLY_INCLUSION",
                    "registry_id": promoted["registry_id"],
                    "record_id": promoted["record_id"],
                    "record_sha256": promoted["raw_sha256"],
                    "registry_root_sha256": promoted["registry_root_sha256"],
                    "recorded_at": promoted["recorded_at"],
                    "read_back_at": promoted["read_back_at"],
                    "verifier_identity": fresh["verifier_identity"],
                    "proof_sha256": fresh["proof_sha256"],
                    "verified_at": fresh["verified_at"]}

        return promoted, verify

    def _anchor_proof(self, candidate: Mapping[str, Any],
                      verifier: Callable[[Mapping[str, Any]], Mapping[str, Any]]) -> dict[str, Any]:
        try:
            proof = verifier(dict(candidate))
        except Exception as exc:
            raise RegistryDenied("EXTERNAL_ANCHOR_NOT_VERIFIED") from exc
        if (not isinstance(proof, Mapping) or proof.get("status") != ANCHOR_STATUS
                or any(proof.get(field) != candidate.get(field) for field in
                       ("registry_id", "record_id", "registry_root_sha256", "recorded_at"))
                or proof.get("record_sha256") != candidate.get("raw_sha256")):
            raise RegistryDenied("EXTERNAL_ANCHOR_NOT_VERIFIED")
        _identity(proof.get("verifier_identity"), "verifier_identity")
        _hash(proof.get("proof_sha256"), "anchor_proof_sha256")
        decision = _instant(candidate["decision_at"], "decision_at")
        recorded = _instant(candidate["recorded_at"], "recorded_at")
        anchored = _instant(proof.get("anchor_received_at"), "anchor_received_at")
        if anchored < recorded or not _in_decision_minute(anchored, decision):
            raise RegistryDenied("LATE_EXTERNAL_ANCHOR")
        read_back = _instant(candidate["read_back_at"], "read_back_at")
        verified = _instant(proof.get("verified_at"), "verified_at")
        now = self._now()
        if not read_back <= verified <= now or (now - read_back).total_seconds() > 15:
            raise RegistryDenied("STALE_EXTERNAL_VERIFICATION")
        return dict(proof)
