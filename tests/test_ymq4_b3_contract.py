from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20260908123000_ymq4_b3_dynamic_beta.sql"


class B3DatabaseContractTests(unittest.TestCase):
    def migration_text(self):
        return MIGRATION.read_text(encoding="utf-8").lower()

    def test_b3_rpcs_and_canonical_b2_gate_are_frozen(self):
        text = self.migration_text()
        self.assertIn("public.ymq4_b3_read_b2_canonical", text)
        self.assertIn("public.ymq4_b3_record_gate", text)
        self.assertIn("runtime.reality_gate_runs", text)
        self.assertIn("'ymq4-b3'", text)
        self.assertIn("'ymq4-b2'", text)
        self.assertIn("8907b60a-445c-4396-8e51-29e6f36620fb", text)

    def test_b3_gate_accepts_both_scientific_outcomes_but_one_physical_status(self):
        text = self.migration_text()
        self.assertIn("b3_dynamic_beta_materialized_pass", text)
        self.assertIn("dynamic_beta_beats_b2", text)
        self.assertIn("dynamic_beta_does_not_beat_b2", text)

    def test_b3_rpcs_are_service_role_only(self):
        text = self.migration_text()
        self.assertIn("from public, anon, authenticated", text)
        self.assertIn("to service_role", text)
        self.assertNotIn("grant select on runtime.reality_gate_runs", text)
        self.assertNotIn("grant select on pit.decision_asof_values", text)

    def test_b4_b7_and_trading_are_fail_closed(self):
        text = self.migration_text()
        self.assertIn("b4_b7_executed", text)
        self.assertIn("trading_action", text)


if __name__ == "__main__":
    unittest.main()
