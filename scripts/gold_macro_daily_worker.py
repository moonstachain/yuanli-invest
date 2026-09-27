#!/usr/bin/env python3
"""Capture FRED-distributed GOLD2 macro bytes at 08:10; never trade."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, time, timezone
import json
from pathlib import Path
import sys
from typing import Callable

if sys.version_info < (3, 12):
    raise SystemExit("gold_macro_daily_worker requires Python >= 3.12")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.gold_au_decision_worker import _private_root  # noqa: E402
from scripts.gold_macro_capture import run as capture_macro  # noqa: E402
from yuanli_invest.gold_au_live_snapshot import SHANGHAI  # noqa: E402


def run_once(runtime_dir: Path, *, clock: Callable[[], datetime] | None = None,
             capture=capture_macro) -> dict:
    runtime = _private_root(runtime_dir)
    clock = clock or (lambda: datetime.now(timezone.utc))
    observed = clock()
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise ValueError("NAIVE_HOST_CLOCK")
    local = observed.astimezone(SHANGHAI)
    day = local.date()
    if day.weekday() >= 5:
        return {"status": "NON_WEEKDAY", "date": day.isoformat(), "broker_action_authorized": False}
    if not time(8, 10) <= local.time().replace(tzinfo=None) < time(8, 20):
        raise ValueError("OUTSIDE_0810_CAPTURE_WINDOW")
    captures_dir = runtime / "macro_captures"
    captures_dir.mkdir(mode=0o700, exist_ok=True)
    target = captures_dir / day.isoformat()
    if target.exists():
        raise FileExistsError("DAILY_CAPTURE_ALREADY_EXISTS")
    result = capture(start=day - timedelta(days=180), end_inclusive=day,
                     output_dir=target, execute=True, now=clock)
    return {"status": result["status"], "date": day.isoformat(),
            "manifest_path": str(target / "manifest.json"),
            "series_captured": [row["provider_series"] for row in result["captures"]
                                if row.get("status") == "CAPTURED"],
            "broker_action_authorized": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        runtime = _private_root(args.runtime_dir)
        result = (run_once(runtime) if args.execute else
                  {"status": "DRY_RUN", "runtime_dir": str(runtime),
                   "broker_action_authorized": False})
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["status"] in {"CAPTURED", "DRY_RUN", "NON_WEEKDAY"} else 2
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "FAILED", "reason": str(exc),
                          "broker_action_authorized": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
