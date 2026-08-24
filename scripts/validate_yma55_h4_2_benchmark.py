from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_runtime.yma55.benchmark import BENCHMARK_VARIANTS, run_benchmark_matrix

H41 = ROOT / "fixtures" / "replay" / "yma55_h4_1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"YMA55-H4.2 benchmark FAIL: {message}")


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
