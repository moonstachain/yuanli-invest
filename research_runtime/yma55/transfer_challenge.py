from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Mapping, Sequence

from .types import TRANSFERABILITY_DIMENSIONS

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
