"""Frozen, offline AU long/flat candidate; no broker or order authority.

Input rows are explicit, timestamped JSON records. `strict` decisions require
release, retrieval and availability before the 08:30 decision. `reconstructed`
is useful for historical sensitivity work but is always labelled exploratory:
it may contain values downloaded or revised after the historical decision.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from statistics import mean
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from .gold_pit import GoldObservation, latest_n_as_of
from .time import instant

SHANGHAI = ZoneInfo("Asia/Shanghai")
AU_CONTRACT = re.compile(r"^au(\d{2})(0[1-9]|1[0-2])$")
MACRO_SERIES = {"FRED:DFII10": "PERCENT", "FED:H10:DTWEXBGS": "INDEX"}
WGC_SERIES = "WGC:GLOBAL_OFFICIAL_NET_PURCHASES"

DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": "gold-au-strategy.v1",
    "measurement_regimes": {
        "FRED:DFII10": "FRED_DFII10_DAILY_10Y_TIPS_DATE_LABEL_NY",
        "FED:H10:DTWEXBGS": "FED_H10_BROAD_DOLLAR_DAILY_DATE_LABEL_NY",
        WGC_SERIES: "WGC_GLOBAL_OFFICIAL_MONTHLY_TONNES_MONTH_END_DATE_LABEL_UTC",
    },
    "tick_size_cny_per_gram": 0.02,
    "multiplier_grams_per_lot": 1000,
    "minimum_delivery_months_ahead": 2,
    "roll_leader_consecutive_days": 2,
    "breakout_lookback": 20,
    "macro_observations": 20,
    "real_yield_favorable_bp": -10,
    "real_yield_adverse_bp": 10,
    "broad_usd_favorable_pct": -0.5,
    "broad_usd_adverse_pct": 0.5,
    "macro_max_age_calendar_days": 14,
    "macro_max_window_calendar_days": 60,
    "wgc_max_age_calendar_days": 120,
    "wgc_max_report_gap_calendar_days": 65,
    "minimum_hold_trading_days_for_soft_exit": 5,
    "soft_exit_low_lookback": 10,
    "maximum_hold_trading_days": 20,
    "atr_lookback": 20,
    "stop_atr_multiple": 2,
    "volatility_reference_days": 252,
    "volatility_percentile": 90,
    "paper_equity_cny": 5_000_000,
    "risk_fraction_per_trade": 0.005,
    "unknown_or_nonpositive_wgc_risk_multiplier": 0.5,
    "high_or_unknown_volatility_risk_multiplier": 0.5,
    "maximum_lots": 1,
    "maximum_margin_fraction": 0.3,
    "freeze_new_entries_drawdown_fraction": 0.05,
    "paper_order_slippage_budget_ticks_per_side": 5,
    "historical_blocks": [
        ["2019-07-01", "2022-12-31"],
        ["2023-01-01", "2024-12-31"],
        ["2025-01-01", "2026-09-25"],
    ],
}


def _number(value: Any, field: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{field} must be finite numeric")
    result = float(value)
    if positive and result <= 0:
        raise ValueError(f"{field} must be positive")
    return result


def _day(value: Any, field: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO date") from exc


def _timestamp(value: Any, field: str) -> datetime:
    try:
        return instant(value)
    except ValueError as exc:
        raise ValueError(f"{field}: {exc}") from exc


def _decision(day: date) -> datetime:
    return datetime.combine(day, time(8, 30), SHANGHAI).astimezone(timezone.utc)


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def _provenance(row: Mapping[str, Any], label: str, release_field: str) -> None:
    for field in ("source_ref", "vintage_id", "raw_sha256"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError(f"{label}.{field} required")
    digest = row["raw_sha256"]
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError(f"{label}.raw_sha256 must be lowercase SHA256")
    released = _timestamp(row.get(release_field), f"{label}.{release_field}")
    retrieved = _timestamp(row.get("retrieved_at"), f"{label}.retrieved_at")
    available = _timestamp(row.get("available_at"), f"{label}.available_at")
    if available < released:
        raise ValueError(f"{label}.available_at precedes release")
    if retrieved < released:
        raise ValueError(f"{label}.retrieved_at precedes release")
    if available < retrieved:
        raise ValueError(f"{label}.available_at precedes retrieval")


def _visible(row: Mapping[str, Any], as_of: datetime, mode: str, release_field: str) -> bool:
    if mode == "reconstructed":
        # Historical observations captured only now can be studied, but never
        # claimed as an as-of-known strategy or used by strict live decisions.
        return True
    if _timestamp(row[release_field], release_field) > as_of:
        return False
    return (
        row.get("pit_grade") in {"VERIFIED", "CONSERVATIVE"}
        and row.get("vintage_kind") in {"FIRST_RELEASE", "REVISION"}
        and
        _timestamp(row["retrieved_at"], "retrieved_at") <= as_of
        and _timestamp(row["available_at"], "available_at") <= as_of
    )


def _delivery_month(contract: str) -> int:
    match = AU_CONTRACT.fullmatch(contract)
    if not match:
        raise ValueError(f"dated AU contract required, got {contract!r}")
    return (2000 + int(match.group(1))) * 12 + int(match.group(2)) - 1


def _eligible(contract: str, trading_day: date, cfg: Mapping[str, Any]) -> bool:
    current_month = trading_day.year * 12 + trading_day.month - 1
    return _delivery_month(contract) >= current_month + cfg["minimum_delivery_months_ahead"]


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    location = (len(ordered) - 1) * percentile / 100
    lower = math.floor(location)
    upper = math.ceil(location)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (location - lower)


@dataclass(frozen=True)
class DecisionPoint:
    decision_date: date
    prior_date: date
    contract: str | None
    close_index: float | None
    low_index: float | None
    atr20: float | None
    high_volatility: bool | None
    reason: str


class GoldAuDataset:
    """Validated in-memory rows. Source verification is external to this class."""

    def __init__(self, payload: Mapping[str, Any]):
        if not isinstance(payload, Mapping):
            raise ValueError("dataset must be an object")
        price_quality = payload.get("price_quality")
        if not isinstance(price_quality, Mapping) or price_quality.get("status") not in {
            "SHFE_AUDITED", "LIVE_SOURCE_CHECKED", "UNVERIFIED_VENDOR_OHLC",
            "OFFICIAL_DAILY_OHLC_PIT_UNVERIFIED", "SYNTHETIC_FIXTURE"
        } or not isinstance(price_quality.get("audit_ref"), str) or not price_quality["audit_ref"]:
            raise ValueError("price_quality.status and audit_ref required")
        self.price_quality = dict(price_quality)
        self.purpose = payload.get("purpose")
        self.execution_cost_status = payload.get("execution_cost_status")
        session_days = payload.get("exchange_sessions")
        calendar_ref = payload.get("exchange_calendar_ref")
        if session_days is not None:
            if not isinstance(session_days, list) or not isinstance(calendar_ref, str) or not calendar_ref:
                raise ValueError("exchange_sessions requires exchange_calendar_ref")
            self.exchange_sessions = {_day(value, "exchange_sessions[]") for value in session_days}
            if len(self.exchange_sessions) != len(session_days):
                raise ValueError("duplicate exchange session")
        else:
            self.exchange_sessions = None
        self.exchange_calendar_ref = calendar_ref
        self.rows: dict[date, dict[str, dict[str, Any]]] = {}
        self.observations: dict[str, list[dict[str, Any]]] = {**{s: [] for s in MACRO_SERIES}, WGC_SERIES: []}
        self.pit_observations: list[GoldObservation] = []
        self.by_vintage: dict[tuple[str, date, str], dict[str, Any]] = {}
        bars = payload.get("bars")
        observations = payload.get("observations")
        if not isinstance(bars, list) or not isinstance(observations, list):
            raise ValueError("bars and observations arrays required")
        for raw in bars:
            if not isinstance(raw, dict):
                raise ValueError("bar must be object")
            row = dict(raw)
            day = _day(row.get("date"), "bar.date")
            if day.weekday() >= 5:
                raise ValueError("weekend-labelled AU daily bar must be quarantined before strategy input")
            if self.exchange_sessions is not None and day not in self.exchange_sessions:
                raise ValueError("AU bar date absent from supplied exchange session calendar")
            contract = row.get("contract")
            if not isinstance(contract, str):
                raise ValueError("bar.contract required")
            _delivery_month(contract)
            _provenance(row, "bar", "first_published_at")
            if row.get("pit_grade") not in {"VERIFIED", "CONSERVATIVE", "UNKNOWN"}:
                raise ValueError("bar.pit_grade required")
            if row.get("vintage_kind") not in {"FIRST_RELEASE", "REVISION", "UNKNOWN"}:
                raise ValueError("bar.vintage_kind required")
            if row.get("execution_cost_grade") not in {"VERIFIED", "CONSERVATIVE", "ASSUMPTION"}:
                raise ValueError("bar.execution_cost_grade required")
            session_close = datetime.combine(day, time(15, 0), SHANGHAI).astimezone(timezone.utc)
            if _timestamp(row["first_published_at"], "first_published_at") < session_close:
                raise ValueError("complete daily bar cannot predate the 15:00 session close")
            for field in ("open", "high", "low", "close", "open_interest", "margin_per_lot_cny"):
                row[field] = _number(row.get(field), f"bar.{field}", positive=field not in {"open_interest"})
            for field in ("fee_open_per_lot_cny", "fee_close_today_per_lot_cny", "fee_close_yesterday_per_lot_cny"):
                row[field] = _number(row.get(field), f"bar.{field}")
                if row[field] < 0:
                    raise ValueError("fees cannot be negative")
            if row["open_interest"] < 0 or not row["low"] <= row["open"] <= row["high"] or not row["low"] <= row["close"] <= row["high"]:
                raise ValueError("invalid OHLC/open interest")
            for field in ("entry_window_price", "post_entry_low"):
                if field in row and row[field] is not None:
                    row[field] = _number(row[field], f"bar.{field}", positive=True)
            if contract in self.rows.setdefault(day, {}):
                raise ValueError(f"duplicate bar {day} {contract}")
            self.rows[day][contract] = row
        for raw in observations:
            if not isinstance(raw, dict):
                raise ValueError("observation must be object")
            row = dict(raw)
            series = row.get("series")
            if series not in self.observations:
                raise ValueError(f"unsupported series {series!r}")
            expected_unit = MACRO_SERIES.get(series, "TONNES")
            if row.get("unit") != expected_unit:
                raise ValueError(f"{series} unit must be {expected_unit}")
            _day(row.get("observed_on"), "observation.observed_on")
            _provenance(row, "observation", "released_at")
            if row.get("pit_grade") not in {"VERIFIED", "CONSERVATIVE", "UNKNOWN"}:
                raise ValueError("observation.pit_grade required")
            if row.get("vintage_kind") not in {"FIRST_RELEASE", "REVISION", "UNKNOWN"}:
                raise ValueError("observation.vintage_kind required")
            if not isinstance(row.get("measurement_regime"), str) or not row["measurement_regime"]:
                raise ValueError("observation.measurement_regime required")
            row["value"] = _number(row.get("value"), "observation.value")
            if series == "FED:H10:DTWEXBGS" and row["value"] <= 0:
                raise ValueError("broad dollar index must be positive")
            observation_date = _day(row["observed_on"], "observed_on")
            label_zone = timezone.utc if series == WGC_SERIES else ZoneInfo("America/New_York")
            observation_at = datetime.combine(observation_date, time.min, label_zone)
            pit = GoldObservation(
                series_id=series, measurement_regime=row["measurement_regime"], unit=row["unit"],
                value=row["value"], observation_at=observation_at, released_at=row["released_at"],
                retrieved_at=row["retrieved_at"], available_at=row["available_at"],
                vintage_id=row["vintage_id"], source_sha256=row["raw_sha256"], pit_grade=row["pit_grade"],
            )
            key = (series, observation_date, row["vintage_id"])
            if key in self.by_vintage:
                raise ValueError("duplicate series/vintage identity")
            self.by_vintage[key] = row
            self.pit_observations.append(pit)
            self.observations[series].append(row)
        self.dates = sorted(self.rows)
        if self.dates and self.exchange_sessions is not None:
            # The official calendar, rather than the set of rows supplied by a
            # vendor, defines the decision sequence. An omitted session must
            # break the return/ATR chain instead of silently joining two bars.
            first_bar, last_bar = self.dates[0], self.dates[-1]
            forthcoming = sorted(day for day in self.exchange_sessions if day > last_bar)
            end = forthcoming[0] if forthcoming else last_bar
            self.dates = sorted(day for day in self.exchange_sessions if first_bar <= day <= end)

    def bar(self, day: date, contract: str, as_of: datetime, mode: str) -> dict[str, Any] | None:
        row = self.rows.get(day, {}).get(contract)
        if row is None or not _visible(row, as_of, mode, "first_published_at"):
            return None
        return row

    def bars_for_day(self, day: date, as_of: datetime, mode: str) -> dict[str, dict[str, Any]]:
        return {contract: row for contract, row in self.rows.get(day, {}).items()
                if _visible(row, as_of, mode, "first_published_at")}

    def latest_n(self, series: str, count: int, as_of: datetime, mode: str,
                 measurement_regime: str) -> list[dict[str, Any]]:
        if mode == "strict":
            eligible = [row for row in self.pit_observations
                        if self.by_vintage[(row.series_id, row.observation_at.astimezone(
                            timezone.utc if row.series_id == WGC_SERIES else ZoneInfo("America/New_York")
                        ).date(), row.vintage_id)]["vintage_kind"] in {"FIRST_RELEASE", "REVISION"}]
            chosen = latest_n_as_of(eligible, as_of=as_of, series_id=series,
                                    unit=MACRO_SERIES.get(series, "TONNES"),
                                    measurement_regime=measurement_regime, n=count,
                                    allowed_pit_grades=frozenset({"VERIFIED", "CONSERVATIVE"}))
            label_zone = timezone.utc if series == WGC_SERIES else ZoneInfo("America/New_York")
            return [self.by_vintage[(series, row.observation_at.astimezone(label_zone).date(), row.vintage_id)]
                    for row in chosen]
        chosen: dict[date, dict[str, Any]] = {}
        for row in self.observations[series]:
            observed = _day(row["observed_on"], "observed_on")
            if (row["measurement_regime"] != measurement_regime or observed > as_of.astimezone(SHANGHAI).date()
                    or not _visible(row, as_of, mode, "released_at")):
                continue
            earlier = chosen.get(observed)
            if earlier is None or (_timestamp(row["released_at"], "released_at"), row["vintage_id"]) > (
                _timestamp(earlier["released_at"], "released_at"), earlier["vintage_id"]
            ):
                chosen[observed] = row
        return [chosen[d] for d in sorted(chosen)[-count:]]


def _choose_contract(dataset: GoldAuDataset, dates: list[date], i: int, previous: str | None,
                     mode: str, cfg: Mapping[str, Any], *,
                     knowledge_at: datetime | None = None) -> tuple[str | None, str]:
    decision_day = dates[i]
    as_of = knowledge_at if knowledge_at is not None else _decision(decision_day)
    prior = dates[i - 1]
    available = {c: b for c, b in dataset.bars_for_day(prior, as_of, mode).items()
                 if _eligible(c, decision_day, cfg)}
    if not available:
        return None, "NO_ELIGIBLE_VISIBLE_CONTRACT"
    leader = max(available, key=lambda c: (available[c]["open_interest"], c))
    if previous is None:
        return leader, "INITIAL_OI_LEADER"
    if previous not in available:
        return leader, "FORCED_ROLL_OR_MISSING_PRIOR_CONTRACT"
    if leader == previous:
        return previous, "KEEP_LEADER"
    if i < 2:
        return previous, "CHALLENGER_NOT_PERSISTENT"
    before = dates[i - 2]
    previous_bars = {c: b for c, b in dataset.bars_for_day(before, as_of, mode).items()
                     if _eligible(c, decision_day, cfg)}
    if not previous_bars:
        return previous, "CHALLENGER_NOT_PERSISTENT"
    leader_before = max(previous_bars, key=lambda c: (previous_bars[c]["open_interest"], c))
    if leader_before == leader:
        return leader, "TWO_DAY_OI_LEADER_ROLL"
    return previous, "CHALLENGER_NOT_PERSISTENT"


def build_decision_path(dataset: GoldAuDataset, *, pit_mode: str = "strict",
                        config: Mapping[str, Any] | None = None) -> list[DecisionPoint]:
    """Historical decisions, each using its own actual information cutoff."""
    return _build_price_path(dataset, pit_mode=pit_mode, config=config)


def build_current_snapshot_path(dataset: GoldAuDataset, *, as_of: datetime,
                                config: Mapping[str, Any] | None = None) -> list[DecisionPoint]:
    """Today's indicator history from bytes known by today's 08:30 cutoff.

    Earlier points are indicator inputs, NOT historical decision records. A
    previously downloaded completed bar need not have been downloaded on its
    observation day to be known today. Its real receipt times remain intact.
    Historical backtests must continue to use build_decision_path instead.
    """
    when = _timestamp(as_of, "as_of")
    day = when.astimezone(SHANGHAI).date()
    if when != _decision(day):
        raise ValueError("current snapshot cutoff must be exactly 08:30 Shanghai")
    if (dataset.purpose != "STRICT_0830_LIVE_SNAPSHOT_ONLY_NOT_HISTORICAL_BACKTEST"
            or dataset.price_quality.get("status") != "LIVE_SOURCE_CHECKED"
            or dataset.exchange_sessions is None or day not in dataset.exchange_sessions
            or not dataset.dates or dataset.dates[-1] != day
            or any(bar_day >= day for bar_day in dataset.rows)):
        raise ValueError("current snapshot requires checked prior bars and current official session")
    if dataset.execution_cost_status not in {"WITNESSED", "DEFERRED_TO_EXECUTION_GATE"}:
        raise ValueError("current snapshot requires explicit execution cost policy")
    # Replayers must reject the entire contaminated current information set,
    # rather than silently discard a future row that happens not to affect the
    # final indicator. Historical strict visibility retains its old semantics.
    for contracts in dataset.rows.values():
        for row in contracts.values():
            if any(_timestamp(row[field], field) > when for field in
                   ("first_published_at", "retrieved_at", "available_at")):
                raise ValueError("postdecision price input in current snapshot")
    for rows in dataset.observations.values():
        for row in rows:
            if (_day(row["observed_on"], "observed_on") > day or
                    any(_timestamp(row[field], field) > when for field in
                        ("released_at", "retrieved_at", "available_at"))):
                raise ValueError("postdecision macro input in current snapshot")
    return _build_price_path(dataset, pit_mode="strict", config=config, knowledge_at=when)


def _build_price_path(dataset: GoldAuDataset, *, pit_mode: str,
                      config: Mapping[str, Any] | None = None,
                      knowledge_at: datetime | None = None) -> list[DecisionPoint]:
    if pit_mode not in {"strict", "reconstructed"}:
        raise ValueError("pit_mode must be strict or reconstructed")
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    dates = dataset.dates
    path: list[DecisionPoint] = []
    selected: str | None = None
    index: float | None = None
    true_ranges: list[float] = []
    atr_history: list[float] = []
    for i in range(1, len(dates)):
        day, prior = dates[i], dates[i - 1]
        next_selected, reason = _choose_contract(dataset, dates, i, selected, pit_mode, cfg,
                                                 knowledge_at=knowledge_at)
        as_of = knowledge_at if knowledge_at is not None else _decision(day)
        current = dataset.bar(prior, next_selected, as_of, pit_mode) if next_selected else None
        previous = dataset.bar(dates[i - 2], next_selected, as_of, pit_mode) if next_selected and i >= 2 else None
        if current is None:
            index = None
            true_ranges.clear()
            atr_history.clear()
            path.append(DecisionPoint(day, prior, None, None, None, None, None, reason))
            selected = None
            continue
        if previous is None:
            # Seed only; no price return or ATR across an unobserved prior close.
            index = 100.0 if index is None else index
            true_ranges.clear()
            atr_history.clear()
            atr = None
        else:
            if index is None:
                index = 100.0
            index *= current["close"] / previous["close"]
            true_ranges.append(max(current["high"] - current["low"],
                                   abs(current["high"] - previous["close"]),
                                   abs(current["low"] - previous["close"])))
            length = int(cfg["atr_lookback"])
            atr = mean(true_ranges[-length:]) if len(true_ranges) >= length else None
        high_volatility = None
        reference_days = int(cfg["volatility_reference_days"])
        if atr is not None:
            if len(atr_history) >= reference_days:
                high_volatility = atr > _percentile(atr_history[-reference_days:], cfg["volatility_percentile"])
            atr_history.append(atr)
        low_index = index * current["low"] / current["close"] if index is not None else None
        path.append(DecisionPoint(day, prior, next_selected, index, low_index, atr, high_volatility, reason))
        selected = next_selected
    return path


def macro_gate(dataset: GoldAuDataset, as_of: datetime, *, pit_mode: str = "strict",
               lookback: int = 20, variant: str = "full", config: Mapping[str, Any] | None = None) -> dict[str, Any]:
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    if variant not in {"full", "price_only", "real_rate_only", "usd_only"}:
        raise ValueError("invalid strategy variant")
    if variant == "price_only":
        return {"pass": True, "reason": "PRICE_ONLY_BASELINE", "real_yield_delta_bp": None, "broad_usd_delta_pct": None}
    required = {"real_rate_only": ["FRED:DFII10"], "usd_only": ["FED:H10:DTWEXBGS"],
                "full": ["FRED:DFII10", "FED:H10:DTWEXBGS"]}[variant]
    changes: dict[str, float] = {}
    refs: dict[str, list[str]] = {}
    for series in required:
        rows = dataset.latest_n(series, lookback, as_of, pit_mode, cfg["measurement_regimes"][series])
        if len(rows) < lookback:
            return {"pass": False, "reason": f"MISSING_{series}_OBSERVATIONS", "evidence": refs}
        last_observed = _day(rows[-1]["observed_on"], "observed_on")
        first_observed = _day(rows[0]["observed_on"], "observed_on")
        if (as_of.astimezone(SHANGHAI).date() - last_observed).days > cfg["macro_max_age_calendar_days"]:
            return {"pass": False, "reason": f"STALE_{series}", "evidence": refs}
        if (last_observed - first_observed).days > cfg["macro_max_window_calendar_days"]:
            return {"pass": False, "reason": f"SPARSE_{series}_WINDOW", "evidence": refs}
        changes[series] = ((rows[-1]["value"] - rows[0]["value"]) * 100 if series == "FRED:DFII10"
                           else (rows[-1]["value"] / rows[0]["value"] - 1) * 100)
        refs[series] = [{"vintage_id": row["vintage_id"], "raw_sha256": row["raw_sha256"],
                         "released_at": row["released_at"], "available_at": row["available_at"]}
                        for row in (rows[0], rows[-1])]
    real = changes.get("FRED:DFII10")
    usd = changes.get("FED:H10:DTWEXBGS")
    adverse = (real is not None and real >= cfg["real_yield_adverse_bp"]) or (
        usd is not None and usd >= cfg["broad_usd_adverse_pct"])
    favorable = (real is not None and real <= cfg["real_yield_favorable_bp"]) or (
        usd is not None and usd <= cfg["broad_usd_favorable_pct"])
    return {"pass": favorable and not adverse,
            "reason": "MACRO_FAVORABLE" if favorable and not adverse else "MACRO_ADVERSE" if adverse else "MACRO_NOT_FAVORABLE",
            "real_yield_delta_bp": real, "broad_usd_delta_pct": usd, "evidence": refs}


def risk_budget(dataset: GoldAuDataset, point: DecisionPoint, equity: float, *,
                pit_mode: str = "strict", config: Mapping[str, Any] | None = None) -> dict[str, Any]:
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    as_of = _decision(point.decision_date)
    reports = dataset.latest_n(WGC_SERIES, 2, as_of, pit_mode, cfg["measurement_regimes"][WGC_SERIES])
    recent = (len(reports) == 2 and
              (as_of.astimezone(SHANGHAI).date() - _day(reports[-1]["observed_on"], "observed_on")).days
              <= cfg["wgc_max_age_calendar_days"] and
              (_day(reports[-1]["observed_on"], "observed_on") - _day(reports[0]["observed_on"], "observed_on")).days
              <= cfg["wgc_max_report_gap_calendar_days"])
    wgc_positive = recent and all(row["value"] > 0 for row in reports)
    credit_multiplier = 1.0 if wgc_positive else cfg["unknown_or_nonpositive_wgc_risk_multiplier"]
    volatility_multiplier = 1.0 if point.high_volatility is False else cfg["high_or_unknown_volatility_risk_multiplier"]
    return {"amount_cny": equity * cfg["risk_fraction_per_trade"] * credit_multiplier * volatility_multiplier,
            "wgc_positive_latest_two": wgc_positive,
            "wgc_vintages": [{"vintage_id": r["vintage_id"], "raw_sha256": r["raw_sha256"]}
                             for r in reports],
            "volatility_state": "HIGH" if point.high_volatility else "NORMAL" if point.high_volatility is False else "UNKNOWN",
            "credit_multiplier": credit_multiplier, "volatility_multiplier": volatility_multiplier}


def evaluate_signal(dataset: GoldAuDataset | Mapping[str, Any], as_of_date: str, *, pit_mode: str = "strict",
                    variant: str = "full", breakout_lookback: int = 20, macro_lookback: int = 20,
                    config: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(dataset, GoldAuDataset):
        dataset = GoldAuDataset(dataset)
    day = _day(as_of_date, "as_of_date")
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    path = [p for p in build_decision_path(dataset, pit_mode=pit_mode, config=cfg) if p.decision_date <= day]
    if not path or path[-1].decision_date != day:
        raise ValueError("decision day must be in supplied AU trading calendar")
    return _signal_for_point(dataset, path, len(path) - 1, pit_mode=pit_mode, variant=variant,
                             breakout_lookback=breakout_lookback, macro_lookback=macro_lookback, config=cfg)


def evaluate_current_snapshot_signal(dataset: GoldAuDataset | Mapping[str, Any], *,
                                     as_of: datetime) -> dict[str, Any]:
    """Frozen V1, today's strict information set only; never submits orders."""
    if not isinstance(dataset, GoldAuDataset):
        dataset = GoldAuDataset(dataset)
    when = _timestamp(as_of, "as_of")
    path = build_current_snapshot_path(dataset, as_of=when)
    if not path:
        raise ValueError("current snapshot has no price path")
    answer = _signal_for_point(dataset, path, len(path) - 1, pit_mode="strict", variant="full",
                               breakout_lookback=DEFAULT_CONFIG["breakout_lookback"],
                               macro_lookback=DEFAULT_CONFIG["macro_observations"], config=DEFAULT_CONFIG)
    had_signal_id = "signal_id" in answer
    answer.pop("evidence_sha256", None)
    answer.pop("signal_id", None)
    if dataset.execution_cost_status == "DEFERRED_TO_EXECUTION_GATE":
        # The shared dataset's legacy numeric cost slots are structural
        # placeholders, never a current account's terms or a sizing result.
        answer.pop("planned_one_lot_loss_cny", None)
        answer.pop("prior_margin_per_lot_cny", None)
        answer["actionable_entry"] = False
        answer["action_block"] = "AWAITING_EXECUTION_COST_VERIFICATION"
        answer["execution_cost_status"] = "DEFERRED_TO_EXECUTION_GATE"
        answer["stop_only_one_lot_loss_cny"] = (
            DEFAULT_CONFIG["stop_atr_multiple"] * path[-1].atr20
            * DEFAULT_CONFIG["multiplier_grams_per_lot"] if path[-1].atr20 is not None else None)
    answer["price_information_set"] = "CURRENT_DECISION_LOOKBACK_NOT_HISTORICAL_SIGNALS"
    answer["price_knowledge_at"] = when.isoformat()
    answer["evidence_sha256"] = _hash(answer)
    if had_signal_id:
        answer["signal_id"] = _hash({"strategy": DEFAULT_CONFIG["schema_version"], "as_of": answer["as_of"],
                                     "contract": answer["contract"], "evidence_sha256": answer["evidence_sha256"]})
    return answer


