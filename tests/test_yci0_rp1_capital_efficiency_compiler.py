import unittest
from pathlib import Path

from runtime.yci0_rp0.contracts import EvidenceStatus, PITAdmissionReason, RealityEvidence, SourceType
from runtime.yci0_rp0.state_compiler import RealityState, compile_reality_state
from runtime.yci0_rp1.capital_efficiency_compiler import compile_capital_efficiency
from runtime.yci0_rp1.capital_efficiency_contract import load_capital_efficiency_contract

CONTRACT = load_capital_efficiency_contract(Path('config/yci0_rp1/capital_efficiency_contract.v0.1.json'))
AS_OF = '2026-08-31T23:59:59Z'
DATES = ['2026-05-01T00:00:00Z', '2026-06-01T00:00:00Z', '2026-07-01T00:00:00Z', '2026-08-01T00:00:00Z']
REPS = {'HYPERSCALER': 'MSFT', 'COMPUTE': 'NVDA', 'NETWORKING': 'ANET', 'POWER_ELECTRICAL': 'ETN'}


def metric_id(cohort, entity, component):
    return f'AIINFRA.CAPITAL_EFFICIENCY.{cohort}.{entity}.{component}'


def series(entity, cohort, component, values, *, entity_override=None, status=EvidenceStatus.PASS):
    out = []
    for i, (when, value) in enumerate(zip(DATES, values), start=1):
        out.append(RealityEvidence(
            evidence_id=f'{entity}-{component}-{i}', metric_id=metric_id(cohort, entity, component),
            entity_id=entity_override or entity, metric_name=component, value=value, unit='ratio', period=when[:10],
            source_type=SourceType.FIRST_PARTY_EVIDENCE, source_name='SEC', source_locator=f'sec://{entity}/{i}',
            observed_at=when, released_at=when, known_as_of=when, retrieved_at=when, revised_at=None,
            vintage='filed', evidence_status=status,
            pit_admission_reason=PITAdmissionReason.PIT_QUALIFIED if status is EvidenceStatus.PASS else PITAdmissionReason.MISSING_REQUIRED_PIT_SEMANTICS,
            receipt_id=f'r-{entity}-{component}-{i}', content_hash=f'h-{entity}-{component}-{i}', authority='RESEARCH',
        ))
    return out


def full_entity(entity, cohort):
    rows = []
    rows += series(entity, cohort, 'INCREMENTAL_ROIC', [0.10, 0.12, 0.15, 0.20])
    rows += series(entity, cohort, 'CASH_CONVERSION', [1.00, 1.05, 1.12, 1.20])
    rows += series(entity, cohort, 'CAPITAL_INTENSITY', [0.20, 0.18, 0.15, 0.11])
    return rows


def full_dimension():
    rows = []
    for cohort, entity in REPS.items():
        rows += full_entity(entity, cohort)
    return rows


