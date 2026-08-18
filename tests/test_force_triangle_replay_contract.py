import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ForceTriangleReplayContractTests(unittest.TestCase):
    def test_replay_can_link_pnx_without_breaking_legacy_replays(self):
        schema = json.loads(
            (ROOT / "packages" / "contracts" / "schemas" / "replay.schema.json").read_text(encoding="utf-8")
        )
        body = schema["allOf"][1]
        required = set(body["required"])
        for field in (
            "paradigm_snapshot_id",
            "stage_snapshot_id",
            "convexity_profile_id",
            "force_triangle_snapshot_id",
        ):
            self.assertIn(field, body["properties"])
            self.assertNotIn(field, required)

    def test_replay_modes_are_closed(self):
        schema = json.loads(
            (ROOT / "packages" / "contracts" / "schemas" / "replay.schema.json").read_text(encoding="utf-8")
        )
        modes = set(schema["allOf"][1]["properties"]["force_triangle_mode"]["enum"])
        self.assertEqual(
            modes,
            {"legacy_narrative_only", "pnx_pre_registered", "pnx_reconstructed_partial"},
        )

    def test_three_cycle_replay_specs_exist(self):
        base = ROOT / "docs" / "methodology" / "historical-calibration"
        for filename in (
            "gold-replay-set-v0.1.md",
            "pc-internet-1995-replay-v0.1.md",
            "mobile-internet-2008-replay-v0.1.md",
            "ai-2023-replay-v0.1.md",
        ):
            self.assertTrue((base / filename).is_file(), filename)

    def test_replay_specs_keep_pre_registration_boundary(self):
        base = ROOT / "docs" / "methodology" / "historical-calibration"
        text = (base / "gold-replay-set-v0.1.md").read_text(encoding="utf-8")
        self.assertIn("pre_registered_reconstruction", text)
        self.assertIn("point-in-time", text)
        self.assertIn("失败也入 Gold", text)


if __name__ == "__main__":
    unittest.main()
