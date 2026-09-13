from pathlib import Path
import copy
import json
import unittest

from jsonschema import Draft202012Validator
from scripts import validate_ymq_os0_g0 as ymq

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "ymq_os0" / "ymq_os0_contract.v0.1.json"
SCHEMAS = ROOT / "packages" / "contracts" / "schemas" / "ymq"
YIOS0_STATUS = ROOT / "docs" / "architecture" / "yios0" / "YIOS0-STATUS-MATRIX.md"

EXPECTED_PLANES = [
    "LAW_CONTROL",
    "EVIDENCE_RUNTIME_TRUTH",
    "EXPERIMENT_COMPUTE",
    "EXPERIENCE_PROJECTION",
]
EXPECTED_OBJECTS = [
    "SourceSnapshot",
    "ObservationPIT",
    "FeaturePIT",
    "StatePIT",
    "TransmissionEdgePIT",
    "ResearchClaim",
    "CapabilityRun",
    "ResearchSettlement",
    "LearningDelta",
]
EXPECTED_ENGINES = [
    ("MQE1", "Macro Reality Engine"),
    ("MQE2", "Industrial Reality Engine"),
    ("MQE3", "Narrative × Herding Engine"),
    ("MQE4", "Dynamic Transmission Engine"),
    ("MQE5", "Price × Payoff Engine"),
]
SCHEMA_FILES = [
    "source_snapshot.schema.json",
    "observation_pit.schema.json",
    "feature_pit.schema.json",
    "state_pit.schema.json",
    "transmission_edge_pit.schema.json",
    "research_claim.schema.json",
    "capability_run.schema.json",
    "research_settlement.schema.json",
    "learning_delta.schema.json",
]


def load_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def load_schema(name):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


class YMQOS0ContractTests(unittest.TestCase):
    def test_program_identity_and_parent_scope(self):
        cfg = load_config()
        self.assertEqual(cfg["identity"]["program_id"], "YMQ-OS0-G0")
        self.assertEqual(cfg["parent_authority"]["system_id"], "YIOS0")
        self.assertEqual(cfg["parent_authority"]["scope"], "L2-L8_RESEARCH_SIDE_ONLY")
        self.assertFalse(cfg["parent_authority"]["parallel_investment_os"])

    def test_physical_planes_are_exact_and_provider_neutral(self):
        cfg = load_config()
        self.assertEqual([p["id"] for p in cfg["physical_planes"]], EXPECTED_PLANES)
        for plane in cfg["physical_planes"]:
            self.assertEqual(len(plane["primary_authority_roles"]), 1)
            self.assertTrue(plane["provider_replaceable"])
        for key in ("law_control", "evidence_runtime_truth", "experiment_compute", "experience_projection"):
            self.assertTrue(cfg["provider_policy"][key]["replaceable"])

    def test_research_loop_and_objects_are_exact(self):
        cfg = load_config()
        self.assertEqual(
            cfg["research_loop"],
            [
                "External Reality", "Evidence Snapshot", "PIT Observation",
                "PIT Feature", "PIT State", "Transmission", "Capability Run",
                "Research Settlement", "LearningDelta",
            ],
        )
        self.assertEqual([o["type"] for o in cfg["canonical_objects"]], EXPECTED_OBJECTS)

    def test_engine_roles_are_exact(self):
        cfg = load_config()
        self.assertEqual([(e["id"], e["name"]) for e in cfg["engines"]], EXPECTED_ENGINES)

    def test_pit_and_unknown_laws_are_fail_closed(self):
        cfg = load_config()
        self.assertEqual(cfg["pit_time_semantics"]["replay_rule"], "known_as_of <= T0")
        self.assertEqual(cfg["pit_time_semantics"]["unknown_semantics"], "DENY")
        self.assertTrue(cfg["pit_time_semantics"]["later_revision_substitution_prohibited"])

    def test_research_and_capital_authorities_are_separate(self):
        cfg = load_config()
        self.assertEqual(cfg["laws"]["research_pass_vs_capital_pass"], "NOT_EQUAL")
        self.assertEqual(
            cfg["laws"]["authority_separation"],
            ["ResearchAuthority", "CapitalAuthority", "ExecutionAuthority"],
        )
        self.assertFalse(cfg["authority"]["capital_authorized"])
        self.assertFalse(cfg["authority"]["execution_authorized"])
        self.assertFalse(cfg["authority"]["broker_authorized"])
        self.assertFalse(cfg["authority"]["real_capital_movement_authorized"])

    def test_physical_pass_can_coexist_with_scientific_no_go(self):
        cfg = load_config()
        pair = {"physical_status": "PHYSICAL_PASS", "scientific_status": "SCIENTIFIC_NO_GO"}
        self.assertIn(pair, cfg["settlement_semantics"]["valid_status_combinations"])

    def test_ymq4_lineage_is_not_renumbered_or_promoted(self):
        cfg = load_config()
        lineage = cfg["ymq4_lineage"]
        self.assertTrue(lineage["preserve_historical_ids"])
        self.assertFalse(lineage["ymq4_equals_mqe4_canon"])
        self.assertEqual(lineage["b3"]["scientific_status"], "SCIENTIFIC_NO_GO")
        self.assertEqual(lineage["b3"]["canon_authority"], "NONE")
        status = YIOS0_STATUS.read_text(encoding="utf-8")
        for token in ("YMQ4-B3", "SCIENTIFIC_NO_GO", "DYNAMIC_BETA_DOES_NOT_BEAT_B2", "PR #72"):
            self.assertIn(token, status)

    def test_provider_identity_does_not_grant_authority(self):
        cfg = load_config()
        providers = cfg["provider_policy"]
        self.assertEqual(providers["experiment_compute"]["authority"], "NONE")
        self.assertTrue(providers["experiment_compute"]["replaceable"])
        self.assertEqual(providers["experience_projection"]["authority"], "PROJECTION_ONLY")
        self.assertTrue(providers["provider_identity_never_grants_canon"])

    def test_non_authorizations_are_machine_explicit(self):
        cfg = load_config()
        for key, value in cfg["non_authorizations"].items():
            self.assertFalse(value, key)


