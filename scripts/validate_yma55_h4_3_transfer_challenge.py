#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_runtime.yma55.transfer_challenge import TRANSFER_VARIANTS, run_h43_matrix

H43 = ROOT / "fixtures" / "replay" / "yma55_h4_3"
DOCS = ROOT / "docs" / "architecture" / "yma55"
STATE_PATH = DOCS / "YMA55-H4.3-STATE.json"
REPORT_PATH = DOCS / "YMA55-H4.3-PAIRED-CHALLENGE-REPORT-v0.1.md"
REVIEW_PATH = DOCS / "YMA55-H4.3-HUMAN-REVIEW-CARD-v0.1.md"
TRANSITION_PATH = DOCS / "YMA55-2.1-KERNEL-CLOSURE-AND-PHASE2-TRANSITION-v0.1.md"

EXPECTED_METRICS = {
    "T0_UNCONDITIONAL_TRANSPORT": {
        "unsafe_prior_applications": 3,
        "correct_structural_blocks": 0,
        "eligible_prior_maintains": 1,
        "eligible_prior_violations_detected": 0,
        "eligible_prior_violations_missed": 2,
        "false_breakers": 0,
        "weak_prior_active_authority_leaks": 1,
        "source_prior_laundering_events": 0,
        "capital_authority_events": 0,
    },
    "T1_TRANSFERABILITY_GATE_ONLY": {
        "unsafe_prior_applications": 0,
        "correct_structural_blocks": 3,
        "eligible_prior_maintains": 1,
        "eligible_prior_violations_detected": 0,
        "eligible_prior_violations_missed": 2,
        "false_breakers": 0,
        "weak_prior_active_authority_leaks": 0,
        "source_prior_laundering_events": 0,
        "capital_authority_events": 0,
    },
    "T2_H3_FULL": {
        "unsafe_prior_applications": 0,
        "correct_structural_blocks": 3,
        "eligible_prior_maintains": 1,
        "eligible_prior_violations_detected": 2,
        "eligible_prior_violations_missed": 0,
        "false_breakers": 0,
        "weak_prior_active_authority_leaks": 0,
        "source_prior_laundering_events": 0,
        "capital_authority_events": 0,
    },
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"YMA55-H4.3 qualification FAIL: {message}")


