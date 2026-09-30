#!/usr/bin/env python3
"""Capture dated AU history to a private directory; never place raw data in Git.

Dry-run is the default. ``--execute`` makes bounded, read-only market-data GETs.
The result is retrospective latest-vintage evidence, not a PIT backtest.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

from yuanli_invest.youquant_au_history import contract_specs, fetch_raw, normalize_raw


def run(*, start: date, end_exclusive: date, output_dir: Path, execute: bool, limit: int = 120,
        pause_seconds: float = 0.75, fetch=fetch_raw, now=lambda: datetime.now(timezone.utc)) -> dict:
    if limit < 1 or limit > 120 or pause_seconds < 0.5:
        raise ValueError("bounded request limit and pause are required")
    specs = contract_specs(start, end_exclusive)
    if len(specs) > limit:
        raise ValueError(f"{len(specs)} contracts exceed configured request limit")
    manifest = {
        "schema_version": "gold-au-history-capture.v1", "mode": "EXECUTE" if execute else "DRY_RUN",
        "interval": [start.isoformat(), end_exclusive.isoformat()],
        "provider_id": "youquant_history", "pit_grade": "LATEST_VINTAGE_ONLY",
        "historical_release_time_verified": False, "account_auth_used": False,
        "orders_submitted": 0, "requested_contracts": [spec.symbol for spec in specs], "captures": [],
    }
    if not execute:
        return manifest
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    for index, spec in enumerate(specs):
        if index:
            time.sleep(pause_seconds)
        captured_at = now().astimezone(timezone.utc).isoformat()
        try:
            raw = fetch(spec)
            normalized = normalize_raw(raw, spec, captured_at=captured_at)
            digest = hashlib.sha256(raw).hexdigest()
            raw_path = raw_dir / f"{digest}.json"
            if raw_path.exists():
                if hashlib.sha256(raw_path.read_bytes()).hexdigest() != digest:
                    raise ValueError("existing immutable raw capture hash mismatch")
            else:
                raw_path.write_bytes(raw)
            normalized["raw_file"] = str(raw_path.resolve())
            manifest["captures"].append(normalized)
        except (OSError, ValueError, RuntimeError, TimeoutError, json.JSONDecodeError) as exc:
            manifest["captures"].append({
                "requested_symbol": spec.symbol, "request_url": spec.url(),
                "captured_at": captured_at, "status": "FAILED",
                "error_type": type(exc).__name__,
            })
    manifest["captured_at"] = now().astimezone(timezone.utc).isoformat()
    manifest["status"] = "CAPTURED" if all("bars" in row for row in manifest["captures"]) else "PARTIAL_FAILURE"
    target = output_dir / "manifest.json"
    if target.exists():
        raise FileExistsError("capture manifest already exists; choose a new output directory")
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2019, 7, 1))
    parser.add_argument("--end-exclusive", type=date.fromisoformat, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--limit", type=int, default=120)
    arguments = parser.parse_args()
    try:
        result = run(start=arguments.start, end_exclusive=arguments.end_exclusive,
                     output_dir=arguments.output_dir, execute=arguments.execute, limit=arguments.limit)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__}), file=sys.stderr)
        return 2
    print(json.dumps({"status": result.get("status", "DRY_RUN"), "contract_count": len(result["requested_contracts"]),
                      "nonempty_captures": sum(bool(row.get("bars")) for row in result["captures"]),
                      "failures": sum(row.get("status") == "FAILED" for row in result["captures"]),
                      "output_dir": str(arguments.output_dir)}, ensure_ascii=False))
    return 0 if result.get("status") != "PARTIAL_FAILURE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
