#!/usr/bin/env python3
"""Verify A9 transition invariants without changing external governance state."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    status = json.loads((ROOT / "governance" / "repository-status.json").read_text(encoding="utf-8"))
    assert status["portfolio_id"] == "A9"
    assert status["decision_id"] == "YL-DEC-A9-20260818-0001"
    assert status["canon_role"] == "designated_target_canon"
    assert status["operational_canon"] == "moonstachain/quant-workspace"
    assert status["evidence_reviewer"] == "UNASSIGNED_HUMAN"
    assert status["research_admission"] == "blocked_unassigned_evidence_reviewer"
    assert status["registry_activation"] == "not_authorized"
    assert status["deployment"] == "not_authorized"

    approved = []
    for path in (ROOT / "canon").rglob("*.json"):
        item = json.loads(path.read_text(encoding="utf-8"))
        if item.get("status") == "approved":
            approved.append(str(path.relative_to(ROOT)))
    assert not approved, f"approved objects blocked while reviewer is unassigned: {approved}"
    print("governance_invariants=valid research_admission=blocked_unassigned_evidence_reviewer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
