#!/usr/bin/env python3
"""Verify and assemble private AU/FRED/SHFE capture manifests for GOLD2.

Dry-run is the default and writes nothing. ``--execute`` writes a new private
dataset and audit report; it never fetches, trades, or upgrades PIT quality.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile

from yuanli_invest.gold_au_dataset_assemble import assemble_dataset


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAPPING = ROOT / "config" / "ymq_gold2" / "fred_h10_mapping.v1.json"


def _private(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if any((ancestor / ".git").exists() for ancestor in (resolved, *resolved.parents)):
        raise ValueError("assembled market data must remain outside a Git worktree")
    return resolved


def _write_exclusive(path: Path, value: dict) -> None:
    encoded = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as target:
        target.write(encoded)


def run(*, au_manifest: Path, macro_manifest: Path | None, shfe_manifest: Path | None,
        mapping: Path, audit_report: Path, output_dir: Path, execute: bool,
        now: datetime | None = None) -> dict:
    current = now or datetime.now(timezone.utc)
    dataset, report = assemble_dataset(
        au_manifest_path=au_manifest,
        macro_manifest_path=macro_manifest,
        shfe_manifest_path=shfe_manifest,
        h10_mapping_path=mapping,
        audit_report_path=audit_report,
        assembled_at=current,
    )
    destination = _private(output_dir)
    if execute:
        if destination.exists():
            raise FileExistsError("choose a new immutable output directory")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".gold-au-assembly-", dir=destination.parent) as temporary:
            staging = Path(temporary)
            _write_exclusive(staging / "dataset.json", dataset)
            _write_exclusive(staging / "report.json", report)
            os.replace(staging, destination)
    return {
        "status": report["status"],
        "mode": "EXECUTE" if execute else "DRY_RUN",
        "output_dir": str(destination),
        "bars": report["assembled_bars"],
        "macro_observations": report["macro_observations"],
        "official_repair_days": report["official_repair_days"],
        "quarantined_weekend_rows": report["weekend_quarantine_count"],
        "quarantined_shfe_error_dates": report["shfe_error_date_count"],
        "quarantined_shfe_error_vendor_bars": report["shfe_error_vendor_bars_quarantined"],
        "raw_sha_verified_count": report["raw_sha_verified_count"],
        "au_manifest_sha256": report["au_manifest_sha256"],
        "macro_manifest_sha256": report["macro_manifest_sha256"],
        "shfe_manifest_sha256": report["shfe_manifest_sha256"],
        "action_authority": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--au-manifest", type=Path, required=True)
    parser.add_argument("--macro-manifest", type=Path)
    parser.add_argument("--shfe-manifest", type=Path)
    parser.add_argument("--h10-mapping", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--audit-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        receipt = run(
            au_manifest=args.au_manifest,
            macro_manifest=args.macro_manifest,
            shfe_manifest=args.shfe_manifest,
            mapping=args.h10_mapping,
            audit_report=args.audit_report,
            output_dir=args.output_dir,
            execute=args.execute,
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__, "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
