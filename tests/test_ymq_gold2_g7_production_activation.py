import tempfile
import unittest
from pathlib import Path

from scripts import ymq_gold2_learning_live as learning
from scripts import ymq_gold2_live_shadow as shadow


class G7ProductionActivationTests(unittest.TestCase):
    def _receipt(self, day, gold, real_rate, usd, known):
        return {
            "status": "LIVE_SHADOW_RECEIPT",
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
            "unknowns": ["policy_path_expectations"],
        }

    def test_default_contract_authorizes_only_production_learning_integration(self):
        cfg = learning.load_contract()
        learning.validate_contract(cfg)
        self.assertTrue(cfg["authority"]["research_learning_authorized"])
        self.assertTrue(cfg["authority"]["production_scheduler_integration_authorized"])
        for field in (
            "accepted_learning_authorized",
            "capital_authorized",
            "sizing_authorized",
            "execution_authorized",
            "broker_action",
            "veighna_authorized",
            "asset_promotion_authorized",
            "canon_promotion_authorized",
        ):
            self.assertFalse(cfg["authority"][field])

    def test_default_hook_emits_learning_candidate_after_two_successful_days(self):
        prior = self._receipt("2026-09-16", 4296.15, 3.05, 99.6335, "2026-09-15")
        current = self._receipt("2026-09-17", 4328.2, 3.06, 100.3293, "2026-09-16")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shadow.write_receipt(prior, root)
            shadow.write_receipt(current, root)
            result = shadow.emit_learning_live(current, root)
            self.assertEqual(result["status"], "LEARNING_CANDIDATE_ONLY")
            self.assertFalse(result["accepted_learning"])
            self.assertTrue(Path(td, "learning", "latest-learning.json").exists())
            self.assertFalse(result["authority"]["capital_authorized"])
            self.assertFalse(result["authority"]["execution_authorized"])


if __name__ == "__main__":
    unittest.main()
