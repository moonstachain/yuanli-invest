#!/usr/bin/env python3
"""Offline historical research closure; never connects to a broker.

Reverify retained SHFE source bytes, fresh FRED CSV bytes and latest values;
run frozen variants, original three blocks and four sensitivity cells. Output
is exclusive, exploratory and explicitly separates hypothetical release time
from genuine capture provenance. No network or credentials are used here.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import date, datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
if sys.version_info < (3, 12):
    raise SystemExit("Python >= 3.12 required")
from scripts.gold_au_shfe_daily_capture import normalize_daily
from yuanli_invest import gold_au_strategy as engine
from yuanli_invest.gold_au_historical_replay import HistoricalResearchDataset, run_historical_scope, scoped_engine
from yuanli_invest.gold_au_official_calendar import load_calendar_receipt
from yuanli_invest.gold_macro_capture import MacroSpec, normalize_raw


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as target:
        json.dump(value, target, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False,
                  default=lambda item: item.isoformat() if isinstance(item, (date, datetime)) else str(item))
        target.write("\n")
    path.chmod(0o600)


def audited_dataset(input_path: Path, shfe_path: Path, macro_path: Path, calendar_path: Path) -> tuple[dict, dict]:
    payload = json.loads(input_path.read_bytes())
    shfe = json.loads(shfe_path.read_bytes())
    if payload["price_quality"].get("retained_bar_source_coverage") != "ALL_OFFICIAL_SHFE_DAILY":
        raise ValueError("FULL_OFFICIAL_RETAINED_PRICE_COVERAGE_REQUIRED")
    by_day: dict[str, dict] = {}
    for row in payload["bars"]:
        by_day.setdefault(row["date"], {})[row["contract"]] = row
    reports = 0
    checked_bars = 0
    verified_raw_files = []
    for report in shfe["reports"]:
        path = Path(report["raw_file"])
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != report["raw_sha256"]:
            raise ValueError("OFFICIAL_RAW_HASH_MISMATCH")
        rows = normalize_daily(raw, report["date"])["bars"]
        actual = by_day[report["date"]]
        if set(actual) != {row["contract"] for row in rows}:
            raise ValueError("OFFICIAL_CONTRACT_COVERAGE_MISMATCH")
        for row in rows:
            retained = actual[row["contract"]]
            if retained["source_provider_id"] != "shfe_official_daily" or retained["raw_sha256"] != report["raw_sha256"]:
                raise ValueError("OFFICIAL_SOURCE_IDENTITY_MISMATCH")
            for field in ("open", "high", "low", "close", "volume", "open_interest"):
                if float(retained[field]) != float(row[field]):
                    raise ValueError("OFFICIAL_RETAINED_VALUE_MISMATCH")
            checked_bars += 1
        reports += 1
        verified_raw_files.append({"date": report["date"], "raw_file": str(path), "sha256": report["raw_sha256"]})
    if reports != len(by_day):
        raise ValueError("OFFICIAL_DAY_COVERAGE_MISMATCH")
    macro = json.loads(macro_path.read_bytes())
    if macro.get("status") != "CAPTURED" or macro.get("historical_release_time_verified") is not False:
        raise ValueError("COMPLETE_LATEST_VINTAGE_MACRO_CAPTURE_REQUIRED")
    old = {(row["series"], row["observed_on"]): row["value"] for row in payload["observations"]}
    observations = []
    macro_sources = []
    changes = []
    additions = []
    for capture in macro["captures"]:
        raw_path = Path(capture["raw_file"])
        raw = raw_path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != capture["raw_sha256"]:
            raise ValueError("MACRO_RAW_HASH_MISMATCH")
        spec = MacroSpec(capture["provider_series"], date.fromisoformat(macro["interval"][0]), date.fromisoformat(macro["interval"][1]))
        rechecked = normalize_raw(raw, spec, captured_at=datetime.fromisoformat(capture["captured_at"]))
        if rechecked["observations"] != capture["observations"]:
            raise ValueError("MACRO_RENORMALIZATION_MISMATCH")
        for original in capture["observations"]:
            row = dict(original)
            if row["series"] == "FRED:DTWEXBGS":
                row["source_series"] = row["series"]
                row["source_measurement_regime"] = row["measurement_regime"]
                row["series"] = "FED:H10:DTWEXBGS"
                row["measurement_regime"] = "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY"
                row["mapping_ref"] = str(ROOT / "config/ymq_gold2/fred_h10_mapping.v1.json")
                row["mapping_sha256"] = _sha(Path(row["mapping_ref"]))
            key = row["series"], row["observed_on"]
            if key not in old:
                additions.append({"series": row["series"], "date": row["observed_on"], "value": row["value"]})
            elif old[key] != row["value"]:
                changes.append({"series": row["series"], "date": row["observed_on"], "prior_capture_value": old[key], "fresh_capture_value": row["value"]})
            observations.append(row)
        macro_sources.append({"url": spec.url(), "sha256": capture["raw_sha256"], "raw_file": str(raw_path),
                              "captured_at": capture["captured_at"], "numeric_observations": len(capture["observations"])})
    payload["observations"] = observations
    payload["purpose"] = "RETROSPECTIVE_RESEARCH_ONLY_LATEST_VINTAGE_PUBLICATION_DELAY_DIAGNOSTIC"
    calendar = load_calendar_receipt(calendar_path)
    last = max(by_day)
    expected = [day for day in calendar["sessions"] if "2025-01-01" <= day <= last]
    supplied = sorted(day for day in by_day if day >= "2025-01-01")
    if supplied != expected:
        raise ValueError("OFFICIAL_2025_2026_CALENDAR_MISMATCH")
    return payload, {"status": "RAW_OFFICIAL_VALUES_REVERIFIED_HISTORICAL_PIT_NOT_PROVEN",
                     "official_report_days": reports, "official_contract_bars": checked_bars,
                     "first_official_bar": min(by_day), "last_official_bar": last,
                     "official_2025_2026_sessions": len(expected), "sessions_per_year": dict(Counter(day[:4] for day in expected)),
                     "2025_2026_missing_sessions": [], "pre2025_calendar": "INFERRED_FROM_RETAINED_OFFICIAL_REPORT_DATES_NOT_INDEPENDENT_CALENDAR",
                     "calendar_receipt": str(calendar_path), "calendar_sha256": _sha(calendar_path),
                     "macro_sources": macro_sources, "macro_changed_values_since_prior_capture": changes,
                     "new_macro_observations": additions, "wgc_historical_rows": 0,
                     "publication_instants_witnessed": False, "first_release_vintages_complete": False,
                     "official_raw_inventory": verified_raw_files,
                     "inputs": {str(path): _sha(path) for path in (input_path, shfe_path, macro_path, calendar_path)},
                     "orders_sent": 0, "broker_action_authorized": False}


def _hold_metrics(dataset: engine.GoldAuDataset, start: date, end: date, ticks: int, config: dict) -> dict:
    path = [p for p in engine.build_decision_path(dataset, pit_mode="reconstructed", config=config)
            if start <= p.decision_date <= end and p.decision_date in dataset.rows]
    equity0 = config["paper_equity_cny"]
    cash, peak, maximum_dd, entry = float(equity0), float(equity0), 0.0, 0.0
    held, entry_day = None, None
    for point in path:
        day, contract = point.decision_date, point.contract
        if contract is None:
            continue
        bar = dataset.rows[day].get(contract)
        if bar is None:
            continue
        if held is not None and contract != held:
            previous = dataset.rows[day][held]
            fee = previous["fee_close_today_per_lot_cny"] if entry_day == day else previous["fee_close_yesterday_per_lot_cny"]
            cash += (engine._fill_price(previous, "SELL", ticks, config) - entry) * config["multiplier_grams_per_lot"] - fee
            held = None
        if held is None:
            entry = engine._fill_price(bar, "BUY", ticks, config)
            cash -= bar["fee_open_per_lot_cny"]
            held, entry_day = contract, day
        marked = cash + (dataset.rows[day][held]["close"] - entry) * config["multiplier_grams_per_lot"]
        peak = max(peak, marked)
        maximum_dd = max(maximum_dd, 1 - marked / peak)
    original = engine._buy_hold_baseline(dataset, path, ticks, config)
    if held is not None:
        last = path[-1].decision_date
        final = dataset.rows[last][held]
        fee = final["fee_close_today_per_lot_cny"] if entry_day == last else final["fee_close_yesterday_per_lot_cny"]
        cash += (final["close"] - ticks * config["tick_size_cny_per_gram"] - entry) * config["multiplier_grams_per_lot"] - fee
        maximum_dd = max(maximum_dd, 1 - cash / peak)
    if abs((cash - equity0) - original["net_pnl_cny"]) > 0.00001:
        raise ValueError("HOLD_CURVE_TERMINAL_DOES_NOT_MATCH_FROZEN_BENCHMARK")
    return {**original, "return_on_5000000_equity_pct": (cash / equity0 - 1) * 100,
            "maximum_marked_drawdown_pct": maximum_dd * 100,
            "semantics": "ONE_LOT_ALWAYS_LONG_SAME_ROLL_AFTER_COSTS_FINAL_CLOSE_PROXY_NO_STRATEGY_RISK_OR_STOP"}


def _summary(run: dict, scope: str, config: dict) -> dict:
    decisions = run["decisions"]
    return {"scope": scope, "start": run["research_scope_start"], "end": run["research_scope_end"],
            "publication_model": run["publication_model"], "pit_mode": run["pit_mode"], "variant": run["variant"],
            "breakout": run["breakout_lookback"], "macro_observations": run["macro_lookback"],
            "ticks_per_side": run["slippage_ticks_per_side"], "status": run["status"],
            "entries": sum(event["event"] == "OPEN" for event in run["events"]), "closed_trades": len(run["trades"]),
            "candidate_signal_days": sum(bool(row["entry"]) for row in decisions),
            "risk_blocked_candidate_days": sum(row.get("execution_decision") == "ONE_LOT_EXCEEDS_RISK_BUDGET" for row in decisions),
            "marked_pnl_cny": run["final_equity_cny"] - config["paper_equity_cny"],
            "realized_pnl_cny": run["net_realized_pnl_cny"],
            "return_on_5000000_equity_pct": (run["final_equity_cny"] / config["paper_equity_cny"] - 1) * 100,
            "maximum_drawdown_pct": run["maximum_drawdown_pct"], "terminal_position": run["terminal_position"],
            "fees_cny": sum(event.get("fee_cny", 0) for event in run["events"]),
            "stop_gap_excess_loss_cny": sum(trade.get("gap_loss_over_planned_stop_cny", 0) for trade in run["trades"]),
            "macro_filtered_opportunities": run["macro_filtered_opportunity_summary"],
            "decision_reason_counts": dict(Counter(row.get("reason", "UNKNOWN") for row in decisions))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--shfe-manifest", required=True, type=Path)
    parser.add_argument("--macro-manifest", required=True, type=Path)
    parser.add_argument("--calendar", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError("Choose a new immutable output directory")
    args.output_dir.mkdir(parents=True, mode=0o700)
    config_path = ROOT / "config/ymq_gold2/gold_au_strategy.v1.json"
    config = json.loads(config_path.read_bytes())
    payload, audit = audited_dataset(args.input, args.shfe_manifest, args.macro_manifest, args.calendar)
    _write(args.output_dir / "dataset.json", payload)
    _write(args.output_dir / "data-audit.json", audit)
    last = date.fromisoformat(audit["last_official_bar"])
    scopes = [("all_continuous", date(2019, 7, 1), last),
              ("block_2019_2022", date(2019, 7, 1), date(2022, 12, 31)),
              ("block_2023_2024", date(2023, 1, 1), date(2024, 12, 31)),
              ("block_2025_latest", date(2025, 1, 1), last),
              ("2026_ytd_reset", date(2026, 1, 1), last)]
    summaries, detailed, holds, risks, visibility = [], [], [], [], []
    selections = [(variant, 20, 20) for variant in ("price_only", "real_rate_only", "usd_only", "full")]
    selections += [("full", breakout, macro) for breakout in (20, 40) for macro in (10, 20) if (breakout, macro) != (20, 20)]
    for publication in ("OBSERVATION_DATE_LEAKY_REFERENCE", "SCHEDULE_DELAY_LATEST_VINTAGE_EXPLORATORY"):
        dataset = HistoricalResearchDataset(payload, publication_model=publication)
        for scope, start, end in scopes:
            for variant, breakout, macro in selections:
                for ticks in (2, 5):
                    run = run_historical_scope(dataset, start=start, end=end, variant=variant,
                                               breakout_lookback=breakout, macro_lookback=macro,
                                               slippage_ticks=ticks, pit_mode="reconstructed", config=config)
                    run["scope"] = scope
                    summaries.append(_summary(run, scope, config))
                    detailed.append(run)
            print(publication, scope, "complete", flush=True)
        # Unit granularity audit is independent of capital performance and counts
        # overlapping signal dates, never pretending they are independent trades.
        risk_path = engine.build_decision_path(dataset, pit_mode="reconstructed", config=config)
        for point_index, point in enumerate(risk_path):
            if point.atr20 is None or point.decision_date not in dataset.rows:
                continue
            signal = engine._signal_for_point(dataset, risk_path, point_index,
                                             pit_mode="reconstructed", variant="full", breakout_lookback=20, macro_lookback=20, config=config)
            budget = engine.risk_budget(dataset, point, config["paper_equity_cny"], pit_mode="reconstructed", config=config)
            planned = 2 * point.atr20 * 1000 + 160
            risks.append({"publication_model": publication, "date": point.decision_date.isoformat(),
                          "atr20_cny_per_gram": point.atr20, "high_volatility": point.high_volatility,
                          "one_lot_plan_loss_2ticks_cny": planned, "frozen_risk_budget_cny": budget["amount_cny"],
                          "one_lot_feasible": planned <= budget["amount_cny"], "full_signal": bool(signal["entry"]),
                          "minimum_equity_for_this_one_lot_under_same_risk_multipliers_cny": config["paper_equity_cny"] * planned / budget["amount_cny"]})
        for day in dataset.dates[1:]:
            as_of = engine._decision(day)
            for count in (10, 20):
                selections_at_cutoff = []
                for series in ("FRED:DFII10", "FED:H10:DTWEXBGS"):
                    selected = dataset.latest_n(series, count, as_of, "reconstructed", config["measurement_regimes"][series])
                    endpoints = [selected[0], selected[-1]] if selected else []
                    fields = ("observed_on", "value", "released_at", "retrieved_at", "available_at", "raw_sha256", "vintage_id", "pit_grade", "vintage_kind")
                    selections_at_cutoff.append({"series": series, "selected_count": len(selected), "requested_count": count,
                                                 "endpoints": [{field: row[field] for field in fields} |
                                                               {"hypothetical_publication_at": row.get("hypothetical_publication_at")}
                                                               for row in endpoints]})
                visibility.append({"publication_model": publication, "decision_day": day.isoformat(),
                                   "decision_at": as_of.isoformat(), "macro_lookback": count,
                                   "selection": selections_at_cutoff, "strict_historical_data_admissible": False})
    strict_dataset = HistoricalResearchDataset(payload)
    for variant in ("price_only", "real_rate_only", "usd_only", "full"):
        for ticks in (2, 5):
            run = run_historical_scope(strict_dataset, start=date(2019, 7, 1), end=last, variant=variant,
                                       slippage_ticks=ticks, pit_mode="strict", config=config)
            run["scope"] = "all_continuous_strict_data_rejection"
            summaries.append(_summary(run, run["scope"], config)); detailed.append(run)
    hold_dataset = HistoricalResearchDataset(payload)
    for scope, start, end in scopes:
        for ticks in (2, 5):
            holds.append({"scope": scope, "ticks_per_side": ticks, **_hold_metrics(hold_dataset, start, end, ticks, config)})
    risk_summary = []
    for publication in ("OBSERVATION_DATE_LEAKY_REFERENCE", "SCHEDULE_DELAY_LATEST_VINTAGE_EXPLORATORY"):
        for year in sorted({row["date"][:4] for row in risks}):
            rows = [row for row in risks if row["publication_model"] == publication and row["date"].startswith(year)]
            signals = [row for row in rows if row["full_signal"]]
            risk_summary.append({"publication_model": publication, "year": year, "atr_valid_days": len(rows),
                                 "one_lot_infeasible_days": sum(not row["one_lot_feasible"] for row in rows),
                                 "one_lot_infeasible_pct": 100 * sum(not row["one_lot_feasible"] for row in rows) / len(rows),
                                 "full_signal_days": len(signals), "infeasible_full_signal_days": sum(not row["one_lot_feasible"] for row in signals),
                                 "latest_day": rows[-1]})
    _, adapter = scoped_engine()
    report = {"schema_version": "gold-au-historical-closure.v1", "created_at": datetime.now(timezone.utc).isoformat(),
              "purpose": "EXPLORATORY_DIAGNOSTIC_NOT_TRADING_EDGE_PROOF", "strategy_config_sha256": _sha(config_path),
              "strategy_parameters_modified": False, "scope_adapter": adapter, "runs": summaries,
              "one_lot_hold_benchmarks": holds, "risk_granularity_by_year": risk_summary,
              "cash_baseline": {"pnl_cny": 0, "return_pct": 0, "interest_assumed": False},
              "strict_zero_semantics": "DATA_INADMISSIBLE_NOT_ZERO_STRATEGY_RETURN",
              "publication_delay_limitations": "REGULAR_FEDERAL_HOLIDAYS_AND_15_MIN_BUFFER_ASSUMED; UNEXPECTED_CLOSURES/FRED_DISTRIBUTION_AND_VINTAGE_REVISIONS_UNPROVEN",
              "execution_limitations": "DAILY_OPEN_MAY_BE_PREDECISION_NIGHT_SESSION; DAILY_LOW_MAY_PRECEDE_ENTRY; NO_0900_0905_MINUTE_OR_STOP_PATH",
              "investment_effectiveness_proven": False, "orders_sent": 0}
    _write(args.output_dir / "comparison.json", report)
    with (args.output_dir / "comparison.csv").open("x", newline="", encoding="utf-8-sig") as stream:
        fields = [key for key in summaries[0] if key not in {"decision_reason_counts", "macro_filtered_opportunities", "terminal_position"}]
        writer = csv.DictWriter(stream, fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(summaries)
    _write(args.output_dir / "risk-granularity-daily.json", risks)
    with gzip.open(args.output_dir / "detailed-runs.json.gz", "xt", encoding="utf-8") as stream:
        json.dump({"runs": detailed}, stream, ensure_ascii=False, allow_nan=False, default=str)
    with gzip.open(args.output_dir / "macro-visibility-audit.json.gz", "xt", encoding="utf-8") as stream:
        json.dump(visibility, stream, ensure_ascii=False, allow_nan=False)
    print(json.dumps({"status": "EXPLORATORY_COMPLETE", "runs": len(summaries), "official_bar_end": last.isoformat(), "orders_sent": 0}))


if __name__ == "__main__":
    main()
