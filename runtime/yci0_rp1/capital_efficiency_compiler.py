from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from runtime.yci0_rp0.contracts import EvidenceStatus, PITAdmissionReason, RealityEvidence
from runtime.yci0_rp0.state_compiler import RealityState
from .capital_efficiency_contract import CapitalEfficiencyContract, CapitalEfficiencyMetricSpec

UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True)
class ComponentEfficiencyState:
    metric_id: str
    cohort: str
    entity_id: str
    component: str
    level: Any
    raw_delta: Any
    raw_delta2: Any
    state: RealityState
    evidence_refs: tuple[str, ...]
    known_as_of: str | None


@dataclass(frozen=True)
class EntityEfficiencyState:
    entity_id: str
    cohort: str
    components: dict[str, ComponentEfficiencyState]
    state: RealityState
    confidence: str


@dataclass(frozen=True)
class CohortEfficiencyState:
    cohort: str
    entities: dict[str, EntityEfficiencyState]
    state: RealityState
    confidence: str


@dataclass(frozen=True)
class CapitalEfficiencyResult:
    state: RealityState
    confidence: str
    evidence_refs: tuple[str, ...]
    known_as_of: str | None
    level: dict[str, Any]
    delta: Any
    delta2: Any
    entities: dict[str, EntityEfficiencyState]
    cohorts: dict[str, CohortEfficiencyState]


def _safe_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _denorm(value: float) -> int | float:
    return int(value) if float(value).is_integer() else value


def _state_from(delta: float, delta2: float) -> RealityState:
    eps = 1e-12
    if abs(delta) <= eps and abs(delta2) <= eps:
        return RealityState.STABLE
    if delta > eps and delta2 > eps:
        return RealityState.ACCELERATING
    if delta < -eps and delta2 < -eps:
        return RealityState.DECELERATING
    return RealityState.MIXED


def _aggregate(states: list[RealityState]) -> tuple[RealityState, str]:
    if not states or any(state is RealityState.UNKNOWN for state in states):
        return RealityState.UNKNOWN, 'LOW'
    if len(set(states)) == 1:
        return states[0], 'HIGH'
    return RealityState.MIXED, 'MEDIUM'


def _unknown_component(spec: CapitalEfficiencyMetricSpec, rows: list[RealityEvidence]) -> ComponentEfficiencyState:
    refs = tuple(sorted({row.evidence_id for row in rows}))
    known = max((row.known_as_of for row in rows if row.known_as_of), default=None)
    level = rows[-1].value if rows and rows[-1].value is not None else UNKNOWN
    return ComponentEfficiencyState(
        metric_id=spec.metric_id,
        cohort=spec.cohort,
        entity_id=spec.entity_id,
        component=spec.component,
        level=level,
        raw_delta=UNKNOWN,
        raw_delta2=UNKNOWN,
        state=RealityState.UNKNOWN,
        evidence_refs=refs,
        known_as_of=known,
    )