def replay_frozen_signal(dataset: GoldAuDataset | Mapping[str, Any], as_of_date: str) -> dict[str, Any]:
    """Exact frozen V1 replay for admission/registration, without authority.

    Only the explicitly tagged and fully validated current snapshot uses its
    current cutoff. Every other dataset retains historical strict PIT replay.
    Signature, independent anchoring and account checks belong to the callers.
    """
    if not isinstance(dataset, GoldAuDataset):
        dataset = GoldAuDataset(dataset)
    day = _day(as_of_date, "as_of_date")
    if dataset.purpose == "STRICT_0830_LIVE_SNAPSHOT_ONLY_NOT_HISTORICAL_BACKTEST":
        return evaluate_current_snapshot_signal(dataset, as_of=_decision(day))
    return evaluate_signal(dataset, day.isoformat(), pit_mode="strict", variant="full",
                           breakout_lookback=20, macro_lookback=20)


def _signal_for_point(dataset: GoldAuDataset, path: list[DecisionPoint], index: int, *, pit_mode: str,
                      variant: str, breakout_lookback: int, macro_lookback: int,
                      config: Mapping[str, Any]) -> dict[str, Any]:
    point = path[index]
    day = point.decision_date
    cfg = config
    answer: dict[str, Any] = {"as_of": _decision(day).isoformat(), "contract": point.contract,
                              "pit_mode": pit_mode, "entry": False, "reason": point.reason,
                              "price_index": point.close_index, "atr20_cny_per_gram": point.atr20,
                              "price_quality": dataset.price_quality,
                              "exchange_calendar_ref": dataset.exchange_calendar_ref,
                              "actionable_entry": False, "broker_order_authorized": False,
                              "requires_gateway_readback": True,
                              "valid_from": datetime.combine(day, time(9, 0), SHANGHAI).isoformat(),
                              "valid_until": datetime.combine(day, time(9, 5), SHANGHAI).isoformat()}
    deferred_execution_cost = dataset.execution_cost_status == "DEFERRED_TO_EXECUTION_GATE"
    if deferred_execution_cost:
        # Enforce this at the shared signal layer too: a mistaken grade upgrade
        # of structural numeric slots must never enable legacy replay/admission.
        answer["action_block"] = "AWAITING_EXECUTION_COST_VERIFICATION"
        answer["execution_cost_status"] = "DEFERRED_TO_EXECUTION_GATE"
        answer["stop_only_one_lot_loss_cny"] = (
            cfg["stop_atr_multiple"] * point.atr20 * cfg["multiplier_grams_per_lot"]
            if point.atr20 is not None else None)
    if point.contract:
        bar = dataset.bar(point.prior_date, point.contract, _decision(day), pit_mode)
        if bar:
            answer["prior_bar_evidence"] = {"date": point.prior_date.isoformat(),
                                             "vintage_id": bar["vintage_id"], "raw_sha256": bar["raw_sha256"],
                                             "retrieved_at": bar["retrieved_at"], "available_at": bar["available_at"]}
    prior_window = path[max(0, index - breakout_lookback):index]
    if (point.contract is None or point.close_index is None or point.atr20 is None
            or len(prior_window) < breakout_lookback
            or any(previous.close_index is None for previous in prior_window)):
        answer["reason"] = "INSUFFICIENT_PRICE_HISTORY"
        answer["evidence_sha256"] = _hash(answer)
        return answer
    if pit_mode == "strict" and dataset.price_quality["status"] not in {"SHFE_AUDITED", "LIVE_SOURCE_CHECKED"}:
        answer["reason"] = "UNVERIFIED_PRICE_QUALITY"
        answer["evidence_sha256"] = _hash(answer)
        return answer
    if pit_mode == "strict" and (dataset.exchange_sessions is None or day not in dataset.exchange_sessions):
        answer["reason"] = "UNVERIFIED_EXCHANGE_SESSION"
        answer["evidence_sha256"] = _hash(answer)
        return answer
    breakout = point.close_index > max(previous.close_index for previous in prior_window)
    answer["price_breakout"] = breakout
    if not breakout:
        answer["reason"] = "NO_BREAKOUT"
        answer["evidence_sha256"] = _hash(answer)
        return answer
    if pit_mode == "strict" and point.high_volatility is None:
        answer["reason"] = "INSUFFICIENT_CONTIGUOUS_ATR_REFERENCE"
        answer["evidence_sha256"] = _hash(answer)
        return answer
    macro = macro_gate(dataset, _decision(day), pit_mode=pit_mode, lookback=macro_lookback, variant=variant, config=cfg)
    answer["macro"] = macro
    if not macro["pass"]:
        answer["reason"] = macro["reason"]
        answer["evidence_sha256"] = _hash(answer)
        return answer
    answer["entry"] = True
    answer["reason"] = "CANDIDATE_ENTRY_SUBJECT_TO_RISK_AND_FILL"
    answer["risk"] = risk_budget(dataset, point, cfg["paper_equity_cny"], pit_mode=pit_mode, config=cfg)
    sizing_bar = dataset.bar(point.prior_date, point.contract, _decision(day), pit_mode)
    if sizing_bar is not None and not deferred_execution_cost:
        ticks = cfg["paper_order_slippage_budget_ticks_per_side"]
        stop_distance = cfg["stop_atr_multiple"] * point.atr20
        planned_loss = ((stop_distance + 2 * ticks * cfg["tick_size_cny_per_gram"])
                        * cfg["multiplier_grams_per_lot"] + sizing_bar["fee_open_per_lot_cny"]
                        + max(sizing_bar["fee_close_today_per_lot_cny"], sizing_bar["fee_close_yesterday_per_lot_cny"]))
        answer["planned_one_lot_loss_cny"] = planned_loss
        answer["prior_margin_per_lot_cny"] = sizing_bar["margin_per_lot_cny"]
        if pit_mode == "strict" and sizing_bar["execution_cost_grade"] in {"VERIFIED", "CONSERVATIVE"}:
            if planned_loss <= answer["risk"]["amount_cny"] and sizing_bar["margin_per_lot_cny"] <= cfg["paper_equity_cny"] * cfg["maximum_margin_fraction"]:
                answer["actionable_entry"] = True
            else:
                answer["action_block"] = "RISK_OR_MARGIN_LIMIT"
        else:
            answer["action_block"] = "RECONSTRUCTED_OR_UNVERIFIED_COST"
    elif not deferred_execution_cost:
        answer["action_block"] = "MISSING_PREDECISION_BAR"
    answer["evidence_sha256"] = _hash(answer)
    answer["signal_id"] = _hash({"strategy": cfg["schema_version"], "as_of": answer["as_of"],
                                 "contract": point.contract, "evidence_sha256": answer["evidence_sha256"]})
    return answer


