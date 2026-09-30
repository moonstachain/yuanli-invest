import json
import tempfile
import unittest
from pathlib import Path

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


class LearningLiveTests(unittest.TestCase):
    def test_contract_keeps_learning_non_authoritative(self):
        cfg = learning.load_contract(CONTRACT)
        learning.validate_contract(cfg)
        self.assertEqual(cfg["status"], "HUMAN_AUTHORIZED_RESEARCH_LEARNING_ONLY")
        self.assertTrue(cfg["authority"]["research_learning_authorized"])
        for field in (
            "accepted_learning_authorized", "capital_authorized", "sizing_authorized",
            "execution_authorized", "broker_action", "veighna_authorized",
            "asset_promotion_authorized", "canon_promotion_authorized",
        ):
            self.assertFalse(cfg["authority"][field])

    def test_contract_freezes_attention_thresholds_and_scoring_law(self):
        cfg = learning.load_contract(CONTRACT)
        self.assertEqual(cfg["attention_thresholds"], {
            "gold_price_pct_abs": 1.0,
            "real_rate_bps_abs": 10.0,
            "usd_pct_abs": 0.5,
        })
        self.assertTrue(cfg["settlement"]["directional_scoring_requires_preregistered_claim"])
        self.assertEqual(cfg["settlement"]["missing_claim_state"], "NOT_SCORABLE")
        self.assertEqual(cfg["settlement"]["known_as_of_regression"], "FAIL_CLOSED")

    def test_delta_math_attention_and_unknown_resolution(self):
        cfg = learning.load_contract(CONTRACT)
        prior = receipt("2026-09-16", 4296.15, 3.05, 99.6335, known="2026-09-15")
        current = receipt(
            "2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16",
            unknowns=["policy_path_expectations"],
        )
        delta = learning.build_state_delta(prior, current, cfg)
        self.assertAlmostEqual(delta["gold_price_pct"], 0.7460167824680175, places=9)
        self.assertAlmostEqual(delta["real_rate_bps"], 1.0, places=6)
        self.assertAlmostEqual(delta["usd_pct"], 0.6983594875217713, places=9)
        self.assertEqual(delta["attention"], ["usd_pct"])
        self.assertEqual(delta["unknowns_resolved"], ["narrative_crowding_if_authoritative"])
        self.assertEqual(delta["unknowns_added"], [])
        self.assertEqual(delta["state_transitions"], {})

    def test_known_as_of_regression_fails_closed(self):
        cfg = learning.load_contract(CONTRACT)
        prior = receipt("2026-09-16", 4296.15, 3.05, 99.63, known="2026-09-15")
        current = receipt("2026-09-17", 4300.0, 3.05, 99.7, known="2026-09-14")
        with self.assertRaisesRegex(ValueError, "known_as_of regression"):
            learning.build_state_delta(prior, current, cfg)

    def test_settlement_without_preregistered_claim_is_not_scorable(self):
        cfg = learning.load_contract(CONTRACT)
        prior = receipt("2026-09-16", 4296.15, 3.05, 99.63, known="2026-09-15")
        current = receipt("2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16")
        delta = learning.build_state_delta(prior, current, cfg)
        settlement = learning.build_settlement(prior, current, delta, cfg)
        self.assertEqual(settlement["pit_integrity"], "PASS")
        self.assertEqual(settlement["directional_claim_score"], "NOT_SCORABLE")
        self.assertEqual(settlement["regime_detection_lag"], "PENDING")
        self.assertEqual(settlement["decision_regret"], "NOT_APPLICABLE")

    def test_learning_candidate_is_non_authoritative_and_hashed(self):
        cfg = learning.load_contract(CONTRACT)
        prior = receipt("2026-09-16", 4296.15, 3.05, 99.63, known="2026-09-15")
        current = receipt("2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16")
        candidate = learning.build_learning_candidate(prior, current, cfg)
        self.assertEqual(candidate["status"], "LEARNING_CANDIDATE_ONLY")
        self.assertFalse(candidate["accepted_learning"])
        self.assertFalse(candidate["authority"]["canon_promotion_authorized"])
        self.assertEqual(len(candidate["source_receipts"]["prior_sha256"]), 64)
        self.assertEqual(len(candidate["source_receipts"]["current_sha256"]), 64)
        self.assertGreaterEqual(candidate["unknown_rate"], 0)
        self.assertLessEqual(candidate["unknown_rate"], 1)

    def test_same_day_receipts_are_skipped_for_daily_learning(self):
        cfg = learning.load_contract(CONTRACT)
        prior = receipt("2026-09-17", 4328.1, 3.06, 100.3, known="2026-09-16")
        current = receipt("2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16")
        result = learning.build_learning_candidate(prior, current, cfg)
        self.assertEqual(result["status"], "DUPLICATE_DAY_SKIPPED")

    def test_find_previous_daily_receipt_ignores_same_day_and_failures(self):
        current = receipt("2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16")
        same_day = receipt("2026-09-17", 4320.0, 3.06, 100.2, known="2026-09-16")
        previous = receipt("2026-09-16", 4296.15, 3.05, 99.6335, known="2026-09-15")
        failed = receipt("2026-09-15", 0, 0, 0, status="PROVIDER_FAIL_CLOSED")
        self.assertEqual(learning.find_previous_daily_receipt(current, [failed, same_day, previous]), previous)

    def test_private_write_creates_learning_tree_only(self):
        cfg = learning.load_contract(CONTRACT)
        prior = receipt("2026-09-16", 4296.15, 3.05, 99.63, known="2026-09-15")
        current = receipt("2026-09-17", 4328.2, 3.06, 100.3293, known="2026-09-16")
        candidate = learning.build_learning_candidate(prior, current, cfg)
        with tempfile.TemporaryDirectory() as td:
            target = learning.write_learning_candidate(candidate, Path(td))
            self.assertTrue(target.exists())
            self.assertTrue(Path(td, "learning", "latest-learning.json").exists())
            self.assertIn("learning", target.parts)

    def test_nonfinite_inputs_cannot_silently_suppress_attention(self):
        cfg = learning.load_contract(CONTRACT)
        prior = receipt("2026-09-16", 1000, 3, 100)
        for value in (float("nan"), float("inf"), float("-inf"), True):
            with self.subTest(value=value):
                current = receipt("2026-09-17", value, 3, 100)
                with self.assertRaises(ValueError):
                    learning.build_learning_candidate(prior, current, cfg)
                bad_cfg = learning.load_contract(CONTRACT)
                bad_cfg["attention_thresholds"]["gold_price_pct_abs"] = value
                with self.assertRaises(ValueError):
                    learning.validate_contract(bad_cfg)

    def test_provider_date_cannot_hide_behind_valid_summary(self):
        prior = receipt("2026-09-16", 1000, 3, 100)
        cfg = learning.load_contract(CONTRACT)
        for metric_day in ("2026-09-18", "2026-09-15"):
            current = receipt("2026-09-17", 1010, 3, 100)
            current["provider_receipts"]["gold_price"]["latest_date"] = metric_day
            with self.subTest(metric_day=metric_day), self.assertRaises(ValueError):
                learning.build_learning_candidate(prior, current, cfg)

    def test_selects_latest_actual_run_within_prior_day(self):
        current = receipt("2026-09-17", 1010, 3, 100)
        early = receipt("2026-09-16", 1000, 3, 100)
        late = receipt("2026-09-16", 1005, 3, 100)
        early["generated_at"] = "2026-09-16T09:00:00+08:00"
        late["generated_at"] = "2026-09-16T02:00:00Z"
        for candidates in ([early, late], [late, early]):
            self.assertEqual(learning.find_previous_daily_receipt(current, iter(candidates)), late)

    def test_legacy_tie_break_remains_deterministic(self):
        current = receipt("2026-09-17", 1010, 3, 100)
        a = receipt("2026-09-16", 1000, 3, 100)
        b = receipt("2026-09-16", 1005, 3, 100)
        expected = max([a, b], key=learning.receipt_sha256)
        self.assertEqual(learning.find_previous_daily_receipt(current, [a, b]), expected)
        self.assertEqual(learning.find_previous_daily_receipt(current, [b, a]), expected)

    def test_process_reads_history_and_writes_linked_candidate(self):
        prior = receipt("2026-09-16", 1000, 3, 100)
        current = receipt("2026-09-17", 1010, 3.1, 101)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            learning.write_receipt(prior, root)
            learning.write_receipt(current, root)
            (root / "2026-09-16" / "receipt-truncated.json").write_text("{")
            candidate = learning.process_current_receipt(current, root)
            self.assertEqual(candidate["delta"]["prior_as_of"], prior["as_of"])
            self.assertEqual(candidate["source_receipts"]["current_sha256"], learning.receipt_sha256(current))
            self.assertTrue(Path(candidate["learning_receipt_path"]).exists())


if __name__ == "__main__":
    unittest.main()