def _compile_component(spec: CapitalEfficiencyMetricSpec, rows: list[RealityEvidence]) -> ComponentEfficiencyState:
    rows = sorted(rows, key=lambda row: ((row.known_as_of or ''), row.evidence_id))
    if len(rows) < spec.minimum_derived_observations:
        return _unknown_component(spec, rows)
    if any(
        row.entity_id != spec.entity_id
        or row.evidence_status is not EvidenceStatus.PASS
        or row.pit_admission_reason is not PITAdmissionReason.PIT_QUALIFIED
        or not row.known_as_of
        for row in rows
    ):
        return _unknown_component(spec, rows)
    numeric = [row for row in rows if _safe_number(row.value) is not None]
    if len(numeric) < spec.minimum_derived_observations:
        return _unknown_component(spec, rows)

    last3 = numeric[-3:]
    v0, v1, v2 = (_safe_number(row.value) for row in last3)
    assert v0 is not None and v1 is not None and v2 is not None
    d_prev = v1 - v0
    raw_delta = v2 - v1
    raw_delta2 = raw_delta - d_prev
    sign = 1.0 if spec.directionality == 'HIGHER_IS_MORE_EFFICIENT' else -1.0
    o0, o1, o2 = v0 * sign, v1 * sign, v2 * sign
    oriented_prev = o1 - o0
    oriented_delta = o2 - o1
    oriented_delta2 = oriented_delta - oriented_prev
    return ComponentEfficiencyState(
        metric_id=spec.metric_id,
        cohort=spec.cohort,
        entity_id=spec.entity_id,
        component=spec.component,
        level=last3[-1].value,
        raw_delta=_denorm(raw_delta),
        raw_delta2=_denorm(raw_delta2),
        state=_state_from(oriented_delta, oriented_delta2),
        evidence_refs=tuple(row.evidence_id for row in numeric),
        known_as_of=max(row.known_as_of for row in numeric if row.known_as_of),
    )


def compile_capital_efficiency(
    evidence: Iterable[RealityEvidence],
    as_of: str,
    contract: CapitalEfficiencyContract,
) -> CapitalEfficiencyResult:
    eligible = [
        row for row in evidence
        if row.authority == 'RESEARCH' and row.known_as_of is not None and row.known_as_of <= as_of
    ]
    by_metric: dict[str, list[RealityEvidence]] = {}
    for row in eligible:
        if row.metric_id.startswith('AIINFRA.CAPITAL_EFFICIENCY.'):
            by_metric.setdefault(row.metric_id, []).append(row)

    unexpected_metric_ids = sorted(set(by_metric) - set(contract.metrics))
    component_by_metric: dict[str, ComponentEfficiencyState] = {}
    for metric_id, spec in contract.metrics.items():
        component_by_metric[metric_id] = _compile_component(spec, by_metric.get(metric_id, []))

    entities: dict[str, EntityEfficiencyState] = {}
    cohorts: dict[str, CohortEfficiencyState] = {}
    for cohort in contract.required_cohorts:
        entity = contract.representatives[cohort]
        components = {
            component: component_by_metric[f'AIINFRA.CAPITAL_EFFICIENCY.{cohort}.{entity}.{component}']
            for component in contract.mandatory_components
        }
        entity_state, entity_confidence = _aggregate([item.state for item in components.values()])
        entity_result = EntityEfficiencyState(
            entity_id=entity,
            cohort=cohort,
            components=components,
            state=entity_state,
            confidence=entity_confidence,
        )
        entities[entity] = entity_result
        cohort_state, cohort_confidence = _aggregate([entity_result.state])
        cohorts[cohort] = CohortEfficiencyState(
            cohort=cohort,
            entities={entity: entity_result},
            state=cohort_state,
            confidence=cohort_confidence,
        )

    state, confidence = _aggregate([cohorts[cohort].state for cohort in contract.required_cohorts])
    if unexpected_metric_ids:
        state, confidence = RealityState.UNKNOWN, 'LOW'
    refs = tuple(sorted({row.evidence_id for row in eligible if row.metric_id.startswith('AIINFRA.CAPITAL_EFFICIENCY.')}))
    known = max((row.known_as_of for row in eligible if row.metric_id.startswith('AIINFRA.CAPITAL_EFFICIENCY.') and row.known_as_of), default=None)
    level = {metric_id: item.level for metric_id, item in component_by_metric.items()}
    delta: Any = {metric_id: item.raw_delta for metric_id, item in component_by_metric.items()}
    delta2: Any = {metric_id: item.raw_delta2 for metric_id, item in component_by_metric.items()}
    return CapitalEfficiencyResult(
        state=state,
        confidence=confidence,
        evidence_refs=refs,
        known_as_of=known,
        level=level,
        delta=delta,
        delta2=delta2,
        entities=entities,
        cohorts=cohorts,
    )
