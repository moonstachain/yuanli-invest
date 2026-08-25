from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Mapping, Sequence

from .prior_violation import evaluate_prior_violation
from .types import (
    TRANSFERABILITY_DIMENSIONS,
    MechanismHypothesis,
    MechanismHypothesisSet,
    TransferabilityAssessment,
    TransferabilityDimension,
)
from .validation import assert_no_capital_outputs, validate_transferability

TRANSFER_VARIANTS = (
    "T0_UNCONDITIONAL_TRANSPORT",
    "T1_TRANSFERABILITY_GATE_ONLY",
    "T2_H3_FULL",
)

VALID_DIMENSION_STATES = {"MATCHED", "PARTIAL", "MISMATCHED", "UNKNOWN"}
_ACTIVE_TRANSFERABILITY = {"HIGH_TRANSFERABILITY", "PARTIAL_TRANSFERABILITY"}
_OPAQUE_PAIR_ID = re.compile(r"^TP-[A-Z0-9]{2}$")


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def resolve_transferability_state(dimensions: Sequence[Mapping[str, Any]]) -> str:
    names = [str(d.get("name", "")) for d in dimensions]
    _require(len(names) == len(TRANSFERABILITY_DIMENSIONS), "all five transferability dimensions are required")
    _require(set(names) == set(TRANSFERABILITY_DIMENSIONS), "transferability dimension set mismatch")

    for dimension in dimensions:
        _require(dimension.get("state") in VALID_DIMENSION_STATES, f"invalid transferability state: {dimension.get('state')}")
        _require(bool(dimension.get("evidence_refs")), f"evidence required for {dimension.get('name')}")

    if any(
        d.get("state") == "MISMATCHED" and bool(d.get("blocking_if_mismatched"))
        for d in dimensions
    ):
        return "NON_TRANSFERABLE"

    if any(
        d.get("state") == "UNKNOWN" and d.get("mechanism_relevance") in {"critical", "material"}
        for d in dimensions
    ):
        return "UNRESOLVED"

    material = [
        d for d in dimensions if d.get("mechanism_relevance") in {"critical", "material"}
    ]
    mismatches = sum(d.get("state") == "MISMATCHED" for d in material)
    partials = sum(d.get("state") == "PARTIAL" for d in material)

    if mismatches >= 2 or partials >= 3:
        return "WEAK_TRANSFERABILITY"
    if mismatches or partials:
        return "PARTIAL_TRANSFERABILITY"
    return "HIGH_TRANSFERABILITY"


def active_prior_allowed(overall_transferability: str) -> bool:
    return overall_transferability in _ACTIVE_TRANSFERABILITY


def validate_transported_diagnostic(contract: Mapping[str, Any]) -> None:
    required = {
        "transport_id",
        "source_prior_ref",
        "source_mechanism_family",
        "target_case_ref_opaque",
        "as_of",
        "frozen_at",
        "observation_window_start",
        "observation_window_end",
        "target_required_conditions",
        "target_expected_observables",
        "target_expected_sequence",
        "target_feasible_policy_set",
        "supporting_evidence_refs",
        "pit_frozen",
        "version",
    }
    missing = sorted(required - set(contract))
    _require(not missing, f"transported diagnostic missing fields: {missing}")
    _require(contract["transport_id"] != contract["source_prior_ref"], "transport contract must not mutate source prior identity")
    _require(contract.get("pit_frozen") is True, "transported diagnostic must be PIT-frozen")
    _require(bool(contract.get("target_required_conditions")), "transported required conditions are required")
    _require(bool(contract.get("target_expected_observables")), "transported expected observables are required")
    _require(bool(contract.get("target_expected_sequence")), "transported expected sequence is required")
    _require(bool(contract.get("supporting_evidence_refs")), "transported diagnostic evidence is required")

    frozen_at = _parse_iso(str(contract["frozen_at"]))
    window_start = _parse_iso(str(contract["observation_window_start"]))
    window_end = _parse_iso(str(contract["observation_window_end"]))
    _require(frozen_at <= window_start, "transported diagnostic must freeze before forward observation window")
    _require(window_start <= window_end, "observation window start must not follow end")


