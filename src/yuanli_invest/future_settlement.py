#!/usr/bin/env python3
"""Offline candidate for preregistered Gold research outcome adjudication.

No provider calls, claim creation, scheduler integration, or action authority.
Hashes bind supplied records, but do not authenticate an external registry's
clock or identity. Real acceptance requires independent registry readback.
"""

from __future__ import annotations

import math
from datetime import datetime
from decimal import Decimal, localcontext
from typing import Any, Mapping

from .receipts import canonical_hash
from .time import instant

IDENTITY_FIELDS = ("target", "series_id", "unit", "currency")
AUTHORITY = {
    "accepted_learning_authorized": False,
    "capital_authorized": False,
    "sizing_authorized": False,
    "execution_authorized": False,
    "broker_action": False,
    "canon_promotion_authorized": False,
}


def number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def validate_claim(claim: Mapping[str, Any], registration: Mapping[str, Any]) -> tuple[datetime, datetime]:
    if claim.get("schema_version") != "gold-future-settlement.v1":
        raise ValueError("unsupported claim contract")
    for field in ("claim_id", "capability_version", *IDENTITY_FIELDS, "baseline_id"):
        if not isinstance(claim.get(field), str) or not claim[field].strip():
            raise ValueError(f"missing claim identity: {field}")
    if claim["target"] != "GOLD":
        raise ValueError("this candidate only adjudicates GOLD")
    if claim.get("data_mode") not in {"SYNTHETIC_ENGINEERING_ONLY", "REAL_OBSERVATIONS"}:
        raise ValueError("explicit data_mode is required")
    start, end = instant(claim.get("t0")), instant(claim.get("horizon_end"))
    if end <= start:
        raise ValueError("horizon must end after T0")
    if instant(claim.get("evidence_known_as_of")) > start:
        raise ValueError("post-T0 decision evidence")
    for field in ("model_direction", "baseline_direction"):
        value = claim.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value not in {-1, 0, 1}:
            raise ValueError(f"{field} must be -1, 0, or 1")
    if number(claim.get("neutral_band_pct"), "neutral_band_pct") < 0:
        raise ValueError("neutral band must be nonnegative")
    if registration.get("claim_sha256") != canonical_hash(claim):
        raise ValueError("claim is missing its matching preregistration hash")
    for field in ("registry_id", "record_id"):
        if not isinstance(registration.get(field), str) or not registration[field].strip():
            raise ValueError("independent preregistration reference required")
    registered = instant(registration.get("recorded_at"))
    if registered > start:
        raise ValueError("claim was registered after T0")
    if instant(claim["evidence_known_as_of"]) > registered:
        raise ValueError("decision evidence became known after preregistration")
    if registration.get("data_mode") != claim["data_mode"]:
        raise ValueError("registration data mode mismatch")
    validate_evidence_kind(registration.get("registry_kind"), claim["data_mode"], "registry")
    reject_explicit_synthetic_reference(registration, ("registry_id", "record_id"), claim["data_mode"])
    if registration.get("verification") != "EXTERNAL_READBACK_REQUIRED":
        raise ValueError("offline input cannot self-authenticate preregistration")
    return start, end


def validate_evidence_kind(kind: Any, data_mode: str, label: str) -> None:
    if kind not in {"SYNTHETIC_FIXTURE", "EXTERNAL_RECORD"}:
        raise ValueError(f"explicit {label} kind is required")
    if data_mode == "REAL_OBSERVATIONS" and kind == "SYNTHETIC_FIXTURE":
        raise ValueError(f"REAL_OBSERVATIONS contradicts declared synthetic {label}")


def reject_explicit_synthetic_reference(row: Mapping[str, Any], fields: tuple[str, ...], data_mode: str) -> None:
    # Recognize explicit fixture declarations only. Absence of these markers
    # does not establish authenticity; every external record remains unverified.
    if data_mode == "REAL_OBSERVATIONS":
        for field in fields:
            if str(row.get(field, "")).upper().startswith("SYNTHETIC"):
                raise ValueError(f"REAL_OBSERVATIONS contradicts explicit SYNTHETIC reference: {field}")


