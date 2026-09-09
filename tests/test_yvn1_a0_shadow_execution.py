from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "packages" / "contracts" / "schemas" / "vnext"
CONFIG = ROOT / "config" / "yvn1" / "yvn1_a0_shadow_execution.v0.1.json"
SCENARIOS = ROOT / "fixtures" / "yvn1" / "yvn1_a0_golden_scenarios.v0.1.json"


class YVN1A0RedContractTests(unittest.TestCase):
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

    def test_scenarios_will_be_exactly_s01_to_s10(self):
        self.assertTrue(SCENARIOS.exists(), str(SCENARIOS))
        registry = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        self.assertEqual(
            [s["scenario_id"] for s in registry["scenarios"]],
            [f"S{i:02d}" for i in range(1, 11)],
        )


if __name__ == "__main__":
    unittest.main()