class YMQOS0SchemaTests(unittest.TestCase):
    def test_exact_nine_schema_files_and_unique_ids(self):
        self.assertEqual(sorted(p.name for p in SCHEMAS.glob("*.schema.json")), sorted(SCHEMA_FILES))
        ids = []
        for name in SCHEMA_FILES:
            schema = load_schema(name)
            Draft202012Validator.check_schema(schema)
            ids.append(schema["$id"])
        self.assertEqual(len(ids), len(set(ids)))

    def test_research_settlement_has_three_axes(self):
        schema = load_schema("research_settlement.schema.json")
        required = set(schema["required"])
        self.assertTrue({"physical_status", "scientific_status", "authority_status"}.issubset(required))
        self.assertNotIn("status", schema["properties"])

    def test_learning_delta_cannot_rewrite_past(self):
        schema = load_schema("learning_delta.schema.json")
        self.assertEqual(schema["properties"]["rewrite_past_authorized"]["const"], False)
        self.assertEqual(schema["properties"]["requires_human_review"]["const"], True)

    def test_schemas_do_not_grant_action_side_authority(self):
        forbidden = (
            "portfolio_weight_authority",
            "position_sizing_authority",
            "order_submission_authority",
            "live_execution_authority",
            "real_capital_movement_authority",
        )
        for name in SCHEMA_FILES:
            text = (SCHEMAS / name).read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, f"{name}: {token}")


class YMQOS0ValidatorTests(unittest.TestCase):
    def test_validator_accepts_repository_candidate(self):
        ymq.validate_all()

    def test_pit_future_knowledge_is_rejected(self):
        bundle = ymq.positive_fixture_bundle()
        bundle["observation"]["known_as_of"] = "2030-01-01T00:00:00Z"
        with self.assertRaises(ValueError):
            ymq.validate_pit_relations(bundle)

    def test_release_after_known_as_of_is_rejected(self):
        bundle = ymq.positive_fixture_bundle()
        bundle["observation"]["release_time"] = "2020-03-12T00:00:00Z"
        with self.assertRaises(ValueError):
            ymq.validate_pit_relations(bundle)

    def test_vintage_after_known_as_of_is_rejected(self):
        bundle = ymq.positive_fixture_bundle()
        bundle["observation"]["vintage_time"] = "2020-03-12T00:00:00Z"
        with self.assertRaises(ValueError):
            ymq.validate_pit_relations(bundle)

    def test_claim_authority_ceiling_is_enforced(self):
        bundle = ymq.positive_fixture_bundle()
        bundle["claim"]["claim_authority"] = "PRIMARY_EVIDENCE"
        bundle["claim"]["evidence_authority"] = "HYPOTHESIS"
        with self.assertRaises(ValueError):
            ymq.validate_claim_authority(bundle)

    def test_claim_cannot_use_future_state(self):
        bundle = ymq.positive_fixture_bundle()
        bundle["claim"]["as_of"] = "2020-03-13T00:00:00Z"
        with self.assertRaises(ValueError):
            ymq.validate_claim_authority(bundle)

    def test_collapsed_settlement_is_rejected(self):
        settlement = ymq.positive_fixture_bundle()["settlement"]
        settlement["status"] = "PASS"
        with self.assertRaises(ValueError):
            ymq.validate_settlement_separation(settlement)

    def test_learning_past_rewrite_is_rejected(self):
        learning = ymq.positive_fixture_bundle()["learning"]
        learning["rewrite_past_authorized"] = True
        with self.assertRaises(ValueError):
            ymq.validate_learning_forward_only(learning)

    def test_settlement_cannot_predate_run_completion(self):
        bundle = ymq.positive_fixture_bundle()
        bundle["settlement"]["settled_at"] = "2020-03-13T23:59:00Z"
        with self.assertRaises(ValueError):
            ymq.validate_lifecycle_relations(bundle)

    def test_learning_cannot_predate_settlement(self):
        bundle = ymq.positive_fixture_bundle()
        bundle["learning"]["created_at"] = "2020-03-14T00:00:30Z"
        with self.assertRaises(ValueError):
            ymq.validate_lifecycle_relations(bundle)

    def test_research_pass_equal_capital_pass_semantics_are_rejected(self):
        cfg = load_config()
        cfg = copy.deepcopy(cfg)
        cfg["laws"]["research_pass_vs_capital_pass"] = "EQUAL"
        with self.assertRaises(ValueError):
            ymq.validate_contract(cfg)

    def test_nonreplaceable_provider_policy_is_rejected(self):
        cfg = copy.deepcopy(load_config())
        cfg["provider_policy"]["law_control"]["replaceable"] = False
        with self.assertRaises(ValueError):
            ymq.validate_contract(cfg)


if __name__ == "__main__":
    unittest.main()
