#!/usr/bin/env python3
"""Fail-closed validation for the ME0 multi-engine ontology candidate."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ME0_DIR = ROOT / "docs" / "architecture" / "me0"
CONTRACT_PATH = ME0_DIR / "ME0-AUTHORITY-CONTRACT-v0.1.json"
SUCCESSOR_MAP_PATH = ME0_DIR / "ME0-SEMANTIC-SUCCESSOR-MAP-v0.1.json"
STATE_PATH = ME0_DIR / "ME0-STATE.json"
REVIEW_CARD_PATH = ME0_DIR / "ME0-HUMAN-REVIEW-CARD-v0.1.md"

EXPECTED_STAGE = "ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE"
EXPECTED_OBJECTIVE = "Lifetime Right-Tail Capture under Survival Constraints"
EXPECTED_ENGINES = {
    "ENG-C": "Compounding",
    "ENG-R": "Reflexive Repricing",
    "ENG-X": "Convexity",
}
EXPECTED_FUTURE_OBJECTS = {
    "EngineThesis",
    "PositionPassport",
    "AssetGraduationEvent",
    "BookState",
    "MetaAllocationResearchState",
}
EXPECTED_MIGRATION_INVARIANTS = {
    "NO_SILENT_THESIS_MIGRATION",
    "HISTORICAL_IDENTITIES_IMMUTABLE",
    "ENGINE_CHANGE_REQUIRES_GOVERNED_EVENT",
    "RESEARCH_PASS_DOES_NOT_IMPLY_CAPITAL_PASS",
    "CLAIM_AUTHORITY_LE_EVIDENCE_AUTHORITY",
}
EXPECTED_DEFERRED_MIGRATIONS = {
    "ME1_STATE_OBJECT_MODEL_REFRAME",
    "ME2_C_X_SEMANTIC_SEPARATION",
    "ME3_REFLEXIVE_ENGINE_MARKET_CLOCK_CONTRACT",
    "ME4_GRADUATION_META_ALLOCATOR",
    "ME5_THREE_ENGINE_GOLD_REPLAY_ABLATION",
}
EXPECTED_PROHIBITIONS = {
    "C_R_X_are_proven_exhaustive_universal_ontology",
    "CAP_R_01_means_ENG_R",
    "cash_is_fourth_return_engine",
    "human_PNX_projection_is_machine_return_engine_ontology",
    "research_target_has_only_one_valid_thesis",
    "engine_change_can_be_implicit",
    "research_pass_implies_capital_pass",
}
EXPECTED_DISTINCTIONS = {
    "asset_form_not_pricing_archetype",
    "pricing_archetype_not_return_engine",
    "return_engine_not_engine_thesis",
    "engine_thesis_not_position_expression",
    "target_identity_does_not_determine_thesis_identity",
    "book_membership_is_thesis_position_specific",
}
EXPECTED_ENGINE_KEYS = {
    "engine_id",
    "name",
    "stable_question",
    "primary_source_of_return",
    "price_semantics",
    "not_this_engine",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_contract(contract: dict) -> None:
    require(contract.get("stage") == EXPECTED_STAGE, "ME0 contract stage mismatch")
    require(contract.get("mother_objective") == EXPECTED_OBJECTIVE, "ME0 mother objective mismatch")

    distinctions = contract.get("ontology_distinctions", {})
    require(set(distinctions) == EXPECTED_DISTINCTIONS, "ME0 ontology distinction keys mismatch")
    require(all(distinctions.values()), "all ontology distinctions must be true")

    layer_ids = [item.get("layer_id") for item in contract.get("authority_layers", [])]
    require(layer_ids == ["L0", "L1", "L2", "L3", "L4", "L5"], "authority layers must be L0-L5 in order")

    engines = contract.get("genesis_engine_set", [])
    require(len(engines) == 3, "ME0 must freeze exactly three Genesis Engines")
    ids = [item.get("engine_id") for item in engines]
    require(len(ids) == len(set(ids)), "Genesis Engine IDs must be unique")
    require(set(ids) == set(EXPECTED_ENGINES), "Genesis Engine IDs mismatch")
    for engine in engines:
        require(set(engine) == EXPECTED_ENGINE_KEYS, f"{engine.get('engine_id')}: engine keys mismatch")
        require(engine.get("name") == EXPECTED_ENGINES[engine["engine_id"]], f"{engine['engine_id']}: name mismatch")
        require(bool(engine.get("stable_question")), f"{engine['engine_id']}: missing stable question")
        require(bool(engine.get("primary_source_of_return")), f"{engine['engine_id']}: missing return mechanism")
        require(bool(engine.get("price_semantics")), f"{engine['engine_id']}: missing price semantics")
        require(bool(engine.get("not_this_engine")), f"{engine['engine_id']}: missing boundary negatives")

    primitives = contract.get("research_primitives_services", {})
    require(primitives.get("P") == "reality_structural_state_family", "P service role mismatch")
    require(primitives.get("N") == "belief_expectation_state_family", "N service role mismatch")
    require(primitives.get("E") == "horizontal_evidence_authority_plane", "E must remain horizontal evidence authority")
    require(primitives.get("V") == "routed_price_interpretation_service_family", "V routed service role mismatch")
    require(primitives.get("S") == "horizontal_survival_constraint", "S must remain horizontal survival constraint")

    cash = contract.get("book_roles", {}).get("BOOK-CASH", {})
    require(cash.get("name") == "Liquidity Reserve", "BOOK-CASH name mismatch")
    require(cash.get("is_return_engine") is False, "Cash must not be a return engine")
    require(
        set(cash.get("roles", [])) >= {
            "survival_buffer",
            "future_optionality",
            "funding_resilience",
            "forced_selling_avoidance",
        },
        "BOOK-CASH roles incomplete",
    )

    require(set(contract.get("migration_invariants", [])) >= EXPECTED_MIGRATION_INVARIANTS, "migration invariants incomplete")

    governance = contract.get("governance", {})
    require(governance.get("engine_registry_closed_world") is False, "engine registry must be open-world")
    for key in (
        "historical_canon_mutation_authority",
        "registry_admission_authority",
        "capability_promotion_authority",
        "position_sizing_authority",
        "portfolio_weight_authority",
        "buy_sell_hold_authority",
        "live_execution_authority",
    ):
        require(governance.get(key) is False, f"{key} must remain false")

    require(set(contract.get("prohibited_interpretations", [])) >= EXPECTED_PROHIBITIONS, "prohibited interpretations incomplete")
    require(
        contract.get("historical_canon_policy", {}).get("receipts_are_immutable_ledger_facts") is True,
        "historical receipts must remain immutable ledger facts",
    )
    require(
        contract.get("human_projection_policy", {}).get("human_projection_is_machine_return_engine_ontology") is False,
        "human projection must not become machine return-engine ontology",
    )


def validate_successor_map(successor_map: dict) -> None:
    require(successor_map.get("stage") == EXPECTED_STAGE, "successor map stage mismatch")
    require(
        successor_map.get("policy") == "semantic_successors_never_mutate_historical_receipts",
        "successor map preservation policy mismatch",
    )

    historical = {item.get("id"): item for item in successor_map.get("historical_identities", [])}
    cap_r = historical.get("CAP-R-01", {})
    require(cap_r.get("historical_meaning") == "Regime Causal Decomposition", "CAP-R-01 historical meaning changed")
    require(cap_r.get("historical_semantic_parent") == "P.capital", "CAP-R-01 historical parent changed")
    require(cap_r.get("redefined_in_place") is False, "CAP-R-01 cannot be redefined in place")
    require(cap_r.get("future_successor_hint") == "CAP-REG-01", "CAP-R-01 successor hint mismatch")

    cap_xs = historical.get("CAP-XS-01", {})
    require(cap_xs.get("historical_meaning") == "Structural Asymmetry Source Mapper", "CAP-XS-01 historical meaning changed")
    require(cap_xs.get("redefined_in_place") is False, "CAP-XS-01 cannot be redefined in place")
    require(cap_xs.get("future_action") == "typed_successor_split_under_ME2", "CAP-XS-01 split must be deferred to ME2")

    cap_v = historical.get("CAP-V-01", {})
    require(cap_v.get("historical_meaning") == "Price-Implied Expectations", "CAP-V-01 historical meaning changed")
    require(cap_v.get("redefined_in_place") is False, "CAP-V-01 cannot be redefined in place")
    require(cap_v.get("future_action") == "routed_price_interpretation_successor", "CAP-V-01 routed successor mismatch")

    roles = {item.get("role_id"): item for item in successor_map.get("successor_roles", [])}
    expected_roles = {"ENG-C", "ENG-R", "ENG-X", "A2_RETURN_ENGINE_ROUTE", "BOOK-C", "BOOK-R", "BOOK-X", "BOOK-CASH"}
    require(set(roles) >= expected_roles, "successor roles incomplete")
    eng_r = roles["ENG-R"]
    require(eng_r.get("meaning") == "Reflexive Repricing", "ENG-R meaning mismatch")
    require(eng_r.get("namespace") == "return_engine", "ENG-R namespace mismatch")
    require("CAP-R-01" in eng_r.get("must_not_alias", []), "ENG-R must not alias CAP-R-01")
    require(roles["BOOK-CASH"].get("is_return_engine") is False, "BOOK-CASH cannot be an engine")

    future_objects = {item.get("object_identity"): item for item in successor_map.get("future_object_identities", [])}
    require(set(future_objects) == EXPECTED_FUTURE_OBJECTS, "future object identities mismatch")
    for name, item in future_objects.items():
        require(item.get("implementation_authority_in_ME0") is False, f"{name}: implementation authority must be false")
        require(item.get("schema_creation_deferred_to") == "ME1_or_later", f"{name}: schema must be deferred")

    deferred = {item.get("migration_id"): item for item in successor_map.get("deferred_migrations", [])}
    require(set(deferred) >= EXPECTED_DEFERRED_MIGRATIONS, "deferred migrations incomplete")
    for migration_id in EXPECTED_DEFERRED_MIGRATIONS:
        require(deferred[migration_id].get("authorized") is False, f"{migration_id}: ME0 must not authorize migration")


def validate_state(state: dict) -> None:
    require(state.get("stage") == EXPECTED_STAGE, "ME0 state stage mismatch")
    require(state.get("status") in {"candidate_started", "candidate_ready_for_human_review"}, "invalid ME0 candidate status")
    require(state.get("repository_base_sha") == "bd8931e1bf21dceb5e34a68ec41aa199b83e9410", "ME0 base SHA mismatch")
    design = state.get("design_approval", {})
    require(design.get("token") == "APPROVE_ME0_DESIGN_FOR_IMPLEMENTATION", "design approval token mismatch")
    require(design.get("decision") == "accepted", "design approval must be accepted")
    human = state.get("human_gate", {})
    require(human.get("token") == "ACCEPT_ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE", "Human Gate token mismatch")
    require(human.get("decision") == "pending", "Human Gate must remain pending in ME0 implementation")
    require(human.get("acceptance_does_not_imply_merge") is True, "Human acceptance must not imply merge")
    for key, value in state.get("implementation_authorities", {}).items():
        require(value is False, f"implementation authority {key} must remain false")

    if state.get("status") == "candidate_started":
        require(state.get("next_gate") == "ME0_MACHINE_QUALIFICATION", "candidate_started next gate mismatch")
    else:
        qualification = state.get("machine_qualification", {})
        require(qualification.get("decision") == "passed", "Human Review candidate requires passed machine qualification")
        require(state.get("next_gate") == "HUMAN_REVIEW", "qualified candidate next gate mismatch")


def validate_review_card(text: str) -> None:
    for index in range(1, 17):
        require(f"D{index}" in text, f"Human Review card missing D{index}")
    require(
        "ACCEPT_ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE" in text,
        "Human Review card missing acceptance token",
    )
    require("Acceptance does not imply merge." in text, "Human Review card must preserve merge separation")


def validate_historical_non_regression() -> None:
    cap_r = load_json(ROOT / "docs" / "architecture" / "r2_3b1" / "CAP-R-01-SPEC-v0.1.json")
    cap_xs = load_json(ROOT / "docs" / "architecture" / "r2_3b1" / "CAP-XS-01-SPEC-v0.1.json")
    cap_v = load_json(ROOT / "docs" / "architecture" / "r2_3b1" / "CAP-V-01-SPEC-v0.1.json")
    yip0 = load_json(ROOT / "docs" / "architecture" / "yip0" / "YIP0-PHILOSOPHY-CONTRACT-v0.1.json")

    require(cap_r["identity"]["name"] == "Regime Causal Decomposition", "historical CAP-R-01 identity regressed")
    require(cap_r["identity"]["semantic_parent"] == "P.capital", "historical CAP-R-01 semantic parent regressed")
    require(cap_xs["identity"]["name"] == "Structural Asymmetry Source Mapper", "historical CAP-XS-01 identity regressed")
    require(cap_v["identity"]["name"] == "Price-Implied Expectations", "historical CAP-V-01 identity regressed")
    require(yip0["stage"] == "YIP0_INVESTMENT_PHILOSOPHY_CANON", "historical YIP0 stage regressed")


def main() -> int:
    contract = load_json(CONTRACT_PATH)
    successor_map = load_json(SUCCESSOR_MAP_PATH)
    state = load_json(STATE_PATH)
    review_card = REVIEW_CARD_PATH.read_text(encoding="utf-8")

    validate_contract(contract)
    validate_successor_map(successor_map)
    validate_state(state)
    validate_review_card(review_card)
    validate_historical_non_regression()

    print(f"me0_engines={len(contract['genesis_engine_set'])} state={state['status']} status=valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # fail closed in CI
        print(f"validation_error: {exc}")
        raise SystemExit(1)
