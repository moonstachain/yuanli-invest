import unittest
from scripts import yos_fin1_core as fin1


class Fin1CoreTests(unittest.TestCase):
    def receipt(self, provider, root, effective='2026-09-15', semantic='US_LONG_REAL_YIELD'):
        return fin1.normalize_receipt(
            provider=provider,
            provider_class='licensed_vendor',
            request_kind='macro_fact',
            query='US long real yield',
            observed_at='2026-09-17T00:00:00Z',
            effective_at=effective,
            instrument_or_series='series-x',
            normalized_fields={'value': 3.05, 'semantic_id': semantic},
            provenance={'source': provider},
            authority_ceiling='EVIDENCE_ONLY',
            evidence_root_id=root,
            response_hash='abc123',
        )

    def test_distinct_provider_roots_can_corroborate(self):
        a = self.receipt('WIND', 'wind:real-yield')
        b = self.receipt('MIAOXIANG', 'mx:real-yield')
        got = fin1.compare_provider_receipts(a, b)
        self.assertEqual(got['status'], 'INDEPENDENT_CORROBORATION_CANDIDATE')
        self.assertEqual(got['independent_root_count'], 2)

    def test_same_provider_requery_is_not_corroboration(self):
        a = self.receipt('WIND', 'wind:real-yield')
        b = self.receipt('WIND', 'wind:real-yield:second-call')
        got = fin1.compare_provider_receipts(a, b)
        self.assertEqual(got['status'], 'SAME_PROVIDER_NOT_CORROBORATION')
        self.assertEqual(got['independent_root_count'], 1)

    def test_pit_mismatch_is_explicit(self):
        a = self.receipt('WIND', 'w', effective='2026-09-15')
        b = self.receipt('MIAOXIANG', 'm', effective='2026-09-12')
        self.assertEqual(fin1.compare_provider_receipts(a, b)['status'], 'PIT_MISMATCH')

    def test_semantic_mismatch_is_explicit(self):
        a = self.receipt('WIND', 'w', semantic='US_LONG_REAL_YIELD')
        b = self.receipt('MIAOXIANG', 'm', semantic='US_10Y_NOMINAL_YIELD')
        self.assertEqual(fin1.compare_provider_receipts(a, b)['status'], 'SEMANTIC_MISMATCH')

    def test_router(self):
        self.assertEqual(fin1.route_request('macro_fact')['primary'], 'WIND')
        self.assertEqual(fin1.route_request('macro_fact')['corroborate_with'], ['MIAOXIANG_DATA'])
        self.assertEqual(fin1.route_request('natural_language_screen')['primary'], 'WENCAI_SCREEN')
        self.assertEqual(fin1.route_request('listed_company_fact')['primary'], 'WIND')
        with self.assertRaises(ValueError):
            fin1.route_request('trade_now')


if __name__ == '__main__': unittest.main()
