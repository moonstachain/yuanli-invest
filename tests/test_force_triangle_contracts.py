import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "packages" / "contracts" / "schemas"


class ForceTriangleContractTests(unittest.TestCase):
    def load(self, name: str):
        return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))

    def test_three_new_contracts_have_stable_urns(self):
        expected = {
            "paradigm-snapshot.schema.json": "urn:yuanli-invest:schema:paradigm-snapshot:1.0.0",
            "convexity-profile.schema.json": "urn:yuanli-invest:schema:convexity-profile:1.0.0",
            "force-triangle-snapshot.schema.json": "urn:yuanli-invest:schema:force-triangle-snapshot:1.0.0",
        }
        for filename, urn in expected.items():
            self.assertEqual(self.load(filename)["$id"], urn)

    def test_force_triangle_forbids_scalar_score(self):
        schema = self.load("force-triangle-snapshot.schema.json")
        body = schema["allOf"][1]
        self.assertEqual(body["properties"]["scalar_score_prohibited"]["const"], True)
        self.assertNotIn("score", body["properties"])
        self.assertNotIn("position", body["properties"])
        self.assertNotIn("target_price", body["properties"])

    def test_paradigm_is_not_a_timing_model(self):
        schema = self.load("paradigm-snapshot.schema.json")
        body = schema["allOf"][1]
        self.assertEqual(
            body["properties"]["scientific_status"]["const"],
            "interpretive_framework_not_timing_model",
        )

    def test_narrative_stage_supports_residual(self):
        schema = self.load("stage-snapshot.schema.json")
        stages = schema["allOf"][1]["properties"]["stage"]["enum"]
        self.assertIn("residual", stages)

    def test_force_triangle_classifications_are_closed(self):
        schema = self.load("force-triangle-snapshot.schema.json")
        values = set(schema["allOf"][1]["properties"]["classification"]["enum"])
        self.assertEqual(
            values,
            {
                "golden_extreme",
                "latent_dragon",
                "paradigm_bubble",
                "meme_extreme",
                "ordinary_asset",
                "unknown",
            },
        )


if __name__ == "__main__":
    unittest.main()