class CapitalEfficiencyCompilerTests(unittest.TestCase):
    def test_same_component_different_entities_never_cross_mix(self):
        rows = series('MSFT', 'HYPERSCALER', 'INCREMENTAL_ROIC', [0.10, 0.15, 0.22, 0.32])
        rows += series('NVDA', 'COMPUTE', 'INCREMENTAL_ROIC', [0.80, 0.70, 0.55, 0.35])
        result = compile_capital_efficiency(rows, AS_OF, CONTRACT)
        self.assertEqual(result.entities['MSFT'].components['INCREMENTAL_ROIC'].state, RealityState.ACCELERATING)
        self.assertEqual(result.entities['NVDA'].components['INCREMENTAL_ROIC'].state, RealityState.DECELERATING)

    def test_lower_is_more_efficient_preserves_raw_delta_but_orients_state(self):
        rows = full_entity('ETN', 'POWER_ELECTRICAL')
        result = compile_capital_efficiency(rows, AS_OF, CONTRACT)
        component = result.entities['ETN'].components['CAPITAL_INTENSITY']
        self.assertAlmostEqual(component.raw_delta, -0.04)
        self.assertAlmostEqual(component.raw_delta2, -0.01)
        self.assertEqual(component.state, RealityState.ACCELERATING)
        self.assertAlmostEqual(component.level, 0.11)

    def test_missing_mandatory_component_for_required_cohort_forces_dimension_unknown(self):
        rows = full_dimension()
        missing_id = metric_id('NETWORKING', 'ANET', 'CASH_CONVERSION')
        rows = [row for row in rows if row.metric_id != missing_id]
        result = compile_capital_efficiency(rows, AS_OF, CONTRACT)
        self.assertEqual(result.state, RealityState.UNKNOWN)
        self.assertEqual(result.confidence, 'LOW')
        self.assertEqual(result.cohorts['NETWORKING'].state, RealityState.UNKNOWN)

    def test_wrong_entity_inside_registered_metric_fails_closed(self):
        rows = full_dimension()
        bad_id = metric_id('HYPERSCALER', 'MSFT', 'INCREMENTAL_ROIC')
        rows = [row for row in rows if row.metric_id != bad_id]
        rows += series('MSFT', 'HYPERSCALER', 'INCREMENTAL_ROIC', [0.10, 0.12, 0.15, 0.20], entity_override='NVDA')
        result = compile_capital_efficiency(rows, AS_OF, CONTRACT)
        self.assertEqual(result.entities['MSFT'].state, RealityState.UNKNOWN)
        self.assertEqual(result.state, RealityState.UNKNOWN)

    def test_unregistered_capital_efficiency_metric_forces_dimension_unknown(self):
        rows = full_dimension()
        rogue = rows[0]
        rows.append(RealityEvidence(
            evidence_id='rogue-1', metric_id='AIINFRA.CAPITAL_EFFICIENCY.HYPERSCALER.MSFT.UNREGISTERED',
            entity_id='MSFT', metric_name='UNREGISTERED', value=1.0, unit='ratio', period='2026-08-01',
            source_type=SourceType.FIRST_PARTY_EVIDENCE, source_name='SEC', source_locator='sec://rogue',
            observed_at=rogue.observed_at, released_at=rogue.released_at, known_as_of=rogue.known_as_of,
            retrieved_at=rogue.retrieved_at, revised_at=None, vintage='filed', evidence_status=EvidenceStatus.PASS,
            pit_admission_reason=PITAdmissionReason.PIT_QUALIFIED, receipt_id='r-rogue', content_hash='h-rogue', authority='RESEARCH',
        ))
        result = compile_capital_efficiency(rows, AS_OF, CONTRACT)
        self.assertEqual(result.state, RealityState.UNKNOWN)
        self.assertIn('rogue-1', result.evidence_refs)

    def test_fail_closed_dimension_still_preserves_qualified_raw_metric_deltas(self):
        rows = full_dimension()
        missing_id = metric_id('NETWORKING', 'ANET', 'CASH_CONVERSION')
        rows = [row for row in rows if row.metric_id != missing_id]
        result = compile_capital_efficiency(rows, AS_OF, CONTRACT)
        qualified_id = metric_id('HYPERSCALER', 'MSFT', 'INCREMENTAL_ROIC')
        self.assertEqual(result.state, RealityState.UNKNOWN)
        self.assertAlmostEqual(result.delta[qualified_id], 0.05)
        self.assertAlmostEqual(result.delta2[qualified_id], 0.02)
        self.assertEqual(result.delta[missing_id], 'UNKNOWN')

    def test_four_qualified_cohorts_compile_to_high_confidence_accelerating(self):
        result = compile_capital_efficiency(full_dimension(), AS_OF, CONTRACT)
        self.assertEqual(result.state, RealityState.ACCELERATING)
        self.assertEqual(result.confidence, 'HIGH')
        self.assertEqual(set(result.cohorts), set(REPS))
        self.assertTrue(result.evidence_refs)
        self.assertEqual(result.known_as_of, '2026-08-01T00:00:00Z')

    def test_rp0_integration_uses_g6_semantics_without_affecting_other_dimensions(self):
        card = compile_reality_state(full_dimension(), AS_OF)
        self.assertEqual(card.dimensions['capital_efficiency'].state, RealityState.ACCELERATING)
        self.assertEqual(card.dimensions['capital_efficiency'].confidence, 'HIGH')
        self.assertEqual(card.dimensions['hyperscaler_capex'].state, RealityState.UNKNOWN)
        self.assertEqual(card.dimensions['compute'].state, RealityState.UNKNOWN)
        self.assertEqual(card.dimensions['networking'].state, RealityState.UNKNOWN)
        self.assertEqual(card.dimensions['power_grid'].state, RealityState.UNKNOWN)
        self.assertEqual(card.dimensions['financing_regime'].state, RealityState.UNKNOWN)


if __name__ == '__main__':
    unittest.main()
