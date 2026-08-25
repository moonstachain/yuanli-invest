import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from scripts import yf3n0_prospective as yf3

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "packages" / "contracts" / "schemas" / "yf3n0"
ARCH = ROOT / "docs" / "architecture" / "yf3n0"
FIXTURES = ARCH / "fixtures"
PROTOCOL = ARCH / "YF3N0-C-PROTOCOL-v0.1.json"
SLOTS = ARCH / "YF3N0-C-GENESIS-COHORT-SLOTS-v0.1.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_instance(schema_name: str, value) -> None:
    schema = load_json(SCHEMA_DIR / schema_name)
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value))
    if errors:
        raise AssertionError("; ".join(error.message for error in errors[:5]))


class YF3N0CCohortTests(unittest.TestCase):
    def test_genesis_cohort_is_exactly_three_by_four(self):
        slots = load_json(SLOTS)
        yf3.validate_genesis_slots(slots)
        self.assertEqual(len(slots["slots"]), 12)
        self.assertEqual({s["domain"] for s in slots["slots"]}, {"entrepreneurship", "investment_capital", "ai_native_os"})
        self.assertEqual({s["structural_type"] for s in slots["slots"]}, {"full_candidate", "ablation_candidate", "uncertain_candidate", "exogenous_control"})

    def test_v01_slots_do_not_enroll_real_actors(self):
        slots = load_json(SLOTS)
        self.assertTrue(all(slot["actor_ref"] is None for slot in slots["slots"]))
        self.assertTrue(all(slot["enrollment_status"] == "UNFILLED" for slot in slots["slots"]))
        self.assertTrue(all(slot["real_case"] is False for slot in slots["slots"]))

    def test_real_case_enrollment_is_fail_closed(self):
        slots = load_json(SLOTS)
        slot = next(item for item in slots["slots"] if item["slot_id"] == "ENT-FULL-01")
        case = load_json(FIXTURES / "synthetic-full-case.json")
        case["real_case"] = True
        seal = load_json(FIXTURES / "synthetic-evidence-seal.json")
        with self.assertRaisesRegex(ValueError, "real case enrollment not authorized"):
            yf3.validate_case_eligibility(case, slot, seal, {"real_case_enrollment_authorized": False})


class YF3N0CFixtureTests(unittest.TestCase):
    def test_synthetic_gold_chain_validates_end_to_end(self):
        case = load_json(FIXTURES / "synthetic-full-case.json")
        seal = load_json(FIXTURES / "synthetic-evidence-seal.json")
        bundle = load_json(FIXTURES / "synthetic-preregistration-bundle.json")
        validate_instance("prospective-case.schema.json", case)
        validate_instance("evidence-seal.schema.json", seal)
        validate_instance("prediction-contract.schema.json", bundle["prediction_contract"])
        validate_instance("resolution-contract.schema.json", bundle["resolution_contract"])
        validate_instance("preregistration-bundle.schema.json", bundle)
        yf3.validate_evidence_seal(case, seal)
        yf3.validate_atomic_preregistration(seal, bundle)
        yf3.validate_prediction_contract(bundle["prediction_contract"], load_json(PROTOCOL))

    def test_synthetic_settlements_validate_and_respect_horizons(self):
        bundle = load_json(FIXTURES / "synthetic-preregistration-bundle.json")
        settlements = load_json(FIXTURES / "synthetic-settlements.json")
        self.assertEqual([item["horizon"] for item in settlements], ["T90", "T180", "T365"])
        for settlement in settlements:
            validate_instance("settlement-record.schema.json", settlement)
            yf3.validate_settlement_timing(bundle, settlement["horizon"], settlement["settled_at"])
        indeterminate = settlements[0]["binary_resolutions"][0]
        self.assertEqual(indeterminate["resolution"], "INDETERMINATE")
        self.assertTrue(all(value is None for value in indeterminate["model_brier_scores"].values()))

    def test_synthetic_qualification_state_is_schema_valid_and_non_authoritative(self):
        value = load_json(FIXTURES / "synthetic-qualification-state.json")
        validate_instance("qualification-state.schema.json", value)
        self.assertTrue(all(flag is False for flag in value["authority"].values()))

    def test_hard_negative_pack_contains_required_attacks(self):
        attacks = {item["attack_id"] for item in load_json(FIXTURES / "hard-negatives.json")}
        self.assertEqual(attacks, {
            "HN01_POST_CUTOFF_EVIDENCE", "HN02_PREDICTION_MUTATION_AFTER_SEAL", "HN03_RESOLUTION_DRIFT_AFTER_SEAL",
            "HN04_TOO_MANY_SECONDARY_PREDICTIONS", "HN05_ABLATION_OUTCOME_MISMATCH", "HN06_INDETERMINATE_AS_SUPPORT",
            "HN07_EARLY_T365_SETTLEMENT", "HN08_UNDECLARED_T730_EXTENSION", "HN09_REAL_CASE_ENROLLMENT_WITHOUT_GATE",
            "HN10_GLOBAL_ACCURACY_SCORE", "HN11_CAPITAL_AUTHORITY_LEAKAGE", "HN12_H5_COMPENSATION_VIOLATION"
        })


class YF3N0CStateTests(unittest.TestCase):
    def test_state_remains_candidate_only_after_implementation(self):
        state = load_json(ARCH / "YF3N0-C-STATE.json")
        self.assertEqual(state["status"], "IMPLEMENTED_CANDIDATE_AWAITING_HUMAN_REVIEW")
        self.assertFalse(state["real_case_enrollment_authorized"])
        self.assertFalse(state["prediction_clock_start_authorized"])
        self.assertFalse(state["canon_promotion_authorized"])
        self.assertFalse(state["merge_authorized"])

    def test_human_projection_preserves_prediction_vs_postdiction_boundary(self):
        text = (ROOT / "docs" / "human-projection" / "YF3N0-C-PROSPECTIVE-PREDICTION-PROTOCOL-v0.1.md").read_text(encoding="utf-8")
        self.assertIn("预测不是事后解释", text)
        self.assertIn("INDETERMINATE", text)
        self.assertIn("三非不是万能成功预测器", text)
        self.assertIn("PIP ∧ EAA ∧ NLP", text)


if __name__ == "__main__":
    unittest.main()
