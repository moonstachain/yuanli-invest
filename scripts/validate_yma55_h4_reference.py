#!/usr/bin/env python3
"""Fail-closed validation for YMA55-H4 reference runtime and replay candidates."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_runtime.yma55.replay import (
    REQUIRED_CASE_TYPES,
    REQUIRED_MECHANISMS,
    load_manifest,
    run_replay_case,
    validate_replay_case,
)
from research_runtime.yma55.validation import assert_no_capital_outputs

MANIFEST = ROOT / "fixtures" / "replay" / "yma55_h4" / "manifest.json"
REQUIRED_HYPOTHESIS_FIELDS = {
    "hypothesis_id",
    "role",
    "mechanism_family",
    "causal_chain",
    "required_conditions",
    "predicted_observables",
    "expected_sequence",
    "expected_horizon",
    "falsifiers",
    "breaker",
    "supporting_evidence_refs",
    "contradicting_evidence_refs",
}
REQUIRED_TRANSFERABILITY_DIMENSIONS = {
    "monetary_regime",
    "fiscal_capacity",
    "market_structure",
    "global_order",
    "policy_toolkit",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_hypothesis_payload(hypothesis: dict[str, Any], expected_role: str) -> None:
    require(REQUIRED_HYPOTHESIS_FIELDS <= set(hypothesis), f"{expected_role} missing required hypothesis fields")
    require(hypothesis.get("role") == expected_role, f"hypothesis role must be {expected_role}")
    chain = hypothesis.get("causal_chain", [])
    require(bool(chain), "causal chain required")
    if len(chain) > 6:
        require(bool(hypothesis.get("complexity_exception")), "causal chain >6 requires complexity_exception")
    require(bool(hypothesis.get("required_conditions")), "required conditions required")
    require(bool(hypothesis.get("predicted_observables")), "predicted observables required")
    require(bool(hypothesis.get("expected_sequence")), "expected sequence required")
    require(bool(hypothesis.get("falsifiers")), "falsifier required")
    require(bool(hypothesis.get("breaker")), "breaker required")
    require(bool(hypothesis.get("supporting_evidence_refs")), "supporting evidence refs required")


def validate_case_contract(case: dict[str, Any]) -> None:
    validate_replay_case(case)
    hypothesis_set = case["t0"]["hypothesis_set"]
    require(hypothesis_set.get("pit_frozen") is True, "hypothesis set must be PIT-frozen")
    require("primary" in hypothesis_set, "primary hypothesis required")
    require("null" in hypothesis_set, "null hypothesis required")
    alternatives = hypothesis_set.get("alternatives", [])
    require(1 <= len(alternatives) <= 3, "1..3 alternatives required")
    validate_hypothesis_payload(hypothesis_set["primary"], "PRIMARY")
    for alternative in alternatives:
        validate_hypothesis_payload(alternative, "ALTERNATIVE")
    validate_hypothesis_payload(hypothesis_set["null"], "NULL")

    template = case["t0"]["transferability_template"]
    require(
        set(template.get("dimensions", [])) == REQUIRED_TRANSFERABILITY_DIMENSIONS,
        "all five transferability dimensions are mandatory",
    )
    require(
        len(template.get("dimensions", [])) == len(REQUIRED_TRANSFERABILITY_DIMENSIONS),
        "transferability dimensions must not be duplicated",
    )
    require(
        template.get("overall_transferability") in {
            "HIGH_TRANSFERABILITY",
            "PARTIAL_TRANSFERABILITY",
            "WEAK_TRANSFERABILITY",
            "NON_TRANSFERABLE",
            "UNRESOLVED",
        },
        "invalid transferability state",
    )
    if case["evidence_status"] != "hydrated":
        require(case.get("gold_qualified") is False, "unhydrated candidate cannot claim Gold qualification")
    validate_settlement_semantics(case["settlement"])


def validate_runner_input(payload: dict[str, Any]) -> None:
    require("settlement" not in payload, "settlement/outcome leakage into T0 runner input")
    validate_research_only_payload(payload)


def validate_research_only_payload(payload: Any) -> None:
    assert_no_capital_outputs(payload)


def validate_prior_application(payload: dict[str, Any]) -> None:
    state = payload.get("overall_transferability")
    application = payload.get("prior_application_state")
    if state == "NON_TRANSFERABLE":
        require(application not in {"ACTIVE", "MATERIAL_AUTHORITY", "CURRENT_PRIOR"}, "non-transferable prior cannot remain active")


def validate_settlement_semantics(settlement: dict[str, Any]) -> None:
    require("outcome_class" in settlement, "settlement outcome_class required")
    require("mechanism_resolution" in settlement, "settlement mechanism_resolution required")
    require("expression_resolution" in settlement, "settlement expression_resolution required")
    outcome = str(settlement["outcome_class"])
    epistemic_success = settlement.get("epistemic_success")
    if "WRONG_MECHANISM" in outcome:
        require(epistemic_success is not True, "wrong-mechanism lucky outcome cannot score epistemic success")
    if outcome == "UNRESOLVED":
        require(epistemic_success is not True, "unresolved settlement cannot be forced into epistemic success")
        require(
            "confirm" not in str(settlement.get("mechanism_resolution", "")).lower(),
            "unresolved settlement cannot claim confirmed mechanism",
        )
    validate_research_only_payload(settlement)


def validate_manifest_and_cases() -> tuple[int, dict[str, int]]:
    manifest = load_manifest(MANIFEST)
    require(manifest.get("status") == "candidate_not_gold_admitted", "H4 replay pack must remain candidate-only")
    require("does not mean evidence-qualified Gold admission" in manifest.get("semantics", ""), "manifest must disambiguate GOLD case role from Gold admission")
    counts: dict[str, int] = {}
    total = 0
    for mechanism_id, mechanism in manifest["mechanisms"].items():
        require(mechanism_id in REQUIRED_MECHANISMS, "unexpected mechanism in H4 manifest")
        require(set(mechanism["case_types"]) == REQUIRED_CASE_TYPES, "each mechanism must contain the four case roles")
        require(len(mechanism["cases"]) == 4, "each mechanism must contain exactly four cases")
        seen_case_types = set()
        for entry in mechanism["cases"]:
            case_path = ROOT / entry["path"]
            require(case_path.exists(), f"missing replay candidate {entry['path']}")
            case = load_json(case_path)
            validate_case_contract(case)
            require(case["mechanism_family"] == mechanism_id, "manifest/case mechanism mismatch")
            require(case["case_type"] == entry["case_type"], "manifest/case role mismatch")
            seen_case_types.add(case["case_type"])
            replay = run_replay_case(case)
            validate_runner_input(replay["runner_input"])
            require("settlement" in replay, "settlement must remain available only after T0 research freeze")
            total += 1
        require(seen_case_types == REQUIRED_CASE_TYPES, "missing H4 case role")
        counts[mechanism_id] = len(mechanism["cases"])
    require(total == 12, "H4 Genesis pack must contain exactly 12 candidates")
    return total, counts


def main() -> int:
    total, counts = validate_manifest_and_cases()
    print(
        "YMA55-H4 reference validation: PASS "
        f"cases={total} duration={counts['MRM-D']} credit={counts['MRM-CR']} scarcity={counts['MRM-SC']} "
        "gold_admission=0 capital_authority=0"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"validation_error: {exc}")
        raise SystemExit(1)
