import unittest
from scripts import ymq_gold2_converge_yios as converge

class Gold2ConvergenceTests(unittest.TestCase):
    def test_yios_gold_state_compiles_without_authority_escalation(self):
        unified = converge.compile_unified_state(converge.load_yios_state())
        self.assertEqual(unified["source_panel"], "gold_core_monthly_v0.1")
        self.assertEqual(unified["property_drift_state"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(unified["expectation_reality_state"], "INDETERMINATE")
        self.assertEqual(unified["valuation_state"], "UNIDENTIFIABLE")
        self.assertFalse(unified["authority_state"]["capital_authorized"])
        self.assertFalse(unified["authority_state"]["execution_authorized"])

    def test_missing_domains_stay_explicit_unknowns(self):
        unified = converge.compile_unified_state(converge.load_yios_state())
        self.assertEqual(unified["fiscal_sovereign_state"], "UNKNOWN_NOT_EXPLICIT_AT_T0")
        self.assertEqual(unified["crowding_state"], "UNKNOWN_NOT_EXPLICIT_AT_T0")
        self.assertIn("fiscal_sovereign_state_not_explicit_in_yios_t0", unified["unknowns"])
        self.assertIn("crowding_state_not_explicit_in_yios_t0", unified["unknowns"])

if __name__ == "__main__":
    unittest.main()
