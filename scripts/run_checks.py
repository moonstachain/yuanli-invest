"""Run current behavior or explicitly catalogued historical assertions.

New tests default to current. Historical assertions are listed by full test ID,
so adding a behavior test to an old file cannot silently exclude it from CI.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def historical_change(paths: list[str]) -> bool:
    prefixes = (
        "canon/", "events/", "registry/", "governance/", "receipts/",
        "docs/architecture/", "docs/os-vnext/", "docs/human-projection/",
        "docs/superpowers/", "packages/contracts/", "config/", "supabase/",
        "scripts/validate_", "scripts/verify_bootstrap", "scripts/check_governance",
        "scripts/build_canon_status", "scripts/run_checks", "tests/", ".github/",
    )
    return any(path.startswith(prefixes) for path in paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("current", "historical"), required=True)
    parser.add_argument("--changed-since", help="Audit historical assets only when relevant files changed")
    args = parser.parse_args()
    if args.scope == "historical" and args.changed_since:
        # Compare merge-base to head; never interpolate a revision into shell code.
        base = subprocess.check_output(
            ["git", "merge-base", args.changed_since, "HEAD"], cwd=ROOT, text=True,
        ).strip()
        paths = subprocess.check_output(
            ["git", "diff", "--name-only", "-z", base, "HEAD"], cwd=ROOT,
        ).decode().split("\0")
        if not historical_change(paths):
            print("Historical assets and their validators unchanged; current checks still run.")
            return 0
    catalog = json.loads((ROOT / "tests/check-scopes.json").read_text())
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    tests = list(flatten(suite))
    historical = set(catalog["historical_tests"])
    unknown = historical - {test.id() for test in tests}
    if unknown:
        raise ValueError(f"Stale historical test IDs: {sorted(unknown)}")
    selected = [test for test in tests if (test.id() in historical) == (args.scope == "historical")]
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    if not result.wasSuccessful():
        return 1
    if args.scope == "historical":
        for command in catalog["historical_commands"]:
            subprocess.run([sys.executable, *command], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
