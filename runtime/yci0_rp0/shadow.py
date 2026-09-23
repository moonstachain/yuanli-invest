from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any

from .audit import RealityAudit
from .projection_compiler import ResearchProjection


class ShadowError(ValueError):
    pass


def _hash(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _parse(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _fmt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ShadowT0:
    shadow_id: str
    projection_id: str
    t0_known_as_of: str
    t0_evidence_hash: str
    t0_context_hash: str
    t0_projection_hash: str
    defeat_condition: str
    review_schedule: dict[str, str]
    status: str
    settlement_result: str | None
    authority: str = "SHADOW_RESEARCH_ONLY"
    capital_authorized: bool = False
    execution_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def freeze_shadow(
    projection: ResearchProjection,
    audit: RealityAudit,
    *,
    shadow_authorized: bool,
    t0_known_as_of: str,
) -> ShadowT0:
    if projection.authority != "RESEARCH" or audit.authority != "RESEARCH":
        raise ShadowError("RESEARCH_AUTHORITY_REQUIRED")
    if audit.projection_id != projection.projection_id:
        raise ShadowError("AUDIT_PROJECTION_MISMATCH")
    if audit.verdict != "PASS":
        raise ShadowError("AUDIT_PASS_REQUIRED")
    if not shadow_authorized:
        raise ShadowError("SHADOW_AUTHORITY_REQUIRED")
    if not projection.defeat_condition:
        raise ShadowError("DEFEAT_CONDITION_REQUIRED")
    if audit.defeat_condition != projection.defeat_condition:
        raise ShadowError("DEFEAT_CONDITION_DRIFT")

    t0 = _parse(t0_known_as_of)
    evidence_hash = _hash({"evidence_refs": projection.evidence_refs})
    context_hash = _hash({"context_pack_id": projection.context_pack_id})
    projection_hash = _hash(projection.to_dict())
    shadow_id = f"YCI0-RP0-SHADOW-{projection_hash[:16]}"
    schedule = {
        "T+30": _fmt(t0 + timedelta(days=30)),
        "T+90": _fmt(t0 + timedelta(days=90)),
        "T+180": _fmt(t0 + timedelta(days=180)),
    }
    return ShadowT0(
        shadow_id=shadow_id,
        projection_id=projection.projection_id,
        t0_known_as_of=_fmt(t0),
        t0_evidence_hash=evidence_hash,
        t0_context_hash=context_hash,
        t0_projection_hash=projection_hash,
        defeat_condition=projection.defeat_condition,
        review_schedule=schedule,
        status="SHADOW_PREREGISTERED",
        settlement_result=None,
    )
