#!/usr/bin/env python3
"""Assemble a bounded official SHFE prior-session archive; never trade.

Daily execution is limited to the official session's 08:05-08:10 window.
Existing verified reports retain their actual capture timestamps. Only up to
five missing official session reports may be fetched; no vendor dates or
historical publication instants are inferred. Dry-run never fetches or writes.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, time, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time as wall_time
from typing import Callable

if sys.version_info < (3, 12):
    raise SystemExit("gold_au_shfe_archive_worker requires Python >= 3.12")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.gold_au_decision_worker import _private_root  # noqa: E402
from scripts.gold_au_shfe_daily_capture import normalize_daily  # noqa: E402
from yuanli_invest.gold_au_live_snapshot import SHANGHAI  # noqa: E402
from yuanli_invest.gold_au_official_calendar import (  # noqa: E402
    CalendarEvidenceError, load_calendar_receipt, session_window,
)
from yuanli_invest.shfe_au_source import SHFE_ROOT, fetch_shfe  # noqa: E402

CONFIG_SCHEMA = "gold-au-shfe-archive-worker-config.v1"
ROLLING_SCHEMA = "gold-au-shfe-rolling-archive.v1"
PRIOR_SESSIONS = 273
MAX_MISSING_REQUESTS = 5
MAX_SOURCE_MANIFESTS = 8
MAX_MANIFEST_BYTES = 16_000_000
MAX_SOURCE_REPORTS = 2500
MAX_RAW_BYTES = 1_000_000
HASH = re.compile(r"^[0-9a-f]{64}$")


class ArchiveDenied(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _instant(value: object) -> datetime:
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ArchiveDenied("INVALID_SHFE_CAPTURE_TIME") from exc
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ArchiveDenied("NAIVE_SHFE_CAPTURE_TIME")
    return stamp.astimezone(timezone.utc)


def _json(path: Path) -> tuple[dict, str]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ArchiveDenied("MISSING_LINKED_OR_OVERSIZED_SOURCE_JSON")
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeError, ValueError) as exc:
        raise ArchiveDenied("INVALID_SOURCE_JSON") from exc
    if not isinstance(value, dict):
        raise ArchiveDenied("SOURCE_JSON_OBJECT_REQUIRED")
    return value, hashlib.sha256(raw).hexdigest()


def _path(value: object, root: Path) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ArchiveDenied("EXPLICIT_SOURCE_PATH_REQUIRED")
    path = Path(value).expanduser()
    return path.absolute() if path.is_absolute() else (root / path).absolute()


def _normal(raw: bytes, day: str) -> dict:
    if not raw or len(raw) > MAX_RAW_BYTES:
        raise ArchiveDenied("INVALID_SHFE_RAW_SIZE")
    try:
        document = json.loads(raw)
        if not isinstance(document, dict) or document.get("report_date") != day.replace("-", ""):
            raise ArchiveDenied("SHFE_RAW_REPORT_DATE_MISMATCH")
        normalized = normalize_daily(raw, day)
        for bar in normalized["bars"]:
            if any(not Decimal(bar[key]).is_finite() for key in
                   ("open", "high", "low", "close", "volume", "open_interest")):
                raise ArchiveDenied("NONFINITE_SHFE_BAR")
    except (TypeError, ValueError, ArithmeticError, KeyError) as exc:
        if isinstance(exc, ArchiveDenied):
            raise
        raise ArchiveDenied("MALFORMED_SHFE_RAW_REPORT") from exc
    return normalized


def _source_reports(paths: list[Path], required: list[str], observed: datetime,
                    decision_day: date) -> tuple[dict, list[dict]]:
    """Validate source inventories and all selected raw reports before writing."""
    if not 1 <= len(paths) <= MAX_SOURCE_MANIFESTS + 1:
        raise ArchiveDenied("UNBOUNDED_SOURCE_MANIFESTS")
    selected, proofs, identities = {}, [], set()
    wanted = set(required)
    for path in paths:
        identity = str(path.resolve())
        if identity in identities:
            raise ArchiveDenied("DUPLICATE_SOURCE_MANIFEST")
        identities.add(identity)
        manifest, digest = _json(path)
        if (manifest.get("schema_version") != "gold-au-shfe-daily-capture.v1"
                or manifest.get("mode") != "EXECUTE"
                or manifest.get("status") not in {"CAPTURED", "PARTIAL_FAILURE"}
                or manifest.get("historical_release_time_verified") is not False):
            raise ArchiveDenied("INVALID_OFFICIAL_SHFE_MANIFEST")
        manifest_capture = _instant(manifest.get("captured_at"))
        if manifest_capture > observed:
            raise ArchiveDenied("FUTURE_SHFE_MANIFEST_CAPTURE")
        reports = manifest.get("reports")
        if not isinstance(reports, list) or not 1 <= len(reports) <= MAX_SOURCE_REPORTS:
            raise ArchiveDenied("UNBOUNDED_SHFE_SOURCE_REPORTS")
        seen = set()
        for report in reports:
            if not isinstance(report, dict):
                raise ArchiveDenied("INVALID_SHFE_SOURCE_REPORT")
            try:
                day = date.fromisoformat(report["date"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ArchiveDenied("INVALID_SHFE_SOURCE_DATE") from exc
            if day.isoformat() != report["date"] or day.isoformat() in seen:
                raise ArchiveDenied("DUPLICATE_OR_NONCANONICAL_SHFE_SOURCE_DATE")
            seen.add(day.isoformat())
            captured = _instant(report.get("captured_at"))
            if captured > observed or day > observed.astimezone(SHANGHAI).date():
                raise ArchiveDenied("FUTURE_SHFE_SOURCE_REPORT")
            if captured > manifest_capture:
                raise ArchiveDenied("REPORT_CAPTURE_AFTER_SOURCE_MANIFEST")
            if captured.astimezone(SHANGHAI).date() < day:
                raise ArchiveDenied("SHFE_CAPTURE_PRECEDES_OBSERVATION")
            if day.isoformat() not in wanted:
                continue
            if day >= decision_day:
                raise ArchiveDenied("SHFE_DECISION_SESSION_NOT_COMPLETED")
            expected = report.get("raw_sha256")
            if not isinstance(expected, str) or HASH.fullmatch(expected) is None:
                raise ArchiveDenied("INVALID_SHFE_RAW_HASH")
            raw_path = _path(report.get("raw_file"), path.parent)
            raw_dir = path.parent / "raw"
            if (raw_path.is_symlink() or raw_dir.is_symlink() or not raw_path.is_file()
                    or raw_path.resolve().parent != raw_dir.resolve()
                    or raw_path.name != "kx" + day.strftime("%Y%m%d") + ".dat"
                    or raw_path.stat().st_size > MAX_RAW_BYTES):
                raise ArchiveDenied("SHFE_RAW_NOT_IN_EXPECTED_ARCHIVE")
            raw = raw_path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ArchiveDenied("SHFE_RAW_HASH_MISMATCH")
            normalized = _normal(raw, day.isoformat())
            if normalized["bars"] != report.get("bars"):
                raise ArchiveDenied("SHFE_MANIFEST_RAW_DISAGREEMENT")
            existing = selected.get(day.isoformat())
            if existing is not None and existing["report"]["raw_sha256"] != expected:
                raise ArchiveDenied("CONFLICTING_OFFICIAL_SHFE_REPORTS")
            # Identical bytes with another genuine capture receipt retain the
            # earliest observed capture. This never invents a release instant.
            if existing is None or captured < existing["captured"]:
                selected[day.isoformat()] = {"report": report, "raw": raw, "captured": captured,
                                             "source_manifest_sha256": digest}
        proofs.append({"manifest_path": str(path.resolve()), "manifest_sha256": digest})
    return selected, proofs


def _exclusive(path: Path, raw: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as target:
        target.write(raw)
        target.flush()
        os.fsync(target.fileno())


def prepare_archive(*, calendar_receipt: dict, seed_manifest_paths: list[Path],
                    decision_day: date, observed_at: datetime, output_dir: Path,
                    execute: bool = False, fetch_missing: bool = False,
                    fetch: Callable[[str], bytes] = fetch_shfe,
                    clock: Callable[[], datetime] | None = None,
                    pause: Callable[[float], None] = wall_time.sleep,
                    capture_deadline: datetime | None = None) -> dict:
    """Prepare a future session's bounded seed offline, or a daily archive.

    Calendar bytes must have been authenticated by load_calendar_receipt. This
    function defaults to no network and no writes. The scheduled run_once is
    responsible for today's session and capture window before fetch is enabled.
    """
    if not isinstance(observed_at, datetime) or observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ArchiveDenied("NAIVE_HOST_CLOCK")
    observed = observed_at.astimezone(timezone.utc)
    window = session_window(calendar_receipt, decision_day, prior_count=PRIOR_SESSIONS, horizons=())
    required = window["prior_sessions"]
    selected, proofs = _source_reports(seed_manifest_paths, required, observed, decision_day)
    missing = [day for day in required if day not in selected]
    if len(missing) > MAX_MISSING_REQUESTS:
        raise ArchiveDenied("OFFICIAL_SHFE_GAP_EXCEEDS_FIVE_REQUESTS")
    summary = {"schema_version": "gold-au-shfe-daily-capture.v1",
               "rolling_schema_version": ROLLING_SCHEMA,
               "mode": "EXECUTE" if execute else "DRY_RUN",
               "decision_date": decision_day.isoformat(),
               "interval": [required[0], required[-1]], "prior_sessions": required,
               "requested_days": PRIOR_SESSIONS, "retained_reports": len(selected),
               "missing_official_sessions": missing, "new_requests": 0,
               "historical_release_time_verified": False,
               "authority": "OBSERVED_OFFICIAL_REPORT_BYTES_NOT_FIRST_PUBLICATION",
               "source_manifests": proofs, "calendar_raw_sha256": calendar_receipt["raw_sha256"],
               "reports": [], "errors": [], "broker_action_authorized": False}
    if not execute:
        return {**summary, "status": "DRY_RUN"}
    if missing and not fetch_missing:
        raise ArchiveDenied("SEED_REQUIRES_MISSING_OFFICIAL_REPORTS")
    output = Path(output_dir).absolute()
    if output.exists() or output.is_symlink() or output.parent.is_symlink():
        raise ArchiveDenied("IMMUTABLE_ARCHIVE_ALREADY_EXISTS_OR_LINKED")
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _private_root(output.parent)
    output.mkdir(mode=0o700)
    raw_dir = output / "raw"
    raw_dir.mkdir(mode=0o700)
    clock = clock or (lambda: datetime.now(timezone.utc))
    for index, day in enumerate(missing):
        if index:
            pause(0.5)
        failure_stage = "PRECHECK"
        try:
            if capture_deadline is not None:
                before = clock()
                if before.tzinfo is None or before.utcoffset() is None or before >= capture_deadline:
                    raise ArchiveDenied("SHFE_CAPTURE_DEADLINE_REACHED")
            summary["new_requests"] += 1
            failure_stage = "FETCH"
            raw = fetch(day)
            failure_stage = "NORMALIZE"
            row = _normal(raw, day)
            failure_stage = "TIME_CHECK"
            captured = clock()
            if captured.tzinfo is None or captured.utcoffset() is None or captured < observed:
                raise ArchiveDenied("INVALID_NEW_SHFE_CAPTURE_CLOCK")
            if captured.astimezone(SHANGHAI).date() != decision_day:
                raise ArchiveDenied("NEW_SHFE_CAPTURE_ON_WRONG_DECISION_DAY")
            if capture_deadline is not None and captured >= capture_deadline:
                raise ArchiveDenied("SHFE_CAPTURE_DEADLINE_REACHED")
            row["captured_at"] = captured.astimezone(timezone.utc).isoformat()
            selected[day] = {"report": row, "raw": raw, "captured": captured,
                              "source_manifest_sha256": None}
        except (OSError, ValueError, ArithmeticError) as exc:
            summary["errors"].append({"date": day, "reason": exc.code if isinstance(exc, ArchiveDenied)
                                      else "SHFE_FETCH_FAILED_" + type(exc).__name__,
                                      "failure_stage": failure_stage})
    for day in required:
        entry = selected.get(day)
        if entry is None:
            continue
        row = entry["report"]
        target = raw_dir / ("kx" + day.replace("-", "") + ".dat")
        _exclusive(target, entry["raw"])
        summary["reports"].append({"date": day, "raw_sha256": row["raw_sha256"],
                                    "raw_file": str(target), "captured_at": row["captured_at"],
                                    "bars": row["bars"],
                                    "source_ref": SHFE_ROOT + "/" + target.name,
                                    "retained_source_manifest_sha256": entry["source_manifest_sha256"]})
    completed = clock()
    if (completed.tzinfo is None or completed.utcoffset() is None or completed < observed
            or any(completed < entry["captured"] for entry in selected.values())):
        raise ArchiveDenied("INVALID_ARCHIVE_COMPLETION_CLOCK")
    summary["captured_at"] = completed.astimezone(timezone.utc).isoformat()
    summary["status"] = "CAPTURED" if len(summary["reports"]) == PRIOR_SESSIONS and not summary["errors"] else "PARTIAL_FAILURE"
    _exclusive(output / "manifest.json", (json.dumps(summary, sort_keys=True, ensure_ascii=False,
                                                    indent=2, allow_nan=False) + "\n").encode("utf-8"))
    return summary


def run_once(runtime_dir: Path, *, execute: bool = False,
             clock: Callable[[], datetime] | None = None,
             fetch: Callable[[str], bytes] = fetch_shfe,
             pause: Callable[[float], None] = wall_time.sleep) -> dict:
    runtime = _private_root(runtime_dir)
    clock = clock or (lambda: datetime.now(timezone.utc))
    observed = clock()
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise ArchiveDenied("NAIVE_HOST_CLOCK")
    local = observed.astimezone(SHANGHAI)
    day = local.date()
    if day.weekday() >= 5:
        return {"status": "SKIPPED_NON_SESSION", "date": day.isoformat(),
                "reason": "WEEKEND", "new_requests": 0, "broker_action_authorized": False}
    config, _ = _json(runtime / "shfe_archive_sources.json")
    if config.get("schema_version") != CONFIG_SCHEMA:
        raise ArchiveDenied("EXPLICIT_SHFE_ARCHIVE_CONFIG_REQUIRED")
    calendar = load_calendar_receipt(_path(config.get("calendar_receipt_path"), runtime), as_of=observed)
    try:
        window = session_window(calendar, day, prior_count=PRIOR_SESSIONS, horizons=())
    except CalendarEvidenceError as exc:
        if exc.code != "DECISION_DAY_NOT_OFFICIAL_SESSION":
            raise
        return {"status": "SKIPPED_NON_SESSION", "date": day.isoformat(),
                "reason": "OFFICIAL_HOLIDAY", "new_requests": 0, "broker_action_authorized": False}
    if execute and not time(8, 5) <= local.time().replace(tzinfo=None) < time(8, 10):
        raise ArchiveDenied("OUTSIDE_0805_ARCHIVE_WINDOW")
    names = config.get("seed_manifest_paths")
    if not isinstance(names, list) or not 1 <= len(names) <= MAX_SOURCE_MANIFESTS:
        raise ArchiveDenied("BOUNDED_EXPLICIT_SEED_MANIFESTS_REQUIRED")
    paths = [_path(name, runtime) for name in names]
    previous = runtime / "shfe_archives" / window["prior_session"] / "manifest.json"
    if previous.exists() or previous.is_symlink():
        prior, _ = _json(previous)
        if (prior.get("rolling_schema_version") != ROLLING_SCHEMA
                or prior.get("decision_date") != window["prior_session"]):
            raise ArchiveDenied("STALE_OR_MISIDENTIFIED_PREVIOUS_ARCHIVE")
        paths.append(previous)
    result = prepare_archive(calendar_receipt=calendar, seed_manifest_paths=paths,
                             decision_day=day, observed_at=observed,
                             output_dir=runtime / "shfe_archives" / day.isoformat(),
                             execute=execute, fetch_missing=execute, fetch=fetch, clock=clock, pause=pause,
                             capture_deadline=local.replace(hour=8, minute=10, second=0, microsecond=0))
    return {"status": result["status"], "date": day.isoformat(),
            "manifest_path": str(runtime / "shfe_archives" / day.isoformat() / "manifest.json"),
            "reports": len(result["reports"]), "retained_reports": result["retained_reports"],
            "missing_official_sessions": result["missing_official_sessions"],
            "new_requests": result["new_requests"], "errors": result["errors"],
            "broker_action_authorized": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        result = run_once(args.runtime_dir, execute=args.execute)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["status"] in {"CAPTURED", "DRY_RUN", "SKIPPED_NON_SESSION"} else 2
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "DENIED", "reason": str(exc),
                          "broker_action_authorized": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
