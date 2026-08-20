#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs" / "architecture"
B0 = ARCH / "r2_3b0"
R23A = ARCH / "r2_3a"

FREEZE = B0 / "R2-3B0-CAPABILITY-CONTRACT-ARCHITECTURE-FREEZE-v0.1.md"
SCHEMA = B0 / "R2-3B0-CONTRACT-SCHEMA-v0.1.json"
PROFILES = B0 / "R2-3B0-P0-CONTRACT-PROFILES-v0.1.json"
REVIEW = B0 / "R2-3B0-HUMAN-REVIEW-CARD-v0.1.md"
STATE = B0 / "R2-3B0-STATE.json"
STATUS = ARCH / "CANON-STATUS.json"
UPSTREAM_STATE = R23A / "R2-3A-STATE.json"
UPSTREAM_RECEIPT = R23A / "R2-3A-MERGE-RECEIPT-v0.1.json"

STAGE = "R2_3B0_CAPABILITY_CONTRACT_ARCHITECTURE_FREEZE"
HUMAN_TOKEN = "ACCEPT_R2_3B0_CAPABILITY_CONTRACT_ARCHITECTURE_FREEZE"
P0 = ["CAP-R-01", "CAP-V-01", "CAP-XS-01"]
REQUIRED_BLOCKS = [
    "identity",
    "scope_routing",
    "theory_causal_mechanism",
    "evidence",
    "input",
    "inference",
    "output",
    "falsification_failure",
    "benchmark_qualification",
    "settlement_learning",
    "runtime_receipt_governance",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require_tokens(text: str, tokens):
    for token in tokens:
        assert token in text, token


def assert_no_authority_regression(text: str):
    prohibited = [
        r"target price\s+(?:is|=)\s+canonical",
        r"recommended (?:portfolio )?weight\s+(?:is|=)\s+authorized",
        r"buy\s*/\s*sell\s+(?:is|=)\s+authorized",
        r"live execution\s+(?:is|=)\s+authorized",
        r"(?:force|pnx|macro)\s*(?:score|评分)\s*[:=]\s*\d+(?:\.\d+)?",
    ]
    for pattern in prohibited:
        assert re.search(pattern, text, flags=re.IGNORECASE) is None, pattern


def main():
    for path in [FREEZE, SCHEMA, PROFILES, REVIEW, STATE, STATUS, UPSTREAM_STATE, UPSTREAM_RECEIPT]:
        assert path.exists(), path

    upstream = load(UPSTREAM_STATE)
    receipt = load(UPSTREAM_RECEIPT)
    assert upstream["status"] == "accepted_merged"
    assert upstream["merge_authority"] == "AUTHORIZE_R2_3A_MERGE"
    assert upstream["merge_commit"] == "ef3f470f7ef0ceb2b58f392d4a2bd5a5c4c691bd"
    assert receipt["merge_authorization"] == "AUTHORIZE_R2_3A_MERGE"
    assert receipt["pre_merge_ci"]["run_number"] == 133
    assert receipt["merge_commit_sha"] == upstream["merge_commit"]

    freeze = FREEZE.read_text(encoding="utf-8")
    require_tokens(freeze, [
        "one_core_three_worlds_three_gates_one_loop",
        "势 · 信 · 极｜真 · 价 · 生",
        "Claim Authority <= Evidence Authority",
        "Asset form is not pricing model",
        "X := (Xs, Xa, Xp)",
        "ResearchCapability",
        "InvocationEnvelope",
        "ResearchReceipt",
        "CAP-R-01 | Regime Causal Decomposition",
        "CAP-V-01 | Price-Implied Expectations",
        "CAP-XS-01 | Structural Asymmetry Source Mapper",
        "research_only",
        "stale",
        HUMAN_TOKEN,
    ])
    assert_no_authority_regression(freeze)

    schema = load(SCHEMA)
    assert schema["stage"] == STAGE
    assert schema["required_blocks"] == REQUIRED_BLOCKS
    assert schema["base_os_model"] == "one_core_three_worlds_three_gates_one_loop"
    assert schema["human_navigation"] == "势信极_真价生"
    assert schema["scope_routing"]["asset_form_is_not_pricing_model"] is True
    assert schema["evidence"]["law"] == "Claim Authority <= Evidence Authority"
    assert schema["evidence"]["point_in_time_required"] is True
    assert schema["input"]["provider_independent_identity"] is True
    assert schema["output"]["canonical_root"] == "ResearchState"
    assert schema["output"]["scalar_master_score_prohibited"] is True
    prohibited_outputs = set(schema["output"]["prohibited_outputs"])
    for item in ["target_price", "recommended_portfolio_weight", "position_size", "buy_sell_hold", "live_execution_instruction"]:
        assert item in prohibited_outputs
    assert schema["falsification_failure"]["fail_closed_states"] == ["insufficient_evidence", "research_only", "stale", "unsupported"]
    assert schema["benchmark_qualification"]["lookahead_prohibited"] is True
    assert schema["settlement_learning"]["outcome_leakage_prohibited"] is True
    runtime = schema["runtime_receipt_governance"]
    assert runtime["invocation_envelope_required"] is True
    assert runtime["research_receipt_required"] is True
    assert runtime["research_pass_implies_capital_pass"] is False
    assert runtime["execution_authority"] == "none"
    assert schema["n02_reunderwrite_policy"]["typed_sla_required"] is True
    assert schema["n02_reunderwrite_policy"]["universal_latency_value_frozen"] is False
    assert schema["n02_reunderwrite_policy"]["on_latency_breach"] == ["research_only", "stale"]
    assert schema["n02_reunderwrite_policy"]["required_reunderwrite_modules"] == ["V", "Xa", "Xp"]
    assert schema["human_gate_token"] == HUMAN_TOKEN

    profiles = load(PROFILES)
    assert profiles["stage"] == STAGE
    ids = [x["capability_id"] for x in profiles["profiles"]]
    assert ids == P0 and len(set(ids)) == 3
    by_id = {x["capability_id"]: x for x in profiles["profiles"]}
    r = by_id["CAP-R-01"]
    assert r["semantic_parent"] == "P.capital"
    assert r["state_type"] == "RegimeCausalState"
    assert r["minimum_state"] == ["growth", "inflation", "liquidity", "risk_appetite", "term_premium", "funding_stress", "policy_reaction_function"]
    assert "No scalar macro score" in r["hard_boundaries"]
    v = by_id["CAP-V-01"]
    assert v["state_type"] == "PriceImpliedExpectationState"
    assert "reverse_dcf" in v["asset_model_families"]["equity"]
    assert "implied_policy_path" in v["asset_model_families"]["sovereign_rates"]
    assert "Target price is not canonical output" in v["hard_boundaries"]
    xs = by_id["CAP-XS-01"]
    assert xs["state_type"] == "StructuralAsymmetrySourceState"
    assert xs["asset_implementations"]["equity"] == "value_control_point"
    assert xs["asset_implementations"]["commodity"] == "scarcity_supply_elasticity"
    assert xs["asset_implementations"]["FX"] == "policy_divergence_carry_flow"
    assert xs["asset_implementations"]["monetary_asset"] == "monetary_scarcity_reserve_demand"
    assert profiles["promotion_authority"] == "none"
    assert profiles["implementation_authority"] == "none"
    assert profiles["execution_authority"] == "none"

    state = load(STATE)
    assert state["stage"] == STAGE
    assert state["status"] in {"candidate_started", "candidate_ready_for_human_review"}
    assert state["upstream_dependency"]["required_status"] == "accepted_merged"
    assert state["upstream_dependency"]["merge_commit"] == upstream["merge_commit"]
    assert state["upstream_dependency"]["resolved"] is True
    assert state["contract_architecture"]["required_blocks"] == 11
    assert state["contract_architecture"]["canonical_output_root"] == "ResearchState"
    assert state["contract_architecture"]["invocation_envelope_required"] is True
    assert state["contract_architecture"]["research_receipt_required"] is True
    assert state["p0_capabilities"] == P0
    assert state["constitutional_invariants"]["point_in_time_required"] is True
    assert state["constitutional_invariants"]["provider_independent_identity"] is True
    assert state["constitutional_invariants"]["scalar_master_score_prohibited"] is True
    assert state["constitutional_invariants"]["research_pass_implies_capital_pass"] is False
    assert state["n02_reunderwrite_policy"]["typed_sla_required"] is True
    assert state["n02_reunderwrite_policy"]["universal_latency_value_frozen"] is False
    assert state["human_gate"]["token"] == HUMAN_TOKEN
    assert state["human_gate"]["decision"] == "pending"

    status = load(STATUS)
    assert status["stages"]["R2_3A"]["status"] == "accepted_merged"
    assert status["r2_3a_merge_fact"]["merge_commit"] == upstream["merge_commit"]
    assert status["stages"]["R2_3B0"]["status"] == state["status"]
    assert status["r2_3b0_contract_architecture"]["required_blocks"] == 11
    assert status["r2_3b0_contract_architecture"]["p0_capabilities"] == P0
    assert status["r2_3b0_contract_architecture"]["canonical_output_root"] == "ResearchState"
    assert status["next_gate"] == state["next_gate"]

    if state["status"] == "candidate_started":
        assert state["machine_qualification"] is None
        assert state["next_gate"] == "R2_3B0_MACHINE_QUALIFICATION"
    else:
        q = state["machine_qualification"]
        assert q["workflow"] == "repository-gates"
        assert q["conclusion"] == "success"
        assert q["contracts"] == "success"
        assert q["governance"] == "success"
        assert q["contract_architecture"] == "success"
        assert q["unit_tests"] == "success"
        assert state["next_gate"] == "R2_3B0_HUMAN_REVIEW"

    review = REVIEW.read_text(encoding="utf-8")
    require_tokens(review, ["D1 | Universal contract architecture", "D11 | Governance boundary", HUMAN_TOKEN])
    assert_no_authority_regression(review)

    print("R2.3-B0 capability contract architecture validation: PASS")


if __name__ == "__main__":
    main()
