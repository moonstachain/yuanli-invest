#!/usr/bin/env python3
"""Pure, fail-closed helpers for YF3N0-C prospective qualification."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timedelta

BINARY_STATES = {"YES", "NO", "INDETERMINATE"}
CAUSAL_STATES = {"SUPPORTED", "PARTIALLY_SUPPORTED", "FALSIFIED", "INDETERMINATE"}
PRIMITIVES = {"PIP", "EAA", "NLP"}
MODEL_VARIANTS = {"FULL", "ABLATE_PIP", "ABLATE_EAA", "ABLATE_NLP", "BASELINE"}
HORIZON_DAYS = {"T90": 90, "T180": 180, "T365": 365, "T730": 730}
GATES = [
    "C_G1_PROTOCOL_INTEGRITY",
    "C_G2_NO_RESOLUTION_DRIFT",
    "C_G3_PRIMITIVE_DISCRIMINATION",
    "C_G4_ABLATION_VALUE",
    "C_G5_CROSS_DOMAIN_ROBUSTNESS",
    "C_G6_NO_CONSTITUTIONAL_BREACH",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def canonical_json_bytes(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_json(value: dict) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def verify_digest(value: dict, expected_digest: str) -> bool:
    return sha256_json(value) == expected_digest


def _without(value: dict, key: str) -> dict:
    copy = deepcopy(value)
    copy.pop(key, None)
    return copy


def validate_evidence_seal(case: dict, seal: dict) -> None:
    require(seal["case_id"] == case["case_id"], "evidence seal case mismatch")
    require(parse_dt(case["known_as_of"]) <= parse_dt(seal["knowledge_cutoff"]), "case knowledge exceeds cutoff")
    require(parse_dt(seal["knowledge_cutoff"]) <= parse_dt(seal["sealed_at"]), "knowledge cutoff exceeds seal time")
    for item in seal.get("evidence_manifest", []):
        require(parse_dt(item["known_as_of"]) <= parse_dt(seal["knowledge_cutoff"]), "post-cutoff evidence prohibited")
    require(
        verify_digest(_without(seal, "evidence_digest_sha256"), seal["evidence_digest_sha256"]),
        "evidence digest mismatch",
    )


def validate_atomic_preregistration(evidence_seal: dict, bundle: dict) -> None:
    prediction = bundle["prediction_contract"]
    resolution = bundle["resolution_contract"]
    require(bundle["case_id"] == evidence_seal["case_id"], "preregistration case mismatch")
    require(bundle["evidence_digest_sha256"] == evidence_seal["evidence_digest_sha256"], "preregistration evidence digest mismatch")
    require(prediction["evidence_digest_sha256"] == bundle["evidence_digest_sha256"], "prediction evidence digest mismatch")
    require(resolution["evidence_digest_sha256"] == bundle["evidence_digest_sha256"], "resolution evidence digest mismatch")
    require(prediction["sealed_at"] == resolution["sealed_at"] == bundle["sealed_at"], "atomic preregistration timestamp mismatch")
    require(parse_dt(evidence_seal["sealed_at"]) <= parse_dt(bundle["sealed_at"]), "preregistration precedes evidence seal")
    require(prediction["case_id"] == resolution["case_id"] == bundle["case_id"], "preregistration nested case mismatch")
    evidence_refs = {item["evidence_ref"] for item in evidence_seal.get("evidence_manifest", [])}
    for item in prediction.get("predictions", []):
        require(set(item.get("source_evidence_refs", [])).issubset(evidence_refs), "prediction cites evidence outside sealed manifest")
    require(verify_digest(_without(bundle, "bundle_digest_sha256"), bundle["bundle_digest_sha256"]), "preregistration bundle digest mismatch")


def validate_genesis_slots(slots: dict) -> None:
    expected_domains = {"entrepreneurship", "investment_capital", "ai_native_os"}
    expected_types = {"full_candidate", "ablation_candidate", "uncertain_candidate", "exogenous_control"}
    rows = slots.get("slots", [])
    require(len(rows) == 12, "genesis cohort must contain exactly 12 slots")
    require(len({row["slot_id"] for row in rows}) == 12, "duplicate genesis slot id")
    pairs = {(row["domain"], row["structural_type"]) for row in rows}
    require(pairs == {(domain, kind) for domain in expected_domains for kind in expected_types}, "genesis cohort must be exact three-by-four")
    for row in rows:
        require(row.get("actor_ref") is None, "v0.1 genesis slot must be empty")
        require(row.get("enrollment_status") == "UNFILLED", "v0.1 genesis slot must be UNFILLED")
        require(row.get("real_case") is False, "v0.1 genesis slot cannot contain real case")


def validate_case_eligibility(case: dict, slot: dict, evidence_seal: dict, protocol_state: dict) -> None:
    require(case["slot_id"] == slot["slot_id"], "case slot mismatch")
    require(case["problem_domain"] == slot["domain"], "case domain mismatch")
    require(case["structural_type"] == slot["structural_type"], "case structural type mismatch")
    require(bool(case.get("reference_group")), "reference group required")
    require(parse_dt(case["known_as_of"]) <= parse_dt(evidence_seal["knowledge_cutoff"]), "case knowledge exceeds cutoff")
    require(case.get("observable_365d") is True, "365-day mechanism must be observable")
    require(case.get("private_secret_required") is False, "private-secret dependent case is ineligible")
    require(any(item.get("source_type") == "non_self_report" for item in evidence_seal.get("evidence_manifest", [])), "non-self-report evidence required")
    if case.get("real_case") is True:
        require(protocol_state.get("real_case_enrollment_authorized") is True, "real case enrollment not authorized")


def _all_forecasts(prediction: dict) -> dict[str, dict]:
    return {
        "FULL": prediction["full_forecast"],
        "ABLATE_PIP": prediction["ablation_forecasts"]["ABLATE_PIP"],
        "ABLATE_EAA": prediction["ablation_forecasts"]["ABLATE_EAA"],
        "ABLATE_NLP": prediction["ablation_forecasts"]["ABLATE_NLP"],
        "BASELINE": prediction["baseline_forecast"],
    }


def validate_model_comparability(prediction: dict) -> None:
    outcome = prediction["outcome_definition_id"]
    rule = prediction["resolution_rule_id"]
    for forecast in _all_forecasts(prediction).values():
        require(forecast["outcome_definition_id"] == outcome, "model outcome definition mismatch")
        require(forecast["resolution_rule_id"] == rule, "model resolution rule mismatch")


def validate_prediction_contract(contract: dict, protocol: dict) -> None:
    primary = [item for item in contract.get("predictions", []) if item.get("role") == "PRIMARY"]
    secondary = [item for item in contract.get("predictions", []) if item.get("role") == "SECONDARY"]
    require([item["prediction_id"] for item in primary] == protocol["primary_prediction_ids"], "primary prediction contract mismatch")
    require(len(secondary) <= protocol["max_secondary_predictions_per_case"], "secondary prediction limit exceeded")
    for item in contract.get("predictions", []):
        validate_model_comparability(item)
        forecasts = _all_forecasts(item)
        require(set(forecasts) == MODEL_VARIANTS, "model variant set mismatch")
        if item["forecast_channel"] == "binary":
            for value in forecasts.values():
                require("probability" in value and "expected_state" not in value, "binary forecast shape mismatch")
                require(0.0 <= float(value["probability"]) <= 1.0, "binary probability out of range")
        elif item["forecast_channel"] == "causal":
            for value in forecasts.values():
                require("expected_state" in value and "probability" not in value, "causal forecast shape mismatch")
                validate_causal_settlement(value["expected_state"])
        else:
            raise ValueError("invalid forecast channel")


def force_candidate_state(primitive_states: dict) -> str:
    require(set(primitive_states) == PRIMITIVES, "primitive state set mismatch")
    for state in primitive_states.values():
        validate_causal_settlement(state)
    if any(primitive_states[key] == "FALSIFIED" for key in PRIMITIVES):
        return "NOT_FULL_FORCE_CANDIDATE"
    if all(primitive_states[key] == "SUPPORTED" for key in PRIMITIVES):
        return "FULL_FORCE_CANDIDATE"
    if any(primitive_states[key] == "INDETERMINATE" for key in PRIMITIVES):
        return "INDETERMINATE"
    return "PARTIAL_FORCE_CANDIDATE"


def build_blind_resolution_packet(bundle: dict, horizon: str, new_evidence_refs: list[dict]) -> dict:
    require(horizon in HORIZON_DAYS, "invalid settlement horizon")
    rules = bundle["resolution_contract"]["rules"]
    return {
        "case_id": bundle["case_id"],
        "preregistration_bundle_id": bundle["preregistration_bundle_id"],
        "horizon": horizon,
        "outcome_definitions": [
            {"outcome_definition_id": rule["outcome_definition_id"], "event_definition": rule["event_definition"]}
            for rule in rules
        ],
        "resolution_rules": deepcopy(rules),
        "new_evidence_refs": deepcopy(new_evidence_refs),
    }


def validate_binary_resolution(value: str) -> None:
    require(value in BINARY_STATES, "invalid binary resolution state")


def brier_score(probability: float, resolution: str) -> float | None:
    validate_binary_resolution(resolution)
    require(0.0 <= float(probability) <= 1.0, "binary probability out of range")
    if resolution == "INDETERMINATE":
        return None
    outcome = 1.0 if resolution == "YES" else 0.0
    return (float(probability) - outcome) ** 2


def validate_causal_settlement(value: str) -> None:
    require(value in CAUSAL_STATES, "invalid causal settlement state")


def _prediction_by_outcome(bundle: dict) -> dict[str, dict]:
    return {item["outcome_definition_id"]: item for item in bundle["prediction_contract"]["predictions"]}


def build_settlement_record(bundle: dict, resolution_output: dict, settled_at: str) -> dict:
    prediction_by_outcome = _prediction_by_outcome(bundle)
    binary_rows = []
    for row in resolution_output.get("binary_resolutions", []):
        validate_binary_resolution(row["resolution"])
        prediction = prediction_by_outcome[row["outcome_definition_id"]]
        require(prediction["forecast_channel"] == "binary", "binary resolution targets non-binary forecast")
        scores = {
            model: brier_score(forecast["probability"], row["resolution"])
            for model, forecast in _all_forecasts(prediction).items()
        }
        binary_rows.append({"outcome_definition_id": row["outcome_definition_id"], "resolution": row["resolution"], "model_brier_scores": scores})
    causal_rows = []
    for row in resolution_output.get("causal_settlements", []):
        validate_causal_settlement(row["state"])
        causal_rows.append({"outcome_definition_id": row["outcome_definition_id"], "state": row["state"]})
    return {
        "settlement_record_id": resolution_output["settlement_record_id"],
        "case_id": bundle["case_id"],
        "preregistration_bundle_id": bundle["preregistration_bundle_id"],
        "schema_version": "1.0.0",
        "horizon": resolution_output["horizon"],
        "settled_at": settled_at,
        "binary_resolutions": binary_rows,
        "causal_settlements": causal_rows,
        "new_evidence_refs": list(resolution_output.get("new_evidence_refs", [])),
        "authority": {"prediction_mutation_authority": False, "capital_authority": False, "canon_authority": False},
    }


def horizon_due_at(sealed_at: str, horizon: str) -> datetime:
    require(horizon in HORIZON_DAYS, "invalid settlement horizon")
    return parse_dt(sealed_at) + timedelta(days=HORIZON_DAYS[horizon])


def validate_optional_horizon(bundle: dict, horizon: str) -> None:
    if horizon == "T730":
        require("T730" in bundle.get("optional_horizons", []), "T730 was not preregistered")
    else:
        require(horizon in {"T90", "T180", "T365"}, "invalid settlement horizon")


def validate_settlement_timing(bundle: dict, horizon: str, settled_at: str) -> None:
    validate_optional_horizon(bundle, horizon)
    require(parse_dt(settled_at) >= horizon_due_at(bundle["sealed_at"], horizon), f"early {horizon} settlement")


def _primitive_for_outcome(outcome_id: str) -> str | None:
    upper = outcome_id.upper()
    for primitive in PRIMITIVES:
        if primitive in upper:
            return primitive
    return None


def build_evidence_matrix(cases: list[dict], settlements: list[dict]) -> dict:
    case_by_id = {case["case_id"]: case for case in cases}
    model_scores: dict[str, list[float]] = {model: [] for model in MODEL_VARIANTS}
    primitives: dict[str, list[str]] = {primitive: [] for primitive in PRIMITIVES}
    domains: dict[str, dict] = {}
    indeterminate = 0
    falsifications = 0
    case_rows = []
    for settlement in settlements:
        case = case_by_id.get(settlement.get("case_id"), {})
        domain = case.get("problem_domain", "unknown")
        domains.setdefault(domain, {"settlement_count": 0, "supported_mechanism_evidence": False})
        domains[domain]["settlement_count"] += 1
        for row in settlement.get("binary_resolutions", []):
            if row["resolution"] == "INDETERMINATE":
                indeterminate += 1
                continue
            for model, score in row.get("model_brier_scores", {}).items():
                if score is not None and model in model_scores:
                    model_scores[model].append(float(score))
        for row in settlement.get("causal_settlements", []):
            state = row["state"]
            primitive = _primitive_for_outcome(row["outcome_definition_id"])
            if primitive:
                primitives[primitive].append(state)
            if state in {"SUPPORTED", "PARTIALLY_SUPPORTED"}:
                domains[domain]["supported_mechanism_evidence"] = True
            if state == "FALSIFIED":
                falsifications += 1
            if state == "INDETERMINATE":
                indeterminate += 1
        case_rows.append({"case_id": settlement.get("case_id"), "domain": domain, "horizon": settlement.get("horizon")})
    means = {model: (sum(values) / len(values) if values else None) for model, values in model_scores.items()}
    full = means.get("FULL")
    ablation_comparisons = {
        model: (None if full is None or means.get(model) is None else full - means[model])
        for model in ("ABLATE_PIP", "ABLATE_EAA", "ABLATE_NLP")
    }
    baseline = means.get("BASELINE")
    return {
        "cases": case_rows,
        "primitive_settlements": primitives,
        "integrated_force_state": "UNASSESSED" if not settlements else "SETTLEMENTS_PRESENT",
        "binary_forecast_scores_by_model": means,
        "indeterminate_counts": indeterminate,
        "falsification_counts": falsifications,
        "ablation_comparisons": ablation_comparisons,
        "ablation_mechanism_value": {},
        "baseline_comparisons": {"FULL_minus_BASELINE_mean_brier": None if full is None or baseline is None else full - baseline},
        "domain_coverage": domains,
        "protocol_integrity_findings": [],
        "constitutional_breaches": [],
    }


def _primitive_discrimination_state(primitives: dict[str, list[str]]) -> str:
    unresolved = False
    for primitive in PRIMITIVES:
        states = [state for state in primitives.get(primitive, []) if state != "INDETERMINATE"]
        positive = any(state in {"SUPPORTED", "PARTIALLY_SUPPORTED"} for state in states)
        negative = any(state == "FALSIFIED" for state in states)
        if positive and negative:
            continue
        if len(states) >= 2:
            return "FAIL"
        unresolved = True
    return "INDETERMINATE" if unresolved else "PASS"


def evaluate_promotion_gates(matrix: dict, protocol_integrity: dict) -> dict:
    gates = {}
    sealed = protocol_integrity.get("all_primary_preregistered_before_outcomes")
    drift = protocol_integrity.get("no_resolution_drift")
    checked = protocol_integrity.get("constitutional_check_complete")
    breaches = list(protocol_integrity.get("constitutional_breaches", [])) + list(matrix.get("constitutional_breaches", []))
    gates["C_G1_PROTOCOL_INTEGRITY"] = "PASS" if sealed is True else ("FAIL" if sealed is False else "INDETERMINATE")
    gates["C_G2_NO_RESOLUTION_DRIFT"] = "PASS" if drift is True else ("FAIL" if drift is False else "INDETERMINATE")
    gates["C_G3_PRIMITIVE_DISCRIMINATION"] = _primitive_discrimination_state(matrix.get("primitive_settlements", {}))
    scores = matrix.get("binary_forecast_scores_by_model", {})
    full = scores.get("FULL")
    ablations = {name: scores.get(name) for name in ("ABLATE_PIP", "ABLATE_EAA", "ABLATE_NLP")}
    if full is None or any(value is None for value in ablations.values()):
        gates["C_G4_ABLATION_VALUE"] = "INDETERMINATE"
    else:
        dominated = [name for name, value in ablations.items() if value < full]
        if not dominated:
            gates["C_G4_ABLATION_VALUE"] = "PASS"
        elif any(matrix.get("ablation_mechanism_value", {}).get(name) is False for name in dominated):
            gates["C_G4_ABLATION_VALUE"] = "FAIL"
        else:
            gates["C_G4_ABLATION_VALUE"] = "INDETERMINATE"
    coverage = matrix.get("domain_coverage", {})
    ent = coverage.get("entrepreneurship", {}).get("supported_mechanism_evidence") is True
    other = any(coverage.get(domain, {}).get("supported_mechanism_evidence") is True for domain in ("investment_capital", "ai_native_os"))
    if ent and other:
        gates["C_G5_CROSS_DOMAIN_ROBUSTNESS"] = "PASS"
    elif any(coverage.get(domain, {}).get("settlement_count", 0) for domain in ("entrepreneurship", "investment_capital", "ai_native_os")):
        gates["C_G5_CROSS_DOMAIN_ROBUSTNESS"] = "INDETERMINATE"
    else:
        gates["C_G5_CROSS_DOMAIN_ROBUSTNESS"] = "INDETERMINATE"
    if breaches:
        gates["C_G6_NO_CONSTITUTIONAL_BREACH"] = "FAIL"
    elif checked is True:
        gates["C_G6_NO_CONSTITUTIONAL_BREACH"] = "PASS"
    else:
        gates["C_G6_NO_CONSTITUTIONAL_BREACH"] = "INDETERMINATE"
    return gates


def derive_qualification_outcome(gates: dict) -> str:
    require(set(gates) == set(GATES), "promotion gate set mismatch")
    for state in gates.values():
        require(state in {"PASS", "FAIL", "INDETERMINATE"}, "invalid promotion gate state")
    if all(state == "PASS" for state in gates.values()):
        return "CANON_PROMOTION_READY"
    if any(gates[name] == "FAIL" for name in ("C_G1_PROTOCOL_INTEGRITY", "C_G2_NO_RESOLUTION_DRIFT", "C_G6_NO_CONSTITUTIONAL_BREACH")):
        return "FIRST_PRINCIPLES_CANON_REJECTED"
    if gates["C_G4_ABLATION_VALUE"] == "FAIL":
        return "PARTIAL_CANON_REFRAME_REQUIRED"
    if any(state == "INDETERMINATE" for state in gates.values()):
        return "INSUFFICIENT_EVIDENCE"
    return "PARTIAL_CANON_REFRAME_REQUIRED"
