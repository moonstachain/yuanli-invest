import json
import tempfile
from pathlib import Path

import pytest

from scripts import ymq_gold2_learning_live as learning

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "ymq_gold2" / "gold2_learning_live.v0.1.json"


def receipt(day, gold, real_rate, usd, known=None, *, status="LIVE_SHADOW_RECEIPT", claim=None, unknowns=None):
    known = known or day
    out = {
        "status": status,
        "as_of": day,
        "known_as_of_min": known,
        "known_as_of_max": known,
        "provider_receipts": {
            "gold_price": {"metric_code": "S0031645", "latest_date": known, "latest_value": gold},
            "real_rate": {"metric_code": "G1147404", "latest_date": known, "latest_value": real_rate},
            "usd": {"metric_code": "M0000271", "latest_date": known, "latest_value": usd},
        },
        "property_drift_state": "DRIFT_CANDIDATE",
        "expectation_reality_state": "INDETERMINATE",
        "valuation_state": "UNIDENTIFIABLE",
        "research_state": "WATCH",
        "lifecycle_state": "未知",
        "unknowns": list(unknowns or ["policy_path_expectations", "narrative_crowding_if_authoritative"]),
    }
    if claim is not None:
        out["preregistered_directional_claim"] = claim
    return out


def test_contract_keeps_learning_non_authoritative():
    cfg = learning.load_contract(CONTRACT)
    learning.validate_contract(cfg)
    assert cfg["status"] == "HUMAN_AUTHORIZED_RESEARCH_LEARNING_ONLY"
    assert cfg["authority"]["research_learning_authorized"] is True
    for field in (
        "accepted_learning_authorized", "capital_authorized", "sizing_authorized",
        "execution_authorized", "broker_action", "veighna_authorized",
        "asset_promotion_authorized", "canon_promotion_authorized",
    ):
        assert cfg["authority"][field] is False


def test_contract_freezes_attention_thresholds_and_scoring_law():
    cfg = learning.load_contract(CONTRACT)
    assert cfg["attention_thresholds"] == {
        "gold_price_pct_abs": 1.0,
        "real_rate_bps_abs": 10.0,
        "usd_pct_abs": 0.5,
    }
    assert cfg["settlement"]["directional_scoring_requires_preregistered_claim"] is True
    assert cfg["settlement"]["missing_claim_state"] == "NOT_SCORABLE"
    assert cfg["settlement"]["known_as_of_regression"] == "FAIL_CLOSED"


def test_delta_math_attention_and_unknown_resolution():
    cfg = learning.load_contract(CONTRACT)
    prior = receipt("2026-09-16", 4296.15, 3.05, 99.6335, known="2026-09-15")
    current = receipt(
        "2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16",
        unknowns=["policy_path_expectations"],
    )
    delta = learning.build_state_delta(prior, current, cfg)
    assert delta["gold_price_pct"] == pytest.approx(0.7460139, rel=1e-6)
    assert delta["real_rate_bps"] == pytest.approx(1.0)
    assert delta["usd_pct"] == pytest.approx(0.6983597, rel=1e-6)
    assert delta["attention"] == ["usd_pct"]
    assert delta["unknowns_resolved"] == ["narrative_crowding_if_authoritative"]
    assert delta["unknowns_added"] == []
    assert delta["state_transitions"] == {}


def test_known_as_of_regression_fails_closed():
    cfg = learning.load_contract(CONTRACT)
    prior = receipt("2026-09-16", 4296.15, 3.05, 99.63, known="2026-09-15")
    current = receipt("2026-09-17", 4300.0, 3.05, 99.7, known="2026-09-14")
    with pytest.raises(ValueError, match="known_as_of regression"):
        learning.build_state_delta(prior, current, cfg)


def test_settlement_without_preregistered_claim_is_not_scorable():
    cfg = learning.load_contract(CONTRACT)
    prior = receipt("2026-09-16", 4296.15, 3.05, 99.63, known="2026-09-15")
    current = receipt("2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16")
    delta = learning.build_state_delta(prior, current, cfg)
    settlement = learning.build_settlement(prior, current, delta, cfg)
    assert settlement["pit_integrity"] == "PASS"
    assert settlement["directional_claim_score"] == "NOT_SCORABLE"
    assert settlement["regime_detection_lag"] == "PENDING"
    assert settlement["decision_regret"] == "NOT_APPLICABLE"


def test_learning_candidate_is_non_authoritative_and_hashed():
    cfg = learning.load_contract(CONTRACT)
    prior = receipt("2026-09-16", 4296.15, 3.05, 99.63, known="2026-09-15")
    current = receipt("2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16")
    candidate = learning.build_learning_candidate(prior, current, cfg)
    assert candidate["status"] == "LEARNING_CANDIDATE_ONLY"
    assert candidate["accepted_learning"] is False
    assert candidate["authority"]["canon_promotion_authorized"] is False
    assert len(candidate["source_receipts"]["prior_sha256"]) == 64
    assert len(candidate["source_receipts"]["current_sha256"]) == 64
    assert 0 <= candidate["unknown_rate"] <= 1


def test_same_day_receipts_are_skipped_for_daily_learning():
    cfg = learning.load_contract(CONTRACT)
    prior = receipt("2026-09-17", 4328.1, 3.06, 100.3, known="2026-09-16")
    current = receipt("2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16")
    result = learning.build_learning_candidate(prior, current, cfg)
    assert result["status"] == "DUPLICATE_DAY_SKIPPED"


def test_find_previous_daily_receipt_ignores_same_day_and_failures():
    current = receipt("2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16")
    same_day = receipt("2026-09-17", 4320.0, 3.06, 100.2, known="2026-09-16")
    previous = receipt("2026-09-16", 4296.15, 3.05, 99.6335, known="2026-09-15")
    failed = receipt("2026-09-15", 0, 0, 0, status="PROVIDER_FAIL_CLOSED")
    assert learning.find_previous_daily_receipt(current, [failed, same_day, previous]) == previous


def test_private_write_creates_learning_tree_only():
    cfg = learning.load_contract(CONTRACT)
    prior = receipt("2026-09-16", 4296.15, 3.05, 99.63, known="2026-09-15")
    current = receipt("2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16")
    candidate = learning.build_learning_candidate(prior, current, cfg)
    with tempfile.TemporaryDirectory() as td:
        target = learning.write_learning_candidate(candidate, Path(td))
        assert target.exists()
        assert Path(td, "learning", "latest-learning.json").exists()
        assert "learning" in target.parts
