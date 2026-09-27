#!/usr/bin/env python3
"""Reproducibly sample every captured AU contract against SHFE official daily data.

One bar per contract is an integrity screen, not full-history certification.
The sample and raw SHFE responses are saved outside Git with SHA-256 hashes.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import time
from yuanli_invest.shfe_au_source import fetch_shfe


FIELDS = {
    "open": "OPENPRICE", "high": "HIGHESTPRICE", "low": "LOWESTPRICE",
    "close": "CLOSEPRICE", "volume": "VOLUME", "open_interest": "OPENINTEREST",
}


def compare_bar(bar: dict, official_raw: bytes) -> dict:
    payload = json.loads(official_raw)
    rows = payload.get("o_curinstrument")
    if not isinstance(rows, list):
        raise ValueError("SHFE daily contract rows missing")
    matches = [row for row in rows if str(row.get("PRODUCTID", "")).strip() == "au_f"
               and str(row.get("DELIVERYMONTH")) == bar["contract"][2:]]
    if len(matches) != 1:
        raise ValueError("exact official AU contract row missing or duplicated")
    official = matches[0]
    differences = {}
    for vendor_key, exchange_key in FIELDS.items():
        vendor = Decimal(str(bar[vendor_key]))
        reference = Decimal(str(official[exchange_key]))
        if vendor != reference:
            differences[vendor_key] = {"provider": str(vendor), "shfe": str(reference)}
    return {"date": bar["date"], "contract": bar["contract"],
            "provider_source_sha256": bar["source_sha256"],
            "shfe_source_sha256": hashlib.sha256(official_raw).hexdigest(),
            "differences": differences, "exact_all_six": not differences}


def audit(manifest: dict, *, fetch=fetch_shfe, pause_seconds: float = 0.5) -> tuple[dict, dict[str, bytes]]:
    if manifest.get("schema_version") != "gold-au-history-capture.v1" or manifest.get("status") != "CAPTURED":
        raise ValueError("complete AU capture manifest required")
    if pause_seconds < 0.5:
        raise ValueError("official source pacing required")
    captures = manifest.get("captures")
    if not isinstance(captures, list) or not captures or len(captures) > 120:
        raise ValueError("bounded nonempty contract list required")
    picks = []
    for capture in captures:
        bars = capture.get("bars")
        if not isinstance(bars, list) or not bars:
            raise ValueError("empty captured contract")
        raw_path = Path(capture["raw_file"])
        if hashlib.sha256(raw_path.read_bytes()).hexdigest() != capture["raw_sha256"]:
            raise ValueError("provider raw capture hash mismatch")
        for bar in bars:
            if bar["source_sha256"] != capture["raw_sha256"]:
                raise ValueError("provider bar hash mismatch")
        # Deterministic nearest weekday to the middle. Sunday-labelled provider
        # rows are quarantined separately; they cannot be an exchange trade day.
        middle = len(bars) // 2
        weekday_candidates = [row for row in bars if datetime.strptime(row["date"], "%Y-%m-%d").weekday() < 5]
        if not weekday_candidates:
            raise ValueError("contract has no weekday-labelled bar")
        picks.append(min(weekday_candidates, key=lambda row: (
            abs(bars.index(row) - middle), bars.index(row))))
    official_by_day: dict[str, bytes] = {}
    outcomes = []
    errors = []
    for bar in picks:
        day = bar["date"]
        if day not in official_by_day:
            if official_by_day:
                time.sleep(pause_seconds)
            try:
                official_by_day[day] = fetch(day)
            except (OSError, ValueError, TimeoutError) as exc:
                errors.append({"date": day, "contract": bar["contract"], "error_type": type(exc).__name__})
                continue
        try:
            outcomes.append(compare_bar(bar, official_by_day[day]))
        except (KeyError, TypeError, ValueError) as exc:
            errors.append({"date": day, "contract": bar["contract"], "error_type": type(exc).__name__})
    totals = {key: sum(key in row["differences"] for row in outcomes) for key in FIELDS}
    report = {
        "schema_version": "gold-au-shfe-contract-sample-audit.v1",
        "sample_rule": "middle captured daily bar for each dated AU contract",
        "sampling_scope": "one bar per contract; no full-history certification",
        "contract_count": len(picks), "compared_count": len(outcomes),
        "official_day_count": len(official_by_day), "errors": errors,
        "field_mismatch_counts": totals, "comparisons": outcomes,
        "contract_metadata_checked": False,
        "authority": "RESEARCH_DATA_QUALITY_ONLY",
    }
    return report, official_by_day


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.output_dir.exists():
        parser.error("output directory already exists; audit evidence is immutable")
    manifest = json.loads(arguments.manifest.read_text(encoding="utf-8"))
    report, raw_by_day = audit(manifest)
    report["generated_at"] = datetime.now(timezone.utc).isoformat()
    report["provider_manifest_sha256"] = hashlib.sha256(arguments.manifest.read_bytes()).hexdigest()
    arguments.output_dir.mkdir(parents=True)
    raw_dir = arguments.output_dir / "raw_shfe"
    raw_dir.mkdir()
    for day, raw in raw_by_day.items():
        (raw_dir / f"kx{day.replace('-', '')}.dat").write_bytes(raw)
    (arguments.output_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: report[key] for key in
                      ("contract_count", "compared_count", "official_day_count", "field_mismatch_counts", "errors")},
                     ensure_ascii=False))
    return 0 if not report["errors"] and not any(report["field_mismatch_counts"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
