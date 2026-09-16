from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .projection_compiler import ResearchProjection


class AuditError(ValueError):
    pass


ALLOWED_VERDICTS = {"OPEN", "PASS", "BLOCKED", "UNKNOWN", "NO_GO"}


@dataclass(frozen=True)
class RealityAudit:
    audit_id: str
    projection_id: str
    hard_negative: str
    evidence_gap: str
    common_shock: str
    survival_risk: str
    defeat_condition: str
    verdict: str
    reviewer: str
    authority: str = "RESEARCH"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required(name: str, value: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise AuditError(f"{name.upper()}_REQUIRED")
    return text


def build_reality_audit(
    projection: ResearchProjection,
    *,
    hard_negative: str,
    evidence_gap: str,
    common_shock: str,
    survival_risk: str,
    defeat_condition: str,
    verdict: str,
    reviewer: str,
) -> RealityAudit:
    if projection.authority != "RESEARCH":
        raise AuditError("RESEARCH_AUTHORITY_REQUIRED")
    if not projection.audit_eligible:
        raise AuditError("PROJECTION_NOT_AUDIT_ELIGIBLE")
    hard_negative = _required("hard_negative", hard_negative)
    evidence_gap = _required("evidence_gap", evidence_gap)
    common_shock = _required("common_shock", common_shock)
    survival_risk = _required("survival_risk", survival_risk)
    defeat_condition = _required("defeat_condition", defeat_condition)
    verdict = _required("verdict", verdict)
    reviewer = _required("reviewer", reviewer)
    if verdict not in ALLOWED_VERDICTS:
        raise AuditError("VERDICT_INVALID")
    if defeat_condition != projection.defeat_condition:
        raise AuditError("DEFEAT_CONDITION_DRIFT")
    audit_id = f"YCI0-RP0-AUDIT-{projection.projection_id[-12:]}"
    return RealityAudit(
        audit_id=audit_id,
        projection_id=projection.projection_id,
        hard_negative=hard_negative,
        evidence_gap=evidence_gap,
        common_shock=common_shock,
        survival_risk=survival_risk,
        defeat_condition=defeat_condition,
        verdict=verdict,
        reviewer=reviewer,
    )
