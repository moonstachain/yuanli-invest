from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .contracts import EvidenceStatus, RealityEvidence

UNKNOWN = "UNKNOWN"


class RealityState(str, Enum):
    ACCELERATING = "ACCELERATING"
    STABLE = "STABLE"
    DECELERATING = "DECELERATING"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class DimensionState:
    dimension: str
    level: Any
    delta: Any
    delta2: Any
    state: RealityState
    confidence: str
    evidence_refs: tuple[str, ...]
    known_as_of: str | None


@dataclass(frozen=True)
class RealityStateCard:
    as_of: str
    dimensions: dict[str, DimensionState]
    authority: str = "RESEARCH"


DIMENSION_PREFIXES: dict[str, tuple[str, ...]] = {
    "financing_regime": ("AIINFRA.RATES.", "AIINFRA.FX."),
    "hyperscaler_capex": ("AIINFRA.CAPEX.",),
    "compute": ("AIINFRA.COMPUTE.",),
    "networking": ("AIINFRA.NETWORKING.",),
    "power_grid": ("AIINFRA.POWER.",),
    "capital_efficiency": ("AIINFRA.CAPITAL_EFFICIENCY.",),
}


def _belongs(metric_id: str, prefixes: tuple[str, ...]) -> bool:
    return any(metric_id.startswith(prefix) for prefix in prefixes)


def _safe_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _state_from(delta: float, delta2: float) -> RealityState:
    eps = 1e-12
    if abs(delta) <= eps and abs(delta2) <= eps:
        return RealityState.STABLE
    if delta > eps and delta2 > eps:
        return RealityState.ACCELERATING
    if delta < -eps and delta2 < -eps:
        return RealityState.DECELERATING
    return RealityState.MIXED


def _denorm(value: float) -> int | float:
    return int(value) if float(value).is_integer() else value


def _compile_metric_series(rows: list[RealityEvidence]) -> tuple[Any, Any, Any, RealityState, tuple[str, ...], str | None]:
    rows = sorted(rows, key=lambda item: ((item.known_as_of or ""), item.evidence_id))
    refs = tuple(item.evidence_id for item in rows)
    latest_known = max((item.known_as_of for item in rows if item.known_as_of), default=None)

    if any(item.evidence_status is not EvidenceStatus.PASS for item in rows):
        latest = rows[-1]
        return latest.value if latest.value is not None else UNKNOWN, UNKNOWN, UNKNOWN, RealityState.UNKNOWN, refs, latest_known

    numeric_rows = [item for item in rows if _safe_number(item.value) is not None]
    if len(numeric_rows) < 3:
        latest = numeric_rows[-1] if numeric_rows else rows[-1]
        return latest.value if latest.value is not None else UNKNOWN, UNKNOWN, UNKNOWN, RealityState.UNKNOWN, refs, latest_known

    last3 = numeric_rows[-3:]
    v0, v1, v2 = (_safe_number(item.value) for item in last3)
    assert v0 is not None and v1 is not None and v2 is not None
    d_prev = v1 - v0
    delta = v2 - v1
    delta2 = delta - d_prev
    return (
        last3[-1].value,
        _denorm(delta),
        _denorm(delta2),
        _state_from(delta, delta2),
        tuple(item.evidence_id for item in numeric_rows),
        max(item.known_as_of for item in numeric_rows if item.known_as_of),
    )


def _compile_dimension(name: str, rows: list[RealityEvidence]) -> DimensionState:
    if not rows:
        return DimensionState(name, UNKNOWN, UNKNOWN, UNKNOWN, RealityState.UNKNOWN, "LOW", (), None)

    by_metric: dict[str, list[RealityEvidence]] = {}
    for row in rows:
        by_metric.setdefault(row.metric_id, []).append(row)

    compiled = {metric_id: _compile_metric_series(series) for metric_id, series in sorted(by_metric.items())}
    states = [result[3] for result in compiled.values()]
    all_refs = tuple(sorted({ref for result in compiled.values() for ref in result[4]}))
    latest_known = max((result[5] for result in compiled.values() if result[5]), default=None)

    fail_closed = any(state is RealityState.UNKNOWN for state in states)
    if fail_closed:
        state = RealityState.UNKNOWN
        confidence = "LOW"
    elif len(set(states)) == 1:
        state = states[0]
        confidence = "HIGH"
    else:
        state = RealityState.MIXED
        confidence = "MEDIUM"

    if len(compiled) == 1:
        result = next(iter(compiled.values()))
        level, delta, delta2 = result[0], result[1], result[2]
    else:
        level = {metric_id: result[0] for metric_id, result in compiled.items()}
        if fail_closed:
            delta = UNKNOWN
            delta2 = UNKNOWN
        else:
            delta = {metric_id: result[1] for metric_id, result in compiled.items()}
            delta2 = {metric_id: result[2] for metric_id, result in compiled.items()}

    return DimensionState(name, level, delta, delta2, state, confidence, all_refs, latest_known)


def _compile_capital_efficiency_dimension(rows: list[RealityEvidence], as_of: str) -> DimensionState:
    from pathlib import Path

    try:
        from runtime.yci0_rp1.capital_efficiency_compiler import compile_capital_efficiency
        from runtime.yci0_rp1.capital_efficiency_contract import load_capital_efficiency_contract

        root = Path(__file__).resolve().parents[2]
        contract = load_capital_efficiency_contract(
            root / "config/yci0_rp1/capital_efficiency_contract.v0.1.json"
        )
        result = compile_capital_efficiency(rows, as_of, contract)
        return DimensionState(
            dimension="capital_efficiency",
            level=result.level,
            delta=result.delta,
            delta2=result.delta2,
            state=result.state,
            confidence=result.confidence,
            evidence_refs=result.evidence_refs,
            known_as_of=result.known_as_of,
        )
    except (FileNotFoundError, KeyError, ValueError):
        return DimensionState(
            "capital_efficiency", UNKNOWN, UNKNOWN, UNKNOWN, RealityState.UNKNOWN, "LOW", (), None
        )


def compile_reality_state(evidence: Iterable[RealityEvidence], as_of: str) -> RealityStateCard:
    eligible = [
        item
        for item in evidence
        if item.authority == "RESEARCH"
        and item.known_as_of is not None
        and item.known_as_of <= as_of
    ]
    dimensions: dict[str, DimensionState] = {}
    for name, prefixes in DIMENSION_PREFIXES.items():
        rows = [item for item in eligible if _belongs(item.metric_id, prefixes)]
        if name == "capital_efficiency":
            dimensions[name] = _compile_capital_efficiency_dimension(rows, as_of)
        else:
            dimensions[name] = _compile_dimension(name, rows)
    return RealityStateCard(as_of=as_of, dimensions=dimensions)
