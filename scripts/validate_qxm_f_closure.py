#!/usr/bin/env python3
"""Fail-closed validator for QXM-F Financial Mechanics Capability Closure."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QXM_F = ROOT / "docs" / "architecture" / "qxm-f"
STATE = QXM_F / "QXM-F-STATE.json"
QXM2_STATE = ROOT / "docs" / "architecture" / "qxm2" / "QXM2-STATE.json"
QXM2_RECEIPT = ROOT / "docs" / "architecture" / "qxm2" / "QXM2-MERGE-RECEIPT-v0.1.json"
REGISTRY_INDEX = ROOT / "registry" / "registry-index.json"
SPEC = ROOT / "docs" / "superpowers" / "specs" / "2026-08-21-qxm-f-financial-mechanics-capability-closure-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-08-21-qxm-f-financial-mechanics-capability-closure.md"
G1_LEDGER = QXM_F / "g1" / "QXM-F-G1-ADMISSION-LEDGER-v0.1.json"
G1_REVIEW = QXM_F / "g1" / "QXM-F-G1-HUMAN-REVIEW-CARD-v0.1.md"

APPROVED_SPEC_SHA256 = "bc06e5b91cdf4ace24a228a691096ceb124285c8ae50fc8418905254a9abe8e2"
APPROVED_PLAN_SHA256 = "61db36bc9fc67365a9ba7e06a654d34563c83c659e9fd8480665b93056970da7"
QXM2_SEMANTIC_MERGE = "e1b7a65736c6f93089d7e635e5c72624345941fc"
QXM2_CLOSURE_MERGE = "5143b3c141c712a58c9a0417ac6bb915882fa4d5"
G1_HUMAN_TOKEN = "ACCEPT_QXM_F_G1_SELECTIVE_ADMISSION"

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

THEORY_HYP_DISPOSITIONS = {"ADMIT", "ADMIT_WITH_BOUNDARY", "KEEP_SHADOW", "REJECT"}
SEED_DISPOSITIONS = {"FORMALIZE", "DEFER", "REJECT"}
EXPECTED_THEORY_SHADOW_IDS = {f"QXM2-SHADOW-THEORY-{i:03d}" for i in range(1, 13)}
EXPECTED_HYP_SHADOW_IDS = {f"QXM2-SHADOW-HYP-{i:03d}" for i in range(1, 13)}
EXPECTED_SEED_IDS = {
    "QXM2-BSEED-P003-DRIVER-OOS",
    "QXM2-BSEED-P004-CASH-CONVERSION",
    "QXM2-BSEED-R01-CREDIT-TRANSMISSION",
    "QXM2-BSEED-V01-EXPECTATION-DECOMPOSITION",
    "QXM2-BSEED-S004-STRESS-EXIT",
    "QXM2-BSEED-CROSS001-RETURN-ATTRIBUTION",
}
EXPECTED_THEORY_IDS = {
    "THEORY-LEVTHIAGARAJAN-1993-FUNDAMENTAL-INFORMATION",
    "THEORY-NISSIMPENMAN-2001-RATIO-HIERARCHY",
    "THEORY-DECHOW-1994-ACCRUAL-MATCHING",
    "THEORY-SLOAN-1996-ACCRUAL-CASH-PERSISTENCE",
    "THEORY-BERNANKEGERTLER-1989-NET-WORTH-AGENCY-COST",
    "THEORY-KIYOTAKIMOORE-1997-COLLATERAL-CREDIT-CYCLES",
    "THEORY-SHARPE-1964-CAPITAL-ASSET-PRICES",
    "THEORY-CAMPBELLSHILLER-1988-PRESENT-VALUE-DECOMPOSITION",
    "THEORY-KYLE-1985-MARKET-DEPTH",
    "THEORY-BRUNNERMEIERPEDERSEN-2009-MARKET-FUNDING-LIQUIDITY",
    "THEORY-BRINSONHOODBEEBOWER-1986-PORTFOLIO-ATTRIBUTION",
    "THEORY-CAMPBELL-1991-RETURN-NEWS-DECOMPOSITION",
}
EXPECTED_HYPOTHESIS_IDS = {
    "HYP-P-201-DRIVER-INCREMENTAL-OOS",
    "HYP-P-202-DRIVER-REGIME-STABILITY",
    "HYP-P-203-CASH-CONVERSION-PERSISTENCE",
    "HYP-P-204-ACCRUAL-RELIABILITY",
    "HYP-P-205-CREDIT-SECTORAL-TRANSMISSION",
    "HYP-P-206-COLLATERAL-FEEDBACK",
    "HYP-V-201-EXPECTATION-DECOMPOSITION",
    "HYP-V-202-OOS-DISCOUNT-RATE",
    "HYP-S-201-STRESS-LIQUIDITY-INCREMENTAL",
    "HYP-S-202-FUNDING-LIQUIDITY-SPIRAL",
    "HYP-CROSS-201-RETURN-IDENTITY-RECONSTRUCTION",
    "HYP-CROSS-202-THESIS-FIDELITY",
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
            if key in {"target_price", "recommended_weight", "position_size", "buy_signal", "sell_signal", "broker_action"}:
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


def _pull_request_changed_paths(root: Path):
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if not base_ref:
        return []
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def assert_g1_pre_human_scope(paths) -> None:
    offenders = [path for path in paths if path.startswith("registry/") or path.startswith("canon/")]
    assert not offenders, f"G1 pre-Human Review cannot mutate formal Registry/Canon paths: {offenders}"


def validate_g1_admission_ledger(root: Path, ledger) -> None:
    require_fields(
        ledger,
        ["stage", "status", "object_count", "theory_count", "hypothesis_count", "benchmark_seed_count", "human_gate_token", "objects"],
        "G1 Admission Ledger",
    )
    assert ledger["stage"] == "QXM_F_G1_SELECTIVE_REGISTRY_ADMISSION"
    assert ledger["status"] == "candidate_ledger_human_pending"
    assert ledger["object_count"] == 30
    assert ledger["theory_count"] == 12
    assert ledger["hypothesis_count"] == 12
    assert ledger["benchmark_seed_count"] == 6
    assert ledger["human_gate_token"] == G1_HUMAN_TOKEN
    for key in (
        "formal_registry_mutation_authorized",
        "hypothesis_preregistration_authorized",
        "benchmark_execution_authorized",
        "capability_promotion_authorized",
        "trading_action_authorized",
    ):
        assert ledger[key] is False, (key, ledger[key])

    rows = ledger["objects"]
    assert len(rows) == 30
    theory_rows = [r for r in rows if r["object_class"] == "TheoryObject"]
    hyp_rows = [r for r in rows if r["object_class"] == "HypothesisObject"]
    seed_rows = [r for r in rows if r["object_class"] == "BenchmarkSeed"]
    assert len(theory_rows) == 12
    assert len(hyp_rows) == 12
    assert len(seed_rows) == 6
    assert {r["source_shadow_id"] for r in theory_rows} == EXPECTED_THEORY_SHADOW_IDS
    assert {r["source_shadow_id"] for r in hyp_rows} == EXPECTED_HYP_SHADOW_IDS
    assert {r["source_shadow_id"] for r in seed_rows} == EXPECTED_SEED_IDS
    assert {r["canonical_object_id"] for r in theory_rows} == EXPECTED_THEORY_IDS
    assert {r["canonical_object_id"] for r in hyp_rows} == EXPECTED_HYPOTHESIS_IDS

    for row in rows:
        require_fields(
            row,
            [
                "source_shadow_id", "object_class", "canonical_object_id", "candidate_id",
                "target_capability_identity", "qxm2_recommendation", "evidence_boundary",
                "recommended_disposition", "human_disposition", "rationale",
                "downstream_authority_requested", "predictive_or_timing_authority_requested",
            ],
            row.get("source_shadow_id", "G1 row"),
        )
        legal = SEED_DISPOSITIONS if row["object_class"] == "BenchmarkSeed" else THEORY_HYP_DISPOSITIONS
        assert row["recommended_disposition"] in legal, row["source_shadow_id"]
        assert row["human_disposition"] is None, row["source_shadow_id"]
        assert str(row["evidence_boundary"]).strip(), row["source_shadow_id"]
        assert str(row["rationale"]).strip(), row["source_shadow_id"]
        assert row["predictive_or_timing_authority_requested"] is False, row["source_shadow_id"]
        if row["candidate_id"] == "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE":
            assert row["predictive_or_timing_authority_requested"] is False

    v202 = next(r for r in hyp_rows if r["canonical_object_id"] == "HYP-V-202-OOS-DISCOUNT-RATE")
    assert v202["recommended_disposition"] == "KEEP_SHADOW"
    assert v202["downstream_authority_requested"] == "none"

    # Upstream referential integrity: the ledger may not invent IDs.
    shadow_theories = load_json(root / "docs" / "architecture" / "qxm2" / "QXM2-SHADOW-THEORY-OBJECTS-v0.1.json")["shadow_theories"]
    shadow_hypotheses = load_json(root / "docs" / "architecture" / "qxm2" / "QXM2-SHADOW-HYPOTHESIS-OBJECTS-v0.1.json")["shadow_hypotheses"]
    seeds = load_json(root / "docs" / "architecture" / "qxm2" / "QXM2-BENCHMARK-SEEDS-v0.1.json")["benchmark_seeds"]
    assert {x["shadow_object_id"] for x in shadow_theories} == EXPECTED_THEORY_SHADOW_IDS
    assert {x["shadow_object_id"] for x in shadow_hypotheses} == EXPECTED_HYP_SHADOW_IDS
    assert {x["benchmark_seed_id"] for x in seeds} == EXPECTED_SEED_IDS


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

    if state["status"] == "G1_SELECTIVE_ADMISSION_READY_FOR_HUMAN_REVIEW":
        ledger_path = root / "docs" / "architecture" / "qxm-f" / "g1" / "QXM-F-G1-ADMISSION-LEDGER-v0.1.json"
        review_path = root / "docs" / "architecture" / "qxm-f" / "g1" / "QXM-F-G1-HUMAN-REVIEW-CARD-v0.1.md"
        assert ledger_path.exists(), "G1 state requires Admission Ledger"
        assert review_path.exists(), "G1 state requires Human Review Card"
        validate_g1_admission_ledger(root, load_json(ledger_path))
        assert state["identity_settlement"] == "candidate_dispositions_complete_human_pending"
        assert state["g1"]["human_gate_token"] == G1_HUMAN_TOKEN
        assert state["next_gate"] == "QXM_F_G1_HUMAN_REVIEW"
        assert_g1_pre_human_scope(_pull_request_changed_paths(root))

    assert_no_authority_escalation(qxm2_receipt)
    assert_registry_counts_consistent(root)

    return {"stage": state["stage"], "status": state["status"], "next_gate": state["next_gate"]}


def main() -> None:
    result = validate_qxm_f(ROOT)
    print(f"QXM-F closure validation: PASS status={result['status']} next_gate={result['next_gate']}")


if __name__ == "__main__":
    main()
