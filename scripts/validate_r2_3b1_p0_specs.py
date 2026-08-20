#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs" / "architecture"
B0 = ARCH / "r2_3b0"
B1 = ARCH / "r2_3b1"

B0_STATE = B0 / "R2-3B0-STATE.json"
B0_RECEIPT = B0 / "R2-3B0-MERGE-RECEIPT-v0.1.json"
MASTER = B1 / "R2-3B1-P0-CAPABILITY-CONTRACT-SPECIFICATION-v0.1.md"
STATE = B1 / "R2-3B1-STATE.json"
REVIEW = B1 / "R2-3B1-HUMAN-REVIEW-CARD-v0.1.md"
SPECS = {
    "CAP-R-01": B1 / "CAP-R-01-SPEC-v0.1.json",
    "CAP-V-01": B1 / "CAP-V-01-SPEC-v0.1.json",
    "CAP-XS-01": B1 / "CAP-XS-01-SPEC-v0.1.json",
}

STAGE = "R2_3B1_P0_CAPABILITY_CONTRACT_SPECIFICATION"
TOKEN = "ACCEPT_R2_3B1_P0_CAPABILITY_CONTRACT_SPECIFICATION"
REQUIRED_BLOCKS = [
    "identity", "scope_routing", "theory_causal_mechanism", "evidence", "input",
    "inference", "output", "falsification_failure", "benchmark_qualification",
    "settlement_learning", "runtime_receipt_governance",
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond, msg):
    assert cond, msg


