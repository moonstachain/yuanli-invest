#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs" / "architecture" / "r2_3a" / "R2-3A-CROSS-ASSET-STRESS-CHECK-v0.1.json"

EXPECTED_TARGETS = ["NVIDIA", "UST30Y", "COPPER", "GOLD", "USDJPY"]
EXPECTED_FORMS = {
    "NVIDIA": "equity",
    "UST30Y": "sovereign_rates",
    "COPPER": "commodity",
    "GOLD": "monetary_asset",
    "USDJPY": "FX",
}
EXPECTED_XS = {
    "NVIDIA": "value_control_point",
    "UST30Y": "duration_convexity_term_premium",
    "COPPER": "scarcity_supply_elasticity",
    "GOLD": "monetary_scarcity_reserve_demand",
    "USDJPY": "policy_divergence_carry_flow",
}


def main():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert data["test_type"] == "architecture_semantic_routing_fixture"
    assert "does not assert current market state" in data["explicit_non_claim"]
    assert data["required_human_grammar"] == ["P_势", "N_信", "X_极", "E_真", "V_价", "S_生"]
    assert data["required_x_tuple"] == ["Xs", "Xa", "Xp"]

    cases = data["cases"]
    targets = [x["target"] for x in cases]
    assert targets == EXPECTED_TARGETS
    assert len({x["A0_asset_form"] for x in cases}) == 5

    for case in cases:
        target = case["target"]
        assert case["A0_asset_form"] == EXPECTED_FORMS[target]
        assert isinstance(case["A1_pricing_archetype"], list) and case["A1_pricing_archetype"]
        assert case["Xs_expected_family"] == EXPECTED_XS[target]
        assert case["P_asset_example"]
        assert case["N_example"]
        assert case["V_expected_family"]
        assert case["stress_assertion"]

    # Force genuine cross-asset specialization rather than one universal equity template.
    assert len({x["Xs_expected_family"] for x in cases}) == 5
    assert len({x["V_expected_family"] for x in cases}) == 5

    joined = json.dumps(data, ensure_ascii=False).lower()
    prohibited = ["buy", "sell", "target_price", "recommended_weight", "live_sizing", "execute_trade"]
    # The pass-conditions prose may mention that those outputs are prohibited; no case may contain action fields.
    for case in cases:
        case_keys = {k.lower() for k in case.keys()}
        for key in prohibited:
            assert key not in case_keys

    assert "semantic/routing coverage" in data["explicit_non_claim"] or "semantic_routing" in data["test_type"]
    print("R2.3-A Cross-Asset Stress Check: PASS")


if __name__ == "__main__":
    main()
