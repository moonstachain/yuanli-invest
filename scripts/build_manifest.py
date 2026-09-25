#!/usr/bin/env python3
"""Build a deterministic content manifest without timestamps."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".venv", "node_modules", "dist", ".cache", "__pycache__"}


def records(root: Path = ROOT):
    rows = []
    for directory, subdirs, filenames in os.walk(root):
        base = Path(directory)
        subdirs[:] = [
            name for name in subdirs
            if name not in EXCLUDED_DIRS
            and (base / name).relative_to(root).as_posix() != "receipts/generated"
        ]
        for name in filenames:
            path = base / name
            if name in EXCLUDED_DIRS or not path.is_file():
                continue
            payload = path.read_bytes()
            rows.append({"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
    return sorted(rows, key=lambda row: Path(row["path"]))


def build(root: Path = ROOT):
    rows = records(root)
    canonical = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return {"schema_version": "1.0.0", "files": rows, "artifact_hash": hashlib.sha256(canonical).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    first = build()
    if args.check and first != build():
        raise SystemExit("blocked_recompute")
    rendered = json.dumps(first, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(f"files={len(first['files'])} artifact_hash={first['artifact_hash']} deterministic=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
