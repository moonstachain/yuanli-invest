#!/usr/bin/env python3
"""Fail-closed validator for QXM-F Financial Mechanics Capability Closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QXM_F = ROOT / "docs" / "architecture" / "qxm-f"
STATE = QXM_F / "QXM-F-STATE.json"
QXM2_STATE = ROOT / "docs" / "architecture" / "qxm2" / "QXM2-STATE.json"
QXM2_RECEIPT = ROOT / "docs" / "architecture" / "qxm2" / "QXM2-MERGE-RECEIPT-v0.1.json"
REGISTRY_INDEX = ROOT / "registry" / "registry-index.json"
SPEC = ROOT / "docs" / "superpowers" / "specs" / "2026-08-21-qxm-f-financial-mechanics-capability-closure-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-08-21-qxm-f-financial-mechanics-capability-closure.md"

APPROVED_SPEC_SHA256 = "bc06e5b91cdf4ace24a228a691096ceb124285c8ae50fc8418905254a9abe8e2"
APPROVED_PLAN_SHA256 = "61db36bc9fc67365a9ba7e06a654d34563c83c659e9fd8480665b93056970da7"
QXM2_SEMANTIC_MERGE = "e1b7a65736c6f93089d7e635e5c72624345941fc"
QXM2_CLOSURE_MERGE = "5143b3c141c712a58c9a0417ac6bb915882fa4d5"

LEGAL_STATES = {
    "G0_QXM2_ACCEPTED_MERGED",
    "G1_SELECTIVE_ADMISSION_READY_FOR_HUMAN_REVIEW",
    "G1_ADMITTED_MERGED",
    "G2_PREREGISTRATION_READY_FOR_HUMAN_REVIEW",
    "G2_PREREGISTERED_MERGED",
    "G3_PROVIDER_PROTOCOL_READY_FOR_HUMAN_REVIEW",
    "G3_REALITY_PROOF_EXECUTION_AUTHORIZED",
    "G3_REALITY_PROOF_READY_FOR_HUMAN_REVIEW",
    "G3_RESULTS_MERGED",
    "G4_SETTLEMENT_READY_FOR_HUMAN_REVIEW",
    "G4_SETTLED_MERGED",
    "G5_CLOSURE_READY_FOR_HUMAN_REVIEW",
    "QXM_PROJECT_CLOSED",
}

PROHIBITED_TRUE_AUTHORITIES = {
    "registry_admission_authorized",
    "hypothesis_preregistration_authorized",
    "formal_benchmark_creation_authorized",
    "benchmark_execution_authorized",
    "benchmark_pass_claim_authorized",
    "capability_promotion_authorized",
    "production_runtime_authorized",
    "trading_action_authorized",
    "live_execution",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require_fields(obj, fields, context="object"):
    missing = [field for field in fields if field not in obj]
    assert not missing, f"{context} missing fields: {missing}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_state(state: str) -> None:
    assert state in LEGAL_STATES, f"illegal QXM-F state: {state}"


def assert_no_authority_escalation(obj) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in PROHIBITED_TRUE_AUTHORITIES:
                assert value is False, f"unauthorized QXM-F authority escalation: {key}={value!r}"
            if key in {
                "target_price",
                "recommended_weight",
                "position_size",
                "buy_signal",
                "sell_signal",
                "broker_action",
            }:
                assert value in (None, False, "none", "not_authorized"), f"prohibited investment action: {key}={value!r}"
            assert_no_authority_escalation(value)
    elif isinstance(obj, list):
        for item in obj:
            assert_no_authority_escalation(item)


def assert_receipt_precedes_projection(state, qxm2_receipt) -> None:
    assert qxm2_receipt["merge_authority"] == "AUTHORIZE_QXM2_MERGE"
    assert qxm2_receipt["semantic_merge_commit"] == QXM2_SEMANTIC_MERGE
    assert state["upstream_qxm2"]["merge_receipt"] == "docs/architecture/qxm2/QXM2-MERGE-RECEIPT-v0.1.json"
    assert state["upstream_qxm2"]["resolved"] is True


def assert_registry_counts_consistent(root: Path) -> None:
    idx = load_json(root / "registry" / "registry-index.json")
    assert idx["entry_count_total"] == sum(item["entry_count"] for item in idx["registries"])
    for item in idx["registries"]:
        subindex = load_json(root / item["path"] / "_index.json")
        assert subindex["entry_count"] == item["entry_count"], item["name"]
        assert subindex["object_type"] == item["object_type"], item["name"]


def validate_qxm_f(root: Path = ROOT):
    root = Path(root)
    state_path = root / "docs" / "architecture" / "qxm-f" / "QXM-F-STATE.json"
    qxm2_state_path = root / "docs" / "architecture" / "qxm2" / "QXM2-STATE.json"
    qxm2_receipt_path = root / "docs" / "architecture" / "qxm2" / "QXM2-MERGE-RECEIPT-v0.1.json"
    spec_path = root / "docs" / "superpowers" / "specs" / "2026-08-21-qxm-f-financial-mechanics-capability-closure-design.md"
    plan_path = root / "docs" / "superpowers" / "plans" / "2026-08-21-qxm-f-financial-mechanics-capability-closure.md"

    for path in (state_path, qxm2_state_path, qxm2_receipt_path, spec_path, plan_path):
        assert path.exists(), f"missing QXM-F dependency: {path.relative_to(root)}"

    state = load_json(state_path)
    qxm2_state = load_json(qxm2_state_path)
    qxm2_receipt = load_json(qxm2_receipt_path)

    assert state["stage"] == "QXM_F_FINANCIAL_MECHANICS_CAPABILITY_CLOSURE"
    assert_state(state["status"])
    assert state["program_formula"] == "Identity Settlement x Reality Settlement x Learning Settlement"

    approved = state["approved_design"]
    assert approved["written_spec_approval"] == "ACCEPT_QXM_F_WRITTEN_DESIGN_SPEC"
    assert approved["approved_spec_sha256"] == APPROVED_SPEC_SHA256
    assert approved["approved_plan_sha256"] == APPROVED_PLAN_SHA256
    assert sha256(spec_path) == APPROVED_SPEC_SHA256, "approved QXM-F spec drift"
    assert sha256(plan_path) == APPROVED_PLAN_SHA256, "approved QXM-F plan drift"

    assert qxm2_state["status"] == "accepted_merged"
    assert qxm2_state["merge_commit"] == QXM2_SEMANTIC_MERGE
    assert qxm2_state["qxm_f_next_gate"] == "QXM_F_G1_SELECTIVE_ADMISSION"
    assert state["upstream_qxm2"]["status"] == "accepted_merged"
    assert state["upstream_qxm2"]["semantic_merge_commit"] == QXM2_SEMANTIC_MERGE
    assert state["upstream_qxm2"]["closure_merge_commit"] == QXM2_CLOSURE_MERGE
    assert_receipt_precedes_projection(state, qxm2_receipt)

    for key in (
        "registry_admission_authority",
        "hypothesis_preregistration_authority",
        "formal_benchmark_creation_authority",
        "benchmark_execution_authority",
        "capability_promotion_authority",
        "production_runtime_authority",
        "trading_authority",
    ):
        assert state[key] == "none", (key, state[key])

    if state["status"] == "G0_QXM2_ACCEPTED_MERGED":
        assert state["identity_settlement"] == "not_started"
        assert state["reality_settlement"] == "not_started"
        assert state["learning_settlement"] == "not_started"
        assert state["next_gate"] == "QXM_F_G1_SELECTIVE_ADMISSION"

    assert_no_authority_escalation(qxm2_receipt)
    assert_registry_counts_consistent(root)

    return {
        "stage": state["stage"],
        "status": state["status"],
        "next_gate": state["next_gate"],
    }


def main() -> None:
    result = validate_qxm_f(ROOT)
    print(f"QXM-F closure validation: PASS status={result['status']} next_gate={result['next_gate']}")


if __name__ == "__main__":
    main()
