#!/usr/bin/env python3
"""Fail-closed QXM2 post-merge ledger/projection validation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QXM2 = ROOT / "docs" / "architecture" / "qxm2"
STATE = QXM2 / "QXM2-STATE.json"
RECEIPT = QXM2 / "QXM2-MERGE-RECEIPT-v0.1.json"
SEMANTIC_MERGE_COMMIT = "e1b7a65736c6f93089d7e635e5c72624345941fc"
MERGE_AUTHORITY = "AUTHORIZE_QXM2_MERGE"
LEGACY_NEXT_GATE = "QXM3_THEORY_HYPOTHESIS_REGISTRY_ADMISSION_BENCHMARK_PREREGISTRATION"
QXM_F_NEXT_GATE = "QXM_F_G1_SELECTIVE_ADMISSION"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    assert STATE.exists(), "missing QXM2 state"
    assert RECEIPT.exists(), "missing QXM2 merge receipt"
    state = load_json(STATE)
    receipt = load_json(RECEIPT)

    assert state["status"] == "accepted_merged"
    assert state["merge_authority"] == MERGE_AUTHORITY
    assert state["merge_commit"] == SEMANTIC_MERGE_COMMIT
    assert state["merge_receipt"] == "docs/architecture/qxm2/QXM2-MERGE-RECEIPT-v0.1.json"
    assert state["next_gate"] == LEGACY_NEXT_GATE
    assert state["qxm_f_next_gate"] == QXM_F_NEXT_GATE

    assert receipt["pr_number"] == 38
    assert receipt["human_acceptance_token"] == "ACCEPT_QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING"
    assert receipt["merge_authority"] == MERGE_AUTHORITY
    assert receipt["semantic_pre_merge_head_sha"] == "846a9c2166d770ca0a0471fc35a9cacc1b9590ea"
    assert receipt["semantic_merge_commit"] == SEMANTIC_MERGE_COMMIT
    assert receipt["merge_method"] == "squash"
    assert receipt["pre_merge_ci"]["run_number"] == 230
    assert receipt["pre_merge_ci"]["run_id"] == 32462649431
    for key in ("conclusion", "contracts", "governance", "qxm2_evidence_hardening", "unit_tests"):
        assert receipt["pre_merge_ci"][key] == "success", (key, receipt["pre_merge_ci"][key])
    assert receipt["accepted_shadow_pack"]["candidate_pack_is_canon"] is False
    assert receipt["qxm_f_next_gate"] == QXM_F_NEXT_GATE

    for key in (
        "registry_admission_authorized",
        "hypothesis_preregistration_authorized",
        "formal_benchmark_creation_authorized",
        "benchmark_execution_authorized",
        "benchmark_pass_claim_authorized",
        "capability_promotion_authorized",
        "production_runtime_authorized",
        "target_price_authorized",
        "recommended_weight_authorized",
        "position_size_authorized",
        "trading_action_authorized",
        "live_execution",
    ):
        assert receipt[key] is False, (key, receipt[key])

    print("QXM2 post-merge closure validation: PASS")


if __name__ == "__main__":
    main()
