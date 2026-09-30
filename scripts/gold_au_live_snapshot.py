#!/usr/bin/env python3
"""Read local GOLD2 evidence at 08:10–08:30; dry-run only, no network/orders."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys

if sys.version_info < (3, 12):
    raise SystemExit("gold_au_live_snapshot requires Python >= 3.12")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from yuanli_invest.gold_au_live_snapshot import prepare_live_snapshot  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--as-of", required=True, help="Explicit timezone-aware current time")
    parser.add_argument("--output", type=Path, help="Optional full local JSON receipt/dataset path")
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    result = prepare_live_snapshot(request, as_of=datetime.fromisoformat(args.as_of.replace("Z", "+00:00")))
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output is not None:
        args.output.write_text(encoded, encoding="utf-8")
    summary = {"status": result["status"], "reason": result.get("reason"),
               "dataset_sha256": result.get("dataset_sha256"),
               "signal_reason": result.get("signal", {}).get("reason"),
               "actionable_entry": result.get("signal", {}).get("actionable_entry", False),
               "broker_action_authorized": False}
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] in {"READY_STRICT_RESEARCH_SIGNAL", "COLLECTING_BEFORE_DECISION"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
