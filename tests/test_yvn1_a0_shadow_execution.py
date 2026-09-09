from pathlib import Path
import copy
import importlib.util
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "packages" / "contracts" / "schemas" / "vnext"
CONFIG = ROOT / "config" / "yvn1" / "yvn1_a0_shadow_execution.v0.1.json"
SCENARIOS = ROOT / "fixtures" / "yvn1" / "yvn1_a0_golden_scenarios.v0.1.json"
VALIDATOR = ROOT / "scripts" / "validate_yvn1_a0_shadow_execution.py"


def load_validator():
    if not VALIDATOR.exists():
        raise AssertionError(str(VALIDATOR))
    spec = importlib.util.spec_from_file_location("validate_yvn1_a0_shadow_execution", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class YVN1A0ContractTests(unittest.TestCase):
    def load_schema(self, name: str) -> dict:
        return json.loads((VNEXT / name).read_text(encoding="utf-8"))

    def test_machine_config_exists(self):
        self.assertTrue(CONFIG.exists(), str(CONFIG))

    def test_golden_scenario_registry_exists(self):
        self.assertTrue(SCENARIOS.exists(), str(SCENARIOS))

    def test_three_provider_neutral_schemas_exist(self):
        for name in (
            "execution-plan.schema.json",
            "provider-state.schema.json",
            "shadow-execution-settlement.schema.json",
        ):
            self.assertTrue((VNEXT / name).exists(), name)

    def test_a0_has_zero_runtime_or_broker_authority(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        for key in (
            "veighna_installation_authorized",
            "veighna_invocation_authorized",
            "broker_credentials_authorized",
            "broker_connection_authorized",
            "market_data_subscription_authorized",
            "broker_paper_authorized",
            "live_execution_authorized",
            "real_capital_movement_authorized",
            "a1_runtime_authorized",
        ):
            self.assertFalse(config["authority_ceiling"][key], key)

    def test_scenarios_are_exactly_s01_to_s10_and_s07_is_p0(self):
        registry = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        self.assertEqual(
            [s["scenario_id"] for s in registry["scenarios"]],
            [f"S{i:02d}" for i in range(1, 11)],
        )
        s07 = next(s for s in registry["scenarios"] if s["scenario_id"] == "S07")
        self.assertEqual(s07["priority"], "P0")

    def test_provider_state_sources_are_distinct(self):
        schema = self.load_schema("provider-state.schema.json")
        self.assertEqual(
            set(schema["properties"]["state_source"]["enum"]),
            {"shadow_oms", "synthetic_broker_custodian"},
        )

    def test_execution_plan_cannot_authorize_live(self):
        schema = self.load_schema("execution-plan.schema.json")
        self.assertIs(schema["properties"]["live_execution_authorized"]["const"], False)
        self.assertIs(schema["properties"]["real_capital_movement_authorized"]["const"], False)

    def test_validator_exists_and_accepts_canonical_a0(self):
        yvn1 = load_validator()
        yvn1.validate_a0()


class YVN1A0AdversarialTests(unittest.TestCase):
    def test_authority_escalation_is_rejected(self):
        yvn1 = load_validator()
        config = yvn1.load_config()
        for key in (
            "veighna_invocation_authorized",
            "broker_paper_authorized",
            "a1_runtime_authorized",
        ):
            mutated = copy.deepcopy(config)
            mutated["authority_ceiling"][key] = True
            with self.assertRaises(ValueError):
                yvn1.validate_authority_ceiling(mutated)

    def test_s07_cannot_lose_p0_status(self):
        yvn1 = load_validator()
        registry = yvn1.load_scenarios()
        mutated = copy.deepcopy(registry)
        next(s for s in mutated["scenarios"] if s["scenario_id"] == "S07")["priority"] = "P1"
        with self.assertRaises(ValueError):
            yvn1.validate_golden_scenarios(mutated)

    def test_s11_cannot_be_silently_added(self):
        yvn1 = load_validator()
        registry = yvn1.load_scenarios()
        mutated = copy.deepcopy(registry)
        mutated["scenarios"].append({
            "scenario_id": "S11",
            "priority": "P1",
            "name": "silent_rescue_scenario",
            "required_terminal_behavior": "SETTLED",
            "required_invariants": [],
        })
        with self.assertRaises(ValueError):
            yvn1.validate_golden_scenarios(mutated)

    def test_broker_network_dependency_is_rejected(self):
        yvn1 = load_validator()
        config = yvn1.load_config()
        mutated = copy.deepcopy(config)
        mutated["deployment_freeze"]["broker_network_dependency"] = True
        with self.assertRaises(ValueError):
            yvn1.validate_deployment_freeze(mutated)


if __name__ == "__main__":
    unittest.main()
