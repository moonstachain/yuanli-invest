"""Point-in-time gold evidence and descriptive attribution invariants."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime
import unittest

from yuanli_invest.gold_pit import (
    AttributionRow,
    GoldObservation,
    fit_contemporaneous_attribution,
    latest_n_as_of,
    select_as_of,
)


def at(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def observation(**overrides: object) -> GoldObservation:
    fields: dict[str, object] = {
        "series_id": "FRED:DFII10",
        "measurement_regime": "TEN_YEAR_TIPS_H15",
        "unit": "percent_per_annum",
        "value": 1.5,
        "observation_at": at("2026-09-21T16:00:00-04:00"),
        "released_at": at("2026-09-21T16:15:00-04:00"),
        "retrieved_at": at("2026-09-21T16:20:00-04:00"),
        "available_at": at("2026-09-21T16:21:00-04:00"),
        "vintage_id": "2026-09-21T16:15:00-04:00",
        "source_sha256": "a" * 64,
        "pit_grade": "VERIFIED",
    }
    fields.update(overrides)
    return GoldObservation(**fields)  # type: ignore[arg-type]


class GoldPITTests(unittest.TestCase):
    def test_observation_is_immutable_and_utc_normalized(self) -> None:
        row = observation()
        self.assertEqual(row.observation_at, at("2026-09-21T20:00:00Z"))
        with self.assertRaises(FrozenInstanceError):
            row.value = 2.0  # type: ignore[misc]

    def test_timestamps_and_source_identity_are_fail_closed(self) -> None:
        invalid = (
            {"observation_at": datetime(2026, 9, 21)},
            {"released_at": at("2026-09-21T15:59:00-04:00")},
            {"retrieved_at": at("2026-09-21T16:14:00-04:00")},
            {"available_at": at("2026-09-21T16:19:00-04:00")},
            {"source_sha256": "not-a-digest"},
            {"series_id": "real_rate"},
            {"pit_grade": "ASSUMED"},
            {"value": float("nan")},
        )
        for changes in invalid:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                observation(**changes)

    def test_delayed_release_and_retrieval_cannot_be_backdated(self) -> None:
        h10 = observation(
            series_id="FED:H10:DTWEXBGS",
            measurement_regime="H10_BROAD_DOLLAR_WEEKLY_RELEASE",
            unit="index_points",
            observation_at=at("2026-09-17T17:00:00-04:00"),
            released_at=at("2026-09-24T16:15:00-04:00"),
            retrieved_at=at("2026-09-24T16:20:00-04:00"),
            available_at=at("2026-09-25T08:00:00+08:00"),
        )
        request = dict(series_id=h10.series_id, unit=h10.unit, measurement_regime=h10.measurement_regime)
        self.assertIsNone(select_as_of([h10], as_of=at("2026-09-24T08:30:00+08:00"), **request))
        self.assertIsNone(select_as_of([h10], as_of=at("2026-09-24T17:00:00-04:00"), **request))
        self.assertEqual(select_as_of([h10], as_of=at("2026-09-25T08:30:00+08:00"), **request), h10)
        with self.assertRaises(ValueError):
            select_as_of([h10], as_of=datetime(2026, 9, 25, 8, 30), **request)

    def test_month_end_is_not_the_wgc_publication_time(self) -> None:
        wgc = observation(
            series_id="WGC:GLOBAL_OFFICIAL_NET_PURCHASES",
            measurement_regime="WGC_MONTHLY_FIRST_CAPTURE",
            unit="metric_tonnes",
            value=-2.5,
            observation_at=at("2026-07-31T23:59:59Z"),
            released_at=at("2026-09-08T10:00:00+01:00"),
            retrieved_at=at("2026-09-08T10:05:00+01:00"),
            available_at=at("2026-09-08T10:10:00+01:00"),
        )
        request = dict(series_id=wgc.series_id, unit=wgc.unit, measurement_regime=wgc.measurement_regime)
        self.assertIsNone(select_as_of([wgc], as_of=at("2026-08-31T08:30:00+08:00"), **request))
        self.assertEqual(select_as_of([wgc], as_of=at("2026-09-09T08:30:00+08:00"), **request), wgc)

    def test_exact_series_regime_unit_and_grade_no_aliasing(self) -> None:
        fred = observation()
        request = dict(as_of=at("2026-09-22T08:30:00+08:00"), unit=fred.unit)
        self.assertIsNone(select_as_of([fred], series_id="WIND:G1147404", measurement_regime=fred.measurement_regime, **request))
        self.assertIsNone(select_as_of([fred], series_id=fred.series_id, measurement_regime="WIND_LONG_END_REAL", **request))
        self.assertIsNone(select_as_of([fred], series_id=fred.series_id, measurement_regime=fred.measurement_regime, unit="basis_points", as_of=request["as_of"]))
        self.assertIsNone(select_as_of([replace(fred, pit_grade="UNKNOWN")], series_id=fred.series_id, measurement_regime=fred.measurement_regime, **request))
        self.assertIsNone(select_as_of([fred], series_id="WIND:M0000271", measurement_regime=fred.measurement_regime, **request))

    def test_revision_is_used_only_after_it_is_available(self) -> None:
        original = observation()
        revision = replace(
            original,
            value=1.6,
            released_at=at("2026-09-23T16:15:00-04:00"),
            retrieved_at=at("2026-09-23T16:20:00-04:00"),
            available_at=at("2026-09-23T16:21:00-04:00"),
            vintage_id="2026-09-23T16:15:00-04:00",
            source_sha256="b" * 64,
        )
        request = dict(series_id=original.series_id, unit=original.unit, measurement_regime=original.measurement_regime)
        self.assertEqual(select_as_of([revision, original], as_of=at("2026-09-22T08:30:00+08:00"), **request), original)
        self.assertEqual(select_as_of([revision, original], as_of=at("2026-09-24T08:30:00+08:00"), **request), revision)
        with self.assertRaises(ValueError):
            select_as_of([original, replace(original, value=2)], as_of=at("2026-09-22T08:30:00+08:00"), **request)

    def test_latest_n_returns_distinct_observations_or_unknown(self) -> None:
        older = observation(
            observation_at=at("2026-09-18T16:00:00-04:00"),
            released_at=at("2026-09-18T16:15:00-04:00"),
            retrieved_at=at("2026-09-18T16:20:00-04:00"),
            available_at=at("2026-09-18T16:21:00-04:00"),
        )
        newest = observation()
        request = dict(as_of=at("2026-09-22T08:30:00+08:00"), series_id=newest.series_id, unit=newest.unit, measurement_regime=newest.measurement_regime)
        self.assertEqual(latest_n_as_of([newest, older], n=2, **request), (older, newest))
        self.assertEqual(latest_n_as_of([newest, older], n=20, **request), ())


def attribution_row(i: int, *, rate_series: str = "FRED:DFII10", dollar_series: str = "FED:H10:DTWEXBGS") -> AttributionRow:
    rate = float((i % 7) - 3)
    dollar = ((i * 11) % 13 - 6) / 100.0
    noise = ((i * 17) % 19 - 9) / 10000.0
    return AttributionRow(
        observation_at=at(f"2025-{i // 28 + 1:02d}-{i % 28 + 1:02d}T16:00:00Z"),
        gold_log_return=0.002 - 0.0004 * rate - 0.35 * dollar + noise,
        real_yield_delta_bp=rate,
        broad_dollar_log_return=dollar,
        gold_series_id="LBMA:USD_GOLD_PM",
        real_yield_series_id=rate_series,
        dollar_series_id=dollar_series,
        measurement_regime="PUBLIC_USD_GOLD_TIPS_H10",
    )


class GoldAttributionTests(unittest.TestCase):
    def test_recomputed_models_are_descriptive_only(self) -> None:
        result = fit_contemporaneous_attribution([attribution_row(i) for i in range(40)])
        self.assertEqual(result.status, "ESTIMATED_CONTEMPORANEOUS")
        self.assertEqual(result.purpose, "CONTEMPORANEOUS_ATTRIBUTION")
        self.assertFalse(result.forecast_ready)
        self.assertLess(abs(result.real_yield_coefficient + 0.0004), 0.0001)
        self.assertLess(abs(result.dollar_coefficient + 0.35), 0.02)
        self.assertGreaterEqual(result.baseline_rmse, result.rates_only_rmse)
        self.assertGreaterEqual(result.rates_only_rmse, result.rates_and_dollar_rmse)

    def test_insufficient_or_singular_panel_is_unknown(self) -> None:
        rows = [attribution_row(i) for i in range(40)]
        self.assertEqual(fit_contemporaneous_attribution(rows[:5]).status, "UNKNOWN_INSUFFICIENT_ROWS")
        flat = [replace(row, broad_dollar_log_return=0.0) for row in rows]
        self.assertEqual(fit_contemporaneous_attribution(flat).status, "UNKNOWN_RANK_DEFICIENT")

    def test_wind_and_public_regimes_cannot_share_coefficients(self) -> None:
        rows = [attribution_row(i) for i in range(40)]
        rows[-1] = replace(rows[-1], real_yield_series_id="WIND:G1147404")
        with self.assertRaises(ValueError):
            fit_contemporaneous_attribution(rows)


if __name__ == "__main__":
    unittest.main()
