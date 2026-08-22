#!/usr/bin/env python3
"""Fail-closed validator for the SDR0 sovereign-debt repression profile candidate."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SDR0 = ROOT / "docs" / "architecture" / "sdr0"
CONTRACT_PATH = SDR0 / "SDR0-CAPABILITY-PROFILE-CONTRACT-v0.1.json"
SOURCE_PATH = SDR0 / "SDR0-SOURCE-PROVENANCE-v0.1.json"
STATE_PATH = SDR0 / "SDR0-STATE.json"
DESIGN_PATH = SDR0 / "SDR0-SOVEREIGN-DEBT-REPRESSION-REAL-VALUE-DILUTION-v0.1.md"
REVIEW_PATH = SDR0 / "SDR0-HUMAN-REVIEW-CARD-v0.1.md"
B0_PROFILE_PATH = ROOT / "docs" / "architecture" / "r2_3b0" / "R2-3B0-P0-CONTRACT-PROFILES-v0.1.json"
QXM1_STATE_PATH = ROOT / "docs" / "architecture" / "qxm1" / "QXM1-STATE.json"

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

EXPECTED_PROFILE_ID = "SDR0-PROFILE-SOVEREIGN-DEBT-REPRESSION-REAL-VALUE-DILUTION"
EXPECTED_GATE = "ACCEPT_SDR0_SOVEREIGN_DEBT_REPRESSION_REAL_VALUE_DILUTION_DESIGN"
EXPECTED_GOLD_REPLAYS = {
    "US_1942_1951_TREASURY_FED_PEG",
    "JAPAN_2016_2024_YCC",
}
EXPECTED_HARD_NEGATIVES = {
    "US_2020_PANDEMIC_QE",
    "UK_2022_LDI_GILT_INTERVENTION",
    "FIMA_REPO_LIQUIDITY_BACKSTOP",
}
EXPECTED_AND_REQUIREMENTS = {
    "fiscal_or_debt_service_pressure_elevated_and_persistent",
    "policy_evidence_supports_systematic_suppression_or_captive_demand_beyond_market_function_support",
    "creditor_real_returns_materially_negative_or_purchasing_power_dilution_observed_over_declared_horizon",
    "at_least_one_major_competing_explanation_tested_and_bounded",
    "minimum_evidence_authority_satisfied",
}
PROHIBITED_OUTPUTS = {
    "soft_default",
    "target_price",
    "recommended_portfolio_weight",
    "position_size",
    "buy_sell_hold",
    "live_execution_instruction",
    "weighted_master_score",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def cap_r01_profile() -> dict:
    profiles = load_json(B0_PROFILE_PATH).get("profiles", [])
    matches = [p for p in profiles if p.get("capability_id") == "CAP-R-01"]
    require(len(matches) == 1, "SDR0: CAP-R-01 mother profile must resolve exactly once")
    return matches[0]


def validate_files_exist() -> None:
    for path in (CONTRACT_PATH, SOURCE_PATH, STATE_PATH, DESIGN_PATH, REVIEW_PATH):
        require(path.exists(), f"SDR0: missing required artifact {path.relative_to(ROOT)}")


def validate_identity(contract: dict, mother: dict) -> None:
    identity = contract["identity"]
    require(contract.get("mother_capability") == "CAP-R-01", "SDR0: mother capability must remain CAP-R-01")
    require(identity.get("capability_id") == "CAP-R-01", "SDR0: capability_id must remain CAP-R-01")
    require(identity.get("profile_id") == EXPECTED_PROFILE_ID, "SDR0: profile_id drift")
    require(identity.get("stable_question") == mother.get("stable_question"), "SDR0: CAP-R-01 mother stable question drift")
    require(identity.get("semantic_parent") == mother.get("semantic_parent") == "P.capital", "SDR0: R must remain inside P.capital")
    require(bool(identity.get("profile_stable_question")), "SDR0: profile-specific stable question required")
    require(identity.get("new_top_level_capability") is False, "SDR0: new top-level capability is prohibited")
    require(contract.get("human_gate_token") == EXPECTED_GATE, "SDR0: Human Gate token drift")


def validate_contract_shape(contract: dict) -> None:
    require(contract.get("required_blocks") == REQUIRED_BLOCKS, "SDR0: universal 11-block contract order drift")
    for block in REQUIRED_BLOCKS:
        require(block in contract and isinstance(contract[block], dict), f"SDR0: missing contract block {block}")
    require(contract.get("status") == "candidate_ready_for_human_review", "SDR0: candidate state drift")


def validate_epistemics(contract: dict) -> None:
    evidence = contract["evidence"]
    require(evidence.get("as_of_required") is True, "SDR0: as_of must be required")
    require(evidence.get("point_in_time_required") is True, "SDR0: Point-in-Time must be required")
    require(evidence.get("evidence_cutoff_required") is True, "SDR0: evidence cutoff must be required")
    require(evidence.get("falsifier_required") is True, "SDR0: falsifier must be required")
    require(evidence.get("law") == "Claim Authority <= Evidence Authority", "SDR0: evidence-authority law drift")
    require(contract["settlement_learning"].get("outcome_leakage_prohibited") is True, "SDR0: outcome leakage must be prohibited")


def validate_source_lineage(contract: dict, source_registry: dict) -> None:
    source_ids = {row["source_id"] for row in source_registry.get("sources", [])}
    require(len(source_ids) == len(source_registry.get("sources", [])), "SDR0: duplicate source IDs")
    for source_ref in contract["theory_causal_mechanism"].get("source_seed_refs", []):
        require(source_ref in source_ids, f"SDR0: unresolved source seed {source_ref}")
    for row in source_registry.get("sources", []):
        require(row.get("theoryobject_admitted") is False, f"SDR0: source {row.get('source_id')} silently admitted to TheoryObject")
    require(source_registry.get("epistemic_law") == "Claim Authority <= Evidence Authority", "SDR0: provenance epistemic law drift")


def validate_mechanism_boundaries(contract: dict) -> None:
    boundary = contract["theory_causal_mechanism"].get("claim_boundary", "").lower()
    for token in ("high debt", "central-bank purchases", "negative real yields", "foreign selling", "gold appreciation", "treasury buybacks"):
        require(token in boundary, f"SDR0: claim boundary missing shortcut guard {token}")
    shortcuts = set(contract["inference"].get("prohibited_shortcuts", []))
    for token in (
        "high_debt_implies_repression",
        "QE_implies_monetization",
        "foreign_selling_implies_crisis",
        "gold_up_implies_soft_default",
        "correlation_implies_causality",
        "feature_importance_implies_causality",
    ):
        require(token in shortcuts, f"SDR0: prohibited shortcut missing {token}")


def validate_output_gate(contract: dict) -> None:
    output = contract["output"]
    require(output.get("state_type") == "SovereignDebtRepressionStateProfile", "SDR0: state type drift")
    stages = set(output.get("regime_stage_vocabulary", []))
    require("soft_default" not in stages, "SDR0: unqualified soft_default cannot be a canonical state")
    require("repression_active" in stages and "real_value_dilution_active" in stages, "SDR0: repression/dilution stages missing")
    gate = output.get("real_value_dilution_active_gate", {})
    require(gate.get("logic") == "AND", "SDR0: real-value dilution gate must be AND")
    require(set(gate.get("requirements", [])) == EXPECTED_AND_REQUIREMENTS, "SDR0: real-value dilution AND requirements drift")
    require(gate.get("two_of_four_rule_prohibited") is True, "SDR0: 2-of-4 voting rule must be prohibited")
    require(PROHIBITED_OUTPUTS <= set(output.get("prohibited_outputs", [])), "SDR0: prohibited-output boundary incomplete")


def validate_replay_benchmark(contract: dict) -> None:
    bench = contract["benchmark_qualification"]
    require(set(bench.get("gold_replays", [])) == EXPECTED_GOLD_REPLAYS, "SDR0: Gold Replay set drift")
    require(set(bench.get("hard_negatives", [])) == EXPECTED_HARD_NEGATIVES, "SDR0: hard-negative set drift")
    require(bench.get("shadow") == "US_JAPAN_2026_POINT_IN_TIME", "SDR0: 2026 PIT Shadow missing")
    require(bench.get("failure_receipts") == "required", "SDR0: failure receipts required")
    require("lookahead" not in bench.get("point_in_time_split_policy", "").lower(), "SDR0: PIT policy wording unexpectedly admits lookahead")


def validate_authority(contract: dict, state: dict, review_text: str) -> None:
    governance = contract["runtime_receipt_governance"]
    require(governance.get("research_pass_implies_capital_pass") is False, "SDR0: research pass cannot imply capital pass")
    require(governance.get("capability_acceptance_implies_promotion") is False, "SDR0: acceptance cannot imply promotion")
    require(governance.get("promotion_implies_evidence_admission") is False, "SDR0: promotion cannot imply evidence admission")
    require(governance.get("execution_authority") == "none", "SDR0: execution authority must be none")
    require(state.get("new_top_level_capability") is False, "SDR0: state cannot create top-level capability")
    require(state.get("status") == "candidate_ready_for_human_review", "SDR0: state must stop at Human Review")
    for forbidden in ("portfolio_action", "live_execution", "canon_promotion", "theoryobject_admission"):
        require(forbidden in state.get("not_authorized", []), f"SDR0: state missing non-authority {forbidden}")
    require(state.get("human_gate_token") == EXPECTED_GATE, "SDR0: state Human Gate drift")
    require(EXPECTED_GATE in review_text, "SDR0: review card missing Human Gate token")


def validate_upstream() -> None:
    qxm1 = load_json(QXM1_STATE_PATH)
    require(qxm1.get("status") == "accepted_merged", "SDR0: QXM1 must remain accepted_merged")
    roles = qxm1.get("candidate_roles", {}).get("existing_capability_profile_candidates", [])
    require(any(item.startswith("CAP-R-01::") for item in roles), "SDR0: upstream QXM1 precedent for CAP-R-01 profile missing")
    invariants = qxm1.get("constitutional_invariants", {})
    require(invariants.get("r_remains_inside_p_capital") is True, "SDR0: upstream R/P.capital invariant regressed")
    require(invariants.get("scalar_master_score_prohibited") is True, "SDR0: upstream scalar-score guard regressed")
    require(invariants.get("research_pass_implies_capital_pass") is False, "SDR0: upstream capital-pass guard regressed")


def main() -> int:
    validate_files_exist()
    contract = load_json(CONTRACT_PATH)
    sources = load_json(SOURCE_PATH)
    state = load_json(STATE_PATH)
    review_text = REVIEW_PATH.read_text(encoding="utf-8")
    mother = cap_r01_profile()

    validate_upstream()
    validate_contract_shape(contract)
    validate_identity(contract, mother)
    validate_epistemics(contract)
    validate_source_lineage(contract, sources)
    validate_mechanism_boundaries(contract)
    validate_output_gate(contract)
    validate_replay_benchmark(contract)
    validate_authority(contract, state, review_text)

    print(
        "SDR0 candidate validation passed: "
        "profile=CAP-R-01::SDR0, 11 blocks, hard AND gate, 2 Gold Replays, "
        "3 hard negatives, 2026 PIT Shadow, execution_authority=none"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"validation_error: {exc}")
        raise SystemExit(1)
