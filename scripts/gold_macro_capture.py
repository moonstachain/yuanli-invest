#!/usr/bin/env python3
"""Capture FRED-distributed DFII10 and DTWEXBGS CSV to a private directory.

Default mode is a dry run. ``--execute`` performs exactly two bounded public
GETs and writes immutable raw bytes plus a manifest. Historical rows remain
UNKNOWN point-in-time grade; this cannot activate a trading signal.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from yuanli_invest.gold_macro_capture import MacroSpec, fetch_raw, normalize_raw


def _private_output(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if any((ancestor / ".git").exists() for ancestor in (resolved, *resolved.parents)):
        raise ValueError("macro raw output must be outside a Git worktree")
    return resolved


def _write_exclusive(path: Path, payload: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as target:
            target.write(payload)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def run(*, start: date, end_inclusive: date, output_dir: Path, execute: bool,
        pause_seconds: float = 0.75, fetch=fetch_raw,
        now=lambda: datetime.now(timezone.utc)) -> dict:
    if pause_seconds < 0.5:
        raise ValueError("capture pacing must be at least 0.5 seconds")
    specs = [MacroSpec(series, start, end_inclusive) for series in ("DFII10", "DTWEXBGS")]
    target = _private_output(output_dir)
    manifest = {
        "schema_version": "gold-macro-capture.v1",
        "mode": "EXECUTE" if execute else "DRY_RUN",
        "interval": [start.isoformat(), end_inclusive.isoformat()],
        "provider_id": "fred_graph_csv",
        "source_urls": [spec.url() for spec in specs],
        "historical_release_time_verified": False,
        "pit_grade": "UNKNOWN",
        "authority": "RESEARCH_EVIDENCE_ONLY",
        "action_authority": "none",
        "account_auth_used": False,
        "orders_submitted": 0,
        "captures": [],
    }
    if not execute:
        manifest["status"] = "DRY_RUN"
        return manifest
    if (target / "manifest.json").exists():
        raise FileExistsError("immutable macro capture manifest already exists")
    target.mkdir(parents=True, exist_ok=True, mode=0o700)
    raw_dir = target / "raw"
    raw_dir.mkdir(exist_ok=True, mode=0o700)
    for index, spec in enumerate(specs):
        if index:
            time.sleep(pause_seconds)
        capture_at = now()
        failure_stage = "FETCH"
        try:
            raw = fetch(spec)
            failure_stage = "NORMALIZE"
            normalized = normalize_raw(raw, spec, captured_at=capture_at)
            if not normalized["observations"]:
                raise ValueError("macro capture returned no numeric observations")
            failure_stage = "PERSIST"
            digest = hashlib.sha256(raw).hexdigest()
            raw_path = raw_dir / f"{spec.provider_series.lower()}-{digest}.csv"
            if raw_path.exists():
                if hashlib.sha256(raw_path.read_bytes()).hexdigest() != digest:
                    raise ValueError("existing immutable macro raw capture hash mismatch")
            else:
                _write_exclusive(raw_path, raw)
            normalized["raw_file"] = str(raw_path)
            normalized["status"] = "CAPTURED"
            manifest["captures"].append(normalized)
        except (OSError, ValueError, TimeoutError, subprocess.TimeoutExpired) as exc:
            manifest["captures"].append({
                "provider_series": spec.provider_series,
                "source_url": spec.url(),
                "status": "FAILED",
                "error_type": type(exc).__name__,
                "failure_stage": failure_stage,
            })
    captured_at = now()
    if captured_at.tzinfo is None or captured_at.utcoffset() is None:
        raise ValueError("capture clock must be timezone-aware")
    manifest["captured_at"] = captured_at.astimezone(timezone.utc).isoformat()
    manifest["status"] = "CAPTURED" if all(row["status"] == "CAPTURED" for row in manifest["captures"]) else "PARTIAL_FAILURE"
    encoded = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    _write_exclusive(target / "manifest.json", encoded)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2019, 7, 1))
    parser.add_argument("--end-inclusive", type=date.fromisoformat, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        result = run(start=args.start, end_inclusive=args.end_inclusive,
                     output_dir=args.output_dir, execute=args.execute)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__}), file=sys.stderr)
        return 2
    print(json.dumps({
        "status": result["status"],
        "row_counts": {item["provider_series"]: item.get("row_count", 0) for item in result["captures"]},
        "output_dir": str(args.output_dir),
        "historical_release_time_verified": False,
        "action_authority": "none",
    }, ensure_ascii=False))
    return 0 if result["status"] != "PARTIAL_FAILURE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
