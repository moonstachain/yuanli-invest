"""Research-only historical scope and publication-delay diagnostics.

The production strategy and its provenance timestamps are never modified.
Publication dates here are a counterfactual schedule, not witnessed historical
availability or first-release vintages. Strict mode retains the engine's real
PIT rejection. This module has no gateway, credentials, or order API.
"""
from __future__ import annotations

import ast
from bisect import bisect_right
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
import hashlib
import inspect
from typing import Any
from zoneinfo import ZoneInfo

from . import gold_au_strategy as engine

NY = ZoneInfo("America/New_York")


def _nth_weekday(year: int, month: int, weekday: int, number: int) -> date:
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (number - 1))


def _observed(day: date) -> date:
    return day - timedelta(days=1) if day.weekday() == 5 else day + timedelta(days=1) if day.weekday() == 6 else day


@lru_cache(maxsize=24)
def assumed_federal_holidays(year: int) -> frozenset[date]:
    """Regular OPM rules only; unscheduled Board closures are not recovered."""
    fixed = [_observed(date(year, month, day)) for month, day in ((1, 1), (7, 4), (11, 11), (12, 25))]
    if year >= 2021:
        fixed.append(_observed(date(year, 6, 19)))
    # The following year's observed New Year can fall on this December 31.
    fixed.append(_observed(date(year + 1, 1, 1)))
    memorial = date(year, 6, 1) - timedelta(days=1)
    memorial -= timedelta(days=memorial.weekday())
    return frozenset(fixed + [_nth_weekday(year, 1, 0, 3), _nth_weekday(year, 2, 0, 3), memorial,
                             _nth_weekday(year, 9, 0, 1), _nth_weekday(year, 10, 0, 2),
                             _nth_weekday(year, 11, 3, 4)])


def _next_assumed_business_day(day: date) -> date:
    while day.weekday() >= 5 or day in assumed_federal_holidays(day.year):
        day += timedelta(days=1)
    return day


def hypothetical_publication_at(series: str, observed: date) -> datetime:
    """Schedule assumptions plus 15 minutes; never used for live or strict PIT.

    H.10 publishes the previous business week on Monday 16:15 ET, shifted
    after federal holidays. H.15 next-business-day publication of the prior
    observation is an explicit conservative inference, not an archived proof.
    FRED distribution delay and unexpected closures remain unknown.
    """
    if series == "FED:H10:DTWEXBGS":
        candidate = observed + timedelta(days=7 - observed.weekday())
    elif series == "FRED:DFII10":
        candidate = observed + timedelta(days=1)
    else:
        raise ValueError("NO_HYPOTHETICAL_SCHEDULE_FOR_SERIES")
    release = _next_assumed_business_day(candidate)
    return datetime.combine(release, time(16, 30), NY).astimezone(timezone.utc)


class HistoricalResearchDataset(engine.GoldAuDataset):
    """Cached exploratory selection, with optional assumed macro delay.

    Input rows keep actual capture times and UNKNOWN vintage grades. An
    independent field records the assumed cutoff used only in reconstructed
    mode; it cannot make those rows admissible under strict mode.
    """
    def __init__(self, payload: Any, *, publication_model: str = "OBSERVATION_DATE_LEAKY_REFERENCE"):
        if publication_model not in {"OBSERVATION_DATE_LEAKY_REFERENCE", "SCHEDULE_DELAY_LATEST_VINTAGE_EXPLORATORY"}:
            raise ValueError("UNSUPPORTED_PUBLICATION_MODEL")
        super().__init__(payload)
        self.publication_model = publication_model
        self._selection_cache: dict[tuple, list[dict]] = {}
        self._ordered: dict[str, list[dict]] = {}
        self._cutoffs: dict[str, list[datetime]] = {}
        for series, rows in self.observations.items():
            chosen: dict[str, dict] = {}
            for row in rows:
                prior = chosen.get(row["observed_on"])
                if prior is None or (row["released_at"], row["vintage_id"]) > (prior["released_at"], prior["vintage_id"]):
                    chosen[row["observed_on"]] = row
            ordered = [chosen[key] for key in sorted(chosen)]
            self._ordered[series] = ordered
            if series in engine.MACRO_SERIES:
                self._cutoffs[series] = [hypothetical_publication_at(series, date.fromisoformat(row["observed_on"]))
                                         for row in ordered]

    def latest_n(self, series: str, count: int, as_of: datetime, mode: str, measurement_regime: str) -> list[dict]:
        key = (series, count, as_of, mode, measurement_regime)
        if key in self._selection_cache:
            return self._selection_cache[key]
        if mode == "strict" or series not in engine.MACRO_SERIES:
            result = super().latest_n(series, count, as_of, mode, measurement_regime)
        elif self.publication_model == "OBSERVATION_DATE_LEAKY_REFERENCE":
            result = super().latest_n(series, count, as_of, mode, measurement_regime)
        else:
            end = bisect_right(self._cutoffs[series], as_of)
            visible = [row for row in self._ordered[series][:end] if row["measurement_regime"] == measurement_regime]
            result = [dict(row, hypothetical_publication_at=hypothetical_publication_at(
                      series, date.fromisoformat(row["observed_on"])).isoformat(),
                      hypothetical_publication_basis="ASSUMED_SCHEDULE_NOT_WITNESSED_PIT") for row in visible[-count:]]
        self._selection_cache[key] = result
        return result


