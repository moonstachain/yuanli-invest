"""Descriptive AU/rates/dollar association from a captured research dataset.

This deliberately joins retrospective *date labels*, not historical releases.
Its estimates cannot establish causality, tradable timing, or investment alpha.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, time
import math
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from .gold_au_strategy import GoldAuDataset, build_decision_path
from .gold_pit import AttributionRow, fit_contemporaneous_attribution


SHANGHAI = ZoneInfo("Asia/Shanghai")
GOLD_ID = "GOLD2:AU_DATED_SAME_CONTRACT_CHAIN"
RATE_ID = "FRED:DFII10"
DOLLAR_ID = "FED:H10:DTWEXBGS"
REGIME = "SHFE_AU_DATED_CHAIN_X_FRED_DFII10_X_FRED_DTWEXBGS_DATE_LABEL"
RATE_REGIME = "FRED_DFII10_DAILY_10Y_TIPS_DATE_LABEL_NY"
DOLLAR_REGIME = "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY"
DOLLAR_SOURCE_REGIME = "FRED_DTWEXBGS_DISTRIBUTED_H10_BROAD_DOLLAR_DATE_LABEL_NY"


def _macro_dates(dataset: GoldAuDataset, series: str) -> dict[date, float]:
    result: dict[date, float] = {}
    for row in dataset.observations[series]:
        if row["pit_grade"] != "UNKNOWN" or row["vintage_kind"] != "UNKNOWN":
            raise ValueError("attribution accepts only captured latest-vintage exploratory macro rows")
        if row.get("measurement_regime") != (RATE_REGIME if series == RATE_ID else DOLLAR_REGIME):
            raise ValueError("macro measurement regime mismatch")
        if series == DOLLAR_ID and (row.get("source_series") != "FRED:DTWEXBGS"
                                    or row.get("provider_series") != "DTWEXBGS"
                                    or row.get("source_measurement_regime") != DOLLAR_SOURCE_REGIME
                                    or not row.get("mapping_sha256")):
            raise ValueError("H10 strategy alias has no explicit FRED distributor mapping")
        day = date.fromisoformat(row["observed_on"])
        if day in result:
            raise ValueError(f"duplicate {series} date label: {day}")
        result[day] = row["value"]
    return result


def build_aligned_rows(dataset: GoldAuDataset) -> tuple[list[AttributionRow], dict[str, int]]:
    """Use the frozen dated-contract selection and same-contract daily returns.

    On a roll day, the *new* contract's two adjacent closes form the return;
    the level jump between old and new contracts is never treated as profit.
    Macro values must exist on both exact Chinese AU trading-date labels.
    """
    rates = _macro_dates(dataset, RATE_ID)
    dollars = _macro_dates(dataset, DOLLAR_ID)
    path = build_decision_path(dataset, pit_mode="reconstructed")
    counts = {"candidate_au_pairs": 0, "skipped_no_same_contract_pair": 0,
              "skipped_missing_macro_date": 0, "aligned_pairs": 0, "roll_pairs": 0}
    aligned: list[AttributionRow] = []
    for earlier, later in zip(path, path[1:]):
        previous_day, day = earlier.prior_date, later.prior_date
        if day <= previous_day or day not in dataset.rows:
            continue
        counts["candidate_au_pairs"] += 1
        contract = later.contract
        if contract is None:
            counts["skipped_no_same_contract_pair"] += 1
            continue
        old_bar = dataset.rows.get(previous_day, {}).get(contract)
        new_bar = dataset.rows.get(day, {}).get(contract)
        if old_bar is None or new_bar is None or later.close_index is None:
            counts["skipped_no_same_contract_pair"] += 1
            continue
        if earlier.contract != contract:
            counts["roll_pairs"] += 1
        if previous_day not in rates or day not in rates or previous_day not in dollars or day not in dollars:
            counts["skipped_missing_macro_date"] += 1
            continue
        aligned.append(AttributionRow(
            observation_at=datetime.combine(day, time(15), SHANGHAI),
            gold_log_return=math.log(new_bar["close"] / old_bar["close"]),
            real_yield_delta_bp=(rates[day] - rates[previous_day]) * 100,
            broad_dollar_log_return=math.log(dollars[day] / dollars[previous_day]),
            gold_series_id=GOLD_ID, real_yield_series_id=RATE_ID,
            dollar_series_id=DOLLAR_ID, measurement_regime=REGIME,
        ))
    counts["aligned_pairs"] = len(aligned)
    return aligned, counts


def _fit(rows: list[AttributionRow]) -> dict[str, Any]:
    result = asdict(fit_contemporaneous_attribution(rows))
    for key in ("window_start", "window_end"):
        if result[key] is not None:
            result[key] = result[key].isoformat()
    baseline = result["baseline_rmse"]
    full = result["rates_and_dollar_rmse"]
    result["in_sample_rmse_reduction_vs_mean_pct"] = (
        (baseline - full) / baseline * 100 if baseline and full is not None else None
    )
    return result


def build_report(payload: Mapping[str, Any], *, dataset_sha256: str,
                 assembly_report: Mapping[str, Any] | None = None,
                 assembly_report_sha256: str | None = None) -> dict[str, Any]:
    if payload.get("schema_version") != "gold-au-reconstructed-dataset.v1":
        raise ValueError("requires the assembled retrospective AU dataset")
    if payload.get("authority") != "RETROSPECTIVE_EXPLORATORY_RESEARCH_ONLY" or payload.get("action_authority") != "none":
        raise ValueError("attribution input must have no action authority")
    quality_status = payload.get("price_quality", {}).get("status")
    if quality_status not in {"UNVERIFIED_VENDOR_OHLC", "OFFICIAL_DAILY_OHLC_PIT_UNVERIFIED"}:
        raise ValueError("this report is pinned to an unverified retrospective capture regime")
    if len(dataset_sha256) != 64:
        raise ValueError("dataset SHA256 required")
    dataset = GoldAuDataset(payload)
    if quality_status == "OFFICIAL_DAILY_OHLC_PIT_UNVERIFIED" and any(
        bar.get("source_provider_id") != "shfe_official_daily"
        for contracts in dataset.rows.values() for bar in contracts.values()
    ):
        raise ValueError("official-only quality label conflicts with retained bar provenance")
    if any(bar["pit_grade"] != "UNKNOWN" or bar["vintage_kind"] != "UNKNOWN"
           for contract_bars in dataset.rows.values() for bar in contract_bars.values()):
        raise ValueError("unexpected historical bar PIT assertion")
    rows, alignment = build_aligned_rows(dataset)
    blocks = {
        "2019-07_to_2022-12": [r for r in rows if r.observation_at.year <= 2022],
        "2023-01_to_2024-12": [r for r in rows if 2023 <= r.observation_at.year <= 2024],
        "2025-01_to_capture": [r for r in rows if r.observation_at.year >= 2025],
    }
    source_shas = {}
    if assembly_report is not None:
        if assembly_report.get("status") != "DATA_QUALITY_BLOCKED":
            raise ValueError("assembly report status incompatible")
        source_shas = {key: assembly_report.get(key) for key in (
            "au_manifest_sha256", "macro_manifest_sha256", "shfe_manifest_sha256",
            "h10_mapping_sha256", "audit_report_sha256")}
    return {
        "schema_version": "gold-au-historical-attribution.v1",
        "status": "EXPLORATORY_DATA_QUALITY_BLOCKED",
        "authority": "DESCRIPTIVE_RESEARCH_ONLY", "action_authority": "none",
        "input_dataset_sha256": dataset_sha256,
        "assembly_report_sha256": assembly_report_sha256,
        "source_sha256": source_shas,
        "price_quality": dict(dataset.price_quality),
        "pit_grade": "UNKNOWN", "vintage_kind": "UNKNOWN",
        "alignment": {**alignment, "join": "EXACT_CALENDAR_DATE_LABEL_BOTH_ENDPOINTS_NO_FORWARD_FILL",
                      "return_basis": "SELECTED_NEW_CONTRACT_CLOSE_T_OVER_SAME_CONTRACT_CLOSE_T_MINUS_1",
                      "calendar_basis": "CHINA_AU_TRADING_DATE_AND_NEW_YORK_OBSERVATION_DATE_LABEL"},
        "series": {"gold": GOLD_ID, "real_yield": RATE_ID,
                   "broad_dollar": DOLLAR_ID, "broad_dollar_source": "FRED:DTWEXBGS",
                   "measurement_regime": REGIME},
        "full_sample": _fit(rows),
        "fixed_blocks": {name: _fit(block_rows) for name, block_rows in blocks.items()},
        "local_gold_spread": {"status": "MISSING", "usd_cny": "MISSING",
                              "london_usd_gold": "MISSING",
                              "reason": "NO_VERIFIED_PERMITTED_HISTORICAL_SAME_TIME_INPUTS"},
        "interpretation_limits": [
            "Contemporaneous date-label association only; no causal or forecast claim.",
            "H10/DFII10 are latest-vintage captures, not verified historical first releases.",
            ("All retained AU daily OHLC bars use captured SHFE official reports; "
             "this does not verify historical release timing, intraday execution path or costs."
             if quality_status == "OFFICIAL_DAILY_OHLC_PIT_UNVERIFIED" else
             "Retained AU OHLC includes vendor bars with unresolved sample mismatches."),
            "SHFE report HTTP-error dates were excluded; the source calendar was not independently certified.",
            "Different exchange time zones and publication lags prohibit strict PIT use.",
            "Unexplained price variation is not identified as a credit contribution.",
            "In-sample RMSE comparisons are not out-of-sample strategy evidence.",
        ],
    }
