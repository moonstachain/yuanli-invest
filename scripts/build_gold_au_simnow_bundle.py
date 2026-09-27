#!/usr/bin/env python3
"""Build and verify a deterministic, credential-free GOLD2 SimNow source bundle.

This is a staging artifact, not a running YouQuant robot or a PaperGrant.  The
fixed allowlist prevents accidentally packaging research data or credentials.
Dry-run is the default; ``--execute`` creates one new private ZIP file.
"""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import stat
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "gold2-au-simnow-source-bundle.v2"
ARCHIVE_PROFILE = "EXACT_CANONICAL_ZIP_BYTES_V2"
SOURCES = {
    "youquant_gold_simnow_strategy.py": "scripts/youquant_gold_simnow_strategy.py",
    "youquant_gold_simnow_preflight.py": "scripts/youquant_gold_simnow_preflight.py",
    "yuanli_invest/__init__.py": "src/yuanli_invest/__init__.py",
    "yuanli_invest/gold_paper.py": "src/yuanli_invest/gold_paper.py",
    "yuanli_invest/gold_au_strategy_accounting.py": "src/yuanli_invest/gold_au_strategy_accounting.py",
}
MAX_SOURCE_BYTES = 1_000_000
MAX_BUNDLE_BYTES = (len(SOURCES) + 1) * MAX_SOURCE_BYTES + 65_536
ZIP_TIME = (1980, 1, 1, 0, 0, 0)


class BundleDenied(ValueError):
    """A safe reason to refuse a source bundle."""


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def source_bundle(root: Path = ROOT) -> tuple[dict[str, bytes], dict]:
    """Read only the fixed source allowlist; refuse links and oversized files."""
    root = Path(root).resolve(strict=True)
    files: dict[str, bytes] = {}
    rows = []
    for archive_path, source_path in sorted(SOURCES.items()):
        path = root / source_path
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            raise BundleDenied("SOURCE_MISSING_LINKED_OR_OUTSIDE_ROOT")
        payload = path.read_bytes()
        if not payload or len(payload) > MAX_SOURCE_BYTES:
            raise BundleDenied("SOURCE_EMPTY_OR_OVERSIZED")
        files[archive_path] = payload
        rows.append({"archive_path": archive_path, "source_path": source_path,
                     "bytes": len(payload), "sha256": _sha(payload)})
    manifest = {
        "schema_version": SCHEMA,
        "archive_profile": ARCHIVE_PROFILE,
        "status": "STAGED_SOURCE_ONLY_NOT_AUTHORIZED",
        "runtime_python_minimum": "3.12",
        "paper_grant_included": False,
        "credential_included": False,
        "broker_connection_included": False,
        "external_anchor_included": False,
        "files": rows,
        "source_set_sha256": _sha(_canonical(rows)),
    }
    files["deployment_manifest.json"] = _canonical(manifest) + b"\n"
    return files, manifest


