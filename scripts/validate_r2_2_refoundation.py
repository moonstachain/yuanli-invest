#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "os-vnext"
ARCH = ROOT / "docs" / "architecture"
SD = ROOT / "packages" / "contracts" / "schemas" / "vnext"
ACCEPTANCE = ARCH / "r2_2" / "R2-2-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
MERGE = ARCH / "r2_2" / "R2-2-MERGE-RECEIPT-v0.1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    constitution = (DOCS / "CONSTITUTION.md").read_text(encoding="utf-8")
    for token in [
        "Lifetime Right-Tail Capture under Survival Constraints",
        "X := (Xs, Xa, Xp)",
        "Claim Authority <= Evidence Authority",
        "ResearchCapability",
    ]:
        assert token in constitution

    state = load(ARCH / "r2_2" / "R2-2-STATE.json")
    assert state["status"] == "accepted_merged"
    assert state["canonical_state"] == "ResearchStateVector"
    assert state["dependency_graph_is_universal_causal_law"] is False
    assert state["human_gate_decision"] == "ACCEPT_R2_2_RESEARCH_INTELLIGENCE_CANON_REFOUNDATION"
    assert state["merge_pr"] == 21
    assert state["merge_commit"] == "3bccf723c301f77364c198b9a7b1282c340f5534"
    assert state["merged_at"] == "2026-08-19T08:48:26Z"
    assert state["merge_receipt"] == "docs/architecture/r2_2/R2-2-MERGE-RECEIPT-v0.1.json"
    assert state["r3a_authority"] == "paused_until_r2_3_merge"
    assert state["next_gate"] == "none_stage_complete"

    acceptance = load(ACCEPTANCE)
    assert acceptance["decision"] == "ACCEPT_R2_2_RESEARCH_INTELLIGENCE_CANON_REFOUNDATION"
    assert acceptance["merge_authority"] == "not_implied_by_acceptance"

    merge = load(MERGE)
    assert merge["pr_number"] == 21
    assert merge["merge_authorization"] == "separate_explicit_user_authorization"
    assert merge["merge_commit_sha"] == state["merge_commit"]
    assert merge["post_acceptance_ci"]["run_number"] == 96
    assert merge["post_acceptance_ci"]["run_id"] == 32231112078
    assert merge["post_acceptance_ci"]["conclusion"] == "success"

    for name in [
        "research-target.schema.json",
        "canonical-observation.schema.json",
        "evidence-claim.schema.json",
        "research-state-vector.schema.json",
        "capability-invocation.schema.json",
        "capability-input-bundle.schema.json",
        "capability-result.schema.json",
        "execution-receipt.schema.json",
        "future-settlement.schema.json",
        "capability-revision.schema.json",
    ]:
        assert (SD / name).exists(), name

    canon = load(ARCH / "CANON-STATUS.json")
    assert canon["stages"]["R2_2"]["status"] == "accepted_merged"
    assert canon["r2_2_merge_fact"]["merge_commit"] == state["merge_commit"]

    print("R2.2 post-merge Research Intelligence Canon validation: PASS")


if __name__ == "__main__":
    main()
