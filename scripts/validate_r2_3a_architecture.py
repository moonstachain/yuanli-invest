#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "os-vnext"
ARCH_ROOT = ROOT / "docs" / "architecture"
ARCH = ARCH_ROOT / "r2_3a"

FREEZE = ARCH / "R2-3A-ARCHITECTURE-FREEZE-v0.1.md"
CANDIDATES = ARCH / "R2-3A-CAPABILITY-CANDIDATES-v0.1.json"
REVIEW = ARCH / "R2-3A-HUMAN-REVIEW-CARD-v0.1.md"
STATE = ARCH / "R2-3A-STATE.json"
STRESS = ARCH / "R2-3A-CROSS-ASSET-STRESS-CHECK-v0.1.json"
ACCEPT_RECEIPT = ARCH / "R2-3A-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json"
MERGE_RECEIPT = ARCH / "R2-3A-MERGE-RECEIPT-v0.1.json"
STATUS = ARCH_ROOT / "CANON-STATUS.json"
R23_STATE = ARCH_ROOT / "r2_3" / "R2-3-STATE.json"
R23_RECEIPT = ARCH_ROOT / "r2_3" / "R2-3-MERGE-RECEIPT-v0.1.json"

P0 = ["CAP-R-01", "CAP-V-01", "CAP-XS-01"]
P1 = ["CAP-N-01", "CAP-N-02", "CAP-XA-01", "CAP-XP-01", "CAP-S-01"]
SUPPORTING = ["CAP-R-02", "CAP-A-01", "CAP-P-01", "CAP-E-01"]
ALL = P0 + P1 + SUPPORTING
BASE_OS_MODEL = "one_core_three_worlds_three_gates_one_loop"
ACCEPT_TOKEN = "ACCEPT_R2_3A_YUANLI_INVESTMENT_OS_ARCHITECTURE_FREEZE"
MERGE_TOKEN = "AUTHORIZE_R2_3A_MERGE"
EXPECTED_EXTENSIONS = [
    "r_as_machine_decomposition_of_p_capital",
    "L0-L4_cross_asset_authority_ladder",
    "two_stage_asset_router_A0_A1",
    "cross_asset_structural_asymmetry_source",
    "human_navigation_势信极_真价生",
    "research_portfolio_authority_split",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require_tokens(text: str, tokens):
    for token in tokens:
        assert token in text, token


def assert_no_scalar_score_regression(corpus: str):
    patterns = [
        r"(?:综合|composite|force|pnx|macro)\s*(?:score|评分|得分)?\s*[:=]\s*\d+(?:\.\d+)?",
        r"(?:P|N|X|E|V|S|R)\s*[+*/]\s*(?:P|N|X|E|V|S|R)\s*=\s*\d+(?:\.\d+)?",
        r"weighted\s+(?:average|score).{0,40}[:=]\s*\d+(?:\.\d+)?",
    ]
    for pattern in patterns:
        assert re.search(pattern, corpus, flags=re.IGNORECASE) is None, pattern


def main():
    for path in [FREEZE, CANDIDATES, REVIEW, STATE, STRESS, ACCEPT_RECEIPT, STATUS, R23_RECEIPT]:
        assert path.exists(), path

    r23 = load(R23_STATE)
    upstream_receipt = load(R23_RECEIPT)
    assert r23["status"] == "accepted_merged"
    assert r23["merge_commit"] == "418f06200cde16173743454d506ee946bbc572fc"
    assert upstream_receipt["merge_authorization"] == "AUTHORIZE_R2_3_MERGE"
    assert upstream_receipt["merge_commit_sha"] == r23["merge_commit"]
    assert upstream_receipt["post_acceptance_ci"]["run_number"] == 118

    constitution = (DOCS / "CONSTITUTION.md").read_text(encoding="utf-8")
    require_tokens(constitution, [
        "Lifetime Right-Tail Capture under Survival Constraints", BASE_OS_MODEL,
        "势 · 信 · 极｜真 · 价 · 生", "P.capital", "P.asset", "R is not a fourth human world",
        "Structural Asymmetry Source", "Value Control Point is an equity-specialized implementation",
        "X := (Xs, Xa, Xp)", "Claim Authority <= Evidence Authority",
        "Asset form is not pricing model", "Lower-level truth does not imply higher-level authorization",
        "A0 | asset_form", "A1 | pricing_archetype", "Price-Implied Expectations",
        "governance-authority split only", "ResearchCapability",
    ])
    assert "X := (Xs, Xa)" not in constitution

    graph = (DOCS / "RESEARCH-DEPENDENCY-GRAPH.md").read_text(encoding="utf-8")
    require_tokens(graph, [
        "P.capital(R) + P.asset", "R is not a fourth human world",
        "L0-L4 | Cross-Asset Authority Ladder", "A0 | asset_form", "A1 | pricing_archetype",
        "Structural Asymmetry Source", "Value Control Point is therefore an equity implementation",
        "X := (Xs, Xa, Xp)", "research_only / stale",
    ])

    seven = (DOCS / "SEVEN-QUESTIONS.md").read_text(encoding="utf-8")
    require_tokens(seven, ["势 · 信 · 极｜真 · 价 · 生", "不对称从哪里来？", "A0 | asset_form", "A1 | pricing_archetype"])

    freeze = FREEZE.read_text(encoding="utf-8")
    require_tokens(freeze, [
        "candidate_started_cross_asset_hardening", BASE_OS_MODEL, "P.capital", "P.asset",
        "R is not a fourth human world", "Structural Asymmetry Source", "Two-Stage Asset Router",
        "Asset form is not pricing model", "CAP-XS-01 | Structural Asymmetry Source Mapper",
        "Cross-Asset Stress Check", "R2-3A-CROSS-ASSET-STRESS-CHECK-v0.1.json", ACCEPT_TOKEN,
    ])

    stress = load(STRESS)
    assert stress["test_type"] == "architecture_semantic_routing_fixture"
    assert len(stress["cases"]) == 5

    data = load(CANDIDATES)
    assert data["stage"] == "R2.3-A"
    assert data["base_dependency"]["status"] == "accepted_merged"
    assert data["priorities"]["P0"] == P0
    assert data["priorities"]["P1"] == P1
    assert data["priorities"]["supporting"] == SUPPORTING
    ids = [x["id"] for x in data["candidates"]]
    assert ids == ALL and len(set(ids)) == 12
    by_id = {x["id"]: x for x in data["candidates"]}
    assert by_id["CAP-XS-01"]["name"] == "Structural Asymmetry Source Mapper"
    assert by_id["CAP-XS-01"]["asset_implementations"]["equity"] == "value_control_point"
    assert "monetary_asset" in by_id["CAP-A-01"]["asset_forms"]
    assert data["promotion_authority"] == "none"
    assert data["execution_authority"] == "none"

    state = load(STATE)
    assert state["stage"] == "R2_3A_YUANLI_INVESTMENT_OS_ARCHITECTURE_FREEZE"
    assert state["status"] in {"candidate_started", "candidate_ready_for_human_review", "human_accepted_ready_for_merge", "accepted_merged"}
    assert state["base_os_model"] == BASE_OS_MODEL
    assert state["human_navigation"] == "势信极_真价生"
    assert state["architecture_extensions"] == EXPECTED_EXTENSIONS
    assert state["upstream_dependency"]["resolved"] is True
    assert state["constitutional_invariants"]["x_semantics"] == "X := (Xs, Xa, Xp)"
    assert state["constitutional_invariants"]["xs_mother_concept"] == "Structural Asymmetry Source"
    assert state["constitutional_invariants"]["asset_form_is_not_pricing_model"] is True
    assert state["r2_3b_contract_requirements"]["n02_reunderwrite_latency_policy_required"] is True

    status = load(STATUS)
    assert status["os_model"] == BASE_OS_MODEL
    assert status["human_navigation"] == "势信极_真价生"
    assert status["architecture_extensions"]["R"].endswith("not_fourth_human_world")
    assert status["constitutional_invariants"]["r_is_fourth_human_world"] is False
    assert status["constitutional_invariants"]["asset_form_is_not_pricing_model"] is True
    assert status["constitutional_invariants"]["xs_mother_concept"] == "Structural Asymmetry Source"
    assert status["stages"]["R2_3A"]["status"] == state["status"]
    assert status["r2_3a_architecture"]["extensions"] == EXPECTED_EXTENSIONS
    assert status["r2_3a_architecture"]["router"] == state["router"]
    assert status["r2_3a_architecture"]["x_semantics_preserved_across_os_split"] is True

    if state["status"] == "candidate_started":
        assert state["machine_qualification"] is None
        assert state["next_gate"] == "R2_3A_MACHINE_QUALIFICATION"
    elif state["status"] == "candidate_ready_for_human_review":
        q = state["machine_qualification"]
        assert q["conclusion"] == "success"
        assert state["next_gate"] == "R2_3A_HUMAN_REVIEW"
    else:
        acceptance = load(ACCEPT_RECEIPT)
        assert acceptance["decision"] == ACCEPT_TOKEN
        assert acceptance["pr_number"] == 23
        assert acceptance["reviewed_ci"]["run_number"] == 124
        assert acceptance["reviewed_ci"]["conclusion"] == "success"
        assert state["human_gate"]["decision"] == ACCEPT_TOKEN
        assert state["human_gate"]["reviewed_ci_run"] == 124
        assert status["r2_3a_acceptance_fact"]["decision"] == ACCEPT_TOKEN

        if state["status"] == "human_accepted_ready_for_merge":
            assert state["merge_authority"] == "not_implied_by_acceptance"
            assert state["next_gate"] == "R2_3A_MERGE"
        else:
            assert MERGE_RECEIPT.exists()
            merge = load(MERGE_RECEIPT)
            assert merge["merge_authorization"] == MERGE_TOKEN
            assert merge["pre_merge_head_sha"] == "5635db72301218b08323228311c1db9a8a2ab39b"
            assert merge["pre_merge_ci"]["run_number"] == 133
            assert merge["pre_merge_ci"]["conclusion"] == "success"
            assert merge["merge_method"] == "squash"
            assert merge["merge_commit_sha"] == "ef3f470f7ef0ceb2b58f392d4a2bd5a5c4c691bd"
            assert state["merge_authority"] == MERGE_TOKEN
            assert state["merge_receipt"] == "docs/architecture/r2_3a/R2-3A-MERGE-RECEIPT-v0.1.json"
            assert state["merge_commit"] == merge["merge_commit_sha"]
            assert state["next_gate"] == "R2_3B0_CAPABILITY_CONTRACT_ARCHITECTURE_FREEZE"
            assert status["r2_3a_merge_fact"]["merge_commit"] == merge["merge_commit_sha"]
            assert status["r2_3a_merge_fact"]["merge_authorization"] == MERGE_TOKEN

    corpus = "\n".join([constitution, graph, seven, freeze, REVIEW.read_text(encoding="utf-8")])
    assert_no_scalar_score_regression(corpus)
    prohibited = [
        "R is the fourth human world",
        "Value Control Point is the universal ontology of Xs",
        "asset form equals pricing model",
        "target price is canonical",
        "recommended portfolio weights are authorized",
        "narrative break is an automatic sell signal",
    ]
    for phrase in prohibited:
        assert phrase not in corpus, phrase

    print("R2.3-A cross-asset architecture validation: PASS")


if __name__ == "__main__":
    main()
