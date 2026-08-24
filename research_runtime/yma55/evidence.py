from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

RESOLVER_TIERS = {"E0", "E1", "E2"}
RETROSPECTIVE_TIERS = {"E3", "E4"}
ALL_TIERS = RESOLVER_TIERS | RETROSPECTIVE_TIERS

REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "title",
    "publisher",
    "canonical_url",
    "document_date",
    "published_at",
    "retrieved_at",
    "evidence_tier",
    "producer_class",
    "originating_source_id",
    "public_at_t0",
    "admissible_at_cutoff",
    "provenance_note",
    "claims",
    "signals",
}


def _dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def validate_evidence_source(source: dict[str, Any]) -> None:
    missing = REQUIRED_SOURCE_FIELDS - set(source)
    if missing:
        raise ValueError(f"evidence source missing fields: {sorted(missing)}")
    if source["evidence_tier"] not in ALL_TIERS:
        raise ValueError("unsupported evidence tier")
    _dt(source["published_at"])
    _dt(source["retrieved_at"])
    if not isinstance(source["claims"], list) or not isinstance(source["signals"], list):
        raise ValueError("claims and signals must be lists")


def admit_evidence(
    sources: list[dict[str, Any]],
    evidence_cutoff: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cutoff = _dt(evidence_cutoff)
    admitted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for raw in sources:
        source = deepcopy(raw)
        validate_evidence_source(source)
        reason: str | None = None
        if _dt(source["published_at"]) > cutoff:
            reason = "POST_CUTOFF"
        elif source["public_at_t0"] is not True:
            reason = "NOT_PUBLIC_AT_T0"
        elif source["evidence_tier"] in RETROSPECTIVE_TIERS:
            reason = "RETROSPECTIVE_TIER"
        elif source.get("admissible_at_cutoff") is not True:
            reason = "NOT_ADMISSIBLE_AT_CUTOFF"
        if reason:
            rejected.append({"source_id": source["source_id"], "reason": reason, "source": source})
        else:
            admitted.append(source)
    return admitted, rejected


def _has_independent_e1(sources: list[dict[str, Any]]) -> bool:
    e0s = [s for s in sources if s.get("evidence_tier") == "E0"]
    e1s = [s for s in sources if s.get("evidence_tier") == "E1"]
    for e0 in e0s:
        for e1 in e1s:
            different_origin = e1.get("originating_source_id") != e0.get("originating_source_id")
            different_producer = e1.get("producer_class") != e0.get("producer_class")
            if different_origin and different_producer:
                return True
    return False


def assess_hydration(sources: list[dict[str, Any]]) -> dict[str, Any]:
    e0_count = sum(1 for s in sources if s.get("evidence_tier") == "E0")
    e1_count = sum(1 for s in sources if s.get("evidence_tier") == "E1")
    independent_e1 = _has_independent_e1(sources)
    if e0_count >= 1 and independent_e1:
        status = "EVIDENCE_HYDRATED"
    elif e0_count >= 1 or e1_count >= 1:
        status = "PARTIAL_HYDRATION"
    else:
        status = "INSUFFICIENT_EVIDENCE"
    return {
        "status": status,
        "e0_count": e0_count,
        "e1_count": e1_count,
        "independent_e1": independent_e1,
    }
