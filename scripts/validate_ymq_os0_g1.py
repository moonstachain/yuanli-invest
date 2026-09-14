from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "config/ymq_os0/g1_sovereign_stack.v0.1.json"

FORBIDDEN_RUNTIME_INTENTS = {"position_sizing", "broker_order", "real_capital_move"}


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    planes = contract.get("planes", {})
    required = {"law", "reality", "experiment", "experience", "runtime"}
    if set(planes) != required:
        errors.append("five_planes_required")
        return errors

    if planes["law"].get("authority") != "CANON":
        errors.append("law_plane_must_hold_canon_authority")
    if planes["law"].get("replaceable") is not False:
        errors.append("law_plane_not_replaceable")

    if planes["experiment"].get("authority") == "CANON":
        errors.append("experiment_provider_cannot_hold_canon_authority")
    if planes["experience"].get("authority") != "PROJECTION_ONLY":
        errors.append("experience_must_be_projection_only")
    if planes["runtime"].get("authority") != "RESEARCH_ORCHESTRATION_ONLY":
        errors.append("runtime_must_be_research_only")

    laws = contract.get("laws", {})
    for law in (
        "unknown_is_deny",
        "research_not_capital",
        "research_not_execution",
        "claim_authority_lte_evidence_authority",
    ):
        if laws.get(law) is not True:
            errors.append(f"law_required:{law}")

    blocked = set(contract.get("explicitly_not_authorized", []))
    required_blocked = {"CAPITAL_AUTHORITY", "POSITION_SIZING", "BROKER_EXECUTION", "REAL_CAPITAL_MOVEMENT"}
    if not required_blocked.issubset(blocked):
        errors.append("explicit_non_authorizations_incomplete")

    identity = contract.get("cross_plane_identity", {})
    if set(identity.get("required", [])) != {"run_id", "git_sha", "as_of", "evidence_refs"}:
        errors.append("cross_plane_identity_incomplete")
    if identity.get("immutable_receipt") is not True:
        errors.append("immutable_receipt_required")
    return errors


def validate_runtime_request(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("evidence_status") in {None, "UNKNOWN", "DENY", "BLOCKED"}:
        return {"allowed": False, "reason": "UNKNOWN_DENY"}
    if payload.get("intent") in FORBIDDEN_RUNTIME_INTENTS:
        return {"allowed": False, "reason": "AUTHORITY_DENY"}
    if payload.get("requested_authority") in {"CAPITAL", "EXECUTION"}:
        return {"allowed": False, "reason": "AUTHORITY_DENY"}
    return {"allowed": True, "reason": "RESEARCH_ONLY"}


def validate_projection_manifest(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("role") != "PROJECTION_ONLY":
        errors.append("projection_role_required")
    if payload.get("canonical_truth") is not False:
        errors.append("projection_cannot_be_canonical_truth")
    if payload.get("can_grant_authority") is not False:
        errors.append("projection_cannot_grant_authority")
    return errors


def main() -> int:
    contract = json.loads(DEFAULT_CONTRACT.read_text())
    errors = validate_contract(contract)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: YMQ-OS0-G1 sovereign stack contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
