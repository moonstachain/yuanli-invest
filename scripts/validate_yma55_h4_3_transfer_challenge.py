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

    print("historical_gold_admission=0")
    print("capital_authority=0")
    print("out_of_sample_claim=NOT_ESTABLISHED")
    print("exact_old_yma55_replication=NOT_CLAIMED")
    print("YMA55-H4.3 paired transfer challenge qualification checkpoint: PASS")


if __name__ == "__main__":
    main()