def build_hypothesis_set_from_transport(contract: Mapping[str, Any]) -> MechanismHypothesisSet:
    validate_transported_diagnostic(contract)
    transport_id = str(contract["transport_id"])
    mechanism_family = str(contract["source_mechanism_family"])
    support_refs = tuple(str(x) for x in contract["supporting_evidence_refs"])
    expected = dict(contract["target_expected_observables"])
    expected_sequence = tuple(str(x) for x in contract["target_expected_sequence"])
    required_conditions = tuple(str(x) for x in contract["target_required_conditions"])
    horizon = f"through:{contract['observation_window_end']}"

    primary = MechanismHypothesis(
        hypothesis_id=f"transported:{transport_id}",
        role="PRIMARY",
        mechanism_family=mechanism_family,
        causal_chain=("transported_source_prior", "target_diagnostic_transmission"),
        required_conditions=required_conditions,
        predicted_observables=expected,
        expected_sequence=expected_sequence,
        expected_horizon=horizon,
        falsifiers=("transported_required_diagnostic_break",),
        breaker="transported_prior_break",
        supporting_evidence_refs=support_refs,
        contradicting_evidence_refs=(),
    )
    alternative = MechanismHypothesis(
        hypothesis_id=f"transported-alt:{transport_id}",
        role="ALTERNATIVE",
        mechanism_family="TRANSPORT_COMPETING_REVIEW",
        causal_chain=("target_evidence", "competing_mechanism_review"),
        required_conditions=("competing_mechanism_supported",),
        predicted_observables={"competing_mechanism_signal": "PRESENT"},
        expected_sequence=("competing_mechanism_signal",),
        expected_horizon=horizon,
        falsifiers=("competing_mechanism_not_supported",),
        breaker="alternative_review_break",
        supporting_evidence_refs=support_refs,
        contradicting_evidence_refs=(),
    )
    null = MechanismHypothesis(
        hypothesis_id=f"transported-null:{transport_id}",
        role="NULL",
        mechanism_family="TRANSPORT_NULL",
        causal_chain=("non_mechanistic_explanation", "target_observation"),
        required_conditions=("null_explanation_supported",),
        predicted_observables={"null_signal": "PRESENT"},
        expected_sequence=("null_signal",),
        expected_horizon=horizon,
        falsifiers=("mechanistic_confirmation_present",),
        breaker="null_review_break",
        supporting_evidence_refs=support_refs,
        contradicting_evidence_refs=(),
    )
    return MechanismHypothesisSet(
        hypothesis_set_id=f"transport-set:{transport_id}",
        as_of=str(contract["as_of"]),
        primary=primary,
        alternatives=(alternative,),
        null=null,
        pit_frozen=True,
        version=int(contract["version"]),
    )


def validate_structural_packet(packet: Mapping[str, Any]) -> None:
    forbidden = {
        "forward_observation_stream",
        "observations",
        "settlement",
        "expected_h3_settlement",
        "source_episode_id",
        "target_episode_id",
        "case_type",
    }
    leaked = sorted(forbidden & set(packet))
    _require(not leaked, f"structural packet leaks forward/settlement identity fields: {leaked}")

    pair_id = str(packet.get("opaque_pair_id", ""))
    _require(bool(_OPAQUE_PAIR_ID.fullmatch(pair_id)), "opaque pair id must match TP-XX and contain no role/year identity")
    _require(packet.get("historical_gold_admission") is False, "H4.3 cannot admit Historical Gold")
    _require(packet.get("capital_authority") is False, "H4.3 cannot grant capital authority")

    structural = packet.get("structural_evidence_at_t0")
    _require(isinstance(structural, Mapping), "structural_evidence_at_t0 is required")
    dimensions = structural.get("dimensions")
    _require(isinstance(dimensions, Sequence) and not isinstance(dimensions, (str, bytes)), "five structural dimensions are required")
    resolve_transferability_state(dimensions)

    contract = packet.get("transported_diagnostic")
    _require(isinstance(contract, Mapping), "transported_diagnostic is required")
    validate_transported_diagnostic(contract)


