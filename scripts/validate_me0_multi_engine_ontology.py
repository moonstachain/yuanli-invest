#!/usr/bin/env python3
"""Fail-closed validation for ME0 multi-engine ontology and acceptance lifecycle."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ME0_DIR = ROOT / "docs" / "architecture" / "me0"
CONTRACT_PATH = ME0_DIR / "ME0-AUTHORITY-CONTRACT-v0.1.json"
SUCCESSOR_MAP_PATH = ME0_DIR / "ME0-SEMANTIC-SUCCESSOR-MAP-v0.1.json"
STATE_PATH = ME0_DIR / "ME0-STATE.json"
REVIEW_CARD_PATH = ME0_DIR / "ME0-HUMAN-REVIEW-CARD-v0.1.md"
ACCEPTANCE_RECEIPT_PATH = ME0_DIR / "ME0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"

EXPECTED_STAGE = "ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE"
ACCEPT_TOKEN = "ACCEPT_ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE"
EXPECTED_ENGINES = {"ENG-C": "Compounding", "ENG-R": "Reflexive Repricing", "ENG-X": "Convexity"}
EXPECTED_FUTURE_OBJECTS = {"EngineThesis", "PositionPassport", "AssetGraduationEvent", "BookState", "MetaAllocationResearchState"}
EXPECTED_MIGRATIONS = {
    "ME1_STATE_OBJECT_MODEL_REFRAME",
    "ME2_C_X_SEMANTIC_SEPARATION",
    "ME3_REFLEXIVE_ENGINE_MARKET_CLOCK_CONTRACT",
    "ME4_GRADUATION_META_ALLOCATOR",
    "ME5_THREE_ENGINE_GOLD_REPLAY_ABLATION",
}
EXPECTED_INVARIANTS = {
    "NO_SILENT_THESIS_MIGRATION",
    "HISTORICAL_IDENTITIES_IMMUTABLE",
    "ENGINE_CHANGE_REQUIRES_GOVERNED_EVENT",
    "RESEARCH_PASS_DOES_NOT_IMPLY_CAPITAL_PASS",
    "CLAIM_AUTHORITY_LE_EVIDENCE_AUTHORITY",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_contract(contract: dict) -> None:
    require(contract.get("stage") == EXPECTED_STAGE, "contract stage mismatch")
    require(contract.get("mother_objective") == "Lifetime Right-Tail Capture under Survival Constraints", "mother objective mismatch")
    distinctions = contract.get("ontology_distinctions", {})
    require(distinctions and all(distinctions.values()), "ontology distinctions must all be true")
    engines = contract.get("genesis_engine_set", [])
    require({x.get("engine_id"): x.get("name") for x in engines} == EXPECTED_ENGINES, "Genesis Engine Set mismatch")
    primitives = contract.get("research_primitives_services", {})
    require(primitives.get("P") == "reality_structural_state_family", "P role mismatch")
    require(primitives.get("N") == "belief_expectation_state_family", "N role mismatch")
    require(primitives.get("E") == "horizontal_evidence_authority_plane", "E role mismatch")
    require(primitives.get("V") == "routed_price_interpretation_service_family", "V role mismatch")
    require(primitives.get("S") == "horizontal_survival_constraint", "S role mismatch")
    require(contract.get("book_roles", {}).get("BOOK-CASH", {}).get("is_return_engine") is False, "Cash cannot be an engine")
    require(set(contract.get("migration_invariants", [])) >= EXPECTED_INVARIANTS, "migration invariants incomplete")
    governance = contract.get("governance", {})
    require(governance.get("engine_registry_closed_world") is False, "engine registry must be open-world")
    for key in (
        "historical_canon_mutation_authority", "registry_admission_authority", "capability_promotion_authority",
        "position_sizing_authority", "portfolio_weight_authority", "buy_sell_hold_authority", "live_execution_authority",
    ):
        require(governance.get(key) is False, f"{key} must remain false")


def validate_successor_map(successor_map: dict) -> None:
    require(successor_map.get("stage") == EXPECTED_STAGE, "successor map stage mismatch")
    historical = {x.get("id"): x for x in successor_map.get("historical_identities", [])}
    require(historical["CAP-R-01"].get("historical_meaning") == "Regime Causal Decomposition", "CAP-R-01 meaning changed")
    require(historical["CAP-R-01"].get("historical_semantic_parent") == "P.capital", "CAP-R-01 parent changed")
    require(historical["CAP-R-01"].get("redefined_in_place") is False, "CAP-R-01 redefined in place")
    require(historical["CAP-XS-01"].get("future_action") == "typed_successor_split_under_ME2", "CAP-XS-01 split boundary changed")
    require(historical["CAP-V-01"].get("future_action") == "routed_price_interpretation_successor", "CAP-V-01 routing changed")
    roles = {x.get("role_id"): x for x in successor_map.get("successor_roles", [])}
    require("CAP-R-01" in roles["ENG-R"].get("must_not_alias", []), "ENG-R must not alias CAP-R-01")
    require(roles["BOOK-CASH"].get("is_return_engine") is False, "BOOK-CASH cannot be engine")
    future = {x.get("object_identity"): x for x in successor_map.get("future_object_identities", [])}
    require(set(future) == EXPECTED_FUTURE_OBJECTS, "future object identities mismatch")
    require(all(x.get("implementation_authority_in_ME0") is False for x in future.values()), "future objects cannot be implemented in ME0")
    migrations = {x.get("migration_id"): x for x in successor_map.get("deferred_migrations", [])}
    require(set(migrations) >= EXPECTED_MIGRATIONS, "deferred migrations incomplete")
    require(all(migrations[x].get("authorized") is False for x in EXPECTED_MIGRATIONS), "ME0 cannot authorize successor stages")


def validate_acceptance_receipt(receipt: dict) -> None:
    require(receipt.get("stage") == EXPECTED_STAGE, "acceptance receipt stage mismatch")
    require(receipt.get("decision") == ACCEPT_TOKEN, "acceptance receipt decision mismatch")
    require(receipt.get("reviewed_head_sha") == "5dfe423f856506ce20701fdc1bb5a721e5df48c8", "acceptance must bind reviewed head")
    ci = receipt.get("reviewed_ci", {})
    require(ci.get("run_number") == 330 and ci.get("run_id") == 32506837751, "acceptance CI basis mismatch")
    require(ci.get("conclusion") == "success", "reviewed CI must be success")
    require(receipt.get("formal_review") == "16/16 PASS", "formal review must be 16/16 PASS")
    require(receipt.get("merge_authority") == "not_implied_by_acceptance", "acceptance cannot imply merge")
    require(receipt.get("required_merge_token") == "AUTHORIZE_ME0_MERGE", "merge token mismatch")
    boundaries = receipt.get("boundaries_preserved", {})
    for key, value in boundaries.items():
        require(value is False, f"acceptance boundary {key} must remain false")


def validate_state(state: dict, receipt: dict | None = None) -> None:
    require(state.get("stage") == EXPECTED_STAGE, "state stage mismatch")
    allowed = {
        "candidate_started", "candidate_ready_for_human_review",
        "human_accepted_pending_post_acceptance_ci", "human_accepted_ready_for_merge_authorization",
    }
    require(state.get("status") in allowed, "invalid ME0 lifecycle status")
    require(state.get("repository_base_sha") == "bd8931e1bf21dceb5e34a68ec41aa199b83e9410", "base SHA mismatch")
    require(state.get("design_approval", {}).get("decision") == "accepted", "design approval missing")
    human = state.get("human_gate", {})
    require(human.get("token") == ACCEPT_TOKEN, "Human Gate token mismatch")
    require(human.get("acceptance_does_not_imply_merge") is True, "acceptance must not imply merge")
    require(all(v is False for v in state.get("implementation_authorities", {}).values()), "implementation authority regression")

    status = state["status"]
    if status == "candidate_started":
        require(human.get("decision") == "pending" and state.get("next_gate") == "ME0_MACHINE_QUALIFICATION", "candidate_started gate mismatch")
    elif status == "candidate_ready_for_human_review":
        require(human.get("decision") == "pending" and state.get("next_gate") == "HUMAN_REVIEW", "human review candidate gate mismatch")
        require(state.get("machine_qualification", {}).get("decision") == "passed", "machine qualification required")
    else:
        require(human.get("decision") == ACCEPT_TOKEN, "accepted state requires exact Human token")
        require(receipt is not None, "accepted state requires acceptance receipt")
        validate_acceptance_receipt(receipt)
        require(human.get("acceptance_receipt") == "docs/architecture/me0/ME0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json", "acceptance receipt path mismatch")
        require(state.get("required_merge_token") == "AUTHORIZE_ME0_MERGE", "required merge token mismatch")
        require(state.get("next_me_stage_authorized") is False, "acceptance cannot authorize next ME stage")
        if status == "human_accepted_pending_post_acceptance_ci":
            require(state.get("next_gate") == "ME0_POST_ACCEPTANCE_CI", "post-acceptance gate mismatch")
        else:
            q = state.get("post_acceptance_qualification", {})
            require(q.get("conclusion") == "success", "post-acceptance qualification required")
            require(state.get("next_gate") == "ME0_MERGE_AUTHORIZATION", "ready-for-merge gate mismatch")


def validate_review_card(text: str, accepted: bool) -> None:
    for i in range(1, 17):
        require(f"D{i}" in text, f"review card missing D{i}")
    require(ACCEPT_TOKEN in text, "review card missing acceptance token")
    require("Acceptance does not imply merge." in text, "review card merge boundary missing")
    if accepted:
        require("16 / 16 PASS" in text, "accepted review card must record 16/16 PASS")


def validate_historical_non_regression() -> None:
    cap_r = load_json(ROOT / "docs" / "architecture" / "r2_3b1" / "CAP-R-01-SPEC-v0.1.json")
    cap_xs = load_json(ROOT / "docs" / "architecture" / "r2_3b1" / "CAP-XS-01-SPEC-v0.1.json")
    cap_v = load_json(ROOT / "docs" / "architecture" / "r2_3b1" / "CAP-V-01-SPEC-v0.1.json")
    yip0 = load_json(ROOT / "docs" / "architecture" / "yip0" / "YIP0-PHILOSOPHY-CONTRACT-v0.1.json")
    require(cap_r["identity"]["name"] == "Regime Causal Decomposition", "historical CAP-R-01 regressed")
    require(cap_r["identity"]["semantic_parent"] == "P.capital", "historical CAP-R-01 parent regressed")
    require(cap_xs["identity"]["name"] == "Structural Asymmetry Source Mapper", "historical CAP-XS-01 regressed")
    require(cap_v["identity"]["name"] == "Price-Implied Expectations", "historical CAP-V-01 regressed")
    require(yip0["stage"] == "YIP0_INVESTMENT_PHILOSOPHY_CANON", "historical YIP0 regressed")


def main() -> int:
    contract = load_json(CONTRACT_PATH)
    successor_map = load_json(SUCCESSOR_MAP_PATH)
    state = load_json(STATE_PATH)
    accepted = state.get("status", "").startswith("human_accepted_")
    receipt = load_json(ACCEPTANCE_RECEIPT_PATH) if accepted else None
    validate_contract(contract)
    validate_successor_map(successor_map)
    validate_state(state, receipt)
    validate_review_card(REVIEW_CARD_PATH.read_text(encoding="utf-8"), accepted)
    validate_historical_non_regression()
    print(f"me0_engines={len(contract['genesis_engine_set'])} state={state['status']} status=valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"validation_error: {exc}")
        raise SystemExit(1)
