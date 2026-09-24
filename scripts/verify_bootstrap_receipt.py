#!/usr/bin/env python3
"""Recompute the bootstrap artifact from the exact source commit in its receipt."""

from __future__ import annotations

import hashlib
from io import BytesIO
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "generated" / "bootstrap-exact-sha.json"


def git(*args: str, binary: bool = False, root: Path = ROOT):
    result = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True,
        text=not binary,
    )
    return result.stdout


def artifact_at(source_commit: str, root: Path = ROOT):
    """Hash exact Git blob bytes with one tree read and one batch object read."""
    entries = []
    tree = git("ls-tree", "-rz", "--full-tree", source_commit, binary=True, root=root)
    for entry in tree.split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        _, kind, object_id = metadata.split()
        relative = path.decode("utf-8")
        if relative.startswith("receipts/generated/"):
            continue
        if kind != b"blob":
            raise ValueError(f"unsupported artifact entry: {relative} ({kind.decode()})")
        entries.append((relative, object_id))
    entries.sort()
    result = subprocess.run(
        ["git", "cat-file", "--batch"], cwd=root, check=True, capture_output=True,
        input=b"".join(object_id + b"\n" for _, object_id in entries),
    )
    stream = BytesIO(result.stdout)
    rows = []
    for relative, object_id in entries:
        header = stream.readline().split()
        if len(header) != 3 or header[:2] != [object_id, b"blob"]:
            raise ValueError(f"cannot read artifact blob {relative}: {header!r}")
        size = int(header[2])
        payload = stream.read(size)
        if len(payload) != size or stream.read(1) != b"\n":
            raise ValueError(f"incomplete artifact blob: {relative}")
        rows.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
    canonical = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return rows, hashlib.sha256(canonical).hexdigest()


def main() -> int:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    source_commit = receipt["source_commit"]
    tree = git("rev-parse", f"{source_commit}^{{tree}}").strip()
    if tree != receipt["source_tree"]:
        raise SystemExit("blocked_recompute:source_tree")
    subprocess.run(["git", "merge-base", "--is-ancestor", source_commit, "HEAD"], cwd=ROOT, check=True)
    rows, artifact_hash = artifact_at(source_commit)
    if len(rows) != receipt["artifact_file_count"]:
        raise SystemExit("blocked_recompute:file_count")
    if artifact_hash != receipt["artifact_hash"]:
        raise SystemExit("blocked_recompute:artifact_hash")
    if receipt["canon_transition"]["state"] != "pending_registry_activation":
        raise SystemExit("blocked_semantic:canon_transition")
    print(
        f"source_commit={source_commit} source_tree={tree} "
        f"files={len(rows)} artifact_hash={artifact_hash} status=verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