def endpoint(
    observations: list[dict[str, Any]], claim: Mapping[str, Any], when: datetime, as_of: datetime
) -> tuple[dict[str, Any] | None, str]:
    matching = []
    for row in observations:
        if not isinstance(row, dict):
            raise ValueError("observation must be an object")
        if any(row.get(field) != claim[field] for field in IDENTITY_FIELDS):
            continue
        observed = instant(row.get("observed_at"))
        if observed != when:
            continue
        if row.get("data_mode") != claim["data_mode"]:
            raise ValueError("observation data mode mismatch")
        validate_evidence_kind(row.get("source_kind"), claim["data_mode"], "observation source")
        reject_explicit_synthetic_reference(row, ("observation_id", "source_ref"), claim["data_mode"])
        available, captured = instant(row.get("available_at")), instant(row.get("captured_at"))
        if not observed <= available <= captured:
            raise ValueError("observation clocks are inconsistent")
        if number(row.get("value"), "observation value") <= 0:
            raise ValueError("Gold endpoint price must be positive")
        if row.get("vintage_kind") not in {"FIRST_RELEASE", "REVISION"}:
            raise ValueError("explicit vintage identity required")
        for key in ("observation_id", "source_ref", "raw_sha256"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"missing observation provenance: {key}")
        digest = row["raw_sha256"]
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("raw_sha256 must be a lowercase SHA256")
        matching.append(row)
    if not matching:
        return None, "MISSING_EXACT_OBSERVATION"
    available_rows = [r for r in matching if instant(r["available_at"]) <= as_of and instant(r["captured_at"]) <= as_of]
    if not available_rows:
        return None, "NOT_YET_AVAILABLE_OR_CAPTURED"
    first = [r for r in available_rows if r["vintage_kind"] == "FIRST_RELEASE"]
    if not first:
        return None, "REVISION_WITHOUT_FIRST_RELEASE"
    # No implicit latest-value selection: inconsistent first-release records block.
    if len({(r["value"], instant(r["available_at"])) for r in first}) != 1:
        raise ValueError("conflicting first-release observations")
    first.sort(key=lambda r: (instant(r["captured_at"]), canonical_hash(r)))
    return first[0], "ELIGIBLE_FIRST_RELEASE"


def settle(payload: Mapping[str, Any]) -> dict[str, Any]:
    claim, registration = payload.get("claim"), payload.get("preregistration")
    if not isinstance(claim, dict) or not isinstance(registration, dict):
        raise ValueError("claim and preregistration objects are required")
    start, end = validate_claim(claim, registration)
    as_of = instant(payload.get("as_of"))
    if as_of < instant(registration["recorded_at"]):
        raise ValueError("settlement as_of predates registration")
    observations = payload.get("observations")
    if not isinstance(observations, list):
        raise ValueError("observations must be an array")
    receipt: dict[str, Any] = {
        "program": "YMQ-GOLD2",
        "battle": "FUTURE-SETTLEMENT-OFFLINE-CANDIDATE",
        "claim_id": claim["claim_id"],
        "as_of": payload["as_of"],
        "data_mode": claim["data_mode"],
        "input_sha256": canonical_hash(payload),
        "claim_sha256": canonical_hash(claim),
        "preregistration_sha256": canonical_hash(registration),
        "preregistration_verification": "EXTERNAL_READBACK_REQUIRED",
        "observation_verification": "EXTERNAL_READBACK_REQUIRED",
        "source_authenticity": "UNVERIFIED",
        "authority": dict(AUTHORITY),
        "accepted_learning": False,
        "investment_effectiveness_proven": False,
        "status": "NOT_DUE",
        "model_score": None,
        "baseline_score": None,
    }
    if as_of < end:
        return receipt
    opening, opening_status = endpoint(observations, claim, start, as_of)
    closing, closing_status = endpoint(observations, claim, end, as_of)
    receipt["endpoint_status"] = {"t0": opening_status, "horizon_end": closing_status}
    if opening is None or closing is None:
        receipt["status"] = "INDETERMINATE_EVIDENCE"
        return receipt
    # Compare decimal products, not rounded binary percentage quotients. The
    # JSON float below is presentation only; it never determines the label.
    with localcontext() as context:
        context.prec = 50
        opening_decimal = Decimal(str(opening["value"]))
        numerator = (Decimal(str(closing["value"])) - opening_decimal) * Decimal(100)
        threshold = Decimal(str(claim["neutral_band_pct"])) * opening_decimal
        realized = 1 if numerator > threshold else -1 if numerator < -threshold else 0
        return_decimal = numerator / opening_decimal
        return_pct = float(return_decimal)
    if not math.isfinite(return_pct):
        raise ValueError("non-finite outcome return")
    receipt.update({
        "status": "SETTLED_RESEARCH_CANDIDATE",
        "outcome_return_pct": return_pct,
        "outcome_return_pct_decimal": str(return_decimal),
        "realized_direction": realized,
        "model_score": {"direction": claim["model_direction"], "correct": claim["model_direction"] == realized},
        "baseline_score": {"baseline_id": claim["baseline_id"], "direction": claim["baseline_direction"], "correct": claim["baseline_direction"] == realized},
        "selected_observation_sha256": {"t0": canonical_hash(opening), "horizon_end": canonical_hash(closing)},
        "outcome_semantics": "EXACT_SERIES_FIRST_RELEASE_SIMPLE_RETURN_NO_PNL_OR_TRADABILITY_CLAIM",
    })
    return receipt