def main() -> None:
    manifest = load_json(H43 / "blind_manifest.json")
    settlement = load_json(H43 / "post_resolution_settlement.json")

    require(manifest.get("program") == "YMA55-H4.3", "manifest program mismatch")
    require(manifest.get("pair_ids") == ["TP-01", "TP-02", "TP-03", "TP-04", "TP-05", "TP-06"], "pair registry drift")
    require(manifest.get("same_pair_across_variants") is True, "same-pair invariant lost")
    require(manifest.get("structural_evidence_authority") == "CANDIDATE_DERIVED_FROM_H4_H41", "structural evidence authority drift")
    require(manifest.get("historical_gold_admission") is False, "manifest cannot admit Historical Gold")
    require(manifest.get("capital_authority") is False, "manifest cannot grant capital authority")

    structural_packets = [load_json(H43 / rel) for rel in manifest["structural_files"]]
    observation_packets = [load_json(H43 / rel) for rel in manifest["observation_files"]]
    settlements = settlement["pairs"]

    require(len(structural_packets) == 6, "expected exactly six structural packets")
    require(len(observation_packets) == 6, "expected exactly six observation packets")
    require(len(settlements) == 6, "expected exactly six settlements")

    matrix = run_h43_matrix(structural_packets, observation_packets, settlements)

    require(matrix["pair_count"] == 6, "matrix pair count drift")
    require(tuple(matrix["variants"]) == TRANSFER_VARIANTS, "variant registry drift")
    require(matrix["same_pair_same_structural_evidence"] is True, "same-pair evidence invariant lost")
    require(matrix["structural_evidence_authority"] == "CANDIDATE_DERIVED_FROM_H4_H41", "matrix evidence authority drift")
    require(matrix["historical_gold_admission"] is False, "matrix cannot admit Historical Gold")
    require(matrix["capital_authority"] is False, "matrix cannot grant capital authority")
    require(matrix["out_of_sample_claim"] == "NOT_ESTABLISHED", "out-of-sample claim overreach")
    require(matrix["exact_old_yma55_replication"] == "NOT_CLAIMED", "old-YMA55 replication overclaim")

    forbidden_metric_fragments = {"win_rate", "probability", "position_size", "trade_action"}
    for variant in TRANSFER_VARIANTS:
        metrics = matrix["metrics"][variant]
        require(not (forbidden_metric_fragments & set(metrics)), f"forbidden pseudo-precision/capital metric in {variant}")
        require(metrics["source_prior_laundering_events"] == 0, f"source prior laundering detected in {variant}")
        require(metrics["capital_authority_events"] == 0, f"capital authority leak detected in {variant}")
        require(metrics["transferability_settlement_mismatches"] == 0, f"transferability settlement mismatch in {variant}")
        for key, expected in EXPECTED_METRICS[variant].items():
            require(metrics[key] == expected, f"{variant}.{key} drift: expected {expected}, got {metrics[key]}")
        print(
            f"{variant} "
            f"unsafe_prior_applications={metrics['unsafe_prior_applications']} "
            f"correct_structural_blocks={metrics['correct_structural_blocks']} "
            f"eligible_prior_maintains={metrics['eligible_prior_maintains']} "
            f"eligible_prior_violations_detected={metrics['eligible_prior_violations_detected']} "
            f"eligible_prior_violations_missed={metrics['eligible_prior_violations_missed']} "
            f"false_breakers={metrics['false_breakers']} "
            f"weak_prior_active_authority_leaks={metrics['weak_prior_active_authority_leaks']} "
            f"source_prior_laundering_events={metrics['source_prior_laundering_events']} "
            f"capital_authority_events={metrics['capital_authority_events']}"
        )

    state = load_json(STATE_PATH)
    require(state.get("program") == "YMA55-H4.3", "state program mismatch")
    require(state.get("status") == "machine_qualified_paired_transfer_challenge_candidate", "state status drift")
    require(state.get("human_acceptance") is False, "machine qualification cannot imply Human Acceptance")
    require(state.get("recommended_acceptance_token") == "ACCEPT_YMA55_H4_3_TRANSFERABILITY_PRIOR_VIOLATION_PAIRED_CHALLENGE", "acceptance token drift")
    for variant in TRANSFER_VARIANTS:
        state_metrics = state["machine_results"][variant]
        for key, expected in EXPECTED_METRICS[variant].items():
            require(state_metrics.get(key) == expected, f"state result drift: {variant}.{key}")
    require(all(value is False for value in state["authority_freeze"].values()), "state contains positive authority")
    require(state["kernel_closure_settlement"]["yma55_2_1_theory_building"] == "RECOMMEND_FREEZE_AFTER_H4_3_HUMAN_ACCEPTANCE", "theory-freeze boundary drift")
    require(state["kernel_closure_settlement"]["no_h4_4_theory_extension_recommended"] is True, "unexpected H4.4 theory extension")

    report = REPORT_PATH.read_text(encoding="utf-8")
    require("unsafe_prior_applications: 3 → 0" in report, "report omits structural-gate result")
    require("eligible_prior_violations_detected: 0 → 2" in report, "report omits prior-violation result")
    require("out-of-sample return forecasting superiority" in report, "report missing non-overclaim boundary")
    require("Phase 2 execution authority" in report, "report missing successor-authority boundary")

    review = REVIEW_PATH.read_text(encoding="utf-8")
    require(review.count("- [ ]") == 24, "Human Review Card must contain exactly 24 unchecked gates")
    require("24/24 PASS" in review, "Human Review threshold drift")
    require("ACCEPT_YMA55_H4_3_TRANSFERABILITY_PRIOR_VIOLATION_PAIRED_CHALLENGE" in review, "Human Review token drift")

    transition = TRANSITION_PATH.read_text(encoding="utf-8")
    require("transition_candidate_pending_h4_3_human_acceptance" in transition, "transition status drift")
    require("DEFAULT_THEORY_EXPANSION = FROZEN" in transition, "theory-freeze rule missing")
    require("YMA55-EH0｜Evidence Authority Hardening" in transition, "EH0 transition missing")
    require("YMA55-SR0｜Current-World Shadow Runtime" in transition, "SR0 transition missing")
    require("YMA55-RS0｜Reality Settlement & Prior Update" in transition, "RS0 transition missing")
    require("Phase-2 execution authority:** none" in transition, "Phase-2 execution authority must remain none")

    print("historical_gold_admission=0")
    print("capital_authority=0")
    print("out_of_sample_claim=NOT_ESTABLISHED")
    print("exact_old_yma55_replication=NOT_CLAIMED")
    print("phase_2_execution_authority=0")
    print("YMA55-H4.3 paired transfer challenge qualification: PASS")


if __name__ == "__main__":
    main()
