"""Offline descriptive AU attribution. No account or broker imports."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from yuanli_invest.gold_au_attribution import build_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--assembly-report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    dataset_raw = args.dataset.read_bytes()
    assembly_raw = args.assembly_report.read_bytes()
    report = build_report(
        json.loads(dataset_raw), dataset_sha256=hashlib.sha256(dataset_raw).hexdigest(),
        assembly_report=json.loads(assembly_raw),
        assembly_report_sha256=hashlib.sha256(assembly_raw).hexdigest(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "aligned_pairs": report["alignment"]["aligned_pairs"],
                      "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
