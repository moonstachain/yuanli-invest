import unittest
from scripts import yos_fin1_wind as wind


class WindAdapterTests(unittest.TestCase):
    def test_classifies_credit_block(self):
        self.assertEqual(wind.classify_failure('账户积分余额不足，无法完成当前操作'), 'QUOTA_OR_CREDIT_BLOCK')

    def test_classifies_auth_failure(self):
        self.assertEqual(wind.classify_failure('WIND_API_KEY 未配置'), 'AUTH_MISSING')
        self.assertEqual(wind.classify_failure('401 Unauthorized'), 'AUTH_REJECTED')

    def test_build_request_uses_backend_compatible_string_observation(self):
        req = wind.build_macro_request('美国长期实际收益率', observations=3)
        self.assertEqual(req['observation'], '3')

    def test_parse_metric_requires_effective_date_and_code(self):
        payload = {'metrics':[{'meta':{'code':'G1147404','name':'real','source':'Treasury','unit':'%'},'date':['20260915'],'value':[3.05]}]}
        got = wind.parse_metric_payload(payload, expected_code='G1147404')
        self.assertEqual(got['effective_at'], '2026-09-15')
        self.assertEqual(got['value'], 3.05)
        with self.assertRaises(ValueError):
            wind.parse_metric_payload(payload, expected_code='WRONG')


if __name__ == '__main__': unittest.main()
