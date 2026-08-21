from pathlib import Path
import copy
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "packages/contracts/schemas/vnext"
V1 = VNEXT / "research-target.schema.json"
V2 = VNEXT / "research-target-v2.schema.json"


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


class ME1ThesisPassportSchemaTests(unittest.TestCase):
    def test_engine_thesis_schema_has_immutable_identity_core(self):
        schema = json.loads((VNEXT / "engine-thesis.schema.json").read_text(encoding="utf-8"))
        required = schema["properties"]["identity_core"]["required"]
        self.assertIn("primary_engine", required)
        self.assertIn("opened_at", required)
        self.assertNotIn("enum", schema["properties"]["identity_core"]["properties"]["primary_engine"])

    def test_position_passport_cannot_grant_trade_execution(self):
        schema = json.loads((VNEXT / "position-passport.schema.json").read_text(encoding="utf-8"))
        authority = schema["properties"]["authority"]["properties"]
        self.assertEqual(authority["portfolio_weight_authority"]["const"], False)
        self.assertEqual(authority["trade_execution_authority"]["const"], False)


class ME1BookCompatibilitySchemaTests(unittest.TestCase):
    def test_book_state_requires_point_in_time(self):
        schema = json.loads((VNEXT / "book-state.schema.json").read_text(encoding="utf-8"))
        self.assertIn("as_of", schema["required"])
        snapshot = schema["properties"]["snapshot"]["properties"]
        self.assertEqual(snapshot["append_only"]["const"], True)
        self.assertEqual(snapshot["point_in_time"]["const"], True)

    def test_legacy_read_model_is_non_authoritative(self):
        schema = json.loads((VNEXT / "legacy-rsv-read-model.schema.json").read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(props["projection_only"]["const"], True)
        self.assertEqual(props["machine_authority"]["const"], False)
        self.assertEqual(props["write_back_prohibited"]["const"], True)


if __name__ == "__main__":
    unittest.main()
