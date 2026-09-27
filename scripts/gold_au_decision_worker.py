#!/usr/bin/env python3
"""Record exactly one local 08:30 AU research decision; never place an order.

The daily request must already exist in ``requests/YYYY-MM-DD.json``. Missing
or malformed input becomes a recorded SKIPPED decision, not a silent day or a
substitute trading signal. The local log is not an external time witness.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat
import sys
from typing import Callable

if sys.version_info < (3, 12):
    raise SystemExit("gold_au_decision_worker requires Python >= 3.12")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from yuanli_invest.gold_au_decision_log import DecisionLogDenied, LocalDecisionLog  # noqa: E402
from yuanli_invest.gold_au_live_snapshot import SHANGHAI  # noqa: E402


def _private_root(path: Path) -> Path:
    path = path.expanduser().absolute()
    if path.is_symlink() or not path.is_dir():
        raise DecisionLogDenied("PRIVATE_RUNTIME_DIRECTORY_REQUIRED")
    mode = path.stat()
    if mode.st_uid != os.getuid() or stat.S_IMODE(mode.st_mode) != 0o700:
        raise DecisionLogDenied("INSECURE_RUNTIME_DIRECTORY")
    return path


def _request(root: Path, day: str) -> tuple[dict, str]:
    path = root / "requests" / (day + ".json")
    if not path.is_file() or path.is_symlink():
        return {"schema_version": "gold-au-live-snapshot-request.v1",
                "decision_date": day, "request_source_status": "MISSING_DAILY_REQUEST"}, "MISSING_DAILY_REQUEST"
    try:
        if path.stat().st_size > 100_000:
            raise ValueError("oversized")
        request = json.loads(path.read_text(encoding="utf-8"))
        if (not isinstance(request, dict)
                or request.get("schema_version") != "gold-au-live-snapshot-request.v1"
                or request.get("decision_date") != day):
            raise ValueError("wrong request identity")
    except (OSError, UnicodeError, ValueError):
        return {"schema_version": "gold-au-live-snapshot-request.v1",
                "decision_date": day, "request_source_status": "INVALID_DAILY_REQUEST"}, "INVALID_DAILY_REQUEST"
    return request, "PRESENT"


def run_once(runtime_dir: Path, *, clock: Callable[[], datetime] | None = None) -> dict:
    runtime = _private_root(runtime_dir)
    clock = clock or (lambda: datetime.now(timezone.utc))
    observed = clock()
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise DecisionLogDenied("NAIVE_HOST_CLOCK")
    day = observed.astimezone(SHANGHAI).date().isoformat()
    request, input_status = _request(runtime, day)
    log = LocalDecisionLog(runtime / "gold_au_decisions.sqlite", clock=clock)
    receipt = log.capture(request)
    return {"schema_version": "gold-au-decision-worker.v1",
            "decision_date": day, "input_status": input_status,
            "outcome_status": receipt["outcome_status"],
            "outcome_reason": receipt["outcome_reason"],
            "record_id": receipt["record_id"],
            "record_sha256": receipt["record_sha256"],
            "root_sha256": receipt["root_sha256"],
            "external_anchor_required": True, "broker_action_authorized": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        runtime = _private_root(args.runtime_dir)
        if not args.execute:
            result = {"status": "DRY_RUN", "runtime_dir": str(runtime),
                      "request_pattern": str(runtime / "requests" / "YYYY-MM-DD.json"),
                      "broker_action_authorized": False}
        else:
            result = run_once(runtime)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (DecisionLogDenied, OSError) as exc:
        print(json.dumps({"status": "DENIED", "reason": str(exc),
                          "broker_action_authorized": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
