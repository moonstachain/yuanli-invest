#!/usr/bin/env python3
"""Recompute the bootstrap artifact from the exact source commit in its receipt."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "generated" / "bootstrap-exact-sha.json"


def git(*args: str, binary: bool = False):
    result = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True,
        text=not binary,
    )
    return result.stdout


def artifact_at(source_commit: str):
    paths = git("-c", "core.quotePath=false", "ls-tree", "-r", "--name-only", source_commit).splitlines()
    rows = []
    for relative in sorted(paths):
        if relative.startswith("receipts/generated/"):
            continue
        payload = git("show", f"{source_commit}:{relative}", binary=True)
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
