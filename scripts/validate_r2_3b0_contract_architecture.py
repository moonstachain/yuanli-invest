#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs" / "architecture"
B0 = ARCH / "r2_3b0"
R23A = ARCH / "r2_3a"

FREEZE = B0 / "R2-3B0-CAPABILITY-CONTRACT-ARCHITECTURE-FREEZE-v0.1.md"
SCHEMA = B0 / "R2-3B0-CONTRACT-SCHEMA-v0.1.json"
PROFILES = B0 / "R2-3B0-P0-CONTRACT-PROFILES-v0.1.json"
STATE = B0 / "R2-3B0-STATE.json"
ACCEPT_RECEIPT = B0 / "R2-3B0-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
MERGE_RECEIPT = B0 / "R2-3B0-MERGE-RECEIPT-v0.1.json"
STATUS = ARCH / "CANON-STATUS.json"
UPSTREAM_STATE = R23A / "R2-3A-STATE.json"

STAGE = "R2_3B0_CAPABILITY_CONTRACT_ARCHITECTURE_FREEZE"
HUMAN_TOKEN = "ACCEPT_R2_3B0_CAPABILITY_CONTRACT_ARCHITECTURE_FREEZE"
P0 = ["CAP-R-01", "CAP-V-01", "CAP-XS-01"]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    for path in [FREEZE, SCHEMA, PROFILES, STATE, ACCEPT_RECEIPT, MERGE_RECEIPT, STATUS, UPSTREAM_STATE]:
        assert path.exists(), path

    upstream = load(UPSTREAM_STATE)
    assert upstream["status"] == "accepted_merged"
    assert upstream["merge_commit"] == "ef3f470f7ef0ceb2b58f392d4a2bd5a5c4c691bd"

    schema = load(SCHEMA)
    assert len(schema["required_blocks"]) == 11
    assert schema["evidence"]["law"] == "Claim Authority <= Evidence Authority"
    assert schema["evidence"]["point_in_time_required"] is True
    assert schema["input"]["provider_independent_identity"] is True
    assert schema["output"]["canonical_root"] == "ResearchState"
    assert schema["output"]["scalar_master_score_prohibited"] is True
    assert schema["runtime_receipt_governance"]["research_pass_implies_capital_pass"] is False
    assert schema["runtime_receipt_governance"]["execution_authority"] == "none"

    profiles = load(PROFILES)
    assert [x["capability_id"] for x in profiles["profiles"]] == P0
    by_id = {x["capability_id"]: x for x in profiles["profiles"]}
    assert by_id["CAP-R-01"]["semantic_parent"] == "P.capital"
    assert by_id["CAP-V-01"]["state_type"] == "PriceImpliedExpectationState"
    assert by_id["CAP-XS-01"]["asset_implementations"]["equity"] == "value_control_point"
    assert profiles["implementation_authority"] == "none"
    assert profiles["promotion_authority"] == "none"
    assert profiles["execution_authority"] == "none"

    acceptance = load(ACCEPT_RECEIPT)
    assert acceptance["stage"] == STAGE
    assert acceptance["decision"] == HUMAN_TOKEN
    assert acceptance["pr_number"] == 24
    assert acceptance["reviewed_ci"]["run_number"] == 137
    assert acceptance["merge_authority"] == "not_implied_by_acceptance"

    merge = load(MERGE_RECEIPT)
    assert merge["stage"] == STAGE
    assert merge["human_acceptance"] == HUMAN_TOKEN
    assert merge["merge_authorization"] == "AUTHORIZE_R2_3B0_MERGE"
    assert merge["pre_merge_head_sha"] == "cd91977b994971fbb56b48202c96c652394c2ec4"
    assert merge["pre_merge_ci"]["run_number"] == 144
    assert merge["merge_method"] == "squash"
    assert merge["merge_commit_sha"] == "cb5ffd0f2e8e377d82c12d716e995c7b5b328e01"

    state = load(STATE)
    assert state["stage"] == STAGE
    assert state["status"] == "accepted_merged"
    assert state["merge_authority"] == "AUTHORIZE_R2_3B0_MERGE"
    assert state["merge_commit"] == merge["merge_commit_sha"]
    assert state["merge_receipt"] == "docs/architecture/r2_3b0/R2-3B0-MERGE-RECEIPT-v0.1.json"
    assert state["p0_capabilities"] == P0
    assert state["contract_architecture"]["required_blocks"] == 11
    assert state["constitutional_invariants"]["scalar_master_score_prohibited"] is True
    assert state["constitutional_invariants"]["research_pass_implies_capital_pass"] is False
    assert state["next_gate"] == "R2_3B1_SPECIFICATION"

    status = load(STATUS)
    assert status["stages"]["R2_3B0"]["status"] == "accepted_merged"
    assert status["stages"]["R2_3B0"]["merge_commit"] == merge["merge_commit_sha"]
    assert status["r2_3b0_merge_fact"]["merge_authorization"] == "AUTHORIZE_R2_3B0_MERGE"
    assert status["r2_3b0_merge_fact"]["pre_merge_ci_run"] == 144
    assert status["r2_3b0_contract_architecture"]["p0_capabilities"] == P0

    corpus = FREEZE.read_text(encoding="utf-8")
    for phrase in ["target price is canonical", "recommended portfolio weight is authorized", "live execution is authorized"]:
        assert phrase.lower() not in corpus.lower()
    assert re.search(r"(?:force|pnx|macro)\s*(?:score|评分)\s*[:=]\s*\d", corpus, re.I) is None

    print("R2.3-B0 merged capability contract architecture validation: PASS")


if __name__ == "__main__":
    main()
