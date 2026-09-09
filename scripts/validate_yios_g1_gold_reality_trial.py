from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSTITUTION = ROOT / "config" / "yios_g1" / "gold_genesis_case_constitution.v1.json"
STATE = ROOT / "config" / "yios_g1" / "gold_state_t0.v1.json"
RESULT = ROOT / "config" / "yios_g1" / "gold_g1_reality_trial.v1.json"
G0 = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-A0-HUMAN-ACCEPTANCE-RECEIPT-v1.0.json"
G1 = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G1-REALITY-TRIAL-AUTHORIZATION-RECEIPT-v1.0.json"
EVIDENCE = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G1-GOLD-EVIDENCE-PACK-T0-v1.md"
RESULT_DOC = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G1-REALITY-TRIAL-RESULT-v1.md"
REVIEW = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G1-HUMAN-REVIEW-CARD-v1.md"

T0 = "2024-01-31T23:59:59-05:00"
CLAIM = "GOLD_EARLY_MONETARY_REGIME_REPRICING"


def load_json(path: Path):
    if not path.exists():
        raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(actual: float, expected: float, tol: float = 1e-9) -> bool:
    return abs(float(actual) - expected) <= tol


def validate_yios_g1_gold_reality_trial() -> None:
    c = load_json(CONSTITUTION)
    s = load_json(STATE)
    r = load_json(RESULT)
    g0 = load_json(G0)
    g1 = load_json(G1)

    # Governance and exact Constitution freeze.
    require(c["two_clock_law"]["historical_t0"] == T0, "historical T0 drifted")
    require(c["two_clock_law"]["historical_evidence_rule"] == "known_as_of <= T0", "PIT law drifted")
    require(c["two_clock_law"]["invariant"] == "GOVERNANCE_KNOWLEDGE_2026 != HISTORICAL_KNOWLEDGE_AT_T0", "Two-Clock law drifted")
    require(c["primary_claim"]["claim_id"] == CLAIM, "primary claim drifted")
    require(c["primary_settlement_law"]["price_up_alone_can_pass"] is False, "price-up-only proof was enabled")
    require(g0["decision"] == "ACCEPT_GOLD_G1_CASE_CONSTITUTION", "G0 Human acceptance missing")
    require(g1["decision"] == "AUTHORIZE_GOLD_G1_REALITY_TRIAL", "G1 authorization missing")
    require(g1["authority_separation"] == "RESEARCH_TRIAL_AUTHORITY_ONLY", "G1 authority escalated")

    # T0 state must be strictly historical and self-contained.
    require(s["known_as_of"] == T0, "GoldState@T0 timestamp drifted")
    require(s["future_leakage_count"] == 0, "future leakage detected")
    state_text = json.dumps(s, sort_keys=True)
    require("2025" not in state_text and "2026" not in state_text, "post-T0 calendar information entered GoldState@T0")
    require(s["authority"] == "RESEARCH_STATE_ONLY", "T0 state authority escalated")
    require(s["demand_state"]["official_demand"]["decisive_h1_threshold_available"] is False, "H1 threshold falsely declared available at T0")
    require(bool(s["unknown_state"]["decisive_unknowns"]), "decisive unknown omitted")

    # Trial result and fail-closed scientific settlement.
    require(r["historical_t0"] == T0, "result T0 drifted")
    require(r["primary_claim"] == CLAIM, "result claim drifted")
    require(r["pit_integrity"]["status"] == "PASS", "PIT integrity did not pass")
    require(r["pit_integrity"]["future_leakage_count"] == 0, "result records future leakage")
    require(r["pit_integrity"]["b2_b3_used_as_t0_evidence"] is False, "B2/B3 retrojection detected")

    h = r["hypothesis_results"]
    require(h["H1_OFFICIAL_DEMAND_STRUCTURAL"]["status"] == "INDETERMINATE", "H1 must fail closed to INDETERMINATE")
    require(h["H1_OFFICIAL_DEMAND_STRUCTURAL"]["threshold_value"] is None, "mixed-vintage H1 threshold was manufactured")
    h1_reason = h["H1_OFFICIAL_DEMAND_STRUCTURAL"]["reason"].lower()
    require("t0-vintage" in h1_reason and "mixing" in h1_reason and "forbidden" in h1_reason, "H1 evidence-authority gap not explicit")
    require(h["H2_TRADITIONAL_MACRO_DECOUPLING"]["status"] == "SUPPORTED", "H2 settlement mismatch")
    require(h["H3_PRICE_CONFIRMATION"]["status"] == "SUPPORTED", "H3 settlement mismatch")
    require(h["H4_NARRATIVE_PRIVATE_DEMAND_BROADENING"]["decisive"] is False, "H4 became decisive")
    require(r["primary_research_settlement_candidate"] == "INDETERMINATE", "primary claim must remain INDETERMINATE")
    require(r["authority_state"] == "RESEARCH_SETTLEMENT_CANDIDATE_ONLY", "settlement authority escalated")
    require(r["human_settlement_required"] == "ACCEPT_GOLD_G1_RESEARCH_SETTLEMENT", "G2 gate mismatch")

    # Corrected post-T0 windows: February 2024 onward, never including January as a forward return.
    h2_expected = {
        "T+3M": 13.159744628679,
        "T+6M": 15.7785512393508,
        "T+12M": 27.5074997964836,
        "T+24M": 75.6115226190574,
    }
    h3_expected = {
        "T+3M": 13.6293062427252,
        "T+6M": 16.4630758978954,
        "T+12M": 28.6944337265241,
        "T+24M": 84.8771700005504,
    }
    for window, expected in h2_expected.items():
        require(close(h["H2_TRADITIONAL_MACRO_DECOUPLING"]["windows"][window]["cumulative_b0_residual_log_pct"], expected), f"H2 {window} drift")
    for window, expected in h3_expected.items():
        require(close(h["H3_PRICE_CONFIRMATION"]["windows"][window]["cumulative_log_gold_return_pct"], expected), f"H3 {window} drift")

    baseline = r["baseline_forward_readback"]
    require(baseline["months"] == 24, "forward window must contain exactly 24 post-T0 months")
    require(close(baseline["B0_TRADITIONAL_MACRO"]["rmse"], 4.59739791982403), "B0 RMSE drift")
    require(close(baseline["B0_TRADITIONAL_MACRO"]["mae"], 3.39853402948101), "B0 MAE drift")
    require(close(baseline["B1_NULL_PRICE_ONLY"]["rmse"], 4.67959381509622), "B1 RMSE drift")
    require(close(baseline["B1_NULL_PRICE_ONLY"]["mae"], 3.617070681837), "B1 MAE drift")

    # Hard negatives and authority separation.
    negatives = r["hard_negative_results"]
    require(negatives["PRICE_UP_ONLY"] == "REJECTED_AS_SUFFICIENT_PROOF", "price-up hard negative failed")
    require(negatives["POST_T0_LEAKAGE"] == "PASS_ZERO_LEAKAGE", "post-T0 leakage hard negative failed")
    require(negatives["B2_B3_RETROJECTION"] == "PASS_NOT_USED_IN_T0_STATE", "B2/B3 retrojection hard negative failed")
    require(negatives["RESEARCH_TO_CAPITAL_AUTO_PROMOTION"] == "PASS_BLOCKED", "capital auto-promotion not blocked")
    require(negatives["RESEARCH_TO_EXECUTION_AUTO_PROMOTION"] == "PASS_BLOCKED", "execution auto-promotion not blocked")
    for key, value in r["non_authorizations"].items():
        require(value is False, f"unauthorized authority enabled: {key}")

    # Human-readable artifacts must retain the decisive unknown and next gate.
    for path in (EVIDENCE, RESULT_DOC, REVIEW):
        require(path.exists(), f"missing human artifact: {path.relative_to(ROOT)}")
    evidence_text = EVIDENCE.read_text(encoding="utf-8")
    result_text = RESULT_DOC.read_text(encoding="utf-8")
    review_text = REVIEW.read_text(encoding="utf-8")
    require("H1_OFFICIAL_DEMAND_STRUCTURAL = INDETERMINATE" in evidence_text, "H1 gap missing from Evidence Pack")
    require("PRIMARY SCIENTIFIC SETTLEMENT CANDIDATE: INDETERMINATE" in result_text, "primary fail-closed result missing")
    require("ACCEPT_GOLD_G1_RESEARCH_SETTLEMENT" in review_text, "Human G2 token missing")
    require("AUTHORIZE_GOLD_G1_SHADOW_ACTION" in review_text, "separate G3 gate missing")


if __name__ == "__main__":
    validate_yios_g1_gold_reality_trial()
    print("YIOS_G1_GOLD_REALITY_TRIAL_CONTRACT_VALID")