def _fill_price(bar: Mapping[str, Any], side: str, slippage_ticks: int, cfg: Mapping[str, Any], *,
                raw_price: float | None = None) -> float:
    if raw_price is None:
        raw_price = bar.get("entry_window_price") or bar["open"]
    shift = slippage_ticks * cfg["tick_size_cny_per_gram"]
    return raw_price + shift if side == "BUY" else raw_price - shift


def _close_position(position: dict[str, Any], bar: Mapping[str, Any], cash: float, *, reason: str,
                    slippage_ticks: int, cfg: Mapping[str, Any], raw_price: float | None = None,
                    day: date, events: list[dict[str, Any]]) -> float:
    fill = _fill_price(bar, "SELL", slippage_ticks, cfg, raw_price=raw_price)
    fee_name = "fee_close_today_per_lot_cny" if position["leg_open_date"] == day else "fee_close_yesterday_per_lot_cny"
    fee = bar[fee_name]
    pnl = (fill - position["leg_entry_price"]) * cfg["multiplier_grams_per_lot"] - fee
    events.append({"date": day.isoformat(), "event": "CLOSE", "reason": reason,
                   "contract": position["contract"], "fill_cny_per_gram": fill, "fee_cny": fee,
                   "leg_pnl_cny": pnl, "trade_id": position["trade_id"]})
    return cash + pnl


