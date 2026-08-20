#!/usr/bin/env python3
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs" / "architecture"
REG = ROOT / "registry" / "capabilities"
SCHEMA = ROOT / "packages" / "contracts" / "schemas" / "research-capability.schema.json"

V_OLD = "CAP-V-001-REVERSE-DCF-EXPECTATIONS"
V_NEW = "CAP-V-002-PRICE-IMPLIED-EXPECTATIONS"
S_OLD = "CAP-S-002-ROBUST-FRACTIONAL-KELLY"
S_NEW = "CAP-S-003-GROWTH-OPTIMAL-RISK-BUDGET-UNDER-UNCERTAINTY"
ACCEPT_TOKEN = "ACCEPT_R2_3_RUNTIME_BLOCKER_CLOSURE"
MERGE_TOKEN = "AUTHORIZE_R2_3_MERGE"
MERGE_COMMIT = "418f06200cde16173743454d506ee946bbc572fc"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    state = load(ARCH / "r2_3" / "R2-3-STATE.json")
    assert state["status"] in {
        "candidate_started",
        "candidate_ready_for_human_review",
        "human_accepted_ready_for_merge",
        "accepted_merged",
    }
    assert state["base_main_commit"] == "3bccf723c301f77364c198b9a7b1282c340f5534"
    assert state["authorized_scope"] == [
        "post_merge_status_receipt_closure",
        "v_capability_successor",
        "s_capability_successor",
    ]
    assert all(value is False for value in state["scope_guard"].values())
    assert state["effective_gold_count_after_acceptance"] == 12
    assert state["retained_r2_gold_identities"] == 10
    assert state["successor_candidate_count"] == 2

    historical = load(REG / "r2-pnxs-gold-v0.1.json")
    assert historical["entry_count"] == 12
    old = {obj["capability_id"]: obj for obj in historical["objects"]}
    assert V_OLD in old and S_OLD in old
    assert old[V_OLD]["name"] == "Reverse DCF Expectations"
    assert old[S_OLD]["name"] == "Robust Fractional Kelly"

    successors = load(REG / "r2-3-vnext-successors-v0.1.json")
    assert successors["entry_count"] == 2
    schema = load(SCHEMA)
    validator = Draft202012Validator(schema)
    new = {}
    for obj in successors["objects"]:
        validator.validate(obj)
        new[obj["capability_id"]] = obj
    assert set(new) == {V_NEW, S_NEW}
    assert "ALG-V-REVERSEDCF-IMPLIED-EXPECTATIONS" in new[V_NEW]["algorithm_ids"]
    assert "ALG-S-KELLY-ROBUST-FRACTIONAL" in new[S_NEW]["algorithm_ids"]

    smap = load(ARCH / "r2_3" / "R2-3-SUCCESSOR-MAP-v0.1.json")
    assert smap["historical_gold_count"] == 12
    assert smap["effective_vnext_gold_count_after_acceptance"] == 12
    assert smap["other_r2_gold_identities_mutated"] is False
    assert smap["runtime_binding_authorized"] is False
    assert smap["benchmark_result_implied"] is False

    r22 = load(ARCH / "r2_2" / "R2-2-STATE.json")
    assert r22["status"] == "accepted_merged"

    canon = load(ARCH / "CANON-STATUS.json")
    assert canon["stages"]["R2_3"]["status"] == state["status"]
    assert canon["r2_3_successor_candidates"]["effective_vnext_gold_count_after_acceptance"] == 12
    assert canon["r2_3_successor_candidates"]["V"]["successor"] == V_NEW
    assert canon["r2_3_successor_candidates"]["S"]["successor"] == S_NEW

    if state["status"] in {"human_accepted_ready_for_merge", "accepted_merged"}:
        receipt = load(ARCH / "r2_3" / "R2-3-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json")
        assert receipt["decision"] == ACCEPT_TOKEN
        assert receipt["pr_number"] == 22
        assert receipt["reviewed_ci"]["run_number"] == 102
        assert state["human_gate_decision"] == ACCEPT_TOKEN

    if state["status"] == "accepted_merged":
        merge_receipt = load(ARCH / "r2_3" / "R2-3-MERGE-RECEIPT-v0.1.json")
        assert merge_receipt["stage"] == "R2_3_RUNTIME_BLOCKER_CLOSURE"
        assert merge_receipt["pr_number"] == 22
        assert merge_receipt["merge_authorization"] == MERGE_TOKEN
        assert merge_receipt["merge_method"] == "squash"
        assert merge_receipt["merge_commit_sha"] == MERGE_COMMIT
        assert merge_receipt["post_acceptance_ci"]["run_number"] == 118
        assert merge_receipt["post_acceptance_ci"]["conclusion"] == "success"
        assert state["merge_commit"] == MERGE_COMMIT
        assert state["merge_receipt"] == "docs/architecture/r2_3/R2-3-MERGE-RECEIPT-v0.1.json"
        assert canon["r2_3_merge_fact"]["merge_commit"] == MERGE_COMMIT

    print("R2.3 Runtime Blocker Closure validation: PASS")


if __name__ == "__main__":
    main()
