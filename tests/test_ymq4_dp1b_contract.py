import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20260908060000_ymq4_dp1b_historical_backfill.sql"
CONFIG = ROOT / "config/ymq4/gold_dp1b_backfill.v0.1.json"


class TestDP1BContract(unittest.TestCase):
    def test_migration_freezes_fail_closed_panel_and_rpcs(self):
        self.assertTrue(MIGRATION.exists(), "DP1-B migration must exist before cloud apply")
        sql = MIGRATION.read_text(encoding="utf-8").lower()
        self.assertIn("pit.decision_asof_values", sql)
        self.assertIn("known_as_of <= decision_date", sql)
        for fn in ("ymq4_dp1b_ingest_source", "ymq4_dp1b_upsert_panel", "ymq4_dp1b_readback"):
            self.assertIn(fn, sql)
        self.assertIn("enable row level security", sql)
        self.assertIn("revoke all", sql)
        self.assertIn("anon", sql)
        self.assertIn("authenticated", sql)
        self.assertIn("grant execute", sql)
        self.assertIn("service_role", sql)

    def test_source_registry_has_all_frozen_core_sources(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(config["future_leakage_tolerance"], 0)
        self.assertEqual(config["minimum_replay_month_coverage"], 0.80)
        source_ids = {item["source_id"] for item in config["sources"].values()}
        self.assertEqual(
            source_ids,
            {
                "worldbank_pinksheet_gold",
                "fred_cpiaucsl",
                "fred_dtb3",
                "fred_dtwexm",
                "fred_dtwexbgs",
                "fred_dfii10",
            },
        )


if __name__ == "__main__":
    unittest.main()
