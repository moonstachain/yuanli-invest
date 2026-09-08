import calendar
import math
import unittest
from datetime import date

from scripts import ymq4_b2_fixed_beta as b2


FACTORS = ("gold_usd_oz", "usd", "inflation_yoy", "real_rate")


def month_end(year, month):
    return date(year, month, calendar.monthrange(year, month)[1])


def months():
    out = []
    y, m = 1978, 1
    while (y, m) <= (2026, 8):
        out.append(month_end(y, m))
        m += 1
        if m == 13:
            y += 1
            m = 1
    return out


def synthetic_panel():
    rows = []
    for i, d in enumerate(months()):
        values = {
            "gold_usd_oz": 200.0 * math.exp(0.0025 * i + 0.01 * math.sin(i / 7.0)),
            "usd": 90.0 * math.exp(0.0004 * i + 0.004 * math.cos(i / 9.0)),
            "inflation_yoy": 3.0 + 0.4 * math.sin(i / 11.0),
            "real_rate": 1.5 + 0.3 * math.cos(i / 13.0),
        }
        for factor in FACTORS:
            rows.append({
                "panel_id": "gold_core_monthly_v0.1",
                "decision_date": d.isoformat(),
                "factor_id": factor,
                "value_numeric": values[factor],
                "known_as_of": d.isoformat(),
            })
    return rows


class B2TransformTests(unittest.TestCase):
    def test_build_transformed_rows_and_frozen_split_counts(self):
        panel = synthetic_panel()
        b2.validate_panel(panel)
        transformed = b2.build_transformed_rows(panel)
        self.assertEqual(len(transformed), 583)
        self.assertEqual(transformed[0]["decision_date"], "1978-02-28")
        self.assertEqual(transformed[-1]["decision_date"], "2026-08-31")
        train, oos = b2.split_rows(transformed)
        self.assertEqual(len(train), 347)
        self.assertEqual(len(oos), 236)
        self.assertEqual(train[-1]["decision_date"], "2006-12-31")
        self.assertEqual(oos[0]["decision_date"], "2007-01-31")

    def test_transformations_use_log_returns_and_level_differences(self):
        panel = [
            {"panel_id": "gold_core_monthly_v0.1", "decision_date": "1978-01-31", "factor_id": "gold_usd_oz", "value_numeric": 100.0, "known_as_of": "1978-01-31"},
            {"panel_id": "gold_core_monthly_v0.1", "decision_date": "1978-01-31", "factor_id": "usd", "value_numeric": 80.0, "known_as_of": "1978-01-31"},
            {"panel_id": "gold_core_monthly_v0.1", "decision_date": "1978-01-31", "factor_id": "inflation_yoy", "value_numeric": 5.0, "known_as_of": "1978-01-31"},
            {"panel_id": "gold_core_monthly_v0.1", "decision_date": "1978-01-31", "factor_id": "real_rate", "value_numeric": 1.0, "known_as_of": "1978-01-31"},
            {"panel_id": "gold_core_monthly_v0.1", "decision_date": "1978-02-28", "factor_id": "gold_usd_oz", "value_numeric": 110.0, "known_as_of": "1978-02-28"},
            {"panel_id": "gold_core_monthly_v0.1", "decision_date": "1978-02-28", "factor_id": "usd", "value_numeric": 84.0, "known_as_of": "1978-02-28"},
            {"panel_id": "gold_core_monthly_v0.1", "decision_date": "1978-02-28", "factor_id": "inflation_yoy", "value_numeric": 5.4, "known_as_of": "1978-02-28"},
            {"panel_id": "gold_core_monthly_v0.1", "decision_date": "1978-02-28", "factor_id": "real_rate", "value_numeric": 0.7, "known_as_of": "1978-02-28"},
        ]
        row = b2.build_transformed_rows(panel)[0]
        self.assertAlmostEqual(row["gold_return"], 100.0 * math.log(1.10), places=12)
        self.assertAlmostEqual(row["usd_return"], 100.0 * math.log(1.05), places=12)
        self.assertAlmostEqual(row["inflation_change"], 0.4, places=12)
        self.assertAlmostEqual(row["real_rate_change"], -0.3, places=12)

    def test_validate_panel_rejects_duplicate_factor_month(self):
        panel = synthetic_panel()
        panel.append(dict(panel[0]))
        with self.assertRaises(ValueError):
            b2.validate_panel(panel)

    def test_validate_panel_rejects_future_leakage(self):
        panel = synthetic_panel()
        panel[0] = {**panel[0], "known_as_of": "1978-02-01"}
        with self.assertRaises(ValueError):
            b2.validate_panel(panel)


class B2ModelTests(unittest.TestCase):
    def test_ols_recovers_known_coefficients(self):
        rows = []
        alpha, bu, bi, br = 1.25, -0.8, 0.5, -1.4
        for i in range(1, 80):
            u = math.sin(i / 3.0)
            inf = math.cos(i / 5.0)
            rr = ((i % 11) - 5) / 7.0
            y = alpha + bu * u + bi * inf + br * rr
            rows.append({
                "decision_date": f"2000-{((i - 1) % 12) + 1:02d}-28",
                "gold_return": y,
                "usd_return": u,
                "inflation_change": inf,
                "real_rate_change": rr,
            })
        coef = b2.fit_ols(rows)
        self.assertAlmostEqual(coef["alpha"], alpha, places=9)
        self.assertAlmostEqual(coef["beta_usd"], bu, places=9)
        self.assertAlmostEqual(coef["beta_inflation"], bi, places=9)
        self.assertAlmostEqual(coef["beta_real_rate"], br, places=9)

    def test_metrics_and_null_comparison(self):
        actual = [1.0, -1.0, 2.0, -2.0]
        fixed = [0.8, -0.9, 1.7, -1.6]
        null = [0.0, 0.0, 0.0, 0.0]
        fm = b2.metrics(actual, fixed)
        nm = b2.metrics(actual, null)
        self.assertLess(fm["rmse"], nm["rmse"])
        self.assertLess(fm["mae"], nm["mae"])
        self.assertEqual(fm["sign_accuracy"], 1.0)
        rel = b2.relative_metrics(fm, nm)
        self.assertGreater(rel["oos_r2_vs_null"], 0.0)
        self.assertGreater(rel["rmse_improvement_vs_null"], 0.0)

    def test_model_surface_contains_no_dynamic_beta_functions(self):
        forbidden = {"fit_rolling_beta", "fit_tvp_beta", "fit_kalman_beta", "fit_regime_switching"}
        self.assertTrue(forbidden.isdisjoint(set(dir(b2))))


if __name__ == "__main__":
    unittest.main()
