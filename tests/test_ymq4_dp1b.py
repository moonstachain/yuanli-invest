import importlib.util
import pathlib
import unittest
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("dp1b", ROOT / "scripts/ymq4_dp1b_backfill.py")
if SPEC and SPEC.loader and (ROOT / "scripts/ymq4_dp1b_backfill.py").exists():
    MOD = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(MOD)
else:
    MOD = None


class TestDP1B(unittest.TestCase):
    def require_mod(self):
        self.assertIsNotNone(MOD, "scripts/ymq4_dp1b_backfill.py must exist")
        return MOD

    def test_month_ends_are_calendar_month_ends(self):
        m = self.require_mod()
        self.assertEqual(
            m.month_ends(date(1978, 1, 1), date(1978, 3, 31)),
            [date(1978, 1, 31), date(1978, 2, 28), date(1978, 3, 31)],
        )

    def test_latest_on_or_before_never_uses_future_row(self):
        m = self.require_mod()
        rows = [
            {"observation_date": "2020-01-30", "value": 100.0},
            {"observation_date": "2020-01-31", "value": 101.0},
            {"observation_date": "2020-02-03", "value": 999.0},
        ]
        got = m.latest_on_or_before(rows, date(2020, 1, 31))
        self.assertEqual(got["value"], 101.0)
        self.assertLessEqual(date.fromisoformat(got["observation_date"]), date(2020, 1, 31))

    def test_cpi_yoy_uses_same_vintage_levels(self):
        m = self.require_mod()
        rows = [
            {"observation_date": "1978-01-01", "value": 100.0},
            {"observation_date": "1979-01-01", "value": 110.0},
        ]
        self.assertAlmostEqual(m.cpi_yoy_from_same_vintage(rows, date(1979, 1, 1)), 10.0, places=9)

    def test_measurement_regime_switches_are_frozen(self):
        m = self.require_mod()
        r1978 = m.measurement_regime(date(1978, 12, 31))
        r2003 = m.measurement_regime(date(2003, 1, 31))
        r2006 = m.measurement_regime(date(2006, 1, 31))
        self.assertEqual(r1978["real_rate_method"], "DTB3_MINUS_CPI_YOY_ASOF")
        self.assertEqual(r1978["usd_series"], "DTWEXM")
        self.assertEqual(r2003["real_rate_method"], "DFII10")
        self.assertEqual(r2003["usd_series"], "DTWEXM")
        self.assertEqual(r2006["usd_series"], "DTWEXBGS")

    def test_future_leakage_count_detects_known_after_decision(self):
        m = self.require_mod()
        rows = [
            {"decision_date": "2020-01-31", "known_as_of": "2020-01-31"},
            {"decision_date": "2020-02-29", "known_as_of": "2020-03-01"},
        ]
        self.assertEqual(m.future_leakage_count(rows), 1)

    def test_coverage_report_requires_all_four_factors(self):
        m = self.require_mod()
        rows = []
        for factor in ("gold_usd_oz", "usd", "inflation_yoy", "real_rate"):
            rows.append({"decision_date": "2020-01-31", "factor_id": factor, "value_numeric": 1.0})
        rows.extend([
            {"decision_date": "2020-02-29", "factor_id": "gold_usd_oz", "value_numeric": 1.0},
            {"decision_date": "2020-02-29", "factor_id": "usd", "value_numeric": 1.0},
            {"decision_date": "2020-02-29", "factor_id": "inflation_yoy", "value_numeric": 1.0},
        ])
        report = m.coverage_report(
            rows,
            {"mini": (date(2020, 1, 1), date(2020, 2, 29))},
            threshold=0.80,
        )
        self.assertEqual(report["mini"]["complete_months"], 1)
        self.assertEqual(report["mini"]["expected_months"], 2)
        self.assertEqual(report["mini"]["coverage"], 0.5)
        self.assertFalse(report["mini"]["pass"])


if __name__ == "__main__":
    unittest.main()
