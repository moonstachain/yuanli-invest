from pathlib import Path
import copy
import json
import unittest

from scripts import validate_me1_state_object_model as me1

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


class ME1SchemaTests(unittest.TestCase):
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


class ME1RelationalNegativeTests(unittest.TestCase):
    def bundle(self):
        return me1.load_fixture_bundle()

    def assert_rejected(self, fn, bundle):
        with self.assertRaises(ValueError):
            fn(bundle)

    def test_engine_migration_same_thesis_id_is_rejected(self):
        b = self.bundle()
        old = copy.deepcopy(b["theses"][0])
        new = copy.deepcopy(old)
        new["lifecycle"]["revision"] = 2
        new["lifecycle"]["supersedes_revision"] = 1
        new["identity_core"]["primary_engine"] = "ENG-R"
        b["thesis_histories"] = {old["engine_thesis_id"]: [old, new]}
        self.assert_rejected(me1.validate_no_silent_migration, b)

    def test_passport_engine_mismatch_is_rejected(self):
        b = self.bundle(); b["passports"][0]["primary_engine"] = "ENG-R"
        self.assert_rejected(me1.validate_engine_consistency, b)

    def test_wrong_engine_book_membership_is_rejected(self):
        b = self.bundle(); b["books"][0]["book_id"] = "BOOK-R"
        self.assert_rejected(me1.validate_engine_consistency, b)

    def test_legacy_projection_cannot_create_thesis(self):
        b = self.bundle(); b["projections"][0]["auto_engine_thesis_creation_authorized"] = True
        self.assert_rejected(me1.validate_authority_integrity, b)

    def test_legacy_read_model_write_back_is_rejected(self):
        b = self.bundle(); b["legacy_read_models"][0]["write_back_prohibited"] = False
        self.assert_rejected(me1.validate_authority_integrity, b)

    def test_settled_thesis_revision_is_rejected(self):
        b = self.bundle()
        settled = copy.deepcopy(b["theses"][0]); settled["lifecycle"]["status"] = "settled"; settled["lifecycle"]["settlement_ref"] = "SETTLE-1"
        later = copy.deepcopy(settled); later["lifecycle"]["revision"] = 2; later["lifecycle"]["supersedes_revision"] = 1; later["lifecycle"]["status"] = "active"
        b["thesis_histories"] = {settled["engine_thesis_id"]: [settled, later]}
        self.assert_rejected(me1.validate_lifecycle_consistency, b)

    def test_invalidated_thesis_new_active_passport_is_rejected(self):
        b = self.bundle(); t = b["theses"][0]; t["lifecycle"]["status"] = "invalidated"; t["falsification"]["invalidation_reason"] = "falsified"; t["falsification"]["triggered_falsifier_refs"] = ["F-NVDA-C-1"]; b["passports"][0]["lifecycle"]["status"] = "active"
        self.assert_rejected(me1.validate_lifecycle_consistency, b)

    def test_double_primary_book_membership_is_rejected(self):
        b = self.bundle(); duplicate = copy.deepcopy(b["books"][0]); duplicate["book_state_id"] = "BS-DUPLICATE"; duplicate["book_id"] = "BOOK-C"; b["books"].append(duplicate)
        self.assert_rejected(me1.validate_identity_integrity, b)

    def test_book_state_without_as_of_is_rejected(self):
        b = self.bundle(); del b["books"][0]["as_of"]
        self.assert_rejected(me1.validate_bundle_shapes, b)

    def test_future_knowledge_is_rejected(self):
        b = self.bundle(); b["theses"][0]["evidence"]["known_as_of"] = "2026-08-22T00:30:00+08:00"; b["theses"][0]["evidence"]["knowledge_cutoff"] = "2026-08-21T23:59:00+08:00"
        self.assert_rejected(me1.validate_pit_integrity, b)

    def test_trading_authority_is_rejected(self):
        b = self.bundle(); b["passports"][0]["authority"]["trade_execution_authority"] = True
        self.assert_rejected(me1.validate_authority_integrity, b)

    def test_eng_cash_is_rejected(self):
        b = self.bundle(); b["theses"][0]["identity_core"]["primary_engine"] = "ENG-CASH"; b["passports"][0]["primary_engine"] = "ENG-CASH"
        self.assert_rejected(me1.validate_engine_consistency, b)

    def test_unknown_engine_without_authority_is_rejected(self):
        b = self.bundle(); b["theses"][0]["identity_core"]["primary_engine"] = "ENG-Y"; b["theses"][0]["identity_core"]["engine_authority_ref"] = None; b["passports"][0]["primary_engine"] = "ENG-Y"
        self.assert_rejected(me1.validate_engine_consistency, b)

    def test_recorded_at_cannot_replace_known_as_of(self):
        b = self.bundle(); b["theses"][0]["evidence"]["known_as_of"] = None
        self.assert_rejected(me1.validate_pit_integrity, b)

    def test_research_target_v1_redefinition_is_rejected(self):
        b = self.bundle(); b["successor_map"]["historical_identities"][0]["redefined_in_place"] = True
        self.assert_rejected(me1.validate_historical_successor_policy, b)

    def test_v1_target_cannot_gain_thesis_authority(self):
        b = self.bundle(); b["successor_map"]["historical_identities"][0]["future_write_authority"] = True
        self.assert_rejected(me1.validate_historical_successor_policy, b)

    def test_positive_fixture_bundle_is_valid(self):
        b = self.bundle()
        me1.validate_bundle_shapes(b)
        me1.validate_identity_integrity(b)
        me1.validate_reference_integrity(b)
        me1.validate_engine_consistency(b)
        me1.validate_lifecycle_consistency(b)
        me1.validate_no_silent_migration(b)
        me1.validate_pit_integrity(b)
        me1.validate_authority_integrity(b)


if __name__ == "__main__":
    unittest.main()
