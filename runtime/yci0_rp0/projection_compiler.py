from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Mapping

from .context_adapter import ContextPack
from .narrative_transmission import NarrativeTransmissionCard
from .price_payoff import PricePayoffCard
from .state_compiler import RealityStateCard


class ProjectionError(ValueError):
    pass


@dataclass(frozen=True)
class ResearchProjection:
    projection_id: str
    question_id: str
    as_of: str
    reality_as_of: str
    context_pack_id: str
    narrative: NarrativeTransmissionCard
    price_payoff: PricePayoffCard
    defeat_condition: str
    confidence: str
    evidence_refs: tuple[str, ...]
    audit_eligible: bool
    authority: str = "RESEARCH"
    status: str = "RESEARCH_ONLY"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def compile_projection(
    question: Mapping[str, Any],
    reality: RealityStateCard,
    context: ContextPack,
    narrative: NarrativeTransmissionCard,
    payoff: PricePayoffCard,
) -> ResearchProjection:
    if str(question.get("authority")) != "RESEARCH":
        raise ProjectionError("RESEARCH_AUTHORITY_REQUIRED")
    if reality.authority != "RESEARCH" or context.authority != "RESEARCH":
        raise ProjectionError("UPSTREAM_AUTHORITY_INVALID")
    if narrative.authority != "RESEARCH" or payoff.authority != "RESEARCH":
        raise ProjectionError("COMPILER_AUTHORITY_INVALID")
    if narrative.scientific_status != "LIMITED":
        raise ProjectionError("NARRATIVE_STATUS_INVALID")
    if payoff.scientific_status != "RESEARCH":
        raise ProjectionError("PAYOFF_STATUS_INVALID")
    defeat_condition = str(payoff.defeat_condition or "").strip()
    if not defeat_condition:
        raise ProjectionError("DEFEAT_CONDITION_REQUIRED")
    question_id = str(question.get("question_id") or "").strip()
    as_of = str(question.get("as_of") or "").strip()
    if not question_id or not as_of:
        raise ProjectionError("QUESTION_ID_AND_AS_OF_REQUIRED")
    if context.question_id != question_id:
        raise ProjectionError("CONTEXT_QUESTION_MISMATCH")
    evidence_refs = tuple(dict.fromkeys(narrative.evidence_refs + payoff.evidence_refs))
    payload = {
        "question_id": question_id,
        "as_of": as_of,
        "reality_as_of": reality.as_of,
        "context_pack_id": context.context_pack_id,
        "narrative": narrative.to_dict(),
        "price_payoff": payoff.to_dict(),
        "defeat_condition": defeat_condition,
        "evidence_refs": evidence_refs,
        "authority": "RESEARCH",
    }
    projection_hash = _hash(payload)
    return ResearchProjection(
        projection_id=f"YCI0-RP0-PROJ-{projection_hash[:16]}",
        question_id=question_id,
        as_of=as_of,
        reality_as_of=reality.as_of,
        context_pack_id=context.context_pack_id,
        narrative=narrative,
        price_payoff=payoff,
        defeat_condition=defeat_condition,
        confidence="MEDIUM",
        evidence_refs=evidence_refs,
        audit_eligible=True,
    )
