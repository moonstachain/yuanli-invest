from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .types import (
    TRANSFERABILITY_DIMENSIONS,
    MechanismHypothesis,
    MechanismHypothesisSet,
    TransferabilityAssessment,
)

VALID_ROLES = {"PRIMARY", "ALTERNATIVE", "NULL"}
VALID_TRANSFERABILITY_STATES = {"MATCHED", "PARTIAL", "MISMATCHED", "UNKNOWN"}
VALID_OVERALL_TRANSFERABILITY = {
    "HIGH_TRANSFERABILITY",
    "PARTIAL_TRANSFERABILITY",
    "WEAK_TRANSFERABILITY",
    "NON_TRANSFERABLE",
    "UNRESOLVED",
}
PROHIBITED_CAPITAL_FIELDS = {
    "position_size",
    "target_weight",
    "portfolio_weight",
    "recommended_weight",
    "buy",
    "sell",
    "hold",
    "trade_action",
    "execution_action",
    "order",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _validate_hypothesis(hypothesis: MechanismHypothesis, expected_role: str) -> None:
    require(hypothesis.role in VALID_ROLES, f"unknown hypothesis role: {hypothesis.role}")
    require(hypothesis.role == expected_role, f"expected {expected_role}, got {hypothesis.role}")
    require(bool(hypothesis.mechanism_family), "mechanism family required")
    require(bool(hypothesis.causal_chain), "causal chain required")
    if len(hypothesis.causal_chain) > 6:
        require(bool(hypothesis.complexity_exception), "causal chain >6 requires complexity_exception")
    require(bool(hypothesis.required_conditions), "required conditions required")
    require(bool(hypothesis.predicted_observables), "predicted observables required")
    require(bool(hypothesis.expected_sequence), "expected sequence required")
    require(bool(hypothesis.expected_horizon), "expected horizon required")
    require(bool(hypothesis.falsifiers), "falsifier required before conviction")
    require(bool(hypothesis.breaker), "breaker required")
    require(bool(hypothesis.supporting_evidence_refs), "supporting evidence reference required")


def validate_hypothesis_set(hypothesis_set: MechanismHypothesisSet) -> None:
    require(hypothesis_set.pit_frozen is True, "hypothesis set must be PIT-frozen")
    _validate_hypothesis(hypothesis_set.primary, "PRIMARY")
    require(1 <= len(hypothesis_set.alternatives) <= 3, "alternatives must contain 1..3 hypotheses")
    for alternative in hypothesis_set.alternatives:
        _validate_hypothesis(alternative, "ALTERNATIVE")
    require(hypothesis_set.null is not None, "exactly one null hypothesis is required")
    _validate_hypothesis(hypothesis_set.null, "NULL")
    ids = [hypothesis_set.primary.hypothesis_id]
    ids.extend(h.hypothesis_id for h in hypothesis_set.alternatives)
    ids.append(hypothesis_set.null.hypothesis_id)
    require(len(ids) == len(set(ids)), "hypothesis ids must be unique")


def validate_transferability(assessment: TransferabilityAssessment) -> None:
    require(assessment.overall_transferability in VALID_OVERALL_TRANSFERABILITY, "unknown overall transferability")
    names = tuple(d.name for d in assessment.dimensions)
    require(set(names) == set(TRANSFERABILITY_DIMENSIONS), "all five transferability dimensions are mandatory")
    require(len(names) == len(TRANSFERABILITY_DIMENSIONS), "transferability dimensions must not be duplicated")
    for dimension in assessment.dimensions:
        require(dimension.state in VALID_TRANSFERABILITY_STATES, f"unknown dimension state: {dimension.state}")
        require(bool(dimension.evidence_refs), f"evidence required for transferability dimension {dimension.name}")
    blocking_mismatch = any(
        d.blocking_if_mismatched and d.state == "MISMATCHED" for d in assessment.dimensions
    )
    if blocking_mismatch:
        require(
            assessment.overall_transferability == "NON_TRANSFERABLE",
            "blocking structural mismatch must force NON_TRANSFERABLE",
        )
    critical_unknowns = [
        d for d in assessment.dimensions if d.state == "UNKNOWN" and d.mechanism_relevance in {"critical", "material"}
    ]
    if critical_unknowns:
        require(
            assessment.overall_transferability in {"WEAK_TRANSFERABILITY", "UNRESOLVED", "NON_TRANSFERABLE"},
            "mechanism-critical unknowns cannot support high/partial transferability",
        )


def assert_no_capital_outputs(payload: Any) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if str(key) in PROHIBITED_CAPITAL_FIELDS:
                raise ValueError(f"capital/trading output prohibited: {key}")
            assert_no_capital_outputs(value)
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for item in payload:
            assert_no_capital_outputs(item)
