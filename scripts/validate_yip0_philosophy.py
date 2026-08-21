#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YIP0 = ROOT / "docs" / "architecture" / "yip0"
OS = ROOT / "docs" / "os-vnext"

CANON = YIP0 / "YIP0-INVESTMENT-PHILOSOPHY-CANON-v0.1.md"
CONTRACT = YIP0 / "YIP0-PHILOSOPHY-CONTRACT-v0.1.json"
STATE = YIP0 / "YIP0-STATE.json"
REVIEW = YIP0 / "YIP0-HUMAN-REVIEW-CARD-v0.1.md"
ACCEPT_RECEIPT = YIP0 / "YIP0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
MERGE_RECEIPT = YIP0 / "YIP0-MERGE-RECEIPT-v0.1.json"
CONSTITUTION = OS / "CONSTITUTION.md"
CANON_STATUS = ROOT / "docs" / "architecture" / "CANON-STATUS.json"

STAGE = "YIP0_INVESTMENT_PHILOSOPHY_CANON"
HUMAN_TOKEN = "ACCEPT_YIP0_INVESTMENT_PHILOSOPHY_CANON"
MERGE_TOKEN = "AUTHORIZE_YIP0_MERGE"
ACCEPTED_REVIEW_HEAD = "500b1fac6771861d1222275781460fdebfafa196"
ACCEPTED_REVIEW_RUN = 220
ACCEPTED_REVIEW_RUN_ID = 32462028520
PRE_MERGE_HEAD = "112445a57f0650e423803d85288645a593844929"
PRE_MERGE_RUN = 249
PRE_MERGE_RUN_ID = 32468483237
SEMANTIC_MERGE_COMMIT = "b79581c82ca7197a9ce078baa6f3b5e8708a1e17"
MERGED_AT = "2026-08-21T09:34:17Z"
EXPECTED_AXIOMS = [f"YL-PH-{i:02d}" for i in range(1, 13)]
EXPECTED_MOTHER_LAWS = [
    "REALITY_OVER_BELIEF",
    "REFLEXIVITY",
    "TAIL_ASYMMETRY",
    "SURVIVAL_FIRST",
]
PROHIBITED_SCORE_KEYS = {
    "score",
    "master_score",
    "pnx_score",
    "force_score",
    "macro_score",
    "philosophy_score",
    "weighted_score",
    "composite_score",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def iter_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from iter_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_keys(item)


def assert_success_qualification(qualification, *, require_review=False):
    assert qualification["workflow"] == "repository-gates"
    assert qualification["conclusion"] == "success"
    assert qualification["contracts"] == "success"
    assert qualification["governance"] == "success"
    assert qualification["yip0_philosophy"] == "success"
    assert qualification["unit_tests"] == "success"
    if require_review:
        assert qualification["validated_head_sha"] == ACCEPTED_REVIEW_HEAD
        assert qualification["run_number"] == ACCEPTED_REVIEW_RUN
        assert qualification["run_id"] == ACCEPTED_REVIEW_RUN_ID
        assert qualification["formal_review"] == "12/12 PASS"


def assert_acceptance_receipt(acceptance):
    assert acceptance["stage"] == STAGE
    assert acceptance["decision"] == HUMAN_TOKEN
    assert acceptance["pr_number"] == 39
    assert acceptance["reviewed_head_sha"] == ACCEPTED_REVIEW_HEAD
    reviewed_ci = acceptance["reviewed_ci"]
    assert reviewed_ci["workflow"] == "repository-gates"
    assert reviewed_ci["run_number"] == ACCEPTED_REVIEW_RUN
    assert reviewed_ci["run_id"] == ACCEPTED_REVIEW_RUN_ID
    assert reviewed_ci["conclusion"] == "success"
    assert reviewed_ci["contracts"] == "success"
    assert reviewed_ci["governance"] == "success"
    assert reviewed_ci["yip0_philosophy"] == "success"
    assert reviewed_ci["unit_tests"] == "success"
    accepted_decisions = acceptance["accepted_decisions"]
    assert accepted_decisions["axiom_count"] == 12
    assert accepted_decisions["axiom_ids"] == EXPECTED_AXIOMS
    assert accepted_decisions["mother_laws"] == EXPECTED_MOTHER_LAWS
    assert accepted_decisions["os_model"] == "one_core_three_worlds_three_gates_one_loop"
    assert accepted_decisions["p_not_equal_n"] is True
    assert accepted_decisions["x_semantics"] == "X := (Xs, Xa, Xp)"
    assert accepted_decisions["lineage_is_not_evidence_authority_laundering"] is True
    assert accepted_decisions["scalar_master_score_prohibited"] is True
    boundaries = acceptance["boundaries_preserved"]
    assert all(value is False for value in boundaries.values())
    assert acceptance["merge_authority"] == "not_implied_by_acceptance"
    assert acceptance["required_merge_token"] == MERGE_TOKEN
    assert acceptance["post_acceptance_ci"] == "required_on_acceptance_record_head"


def main():
    for path in [CANON, CONTRACT, STATE, REVIEW, CONSTITUTION, CANON_STATUS]:
        assert path.exists(), path

    canon_text = CANON.read_text(encoding="utf-8")
    review_text = REVIEW.read_text(encoding="utf-8")
    constitution_text = CONSTITUTION.read_text(encoding="utf-8")
    contract = load_json(CONTRACT)
    state = load_json(STATE)
    status_projection = load_json(CANON_STATUS)

    # Stable identity and philosophical structure.
    assert contract["schema_version"] == "0.1.0"
    assert contract["stage"] == STAGE
    assert contract["status"] == "candidate_philosophy_authority"
    identity = contract["identity"]
    assert identity["english_name"] == "Fallibilist Reflexive Evolutionary Realism"
    assert identity["human_name_zh"] == "原力投研哲学｜可错的反身演化实在论"
    assert identity["os_identity_preserved"] == "one_core_three_worlds_three_gates_one_loop"
    assert contract["compression"] == ["实在", "可错", "反身", "演化", "凸性", "生存"]

    mother_laws = [item["id"] for item in contract["mother_laws"]]
    assert mother_laws == EXPECTED_MOTHER_LAWS
    assert len(set(mother_laws)) == 4

    axioms = contract["axioms"]
    axiom_ids = [item["id"] for item in axioms]
    assert axiom_ids == EXPECTED_AXIOMS
    assert len(set(axiom_ids)) == 12
    for axiom_id in EXPECTED_AXIOMS:
        assert canon_text.count(f"`{axiom_id}") >= 1, f"missing Canon axiom {axiom_id}"

    # Accepted OS semantics must remain unchanged.
    mapping = contract["os_mapping"]
    assert mapping["objective"] == "Lifetime Right-Tail Capture under Survival Constraints"
    assert mapping["worlds"] == {"P": "Reality", "N": "Belief", "X": "Asymmetry"}
    assert mapping["x_semantics"] == "X := (Xs, Xa, Xp)"
    assert mapping["evidence_law"] == "Claim Authority <= Evidence Authority"
    assert mapping["evidence_role"] == "horizontal_claim_control_plane"
    assert mapping["gates"]["V"] == "Price-Implied Expectations"
    assert mapping["gates"]["S"] == "Portfolio Survival"
    assert mapping["dependency_graph_is_universal_causal_law"] is False
    assert mapping["reflexivity_is_target_system_property_not_dependency_graph_rewrite"] is True

    assert "one_core_three_worlds_three_gates_one_loop" in constitution_text
    assert "`X := (Xs, Xa, Xp)`" in constitution_text
    assert "Claim Authority <= Evidence Authority" in constitution_text
    assert "Price-Implied Expectations" in constitution_text
    assert "Portfolio Survival" in constitution_text
    assert "P != N" in canon_text

    # Explicit anti-authority-laundering lineage rule.
    lineage = contract["lineage_boundary"]
    assert lineage["rule"] == "Intellectual lineage is orientation, not evidence-authority laundering."
    lineage_names = {item["name"] for item in lineage["lineages"]}
    assert lineage_names == {
        "Popper",
        "Soros",
        "Shiller",
        "Schumpeter_Kuhn_Perez",
        "Knight_Taleb_EVT_tradition",
        "Yuanli_synthesis",
    }
    assert "Intellectual lineage is not evidence-authority laundering." in canon_text

    # Required philosophical prohibitions.
    forbidden = set(contract["forbidden_interpretations"])
    for required in {
        "fourth_human_world",
        "scalar_pnx_score",
        "scalar_force_score",
        "scalar_macro_score",
        "scalar_philosophy_score",
        "arithmetic_Xs_plus_Xa_plus_Xp",
        "numeric_Xs_times_Xa_times_Xp",
        "narrative_strength_proves_reality",
        "target_price_is_canonical_V_state",
        "S_automatically_outputs_recommended_position_size",
        "philosophy_acceptance_implies_trade_authority",
    }:
        assert required in forbidden, required

    # Machine structure, not explanatory prose, is the authorization surface.
    machine_keys = set(iter_keys(contract)) | set(iter_keys(state))
    prohibited_present = sorted(PROHIBITED_SCORE_KEYS & machine_keys)
    assert not prohibited_present, f"scalar score fields prohibited: {prohibited_present}"
    assert not any(
        key.endswith("_master_score") or key.startswith("scalar_score_")
        for key in machine_keys
    ), "scalar master-score machine field prohibited"

    # Governance must remain research/philosophy-only.
    governance = contract["governance"]
    assert governance["new_human_worlds_added"] == 0
    assert governance["existing_os_semantics_mutated"] is False
    assert governance["research_capabilities_promoted"] == 0
    for field in [
        "evidence_admission_authority",
        "outcome_admission_authority",
        "benchmark_execution_authority",
        "runtime_authority",
        "target_price_authority",
        "recommended_weight_authority",
        "position_size_authority",
        "buy_sell_authority",
        "live_execution_authority",
    ]:
        assert governance[field] == "none", f"{field} must remain none"
    assert governance["active_repository_gate_override"] is False
    assert governance["parallel_candidate_track"] is True

    # Lifecycle state and Human Gate.
    allowed_states = {
        "candidate_started",
        "candidate_ready_for_human_review",
        "human_accepted_pending_post_acceptance_ci",
        "human_accepted_ready_for_merge",
        "accepted_merged",
    }
    assert state["stage"] == STAGE
    assert state["status"] in allowed_states
    invariants = state["constitutional_invariants"]
    assert invariants["os_model"] == "one_core_three_worlds_three_gates_one_loop"
    assert invariants["p_not_equal_n"] is True
    assert invariants["x_semantics"] == "X := (Xs, Xa, Xp)"
    assert invariants["evidence_role"] == "horizontal_claim_control_plane"
    assert invariants["v_identity"] == "Price-Implied Expectations"
    assert invariants["s_identity"] == "Portfolio Survival"
    assert invariants["scalar_master_score_prohibited"] is True
    assert invariants["new_human_worlds_added"] is False
    assert invariants["active_repository_gate_override"] is False

    human_gate = state["human_gate"]
    assert human_gate["token"] == HUMAN_TOKEN
    assert human_gate["acceptance_does_not_imply_merge"] is True
    assert human_gate["acceptance_does_not_imply_capability_promotion"] is True
    assert human_gate["acceptance_does_not_imply_evidence_admission"] is True
    assert human_gate["acceptance_does_not_imply_runtime_authority"] is True
    assert human_gate["acceptance_does_not_imply_trading_authority"] is True

    if state["status"] == "candidate_started":
        assert state["machine_qualification"] is None
        assert human_gate["decision"] == "pending"
        assert state["merge_authority"] == MERGE_TOKEN
        assert state["next_gate"] == "YIP0_MACHINE_QUALIFICATION"
        assert state["global_gate_behavior"] == "parallel_candidate_does_not_override_repository_next_gate"
    elif state["status"] == "candidate_ready_for_human_review":
        assert_success_qualification(state["machine_qualification"])
        assert human_gate["decision"] == "pending"
        assert state["merge_authority"] == MERGE_TOKEN
        assert state["next_gate"] == "YIP0_HUMAN_REVIEW"
        assert state["global_gate_behavior"] == "parallel_candidate_does_not_override_repository_next_gate"
    else:
        assert ACCEPT_RECEIPT.exists(), ACCEPT_RECEIPT
        acceptance = load_json(ACCEPT_RECEIPT)
        assert_acceptance_receipt(acceptance)

        assert human_gate["decision"] == HUMAN_TOKEN
        assert human_gate["accepted_at"] == acceptance["accepted_at"]
        assert human_gate["acceptance_receipt"] == "docs/architecture/yip0/YIP0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
        assert human_gate["reviewed_head_sha"] == ACCEPTED_REVIEW_HEAD
        assert human_gate["reviewed_ci_run"] == ACCEPTED_REVIEW_RUN
        assert_success_qualification(state["human_review_qualification"], require_review=True)
        assert state["required_merge_token"] == MERGE_TOKEN
        assert state["post_acceptance_ci_required"] is True

        if state["status"] == "human_accepted_pending_post_acceptance_ci":
            assert state["merge_authority"] == "not_implied_by_acceptance"
            assert state["post_acceptance_qualification"] is None
            assert state["post_acceptance_ci_satisfied"] is False
            assert state["next_gate"] == "YIP0_POST_ACCEPTANCE_CI"
            assert state["global_gate_behavior"] == "parallel_candidate_does_not_override_repository_next_gate"
        elif state["status"] == "human_accepted_ready_for_merge":
            assert state["merge_authority"] == "not_implied_by_acceptance"
            assert_success_qualification(state["post_acceptance_qualification"])
            assert state["post_acceptance_ci_satisfied"] is True
            assert state["next_gate"] == "YIP0_MERGE"
            assert state["global_gate_behavior"] == "parallel_candidate_does_not_override_repository_next_gate"
        else:
            assert state["merge_authority"] == MERGE_TOKEN
            assert state["merge_method"] == "squash"
            assert state["merge_commit"] == SEMANTIC_MERGE_COMMIT
            assert state["merge_receipt"] == "docs/architecture/yip0/YIP0-MERGE-RECEIPT-v0.1.json"
            assert state["merged_at"] == MERGED_AT
            assert state["post_acceptance_ci_satisfied"] is True
            assert state["next_gate"] == "YIP0_COMPLETE"
            assert state["next_yip_stage_authorized"] is False
            assert state["global_gate_behavior"] == "parallel_philosophy_authority_does_not_override_repository_next_gate"

            pre_merge = state["pre_merge_rebase_qualification"]
            assert_success_qualification(pre_merge)
            assert pre_merge["validated_head_sha"] == PRE_MERGE_HEAD
            assert pre_merge["run_number"] == PRE_MERGE_RUN
            assert pre_merge["run_id"] == PRE_MERGE_RUN_ID

            assert MERGE_RECEIPT.exists(), MERGE_RECEIPT
            merge_receipt = load_json(MERGE_RECEIPT)
            assert merge_receipt["stage"] == STAGE
            assert merge_receipt["pr_number"] == 39
            assert merge_receipt["human_acceptance_token"] == HUMAN_TOKEN
            assert merge_receipt["merge_authority"] == MERGE_TOKEN
            assert merge_receipt["semantic_pre_merge_head_sha"] == PRE_MERGE_HEAD
            assert merge_receipt["merge_method"] == "squash"
            assert merge_receipt["semantic_merge_commit"] == SEMANTIC_MERGE_COMMIT
            assert merge_receipt["merged_at"] == MERGED_AT
            assert merge_receipt["yip0_status"] == "accepted_merged"
            assert merge_receipt["next_yip_stage_authorized"] is False
            assert merge_receipt["conflict_resolution"]["semantic_change_to_yip0"] is False
            pre_merge_ci = merge_receipt["pre_merge_ci"]
            assert pre_merge_ci["run_number"] == PRE_MERGE_RUN
            assert pre_merge_ci["run_id"] == PRE_MERGE_RUN_ID
            assert pre_merge_ci["conclusion"] == "success"
            assert pre_merge_ci["contracts"] == "success"
            assert pre_merge_ci["governance"] == "success"
            assert pre_merge_ci["yip0_philosophy"] == "success"
            assert pre_merge_ci["unit_tests"] == "success"
            assert all(value is False for value in merge_receipt["boundaries_preserved"].values())

    assert state["repository_next_gate_expected_to_remain_external_to_yip0"] is True

    # YIP0 must not become the repository-wide active gate while it is a parallel philosophy track.
    assert status_projection["os_model"] == "one_core_three_worlds_three_gates_one_loop"
    assert status_projection["next_gate"] != STAGE
    assert status_projection["next_gate"] != "YIP0_HUMAN_REVIEW"
    assert status_projection["next_gate"] != "YIP0_MERGE"

    # Review card must expose all 12 independent review dimensions.
    for index in range(1, 13):
        assert f"## D{index} |" in review_text, f"missing D{index}"
    assert HUMAN_TOKEN in review_text
    assert MERGE_TOKEN in review_text
    if state["status"].startswith("human_accepted"):
        assert review_text.count("— PASS") >= 12
        assert "Human Decision" in review_text
        assert "YIP0_POST_ACCEPTANCE_CI" in review_text or "YIP0_MERGE" in review_text
    elif state["status"] == "accepted_merged":
        assert review_text.count("— PASS") >= 12
        assert "Status: `accepted_merged`" in review_text
        assert "Merge Decision" in review_text
        assert "`YIP0_COMPLETE`" in review_text
        assert "YIP0-MERGE-RECEIPT-v0.1.json" in review_text

    print("YIP0 philosophy canon validation: PASS")


if __name__ == "__main__":
    main()
