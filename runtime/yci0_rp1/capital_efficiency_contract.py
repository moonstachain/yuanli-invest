from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

MANDATORY_COMPONENTS = ('INCREMENTAL_ROIC', 'CASH_CONVERSION', 'CAPITAL_INTENSITY')
REQUIRED_COHORTS = ('HYPERSCALER', 'COMPUTE', 'NETWORKING', 'POWER_ELECTRICAL')
DIRECTIONS = {'HIGHER_IS_MORE_EFFICIENT', 'LOWER_IS_MORE_EFFICIENT'}
REPRESENTATIVES = {
    'HYPERSCALER': 'MSFT',
    'COMPUTE': 'NVDA',
    'NETWORKING': 'ANET',
    'POWER_ELECTRICAL': 'ETN',
}
PREFIX = 'AIINFRA.CAPITAL_EFFICIENCY'


@dataclass(frozen=True)
class CapitalEfficiencyMetricSpec:
    metric_id: str
    cohort: str
    entity_id: str
    component: str
    directionality: str
    unit: str
    authority: str
    pit_policy: str
    minimum_derived_observations: int
    minimum_raw_quarters: int


@dataclass(frozen=True)
class CapitalEfficiencyContract:
    contract_id: str
    authority: str
    mandatory_components: tuple[str, ...]
    required_cohorts: tuple[str, ...]
    representatives: dict[str, str]
    metrics: dict[str, CapitalEfficiencyMetricSpec]

    def metric_spec(self, metric_id: str) -> CapitalEfficiencyMetricSpec:
        try:
            return self.metrics[metric_id]
        except KeyError as exc:
            raise KeyError(f'unregistered capital-efficiency metric: {metric_id}') from exc


def _validate_metric(raw: dict) -> CapitalEfficiencyMetricSpec:
    required = {
        'metric_id', 'cohort', 'entity_id', 'component', 'directionality', 'unit',
        'authority', 'pit_policy', 'minimum_derived_observations', 'minimum_raw_quarters',
    }
    missing = sorted(required - raw.keys())
    if missing:
        raise ValueError(f'metric missing fields: {missing}')
    spec = CapitalEfficiencyMetricSpec(**{key: raw[key] for key in required})
    if spec.cohort not in REQUIRED_COHORTS:
        raise ValueError(f'unknown cohort: {spec.cohort}')
    if spec.component not in MANDATORY_COMPONENTS:
        raise ValueError(f'unknown component: {spec.component}')
    expected = f'{PREFIX}.{spec.cohort}.{spec.entity_id}.{spec.component}'
    if spec.metric_id != expected:
        raise ValueError(f'metric identity mismatch: expected {expected}, got {spec.metric_id}')
    if spec.entity_id != REPRESENTATIVES[spec.cohort]:
        raise ValueError(f'unknown representative for cohort {spec.cohort}: {spec.entity_id}')
    if spec.directionality not in DIRECTIONS:
        raise ValueError(f'unknown directionality: {spec.directionality}')
    if spec.authority != 'RESEARCH':
        raise ValueError(f'authority must be RESEARCH: {spec.metric_id}')
    if spec.minimum_derived_observations != 4 or spec.minimum_raw_quarters < 8:
        raise ValueError(f'invalid observation minimums: {spec.metric_id}')
    return spec


def load_capital_efficiency_contract(path: str | Path) -> CapitalEfficiencyContract:
    raw = json.loads(Path(path).read_text(encoding='utf-8'))
    mandatory = tuple(raw.get('mandatory_components') or ())
    cohorts = tuple(raw.get('required_cohorts') or ())
    representatives = dict(raw.get('representatives') or {})
    if mandatory != MANDATORY_COMPONENTS:
        raise ValueError(f'mandatory components must equal {MANDATORY_COMPONENTS}')
    if cohorts != REQUIRED_COHORTS:
        raise ValueError(f'required cohorts must equal {REQUIRED_COHORTS}')
    if representatives != REPRESENTATIVES:
        raise ValueError(f'representatives must equal {REPRESENTATIVES}')
    if raw.get('authority') != 'RESEARCH':
        raise ValueError('contract authority must be RESEARCH')

    metrics: dict[str, CapitalEfficiencyMetricSpec] = {}
    for item in raw.get('metrics') or []:
        spec = _validate_metric(item)
        if spec.metric_id in metrics:
            raise ValueError(f'duplicate metric_id: {spec.metric_id}')
        metrics[spec.metric_id] = spec
    expected_count = len(REQUIRED_COHORTS) * len(MANDATORY_COMPONENTS)
    if len(metrics) != expected_count:
        raise ValueError(f'expected {expected_count} metrics, got {len(metrics)}')
    expected_ids = {
        f'{PREFIX}.{cohort}.{REPRESENTATIVES[cohort]}.{component}'
        for cohort in REQUIRED_COHORTS for component in MANDATORY_COMPONENTS
    }
    if set(metrics) != expected_ids:
        raise ValueError('metric registry does not cover exact frozen cohort/entity/component cross-product')

    return CapitalEfficiencyContract(
        contract_id=str(raw.get('contract_id') or ''),
        authority='RESEARCH',
        mandatory_components=mandatory,
        required_cohorts=cohorts,
        representatives=representatives,
        metrics=metrics,
    )