def _entry(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, ZIP_TIME)
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.compress_type = zipfile.ZIP_STORED
    return info


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    """One canonical representation; ZIP metadata and trailing bytes are fixed."""
    raw = BytesIO()
    with zipfile.ZipFile(raw, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in sorted(files.items()):
            archive.writestr(_entry(name), payload)
    return raw.getvalue()


def build_bundle(output: Path, *, root: Path = ROOT) -> dict:
    """Create a new mode-0600 ZIP, then verify its contents before returning."""
    output = Path(output)
    if not output.is_absolute() or output.suffix != ".zip":
        raise BundleDenied("OUTPUT_MUST_BE_ABSOLUTE_ZIP")
    if not output.parent.is_dir() or output.parent.is_symlink() or output.is_symlink():
        raise BundleDenied("OUTPUT_PARENT_INVALID")
    files, manifest = source_bundle(root)
    canonical_zip = _zip_bytes(files)
    try:
        descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise BundleDenied("OUTPUT_ALREADY_EXISTS") from exc
    try:
        with os.fdopen(descriptor, "wb") as raw:
            raw.write(canonical_zip)
            raw.flush()
            os.fsync(raw.fileno())
        verified = verify_bundle(output, source_root=root)
        if verified["source_set_sha256"] != manifest["source_set_sha256"]:
            raise BundleDenied("POST_WRITE_HASH_MISMATCH")
        return verified
    except Exception:
        output.unlink(missing_ok=True)
        raise


def verify_bundle(path: Path, *, source_root: Path = ROOT) -> dict:
    """Verify exact archive bytes against the current allowlisted source tree."""
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise BundleDenied("BUNDLE_MISSING_OR_LINKED")
    if path.stat().st_size > MAX_BUNDLE_BYTES:
        raise BundleDenied("BUNDLE_OVERSIZED")
    actual_bytes = path.read_bytes()
    if len(actual_bytes) > MAX_BUNDLE_BYTES:
        raise BundleDenied("BUNDLE_OVERSIZED")
    try:
        with zipfile.ZipFile(BytesIO(actual_bytes), "r") as archive:
            infos = archive.infolist()
            expected = set(SOURCES) | {"deployment_manifest.json"}
            names = [info.filename for info in infos]
            if len(names) != len(expected) or set(names) != expected:
                raise BundleDenied("BUNDLE_FILE_SET_MISMATCH")
            for info in infos:
                if info.is_dir() or stat.S_IFMT(info.external_attr >> 16) != stat.S_IFREG:
                    raise BundleDenied("BUNDLE_NONREGULAR_ENTRY")
                if info.file_size <= 0 or info.file_size > MAX_SOURCE_BYTES:
                    raise BundleDenied("BUNDLE_ENTRY_SIZE_INVALID")
            raw_manifest = archive.read("deployment_manifest.json")
            manifest = json.loads(raw_manifest)
            if raw_manifest != _canonical(manifest) + b"\n":
                raise BundleDenied("MANIFEST_NOT_CANONICAL")
            if (set(manifest) != {"schema_version", "archive_profile", "status", "runtime_python_minimum",
                                  "paper_grant_included", "credential_included",
                                  "broker_connection_included", "external_anchor_included",
                                  "files", "source_set_sha256"}
                    or manifest.get("schema_version") != SCHEMA
                    or manifest.get("archive_profile") != ARCHIVE_PROFILE
                    or manifest.get("status") != "STAGED_SOURCE_ONLY_NOT_AUTHORIZED"
                    or manifest.get("runtime_python_minimum") != "3.12"
                    or manifest.get("paper_grant_included") is not False
                    or manifest.get("credential_included") is not False
                    or manifest.get("broker_connection_included") is not False
                    or manifest.get("external_anchor_included") is not False):
                raise BundleDenied("MANIFEST_AUTHORITY_MISMATCH")
            rows = manifest.get("files")
            if not isinstance(rows, list) or len(rows) != len(SOURCES):
                raise BundleDenied("MANIFEST_FILE_SET_MISMATCH")
            if {row.get("archive_path") for row in rows if isinstance(row, dict)} != set(SOURCES):
                raise BundleDenied("MANIFEST_FILE_SET_MISMATCH")
            for row in rows:
                name = row["archive_path"]
                payload = archive.read(name)
                if (row.get("source_path") != SOURCES[name]
                        or row.get("bytes") != len(payload)
                        or row.get("sha256") != _sha(payload)):
                    raise BundleDenied("BUNDLE_SOURCE_HASH_MISMATCH")
            if manifest.get("source_set_sha256") != _sha(_canonical(rows)):
                raise BundleDenied("BUNDLE_SET_HASH_MISMATCH")
    except (OSError, zipfile.BadZipFile, KeyError, ValueError, TypeError) as exc:
        if isinstance(exc, BundleDenied):
            raise
        raise BundleDenied("BUNDLE_INVALID") from exc
    current_files, current_manifest = source_bundle(source_root)
    if manifest["source_set_sha256"] != current_manifest["source_set_sha256"]:
        raise BundleDenied("BUNDLE_DOES_NOT_MATCH_CURRENT_SOURCE")
    if actual_bytes != _zip_bytes(current_files):
        raise BundleDenied("BUNDLE_BYTES_NOT_CANONICAL")
    return {"status": "SOURCE_BUNDLE_VERIFIED_NOT_DEPLOYED",
            "source_set_sha256": manifest["source_set_sha256"],
            "bundle_sha256": _sha(actual_bytes),
            "file_count": len(SOURCES),
            "host_compatibility_verified": False,
            "broker_connection_verified": False,
            "paper_authority_enabled": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--execute", action="store_true", help="write one new bundle at --output")
    group.add_argument("--verify", type=Path, help="verify an existing bundle only")
    parser.add_argument("--output", type=Path, help="absolute new .zip path for --execute")
    args = parser.parse_args()
    if args.verify is not None:
        result = verify_bundle(args.verify)
    elif args.execute:
        if args.output is None:
            parser.error("--execute requires --output")
        result = build_bundle(args.output)
    else:
        _, manifest = source_bundle()
        result = {"status": "DRY_RUN_NO_FILE_WRITTEN",
                  "source_set_sha256": manifest["source_set_sha256"],
                  "file_count": len(SOURCES), "paper_authority_enabled": False}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
