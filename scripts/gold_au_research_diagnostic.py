#!/usr/bin/env python3
"""Independent current-time public research probe and read-only morning acceptance.

--capture-public performs two bounded FRED GETs and one official SHFE GET,
writing only a new private diagnostic directory. It cannot populate scheduled
requests, daily macro/SHFE archives, decision SQLite, or any broker runtime.
--accept-day only reads the natural morning artifacts; it never replays a missed
08:30 freeze. A missing account-cost receipt remains an explicit dependency.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from urllib.parse import quote

if sys.version_info < (3, 12):
    raise SystemExit("gold_au_research_diagnostic requires Python >= 3.12")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from scripts.gold_au_daily_request import _private_child, _exclusive_json
from scripts.gold_au_decision_worker import _private_root
from scripts.gold_macro_capture import run as capture_macro
from yuanli_invest.gold_au_decision_log import LocalDecisionLog
from yuanli_invest.gold_au_live_snapshot import SHANGHAI, _official_day
from yuanli_invest.gold_au_official_calendar import load_calendar_receipt
from yuanli_invest.gold_au_research_diagnostic import observe_public_evidence
from yuanli_invest.receipts import canonical_hash
from yuanli_invest.shfe_au_source import fetch_shfe


def _read(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16_000_000:
        raise ValueError("EXPLICIT_BOUNDED_JSON_REQUIRED")
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("JSON_OBJECT_REQUIRED")
    return value


def _catalog_path(root: Path, text: str) -> Path:
    path = Path(text).expanduser()
    return path.absolute() if path.is_absolute() else root / path


def capture_current(runtime_dir: Path, *, clock=lambda: datetime.now(timezone.utc),
                    macro_capture=capture_macro, shfe_fetch=fetch_shfe) -> dict:
    runtime = _private_root(runtime_dir)
    started = clock()
    if started.tzinfo is None or started.utcoffset() is None:
        raise ValueError("AWARE_CLOCK_REQUIRED")
    sources = _read(runtime / "daily_request_sources.json")
    archive = _read(runtime / "shfe_archive_sources.json")
    seeds = archive.get("seed_manifest_paths")
    if not isinstance(seeds, list) or not 1 <= len(seeds) <= 8:
        raise ValueError("EXPLICIT_RESEARCH_SEED_ARCHIVES_REQUIRED")
    parent = _private_child(runtime, "research_diagnostics")
    stamp = started.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = parent / stamp
    output.mkdir(mode=0o700)  # A fresh run cannot overwrite even a failed probe.
    today = started.astimezone(SHANGHAI).date()
    calendar_path = _catalog_path(runtime, sources["calendar_receipt_path"])
    calendar = load_calendar_receipt(calendar_path, as_of=started)
    prior = [d for d in calendar["sessions"] if d < today.isoformat()]
    if not prior:
        raise ValueError("COMPLETED_OFFICIAL_SESSION_REQUIRED")
    last = prior[-1]
    macro = macro_capture(start=today - timedelta(days=180), end_inclusive=today,
                          output_dir=output / "macro", execute=True, now=clock)
    request = {"schema_version": "gold-au-research-observation-request.v1",
               "calendar_receipt_path": str(calendar_path),
               "h10_mapping_receipt_path": str(_catalog_path(runtime, sources["h10_mapping_receipt_path"])),
               "fred_manifest_path": str(output / "macro" / "manifest.json"),
               "shfe_manifest_paths": [str(_catalog_path(runtime, name)) for name in seeds]}
    _exclusive_json(output / "request.json", request)
    try:
        raw = shfe_fetch(last)
        document = json.loads(raw)
        if not isinstance(document, dict) or document.get("report_date") != last.replace("-", ""):
            raise ValueError("SHFE_PROBE_REPORT_DATE_MISMATCH")
        rows = _official_day(raw, date.fromisoformat(last))
        raw_dir = _private_child(output, "raw")
        path = raw_dir / ("kx" + last.replace("-", "") + ".dat")
        import os
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
        probe = {"status": "CAPTURED", "date": last, "captured_at": clock().isoformat(),
                 "raw_file": str(path), "raw_sha256": hashlib.sha256(raw).hexdigest(), "active_au_rows": len(rows)}
        seed_hashes = {r["raw_sha256"] for name in request["shfe_manifest_paths"]
                       for r in _read(Path(name)).get("reports", []) if r.get("date") == last}
        probe["matches_existing_latest_session_seed"] = seed_hashes == {probe["raw_sha256"]}
    except (OSError, ValueError, TypeError, KeyError) as exc:
        probe = {"status": "FAILED", "date": last, "error_type": type(exc).__name__}
    _exclusive_json(output / "public-shfe-probe.json", probe)
    observed = clock()  # Always the real post-capture time, never a fake 08:30.
    result = observe_public_evidence(request, as_of=observed)
    if macro.get("status") != "CAPTURED" or not probe.get("matches_existing_latest_session_seed"):
        result = {"schema_version": "gold-au-current-research-observation.v1", "status": "BLOCKED",
                  "reason": "PUBLIC_CAPTURE_FAILED_OR_LATEST_SHFE_SEED_CONFLICT", "observed_at": observed.isoformat(),
                  "broker_action_authorized": False, "actionable_entry": False, "decision_frozen": False}
    result.update({"started_at": started.isoformat(), "public_probe": probe,
                   "source_catalog_sha256": canonical_hash(sources), "archive_catalog_sha256": canonical_hash(archive),
                   "formal_daily_artifacts_written": False, "output_dir": str(output)})
    _exclusive_json(output / "report.json", result)
    return result


def accept_natural_morning(runtime_dir: Path, *, decision_date: str, as_of: datetime) -> dict:
    runtime = _private_root(runtime_dir)
    day = date.fromisoformat(decision_date)
    if day.isoformat() != decision_date or as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("CANONICAL_DAY_AND_AWARE_CLOCK_REQUIRED")
    cutoff = datetime.combine(day, time(8, 31), SHANGHAI)
    names = {"shfe_archive": runtime / "shfe_archives" / decision_date / "manifest.json",
             "macro_capture": runtime / "macro_captures" / decision_date / "manifest.json",
             "account_cost_margin": runtime / "cost_receipts" / decision_date / "receipt.json",
             "assembled_request": runtime / "requests" / (decision_date + ".json")}
    proofs = {}
    for key, path in names.items():
        try:
            value = _read(path)
            proofs[key] = {"status": "PRESENT_NOT_YET_OUTCOME_VALIDATED", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                           "path": str(path), "schema_version": value.get("schema_version")}
        except (OSError, ValueError):
            proofs[key] = {"status": "MISSING_OR_INVALID", "path": str(path)}
    db = runtime / "gold_au_decisions.sqlite"
    result = {"schema_version": "gold-au-natural-morning-acceptance.v1", "decision_date": decision_date,
              "checked_at": as_of.isoformat(), "status": "PENDING" if as_of < cutoff else "MISSING_NATURAL_DECISION",
              "broker_action_authorized": False, "replay_performed": False, "inputs": proofs,
              "external_time_anchor": "NOT_VERIFIED"}
    if db.is_symlink() or not db.is_file():
        return result
    try:
        with sqlite3.connect("file:" + quote(str(db), safe="/") + "?mode=ro", uri=True) as conn:
            conn.execute("PRAGMA query_only=ON")
            if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise ValueError("SQLITE_CORRUPT")
            LocalDecisionLog._verify_triggers(conn)
            rows = LocalDecisionLog._rows(conn)
            root = LocalDecisionLog._verify_rows(rows)
        record = next((json.loads(row[3]) for row in rows if row[1] == decision_date), None)
        result["chain_record_count"] = len(rows)
        result["chain_root_sha256"] = root
        if record:
            if datetime.fromisoformat(record["recorded_at"]) > as_of:
                result.update({"status": "INVALID_DECISION_LOG", "reason": "RECORD_NOT_YET_AVAILABLE_AT_ACCEPTANCE"})
                return result
            snapshot = record["snapshot"]
            result.update({"status": "ACCEPTED_RESEARCH_FREEZE" if record["outcome_status"] == "READY_STRICT_RESEARCH_SIGNAL" else "RECORDED_EXPLICIT_SKIP",
                           "outcome_status": record["outcome_status"], "outcome_reason": record["outcome_reason"],
                           "record_id": record["record_id"], "started_at": record["started_at"], "recorded_at": record["recorded_at"],
                           "snapshot_sha256": record["snapshot_sha256"],
                           "dataset_sha256": snapshot.get("dataset_sha256"), "actionable_entry": record["actionable_entry"],
                           "action_block": record["action_block"], "broker_action_authorized": False})
    except (OSError, ValueError, sqlite3.Error, KeyError):
        result.update({"status": "INVALID_DECISION_LOG", "reason": "READ_ONLY_CHAIN_VERIFICATION_FAILED"})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", required=True, type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture-public", action="store_true")
    group.add_argument("--accept-day")
    args = parser.parse_args()
    try:
        result = (capture_current(args.runtime_dir) if args.capture_public else
                  accept_natural_morning(args.runtime_dir, decision_date=args.accept_day, as_of=datetime.now(timezone.utc)))
        print(json.dumps({k: v for k, v in result.items() if k not in {"public_dataset", "source_inventory", "source_receipts"}}, ensure_ascii=False, sort_keys=True))
        return 0 if result["status"] in {"READY_RESEARCH_OBSERVATION", "ACCEPTED_RESEARCH_FREEZE", "RECORDED_EXPLICIT_SKIP", "PENDING"} else 2
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "DENIED", "reason": type(exc).__name__, "broker_action_authorized": False}), file=sys.stderr)
        return 2
if __name__ == "__main__":
    raise SystemExit(main())
