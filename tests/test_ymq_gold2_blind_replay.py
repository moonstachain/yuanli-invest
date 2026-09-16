import calendar
import math
import unittest
from datetime import date

from scripts import ymq_gold2_blind_replay as replay


FACTORS = ("gold_usd_oz", "usd", "inflation_yoy", "real_rate")


def month_end(year, month):
    return date(year, month, calendar.monthrange(year, month)[1])


def synthetic_panel():
    dates = []
    year, month = 1978, 1
    while (year, month) <= (2026, 8):
        dates.append(month_end(year, month))
        month += 1
        if month == 13:
            year += 1
            month = 1
    rows = []
    for i, d in enumerate(dates):
        values = {
            "gold_usd_oz": 200.0 * math.exp(0.002 * i + 0.01 * math.sin(i / 9.0)),
            "usd": 90.0 * math.exp(0.0003 * i + 0.004 * math.cos(i / 11.0)),
            "inflation_yoy": 3.0 + 0.5 * math.sin(i / 13.0),
            "real_rate": 1.5 + 0.4 * math.cos(i / 17.0),
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


class Gold2BlindReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets = replay.build_replay_packets(synthetic_panel())

    def test_all_eight_frozen_windows_materialize(self):
        self.assertEqual(len(self.packets), 8)
        self.assertEqual([p["window_id"] for p in self.packets], [f"R{i}" for i in range(1, 9)])

    def test_missing_domains_fail_closed(self):
        for packet in self.packets:
            self.assertEqual(packet["expectation_reality_state"], "INDETERMINATE")
            self.assertEqual(packet["valuation_state"], "UNIDENTIFIABLE")
            self.assertGreaterEqual(len(packet["unknowns"]), 5)

    def test_pre_oos_windows_do_not_backfill_property_drift_with_future_b2(self):
        early = [p for p in self.packets if p["window_id"] in {"R1", "R2", "R3"}]
        for packet in early:
            self.assertEqual(packet["property_drift_state"], "INSUFFICIENT_EVIDENCE")

    def test_no_replay_grants_action_authority(self):
        for packet in self.packets:
            self.assertFalse(packet["capital_authorized"])
            self.assertFalse(packet["execution_authorized"])
            self.assertEqual(packet["b3_settlement"], "DYNAMIC_BETA_DOES_NOT_BEAT_B2")


if __name__ == "__main__":
    unittest.main()
