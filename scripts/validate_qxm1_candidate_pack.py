#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs" / "architecture"
QXM = ARCH / "qxm1"
B0 = ARCH / "r2_3b0"

PACK = QXM / "QXM1-FINANCIAL-MECHANICS-CAPABILITY-CANDIDATE-PACK-v0.1.md"
CONTRACTS = QXM / "QXM1-CANDIDATE-CONTRACTS-v0.1.json"
SOURCES = QXM / "QXM1-SOURCE-PROVENANCE-v0.1.json"
STATE = QXM / "QXM1-STATE.json"
REVIEW = QXM / "QXM1-HUMAN-REVIEW-CARD-v0.1.md"
ACCEPT_RECEIPT = QXM / "QXM1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
MERGE_RECEIPT = QXM / "QXM1-MERGE-RECEIPT-v0.1.json"
B0_SCHEMA = B0 / "R2-3B0-CONTRACT-SCHEMA-v0.1.json"
B0_PROFILES = B0 / "R2-3B0-P0-CONTRACT-PROFILES-v0.1.json"
B0_STATE = B0 / "R2-3B0-STATE.json"
B0_MERGE = B0 / "R2-3B0-MERGE-RECEIPT-v0.1.json"

STAGE = "QXM1_FINANCIAL_MECHANICS_CAPABILITY_CANDIDATE_PACK"
HUMAN_TOKEN = "ACCEPT_QXM1_FINANCIAL_MECHANICS_CAPABILITY_CANDIDATE_PACK"
MERGE_TOKEN = "AUTHORIZE_QXM1_MERGE"
B0_MERGE_COMMIT = "cb5ffd0f2e8e377d82c12d716e995c7b5b328e01"
QXM1_MERGE_COMMIT = "81bf6d83da7463e31c58e2d35bcabc291b580546"
EXPECTED_CANDIDATES = [
    "QXM1-CAND-01-FUNDAMENTAL-DRIVER-DECOMPOSITION",
    "QXM1-CAND-02-THREE-STATEMENT-INTEGRITY",
    "QXM1-CAND-03-CREDIT-BALANCE-SHEET-TRANSMISSION",
    "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE",
    "QXM1-CAND-05-STRESS-EXIT-LIQUIDITY",
    "QXM1-CAND-06-RETURN-SOURCE-ATTRIBUTION",
]
EXPECTED_NEW_CAPS = {
    "CAP-P-003-FUNDAMENTAL-DRIVER-DECOMPOSITION",
    "CAP-P-004-THREE-STATEMENT-INTEGRITY-CASH-CONVERSION",
    "CAP-S-004-STRESS-EXIT-LIQUIDITY",
    "CAP-CROSS-001-RETURN-SOURCE-ATTRIBUTION",
}
EXPECTED_PROFILE_CAPS = {"CAP-R-01", "CAP-V-01"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require_fields(obj, fields, context):
    missing = [field for field in fields if field not in obj]
    assert not missing, f"{context} missing fields: {missing}"


def assert_no_authority_regression(text: str):
    prohibited = [
        r"(?:force|pnx|macro)\s*(?:score|评分)\s*[:=]\s*\d+(?:\.\d+)?",
        r"recommended (?:portfolio )?weight\s*(?:=|:)\s*\d+",
        r"position size\s*(?:=|:)\s*\d+",
        r"buy\s*/\s*sell\s*(?:=|:)\s*(?:buy|sell)",
        r"live execution\s*(?:=|:)\s*(?:true|authorized)",
    ]
    for pattern in prohibited:
        assert re.search(pattern, text, flags=re.IGNORECASE) is None, pattern


def main():
    for path in [PACK, CONTRACTS, SOURCES, STATE, REVIEW, B0_SCHEMA, B0_PROFILES, B0_STATE, B0_MERGE]:
        assert path.exists(), path

    b0_state = load(B0_STATE)
    b0_merge = load(B0_MERGE)
    assert b0_state["status"] == "accepted_merged"
    assert b0_state["merge_commit"] == B0_MERGE_COMMIT
    assert b0_state["merge_receipt"] == "docs/architecture/r2_3b0/R2-3B0-MERGE-RECEIPT-v0.1.json"
    assert b0_merge["merge_commit_sha"] == B0_MERGE_COMMIT
    assert b0_merge["merge_authorization"] == "AUTHORIZE_R2_3B0_MERGE"
    assert b0_merge["pre_merge_ci"]["run_number"] == 144
    assert b0_merge["pre_merge_ci"]["conclusion"] == "success"

    schema = load(B0_SCHEMA)
    required_blocks = schema["required_blocks"]
    assert len(required_blocks) == 11

    sources = load(SOURCES)
    assert sources["stage"] == STAGE
    assert sources["authority_law"] == "Claim Authority <= Evidence Authority"
    assert sources["source_repository"] == "moonstachain/llm-wiki"
    assert len(sources["sources"]) == 9
    for source in sources["sources"]:
        assert source["authority_class"] in {"practitioner_teaching_source", "research_synthesis"}
        assert "primary_theory_authority" in source["not_usable_as"] or "primary_accounting_standard" in source["not_usable_as"] or "primary_asset_pricing_theory" in source["not_usable_as"] or "primary_macro_theory" in source["not_usable_as"] or "primary_private_market_theory" in source["not_usable_as"] or "portfolio_policy_authority" in source["not_usable_as"]
    assert sources["promotion_requirements"]["primary_source_research_required"] is True
    assert sources["admission"]["theory"] == "not_authorized"
    assert sources["admission"]["evidence"] == "not_authorized"
    assert sources["admission"]["outcome"] == "not_authorized"
    assert sources["admission"]["capability_promotion"] == "not_authorized"

    contracts = load(CONTRACTS)
    assert contracts["stage"] == STAGE
    assert contracts["status"] == "candidate_specification_only"
    assert contracts["required_blocks"] == required_blocks
    assert contracts["candidate_count"] == 6
    candidates = contracts["candidates"]
    assert [c["candidate_id"] for c in candidates] == EXPECTED_CANDIDATES
    assert len({c["candidate_id"] for c in candidates}) == 6

    required_by_block = {
        "identity": schema["identity"]["required_fields"],
        "scope_routing": schema["scope_routing"]["required_fields"],
        "theory_causal_mechanism": schema["theory_causal_mechanism"]["required_fields"],
        "evidence": schema["evidence"]["required_fields"],
        "input": schema["input"]["required_fields"],
        "inference": schema["inference"]["required_fields"],
        "output": schema["output"]["required_fields"],
        "falsification_failure": schema["falsification_failure"]["required_fields"],
        "benchmark_qualification": schema["benchmark_qualification"]["required_fields"],
        "settlement_learning": schema["settlement_learning"]["required_fields"],
    }

    new_caps = set()
    profile_caps = set()
    for candidate in candidates:
        for block in required_blocks:
            assert block in candidate, f"{candidate['candidate_id']} missing block {block}"
        for block, fields in required_by_block.items():
            require_fields(candidate[block], fields, f"{candidate['candidate_id']}::{block}")

        ident = candidate["identity"]
        output = candidate["output"]
        evidence = candidate["evidence"]
        runtime = candidate["runtime_receipt_governance"]
        settlement = candidate["settlement_learning"]
        benchmark = candidate["benchmark_qualification"]

        assert ident["maturity_state"] in {"candidate_specified", "candidate_profile_specified"}
        assert output["state_type"]
        assert output["evidence_refs"] == "required"
        assert evidence["as_of_required"] is True
        assert evidence["point_in_time_required"] is True
        assert evidence["evidence_cutoff_required"] is True
        assert evidence["falsifier_required"] is True
        assert settlement["outcome_leakage_prohibited"] is True
        assert benchmark["failure_receipts"] == "required"
        assert runtime["invocation_envelope_required"] is True
        assert runtime["research_receipt_required"] is True
        assert runtime["research_pass_implies_capital_pass"] is False
        assert runtime["capability_acceptance_implies_promotion"] is False
        assert runtime["promotion_implies_evidence_admission"] is False
        assert runtime["execution_authority"] == "none"

        role = candidate["candidate_role"]
        if role.startswith("new_capability_candidate"):
            new_caps.add(ident["capability_id"])
        elif role == "existing_capability_profile_candidate":
            profile_caps.add(ident["capability_id"])
            assert "profile_id" in ident
        else:
            raise AssertionError(f"unexpected candidate role: {role}")

        theory = candidate["theory_causal_mechanism"]
        for theory_id in theory["theory_ids"]:
            assert not theory_id.startswith("THEORY-QIN"), "Qin teaching source cannot self-promote to TheoryObject"

    assert new_caps == EXPECTED_NEW_CAPS
    assert profile_caps == EXPECTED_PROFILE_CAPS

    b0_profiles = load(B0_PROFILES)
    mother = {p["capability_id"]: p for p in b0_profiles["profiles"]}
    for candidate in candidates:
        ident = candidate["identity"]
        if ident["capability_id"] in EXPECTED_PROFILE_CAPS:
            assert ident["stable_question"] == mother[ident["capability_id"]]["stable_question"]
    r_profile = next(c for c in candidates if c["identity"]["capability_id"] == "CAP-R-01")
    assert r_profile["identity"]["semantic_parent"] == "P.capital"
    assert "not a new human world" in r_profile["identity"]["owner_scope"]
    v_profile = next(c for c in candidates if c["identity"]["capability_id"] == "CAP-V-01")
    assert v_profile["identity"]["semantic_parent"] == "V"

    governance = contracts["governance"]
    assert governance["new_top_level_human_worlds"] == 0
    assert governance["new_canonical_capabilities_admitted"] == 0
    assert governance["new_registry_objects_admitted"] == 0
    assert governance["existing_capability_semantics_mutated"] is False
    assert governance["candidate_pack_is_canon"] is False
    assert governance["implementation_authority"] == "none"
    assert governance["benchmark_execution_authority"] == "none"
    assert governance["evidence_outcome_admission_authority"] == "none"
    assert governance["trading_execution_authority"] == "none"

    state = load(STATE)
    allowed_states = {
        "candidate_started",
        "candidate_ready_for_human_review",
        "human_accepted_pending_post_acceptance_ci",
        "human_accepted_ready_for_merge",
        "accepted_merged",
    }
    assert state["stage"] == STAGE
    assert state["status"] in allowed_states
    assert state["upstream_dependency"]["required_status"] == "accepted_merged"
    assert state["upstream_dependency"]["merge_commit"] == B0_MERGE_COMMIT
    assert state["upstream_dependency"]["resolved"] is True
    assert state["candidate_count"] == 6
    assert set(state["candidate_roles"]["new_capability_candidates"]) == EXPECTED_NEW_CAPS
    assert len(state["candidate_roles"]["existing_capability_profile_candidates"]) == 2
    assert state["contract_architecture"]["required_blocks"] == 11
    assert state["contract_architecture"]["canonical_output_root"] == "ResearchState"
    assert state["source_authority"]["primary_theory_authority"] is False
    assert state["source_authority"]["independent_empirical_evidence"] is False
    assert state["constitutional_invariants"]["new_human_worlds_added"] is False
    assert state["constitutional_invariants"]["r_remains_inside_p_capital"] is True
    assert state["constitutional_invariants"]["asset_form_is_not_pricing_model"] is True
    assert state["constitutional_invariants"]["x_semantics"] == "X := (Xs, Xa, Xp)"
    assert state["constitutional_invariants"]["scalar_master_score_prohibited"] is True
    assert state["human_gate"]["token"] == HUMAN_TOKEN
    assert state["human_gate"]["acceptance_does_not_imply_implementation"] is True
    assert state["human_gate"]["acceptance_does_not_imply_promotion"] is True

    if state["status"] == "candidate_started":
        assert state["machine_qualification"] is None
        assert state["human_gate"]["decision"] == "pending"
        assert state["next_gate"] == "QXM1_MACHINE_QUALIFICATION"
    elif state["status"] == "candidate_ready_for_human_review":
        q = state["machine_qualification"]
        assert q["workflow"] == "repository-gates"
        assert q["conclusion"] == "success"
        assert q["contracts"] == "success"
        assert q["governance"] == "success"
        assert q["qxm1_candidate_pack"] == "success"
        assert q["unit_tests"] == "success"
        assert state["human_gate"]["decision"] == "pending"
        assert state["next_gate"] == "QXM1_HUMAN_REVIEW"
    else:
        assert ACCEPT_RECEIPT.exists(), ACCEPT_RECEIPT
        acceptance = load(ACCEPT_RECEIPT)
        assert acceptance["stage"] == STAGE
        assert acceptance["decision"] == HUMAN_TOKEN
        assert acceptance["pr_number"] == 36
        assert acceptance["reviewed_head_sha"] == "0b2ae99f3d5b38946e55cc600eb774831075e306"
        assert acceptance["reviewed_ci"]["run_number"] == 173
        assert acceptance["reviewed_ci"]["run_id"] == 32439720306
        assert acceptance["reviewed_ci"]["conclusion"] == "success"
        assert acceptance["reviewed_ci"]["qxm1_candidate_pack"] == "success"
        assert acceptance["boundaries_preserved"]["merge_authorized"] is False
        assert acceptance["merge_authority"] == "not_implied_by_acceptance"
        assert acceptance["next_gate"] == "QXM1_POST_ACCEPTANCE_CI"
        assert state["human_gate"]["decision"] == HUMAN_TOKEN
        assert state["human_gate"]["acceptance_receipt"] == "docs/architecture/qxm1/QXM1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
        assert state["human_gate"]["reviewed_head_sha"] == acceptance["reviewed_head_sha"]
        assert state["human_gate"]["reviewed_ci_run"] == 173
        assert state["human_review_qualification"]["run_number"] == 173
        assert state["post_acceptance_ci_required"] is True

        if state["status"] == "human_accepted_pending_post_acceptance_ci":
            assert state["merge_authority"] == "not_implied_by_acceptance"
            assert state["post_acceptance_qualification"] is None
            assert state["post_acceptance_ci_satisfied"] is False
            assert state["next_gate"] == "QXM1_POST_ACCEPTANCE_CI"
        else:
            q = state["post_acceptance_qualification"]
            assert q["workflow"] == "repository-gates"
            assert q["conclusion"] == "success"
            assert q["contracts"] == "success"
            assert q["governance"] == "success"
            assert q["qxm1_candidate_pack"] == "success"
            assert q["unit_tests"] == "success"
            assert state["post_acceptance_ci_satisfied"] is True

            if state["status"] == "human_accepted_ready_for_merge":
                assert state["merge_authority"] == "not_implied_by_acceptance"
                assert state["next_gate"] == "QXM1_MERGE"
            else:
                assert MERGE_RECEIPT.exists(), MERGE_RECEIPT
                merge = load(MERGE_RECEIPT)
                assert merge["stage"] == STAGE
                assert merge["pr_number"] == 36
                assert merge["human_acceptance"] == HUMAN_TOKEN
                assert merge["merge_authorization"] == MERGE_TOKEN
                assert merge["pre_merge_head_sha"] == "5e02e369328c355dc754d8eb2747652b7dd65eec"
                assert merge["pre_merge_ci"]["run_number"] == 183
                assert merge["pre_merge_ci"]["run_id"] == 32440277831
                assert merge["pre_merge_ci"]["conclusion"] == "success"
                assert merge["pre_merge_ci"]["contracts"] == "success"
                assert merge["pre_merge_ci"]["governance"] == "success"
                assert merge["pre_merge_ci"]["qxm1_candidate_pack"] == "success"
                assert merge["pre_merge_ci"]["unit_tests"] == "success"
                assert merge["merge_method"] == "squash"
                assert merge["merge_commit_sha"] == QXM1_MERGE_COMMIT
                assert merge["accepted_candidate_pack"]["candidate_count"] == 6
                assert merge["accepted_candidate_pack"]["candidate_pack_is_canon"] is False
                assert merge["boundaries_preserved"]["registry_admission_authorized"] is False
                assert merge["boundaries_preserved"]["capability_implementation_authorized"] is False
                assert merge["boundaries_preserved"]["capability_promotion_authorized"] is False
                assert merge["boundaries_preserved"]["benchmark_execution_authorized"] is False
                assert merge["boundaries_preserved"]["shadow_qualification_authorized"] is False
                assert merge["boundaries_preserved"]["trading_action_authorized"] is False
                assert merge["next_gate"] == "QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING"
                assert state["merge_authority"] == MERGE_TOKEN
                assert state["merge_commit"] == QXM1_MERGE_COMMIT
                assert state["merge_receipt"] == "docs/architecture/qxm1/QXM1-MERGE-RECEIPT-v0.1.json"
                assert state["pre_merge_qualification"]["validated_head_sha"] == merge["pre_merge_head_sha"]
                assert state["pre_merge_qualification"]["run_number"] == 183
                assert state["pre_merge_qualification"]["conclusion"] == "success"
                assert state["next_gate"] == "QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING"

    pack_text = PACK.read_text(encoding="utf-8")
    review_text = REVIEW.read_text(encoding="utf-8")
    require_tokens = [
        "Classical Financial Mechanics",
        "Fundamental Driver Decomposition",
        "Three-Statement Integrity & Cash Conversion",
        "Stress Exit Liquidity",
        "Return Source Attribution",
        "Asset form is not pricing model",
        HUMAN_TOKEN,
    ]
    for token in require_tokens:
        assert token in pack_text or token in review_text, token
    assert_no_authority_regression(pack_text)
    assert_no_authority_regression(review_text)
    assert_no_authority_regression(json.dumps(contracts, ensure_ascii=False))

    print("QXM1 Financial Mechanics Capability Candidate Pack validation: PASS")


if __name__ == "__main__":
    main()
