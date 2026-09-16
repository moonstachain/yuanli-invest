import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20260916_yci0_rp0_research_loop.sql"


class YCI0RP0SupabaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exists = MIGRATION.exists()
        cls.sql = MIGRATION.read_text(encoding="utf-8").lower() if cls.exists else ""

    def test_migration_exists_and_is_additive_to_existing_lineage(self):
        self.assertTrue(self.exists, "Task 3 migration must exist")
        for table in (
            "runtime.capital_questions",
            "runtime.context_packs",
            "runtime.ai_infra_state_cards",
            "runtime.shadow_settlements",
        ):
            self.assertIn(f"create table if not exists {table}", self.sql)
        self.assertNotIn("create schema yci", self.sql)
        self.assertNotIn("create table if not exists evidence.reality_evidence", self.sql)

    def test_new_objects_link_existing_evidence_and_runtime_objects(self):
        required_refs = (
            "references evidence.source_snapshots(snapshot_id)",
            "references evidence.claim_receipts(claim_receipt_id)",
            "references pit.observations(observation_id)",
            "references runtime.agent_runs(run_id)",
            "references runtime.research_projections(projection_id)",
            "references runtime.reality_gate_runs(run_id)",
            "references runtime.learning_deltas(learning_delta_id)",
        )
        for ref in required_refs:
            self.assertIn(ref, self.sql)

    def test_all_new_tables_are_rls_protected_and_research_only(self):
        for table in (
            "runtime.capital_questions",
            "runtime.context_packs",
            "runtime.ai_infra_state_cards",
            "runtime.shadow_settlements",
        ):
            self.assertIn(f"alter table {table} enable row level security", self.sql)
        self.assertGreaterEqual(self.sql.count("check (authority = 'research')"), 4)

    def test_indexes_cover_question_stage_known_asof_sources_and_review(self):
        expected_fragments = (
            "on runtime.capital_questions (journey_stage, question_id)",
            "on runtime.context_packs (question_id, known_as_of desc)",
            "on runtime.context_packs (source_snapshot_id)",
            "on runtime.ai_infra_state_cards (question_id, journey_stage, known_as_of desc)",
            "on runtime.ai_infra_state_cards (observation_id)",
            "on runtime.ai_infra_state_cards (source_snapshot_id)",
            "on runtime.shadow_settlements (next_review_at, question_id)",
        )
        for fragment in expected_fragments:
            self.assertIn(fragment, self.sql)

    def test_shadow_t0_identity_and_hashes_are_immutable(self):
        self.assertIn("create or replace function runtime.yci0_rp0_guard_shadow_t0_immutable", self.sql)
        self.assertIn("create trigger yci0_rp0_shadow_t0_immutable", self.sql)
        for field in (
            "question_id",
            "run_id",
            "t0_known_as_of",
            "t0_question_hash",
            "t0_context_hash",
            "t0_projection_hash",
        ):
            self.assertRegex(self.sql, rf"new\.{field}\s+is\s+distinct\s+from\s+old\.{field}")

    def test_rpcs_are_security_definer_and_service_role_only(self):
        functions = (
            "public.yci0_rp0_bind_evidence",
            "public.yci0_rp0_read_evidence_bindings",
            "public.yci0_rp0_insert_shadow_settlement",
            "public.yci0_rp0_read_shadow_settlements",
        )
        for function in functions:
            self.assertIn(f"create or replace function {function}", self.sql)
        self.assertGreaterEqual(self.sql.count("security definer"), len(functions))
        for role in ("public", "anon", "authenticated"):
            self.assertRegex(self.sql, rf"revoke all on function public\.yci0_rp0_[^;]+ from [^;]*\b{role}\b")
        self.assertGreaterEqual(self.sql.count("to service_role;"), len(functions))

    def test_rpc_cannot_accept_or_write_capital_execution_authority(self):
        self.assertNotRegex(self.sql, r"authority\s*=\s*'capital'")
        self.assertNotRegex(self.sql, r"authority\s*=\s*'execution'")
        grants = re.findall(r"grant\s+execute\s+on\s+function\s+[^;]+;", self.sql)
        self.assertTrue(grants)
        for grant in grants:
            self.assertRegex(grant, r"\bto\s+service_role;")

    def test_no_anon_or_authenticated_table_write_policies_or_grants(self):
        prohibited = re.compile(
            r"(?:grant\s+(?:insert|update|delete|all).*?\bto\s+(?:anon|authenticated)\b|"
            r"create\s+policy.*?\bto\s+(?:anon|authenticated)\b)",
            re.DOTALL,
        )
        self.assertIsNone(prohibited.search(self.sql))


if __name__ == "__main__":
    unittest.main()
