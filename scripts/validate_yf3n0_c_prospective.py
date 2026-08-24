#!/usr/bin/env python3
"""Fail-closed repository validation for YF3N0-C prospective protocol."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from scripts import yf3n0_prospective as yf3

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "packages" / "contracts" / "schemas" / "yf3n0"
ARCH = ROOT / "docs" / "architecture" / "yf3n0"
FIXTURES = ARCH / "fixtures"
PROTOCOL_PATH = ARCH / "YF3N0-C-PROTOCOL-v0.1.json"
SLOTS_PATH = ARCH / "YF3N0-C-GENESIS-COHORT-SLOTS-v0.1.json"
STATE_PATH = ARCH / "YF3N0-C-STATE.json"
HUMAN_PATH = ROOT / "docs" / "human-projection" / "YF3N0-C-PROSPECTIVE-PREDICTION-PROTOCOL-v0.1.md"
HARD_NEGATIVES_PATH = FIXTURES / "hard-negatives.json"

SCHEMA_FILES = {
    "prospective-case.schema.json",
    "evidence-seal.schema.json",
    "prediction-contract.schema.json",
    "resolution-contract.schema.json",
    "preregistration-bundle.schema.json",
    "settlement-record.schema.json",
    "qualification-state.schema.json",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_instance(schema_name: str, value, label: str) -> None:
    schema = load_json(SCHEMAS / schema_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.path))
    if errors:
        detail = "; ".join(error.message for error in errors[:8])
        raise ValueError(f"{label}: {detail}")


def assert_all_false(values: dict, label: str) -> None:
    require(bool(values) and all(value is False for value in values.values()), f"{label}: authority must remain false")


def assert_no_global_score(value: dict) -> None:
    forbidden = {"global_accuracy", "overall_score", "three_non_accuracy", "global_accuracy_score"}
    found = forbidden.intersection(value)
    require(not found, "global accuracy score prohibited")


def validate_schemas() -> None:
    found = {path.name for path in SCHEMAS.glob("*.json")}
    require(found == SCHEMA_FILES, "YF3N0-C schema set mismatch")
    for path in SCHEMAS.glob("*.json"):
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        text = path.read_text(encoding="utf-8")
        require('"const": true' not in text, f"{path.name}: authority or immutable boolean unexpectedly true")


def validate_protocol() -> dict:
    protocol = load_json(PROTOCOL_PATH)
    require(protocol["protocol_id"] == "YF3N0-C-v0.1", "protocol identity mismatch")
    require(protocol["hypotheses"] == ["H1_DURATION", "H2_EDGE", "H3_LEVERAGE", "H4_CONJUNCTIVE", "H5_WEAKEST_LINK"], "hypothesis registry mismatch")
    require(protocol["primary_prediction_ids"] == ["P1_PIP_PERSISTENCE", "P2_EAA_PERSISTENCE_OR_DECAY", "P3_NLP_ACTIVATION_OR_FAILURE", "P4_INTEGRATED_FORCE_POTENTIAL"], "primary prediction registry mismatch")
    require(protocol["model_variants"] == ["FULL", "ABLATE_PIP", "ABLATE_EAA", "ABLATE_NLP", "BASELINE"], "model variants mismatch")
    require(protocol["required_horizons"] == ["T90", "T180", "T365"], "required horizons mismatch")
    require(protocol["optional_horizons"] == ["T730"], "optional horizon mismatch")
    require(protocol["binary_resolution_states"] == ["YES", "NO", "INDETERMINATE"], "binary states mismatch")
    require(protocol["causal_settlement_states"] == ["SUPPORTED", "PARTIALLY_SUPPORTED", "FALSIFIED", "INDETERMINATE"], "causal states mismatch")
    require(len(protocol["promotion_gates"]) == 6, "promotion gate count mismatch")
    assert_all_false(protocol["authority"], "protocol")
    return protocol


def validate_slots() -> dict:
    slots = load_json(SLOTS_PATH)
    yf3.validate_genesis_slots(slots)
    return slots


def validate_fixtures(protocol: dict, slots: dict) -> tuple[dict, dict, dict, list[dict], dict]:
    case = load_json(FIXTURES / "synthetic-full-case.json")
    seal = load_json(FIXTURES / "synthetic-evidence-seal.json")
    bundle = load_json(FIXTURES / "synthetic-preregistration-bundle.json")
    settlements = load_json(FIXTURES / "synthetic-settlements.json")
    qualification = load_json(FIXTURES / "synthetic-qualification-state.json")

    validate_instance("prospective-case.schema.json", case, "synthetic case")
    validate_instance("evidence-seal.schema.json", seal, "synthetic evidence seal")
    validate_instance("prediction-contract.schema.json", bundle["prediction_contract"], "synthetic prediction contract")
    validate_instance("resolution-contract.schema.json", bundle["resolution_contract"], "synthetic resolution contract")
    validate_instance("preregistration-bundle.schema.json", bundle, "synthetic preregistration bundle")
    for index, settlement in enumerate(settlements):
        validate_instance("settlement-record.schema.json", settlement, f"synthetic settlement[{index}]")
    validate_instance("qualification-state.schema.json", qualification, "synthetic qualification")

    yf3.validate_evidence_seal(case, seal)
    yf3.validate_atomic_preregistration(seal, bundle)
    yf3.validate_prediction_contract(bundle["prediction_contract"], protocol)
    slot = next(row for row in slots["slots"] if row["slot_id"] == case["slot_id"])
    yf3.validate_case_eligibility(case, slot, seal, {"real_case_enrollment_authorized": False})

    prediction_by_outcome = {item["outcome_definition_id"]: item for item in bundle["prediction_contract"]["predictions"]}
    for settlement in settlements:
        yf3.validate_settlement_timing(bundle, settlement["horizon"], settlement["settled_at"])
        for row in settlement["binary_resolutions"]:
            prediction = prediction_by_outcome[row["outcome_definition_id"]]
            forecasts = {
                "FULL": prediction["full_forecast"],
                "ABLATE_PIP": prediction["ablation_forecasts"]["ABLATE_PIP"],
                "ABLATE_EAA": prediction["ablation_forecasts"]["ABLATE_EAA"],
                "ABLATE_NLP": prediction["ablation_forecasts"]["ABLATE_NLP"],
                "BASELINE": prediction["baseline_forecast"],
            }
            for model, forecast in forecasts.items():
                expected = yf3.brier_score(forecast["probability"], row["resolution"])
                require(row["model_brier_scores"][model] == expected, f"stored Brier mismatch: {settlement['horizon']} {model}")
        for row in settlement["causal_settlements"]:
            yf3.validate_causal_settlement(row["state"])

    matrix = yf3.build_evidence_matrix([case], settlements)
    assert_no_global_score(matrix)
    require(yf3.derive_qualification_outcome(qualification["gate_states"]) == qualification["final_outcome"], "synthetic qualification outcome mismatch")
    assert_all_false(qualification["authority"], "qualification fixture")
    return case, seal, bundle, settlements, qualification


def _run_attack(attack_id: str, case: dict, seal: dict, bundle: dict, slots: dict, protocol: dict) -> None:
    if attack_id == "HN01_POST_CUTOFF_EVIDENCE":
        bad = copy.deepcopy(seal)
        bad["evidence_manifest"][0]["known_as_of"] = "2026-08-24T00:01:00Z"
        bad["evidence_digest_sha256"] = yf3.sha256_json({key: value for key, value in bad.items() if key != "evidence_digest_sha256"})
        yf3.validate_evidence_seal(case, bad)
    elif attack_id == "HN02_PREDICTION_MUTATION_AFTER_SEAL":
        bad = copy.deepcopy(bundle)
        bad["prediction_contract"]["predictions"][3]["full_forecast"]["probability"] = 0.99
        yf3.validate_atomic_preregistration(seal, bad)
    elif attack_id == "HN03_RESOLUTION_DRIFT_AFTER_SEAL":
        bad = copy.deepcopy(bundle)
        bad["resolution_contract"]["rules"][0]["event_definition"] = "Post-seal rewritten rule"
        yf3.validate_atomic_preregistration(seal, bad)
    elif attack_id == "HN04_TOO_MANY_SECONDARY_PREDICTIONS":
        bad = copy.deepcopy(bundle["prediction_contract"])
        base = copy.deepcopy(bad["predictions"][3])
        for index in range(3):
            item = copy.deepcopy(base)
            item["prediction_id"] = f"SYN-SECONDARY-{index + 1}"
            item["role"] = "SECONDARY"
            item["outcome_definition_id"] = f"OUT-SECONDARY-{index + 1}"
            item["resolution_rule_id"] = f"RULE-OUT-SECONDARY-{index + 1}"
            item["full_forecast"]["outcome_definition_id"] = item["outcome_definition_id"]
            item["full_forecast"]["resolution_rule_id"] = item["resolution_rule_id"]
            for value in item["ablation_forecasts"].values():
                value["outcome_definition_id"] = item["outcome_definition_id"]
                value["resolution_rule_id"] = item["resolution_rule_id"]
            item["baseline_forecast"]["outcome_definition_id"] = item["outcome_definition_id"]
            item["baseline_forecast"]["resolution_rule_id"] = item["resolution_rule_id"]
            bad["predictions"].append(item)
        yf3.validate_prediction_contract(bad, protocol)
    elif attack_id == "HN05_ABLATION_OUTCOME_MISMATCH":
        bad = copy.deepcopy(bundle["prediction_contract"]["predictions"][3])
        bad["ablation_forecasts"]["ABLATE_EAA"]["outcome_definition_id"] = "DIFFERENT-OUTCOME"
        yf3.validate_model_comparability(bad)
    elif attack_id == "HN06_INDETERMINATE_AS_SUPPORT":
        yf3.validate_causal_settlement("INDETERMINATE_AS_SUPPORT")
    elif attack_id == "HN07_EARLY_T365_SETTLEMENT":
        yf3.validate_settlement_timing(bundle, "T365", "2027-08-23T00:00:00Z")
    elif attack_id == "HN08_UNDECLARED_T730_EXTENSION":
        yf3.validate_optional_horizon(bundle, "T730")
    elif attack_id == "HN09_REAL_CASE_ENROLLMENT_WITHOUT_GATE":
        bad = copy.deepcopy(case)
        bad["real_case"] = True
        slot = next(row for row in slots["slots"] if row["slot_id"] == bad["slot_id"])
        yf3.validate_case_eligibility(bad, slot, seal, {"real_case_enrollment_authorized": False})
    elif attack_id == "HN10_GLOBAL_ACCURACY_SCORE":
        assert_no_global_score({"global_accuracy": 0.99})
    elif attack_id == "HN11_CAPITAL_AUTHORITY_LEAKAGE":
        assert_all_false({"capital_authority": True}, "hard negative")
    elif attack_id == "HN12_H5_COMPENSATION_VIOLATION":
        states = {"PIP": "SUPPORTED", "EAA": "FALSIFIED", "NLP": "SUPPORTED"}
        require(yf3.force_candidate_state(states) == "FULL_FORCE_CANDIDATE", "H5 compensation violation")
    else:
        raise ValueError(f"unknown hard-negative attack: {attack_id}")


def validate_hard_negatives(case: dict, seal: dict, bundle: dict, slots: dict, protocol: dict) -> None:
    attacks = load_json(HARD_NEGATIVES_PATH)
    require(len(attacks) == 12, "hard-negative attack count mismatch")
    require(len({item["attack_id"] for item in attacks}) == 12, "duplicate hard-negative attack id")
    for attack in attacks:
        expected = attack["expected_error_substring"]
        try:
            _run_attack(attack["attack_id"], case, seal, bundle, slots, protocol)
        except ValueError as exc:
            require(expected in str(exc), f"{attack['attack_id']}: wrong failure reason: {exc}")
        else:
            raise ValueError(f"{attack['attack_id']}: hard negative unexpectedly passed")


def validate_state_and_projection() -> None:
    state = load_json(STATE_PATH)
    require(state["status"] == "IMPLEMENTED_CANDIDATE_AWAITING_HUMAN_REVIEW", "candidate state mismatch")
    require(state["parent_written_spec_accepted"] is True, "parent written spec acceptance missing")
    require(state["protocol_implemented"] is True, "protocol implementation flag missing")
    for field in ("real_case_enrollment_authorized", "prediction_clock_start_authorized", "canon_promotion_authorized", "merge_authorized"):
        require(state[field] is False, f"{field} must remain false")
    text = HUMAN_PATH.read_text(encoding="utf-8")
    for phrase in ("预测不是事后解释", "INDETERMINATE", "三非不是万能成功预测器", "PIP ∧ EAA ∧ NLP"):
        require(phrase in text, f"human projection missing: {phrase}")
    require("Real-case enrollment: NOT AUTHORIZED" in text, "human projection enrollment boundary missing")
    require("Canon promotion: NOT AUTHORIZED" in text, "human projection canon boundary missing")


def validate_no_authority_leakage() -> None:
    protocol = load_json(PROTOCOL_PATH)
    assert_all_false(protocol["authority"], "protocol")
    state = load_json(STATE_PATH)
    require(state["real_case_enrollment_authorized"] is False, "real-case authority leakage")
    require(state["prediction_clock_start_authorized"] is False, "clock authority leakage")
    require(state["canon_promotion_authorized"] is False, "canon authority leakage")
    schema_text = "\n".join(path.read_text(encoding="utf-8") for path in SCHEMAS.glob("*.json"))
    require('"const": true' not in schema_text, "schema authority leakage")


def main() -> int:
    validate_schemas()
    protocol = validate_protocol()
    slots = validate_slots()
    case, seal, bundle, settlements, qualification = validate_fixtures(protocol, slots)
    validate_hard_negatives(case, seal, bundle, slots, protocol)
    validate_state_and_projection()
    validate_no_authority_leakage()
    print(
        "YF3N0-C schemas=7 slots=12 hard_negatives=12 prospective_protocol=valid "
        "real_case_enrollment_authorized=false canon_promotion_authorized=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"validation_error: {exc}")
        raise SystemExit(1)
