"""Research diagnostics safety; synthetic fixtures never market evidence."""
import copy
from datetime import date, datetime
import unittest
from zoneinfo import ZoneInfo

from yuanli_invest.gold_au_historical_replay import (
    HistoricalResearchDataset, hypothetical_publication_at, run_historical_scope, scoped_engine,
)
from yuanli_invest.gold_au_strategy import GoldAuDataset, run_backtest
from tests.test_gold_au_strategy import fixture

SH = ZoneInfo("Asia/Shanghai")


class HistoricalReplayTests(unittest.TestCase):
    def test_h10_weekly_release_has_no_same_observation_day_visibility(self):
        self.assertEqual(hypothetical_publication_at("FED:H10:DTWEXBGS", date(2025, 9, 12)).astimezone(SH).isoformat(),
                         "2025-09-16T04:30:00+08:00")

    def test_h10_monday_holiday_rolls_to_next_assumed_business_day(self):
        self.assertEqual(hypothetical_publication_at("FED:H10:DTWEXBGS", date(2025, 1, 17)).astimezone(SH).isoformat(),
                         "2025-01-22T05:30:00+08:00")

    def test_h15_next_business_day_observation_and_dst_conversion(self):
        self.assertEqual(hypothetical_publication_at("FRED:DFII10", date(2025, 7, 3)).astimezone(SH).isoformat(),
                         "2025-07-08T04:30:00+08:00")

    def test_scope_adapter_full_range_exact_engine_equivalence(self):
        dataset = GoldAuDataset(fixture(100))
        original = run_backtest(dataset, variant="full", pit_mode="reconstructed")
        function, _ = scoped_engine()
        scoped = function(dataset, variant="full", pit_mode="reconstructed")
        self.assertEqual({key: value for key, value in scoped.items() if key != "terminal_position"}, original)

    def test_post_end_price_oi_and_macro_cannot_change_period_execution(self):
        payload = fixture(150)
        start, end = date(2026, 2, 2), date(2026, 3, 31)
        original = run_historical_scope(GoldAuDataset(payload), start=start, end=end, pit_mode="reconstructed")
        altered = copy.deepcopy(payload)
        for row in altered["bars"]:
            if row["date"] > end.isoformat():
                for field in ("open", "high", "low", "close"):
                    row[field] *= 7
                row["open_interest"] += 999999
        for row in altered["observations"]:
            if row["observed_on"] > end.isoformat():
                row["value"] *= 5
        changed = run_historical_scope(GoldAuDataset(altered), start=start, end=end, pit_mode="reconstructed")
        for field in ("decisions", "events", "trades", "equity_curve", "terminal_position"):
            self.assertEqual(changed[field], original[field])
        self.assertTrue(all(start.isoformat() <= row["date"] <= end.isoformat() for row in original["events"]))

    def test_assumed_delay_preserves_capture_provenance_and_strict_rejection(self):
        payload = fixture(100, retrieved_after=True)
        dataset = HistoricalResearchDataset(payload, publication_model="SCHEDULE_DELAY_LATEST_VINTAGE_EXPLORATORY")
        at = datetime(2026, 2, 3, 8, 30, tzinfo=SH)
        regime = "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY"
        rows = dataset.latest_n("FED:H10:DTWEXBGS", 20, at, "reconstructed", regime)
        self.assertTrue(rows)
        self.assertTrue(all(datetime.fromisoformat(row["hypothetical_publication_at"]) <= at for row in rows))
        original = {row["vintage_id"]: row for row in payload["observations"]}
        for row in rows:
            for field in ("released_at", "retrieved_at", "available_at", "vintage_kind", "pit_grade"):
                self.assertEqual(row[field], original[row["vintage_id"]][field])
        self.assertEqual(dataset.latest_n("FED:H10:DTWEXBGS", 20, at, "strict", regime), [])

    def test_unknown_models_and_series_and_inverted_scope_reject(self):
        with self.assertRaises(ValueError):
            HistoricalResearchDataset(fixture(10), publication_model="PIT_VERIFIED")
        with self.assertRaises(ValueError):
            hypothetical_publication_at("WGC:GLOBAL_OFFICIAL_NET_PURCHASES", date(2025, 1, 1))
        with self.assertRaises(ValueError):
            run_historical_scope(GoldAuDataset(fixture(10)), start=date(2026, 2, 1), end=date(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()
