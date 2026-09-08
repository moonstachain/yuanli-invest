from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20260908070000_ymq4_b2_fixed_beta.sql"
READBACK_FIX = ROOT / "supabase/migrations/20260908070500_ymq4_b2_read_panel_json_aggregate.sql"


class B2DatabaseContractTests(unittest.TestCase):
    def migration_text(self):
        return MIGRATION.read_text(encoding="utf-8")

    def test_migration_exists_and_freezes_read_and_gate_rpcs(self):
        text = self.migration_text()
        low = text.lower()
        self.assertIn("create or replace function public.ymq4_b2_read_panel", low)
        self.assertIn("create or replace function public.ymq4_b2_record_gate", low)
        self.assertIn("pit.decision_asof_values", low)
        self.assertIn("runtime.reality_gate_runs", low)
        self.assertIn("'ymq4-b2'", low)

    def test_panel_rpc_exposes_only_required_research_fields(self):
        text = self.migration_text().lower()
        for token in (
            "panel_id", "decision_date", "factor_id", "value_numeric", "known_as_of",
        ):
            self.assertIn(token, text)
        self.assertIn("order by decision_date, factor_id", text)

    def test_rpcs_are_service_role_only(self):
        text = self.migration_text().lower()
        self.assertIn("revoke all", text)
        self.assertIn("from public, anon, authenticated", text)
        self.assertIn("grant execute", text)
        self.assertIn("to service_role", text)
        self.assertNotIn("grant select on pit.decision_asof_values", text)

    def test_readback_hotfix_aggregates_all_rows_into_one_json_value(self):
        text = READBACK_FIX.read_text(encoding="utf-8").lower()
        # PostgreSQL cannot CREATE OR REPLACE a function while changing its
        # return type from SETOF rows to JSONB, so the hotfix must explicitly
        # drop and recreate the same service-role-only RPC.
        self.assertIn("drop function if exists public.ymq4_b2_read_panel(text)", text)
        self.assertIn("create function public.ymq4_b2_read_panel", text)
        self.assertIn("returns jsonb", text)
        self.assertIn("jsonb_agg", text)
        self.assertIn("order by decision_date, factor_id", text)
        self.assertIn("from public, anon, authenticated", text)
        self.assertIn("to service_role", text)
        self.assertNotIn("grant select on pit.decision_asof_values", text)


if __name__ == "__main__":
    unittest.main()