@lru_cache(maxsize=1)
def scoped_engine() -> tuple[Any, dict[str, Any]]:
    """Guarded AST adapter adds only execution scope; indicators retain warmup.

    The source and adapter hashes are emitted. Tests assert full-range exact
    equivalence and future-input invariance. A changed source structure raises
    rather than silently introducing a different execution algorithm.
    """
    original = inspect.getsource(engine.run_backtest)
    module = ast.parse(original)
    function = module.body[0]
    if not isinstance(function, ast.FunctionDef) or function.name != "run_backtest":
        raise ValueError("FROZEN_ENGINE_STRUCTURE_CHANGED")
    function.name = "run_scoped_backtest"
    function.args.kwonlyargs.extend([ast.arg(arg="scope_start"), ast.arg(arg="scope_end")])
    function.args.kw_defaults.extend([ast.Constant(None), ast.Constant(None)])
    loops = [node for node in function.body if isinstance(node, ast.For) and isinstance(node.target, ast.Tuple)
             and ast.unparse(node.target) == "(j, point)"]
    if len(loops) != 1 or ast.unparse(loops[0].body[0]) != "day = point.decision_date":
        raise ValueError("FROZEN_ENGINE_LOOP_STRUCTURE_CHANGED")
    loops[0].body[1:1] = ast.parse("if (scope_start is not None and day < scope_start) or (scope_end is not None and day > scope_end):\n    continue").body
    for index, node in enumerate(function.body):
        if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == "first_index":
            function.body[index:index] = ast.parse("report_path = [point for point in path if (scope_start is None or point.decision_date >= scope_start) and (scope_end is None or point.decision_date <= scope_end)]").body
            break
    else:
        raise ValueError("FROZEN_ENGINE_REPORT_STRUCTURE_CHANGED")
    for node in function.body:
        if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) in {"first_index", "last_index"}:
            for child in ast.walk(node.value):
                if isinstance(child, ast.Name) and child.id == "path":
                    child.id = "report_path"
    for node in ast.walk(function):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            slot = 1 if node.func.id == "_buy_hold_baseline" else 0 if node.func.id == "_historical_blocks" else None
            if slot is not None:
                if not isinstance(node.args[slot], ast.Name) or node.args[slot].id != "path":
                    raise ValueError("FROZEN_ENGINE_BASELINE_STRUCTURE_CHANGED")
                node.args[slot].id = "report_path"
    returned = function.body[-1]
    if not isinstance(returned, ast.Return) or not isinstance(returned.value, ast.Dict):
        raise ValueError("FROZEN_ENGINE_RETURN_STRUCTURE_CHANGED")
    returned.value.keys.append(ast.Constant("terminal_position"))
    returned.value.values.append(ast.parse("dict(position) if position else None", mode="eval").body)
    ast.fix_missing_locations(module)
    adapted = ast.unparse(module) + "\n"
    namespace = dict(vars(engine))
    exec(compile(module, "<gold-au-research-scope-adapter>", "exec"), namespace)
    receipt = {"frozen_function_sha256": hashlib.sha256(original.encode()).hexdigest(),
               "scope_adapter_sha256": hashlib.sha256(adapted.encode()).hexdigest(),
               "strategy_parameters_modified": False, "full_preperiod_signal_warmup": True,
               "scope_semantics": "FLAT_AT_START_5000000_EQUITY_NO_PREPERIOD_EXECUTION",
               "broker_action_authorized": False}
    return namespace[function.name], receipt


def run_historical_scope(dataset: engine.GoldAuDataset, *, start: date, end: date, **kwargs: Any) -> dict:
    if not isinstance(start, date) or not isinstance(end, date) or start > end:
        raise ValueError("VALID_HISTORICAL_SCOPE_REQUIRED")
    function, receipt = scoped_engine()
    result = function(dataset, scope_start=start, scope_end=end, **kwargs)
    result.update(research_scope_start=start.isoformat(), research_scope_end=end.isoformat(),
                  research_adapter=receipt, publication_model=getattr(dataset, "publication_model", "ENGINE_DEFAULT"))
    return result
