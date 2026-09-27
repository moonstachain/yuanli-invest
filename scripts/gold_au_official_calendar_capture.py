#!/usr/bin/env python3
"""Capture two official annual SHFE calendar notices; dry-run by default."""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from yuanli_invest.gold_au_official_calendar import SOURCES, capture_calendar, session_window


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--decision-date", type=date.fromisoformat)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"status": "DRY_RUN", "sources": SOURCES, "broker_action_authorized": False}))
        return 0
    receipt = capture_calendar(args.output_dir)
    summary = {"status": receipt["status"], "receipt_path": str((args.output_dir / "receipt.json").resolve()),
               "source_bundle_sha256": receipt["raw_sha256"], "covered_years": receipt["covered_years"],
               "session_count": len(receipt["sessions"]), "broker_action_authorized": False}
    if args.decision_date:
        window = session_window(receipt, args.decision_date)
        summary["window"] = {key: value for key, value in window.items() if key != "prior_sessions"}
        summary["prior_273_start"] = window["prior_sessions"][0]
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
