"""Immutable, provider-neutral point-in-time gold research inputs.

All selection is by the actual decision-time availability of an exact series.
These utilities neither infer publication time from an observation date nor
translate one provider's rate or dollar series into another provider's series.
The attribution fit is a contemporaneous description, never a forecast.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
import re
from typing import Iterable, Sequence

from .time import instant


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_GRADES = frozenset({"VERIFIED", "CONSERVATIVE", "UNKNOWN"})


def _identity(value: str, name: str, *, namespaced: bool = False) -> str:
    if not isinstance(value, str) or not value or value.strip() != value or any(c.isspace() for c in value):
        raise ValueError(f"{name} must be a nonempty whitespace-free string")
    if namespaced and (":" not in value or value.startswith(":") or value.endswith(":")):
        raise ValueError(f"{name} must include a provider namespace")
    return value


def _number(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


@dataclass(frozen=True, slots=True)
class GoldObservation:
    """One source-versioned observation, including ingestion availability.

    ``VERIFIED`` means an exact source publication timestamp and captured source
    version are evidenced. ``CONSERVATIVE`` is a deliberately later release
    bound; ``UNKNOWN`` must never be used for a strict trading signal. Merely
    having a dated observation does not establish any of these release times.
    """

    series_id: str
    measurement_regime: str
    unit: str
    value: float
    observation_at: datetime
    released_at: datetime
    retrieved_at: datetime
    available_at: datetime
    vintage_id: str
    source_sha256: str
    pit_grade: str

    def __post_init__(self) -> None:
        _identity(self.series_id, "series_id", namespaced=True)
        _identity(self.measurement_regime, "measurement_regime")
        _identity(self.unit, "unit")
        _identity(self.vintage_id, "vintage_id")
        object.__setattr__(self, "value", _number(self.value, "value"))
        if not isinstance(self.source_sha256, str) or _SHA256.fullmatch(self.source_sha256) is None:
            raise ValueError("source_sha256 must be a lowercase SHA-256 hex digest")
        if self.pit_grade not in _GRADES:
            raise ValueError("pit_grade must be VERIFIED, CONSERVATIVE, or UNKNOWN")
        for field in ("observation_at", "released_at", "retrieved_at", "available_at"):
            object.__setattr__(self, field, instant(getattr(self, field)))
        if not (self.observation_at <= self.released_at <= self.retrieved_at <= self.available_at):
            raise ValueError("observation, release, retrieval, availability must be ordered")


def _as_of(value: datetime) -> datetime:
    return instant(value)


def _candidate_versions(
    observations: Iterable[GoldObservation],
    *,
    as_of: datetime,
    series_id: str,
    unit: str,
    measurement_regime: str,
    allowed_pit_grades: frozenset[str],
) -> tuple[GoldObservation, ...]:
    _identity(series_id, "series_id", namespaced=True)
    _identity(unit, "unit")
    _identity(measurement_regime, "measurement_regime")
    if not allowed_pit_grades or not allowed_pit_grades <= _GRADES:
        raise ValueError("allowed_pit_grades must be a nonempty set of known grades")
    decision_at = _as_of(as_of)
    eligible: list[GoldObservation] = []
    seen: dict[tuple[str, str, datetime, str], GoldObservation] = {}
    for row in observations:
        if not isinstance(row, GoldObservation):
            raise ValueError("observations must contain GoldObservation records")
        key = (row.series_id, row.measurement_regime, row.observation_at, row.vintage_id)
        previous = seen.setdefault(key, row)
        if previous != row:
            raise ValueError("conflicting records for the same observation vintage")
        if (
            row.series_id == series_id
            and row.unit == unit
            and row.measurement_regime == measurement_regime
            and row.pit_grade in allowed_pit_grades
            and row.available_at <= decision_at
        ):
            eligible.append(row)
    return tuple(eligible)


def latest_n_as_of(
    observations: Iterable[GoldObservation],
    *,
    as_of: datetime,
    series_id: str,
    unit: str,
    measurement_regime: str,
    n: int,
    allowed_pit_grades: frozenset[str] = frozenset({"VERIFIED"}),
) -> tuple[GoldObservation, ...]:
    """Select the last ``n`` distinct observations, with their then-known vintages.

    Result is ordered by observation time, oldest first. Fewer than ``n`` rows
    means insufficient evidence: this returns an empty tuple rather than a
    shortened window. All matching is exact; no Wind/FRED or DXY/H.10 aliasing.
    """
    if type(n) is not int or n < 1:
        raise ValueError("n must be a positive integer")
    versions = _candidate_versions(
        observations,
        as_of=as_of,
        series_id=series_id,
        unit=unit,
        measurement_regime=measurement_regime,
        allowed_pit_grades=allowed_pit_grades,
    )
    by_observation: dict[datetime, GoldObservation] = {}
    for row in versions:
        previous = by_observation.get(row.observation_at)
        if previous is None or (row.available_at, row.released_at, row.vintage_id) > (
            previous.available_at,
            previous.released_at,
            previous.vintage_id,
        ):
            by_observation[row.observation_at] = row
    dates = sorted(by_observation)
    if len(dates) < n:
        return ()
    return tuple(by_observation[date] for date in dates[-n:])


def select_as_of(
    observations: Iterable[GoldObservation],
    *,
    as_of: datetime,
    series_id: str,
    unit: str,
    measurement_regime: str,
    allowed_pit_grades: frozenset[str] = frozenset({"VERIFIED"}),
) -> GoldObservation | None:
    """Return the latest eligible exact-series observation, or ``None``."""
    rows = latest_n_as_of(
        observations,
        as_of=as_of,
        series_id=series_id,
        unit=unit,
        measurement_regime=measurement_regime,
        n=1,
        allowed_pit_grades=allowed_pit_grades,
    )
    return rows[0] if rows else None


@dataclass(frozen=True, slots=True)
class AttributionRow:
    """Aligned historical changes, never a forward-return training row."""

    observation_at: datetime
    gold_log_return: float
    real_yield_delta_bp: float
    broad_dollar_log_return: float
    gold_series_id: str
    real_yield_series_id: str
    dollar_series_id: str
    measurement_regime: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_at", instant(self.observation_at))
        for name in ("gold_log_return", "real_yield_delta_bp", "broad_dollar_log_return"):
            object.__setattr__(self, name, _number(getattr(self, name), name))
        for name in ("gold_series_id", "real_yield_series_id", "dollar_series_id"):
            _identity(getattr(self, name), name, namespaced=True)
        _identity(self.measurement_regime, "measurement_regime")


@dataclass(frozen=True, slots=True)
class AttributionResult:
    status: str
    n: int
    purpose: str = "CONTEMPORANEOUS_ATTRIBUTION"
    forecast_ready: bool = False
    gold_series_id: str | None = None
    real_yield_series_id: str | None = None
    dollar_series_id: str | None = None
    measurement_regime: str | None = None
    window_start: datetime | None = None
    window_end: datetime | None = None
    intercept: float | None = None
    real_yield_coefficient: float | None = None
    dollar_coefficient: float | None = None
    baseline_rmse: float | None = None
    rates_only_rmse: float | None = None
    rates_and_dollar_rmse: float | None = None


def _solve(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float] | None:
    """Small normal-equation solver; return None when predictors lack rank."""
    size = len(vector)
    a = [list(matrix[i]) + [vector[i]] for i in range(size)]
    scale = max(abs(value) for row in a for value in row)
    if scale == 0:
        return None
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(a[row][col]))
        if abs(a[pivot][col]) <= 1e-10 * scale:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        divisor = a[col][col]
        for j in range(col, size + 1):
            a[col][j] /= divisor
        for row in range(size):
            if row == col:
                continue
            multiple = a[row][col]
            for j in range(col, size + 1):
                a[row][j] -= multiple * a[col][j]
    return [a[i][size] for i in range(size)]


def _ols_rmse(rows: Sequence[AttributionRow], predictors: tuple[str, ...]) -> tuple[list[float], float] | None:
    xs = [[1.0] + [getattr(row, name) for name in predictors] for row in rows]
    ys = [row.gold_log_return for row in rows]
    width = len(predictors) + 1
    matrix = [[sum(x[i] * x[j] for x in xs) for j in range(width)] for i in range(width)]
    vector = [sum(x[i] * y for x, y in zip(xs, ys)) for i in range(width)]
    coefficients = _solve(matrix, vector)
    if coefficients is None:
        return None
    rmse = math.sqrt(sum((y - sum(c * v for c, v in zip(coefficients, x))) ** 2 for x, y in zip(xs, ys)) / len(ys))
    return coefficients, rmse


def fit_contemporaneous_attribution(
    rows: Iterable[AttributionRow], *, minimum_rows: int = 30
) -> AttributionResult:
    """Recompute in-sample baseline/rates/rates+FX fits on one exact data regime.

    Same-period association cannot validate direction, causality, or trading
    alpha. Coefficients are never carried between Wind and public-series runs.
    """
    if type(minimum_rows) is not int or minimum_rows < 4:
        raise ValueError("minimum_rows must be at least four")
    data = tuple(rows)
    if any(not isinstance(row, AttributionRow) for row in data):
        raise ValueError("rows must contain AttributionRow records")
    if len(data) < minimum_rows:
        return AttributionResult(status="UNKNOWN_INSUFFICIENT_ROWS", n=len(data))
    identities = {
        (row.gold_series_id, row.real_yield_series_id, row.dollar_series_id, row.measurement_regime)
        for row in data
    }
    if len(identities) != 1:
        raise ValueError("attribution cannot pool different series or measurement regimes")
    dates = [row.observation_at for row in data]
    if len(set(dates)) != len(dates):
        raise ValueError("attribution cannot use duplicate observation times")
    baseline = _ols_rmse(data, ())
    rates = _ols_rmse(data, ("real_yield_delta_bp",))
    full = _ols_rmse(data, ("real_yield_delta_bp", "broad_dollar_log_return"))
    if baseline is None or rates is None or full is None:
        return AttributionResult(status="UNKNOWN_RANK_DEFICIENT", n=len(data))
    gold_series_id, real_yield_series_id, dollar_series_id, measurement_regime = next(iter(identities))
    return AttributionResult(
        status="ESTIMATED_CONTEMPORANEOUS",
        n=len(data),
        gold_series_id=gold_series_id,
        real_yield_series_id=real_yield_series_id,
        dollar_series_id=dollar_series_id,
        measurement_regime=measurement_regime,
        window_start=min(dates),
        window_end=max(dates),
        intercept=full[0][0],
        real_yield_coefficient=full[0][1],
        dollar_coefficient=full[0][2],
        baseline_rmse=baseline[1],
        rates_only_rmse=rates[1],
        rates_and_dollar_rmse=full[1],
    )