def _open_position(bar: Mapping[str, Any], contract: str, day: date, *, cash: float,
                   entry_index: int, stop_distance: float, trade_id: str, trade_start_cash: float,
                   slippage_ticks: int, cfg: Mapping[str, Any], events: list[dict[str, Any]],
                   rolled: bool = False) -> tuple[dict[str, Any], float]:
    fill = _fill_price(bar, "BUY", slippage_ticks, cfg)
    fee = bar["fee_open_per_lot_cny"]
    events.append({"date": day.isoformat(), "event": "ROLL_OPEN" if rolled else "OPEN",
                   "contract": contract, "fill_cny_per_gram": fill, "fee_cny": fee,
                   "trade_id": trade_id})
    return ({"contract": contract, "leg_entry_price": fill, "leg_open_date": day,
             "entry_index": entry_index, "stop_distance": stop_distance,
             "stop_price": fill - stop_distance, "trade_id": trade_id,
             "trade_start_cash": trade_start_cash}, cash - fee)


def _apply_protective_stop(position: dict[str, Any], bar: Mapping[str, Any], cash: float, *,
                           day: date, entry_date: date, slippage_ticks: int,
                           cfg: Mapping[str, Any], events: list[dict[str, Any]],
                           include_preopen: bool = False) -> tuple[float, dict[str, Any] | None, bool]:
    """Conservatively prioritize an observed daily stop breach over a 09:00 exit.

    A daily bar cannot order a night/day stop against a planned morning exit.
    Counting the stop first prevents an unearned favorable MAX_HOLD exit.
    """
    # A carried position is exposed during the night/pre-open session. A
    # post-entry-window low could omit exactly that earlier stop touch.
    low = None if include_preopen else bar.get("post_entry_low")
    proxy = low is None
    if low is None:
        low = bar["low"]
    if low > position["stop_price"]:
        return cash, None, proxy
    gap = position["leg_open_date"] != day and bar["open"] < position["stop_price"]
    raw_stop = bar["open"] if gap else position["stop_price"]
    reason = "STOP_GAP" if gap else "STOP_TOUCH"
    cash = _close_position(position, bar, cash, reason=reason,
                           slippage_ticks=slippage_ticks, cfg=cfg, raw_price=raw_stop,
                           day=day, events=events)
    return cash, {"trade_id": position["trade_id"], "entry_date": entry_date.isoformat(),
                  "exit_date": day.isoformat(), "exit_reason": reason,
                  "net_pnl_cny": cash - position["trade_start_cash"],
                  "gap_loss_over_planned_stop_cny": max(0.0, (position["stop_price"] - raw_stop)
                                                        * cfg["multiplier_grams_per_lot"])}, proxy