def _build_transferability_assessment(packet: Mapping[str, Any], state: str) -> TransferabilityAssessment:
    structural = packet["structural_evidence_at_t0"]
    dimensions = tuple(
        TransferabilityDimension(
            name=str(row["name"]),
            state=str(row["state"]),
            blocking_if_mismatched=bool(row.get("blocking_if_mismatched")),
            evidence_refs=tuple(str(ref) for ref in row["evidence_refs"]),
            mechanism_relevance=str(row.get("mechanism_relevance", "material")),
            why_it_matters="H4.3 candidate-derived source/target structural comparison",
        )
        for row in structural["dimensions"]
    )
    assessment = TransferabilityAssessment(
        assessment_id=f"h43-transfer:{packet['opaque_pair_id']}",
        historical_episode_ref=str(packet["transported_diagnostic"]["source_prior_ref"]),
        current_case_ref=str(packet["opaque_pair_id"]),
        mechanism_ref=str(packet["mechanism_family"]),
        as_of=str(structural["as_of"]),
        dimensions=dimensions,
        overall_transferability=state,
        unknowns=tuple(d.name for d in dimensions if d.state == "UNKNOWN"),
    )
    validate_transferability(assessment)
    return assessment


def _validate_observation_packet(
    observation: Mapping[str, Any],
    structural_packet: Mapping[str, Any],
) -> None:
    forbidden = {"settlement", "expected_h3_settlement", "source_episode_id", "target_episode_id", "challenge_role"}
    leaked = sorted(forbidden & set(observation))
    _require(not leaked, f"forward observation packet leaks settlement/identity fields: {leaked}")
    _require(observation.get("opaque_pair_id") == structural_packet.get("opaque_pair_id"), "observation pair id mismatch")
    _require(observation.get("historical_gold_admission") is False, "observation packet cannot admit Historical Gold")
    _require(observation.get("capital_authority") is False, "observation packet cannot grant capital authority")
    stream = observation.get("observation_stream")
    _require(isinstance(stream, Sequence) and not isinstance(stream, (str, bytes)) and bool(stream), "forward observation stream required")
    contract = structural_packet["transported_diagnostic"]
    frozen_at = _parse_iso(str(contract["frozen_at"]))
    window_start = _parse_iso(str(contract["observation_window_start"]))
    window_end = _parse_iso(str(contract["observation_window_end"]))
    for event in stream:
        known_at = _parse_iso(str(event["known_at"]))
        _require(known_at > frozen_at, "forward observation must be known after transferability freeze")
        _require(known_at >= window_start, "forward observation precedes observation window")
        _require(known_at <= window_end, "forward observation exceeds observation window")
        _require(bool(event.get("signals")), "observation event must contain signals")


def _observation_payload(
    observation: Mapping[str, Any],
    structural_packet: Mapping[str, Any],
) -> tuple[dict[str, Any], str]:
    _validate_observation_packet(observation, structural_packet)
    observed: dict[str, Any] = {}
    latest_known_at = ""
    for event in observation["observation_stream"]:
        latest_known_at = max(latest_known_at, str(event["known_at"]))
        for signal in event["signals"]:
            observed[str(signal["observable"])] = signal["state"]
    contract = structural_packet["transported_diagnostic"]
    payload = {
        "observables": observed,
        "observed_sequence": tuple(observation.get("observed_sequence", ())),
        "window_closed": bool(observation.get("window_closed")),
        "feasible_policy_set": tuple(contract.get("target_feasible_policy_set", ())),
    }
    for key in ("policy_reaction", "timing_surprise", "magnitude_violation", "persistence_violation"):
        if key in observation:
            payload[key] = observation[key]
    return payload, latest_known_at


