import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20260914_ymq_os0_g1_sovereign_stack.sql"
HARDENING = ROOT / "supabase/migrations/20260914_ymq_os0_g1_fk_index_hardening.sql"


class YMQOS0G1SupabaseContractTests(unittest.TestCase):
    def test_additive_migration_reuses_existing_schemas(self):
        sql = MIGRATION.read_text()
        self.assertIn("create table if not exists evidence.claim_receipts", sql)
        self.assertIn("create table if not exists runtime.agent_runs", sql)
        self.assertIn("create table if not exists runtime.research_projections", sql)
        self.assertIn("create table if not exists runtime.learning_deltas", sql)
        self.assertNotIn("create schema ymq", sql.lower())

    def test_runtime_objects_are_rls_protected(self):
        sql = MIGRATION.read_text().lower()
        for table in (
            "evidence.claim_receipts",
            "runtime.agent_runs",
            "runtime.research_projections",
            "runtime.learning_deltas",
        ):
            self.assertIn(f"alter table {table} enable row level security", sql)

    def test_runtime_contract_has_explicit_authority_columns(self):
        sql = MIGRATION.read_text().lower()
        self.assertIn("requested_authority text not null", sql)
        self.assertIn("granted_authority text not null", sql)
        self.assertIn("check (granted_authority = 'research')", sql)
        self.assertIn("check (not can_grant_authority)", sql)

    def test_learning_delta_is_forward_only(self):
        sql = MIGRATION.read_text().lower()
        self.assertIn("effective_after timestamptz not null", sql)
        self.assertIn("check (effective_after >= created_at)", sql)

    def test_foreign_keys_have_leading_covering_indexes(self):
        sql = HARDENING.read_text().lower()
        self.assertIn(
            "on evidence.claim_receipts (source_snapshot_id)", sql
        )
        self.assertIn(
            "on runtime.learning_deltas (source_run_id)", sql
        )


if __name__ == "__main__":
    unittest.main()
