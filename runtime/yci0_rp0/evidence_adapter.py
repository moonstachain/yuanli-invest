from __future__ import annotations

import hashlib
import json
from typing import Any

from .contracts import EvidenceStatus, PITAdmissionReason, RealityEvidence, SourceType

RESEARCH_AUTHORITY = "RESEARCH"


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _classify_source(raw: dict[str, Any], metric_spec: dict[str, Any]) -> SourceType:
    descriptor = " ".join(
        filter(
            None,
            [
                _text(raw.get("source_type")),
                _text(raw.get("source_name")),
                _text(metric_spec.get("source_type")),
            ],
        )
    ).upper()
    if "ALICE" in descriptor or "AUTHORED" in descriptor:
        return SourceType.AUTHORED_KNOWLEDGE_CANDIDATE
    if "FIRST_PARTY" in descriptor:
        return SourceType.FIRST_PARTY_EVIDENCE
    if "OFFICIAL" in descriptor:
        return SourceType.OFFICIAL_EVIDENCE
    if "STRUCTURED" in descriptor or "SENSOR" in descriptor or "WIND" in descriptor:
        return SourceType.STRUCTURED_SENSOR
    return SourceType.UNKNOWN


def _source_locator(raw: dict[str, Any], metric_spec: dict[str, Any]) -> str:
    explicit = _text(raw.get("source_locator"))
    if explicit:
        return explicit
    parts = [
        _text(raw.get("source_name")) or "unknown-source",
        _text(metric_spec.get("metric_id")) or "unknown-metric",
        _text(raw.get("entity_id")) or "unknown-entity",
        _text(raw.get("period")) or "unknown-period",
    ]
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"source://{digest}"


def _required_semantics_missing(raw: dict[str, Any], metric_spec: dict[str, Any]) -> list[str]:
    policy = str(metric_spec.get("pit_policy") or "").upper()
    missing: list[str] = []
    if "OBSERVED" in policy and not _text(raw.get("observed_at")):
        missing.append("observed_at")
    if "RELEASE" in policy and not _text(raw.get("released_at")):
        missing.append("released_at")
    if "VINTAGE" in policy and not _text(raw.get("vintage")):
        missing.append("vintage")
    if "PROXY_DEFINITION" in policy and not (
        _text(raw.get("proxy_definition")) or _text(metric_spec.get("proxy_definition"))
    ):
        missing.append("proxy_definition")
    return missing


def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def normalize_observation(raw: dict[str, Any], metric_spec: dict[str, Any]) -> RealityEvidence:
    source_type = _classify_source(raw, metric_spec)
    locator = _source_locator(raw, metric_spec)
    authority_in = _text(raw.get("authority"))
    known_as_of = _text(raw.get("known_as_of"))
    semantic_missing = _required_semantics_missing(raw, metric_spec)

    if authority_in not in (None, RESEARCH_AUTHORITY):
        status = EvidenceStatus.BLOCKED
        reason = PITAdmissionReason.AUTHORITY_VIOLATION
    elif source_type is SourceType.AUTHORED_KNOWLEDGE_CANDIDATE:
        status = EvidenceStatus.CURRENT_CONTEXT_ONLY
        reason = PITAdmissionReason.AUTHORED_SOURCE_NOT_EVIDENCE
    elif not known_as_of:
        status = EvidenceStatus.UNKNOWN
        reason = PITAdmissionReason.MISSING_KNOWN_AS_OF
    elif semantic_missing:
        status = EvidenceStatus.CURRENT_CONTEXT_ONLY
        if any(item in {"released_at", "vintage"} for item in semantic_missing):
            reason = PITAdmissionReason.MISSING_RELEASE_OR_VINTAGE
        else:
            reason = PITAdmissionReason.MISSING_REQUIRED_PIT_SEMANTICS
    elif source_type is SourceType.UNKNOWN:
        status = EvidenceStatus.UNKNOWN
        reason = PITAdmissionReason.UNKNOWN_SOURCE
    else:
        status = EvidenceStatus.PASS
        reason = PITAdmissionReason.PIT_QUALIFIED

    core = {
        "metric_id": _text(metric_spec.get("metric_id")) or "UNKNOWN",
        "entity_id": _text(raw.get("entity_id")),
        "metric_name": _text(raw.get("metric_name")) or _text(metric_spec.get("family")) or "UNKNOWN",
        "value": raw.get("value"),
        "unit": _text(raw.get("unit")),
        "period": _text(raw.get("period")),
        "source_type": source_type.value,
        "source_name": _text(raw.get("source_name")) or "UNKNOWN",
        "source_locator": locator,
        "observed_at": _text(raw.get("observed_at")),
        "released_at": _text(raw.get("released_at")),
        "known_as_of": known_as_of,
        "retrieved_at": _text(raw.get("retrieved_at")),
        "revised_at": _text(raw.get("revised_at")),
        "vintage": _text(raw.get("vintage")),
        "receipt_id": _text(raw.get("receipt_id")),
        "authority": RESEARCH_AUTHORITY,
    }
    content_hash = _canonical_hash(core)
    evidence_id = _text(raw.get("evidence_id")) or f"evd-{content_hash[:24]}"
    return RealityEvidence(
        evidence_id=evidence_id,
        evidence_status=status,
        pit_admission_reason=reason,
        content_hash=content_hash,
        **core,
    )


def pit_eligible(evidence: RealityEvidence) -> bool:
    return (
        evidence.authority == RESEARCH_AUTHORITY
        and evidence.evidence_status is EvidenceStatus.PASS
        and evidence.pit_admission_reason is PITAdmissionReason.PIT_QUALIFIED
        and bool(evidence.known_as_of)
        and evidence.source_type is not SourceType.AUTHORED_KNOWLEDGE_CANDIDATE
    )
