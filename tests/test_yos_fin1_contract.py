import copy
import unittest

from scripts import yos_fin1_core as fin1


class Fin1ContractTests(unittest.TestCase):
    def test_contract_provider_roles_and_authority(self):
        c = fin1.load_contract()
        fin1.validate_contract(c)
        self.assertEqual(c['providers']['WIND']['authority_ceiling'], 'EVIDENCE_ONLY')
        self.assertEqual(c['providers']['MIAOXIANG_DATA']['authority_ceiling'], 'EVIDENCE_ONLY')
        self.assertEqual(c['providers']['WENCAI_SCREEN']['authority_ceiling'], 'NO_EVIDENCE_AUTHORITY')

    def test_contract_rejects_action_authority(self):
        c = copy.deepcopy(fin1.load_contract())
        c['authority']['execution_authorized'] = True
        with self.assertRaises(ValueError):
            fin1.validate_contract(c)

    def test_contract_requires_distinct_provider_roots_for_corroboration(self):
        c = fin1.load_contract()
        self.assertTrue(c['anti_echo']['distinct_provider_roots_required'])
        self.assertFalse(c['anti_echo']['same_provider_requery_counts_as_corroboration'])

    def test_contract_has_required_failure_taxonomy(self):
        c = fin1.load_contract()
        required = {
            'AUTH_MISSING','AUTH_REJECTED','QUOTA_OR_CREDIT_BLOCK','ENDPOINT_DRIFT',
            'SCHEMA_DRIFT','ENTITY_UNRESOLVED','PIT_MISSING','SEMANTIC_MISMATCH',
            'PROVIDER_UNAVAILABLE','DISCOVERY_ONLY','UNKNOWN'
        }
        self.assertTrue(required.issubset(set(c['failure_taxonomy'])))


if __name__ == '__main__':
    unittest.main()
