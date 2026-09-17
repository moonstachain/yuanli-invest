import json
import tempfile
import unittest
from pathlib import Path

from runtime.yci0_rp1.capital_efficiency_contract import load_capital_efficiency_contract

CONTRACT = Path('config/yci0_rp1/capital_efficiency_contract.v0.1.json')


class CapitalEfficiencyContractTests(unittest.TestCase):
    def test_contract_has_exact_mandatory_components_and_cohorts(self):
        c = load_capital_efficiency_contract(CONTRACT)
        self.assertEqual(c.mandatory_components, ('INCREMENTAL_ROIC', 'CASH_CONVERSION', 'CAPITAL_INTENSITY'))
        self.assertEqual(c.required_cohorts, ('HYPERSCALER', 'COMPUTE', 'NETWORKING', 'POWER_ELECTRICAL'))
        self.assertEqual(len(c.metrics), 12)

    def test_metric_ids_encode_cohort_entity_component_and_direction(self):
        c = load_capital_efficiency_contract(CONTRACT)
        spec = c.metric_spec('AIINFRA.CAPITAL_EFFICIENCY.HYPERSCALER.MSFT.INCREMENTAL_ROIC')
        self.assertEqual(spec.entity_id, 'MSFT')
        self.assertEqual(spec.cohort, 'HYPERSCALER')
        self.assertEqual(spec.directionality, 'HIGHER_IS_MORE_EFFICIENT')
        burden = c.metric_spec('AIINFRA.CAPITAL_EFFICIENCY.POWER_ELECTRICAL.ETN.CAPITAL_INTENSITY')
        self.assertEqual(burden.directionality, 'LOWER_IS_MORE_EFFICIENT')

    def test_all_specs_are_research_only_and_have_frozen_pit_minimums(self):
        c = load_capital_efficiency_contract(CONTRACT)
        for spec in c.metrics.values():
            self.assertEqual(spec.authority, 'RESEARCH')
            self.assertIn(spec.directionality, {'HIGHER_IS_MORE_EFFICIENT', 'LOWER_IS_MORE_EFFICIENT'})
            self.assertEqual(spec.minimum_derived_observations, 4)
            expected = {'INCREMENTAL_ROIC': 11, 'CASH_CONVERSION': 7, 'CAPITAL_INTENSITY': 7}[spec.component]
            self.assertEqual(spec.minimum_raw_quarters, expected)
            self.assertIn('KNOWN_AS_OF', spec.pit_policy)
            self.assertIn('RAW_HASH_LINEAGE', spec.pit_policy)

    def test_duplicate_metric_id_fails_closed(self):
        raw = json.loads(CONTRACT.read_text())
        raw['metrics'].append(dict(raw['metrics'][0]))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'contract.json'
            path.write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError, 'duplicate metric_id'):
                load_capital_efficiency_contract(path)

    def test_identity_mismatch_fails_closed(self):
        raw = json.loads(CONTRACT.read_text())
        raw['metrics'][0]['entity_id'] = 'WRONG'
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'contract.json'
            path.write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError, 'metric identity mismatch'):
                load_capital_efficiency_contract(path)


if __name__ == '__main__':
    unittest.main()
