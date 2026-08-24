from __future__ import annotations

from typing import Any, Mapping

from .types import MechanismHypothesisSet, PriorViolationRecord, TransferabilityAssessment


def _record(
    hypothesis_set: MechanismHypothesisSet,
    as_of: str,
    *,
    status: str,
    violation_type: str | None = None,
    severity: str | None = None,
    posterior_effect: str = "NO_CHANGE",
    research_response: str = "MAINTAIN_PRIOR",
    notes: str = "",
) -> PriorViolationRecord:
    return PriorViolationRecord(
        violation_id=f"pv:{hypothesis_set.hypothesis_set_id}:{as_of}",
        prior_ref=hypothesis_set.primary.hypothesis_id,
        hypothesis_set_ref=hypothesis_set.hypothesis_set_id,
        as_of=as_of,
        status=status,
        violation_type=violation_type,
        severity=severity,
        posterior_effect=posterior_effect,
        research_response=research_response,
        evidence_refs=(),
        notes=notes,
    )


def evaluate_prior_violation(
    transferability: TransferabilityAssessment,
    hypothesis_set: MechanismHypothesisSet,
    observations: Mapping[str, Any],
    as_of: str,
) -> PriorViolationRecord:
    """Evaluate PIT-frozen expectations against current observations.

    This is a qualitative research-state evaluator. It never emits a capital or
    trading action and deliberately avoids pseudo-Bayesian point probabilities.
    """

    if not hypothesis_set.pit_frozen or not hypothesis_set.primary.predicted_observables:
        return _record(
            hypothesis_set,
            as_of,
            status="NOT_EVALUABLE",
            research_response="UNRESOLVED_NEEDS_EVIDENCE",
            notes="PIT-frozen diagnostic expectations are required",
        )

    if transferability.overall_transferability in {"NON_TRANSFERABLE", "UNRESOLVED"}:
        response = (
            "RETIRE_CURRENT_PRIOR_APPLICATION"
            if transferability.overall_transferability == "NON_TRANSFERABLE"
            else "UNRESOLVED_NEEDS_EVIDENCE"
        )
        return _record(
            hypothesis_set,
            as_of,
            status="NOT_EVALUABLE",
            research_response=response,
            notes=f"historical prior transferability={transferability.overall_transferability}",
        )

    feasible_policy_set = tuple(observations.get("feasible_policy_set", ()))
    policy_reaction = observations.get("policy_reaction")
    if feasible_policy_set and policy_reaction is not None and policy_reaction not in feasible_policy_set:
        return _record(
            hypothesis_set,
            as_of,
            status="VIOLATION",
            violation_type="POLICY_REACTION_VIOLATION",
            severity="BREAKER",
            posterior_effect="SHIFT_TO_ALTERNATIVE_REVIEW",
            research_response="REOPEN_MECHANISM_COMPETITION",
            notes="observed policy reaction is outside the pre-committed feasible set",
        )

    observed = dict(observations.get("observables", {}))
    expected = dict(hypothesis_set.primary.predicted_observables)

    for sensor, expected_state in expected.items():
        if sensor in observed and observed[sensor] != expected_state:
            return _record(
                hypothesis_set,
                as_of,
                status="VIOLATION",
                violation_type="SIGN_VIOLATION",
                severity="MATERIAL",
                posterior_effect="MAJOR_DOWNGRADE",
                research_response="REOPEN_MECHANISM_COMPETITION",
                notes=f"{sensor}: expected {expected_state}, observed {observed[sensor]}",
            )

    if observations.get("magnitude_violation") is True:
        return _record(
            hypothesis_set,
            as_of,
            status="VIOLATION",
            violation_type="MAGNITUDE_VIOLATION",
            severity="MATERIAL",
            posterior_effect="MODEST_DOWNGRADE",
            research_response="DOWNGRADE_PRIOR",
        )

    if observations.get("persistence_violation") is True:
        return _record(
            hypothesis_set,
            as_of,
            status="VIOLATION",
            violation_type="PERSISTENCE_VIOLATION",
            severity="MATERIAL",
            posterior_effect="MAJOR_DOWNGRADE",
            research_response="REOPEN_MECHANISM_COMPETITION",
        )

    expected_sequence = tuple(hypothesis_set.primary.expected_sequence)
    observed_sequence = tuple(observations.get("observed_sequence", ()))
    if expected_sequence and observed_sequence and all(sensor in observed for sensor in expected_sequence):
        if observed_sequence[: len(expected_sequence)] != expected_sequence:
            return _record(
                hypothesis_set,
                as_of,
                status="VIOLATION",
                violation_type="SEQUENCE_VIOLATION",
                severity="MATERIAL",
                posterior_effect="MODEST_DOWNGRADE",
                research_response="REOPEN_MECHANISM_COMPETITION",
            )

    if observations.get("window_closed") is True:
        missing = [sensor for sensor in expected if sensor not in observed]
        if missing:
            return _record(
                hypothesis_set,
                as_of,
                status="VIOLATION",
                violation_type="CROSS_ASSET_CONFIRMATION_VIOLATION",
                severity="MATERIAL",
                posterior_effect="MODEST_DOWNGRADE",
                research_response="REOPEN_MECHANISM_COMPETITION",
                notes=f"missing required confirmation sensors: {', '.join(missing)}",
            )

    if observations.get("timing_surprise") is True:
        return _record(
            hypothesis_set,
            as_of,
            status="SURPRISE_ONLY",
            posterior_effect="NO_CHANGE",
            research_response="MAINTAIN_PRIOR",
            notes="timing differed while required signs and causal order remained compatible",
        )

    return _record(
        hypothesis_set,
        as_of,
        status="NO_VIOLATION",
        posterior_effect="NO_CHANGE",
        research_response="MAINTAIN_PRIOR",
    )
