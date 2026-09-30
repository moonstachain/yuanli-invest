"""Synthetic mechanics checks. These fixtures are never market evidence."""

from __future__ import annotations

import json
import unittest
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from yuanli_invest.gold_au_strategy import (
    GoldAuDataset,
    build_decision_path,
    evaluate_signal,
    macro_gate,
    run_backtest,
)

SHA = "a" * 64
NY = ZoneInfo("America/New_York")
SHANGHAI = ZoneInfo("Asia/Shanghai")


def _stamp(day: date, hour: int, zone=SHANGHAI) -> str:
    return datetime(day.year, day.month, day.day, hour, tzinfo=zone).isoformat()


def _weekdays(start: date, count: int) -> list[date]:
    days = []
    current = start
    while len(days) < count:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def fixture(n: int = 100, *, retrieved_after: bool = False, wide_range: bool = False) -> dict:
    dates = _weekdays(date(2026, 1, 5), n)
    bars = []
    observations = []
    for i, day in enumerate(dates):
        for contract, basis in (("au2712", 0), ("au2802", 50)):
            close = 1000 + basis + 0.30 * i
            radius = 15 if wide_range else 1
            first_published = _stamp(day, 18)
            retrieved = _stamp(day + timedelta(days=1), 7) if not retrieved_after else _stamp(day + timedelta(days=60), 7)
            bars.append({"date": day.isoformat(), "contract": contract, "open": close,
                         "high": close + radius, "low": close - radius, "close": close,
                         "open_interest": (10000 if i < 80 else 8000) if contract == "au2712" else (9000 if i < 80 else 11000),
                         "margin_per_lot_cny": 200000,
                         "fee_open_per_lot_cny": 20, "fee_close_today_per_lot_cny": 20,
                         "fee_close_yesterday_per_lot_cny": 20,
                         "execution_cost_grade": "VERIFIED",
                         "first_published_at": first_published, "retrieved_at": retrieved,
                         "available_at": retrieved, "source_ref": "SYNTHETIC_TEST_ONLY",
                         "vintage_id": f"{contract}-{day}", "raw_sha256": SHA,
                         "pit_grade": "UNKNOWN" if retrieved_after else "VERIFIED",
                         "vintage_kind": "UNKNOWN" if retrieved_after else "FIRST_RELEASE",
                         "entry_window_price": close, "post_entry_low": close - radius})
        for series, unit, regime, value in (
            ("FRED:DFII10", "PERCENT", "FRED_DFII10_DAILY_10Y_TIPS_DATE_LABEL_NY", 4.5 - i * 0.01),
            ("FED:H10:DTWEXBGS", "INDEX", "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY", 100 - i * 0.05),
        ):
            released = _stamp(day, 17, NY)
            retrieved = _stamp(day, 18, NY) if not retrieved_after else _stamp(day + timedelta(days=60), 18, NY)
            observations.append({"series": series, "unit": unit, "measurement_regime": regime,
                                 "observed_on": day.isoformat(), "value": value,
                                 "released_at": released, "retrieved_at": retrieved,
                                 "available_at": retrieved, "source_ref": "SYNTHETIC_TEST_ONLY",
                                 "vintage_id": f"{series}-{day}", "raw_sha256": SHA,
                                 "pit_grade": "UNKNOWN" if retrieved_after else "VERIFIED",
                                 "vintage_kind": "UNKNOWN" if retrieved_after else "FIRST_RELEASE"})
    for month, value in ((date(2025, 11, 30), 20), (date(2025, 12, 31), 15)):
        released = _stamp(date(2026, 1, 1), 10)
        retrieved = _stamp(date(2026, 1, 1), 11)
        observations.append({"series": "WGC:GLOBAL_OFFICIAL_NET_PURCHASES", "unit": "TONNES",
                             "measurement_regime": "WGC_GLOBAL_OFFICIAL_MONTHLY_TONNES_MONTH_END_DATE_LABEL_UTC",
                             "observed_on": month.isoformat(), "value": value,
                             "released_at": released, "retrieved_at": retrieved, "available_at": retrieved,
                             "source_ref": "SYNTHETIC_TEST_ONLY", "vintage_id": f"WGC-{month}",
                             "raw_sha256": SHA, "pit_grade": "VERIFIED", "vintage_kind": "FIRST_RELEASE"})
    return {"price_quality": {"status": "SHFE_AUDITED", "audit_ref": "SYNTHETIC_TEST_ASSUMPTION_ONLY"},
            "exchange_sessions": [day.isoformat() for day in dates],
            "exchange_calendar_ref": "SYNTHETIC_TEST_CALENDAR_ONLY",
            "bars": bars, "observations": observations}


