import copy
import json
import unittest
from pathlib import Path

from scripts.validate_yci0_rp0 import validate_contract


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config" / "yci0_rp0"


class YCI0RP0ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.question = json.loads(
            (CONFIG_DIR / "ai_infra_question.v0.1.json").read_text(encoding="utf-8")
        )
        cls.reality_contract = json.loads(
            (CONFIG_DIR / "ai_infra_reality_contract.v0.1.json").read_text(encoding="utf-8")
        )
        cls.metric_registry = json.loads(
            (CONFIG_DIR / "wind_metric_registry.v0.1.json").read_text(encoding="utf-8")
        )

    def test_question_is_frozen_research_only_object(self):
        self.assertEqual(self.question["question_id"], "YCI0-RP0-CQ-001")
        self.assertEqual(self.question["theme"], "AI_INFRA")
        self.assertEqual(self.question["authority"], "RESEARCH")
        self.assertTrue(self.question["prior_belief"].strip())
        self.assertTrue(self.question["defeat_condition"].strip())
        self.assertFalse(self.question["capital_authorized"])
        self.assertFalse(self.question["execution_authorized"])

    def test_registry_contains_every_priority_a_metric_family(self):
        expected = {
            "US_10Y_NOMINAL_YIELD",
            "US_10Y_REAL_YIELD",
            "DXY_USD_PROXY",
            "HYPERSCALER_CAPEX",
            "HYPERSCALER_GUIDANCE",
            "NVDA_DATA_CENTER_REVENUE",
            "COMPUTE_SUPPLY_NORMALIZATION_PROXY",
            "NETWORKING_PROXY",
            "POWER_EQUIPMENT_PROXY",
            "POWER_AVAILABILITY_PROXY",
            "MARKET_PRICE",
            "VALUATION",
        }
        actual = {metric["family"] for metric in self.metric_registry["metrics"]}
        self.assertTrue(expected.issubset(actual), expected - actual)

    def test_every_metric_declares_admission_contract(self):
        required = {
            "source_type",
            "pit_policy",
            "required_timestamps",
            "admission_rule",
            "fallback",
        }
        for metric in self.metric_registry["metrics"]:
            with self.subTest(metric_id=metric.get("metric_id")):
                self.assertTrue(required.issubset(metric))
                self.assertEqual(metric["fallback"], "UNKNOWN")
                self.assertTrue(metric["required_timestamps"])

    def test_frozen_closed_sets_match_accepted_spec(self):
        self.assertEqual(
            self.reality_contract["closed_sets"],
            {
                "authority": ["RESEARCH"],
                "evidence_status": ["PASS", "CURRENT_CONTEXT_ONLY", "BLOCKED", "UNKNOWN"],
                "reality_state": ["ACCELERATING", "STABLE", "DECELERATING", "MIXED", "UNKNOWN"],
                "narrative_stage": ["D0", "D1", "D2", "D3", "D4", "UNKNOWN"],
                "gate_status": ["OPEN", "PASS", "BLOCKED", "UNKNOWN", "NO_GO"],
            },
        )

    def test_validator_accepts_frozen_contracts(self):
        self.assertEqual(
            validate_contract(self.question, self.reality_contract, self.metric_registry), []
        )

    def test_validator_fails_closed_on_authority_leak_and_bad_metric(self):
        question = copy.deepcopy(self.question)
        question["capital_authorized"] = True
        registry = copy.deepcopy(self.metric_registry)
        registry["metrics"][0]["fallback"] = "PASS"
        errors = validate_contract(question, self.reality_contract, registry)
        self.assertIn("question:capital_authority_must_be_false", errors)
        self.assertIn(
            f"metric:{registry['metrics'][0]['metric_id']}:fallback_must_be_UNKNOWN", errors
        )

    def test_validator_rejects_source_authority_expansion(self):
        contract = copy.deepcopy(self.reality_contract)
        contract["system_roles"]["wind_structured_mcp"] = "DECISION_AUTHORITY"
        contract["explicitly_not_authorized"].remove("EXECUTION_AUTHORITY")
        errors = validate_contract(self.question, contract, self.metric_registry)
        self.assertIn("reality_contract:system_roles_mismatch", errors)
        self.assertIn("reality_contract:explicit_non_authorizations_incomplete", errors)


if __name__ == "__main__":
    unittest.main()
