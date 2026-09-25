#!/usr/bin/env python3
"""Compatibility CLI for the strict exact-instant first-release offline method."""

import argparse
import json
from pathlib import Path

from yuanli_invest.future_settlement import AUTHORITY, IDENTITY_FIELDS, settle
from yuanli_invest.receipts import canonical_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = settle(json.loads(args.input.read_text(encoding="utf-8")))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "error_type": type(exc).__name__, "error": str(exc), "authority": AUTHORITY}, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
