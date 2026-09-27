#!/usr/bin/env python3
"""Assemble local AU research request/evidence; no network, schedule or orders.

Dry run is the default. --execute writes a local evidence record and, only
when all required inputs validate, a request for the existing 08:30 worker.
It never manufactures the official source receipts named by the catalog.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

if sys.version_info < (3, 12):
    raise SystemExit("gold_au_daily_request requires Python >= 3.12")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.gold_au_decision_worker import _private_root  # noqa: E402
from yuanli_invest.gold_au_daily_request import assemble_daily_request  # noqa: E402
from yuanli_invest.gold_au_live_snapshot import SHANGHAI  # noqa: E402
from yuanli_invest.receipts import canonical_hash  # noqa: E402


def _private_child(root: Path, name: str) -> Path:
    child = root / name
    if not child.exists():
        child.mkdir(mode=0o700)
    mode = child.stat()
    if child.is_symlink() or not stat.S_ISDIR(mode.st_mode) or mode.st_uid != os.getuid() or stat.S_IMODE(mode.st_mode) != 0o700:
        raise ValueError("INSECURE_OUTPUT_DIRECTORY")
    return child


def _exclusive_json(path: Path, value: dict) -> None:
    encoded = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    fd, temporary = tempfile.mkstemp(prefix=".request-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            # Atomically publish complete bytes without replacing another day
            # or exposing a partially written file to the 08:30 worker.
            os.link(temporary, path)
        except FileExistsError:
            mode = path.stat()
            if (path.is_symlink() or not stat.S_ISREG(mode.st_mode) or mode.st_uid != os.getuid()
                    or stat.S_IMODE(mode.st_mode) != 0o600 or path.read_bytes() != encoded):
                raise
            # Identical replay after a restart is a no-op; history is immutable.
    finally:
        os.unlink(temporary)


def run(runtime_dir: Path, *, as_of: datetime, sources_path: Path | None = None,
        decision_date: str | None = None, execute: bool = False) -> dict:
    runtime = _private_root(runtime_dir)
    if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("TIMEZONE_AWARE_ASSEMBLY_TIME_REQUIRED")
    day = decision_date or as_of.astimezone(SHANGHAI).date().isoformat()
    if date.fromisoformat(day).isoformat() != day:
        raise ValueError("ISO_DECISION_DATE_REQUIRED")
    catalog_path = sources_path or runtime / "daily_request_sources.json"
    # Only the explicitly named, bounded JSON catalog is read; no discovery of
    # config files or credentials under the private runtime is performed.
    try:
        if catalog_path.is_symlink() or catalog_path.stat().st_size > 100_000:
            raise ValueError
        catalog_bytes = catalog_path.read_bytes()
        catalog = json.loads(catalog_bytes)
    except (OSError, UnicodeError, ValueError):
        catalog = None
    result = assemble_daily_request(catalog, runtime_dir=runtime, decision_date=day, as_of=as_of)
    if catalog is not None:
        result["source_catalog_bytes_sha256"] = hashlib.sha256(catalog_bytes).hexdigest()
        result["source_catalog_path"] = str(catalog_path.absolute())
    result["mode"] = "EXECUTE_LOCAL_ONLY" if execute else "DRY_RUN"
    if execute:
        evidence_dir = _private_child(runtime, "request_evidence")
        day_dir = _private_child(evidence_dir, day)
        evidence_path = day_dir / (canonical_hash(result) + ".json")
        if result["status"] == "READY_OFFLINE_CANDIDATE":
            requests_dir = _private_child(runtime, "requests")
            request_path = requests_dir / (day + ".json")
            # Check both destinations before either immutable write. The
            # exclusive writes still prevent races; no existing day is edited.
            _exclusive_json(evidence_path, result)
            _exclusive_json(request_path, result["request"])
        else:
            _exclusive_json(evidence_path, result)
        result["evidence_path"] = str(evidence_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", required=True, type=Path)
    parser.add_argument("--sources", type=Path, help="Explicit local source catalog; defaults to runtime/daily_request_sources.json")
    parser.add_argument("--as-of", help="Explicit aware assembly time for offline use; defaults to host clock")
    parser.add_argument("--decision-date", help="YYYY-MM-DD; defaults to Shanghai date at as-of")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        observed = datetime.fromisoformat(args.as_of.replace("Z", "+00:00")) if args.as_of else datetime.now(timezone.utc)
        result = run(args.runtime_dir, as_of=observed, sources_path=args.sources,
                     decision_date=args.decision_date, execute=args.execute)
        summary = {key: value for key, value in result.items() if key not in {"request", "source_inventory"}}
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0 if result["status"] == "READY_OFFLINE_CANDIDATE" else 2
    except (OSError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "DENIED", "reason": type(exc).__name__,
                          "broker_action_authorized": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
