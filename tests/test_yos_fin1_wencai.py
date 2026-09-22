import unittest
from scripts import yos_fin1_wencai as wc

class WencaiAdapterTests(unittest.TestCase):
    def test_openapi_missing_key_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError,'AUTH_MISSING'):
            wc.discover_api_key({})

    def test_openapi_request_is_marked_runtime_verification_required(self):
        req=wc.build_openapi_request('低PB且ROE连续三年大于15%的A股')
        self.assertEqual(req['url'],'https://openapi.iwencai.com/v1/query2data')
        self.assertEqual(req['endpoint_authority'],'COMMUNITY_DOCUMENTED_RUNTIME_VERIFICATION_REQUIRED')

    def test_screen_result_never_has_evidence_authority(self):
        body={'status_code':0,'datas':[{'股票代码':'600519','股票简称':'贵州茅台'}],'code_count':1}
        got=wc.normalize_screen_response(body,'低PB高ROE')
        self.assertEqual(got['authority_ceiling'],'NO_EVIDENCE_AUTHORITY')
        self.assertEqual(got['candidate_count'],1)
        self.assertEqual(got['candidates'][0]['code'],'600519')

    def test_browser_cli_is_discovery_only(self):
        got=wc.browser_cli_descriptor('/usr/local/bin/iwencai-query')
        self.assertEqual(got['authority_ceiling'],'NO_CANON_AUTHORITY')
        self.assertEqual(got['role'],'DISCOVERY_ONLY')

if __name__ == '__main__': unittest.main()
