import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "config/yios_g1/gold_g3_shadow_action.v1.json"
PASSPORT = ROOT / "config/yios_g1/gold_g3_shadow_position_passport.v1.json"
LEARNING = ROOT / "docs/architecture/yios_g1/YIOS-G1-G3-LEARNING-RECEIPT-v1.0.json"


def validate_yios_g1_gold_shadow_action():
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    passport = json.loads(PASSPORT.read_text(encoding="utf-8"))
    learning = json.loads(LEARNING.read_text(encoding="utf-8"))

    assert bundle["research_settlement"]["primary_settlement"] == "INDETERMINATE"
    assert bundle["capital_admission"]["decision"] == "deny"
    assert bundle["capital_admission"]["risk_budget"] == {"max_notional": 0, "max_loss": 0}
    assert bundle["execution_intent"]["quantity_delta"] == 0
    assert bundle["action_contract"]["execution_mode"] == "shadow"
    assert bundle["action_contract"]["scope"]["max_notional"] == 0

    events = {event["event_type"] for event in bundle["execution_events"]}
    assert "OrderSubmitted" not in events
    assert "OrderAccepted" not in events
    assert "PartialFillReceived" not in events
    assert "FillReceived" not in events
    assert "ExecutionFailureObserved" in events
    assert bundle["execution_settlement"]["status"] == "FAIL_CLOSED"

    assert passport["authority"]["portfolio_weight_authority"] is False
    assert passport["authority"]["position_sizing_authority"] is False
    assert passport["authority"]["trade_execution_authority"] is False
    assert passport["authority"]["live_execution_authority"] is False

    assert learning["learning_outcome"] == "DENIAL_IS_VALID_EXECUTION_OUTCOME"
    assert learning["authority_changes"]["capital_authority_granted"] is False
    assert learning["authority_changes"]["execution_authority_granted"] is False
    assert learning["authority_changes"]["real_capital_authority_granted"] is False

    return True


if __name__ == "__main__":
    validate_yios_g1_gold_shadow_action()
    print("YIOS_G1_GOLD_SHADOW_ACTION_CONTRACT_VALID")
