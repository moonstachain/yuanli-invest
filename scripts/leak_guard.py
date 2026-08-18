#!/usr/bin/env python3
"""Fail closed when prohibited secrets or raw artifacts enter the repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "node_modules", "dist", ".cache", "__pycache__"}
BLOCKED_SUFFIXES = {".pdf", ".xlsx", ".xls", ".parquet", ".duckdb", ".map"}
BLOCKED_NAME_PATTERNS = (
    re.compile(r"(?i)^claude.*\.pdf$"),
    re.compile(r"^AI.*选股.*\.xlsx$"),
    re.compile(r"(?i)^final_report.*\.md$"),
)
PATTERNS = {
    "absolute_local_path": re.compile(r"/(?:Users|home)/[^/\s]+/"),
    "private_key": re.compile(r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY"),
    "github_token": re.compile(r"gh[opusr]_[A-Za-z0-9_]{20,}"),
    "generic_secret": re.compile(r"(?i)(?:password|api[_-]?key|secret)\s*[:=]\s*['\"][^'\"]{8,}"),
    "legacy_gate_hash": re.compile("ODYSSEY" + r"_INVEST_(?:CLASSIC_)?GATE"),
}


def files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def main() -> int:
    findings: list[str] = []
    for path in files():
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            findings.append(f"blocked_suffix:{relative}")
            continue
        if any(pattern.match(path.name) for pattern in BLOCKED_NAME_PATTERNS):
            findings.append(f"blocked_name:{relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"unexpected_binary:{relative}")
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label}:{relative}")
    if findings:
        print("blocked_public_projection_leak")
        for finding in findings:
            print(finding)
        return 1
    print("leak_findings=0 status=valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
