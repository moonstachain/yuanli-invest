#!/usr/bin/env python3
"""Offline only: validate a redacted candidate; optionally preserve a new evidence bundle."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from yuanli_invest.gold_au_ctp_cost_evidence import ProbeBlocked, canonical, load_candidate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt")
    parser.add_argument("--as-of", default=None)
    parser.add_argument("--expected-investor-token", default=None)
    parser.add_argument("--output-dir")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    try:
        receipt, validation = load_candidate(args.receipt,
            as_of=args.as_of or datetime.now(timezone.utc),
            expected_investor_token=args.expected_investor_token)
        if args.execute:
            if not args.output_dir:
                raise ProbeBlocked("NEW_PRIVATE_OUTPUT_DIR_REQUIRED")
            target = Path(args.output_dir).absolute()
            for part in (target, *target.parents):
                if part.is_symlink():
                    raise ProbeBlocked("SYMLINK_PATH_FORBIDDEN")
            if target == ROOT or ROOT in target.parents:
                raise ProbeBlocked("OUTPUT_MUST_BE_OUTSIDE_REPOSITORY")
            target.mkdir(mode=0o700, parents=False, exist_ok=False)
            for name, value in (("candidate.json", receipt), ("content-validation.json", validation)):
                path = target / name
                with path.open("xb") as stream:
                    stream.write(canonical(value) + b"\n")
                path.chmod(0o600)
        print(json.dumps({"status": "CONTENT_VALIDATED_UNATTESTED", "dry_run": not args.execute,
                          "validation": validation}, sort_keys=True, ensure_ascii=False))
        return 0
    except (ProbeBlocked, OSError, ValueError, TypeError, KeyError):
        # Do not leak a file path, provider error, identifier or malformed content.
        print('{"status":"BLOCKED","reason_code":"CANDIDATE_IMPORT_REJECTED"}')
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