def main():
    for path in [B0_STATE, B0_RECEIPT, MASTER, STATE, REVIEW, *SPECS.values()]:
        require(path.exists(), f"missing {path}")

    b0 = load(B0_STATE)
    receipt = load(B0_RECEIPT)
    require(b0["status"] == "accepted_merged", "B0 not merged")
    require(b0["merge_commit"] == "cb5ffd0f2e8e377d82c12d716e995c7b5b328e01", "wrong B0 merge commit")
    require(receipt["merge_authorization"] == "AUTHORIZE_R2_3B0_MERGE", "missing B0 merge authority")
    require(receipt["pre_merge_ci"]["run_number"] == 144, "wrong B0 qualification")

    state = load(STATE)
    require(state["stage"] == STAGE, "wrong stage")
    require(state["status"] in {"candidate_started", "candidate_ready_for_human_review", "human_accepted_ready_for_merge"}, "bad status")
    require(state["upstream_dependency"]["resolved"] is True, "upstream unresolved")
    require(state["required_contract_blocks"] == 11, "wrong block count")
    require(state["p0_capabilities"] == ["CAP-R-01", "CAP-V-01", "CAP-XS-01"], "wrong P0 order")
    require(state["human_gate"]["token"] == TOKEN, "wrong token")

    specs = {k: load(v) for k, v in SPECS.items()}
    for cap_id, spec in specs.items():
        require(spec["stage"] == STAGE, f"{cap_id} wrong stage")
        for block in REQUIRED_BLOCKS:
            require(block in spec, f"{cap_id} missing {block}")
        require(spec["identity"]["capability_id"] == cap_id, f"{cap_id} identity mismatch")
        require(spec["identity"]["maturity_state"] == "specified", f"{cap_id} not specified")
        require(spec["evidence"]["as_of_required"] is True, f"{cap_id} as_of")
        require(spec["evidence"]["point_in_time_required"] is True, f"{cap_id} PIT")
        require(spec["evidence"]["evidence_cutoff_required"] is True, f"{cap_id} cutoff")
        require(spec["runtime_receipt_governance"]["invocation_envelope_required"] is True, f"{cap_id} envelope")
        require(spec["runtime_receipt_governance"]["research_receipt_required"] is True, f"{cap_id} receipt")
        require(spec["runtime_receipt_governance"]["research_pass_implies_capital_pass"] is False, f"{cap_id} capital leak")
        require(spec["runtime_receipt_governance"]["implementation_authority"] == "not_authorized_in_B1", f"{cap_id} implementation leak")
        require(spec["runtime_receipt_governance"]["promotion_authority"] == "none", f"{cap_id} promotion leak")
        require(spec["runtime_receipt_governance"]["execution_authority"] == "none", f"{cap_id} execution leak")
        require("target_price" in spec["output"]["prohibited_outputs"], f"{cap_id} target price leak")

    r = specs["CAP-R-01"]
    require(r["identity"]["semantic_parent"] == "P.capital", "R parent")
    require(r["output"]["state_type"] == "RegimeCausalState", "R state type")
    require(r["output"]["state_dimensions"] == ["growth", "inflation", "liquidity", "risk_appetite", "term_premium", "funding_stress", "policy_reaction_function"], "R dimensions")
    require("single_rate_level" in r["benchmark_qualification"]["simpler_baselines"], "R baseline")
    require("scalar_macro_score" in r["output"]["prohibited_outputs"], "R scalar guard")

    v = specs["CAP-V-01"]
    require(v["identity"]["semantic_parent"] == "V", "V parent")
    require(v["output"]["state_type"] == "PriceImpliedExpectationState", "V state type")
    require("reverse_dcf" in v["asset_model_families"]["equity"], "V equity router")
    require("implied_policy_path" in v["asset_model_families"]["sovereign_rates"], "V rates router")
    require("implied_volatility_surface" in v["asset_model_families"]["derivative"], "V derivative router")
    require("underidentified" in v["output"]["degrade_state"], "V underidentification guard")
    require("canonical_upside_percentage" in v["output"]["prohibited_outputs"], "V upside leak")

    xs = specs["CAP-XS-01"]
    require(xs["identity"]["semantic_parent"] == "Xs", "Xs parent")
    require(xs["output"]["state_type"] == "StructuralAsymmetrySourceState", "Xs state type")
    require(xs["asset_implementations"]["equity"] == "value_control_point", "Xs equity")
    require(xs["asset_implementations"]["commodity"] == "scarcity_supply_elasticity", "Xs commodity")
    require(xs["asset_implementations"]["FX"] == "policy_divergence_carry_flow", "Xs FX")
    require(xs["asset_implementations"]["monetary_asset"] == "monetary_scarcity_reserve_demand", "Xs gold")
    require(xs["downstream_dependencies"] if False else True, "noop")
    require("Xa" in xs["output"]["downstream_dependencies"] and "Xp" in xs["output"]["downstream_dependencies"] and "S" in xs["output"]["downstream_dependencies"], "Xs boundaries")

    master = MASTER.read_text(encoding="utf-8")
    for token in ["势 · 信 · 极｜真 · 价 · 生", "Research PASS != Capital PASS", "B2-R", "B2-V", "B2-XS", TOKEN]:
        require(token in master, f"master missing {token}")
    review = REVIEW.read_text(encoding="utf-8")
    for token in ["D1｜B0 contract inheritance", "D12｜Governance boundary", TOKEN]:
        require(token in review, f"review missing {token}")

    if state["status"] == "candidate_started":
        require(state["machine_qualification"] is None, "premature qualification")
        require(state["next_gate"] == "R2_3B1_MACHINE_QUALIFICATION", "wrong machine gate")
    elif state["status"] == "candidate_ready_for_human_review":
        q = state["machine_qualification"]
        require(q["conclusion"] == "success", "qualification not success")
        require(q["contracts"] == "success", "contracts not success")
        require(q["governance"] == "success", "governance not success")
        require(q["p0_specification"] == "success", "spec not success")
        require(q["unit_tests"] == "success", "tests not success")
        require(state["next_gate"] == "R2_3B1_HUMAN_REVIEW", "wrong human gate")

    print("R2.3-B1 P0 capability specification validation: PASS")


if __name__ == "__main__":
    main()
