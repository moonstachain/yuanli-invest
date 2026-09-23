from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class EvidenceStatus(str, Enum):
    PASS = "PASS"
    CURRENT_CONTEXT_ONLY = "CURRENT_CONTEXT_ONLY"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class SourceType(str, Enum):
    STRUCTURED_SENSOR = "STRUCTURED_SENSOR"
    FIRST_PARTY_EVIDENCE = "FIRST_PARTY_EVIDENCE"
    OFFICIAL_EVIDENCE = "OFFICIAL_EVIDENCE"
    AUTHORED_KNOWLEDGE_CANDIDATE = "AUTHORED_KNOWLEDGE_CANDIDATE"
    UNKNOWN = "UNKNOWN"


class PITAdmissionReason(str, Enum):
    PIT_QUALIFIED = "PIT_QUALIFIED"
    MISSING_KNOWN_AS_OF = "MISSING_KNOWN_AS_OF"
    MISSING_RELEASE_OR_VINTAGE = "MISSING_RELEASE_OR_VINTAGE"
    MISSING_REQUIRED_PIT_SEMANTICS = "MISSING_REQUIRED_PIT_SEMANTICS"
    AUTHORED_SOURCE_NOT_EVIDENCE = "AUTHORED_SOURCE_NOT_EVIDENCE"
    AUTHORITY_VIOLATION = "AUTHORITY_VIOLATION"
    UNKNOWN_SOURCE = "UNKNOWN_SOURCE"


@dataclass(frozen=True)
class RealityEvidence:
    evidence_id: str
    metric_id: str
    entity_id: str | None
    metric_name: str
    value: Any
    unit: str | None
    period: str | None
    source_type: SourceType
    source_name: str
    source_locator: str
    observed_at: str | None
    released_at: str | None
    known_as_of: str | None
    retrieved_at: str | None
    revised_at: str | None
    vintage: str | None
    evidence_status: EvidenceStatus
    pit_admission_reason: PITAdmissionReason
    receipt_id: str | None
    content_hash: str
    authority: str
