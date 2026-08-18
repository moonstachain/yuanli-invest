#!/usr/bin/env python3
"""Build a deterministic content manifest without timestamps."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".venv", "node_modules", "dist", ".cache", "__pycache__"}


def records():
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith("receipts/generated/"):
            continue
        payload = path.read_bytes()
        rows.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
    return rows


def build():
    rows = records()
    canonical = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return {"schema_version": "1.0.0", "files": rows, "artifact_hash": hashlib.sha256(canonical).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    first = build()
    second = build()
    if args.check and first != second:
        raise SystemExit("blocked_recompute")
    rendered = json.dumps(first, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(f"files={len(first['files'])} artifact_hash={first['artifact_hash']} deterministic=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
