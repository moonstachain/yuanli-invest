#!/usr/bin/env python3
"""Generate a new read-only GOLD2 operations HTML/JSON evidence projection."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
from yuanli_invest.gold_au_operations_status import SHANGHAI, build_operations_status, render_html
from yuanli_invest.gold_au_official_calendar import load_calendar_receipt
from scripts.gold_au_research_diagnostic import accept_natural_morning


def write_new_output(output: Path, result: dict) -> None:
    if not output.is_absolute() or not output.parent.is_dir() or output.exists() or output.is_symlink():
        raise ValueError("NEW_ABSOLUTE_OUTPUT_DIRECTORY_REQUIRED")
    output.mkdir(mode=0o700)
    for name, raw in (("status.json", (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()),
                      ("index.html", render_html(result).encode("utf-8"))):
        fd = os.open(output / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--no-launchd", action="store_true")
    args = parser.parse_args()
    try:
        if args.config.is_symlink() or not args.config.is_file() or args.config.stat().st_size > 100000:
            raise ValueError("CONFIG_REQUIRED")
        config = json.loads(args.config.read_bytes())
        now = datetime.now(timezone.utc)
        runtime = config.get("runtime_dir")
        morning = None
        if isinstance(runtime, str) and runtime:
            morning = accept_natural_morning(Path(runtime), decision_date=now.astimezone(SHANGHAI).date().isoformat(), as_of=now)
        calendar_path = config.get("calendar_receipt_path")
        if isinstance(calendar_path, str) and calendar_path:
            calendar = load_calendar_receipt(Path(calendar_path), as_of=now)
            today = now.astimezone(SHANGHAI).date().isoformat()
            sessions = calendar["sessions"]
            if sessions[0] <= today <= sessions[-1] and today not in sessions:
                morning = {"status": "OFFICIAL_NON_SESSION_DAY", "decision_date": today,
                           "checked_at": now.isoformat(), "reason": "RESEARCH_FREEZE_NOT_SCHEDULED", "external_time_anchor": "NOT_VERIFIED"}
        options = {"launchd_observer": lambda label: {"installation": "UNKNOWN"}} if args.no_launchd else {}
        result = build_operations_status(config, as_of=now, morning_acceptance=morning, **options)
        write_new_output(args.output_dir, result)
        print(json.dumps({"status": "READ_ONLY_STATUS_GENERATED", "output_dir": str(args.output_dir),
                          "broker_action_authorized": False, "observed_at": result["observed_at"]}))
        return 0
    except (OSError, ValueError, TypeError, KeyError):
        print(json.dumps({"status": "DENIED", "reason": "CONFIG_EVIDENCE_OR_OUTPUT_INVALID", "broker_action_authorized": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
