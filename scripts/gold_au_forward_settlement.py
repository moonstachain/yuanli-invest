#!/usr/bin/env python3
"""Offline v2 decision-to-fill-to-D+5/D+20 settlement; no account access."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if sys.version_info < (3, 12):
    raise SystemExit("gold_au_forward_settlement requires Python >= 3.12")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from yuanli_invest.gold_au_forward_settlement import assess_program, settle_forward  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--mode", choices=("settle", "assess"), default="settle")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if args.mode == "settle":
        result = settle_forward(payload)
    else:
        result = assess_program(payload["receipts"], as_of=payload["as_of"])
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.write_text(encoded, encoding="utf-8")


if __name__ == "__main__":
    main()
