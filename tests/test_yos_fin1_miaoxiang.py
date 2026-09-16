import os, unittest
from scripts import yos_fin1_miaoxiang as mx


class MiaoXiangAdapterTests(unittest.TestCase):
    def test_discover_key_prefers_mx_without_echo(self):
        env={'MX_APIKEY':'secret-a','EASTMONEY_APIKEY':'secret-b'}
        got=mx.discover_api_key(env)
        self.assertEqual(got['source'],'MX_APIKEY')
        self.assertNotIn('secret-a', repr(got))

    def test_missing_auth_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError,'AUTH_MISSING'):
            mx.discover_api_key({})

    def test_request_contract(self):
        req=mx.build_data_request('贵州茅台ROE')
        self.assertEqual(req['url'],'https://mkapi2.dfcfs.com/finskillshub/api/claw/query')
        self.assertEqual(req['payload'],{'toolQuery':'贵州茅台ROE'})

    def test_provider_error_classification(self):
        self.assertEqual(mx.classify_error(113,'今日调用次数已达上限'),'QUOTA_OR_CREDIT_BLOCK')
        self.assertEqual(mx.classify_error(114,'API密钥不存在'),'AUTH_REJECTED')

    def test_normalized_receipt_requires_effective_at_for_evidence(self):
        body={'status':0,'data':{'questionId':'q1','dataTableDTOList':[]}}
        got=mx.normalize_data_response(body,'贵州茅台ROE')
        self.assertEqual(got['authority_ceiling'],'KNOWLEDGE_CANDIDATE_INPUT')
        self.assertIsNone(got['effective_at'])


if __name__ == '__main__': unittest.main()
