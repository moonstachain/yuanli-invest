import hashlib
import json
import math
import unittest
from datetime import date

try:
    from scripts import ymq4_b3_dynamic_beta as b3
except ImportError:
    b3 = None


class B3ContractTests(unittest.TestCase):
    def test_module_exists(self):
        self.assertIsNotNone(b3, "scripts.ymq4_b3_dynamic_beta must exist")

    def test_frozen_constants(self):
        self.assertEqual(b3.WINDOW_MONTHS, 60)
        self.assertEqual(b3.EXPECTED_OOS_ROWS, 236)
        self.assertEqual(b3.CANONICAL_B2_GATE_ID, "8907b60a-445c-4396-8e51-29e6f36620fb")

    def test_rolling_uses_strictly_prior_60_rows(self):
        rows = []
        for i in range(70):
            year = 2000 + i // 12
            month = i % 12 + 1
            d = date(year, month, 28).isoformat()
            x = float(i + 1)
            rows.append({
                "decision_date": d,
                "known_as_of": d,
                "gold_return": 1.0 + 2.0 * x + 3.0 * (x / 10.0) - 0.5 * (x / 100.0),
                "usd_return": x,
                "inflation_change": x / 10.0,
                "real_rate_change": x / 100.0,
            })
        states = b3.rolling_dynamic_predictions(rows, start_index=60, window=60)
        self.assertEqual(len(states), 10)
        self.assertEqual(states[0]["estimation_rows"], 60)
        self.assertEqual(states[0]["estimation_end"], rows[59]["decision_date"])
        self.assertEqual(states[0]["decision_date"], rows[60]["decision_date"])
        self.assertLess(states[0]["estimation_end"], states[0]["decision_date"])

    def test_coefficient_state_sha_is_deterministic(self):
        states = [
            {"decision_date": "2020-01-31", "coefficients": {"alpha": 1.0, "beta_usd": -1.0}},
            {"decision_date": "2020-02-29", "coefficients": {"alpha": 2.0, "beta_usd": -2.0}},
        ]
        a = b3.coefficient_state_sha(states)
        b = b3.coefficient_state_sha(list(states))
        self.assertEqual(a, b)
        self.assertEqual(len(a), 64)
        int(a, 16)

    def test_compare_to_b2_requires_all_three_gates(self):
        b2 = {
            "rmse": 3.0,
            "mae": 2.0,
            "blocks": {"a": 4.0, "b": 4.0, "c": 4.0, "d": 4.0},
        }
        dynamic = {
            "rmse": 2.9,
            "mae": 2.0,
            "blocks": {"a": 3.9, "b": 3.8, "c": 3.7, "d": 4.1},
        }
        result = b3.compare_to_b2(dynamic, b2, minimum_positive_blocks=3)
        self.assertTrue(result["beats_b2"])
        self.assertEqual(result["positive_rmse_blocks"], 3)
        dynamic["mae"] = 2.1
        self.assertFalse(b3.compare_to_b2(dynamic, b2, minimum_positive_blocks=3)["beats_b2"])

    def test_no_complex_rescue_surface(self):
        source = open(b3.__file__, encoding="utf-8").read().lower()
        for forbidden in (
            "kalman", "tvp", "dcc", "hmm", "regime_switch", "window_search",
            "place_order", "submit_order", "broker.connect", "portfolio_size",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