def _buy_hold_baseline(dataset: GoldAuDataset, path: list[DecisionPoint], ticks: int,
                       cfg: Mapping[str, Any]) -> dict[str, Any]:
    """One continuously held lot with the same dated-contract roll rule/costs."""
    cash = float(cfg["paper_equity_cny"])
    held: str | None = None
    entry_fill = 0.0
    entry_day: date | None = None
    transactions = 0
    for point in path:
        day = point.decision_date
        contract = point.contract
        if contract is None:
            continue
        bar = dataset.rows.get(day, {}).get(contract)
        if bar is None:
            continue
        if held is not None and contract != held:
            old = dataset.rows.get(day, {}).get(held)
            if old is None:
                return {"status": "UNRESOLVED_MISSING_ROLL_BAR", "net_pnl_cny": None,
                        "transactions": transactions}
            exit_fill = _fill_price(old, "SELL", ticks, cfg)
            fee = old["fee_close_today_per_lot_cny"] if entry_day == day else old["fee_close_yesterday_per_lot_cny"]
            cash += (exit_fill - entry_fill) * cfg["multiplier_grams_per_lot"] - fee
            transactions += 1
            held = None
        if held is None:
            entry_fill = _fill_price(bar, "BUY", ticks, cfg)
            cash -= bar["fee_open_per_lot_cny"]
            held = contract
            entry_day = day
            transactions += 1
    if held is None:
        return {"status": "NO_EXECUTABLE_CONTRACT", "net_pnl_cny": 0.0, "transactions": transactions}
    # The final session's close is a measured mark rather than a morning entry
    # window. Deduct the stated side slippage and closing fee conservatively.
    final_day = path[-1].decision_date
    final = dataset.rows.get(final_day, {}).get(held)
    if final is None:
        return {"status": "UNRESOLVED_FINAL_BAR", "net_pnl_cny": None, "transactions": transactions}
    exit_fill = final["close"] - ticks * cfg["tick_size_cny_per_gram"]
    fee = final["fee_close_today_per_lot_cny"] if entry_day == final_day else final["fee_close_yesterday_per_lot_cny"]
    cash += (exit_fill - entry_fill) * cfg["multiplier_grams_per_lot"] - fee
    return {"status": "EXPLORATORY_COST_MODEL", "net_pnl_cny": cash - cfg["paper_equity_cny"],
            "transactions": transactions + 1}


