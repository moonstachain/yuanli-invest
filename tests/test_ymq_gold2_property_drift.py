import math
import unittest
from datetime import date

from scripts import ymq_gold2_property_drift as drift


class Gold2PropertyDriftTests(unittest.TestCase):
    def test_coefficient_distance_zero_for_same_vector(self):
        coef = {"alpha": 1.0, "beta_usd": -1.0, "beta_inflation": 0.5, "beta_real_rate": -0.8}
        self.assertAlmostEqual(drift.coefficient_distance(coef, coef), 0.0)

    def test_dominant_factor_uses_absolute_contribution(self):
        row = {"usd_return": 2.0, "inflation_change": 0.1, "real_rate_change": -0.2}
        coef = {"alpha": 0.0, "beta_usd": -1.0, "beta_inflation": 5.0, "beta_real_rate": 2.0}
        self.assertEqual(drift.dominant_factor(row, coef), "usd_return")

    def test_block_summary_is_research_only(self):
        fixed = {"alpha": 0.0, "beta_usd": -1.0, "beta_inflation": 0.5, "beta_real_rate": -0.5}
        states = []
        for month in range(1, 7):
            row = {
                "decision_date": f"2020-{month:02d}-28",
                "known_as_of": f"2020-{month:02d}-28",
                "gold_return": 1.0,
                "usd_return": 0.2,
                "inflation_change": 0.1,
                "real_rate_change": -0.1,
            }
            states.append({
                "decision_date": row["decision_date"],
                "known_as_of": row["known_as_of"],
                "row": row,
                "coefficients": {"alpha": 0.0, "beta_usd": 0.5, "beta_inflation": 2.0, "beta_real_rate": 1.5},
            })
        result = drift.block_summary(states, fixed, date(2020, 1, 1), date(2020, 12, 31))
        self.assertIn(result["property_drift_state"], {
            "STABLE_PROPERTY",
            "DRIFT_CANDIDATE",
            "DRIFT_CONFIRMED_RESEARCH_ONLY",
            "INSUFFICIENT_EVIDENCE",
        })
        self.assertNotIn("alpha", result["property_drift_state"].lower())

    def test_stable_diagnostics_are_evidence_not_missing_evidence(self):
        fixed = {"alpha": 0.0, "beta_usd": -1.0, "beta_inflation": 0.5, "beta_real_rate": -0.5}
        states = []
        for month, residual in ((1, -0.1), (2, 0.1)):
            row = {
                "decision_date": f"2020-{month:02d}-28",
                "gold_return": -0.1 + residual,
                "usd_return": 0.2,
                "inflation_change": 0.1,
                "real_rate_change": -0.1,
            }
            states.append({"decision_date": row["decision_date"], "row": row, "coefficients": fixed})

        result = drift.block_summary(states, fixed, date(2020, 1, 1), date(2020, 12, 31))
        self.assertEqual(result["property_drift_state"], "STABLE_PROPERTY")
        self.assertEqual(result["independent_evidence_count"], 3)
        self.assertFalse(any(result["diagnostics"].values()))

    def test_one_abnormal_diagnostic_can_use_other_available_diagnostics(self):
        fixed = {"alpha": 0.0, "beta_usd": -1.0, "beta_inflation": 0.5, "beta_real_rate": -0.5}
        dynamic = {key: value * 1.8 for key, value in fixed.items()}
        states = []
        for month, residual in ((1, -0.1), (2, 0.1)):
            row = {
                "decision_date": f"2020-{month:02d}-28",
                "gold_return": -0.1 + residual,
                "usd_return": 0.2,
                "inflation_change": 0.1,
                "real_rate_change": -0.1,
            }
            states.append({"decision_date": row["decision_date"], "row": row, "coefficients": dynamic})

        result = drift.block_summary(states, fixed, date(2020, 1, 1), date(2020, 12, 31))
        self.assertEqual(result["property_drift_state"], "DRIFT_CANDIDATE")
        self.assertEqual(sum(result["diagnostics"].values()), 1)
        self.assertEqual(result["independent_evidence_count"], 3)

    def test_rmse_requires_nonempty_vector(self):
        with self.assertRaises(ValueError):
            drift.rmse([])


if __name__ == "__main__":
    unittest.main()
