from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_runtime.yma55.benchmark import BENCHMARK_VARIANTS, run_benchmark_matrix

H41 = ROOT / "fixtures" / "replay" / "yma55_h4_1"
STATE_PATH = ROOT / "docs" / "architecture" / "yma55" / "YMA55-H4.2-STATE.json"
REPORT_PATH = ROOT / "docs" / "architecture" / "yma55" / "YMA55-H4.2-SAME-CASE-BASELINE-ABLATION-REPORT-v0.1.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"YMA55-H4.2 benchmark FAIL: {message}")


def validate_state_and_report(matrix: dict) -> None:
    state = load(STATE_PATH)
    require(state["program"] == "YMA55-H4.2", "state program mismatch")
    require(
        state["status"] in {
            "qualification_candidate_pending_final_exact_head",
            "machine_qualified_same_case_benchmark_candidate",
        },
        "invalid H4.2 state status",
    )
    design = state["experiment_design"]
    require(design["case_count"] == 12, "state case count mismatch")
    require(design["same_case_same_evidence"] is True, "state must preserve same-case/same-evidence")
    require(design["same_settlement"] is True, "state must preserve same settlement")
    require(design["iid_or_out_of_sample_claim"] is False, "state cannot claim IID/out-of-sample result")
    require(design["exact_old_yma55_replication_claim"] is False, "state cannot claim exact old-YMA55 replication")

    key_map = {
        "fully_hydrated_mechanism_accuracy": "fully_hydrated_mechanism_accuracy",
        "hard_negative_discrimination": "hard_negative_discrimination",
        "matches": "matches",
        "mismatches": "mismatches",
        "abstentions": "evidence_abstentions",
        "partial_case_forced_resolution": "partial_case_forced_resolution",
    }
    for variant in BENCHMARK_VARIANTS:
        state_score = state["benchmark_results"][variant]
        machine_score = matrix["scores"][variant]
        for state_key, machine_key in key_map.items():
            require(
                state_score[state_key] == machine_score[machine_key],
                f"state benchmark truth drift: {variant}/{state_key}",
            )

    settlement = state["epistemic_settlement"]
    require(
        settlement["incremental_superiority_vs_frozen_naive_baselines"]
        == "SUPPORTED_WITHIN_CONSTRUCTED_CHALLENGE_SET",
        "baseline increment conclusion drift",
    )
    require(
        settlement["incremental_superiority_vs_exact_pre_h1_h2_h3_yma55"] == "NOT_ESTABLISHED",
        "cannot claim exact old-YMA55 superiority",
    )
    require(
        settlement["evidence_gate_value"]
        == "SUPPORTED_AS_ABSTENTION_DISCIPLINE_NOT_MECHANISM_ACCURACY",
        "evidence-gate contribution must remain narrow",
    )
    require(
        settlement["h2_individual_contribution"] == "DOMINANT_MEASURED_INCREMENT_WITHIN_CHALLENGE_SET",
        "H2 measured contribution drift",
    )
    require(
        settlement["h3_incremental_contribution"] == "NOT_IDENTIFIABLE_IN_HISTORICAL_ONLY_REPLAY",
        "H3 cannot be manufactured from historical-only benchmark",
    )
    require(settlement["out_of_sample_predictive_superiority"] == "NOT_ESTABLISHED", "no OOS claim")

    for authority, value in state["authority_freeze"].items():
        require(value is False, f"authority must remain false: {authority}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    required_phrases = (
        "does **not** claim exact replication",
        "Evidence gating improves epistemic safety",
        "competing-mechanism adjudication",
        "H3 incremental contribution = NOT_IDENTIFIABLE_IN_HISTORICAL_ONLY_REPLAY",
        "Historical Gold admission",
        "Research PASS != Capital PASS",
    )
    for phrase in required_phrases:
        require(phrase in report, f"report missing required boundary/settlement: {phrase}")


def main() -> None:
    manifest = load(H41 / "blind_manifest.json")
    packets = [load(H41 / rel) for rel in manifest["case_files"]]
    settlements = load(H41 / "post_resolution_unblinding.json")["cases"]
    matrix = run_benchmark_matrix(packets, settlements)

    require(matrix["case_count"] == 12, "same-case matrix must contain 12 cases")
    require(tuple(matrix["variants"]) == BENCHMARK_VARIANTS, "variant registry drift")
    require(matrix["same_case_same_evidence"] is True, "same-case/same-evidence invariant required")
    require(matrix["old_yma55_replication_claim"] == "NOT_CLAIMED", "cannot mislabel B0 as exact old-YMA55 replication")
    require(matrix["h3_incremental_contribution"] == "NOT_IDENTIFIABLE_IN_HISTORICAL_ONLY_REPLAY", "H3 contribution must not be faked")
    require(matrix["scores"]["B3_H1_H2_FULL_RESOLVER"]["fully_hydrated_mechanism_accuracy"] == "10/11", "B3 must reproduce H4.1")
    require(matrix["scores"]["B0_NAIVE_PRIMARY_PRIOR"]["partial_case_forced_resolution"] is True, "naive prior should expose unsafe forced resolution")
    require(matrix["scores"]["B1_EVIDENCE_GATED_PRIMARY"]["partial_case_forced_resolution"] is False, "evidence gate must remove partial-case forcing")
    require(matrix["scores"]["B4_H1_H2_H3_HISTORICAL_ONLY"] == matrix["scores"]["B3_H1_H2_FULL_RESOLVER"], "historical-only set cannot identify H3 incremental effect")
    validate_state_and_report(matrix)

    print("YMA55-H4.2 benchmark: PASS")
    for variant in BENCHMARK_VARIANTS:
        score = matrix["scores"][variant]
        print(
            f"{variant} "
            f"accuracy={score['fully_hydrated_mechanism_accuracy']} "
            f"hard_negative={score['hard_negative_discrimination']} "
            f"matches={score['matches']} mismatches={score['mismatches']} "
            f"abstentions={score['evidence_abstentions']} "
            f"partial_forced={str(score['partial_case_forced_resolution']).lower()}"
        )
    print("H3 incremental contribution=NOT_IDENTIFIABLE_IN_HISTORICAL_ONLY_REPLAY")
    print("old YMA55 exact replication=NOT_CLAIMED")
    print("gold_admission=0 capital_authority=0")


if __name__ == "__main__":
    main()
