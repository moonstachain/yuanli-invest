#!/usr/bin/env python3
"""Fail-closed validation for R2.1 Canon Status Reconciliation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs" / "architecture"
README = ROOT / "README.md"
CANON = ARCH / "CANON-STATUS.json"
R1_STATE = ARCH / "r1" / "R1-STATE.json"
R2_STATE = ARCH / "r2" / "R2-STATE.json"
R2_RECEIPT = ARCH / "r2" / "R2-MERGE-RECEIPT-v0.1.json"
R21_STATE = ARCH / "r2_1" / "R2-1-STATE.json"
R21_SPEC = ARCH / "r2_1" / "R2-1-CANON-STATUS-RECONCILIATION-v0.1.md"
R21_ACCEPT = ARCH / "r2_1" / "R2-1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"

R2_MERGE = "e3f14d2a603b34d39b51a521dc0f47f2b555669b"
R1_MERGE = "bfd1576e08dc836869b359773b09b3a169d09512"
R21_REVIEWED_HEAD = "bc64e2d9ee38c9794299b8d3e14c0f7b848a9130"
EXPECTED_SLICE = [
    "CAP-P-001-TECHNOLOGY-COST-CURVE",
    "CAP-N-001-NARRATIVE-VELOCITY",
    "CAP-XA-001-CONDITIONAL-TAIL-ACTIVATION",
    "CAP-V-001-REVERSE-DCF-EXPECTATIONS",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    for p in (README, CANON, R1_STATE, R2_STATE, R2_RECEIPT, R21_STATE, R21_SPEC, R21_ACCEPT):
        assert p.exists(), f"missing R2.1 reconciliation file: {p.relative_to(ROOT)}"

    r1 = load(R1_STATE)
    assert r1["status"] == "accepted_merged"
    assert r1["handoff_status"] == "complete"
    assert r1["merge_commit"] == R1_MERGE
    assert r1["r2_handoff"]["merge_commit"] == R2_MERGE
    assert r1["r2_handoff"]["status"] == "complete"

    r2 = load(R2_STATE)
    assert r2["status"] == "accepted_merged"
    assert r2["human_gate_decision"] == "ACCEPT_R2_PNXS_GOLD_CAPABILITY_PACK"
    assert r2["merge_pr"] == 19 and r2["merge_commit"] == R2_MERGE
    assert r2["post_acceptance_ci"]["run_number"] == 76
    assert r2["post_acceptance_ci"]["conclusion"] == "success"
    assert r2["capability_count"] == 12 and r2["registry_entry_count"] == 99
    assert r2["canon_entry_count"] == 0
    assert r2["r3_authority"] == "not_authorized"
    assert r2["r3a_follow_on_authority"] == "authorized_after_r2_1_merge_not_started"
    assert r2["q1_state_change"] == "none" and r2["m1_2_state_change"] == "none"

    receipt = load(R2_RECEIPT)
    assert receipt["pr_number"] == 19
    assert receipt["decision"] == "ACCEPT_R2_PNXS_GOLD_CAPABILITY_PACK"
    assert receipt["merge_commit_sha"] == R2_MERGE
    assert receipt["post_acceptance_ci"]["run_number"] == 76
    assert receipt["post_acceptance_ci"]["conclusion"] == "success"

    acceptance = load(R21_ACCEPT)
    assert acceptance["stage"] == "R2_1_CANON_STATUS_RECONCILIATION"
    assert acceptance["decision"] == "ACCEPT_R2_1_CANON_STATUS_RECONCILIATION"
    assert acceptance["pr_number"] == 20
    assert acceptance["reviewed_head_sha"] == R21_REVIEWED_HEAD
    assert acceptance["reviewed_ci"]["run_number"] == 84
    assert acceptance["reviewed_ci"]["conclusion"] == "success"
    assert acceptance["merge_authorized"] is True
    assert acceptance["merge_precondition"] == "post_acceptance_exact_head_repository_gates_success"
    assert acceptance["r3a_authority_after_merge"] == "authorized_not_started"
    assert acceptance["r4a_authority"] == "not_authorized"
    assert acceptance["live_execution"] == "unavailable_by_design"

    canon = load(CANON)
    assert canon["mission"] == "Research Capability Canon"
    assert canon["center_object"] == "ResearchCapability"
    assert canon["current_main_commit"] == R2_MERGE
    assert canon["stages"]["R1"]["status"] == "accepted_merged"
    assert canon["stages"]["R1"]["handoff_status"] == "complete"
    assert canon["stages"]["R2"]["status"] == "accepted_merged"
    assert canon["stages"]["R2"]["canon_entries"] == 0
    assert canon["stages"]["R2_1"]["status"] == "human_accepted_pending_merge"
    assert canon["stages"]["R2_1"]["decision"] == "ACCEPT_R2_1_CANON_STATUS_RECONCILIATION"
    assert canon["stages"]["R3A"]["status"] == "not_started"
    assert canon["r3a_vertical_slice"] == EXPECTED_SLICE
    assert canon["legacy_lane_reconciliation"]["M1_2"] == "closed_superseded_semantic_authority_rebase_as_runtime_state_contract"
    assert canon["legacy_lane_reconciliation"]["Q1"] == "closed_absorbed_as_wind_provider_qualification"
    assert canon["constitutional_invariants"]["x_semantics"] == "X := (Xs, Xa, Xp)"
    assert canon["constitutional_invariants"]["scalar_pnx_score"] == "prohibited"
    assert canon["constitutional_invariants"]["provider_independence"] is True
    assert canon["operational_canon"]["switch_authorized"] is False
    assert canon["admission"]["evidence"] == "not_authorized"
    assert canon["admission"]["outcome"] == "not_authorized"
    assert canon["admission"]["rsi_promotion"] == "not_authorized"
    assert canon["next_gate"] == "R2_1_MERGE"

    r21 = load(R21_STATE)
    assert r21["stage"] == "R2_1_CANON_STATUS_RECONCILIATION"
    assert r21["status"] == "human_accepted_pending_merge"
    assert r21["base_commit"] == R2_MERGE
    assert r21["human_gate_decision"] == "ACCEPT_R2_1_CANON_STATUS_RECONCILIATION"
    assert r21["reviewed_head_sha"] == R21_REVIEWED_HEAD
    assert r21["qualification_ci"]["validated_head_sha"] == R21_REVIEWED_HEAD
    assert r21["qualification_ci"]["run_number"] == 84
    assert r21["qualification_ci"]["conclusion"] == "success"
    assert r21["legacy_prs"]["m1_2_actual_state"] == "closed_superseded_runtime_state_contract"
    assert r21["legacy_prs"]["q1_actual_state"] == "closed_superseded_wind_provider_qualification"
    assert r21["r3a_vertical_slice"] == EXPECTED_SLICE
    assert r21["r3a_authority"] == "authorized_after_r2_1_merge_not_started"
    assert r21["r4a_authority"] == "not_authorized"
    assert r21["merge_authority"] == "granted_by_user"
    assert r21["merge_precondition"] == "post_acceptance_exact_head_repository_gates_success"
    assert r21["live_execution"] == "unavailable_by_design"
    assert r21["next_gate"] == "R2_1_MERGE"

    readme = README.read_text(encoding="utf-8")
    for token in (
        "R1 Capability Object Model & Registry Bootstrap：`accepted_merged`",
        "R2 PNX-S Gold Capability Pack：`accepted_merged`",
        "R2.1 Canon Status Reconciliation：`human_accepted_pending_merge`",
        "R3A Gold Vertical Slice：`not_started`",
        "README 只做人类导航，不再作为状态真源",
        "ACCEPT_R2_1_CANON_STATUS_RECONCILIATION",
        "旧 PR #16 已关闭为 superseded",
        "旧 PR #12 已关闭为 absorbed/superseded",
    ):
        assert token in readme, f"README status projection drift: {token}"

    combined = readme + "\n" + R21_SPEC.read_text(encoding="utf-8")
    assert "Xs + Xa + Xp" not in combined
    assert "X_s + X_a + X_p" not in combined

    print("R2.1 Canon Status Reconciliation validation: PASS")


if __name__ == "__main__":
    main()
