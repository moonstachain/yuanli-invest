"""Synthetic date-join and roll checks; fixtures are not market evidence."""

from __future__ import annotations

from datetime import date, datetime, timedelta
import math
import unittest
from zoneinfo import ZoneInfo

from yuanli_invest.gold_au_attribution import build_aligned_rows, build_report
from yuanli_invest.gold_au_strategy import GoldAuDataset


SHA = "a" * 64
SZ = ZoneInfo("Asia/Shanghai")
NY = ZoneInfo("America/New_York")


def fixture() -> dict:
    days = []
    day = date(2026, 1, 5)
    while len(days) < 55:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    bars, observations = [], []
    for i, day in enumerate(days):
        release = datetime(day.year, day.month, day.day, 18, tzinfo=SZ).isoformat()
        for contract, basis, oi in (("au2712", 0, 1000 if i < 30 else 800),
                                    ("au2802", 80, 900 if i < 30 else 1200)):
            close = 500 + basis + i * 0.2 + math.sin(i / 3)
            bars.append({"date": day.isoformat(), "contract": contract,
                         "open": close, "high": close + 1, "low": close - 1,
                         "close": close, "open_interest": oi,
                         "margin_per_lot_cny": 100000,
                         "fee_open_per_lot_cny": 40, "fee_close_today_per_lot_cny": 40,
                         "fee_close_yesterday_per_lot_cny": 40, "execution_cost_grade": "ASSUMPTION",
                         "first_published_at": release, "retrieved_at": release, "available_at": release,
                         "source_ref": "TEST_ONLY", "vintage_id": f"{contract}-{day}",
                         "raw_sha256": SHA, "pit_grade": "UNKNOWN", "vintage_kind": "UNKNOWN"})
        for series, unit, regime, value in (
            ("FRED:DFII10", "PERCENT", "FRED_DFII10_DAILY_10Y_TIPS_DATE_LABEL_NY", 2 + math.sin(i / 4) * 0.08),
            ("FED:H10:DTWEXBGS", "INDEX", "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY", 110 + math.cos(i / 5)),
        ):
            if series == "FED:H10:DTWEXBGS" and i == 10:
                continue
            stamp = datetime(day.year, day.month, day.day, 18, tzinfo=NY).isoformat()
            row = {"series": series, "unit": unit, "observed_on": day.isoformat(),
                   "value": value, "measurement_regime": regime,
                   "released_at": stamp, "retrieved_at": stamp, "available_at": stamp,
                   "source_ref": "TEST_ONLY", "vintage_id": f"{series}-{day}",
                   "raw_sha256": SHA, "pit_grade": "UNKNOWN", "vintage_kind": "UNKNOWN"}
            if series == "FED:H10:DTWEXBGS":
                row.update(source_series="FRED:DTWEXBGS", provider_series="DTWEXBGS",
                           mapping_sha256=SHA,
                           source_measurement_regime="FRED_DTWEXBGS_DISTRIBUTED_H10_BROAD_DOLLAR_DATE_LABEL_NY")
            observations.append(row)
    return {"schema_version": "gold-au-reconstructed-dataset.v1",
            "authority": "RETROSPECTIVE_EXPLORATORY_RESEARCH_ONLY", "action_authority": "none",
            "price_quality": {"status": "UNVERIFIED_VENDOR_OHLC", "audit_ref": "TEST_ONLY"},
            "bars": bars, "observations": observations}


class AttributionReportTests(unittest.TestCase):
    def test_same_contract_roll_return_excludes_basis_jump_and_missing_macro_days(self) -> None:
        rows, counts = build_aligned_rows(GoldAuDataset(fixture()))
        self.assertGreater(counts["roll_pairs"], 0)
        self.assertEqual(counts["skipped_missing_macro_date"], 2)
        self.assertGreater(len(rows), 30)
        self.assertLess(max(abs(row.gold_log_return) for row in rows), 0.01)
        self.assertEqual(len({row.observation_at for row in rows}), len(rows))

    def test_descriptive_report_has_no_trade_authority_or_credit_residual(self) -> None:
        report = build_report(fixture(), dataset_sha256=SHA)
        self.assertEqual(report["status"], "EXPLORATORY_DATA_QUALITY_BLOCKED")
        self.assertEqual(report["action_authority"], "none")
        self.assertFalse(report["full_sample"]["forecast_ready"])
        self.assertEqual(report["local_gold_spread"]["status"], "MISSING")
        self.assertNotIn("credit_residual", str(report))
        self.assertEqual(report["alignment"]["join"], "EXACT_CALENDAR_DATE_LABEL_BOTH_ENDPOINTS_NO_FORWARD_FILL")

    def test_h10_alias_without_original_identity_fails(self) -> None:
        payload = fixture()
        next(row for row in payload["observations"] if row["series"] == "FED:H10:DTWEXBGS").pop("source_series")
        with self.assertRaisesRegex(ValueError, "explicit FRED distributor mapping"):
            build_report(payload, dataset_sha256=SHA)

    def test_rejects_any_action_authority(self) -> None:
        payload = fixture()
        payload["action_authority"] = "broker_paper"
        with self.assertRaisesRegex(ValueError, "no action authority"):
            build_report(payload, dataset_sha256=SHA)

    def test_all_official_price_quality_does_not_claim_vendor_contamination_or_pit(self) -> None:
        payload = fixture()
        payload["price_quality"] = {
            "status": "OFFICIAL_DAILY_OHLC_PIT_UNVERIFIED", "audit_ref": "TEST_ONLY",
            "retained_bar_source_coverage": "ALL_OFFICIAL_SHFE_DAILY",
            "official_retained_bars": len(payload["bars"]), "vendor_retained_bars": 0,
            "shfe_http_error_dates_excluded": 20,
        }
        for bar in payload["bars"]:
            bar["source_provider_id"] = "shfe_official_daily"
        report = build_report(payload, dataset_sha256=SHA)
        self.assertEqual(report["status"], "EXPLORATORY_DATA_QUALITY_BLOCKED")
        self.assertEqual(report["price_quality"]["status"], "OFFICIAL_DAILY_OHLC_PIT_UNVERIFIED")
        limits = " ".join(report["interpretation_limits"])
        self.assertIn("all retained au daily ohlc bars use captured shfe official reports", limits.lower())
        self.assertNotIn("unverified vendor periods", limits.lower())
        self.assertIn("not verified historical first releases", limits)
        payload["bars"][0]["source_provider_id"] = "youquant_history"
        with self.assertRaisesRegex(ValueError, "official-only quality label conflicts"):
            build_report(payload, dataset_sha256=SHA)


if __name__ == "__main__":
    unittest.main()
