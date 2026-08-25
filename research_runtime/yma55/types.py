from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

HUMAN_KERNEL = ("WORLD", "CONSTRAINT", "TRANSMISSION", "MECHANISM", "SETTLEMENT")
TRANSFERABILITY_DIMENSIONS = (
    "monetary_regime",
    "fiscal_capacity",
    "market_structure",
    "global_order",
    "policy_toolkit",
)


@dataclass(frozen=True)
class WorldState:
    epoch_id: str
    as_of: str
    macro_state: Mapping[str, Mapping[str, Any]]
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class StructuralConstraint:
    constraint_id: str
    constraint_type: str
    bound_actor: str
    binding_resource_or_freedom: str
    binding_evidence: tuple[str, ...]
    easing_evidence: tuple[str, ...]
    horizon: str


@dataclass(frozen=True)
class TransmissionState:
    transmission_id: str
    feasible_policy_set: tuple[str, ...]
    observed_reaction: str | None
    channels: tuple[str, ...]
    expected_sequence: tuple[str, ...]
    break_conditions: tuple[str, ...]


@dataclass(frozen=True)
class MechanismHypothesis:
    hypothesis_id: str
    role: str
    mechanism_family: str
    causal_chain: tuple[str, ...]
    required_conditions: tuple[str, ...]
    predicted_observables: Mapping[str, str]
    expected_sequence: tuple[str, ...]
    expected_horizon: str
    falsifiers: tuple[str, ...]
    breaker: str
    supporting_evidence_refs: tuple[str, ...]
    contradicting_evidence_refs: tuple[str, ...]
    complexity_exception: str | None = None


@dataclass(frozen=True)
class MechanismHypothesisSet:
    hypothesis_set_id: str
    as_of: str
    primary: MechanismHypothesis
    alternatives: tuple[MechanismHypothesis, ...]
    null: MechanismHypothesis | None
    pit_frozen: bool
    discrimination_matrix: tuple[Mapping[str, Any], ...] = ()
    evidence_search_budget: Mapping[str, Any] = field(default_factory=dict)
    resolution_state: str = "UNRESOLVED"
    version: int = 1


@dataclass(frozen=True)
class TransferabilityDimension:
    name: str
    state: str
    blocking_if_mismatched: bool
    evidence_refs: tuple[str, ...]
    mechanism_relevance: str = "material"
    why_it_matters: str = ""


@dataclass(frozen=True)
class TransferabilityAssessment:
    assessment_id: str
    historical_episode_ref: str
    current_case_ref: str
    mechanism_ref: str
    as_of: str
    dimensions: tuple[TransferabilityDimension, ...]
    overall_transferability: str
    unknowns: tuple[str, ...] = ()
    version: int = 1


@dataclass(frozen=True)
class PriorViolationRecord:
    violation_id: str
    prior_ref: str
    hypothesis_set_ref: str
    as_of: str
    status: str
    violation_type: str | None
    severity: str | None
    posterior_effect: str
    research_response: str
    evidence_refs: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class RealitySettlement:
    episode_id: str
    outcome_class: str
    mechanism_resolution: str
    expression_resolution: str
    notes: str = ""
