import unittest
from pathlib import Path

from research_runtime.yma55.replay import load_manifest, load_replay_case, run_replay_case

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "fixtures/replay/yma55_h4/manifest.json"


class YMA55H4ReplayTests(unittest.TestCase):
    def test_manifest_has_exact_three_by_four_matrix(self):
        manifest = load_manifest(MANIFEST)
        self.assertEqual(set(manifest["mechanisms"]), {"MRM-D", "MRM-CR", "MRM-SC"})
        expected = {"GOLD", "NEAR_MISS", "WRONG_MECHANISM", "WRONG_STRIKE"}
        total = 0
        for mechanism in manifest["mechanisms"].values():
            self.assertEqual(set(mechanism["case_types"]), expected)
            self.assertEqual(len(mechanism["cases"]), 4)
            total += len(mechanism["cases"])
        self.assertEqual(total, 12)

    def test_every_manifest_case_exists_and_matches_declared_type(self):
        manifest = load_manifest(MANIFEST)
        for mechanism_id, mechanism in manifest["mechanisms"].items():
            for entry in mechanism["cases"]:
                case = load_replay_case(ROOT / entry["path"])
                self.assertEqual(case["mechanism_family"], mechanism_id)
                self.assertEqual(case["case_type"], entry["case_type"])
                self.assertFalse(case.get("gold_qualified", False))

    def test_settlement_is_not_visible_to_t0_runner(self):
        manifest = load_manifest(MANIFEST)
        first = manifest["mechanisms"]["MRM-D"]["cases"][0]
        case = load_replay_case(ROOT / first["path"])
        result = run_replay_case(case)
        self.assertNotIn("settlement", result["runner_input"])
        self.assertIn("settlement", result)
        self.assertEqual(result["episode_id"], case["episode_id"])

    def test_unhydrated_candidate_cannot_claim_gold_qualification(self):
        manifest = load_manifest(MANIFEST)
        for mechanism in manifest["mechanisms"].values():
            for entry in mechanism["cases"]:
                case = load_replay_case(ROOT / entry["path"])
                if case["evidence_status"] != "hydrated":
                    self.assertFalse(case.get("gold_qualified", False))

    def test_t0_contract_contains_five_layer_inputs_and_competing_hypotheses(self):
        manifest = load_manifest(MANIFEST)
        for mechanism in manifest["mechanisms"].values():
            for entry in mechanism["cases"]:
                case = load_replay_case(ROOT / entry["path"])
                t0 = case["t0"]
                self.assertEqual(set(t0), {"world", "constraint", "transmission", "hypothesis_set", "transferability_template"})
                hs = t0["hypothesis_set"]
                self.assertIn("primary", hs)
                self.assertGreaterEqual(len(hs["alternatives"]), 1)
                self.assertLessEqual(len(hs["alternatives"]), 3)
                self.assertIn("null", hs)
                self.assertTrue(hs["pit_frozen"])


if __name__ == "__main__":
    unittest.main()