class GoldAuStrategyTests(unittest.TestCase):
    def test_roll_needs_two_leader_days_and_chain_ignores_contract_basis(self):
        dataset = GoldAuDataset(fixture(100))
        path = build_decision_path(dataset)
        self.assertEqual(path[80].contract, "au2712")
        self.assertEqual(path[81].contract, "au2802")
        self.assertEqual(path[81].reason, "TWO_DAY_OI_LEADER_ROLL")
        self.assertLess(path[81].close_index / path[80].close_index - 1, 0.001)

    def test_strict_capture_timing_blocks_historical_backfill(self):
        payload = fixture(50, retrieved_after=True)
        last = sorted({row["date"] for row in payload["bars"]})[-1]
        strict = evaluate_signal(payload, last, pit_mode="strict")
        reconstructed = evaluate_signal(payload, last, pit_mode="reconstructed")
        self.assertFalse(strict["entry"])
        self.assertTrue(reconstructed["entry"])

    def test_0830_next_session_needs_no_current_day_bar(self):
        payload = fixture(274)
        last = max(date.fromisoformat(row["date"]) for row in payload["bars"])
        following = last + timedelta(days=1)
        while following.weekday() >= 5:
            following += timedelta(days=1)
        payload["exchange_sessions"].append(following.isoformat())
        dataset = GoldAuDataset(payload)
        self.assertNotIn(following, dataset.rows)
        signal = evaluate_signal(dataset, following.isoformat(), pit_mode="strict")
        self.assertEqual(signal["as_of"], datetime.combine(following, datetime.min.time(), SHANGHAI)
                         .replace(hour=8, minute=30).astimezone(timezone.utc).isoformat())
        self.assertTrue(signal["entry"])
        self.assertTrue(signal["actionable_entry"])

    def test_strict_calendar_gap_breaks_required_price_and_atr_chain(self):
        payload = fixture(300)
        days = sorted({row["date"] for row in payload["bars"]})
        missing = days[-10]
        payload["bars"] = [row for row in payload["bars"] if row["date"] != missing]
        dataset = GoldAuDataset(payload)
        self.assertIn(date.fromisoformat(missing), dataset.dates)
        signal = evaluate_signal(dataset, days[-1], pit_mode="strict")
        self.assertFalse(signal["actionable_entry"])
        self.assertEqual(signal["reason"], "INSUFFICIENT_PRICE_HISTORY")
        report = run_backtest(dataset, pit_mode="strict")
        self.assertEqual(report["status"], "UNRESOLVED_DATA")
        self.assertIn(missing, report["missing_official_session_bar_days"])

    def test_40_day_breakout_never_compares_across_calendar_gap(self):
        payload = fixture(100)
        days = sorted({row["date"] for row in payload["bars"]})
        missing = days[50]
        payload["bars"] = [row for row in payload["bars"] if row["date"] != missing]
        signal = evaluate_signal(payload, days[75], pit_mode="reconstructed",
                                 breakout_lookback=40)
        self.assertEqual(signal["reason"], "INSUFFICIENT_PRICE_HISTORY")
        self.assertFalse(signal["entry"])

    def test_adverse_usd_vetoes_favorable_real_yield(self):
        payload = fixture(50)
        date_rank = {day: i for i, day in enumerate(sorted({row["observed_on"] for row in payload["observations"]
                                                           if row["series"] == "FED:H10:DTWEXBGS"}))}
        for row in payload["observations"]:
            if row["series"] == "FED:H10:DTWEXBGS":
                row["value"] = 100 + date_rank[row["observed_on"]] * 0.1
        dataset = GoldAuDataset(payload)
        last = dataset.dates[-1]
        gate = macro_gate(dataset, datetime.combine(last, datetime.min.time(), SHANGHAI).replace(hour=8, minute=30).astimezone(timezone.utc))
        self.assertFalse(gate["pass"])
        self.assertEqual(gate["reason"], "MACRO_ADVERSE")

    def test_risk_budget_can_block_every_one_lot_signal(self):
        report = run_backtest(fixture(70, wide_range=True), pit_mode="reconstructed")
        self.assertGreater(report["candidate_entries"], 0)
        self.assertGreater(report["risk_blocked_entries"], 0)
        self.assertEqual(report["completed_trades"], 0)
        self.assertFalse(report["investment_effectiveness_proven"])

    def test_paper_counterfactual_exits_and_never_claims_validation(self):
        report = run_backtest(fixture(90), pit_mode="reconstructed")
        self.assertGreater(report["completed_trades"], 0)
        self.assertTrue(any(row["exit_reason"] == "MAX_HOLD" for row in report["trades"]))
        self.assertEqual(report["status"], "EXPLORATORY_NOT_VALIDATED")
        self.assertFalse(report["broker_order_authorized"])
        self.assertFalse(report["fills_use_daily_open_proxy"])
        self.assertTrue(report["stops_use_daily_low_proxy"])
        self.assertGreater(report["buy_hold_chained_index_gross_return_pct"], 0)
        self.assertEqual(len(report["historical_blocks"]), 3)
        self.assertIsNotNone(report["buy_hold_one_lot_after_costs"]["net_pnl_cny"])

    def test_stop_precedes_ambiguous_morning_max_hold_exit(self):
        payload = fixture(90)
        for row in payload["bars"]:
            if row["contract"] == "au2712" and row["date"] == "2026-03-03":
                row["low"] = 1000  # Night low; post-entry-window low remains above stop.
        report = run_backtest(payload, pit_mode="reconstructed")
        self.assertEqual(report["trades"][0]["exit_reason"], "STOP_TOUCH")
        self.assertLess(report["trades"][0]["net_pnl_cny"], 0)
        self.assertTrue(report["stops_use_daily_low_proxy"])
        self.assertIn("STOP_FIRST", report["stop_vs_morning_exit_order_assumption"])

    def test_soft_exit_includes_immediately_prior_close_and_executes_next_session(self):
        def changed(yesterday_close: float) -> dict:
            payload = fixture(90)
            for row in payload["bars"]:
                if row["contract"] != "au2712":
                    continue
                if row["date"] == "2026-02-06":
                    row["close"], row["low"], row["post_entry_low"] = 1003.5, 1003.3, 1003.3
                if row["date"] == "2026-02-09":
                    row["close"] = yesterday_close
                    row["low"] = row["post_entry_low"] = yesterday_close - 0.2
            return run_backtest(payload, pit_mode="reconstructed")

        self.assertNotEqual(changed(1003.7)["trades"][0]["exit_reason"], "TEN_DAY_CLOSE_LOW")
        exit_trade = changed(1003.4)["trades"][0]
        self.assertEqual(exit_trade["exit_reason"], "TEN_DAY_CLOSE_LOW")
        self.assertEqual(exit_trade["exit_date"], "2026-02-10")

    def test_every_macro_filtered_breakout_counts_later_rise_or_censor(self):
        payload = fixture(330)
        for row in payload["observations"]:
            if row["series"] in {"FRED:DFII10", "FED:H10:DTWEXBGS"}:
                row["value"] = 4.0 if row["series"] == "FRED:DFII10" else 100.0
        report = run_backtest(payload, pit_mode="strict", variant="full", config={
            "historical_blocks": [["2019-07-01", "2022-12-31"],
                                  ["2023-01-01", "2024-12-31"],
                                  ["2025-01-01", "2027-12-31"]]})
        summary = report["macro_filtered_opportunity_summary"]
        self.assertGreater(summary["price_breakouts_filtered_by_macro"], 0)
        self.assertEqual(summary["price_breakouts_filtered_by_macro"], len(report["macro_filtered_opportunities"]))
        self.assertEqual(summary["horizons"]["5"]["later_positive_count"],
                         summary["horizons"]["5"]["observed_count"])
        self.assertGreater(summary["horizons"]["20"]["censored_count"], 0)
        self.assertFalse(summary["opportunities_are_independent_entries"])
        self.assertEqual(report["historical_blocks"][2]["macro_filtered_opportunity_summary"], summary)

    def test_missing_macro_observations_also_count_as_filtered_opportunities(self):
        payload = fixture(300)
        payload["observations"] = [row for row in payload["observations"]
                                   if row["series"] != "FED:H10:DTWEXBGS"]
        report = run_backtest(payload, pit_mode="strict", variant="full")
        summary = report["macro_filtered_opportunity_summary"]
        self.assertGreater(summary["price_breakouts_filtered_by_macro"], 0)
        self.assertGreater(summary["reason_counts"]["MISSING_FED:H10:DTWEXBGS_OBSERVATIONS"], 0)
        self.assertEqual(summary["horizons"]["5"]["observed_count"]
                         + summary["horizons"]["5"]["censored_count"],
                         summary["price_breakouts_filtered_by_macro"])

    def test_bad_vendor_ohlc_is_study_only_and_strict_signal_blocks(self):
        for status in ("UNVERIFIED_VENDOR_OHLC", "OFFICIAL_DAILY_OHLC_PIT_UNVERIFIED"):
            payload = fixture(60)
            payload["price_quality"] = {"status": status, "audit_ref": "SYNTHETIC_AUDIT"}
            last = sorted({row["date"] for row in payload["bars"]})[-1]
            self.assertEqual(evaluate_signal(payload, last, pit_mode="strict")["reason"], "UNVERIFIED_PRICE_QUALITY")
            report = run_backtest(payload, pit_mode="reconstructed")
            self.assertEqual(report["status"], "DATA_QUALITY_BLOCKED_EXPLORATORY")
            self.assertFalse(report["investment_effectiveness_proven"])

    def test_assumed_margin_and_fees_block_strict_order_risk(self):
        payload = fixture(300)
        for row in payload["bars"]:
            row["execution_cost_grade"] = "ASSUMPTION"
        report = run_backtest(payload, pit_mode="strict")
        self.assertGreater(report["candidate_entries"], 0)
        self.assertEqual(report["completed_trades"], 0)
        self.assertTrue(any(row.get("execution_decision") == "UNVERIFIED_PREDECISION_COST_AND_MARGIN"
                            for row in report["decisions"]))

    def test_no_continuous_contract_or_missing_provenance(self):
        payload = fixture(3)
        payload["bars"][0]["contract"] = "au888"
        with self.assertRaisesRegex(ValueError, "dated AU"):
            GoldAuDataset(payload)
        payload = fixture(3)
        del payload["bars"][0]["raw_sha256"]
        with self.assertRaisesRegex(ValueError, "raw_sha256"):
            GoldAuDataset(payload)
        payload = fixture(3)
        payload["bars"][0]["date"] = "2026-01-04"  # Sunday vendor anomaly
        with self.assertRaisesRegex(ValueError, "weekend-labelled"):
            GoldAuDataset(payload)

    def test_config_is_frozen_with_runtime_defaults(self):
        from pathlib import Path
        from yuanli_invest.gold_au_strategy import DEFAULT_CONFIG
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root / "config/ymq_gold2/gold_au_strategy.v1.json").read_text())
        for key, value in DEFAULT_CONFIG.items():
            self.assertEqual(config[key], value, key)


if __name__ == "__main__":
    unittest.main()
