"""Gold research labels: pure calculations without repository or provider access."""

from collections import Counter
import math
from typing import Any, Mapping

VALUATION_LENSES = (
    "MACRO_FAIR_VALUE_LENS",
    "MONETARY_REGIME_PREMIUM_LENS",
    "REFLEXIVITY_POSITIONING_LENS",
)

def classify_property_drift(
    *,
    coefficient_distance: float,
    dominant_factor_match_share: float,
    residual_bias_ratio: float,
    independent_evidence_count: int,
) -> str:
    """Classify explanatory-property drift without claiming alpha.

    Thresholds are frozen before the physical PIT run. They deliberately require
    agreement across multiple diagnostics. None of the diagnostics is a forecast
    or a portfolio signal.
    """
    if any(type(value) not in {int, float} or not math.isfinite(value) for value in (coefficient_distance, dominant_factor_match_share, residual_bias_ratio)):
        raise ValueError("diagnostics must be finite numbers")
    if type(independent_evidence_count) is not int or independent_evidence_count < 0:
        raise ValueError("independent_evidence_count must be a nonnegative integer")
    if coefficient_distance < 0.0:
        raise ValueError("coefficient_distance must be non-negative")
    if not 0.0 <= dominant_factor_match_share <= 1.0:
        raise ValueError("dominant_factor_match_share must be in [0,1]")
    if residual_bias_ratio < 0.0:
        raise ValueError("residual_bias_ratio must be non-negative")
    if independent_evidence_count < 2:
        return "INSUFFICIENT_EVIDENCE"
    if (
        independent_evidence_count >= 3
        and coefficient_distance >= 1.0
        and dominant_factor_match_share <= 0.35
        and residual_bias_ratio >= 0.25
    ):
        return "DRIFT_CONFIRMED_RESEARCH_ONLY"
    if independent_evidence_count >= 2 and (
        coefficient_distance >= 0.50 or dominant_factor_match_share <= 0.50
    ):
        return "DRIFT_CANDIDATE"
    if (
        coefficient_distance <= 0.35
        and dominant_factor_match_share >= 0.65
        and residual_bias_ratio <= 0.15
    ):
        return "STABLE_PROPERTY"
    return "INSUFFICIENT_EVIDENCE"


def classify_expectation_reality(
    reality_score: float,
    expectation_score: float,
    evidence_complete: bool,
) -> str:
    """Compile a bounded research label from normalized [-1,1] scores."""
    if not evidence_complete:
        return "INDETERMINATE"
    for value in (reality_score, expectation_score):
        if not -1.0 <= value <= 1.0:
            raise ValueError("scores must be in [-1,1]")
    if reality_score * expectation_score < 0 and abs(reality_score) >= 0.5 and abs(expectation_score) >= 0.5:
        return "DIVERGENT"
    if abs(reality_score) >= 0.6 and abs(expectation_score) >= 0.6 and reality_score * expectation_score > 0:
        return "CONFIRMED"
    if reality_score - expectation_score >= 0.4:
        return "REALITY_LED"
    if expectation_score - reality_score >= 0.4:
        return "EXPECTATION_LED"
    return "INDETERMINATE"


def classify_valuation(lens_states: Mapping[str, str]) -> str:
    """Combine three Gold valuation lenses without emitting a target price."""
    required = set(VALUATION_LENSES)
    if set(lens_states) != required:
        return "UNIDENTIFIABLE"
    allowed = {"UNDERPRICED", "FAIR", "OVERPRICED", "UNIDENTIFIABLE"}
    if any(value not in allowed for value in lens_states.values()):
        raise ValueError("unsupported valuation-lens state")
    if "UNIDENTIFIABLE" in lens_states.values():
        return "UNIDENTIFIABLE"
    counts = Counter(lens_states.values())
    state, n = counts.most_common(1)[0]
    return state if n >= 2 else "UNIDENTIFIABLE"


def build_triangulation(*, machine_state_judgment: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(machine_state_judgment, Mapping):
        raise ValueError("machine judgment must be an object")
    if not machine_state_judgment.get("known_as_of"):
        raise ValueError("machine judgment requires known_as_of")
    return {
        "ray_regime_judgment": "PENDING_HUMAN_EVIDENCE",
        "yiru_timing_judgment": "PENDING_HUMAN_EVIDENCE",
        "machine_state_judgment": dict(machine_state_judgment),
        "settlement": "PENDING_REALITY",
        "attribution": "PENDING_SETTLEMENT",
    }
