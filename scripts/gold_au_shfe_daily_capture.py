#!/usr/bin/env python3
"""Capture official SHFE AU daily reports for a bounded period, read-only.

This retrospective exchange series is useful for correcting vendor daily
OHLC/date anomalies, but does not establish historical first-release times.
Dry-run by default. Raw reports and manifest are private output, not Git data.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import time

from yuanli_invest.shfe_au_source import fetch_shfe


def normalize_daily(raw: bytes, day: str) -> dict:
    payload = json.loads(raw)
    rows = payload.get("o_curinstrument")
    if not isinstance(rows, list):
        raise ValueError("SHFE daily contract rows missing")
    bars = []
    contracts = set()
    for item in rows:
        if not isinstance(item, dict) or str(item.get("PRODUCTID", "")).strip() != "au_f":
            continue
        month = str(item.get("DELIVERYMONTH", ""))
        if len(month) != 4 or not month.isdigit():
            continue
        contract = "au" + month
        try:
            fields = {name: Decimal(str(item[key])) for name, key in {
                "open": "OPENPRICE", "high": "HIGHESTPRICE", "low": "LOWESTPRICE", "close": "CLOSEPRICE",
                "volume": "VOLUME", "open_interest": "OPENINTEREST",
            }.items()}
        except (KeyError, InvalidOperation):
            # Inactive contracts may have blank OHLC; they are not tradable bars.
            continue
        if (min(fields["open"], fields["high"], fields["low"], fields["close"]) <= 0
                or fields["volume"] <= 0 or fields["open_interest"] <= 0
                or not fields["low"] <= min(fields["open"], fields["close"])
                or not max(fields["open"], fields["close"]) <= fields["high"]):
            continue
        if contract in contracts:
            raise ValueError("duplicate official AU contract row")
        contracts.add(contract)
        bars.append({"date": day, "contract": contract, **{name: str(value) for name, value in fields.items()},
                     "source_sha256": hashlib.sha256(raw).hexdigest(),
                     "pit_grade": "LATEST_VINTAGE_ONLY"})
    if not bars:
        raise ValueError("official daily report has no active AU contracts")
    return {"date": day, "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "bars": sorted(bars, key=lambda row: row["contract"])}


def run(*, provider_manifest: dict, start: date, end: date, output_dir: Path,
        execute: bool, max_requests: int = 900, pause_seconds: float = 0.5,
        fetch=fetch_shfe) -> dict:
    if provider_manifest.get("schema_version") != "gold-au-history-capture.v1":
        raise ValueError("dated provider manifest required")
    if start > end or max_requests < 1 or max_requests > 1000 or pause_seconds < 0.5:
        raise ValueError("invalid bounded capture scope")
    days = sorted({bar["date"] for capture in provider_manifest["captures"] for bar in capture["bars"]
                   if start <= date.fromisoformat(bar["date"]) <= end
                   and date.fromisoformat(bar["date"]).weekday() < 5})
    if len(days) > max_requests:
        raise ValueError(f"{len(days)} dates exceed request limit")
    summary = {"schema_version": "gold-au-shfe-daily-capture.v1",
               "mode": "EXECUTE" if execute else "DRY_RUN",
               "interval": [start.isoformat(), end.isoformat()],
               "requested_days": len(days), "historical_release_time_verified": False,
               "authority": "RETROSPECTIVE_RESEARCH_EVIDENCE_ONLY", "reports": [], "errors": []}
    if not execute:
        return summary
    if output_dir.exists():
        raise FileExistsError("choose a new immutable output directory")
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True)
    for index, day in enumerate(days):
        if index:
            time.sleep(pause_seconds)
        try:
            raw = fetch(day)
            row = normalize_daily(raw, day)
            row["captured_at"] = datetime.now(timezone.utc).isoformat()
            path = raw_dir / f"kx{day.replace('-', '')}.dat"
            path.write_bytes(raw)
            row["raw_file"] = str(path.resolve())
            summary["reports"].append(row)
        except (OSError, ValueError, TimeoutError, json.JSONDecodeError) as exc:
            summary["errors"].append({"date": day, "error_type": type(exc).__name__})
    summary["captured_at"] = datetime.now(timezone.utc).isoformat()
    summary["status"] = "CAPTURED" if not summary["errors"] else "PARTIAL_FAILURE"
    (output_dir / "manifest.json").write_text(
        json.dumps(summary, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider-manifest", type=Path, required=True)
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--max-requests", type=int, default=900)
    args = parser.parse_args()
    provider = json.loads(args.provider_manifest.read_text(encoding="utf-8"))
    result = run(provider_manifest=provider, start=args.start, end=args.end,
                 output_dir=args.output_dir, execute=args.execute, max_requests=args.max_requests)
    print(json.dumps({"status": result.get("status", "DRY_RUN"), "requested_days": result["requested_days"],
                      "reports": len(result["reports"]), "errors": len(result["errors"]),
                      "output_dir": str(args.output_dir)}, ensure_ascii=False))
    return 0 if not result["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
