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


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    state = load(ARCH / "r2_3" / "R2-3-STATE.json")
    assert state["status"] in {"candidate_started", "candidate_ready_for_human_review"}
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
    assert state["r3a_authority"] == "paused_until_r2_3_merge"

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

    v = new[V_NEW]
    assert v["name"] == "Price-Implied Expectations"
    assert "ALG-V-REVERSEDCF-IMPLIED-EXPECTATIONS" in v["algorithm_ids"]
    assert "Reverse DCF may be one algorithm" in v["output_contract"]
    assert v["maturity_state"] == "specified"

    s = new[S_NEW]
    assert s["name"] == "Growth-Optimal Risk Budget under Uncertainty"
    assert "ALG-S-KELLY-ROBUST-FRACTIONAL" in s["algorithm_ids"]
    assert "no recommended weight" in s["output_contract"]
    assert s["maturity_state"] == "specified"

    smap = load(ARCH / "r2_3" / "R2-3-SUCCESSOR-MAP-v0.1.json")
    assert smap["historical_gold_count"] == 12
    assert smap["effective_vnext_gold_count_after_acceptance"] == 12
    assert smap["other_r2_gold_identities_mutated"] is False
    pairs = {(x["predecessor_capability_id"], x["successor_capability_id"]) for x in smap["successions"]}
    assert pairs == {(V_OLD, V_NEW), (S_OLD, S_NEW)}
    assert all(x["predecessor_mutated"] is False for x in smap["successions"])
    assert all(x["predecessor_deleted"] is False for x in smap["successions"])
    assert smap["runtime_binding_authorized"] is False
    assert smap["benchmark_result_implied"] is False

    r22 = load(ARCH / "r2_2" / "R2-2-STATE.json")
    assert r22["status"] == "accepted_merged"
    assert r22["merge_commit"] == "3bccf723c301f77364c198b9a7b1282c340f5534"

    canon = load(ARCH / "CANON-STATUS.json")
    assert canon["stages"]["R2_2"]["status"] == "accepted_merged"
    assert canon["stages"]["R2_3"]["status"] == state["status"]
    assert canon["r2_3_successor_candidates"]["effective_vnext_gold_count_after_acceptance"] == 12
    assert canon["r2_3_successor_candidates"]["V"]["successor"] == V_NEW
    assert canon["r2_3_successor_candidates"]["S"]["successor"] == S_NEW
    assert canon["r2_3_successor_candidates"]["other_r2_gold_identities_mutated"] is False
    assert canon["stages"]["R3A"]["status"] == "paused_not_started"
    assert canon["next_gate"] == state["next_gate"]

    if state["status"] == "candidate_started":
        assert state["machine_qualification"] is None
        assert state["next_gate"] == "R2_3_MACHINE_QUALIFICATION"
    else:
        q = state["machine_qualification"]
        assert q["conclusion"] == "success"
        assert q["contracts"] == "success"
        assert q["governance"] == "success"
        assert state["next_gate"] == "R2_3_HUMAN_REVIEW"

    print("R2.3 Runtime Blocker Closure validation: PASS")


if __name__ == "__main__":
    main()