def _macro_filtered_opportunities(full_path: list[DecisionPoint], decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Count every filtered breakout, including overlapping non-trade signals.

    The reference is the index known at 08:30 (yesterday's close). D+5/D+20
    is the close of the fifth/twentieth later session, observed through the
    next morning's chained-index point. Without an official calendar these
    are exploratory vendor-row sessions. Missing marks are censored.
    """
    positions = {point.decision_date.isoformat(): i for i, point in enumerate(full_path)}
    result: list[dict[str, Any]] = []
    for signal in decisions:
        if (signal.get("price_breakout") is not True
                or not isinstance(signal.get("macro"), Mapping)
                or signal["macro"].get("pass") is not False):
            continue
        index = positions[signal["date"]]
        reference = full_path[index].close_index
        row: dict[str, Any] = {"decision_date": signal["date"], "reason": signal["reason"],
                               "reference_preopen_index": reference,
                               "overlapping_signal_not_independent_entry": True, "horizons": {}}
        for horizon in (5, 20):
            due_index = index + horizon
            mark_index = due_index + 1
            complete = (reference is not None and mark_index < len(full_path)
                        and all(point.close_index is not None
                                for point in full_path[index:mark_index + 1]))
            if not complete:
                row["horizons"][str(horizon)] = {
                    "status": "CENSORED_INCOMPLETE_FUTURE_INDEX", "return_pct": None,
                    "later_positive": None}
                continue
            terminal = full_path[mark_index].close_index
            change = (terminal / reference - 1) * 100
            row["horizons"][str(horizon)] = {
                "status": "OBSERVED_EXPLORATORY",
                "due_session": full_path[due_index].decision_date.isoformat(),
                "return_pct": change, "later_positive": change > 0}
        result.append(row)
    return result


def _filtered_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"price_breakouts_filtered_by_macro": len(rows),
            "opportunities_are_independent_entries": False,
            "reason_counts": {reason: sum(row["reason"] == reason for row in rows)
                              for reason in sorted({row["reason"] for row in rows})},
            "horizons": {str(horizon): {
                "observed_count": sum(row["horizons"][str(horizon)]["status"] == "OBSERVED_EXPLORATORY" for row in rows),
                "later_positive_count": sum(row["horizons"][str(horizon)]["later_positive"] is True for row in rows),
                "censored_count": sum(row["horizons"][str(horizon)]["status"] == "CENSORED_INCOMPLETE_FUTURE_INDEX" for row in rows),
            } for horizon in (5, 20)}}


def _historical_blocks(path: list[DecisionPoint], decisions: list[dict[str, Any]],
                       trades: list[dict[str, Any]], equity_curve: list[dict[str, Any]],
                       filtered_opportunities: list[dict[str, Any]],
                       cfg: Mapping[str, Any]) -> list[dict[str, Any]]:
    result = []
    for start_text, end_text in cfg["historical_blocks"]:
        start, end = date.fromisoformat(start_text), date.fromisoformat(end_text)
        block_trades = [t for t in trades if start <= date.fromisoformat(t["entry_date"]) <= end]
        block_equity = [r for r in equity_curve if start <= date.fromisoformat(r["date"]) <= end]
        block_points = [p for p in path if start <= p.decision_date <= end and p.close_index is not None]
        block_decisions = [r for r in decisions if start <= date.fromisoformat(r["date"]) <= end]
        block_filtered = [r for r in filtered_opportunities
                          if start <= date.fromisoformat(r["decision_date"]) <= end]
        gross_price = ((block_points[-1].close_index / block_points[0].close_index - 1) * 100
                       if len(block_points) >= 2 else None)
        starting_equity = (next((r["equity_cny"] for r in reversed(equity_curve)
                                if date.fromisoformat(r["date"]) < start), cfg["paper_equity_cny"]))
        result.append({"start": start_text, "end": end_text, "completed_trades_entered_in_block": len(block_trades),
                       "realized_pnl_of_completed_trades_cny": sum(t["net_pnl_cny"] for t in block_trades),
                       "candidate_entries": sum(bool(r["entry"]) for r in block_decisions),
                       "macro_filtered_opportunity_summary": _filtered_summary(block_filtered),
                       "risk_blocked_entries": sum(r.get("execution_decision") == "ONE_LOT_EXCEEDS_RISK_BUDGET"
                                                   for r in block_decisions),
                       "equity_change_cny": block_equity[-1]["equity_cny"] - starting_equity if block_equity else None,
                       "buy_hold_chained_index_gross_return_pct": gross_price,
                       "status": "NO_COMPLETED_TRADES" if not block_trades else "EXPLORATORY_NOT_VALIDATED"})
    return result


def run_backtest(dataset: GoldAuDataset | Mapping[str, Any], *, variant: str = "full",
                 breakout_lookback: int = 20, macro_lookback: int = 20,
                 slippage_ticks: int = 2, pit_mode: str = "reconstructed",
                 config: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Run an offline one-lot historical counterfactual, never place an order.

    Daily open substitutes for the actual 09:00-09:05 executable price when
    `entry_window_price` is absent. Daily low substitutes for post-entry low
    when `post_entry_low` is absent. Such runs remain exploratory even if PIT
    inputs are strict, because fills/stops cannot be proved from daily bars.
    """
    if not isinstance(dataset, GoldAuDataset):
        dataset = GoldAuDataset(dataset)
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    if type(slippage_ticks) is not int or slippage_ticks < 0:
        raise ValueError("slippage_ticks must be a nonnegative integer")
    if breakout_lookback < 2 or macro_lookback < 2:
        raise ValueError("lookbacks must be at least two")
    if variant not in {"full", "price_only", "real_rate_only", "usd_only"}:
        raise ValueError("invalid variant")
    full_path = build_decision_path(dataset, pit_mode=pit_mode, config=cfg)
    path = [point for point in full_path
            if point.decision_date in dataset.rows]
    cash = float(cfg["paper_equity_cny"])
    high_water = cash
    position: dict[str, Any] | None = None
    frozen = False
    events: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    trades: list[dict[str, Any]] = []
    equity_curve: list[dict[str, Any]] = []
    used_open_proxy = False
    used_stop_proxy = False
    unresolved = False
    for j, point in enumerate(path):
        day = point.decision_date
        signal = _signal_for_point(dataset, path, j, pit_mode=pit_mode, variant=variant,
                                   breakout_lookback=breakout_lookback, macro_lookback=macro_lookback, config=cfg)
        signal["date"] = day.isoformat()
        decisions.append(signal)
        current_bar = dataset.rows.get(day, {}).get(point.contract) if point.contract else None
        old_bar = dataset.rows.get(day, {}).get(position["contract"]) if position else None
        if position is not None and old_bar is None:
            events.append({"date": day.isoformat(), "event": "UNRESOLVED_MISSING_HELD_CONTRACT_BAR",
                           "contract": position["contract"]})
            unresolved = True
            break
        if position is not None:
            cash, stopped_trade, proxy = _apply_protective_stop(
                position, old_bar, cash, day=day,
                entry_date=path[position["entry_index"]].decision_date,
                slippage_ticks=slippage_ticks, cfg=cfg, events=events,
                include_preopen=True)
            used_stop_proxy |= proxy
            if stopped_trade is not None:
                trades.append(stopped_trade)
                position = None
        if position is not None:
            held_days = j - position["entry_index"]
            prior_closes = [p.close_index for p in path[:j] if p.close_index is not None]
            soft_exit = (held_days >= cfg["minimum_hold_trading_days_for_soft_exit"]
                         and point.close_index is not None
                         and len(prior_closes) >= cfg["soft_exit_low_lookback"]
                         and point.close_index < min(prior_closes[-cfg["soft_exit_low_lookback"]:]))
            reason = ("MAX_HOLD" if held_days >= cfg["maximum_hold_trading_days"] else
                      "TEN_DAY_CLOSE_LOW" if soft_exit else None)
            if reason is not None:
                if old_bar.get("entry_window_price") is None:
                    used_open_proxy = True
                cash = _close_position(position, old_bar, cash, reason=reason, slippage_ticks=slippage_ticks,
                                       cfg=cfg, day=day, events=events)
                trades.append({"trade_id": position["trade_id"], "entry_date": path[position["entry_index"]].decision_date.isoformat(),
                               "exit_date": day.isoformat(), "exit_reason": reason,
                               "net_pnl_cny": cash - position["trade_start_cash"]})
                position = None
            elif point.contract is None or current_bar is None:
                events.append({"date": day.isoformat(), "event": "UNRESOLVED_ROLL_DATA", "trade_id": position["trade_id"]})
                unresolved = True
                break
            elif point.contract != position["contract"]:
                if old_bar.get("entry_window_price") is None or current_bar.get("entry_window_price") is None:
                    used_open_proxy = True
                cash = _close_position(position, old_bar, cash, reason="ROLL", slippage_ticks=slippage_ticks,
                                       cfg=cfg, day=day, events=events)
                prior_roll_bar = dataset.bar(point.prior_date, point.contract, _decision(day), pit_mode)
                if prior_roll_bar is None or prior_roll_bar["margin_per_lot_cny"] > cash * cfg["maximum_margin_fraction"]:
                    trades.append({"trade_id": position["trade_id"], "entry_date": path[position["entry_index"]].decision_date.isoformat(),
                                   "exit_date": day.isoformat(), "exit_reason": "ROLL_MARGIN_BLOCK",
                                   "net_pnl_cny": cash - position["trade_start_cash"]})
                    position = None
                else:
                    position, cash = _open_position(current_bar, point.contract, day, cash=cash,
                                                    entry_index=position["entry_index"],
                                                    stop_distance=position["stop_distance"],
                                                    trade_id=position["trade_id"], trade_start_cash=position["trade_start_cash"],
                                                    slippage_ticks=slippage_ticks, cfg=cfg, events=events, rolled=True)
        # A planned exit never immediately reverses into another entry that morning.
        exited_today = any(e["date"] == day.isoformat() and e["event"] == "CLOSE" and e["reason"] != "ROLL" for e in events[-2:])
        if position is None and not exited_today and signal["entry"] and not frozen and current_bar is not None:
            sizing_bar = dataset.bar(point.prior_date, point.contract, _decision(day), pit_mode)
            if sizing_bar is None:
                signal["execution_decision"] = "MISSING_PREDECISION_MARGIN_AND_FEE_SCHEDULE"
                continue
            if current_bar.get("entry_window_price") is None:
                used_open_proxy = True
            provisional_entry = _fill_price(current_bar, "BUY", slippage_ticks, cfg)
            budget = risk_budget(dataset, point, cash, pit_mode=pit_mode, config=cfg)
            stop_distance = cfg["stop_atr_multiple"] * point.atr20
            # Include both directional slippage and both fees in the planned loss.
            planned_loss = (stop_distance + 2 * slippage_ticks * cfg["tick_size_cny_per_gram"]) * cfg["multiplier_grams_per_lot"]
            planned_loss += sizing_bar["fee_open_per_lot_cny"] + max(sizing_bar["fee_close_today_per_lot_cny"], sizing_bar["fee_close_yesterday_per_lot_cny"])
            if cfg["maximum_lots"] < 1:
                block = "MAX_LOTS_ZERO"
            elif pit_mode == "strict" and sizing_bar["execution_cost_grade"] == "ASSUMPTION":
                block = "UNVERIFIED_PREDECISION_COST_AND_MARGIN"
            elif planned_loss > budget["amount_cny"]:
                block = "ONE_LOT_EXCEEDS_RISK_BUDGET"
            elif sizing_bar["margin_per_lot_cny"] > cash * cfg["maximum_margin_fraction"]:
                block = "ONE_LOT_EXCEEDS_MARGIN_CAP"
            else:
                block = None
            signal["planned_loss_cny"] = planned_loss
            signal["risk_budget_cny"] = budget["amount_cny"]
            signal["entry_fill_proxy_cny_per_gram"] = provisional_entry
            if block:
                signal["execution_decision"] = block
            else:
                trade_id = _hash({"strategy": cfg["schema_version"], "day": day.isoformat(), "contract": point.contract,
                                  "variant": variant, "slippage_ticks": slippage_ticks})[:20]
                position, cash = _open_position(current_bar, point.contract, day, cash=cash, entry_index=j,
                                                stop_distance=stop_distance, trade_id=trade_id, trade_start_cash=cash,
                                                slippage_ticks=slippage_ticks, cfg=cfg, events=events)
                signal["execution_decision"] = "SIMULATED_ONE_LOT_ENTRY"
        elif position is None and signal["entry"]:
            signal["execution_decision"] = "FROZEN_OR_MISSING_EXECUTION_BAR" if frozen or current_bar is None else "EXITED_SAME_MORNING"
        if position is not None:
            held_bar = dataset.rows.get(day, {}).get(position["contract"])
            if held_bar is None:
                events.append({"date": day.isoformat(), "event": "UNRESOLVED_MISSING_HELD_CONTRACT_BAR",
                               "contract": position["contract"]})
                unresolved = True
                break
            cash, stopped_trade, proxy = _apply_protective_stop(
                position, held_bar, cash, day=day,
                entry_date=path[position["entry_index"]].decision_date,
                slippage_ticks=slippage_ticks, cfg=cfg, events=events)
            used_stop_proxy |= proxy
            if stopped_trade is not None:
                trades.append(stopped_trade)
                position = None
        equity = cash
        if position is not None:
            bar = dataset.rows[day][position["contract"]]
            equity += (bar["close"] - position["leg_entry_price"]) * cfg["multiplier_grams_per_lot"]
        high_water = max(high_water, equity)
        drawdown = 1 - equity / high_water
        if drawdown >= cfg["freeze_new_entries_drawdown_fraction"] and not frozen:
            frozen = True
            events.append({"date": day.isoformat(), "event": "ENTRY_FREEZE_5PCT_DRAWDOWN", "drawdown": drawdown})
        equity_curve.append({"date": day.isoformat(), "equity_cny": equity, "drawdown": drawdown,
                             "position_contract": position["contract"] if position else None})
    first_index = next((p.close_index for p in path if p.close_index is not None), None)
    last_index = next((p.close_index for p in reversed(path) if p.close_index is not None), None)
    benchmark = ((last_index / first_index - 1) * 100 if first_index and last_index else None)
    possible = sum(1 for d in decisions if d.get("entry"))
    blocked_risk = sum(1 for d in decisions if d.get("execution_decision") == "ONE_LOT_EXCEEDS_RISK_BUDGET")
    buy_hold = _buy_hold_baseline(dataset, path, slippage_ticks, cfg)
    filtered_opportunities = _macro_filtered_opportunities(full_path, decisions)
    missing_calendar_bar_days = ([day.isoformat() for day in dataset.dates[:-1]
                                  if dataset.exchange_sessions is not None and day not in dataset.rows]
                                 if dataset.dates else [])
    quality_blocked = dataset.price_quality["status"] in {
        "UNVERIFIED_VENDOR_OHLC", "OFFICIAL_DAILY_OHLC_PIT_UNVERIFIED", "SYNTHETIC_FIXTURE"}
    return {"schema_version": "gold-au-backtest.v1", "strategy_version": cfg["schema_version"],
            "variant": variant, "pit_mode": pit_mode,
            "status": "UNRESOLVED_DATA" if unresolved or missing_calendar_bar_days else "DATA_QUALITY_BLOCKED_EXPLORATORY" if quality_blocked else "EXPLORATORY_NOT_VALIDATED",
            "investment_effectiveness_proven": False, "broker_order_authorized": False,
            "price_quality": dataset.price_quality,
            "exchange_calendar_ref": dataset.exchange_calendar_ref,
            "missing_official_session_bar_days": missing_calendar_bar_days,
            "input_sha256": _hash({"price_quality": dataset.price_quality,
                                   "exchange_sessions": sorted(d.isoformat() for d in dataset.exchange_sessions) if dataset.exchange_sessions is not None else None,
                                   "exchange_calendar_ref": dataset.exchange_calendar_ref,
                                   "bars": [row for day in dataset.dates for row in dataset.rows.get(day, {}).values()],
                                   "observations": [row for values in dataset.observations.values() for row in values]}),
            "config_sha256": _hash(cfg), "breakout_lookback": breakout_lookback,
            "macro_lookback": macro_lookback, "slippage_ticks_per_side": slippage_ticks,
            "paper_initial_equity_cny": cfg["paper_equity_cny"],
            "final_equity_cny": equity_curve[-1]["equity_cny"] if equity_curve else cash,
            "mark_to_market_open_position": bool(position), "frozen_new_entries": frozen,
            "buy_hold_chained_index_gross_return_pct": benchmark,
            "buy_hold_one_lot_after_costs": buy_hold, "cash_baseline_return_pct": 0,
            "candidate_entries": possible, "risk_blocked_entries": blocked_risk,
            "completed_trades": len(trades), "net_realized_pnl_cny": cash - cfg["paper_equity_cny"],
            "maximum_drawdown_pct": 100 * max((r["drawdown"] for r in equity_curve), default=0),
            "fills_use_daily_open_proxy": used_open_proxy, "stops_use_daily_low_proxy": used_stop_proxy,
            "stop_vs_morning_exit_order_assumption": "STOP_FIRST_WHEN_DAILY_LOW_BREACHES_BECAUSE_INTRADAY_ORDER_UNKNOWN",
            "historical_vintages_independently_verified": False,
            "macro_filtered_opportunity_summary": _filtered_summary(filtered_opportunities),
            "macro_filtered_opportunities": filtered_opportunities,
            "macro_filtered_return_reference": "PREOPEN_PRIOR_CLOSE_INDEX_TO_D_PLUS_H_LATER_SESSION_CLOSE",
            "macro_filtered_horizon_calendar_grade": ("OFFICIAL_EXCHANGE_SESSIONS" if dataset.exchange_sessions is not None
                                                      else "INFERRED_BAR_DATES_EXPLORATORY"),
            "historical_blocks": _historical_blocks(path, decisions, trades, equity_curve,
                                                     filtered_opportunities, cfg),
            "decisions": decisions, "events": events, "trades": trades, "equity_curve": equity_curve}
