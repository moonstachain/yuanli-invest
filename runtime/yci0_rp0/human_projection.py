from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

from .projection_compiler import ResearchProjection


class HumanProjectionError(ValueError):
    pass


@dataclass(frozen=True)
class MachineReceipt:
    receipt_id: str
    event_id: str
    source_id: str
    question_id: str
    request_hash: str
    response_hash: str
    status: str
    authority: str = "RESEARCH"


@dataclass(frozen=True)
class HumanProjectionResult:
    patch: dict[str, Any]
    receipt: MachineReceipt


ALLOWED_PATCH_FIELDS = {
    "Journey Stage",
    "Gate Status",
    "Machine Evidence Status",
    "Machine Gate Status",
    "Machine Known As Of",
    "Machine Event ID",
    "Machine Source ID",
    "Machine Sync Status",
    "Transition Suggestion",
    "Transition Reason",
    "Runtime Projection ID",
}


def _hash(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _receipt(current: Mapping[str, Any], event: Mapping[str, Any], projection: ResearchProjection, patch: Mapping[str, Any], status: str) -> MachineReceipt:
    request = {
        "question_id": projection.question_id,
        "projection_id": projection.projection_id,
        "current_stage": current.get("Journey Stage"),
        "current_machine_known_as_of": current.get("Machine Known As Of"),
        "event": {
            "event_id": event.get("event_id"),
            "source_id": event.get("source_id"),
            "known_as_of": event.get("known_as_of"),
            "evidence_status": event.get("evidence_status"),
            "gate_status": event.get("gate_status"),
            "authority": event.get("authority"),
        },
    }
    request_hash = _hash(request)
    response_hash = _hash(dict(patch))
    receipt_id = f"YCI0-RP0-RCPT-{_hash({'request': request_hash, 'response': response_hash, 'status': status})[:16]}"
    return MachineReceipt(
        receipt_id=receipt_id,
        event_id=str(event.get("event_id") or ""),
        source_id=str(event.get("source_id") or ""),
        question_id=projection.question_id,
        request_hash=request_hash,
        response_hash=response_hash,
        status=status,
    )


def build_human_projection(
    current: Mapping[str, Any],
    event: Mapping[str, Any],
    projection: ResearchProjection,
) -> HumanProjectionResult:
    if projection.authority != "RESEARCH" or str(event.get("authority")) != "RESEARCH":
        raise HumanProjectionError("RESEARCH_AUTHORITY_REQUIRED")
    question_id = str(current.get("Question ID") or "")
    if question_id != projection.question_id:
        raise HumanProjectionError("QUESTION_ID_MISMATCH")
    event_id = str(event.get("event_id") or "")
    source_id = str(event.get("source_id") or "")
    known_as_of = str(event.get("known_as_of") or "")
    if not event_id or not source_id or not known_as_of:
        raise HumanProjectionError("EVENT_ID_SOURCE_AND_KNOWN_AS_OF_REQUIRED")

    current_known = str(current.get("Machine Known As Of") or "")
    if current_known and known_as_of <= current_known:
        patch: dict[str, Any] = {}
        return HumanProjectionResult(
            patch=patch,
            receipt=_receipt(current, event, projection, patch, "STALE_IGNORED"),
        )

    evidence_status = str(event.get("evidence_status") or "UNKNOWN")
    gate_status = str(event.get("gate_status") or "UNKNOWN")
    if evidence_status not in {"PASS", "CURRENT_CONTEXT_ONLY", "BLOCKED", "UNKNOWN"}:
        raise HumanProjectionError("EVIDENCE_STATUS_INVALID")
    if gate_status not in {"OPEN", "PASS", "BLOCKED", "UNKNOWN", "NO_GO"}:
        raise HumanProjectionError("GATE_STATUS_INVALID")

    patch = {
        "Machine Evidence Status": evidence_status,
        "Machine Gate Status": gate_status,
        "Machine Known As Of": known_as_of,
        "Machine Event ID": event_id,
        "Machine Source ID": source_id,
        "Machine Sync Status": "APPLIED",
        "Runtime Projection ID": projection.projection_id,
    }
    current_stage = str(current.get("Journey Stage") or "")

    if evidence_status in {"UNKNOWN", "BLOCKED"}:
        patch["Journey Stage"] = "02 EVIDENCE"
        patch["Gate Status"] = evidence_status
        patch["Transition Suggestion"] = "02 EVIDENCE"
        patch["Transition Reason"] = f"FAIL_CLOSED_{evidence_status}"
    elif (
        evidence_status == "PASS"
        and gate_status == "PASS"
        and current_stage == "04 TRANSMISSION"
        and projection.audit_eligible
        and projection.defeat_condition
    ):
        patch["Journey Stage"] = "05 AUDIT"
        patch["Gate Status"] = "PASS"
        patch["Transition Suggestion"] = "05 AUDIT"
        patch["Transition Reason"] = "ONE_STAGE_FORWARD_TO_AUDIT"
    else:
        patch["Transition Suggestion"] = "HOLD"
        patch["Transition Reason"] = "NO_AUTHORIZED_TRANSITION"

    if "Journey Stage" in patch and patch["Journey Stage"] == "06 SHADOW":
        raise HumanProjectionError("SHADOW_TRANSITION_DENIED")
    if not set(patch).issubset(ALLOWED_PATCH_FIELDS):
        raise HumanProjectionError("PATCH_FIELD_NOT_WHITELISTED")

    return HumanProjectionResult(
        patch=patch,
        receipt=_receipt(current, event, projection, patch, "APPLIED"),
    )
