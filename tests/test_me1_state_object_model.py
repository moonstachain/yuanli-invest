from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "packages/contracts/schemas/vnext/research-target.schema.json"
V2 = ROOT / "packages/contracts/schemas/vnext/research-target-v2.schema.json"


class ME1ResearchTargetTests(unittest.TestCase):
    def test_research_target_v1_identity_is_preserved(self):
        v1 = json.loads(V1.read_text(encoding="utf-8"))
        self.assertEqual(v1["$id"], "urn:yuanli-invest:schema:vnext-research-target:1.0.0")
        self.assertEqual(v1["required"], ["target_type", "target_id", "display_name"])

    def test_research_target_v2_exists_as_semantic_successor(self):
        v2 = json.loads(V2.read_text(encoding="utf-8"))
        self.assertEqual(v2["$id"], "urn:yuanli-invest:schema:vnext-research-target:2.0.0")
        self.assertIn("canonical_name", v2["properties"])
        self.assertIn("asset_form", v2["properties"])


if __name__ == "__main__":
    unittest.main()