def run_transfer_variant(
    structural_packet: Mapping[str, Any],
    observation: Mapping[str, Any],
    variant: str,
) -> dict[str, Any]:
    validate_structural_packet(structural_packet)
    _require(variant in TRANSFER_VARIANTS, f"unknown H4.3 transfer variant: {variant}")

    dimensions = structural_packet["structural_evidence_at_t0"]["dimensions"]
    state = resolve_transferability_state(dimensions)
    pair_id = str(structural_packet["opaque_pair_id"])
    source_eligible = structural_packet.get("source_prior_eligible") is True

    if not source_eligible:
        result = {
            "opaque_pair_id": pair_id,
            "variant": variant,
            "transferability": state,
            "authority_settlement": "ACTIVE_PRIOR_BLOCKED",
            "observation_settlement": "NOT_APPLICABLE",
            "prior_violation_status": "NOT_EVALUABLE_SOURCE_PRIOR_INELIGIBLE",
            "prior_violation_type": None,
            "prior_violation_severity": None,
            "unsafe_prior_application": False,
            "weak_prior_active_authority_leak": False,
            "source_prior_laundering_event": False,
            "historical_gold_admission": False,
            "capital_authority": False,
        }
        assert_no_capital_outputs(result)
        return result

    if variant == "T0_UNCONDITIONAL_TRANSPORT":
        authority = "ACTIVE_PRIOR_ALLOWED"
        observation_settlement = "MAINTAIN_PRIOR"
        prior_status = "NOT_EVALUATED_BY_VARIANT"
        violation_type = None
        severity = None
    elif variant == "T1_TRANSFERABILITY_GATE_ONLY":
        if active_prior_allowed(state):
            authority = "ACTIVE_PRIOR_ALLOWED"
            observation_settlement = "MAINTAIN_PRIOR"
        else:
            authority = "ACTIVE_PRIOR_BLOCKED"
            observation_settlement = "NOT_APPLICABLE"
        prior_status = "NOT_EVALUATED_BY_VARIANT"
        violation_type = None
        severity = None
    else:
        if not active_prior_allowed(state):
            authority = "ACTIVE_PRIOR_BLOCKED"
            observation_settlement = "NOT_APPLICABLE"
            prior_status = "NOT_EVALUABLE_TRANSFERABILITY_GATE"
            violation_type = None
            severity = None
        else:
            authority = "ACTIVE_PRIOR_ALLOWED"
            assessment = _build_transferability_assessment(structural_packet, state)
            hypothesis_set = build_hypothesis_set_from_transport(structural_packet["transported_diagnostic"])
            observation_payload, as_of = _observation_payload(observation, structural_packet)
            record = evaluate_prior_violation(assessment, hypothesis_set, observation_payload, as_of)
            observation_settlement = record.research_response
            prior_status = record.status
            violation_type = record.violation_type
            severity = record.severity

    result = {
        "opaque_pair_id": pair_id,
        "variant": variant,
        "transferability": state,
        "authority_settlement": authority,
        "observation_settlement": observation_settlement,
        "prior_violation_status": prior_status,
        "prior_violation_type": violation_type,
        "prior_violation_severity": severity,
        "unsafe_prior_application": authority == "ACTIVE_PRIOR_ALLOWED" and not active_prior_allowed(state),
        "weak_prior_active_authority_leak": authority == "ACTIVE_PRIOR_ALLOWED" and state == "WEAK_TRANSFERABILITY",
        "source_prior_laundering_event": False,
        "historical_gold_admission": False,
        "capital_authority": False,
    }
    assert_no_capital_outputs(result)
    return result


