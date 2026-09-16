import unittest
from scripts import yos_fin1_probe as p

class ProbeQualificationTests(unittest.TestCase):
    def test_compile_preserves_real_blockers(self):
        got=p.compile_qualification(
            wind={'status':'FAIL_CLOSED','error_code':'ENTITY_UNRESOLVED'},
            mx={'status':'HUMAN_GATE','error_code':'MIAOXIANG_CREDENTIAL_REQUIRED'},
            wc={'status':'HUMAN_GATE','error_code':'IWENCAI_CREDENTIAL_REQUIRED','browser_cli':{'available':False}},
        )
        self.assertEqual(got['state'],'AWAITING_PROVIDER_CREDENTIALS')
        self.assertEqual(got['probe_a_macro'],'PARTIAL_WIND_FAIL_CLOSED_MIAOXIANG_HUMAN_GATE')
        self.assertEqual(got['probe_b_equity'],'MIAOXIANG_HUMAN_GATE')
        self.assertEqual(got['probe_c_screen'],'IWENCAI_HUMAN_GATE')
        self.assertFalse(got['authority']['capital_authorized'])
        self.assertFalse(got['authority']['execution_authorized'])

    def test_no_provider_success_is_fabricated(self):
        got=p.compile_qualification(
            wind={'status':'PASS'}, mx={'status':'PASS'}, wc={'status':'PASS','candidate_count':5}
        )
        self.assertEqual(got['state'],'THREE_SOURCE_RUNTIME_READY_FOR_PROBE')
        self.assertNotEqual(got['state'],'PROBES_PASSED')

if __name__ == '__main__': unittest.main()
