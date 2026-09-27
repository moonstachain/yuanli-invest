#!/usr/bin/env python3
"""Build a separate, inert host diagnostic from the audited GOLD2 source.

The generated YouQuant strategy exercises only pure core functions.  It does
not inspect an exchange, call a command API, create a grant, or enter the
production runtime.  Its source includes the exact pinned single-file bundle
so a host run can check that bundle's Python imports and definitions too.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

try:
    from scripts.build_gold_au_simnow_single_file import build_source
except ModuleNotFoundError:
    from build_gold_au_simnow_single_file import build_source


DIAGNOSTIC_TAIL = '''
# The diagnostic main deliberately replaces the unconfigured paper entrypoint.
# No broker object, command, persistence, or order method is referenced here.
import sys as _gold2_diag_sys

def main():
    report = {
        "schema_version": "gold2-au-simnow-core-dryrun.v1",
        "status": "CORE_DRYRUN_BLOCKED",
        "reason_code": None,
        "stage": "precheck",
        "python_version": "%s.%s.%s" % tuple(_gold2_diag_sys.version_info[:3]),
        "python_39_or_later": _gold2_diag_sys.version_info >= (3, 9),
        "bundle_sha256": "__BUNDLE_SHA256__",
        "runtime_injected": globals().get("GOLD2_SIMNOW_RUNTIME") is not None,
        "broker_api_calls": 0,
        "order_api_calls": 0,
        "paper_authority_enabled": False,
        "broker_connection_verified": False,
    }
    try:
        if not report["python_39_or_later"]:
            report["reason_code"] = "PYTHON_VERSION_UNSUPPORTED"
        elif report["runtime_injected"]:
            report["reason_code"] = "UNEXPECTED_RUNTIME_PRESENT"
        else:
            report["stage"] = "timezone"
            at = datetime(2026, 9, 25, 8, 30, tzinfo=SHANGHAI)
            if at.utcoffset() != timedelta(hours=8):
                raise ValueError("SHANGHAI_TIMEZONE_INVALID")
            report["stage"] = "action_hash"
            digest = action_hash({"dryrun": "GOLD2_AU", "version": 1})
            if not isinstance(digest, str) or not digest.startswith("sha256:") or len(digest) != 71:
                raise ValueError("ACTION_HASH_INVALID")
            report["stage"] = "event_chain"
            ledger = PaperLedger()
            ledger.append("DryRunObserved", "CMD-GOLD2-HOST-DRYRUN-001",
                          at.astimezone(timezone.utc).isoformat(),
                          {"action_hash": digest})
            ledger.verify_chain()
            if len(ledger.events) != 1 or not ledger.root_hash.startswith("sha256:") or len(ledger.root_hash) != 71:
                raise ValueError("LEDGER_CHAIN_INVALID")
            report["status"] = "CORE_PURE_FUNCTIONS_OBSERVED"
            report["reason_code"] = "NONE"
            report["stage"] = "complete"
    except Exception:
        # Do not expose provider or host exception text in logs.
        report["reason_code"] = "PURE_CORE_EXCEPTION"
    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"))
    logger = globals().get("Log")
    if callable(logger):
        logger("GOLD2_SIMNOW_CORE_DRYRUN", rendered)
    else:
        print(rendered)
    return report
'''


def build_diagnostic_source() -> bytes:
    bundle = build_source()
    bundle_sha256 = hashlib.sha256(bundle).hexdigest()
    tail = DIAGNOSTIC_TAIL.replace("__BUNDLE_SHA256__", "sha256:" + bundle_sha256)
    payload = bundle + tail.encode("utf-8")
    compile(payload, "gold2_au_simnow_core_dryrun.py", "exec")
    return payload


def write_diagnostic(path: Path) -> dict:
    path = Path(path)
    if not path.is_absolute() or path.suffix != ".py" or not path.parent.is_dir():
        raise ValueError("OUTPUT_MUST_BE_ABSOLUTE_PY_IN_EXISTING_DIRECTORY")
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError("OUTPUT_LINK_DENIED")
    payload = build_diagnostic_source()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as raw:
            raw.write(payload)
            raw.flush()
            os.fsync(raw.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return {"status": "CORE_DRYRUN_STAGED_NOT_DEPLOYED",
            "sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload), "paper_authority_enabled": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="write a new private diagnostic .py; omit for dry-run")
    args = parser.parse_args()
    if args.output is None:
        payload = build_diagnostic_source()
        result = {"status": "DRY_RUN_NO_FILE_WRITTEN",
                  "sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
                  "bytes": len(payload), "paper_authority_enabled": False}
    else:
        result = write_diagnostic(args.output)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