def _score_transfer_variant(
    outputs: Sequence[Mapping[str, Any]],
    settlements: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    unsafe = 0
    correct_blocks = 0
    maintains = 0
    violations_detected = 0
    violations_missed = 0
    false_breakers = 0
    weak_leaks = 0
    laundering = 0
    capital_events = 0
    transferability_mismatches = 0

    violation_expected_states = {
        "DOWNGRADE_PRIOR",
        "REOPEN_MECHANISM_COMPETITION",
        "RETIRE_CURRENT_PRIOR_APPLICATION",
    }
    for output in outputs:
        expected = settlements[str(output["opaque_pair_id"])]
        if output["transferability"] != expected["expected_transferability"]:
            transferability_mismatches += 1
        unsafe += int(bool(output["unsafe_prior_application"]))
        if expected["expected_authority_settlement"] == "ACTIVE_PRIOR_BLOCKED" and output["authority_settlement"] == "ACTIVE_PRIOR_BLOCKED":
            correct_blocks += 1
        if (
            expected["expected_authority_settlement"] == "ACTIVE_PRIOR_ALLOWED"
            and expected["expected_observation_settlement"] == "MAINTAIN_PRIOR"
            and output["observation_settlement"] == "MAINTAIN_PRIOR"
        ):
            maintains += 1
        if (
            expected["expected_authority_settlement"] == "ACTIVE_PRIOR_ALLOWED"
            and expected["expected_observation_settlement"] in violation_expected_states
        ):
            if output["observation_settlement"] == expected["expected_observation_settlement"]:
                violations_detected += 1
            else:
                violations_missed += 1
        if (
            expected["expected_observation_settlement"] == "MAINTAIN_PRIOR"
            and output["observation_settlement"] in violation_expected_states
        ):
            false_breakers += 1
        weak_leaks += int(bool(output["weak_prior_active_authority_leak"]))
        laundering += int(bool(output["source_prior_laundering_event"]))
        capital_events += int(bool(output["capital_authority"]))

    return {
        "unsafe_prior_applications": unsafe,
        "correct_structural_blocks": correct_blocks,
        "eligible_prior_maintains": maintains,
        "eligible_prior_violations_detected": violations_detected,
        "eligible_prior_violations_missed": violations_missed,
        "false_breakers": false_breakers,
        "weak_prior_active_authority_leaks": weak_leaks,
        "source_prior_laundering_events": laundering,
        "capital_authority_events": capital_events,
        "transferability_settlement_mismatches": transferability_mismatches,
    }


def run_h43_matrix(
    structural_packets: Sequence[Mapping[str, Any]],
    observation_packets: Sequence[Mapping[str, Any]],
    settlements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    structural_ids = [str(packet["opaque_pair_id"]) for packet in structural_packets]
    observation_by_id = {str(packet["opaque_pair_id"]): packet for packet in observation_packets}
    settlement_by_id = {str(row["opaque_pair_id"]): row for row in settlements}
    _require(len(structural_ids) == len(set(structural_ids)), "structural pair ids must be unique")
    _require(set(structural_ids) == set(observation_by_id), "structural and observation pair ids must match exactly")
    _require(set(structural_ids) == set(settlement_by_id), "pair ids and settlements must match exactly")

    outputs: dict[str, list[dict[str, Any]]] = {}
    metrics: dict[str, dict[str, int]] = {}
    for variant in TRANSFER_VARIANTS:
        variant_outputs = [
            run_transfer_variant(packet, observation_by_id[str(packet["opaque_pair_id"])], variant)
            for packet in structural_packets
        ]
        outputs[variant] = variant_outputs
        metrics[variant] = _score_transfer_variant(variant_outputs, settlement_by_id)

    result = {
        "pair_count": len(structural_packets),
        "variants": list(TRANSFER_VARIANTS),
        "same_pair_same_structural_evidence": True,
        "structural_evidence_authority": "CANDIDATE_DERIVED_FROM_H4_H41",
        "outputs": outputs,
        "metrics": metrics,
        "out_of_sample_claim": "NOT_ESTABLISHED",
        "exact_old_yma55_replication": "NOT_CLAIMED",
        "historical_gold_admission": False,
        "capital_authority": False,
    }
    assert_no_capital_outputs(result)
    return result
