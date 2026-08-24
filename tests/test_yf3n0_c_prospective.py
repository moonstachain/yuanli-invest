import json
import unittest
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator
from scripts import yf3n0_prospective as yf3

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "packages" / "contracts" / "schemas" / "yf3n0"
ARCH = ROOT / "docs" / "architecture" / "yf3n0"
PROTOCOL = ARCH / "YF3N0-C-PROTOCOL-v0.1.json"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def forecast(outcome_id, rule_id, probability=None, expected_state=None):
    value = {"outcome_definition_id": outcome_id, "resolution_rule_id": rule_id}
    if probability is not None:
        value["probability"] = probability
    if expected_state is not None:
        value["expected_state"] = expected_state
    return value


def make_binary_primary_prediction(prediction_id="P1_PIP_PERSISTENCE", hypothesis_id="H1_DURATION", outcome_id="OUT-PIP"):
    rule_id = f"RULE-{outcome_id}"
    return {
        "prediction_id": prediction_id,
        "hypothesis_id": hypothesis_id,
        "role": "PRIMARY",
        "outcome_definition_id": outcome_id,
        "resolution_rule_id": rule_id,
        "forecast_channel": "binary",
        "full_forecast": forecast(outcome_id, rule_id, probability=0.80),
        "ablation_forecasts": {
            "ABLATE_PIP": forecast(outcome_id, rule_id, probability=0.55),
            "ABLATE_EAA": forecast(outcome_id, rule_id, probability=0.65),
            "ABLATE_NLP": forecast(outcome_id, rule_id, probability=0.70),
        },
        "baseline_forecast": forecast(outcome_id, rule_id, probability=0.50),
        "falsifiers": ["No sustained voluntary engagement at resolution horizon"],
        "source_evidence_refs": ["SYN-EV-001"],
    }


def make_causal_primary_prediction(prediction_id, hypothesis_id, outcome_id, expected="SUPPORTED"):
    rule_id = f"RULE-{outcome_id}"
    return {
        "prediction_id": prediction_id,
        "hypothesis_id": hypothesis_id,
        "role": "PRIMARY",
        "outcome_definition_id": outcome_id,
        "resolution_rule_id": rule_id,
        "forecast_channel": "causal",
        "full_forecast": forecast(outcome_id, rule_id, expected_state=expected),
        "ablation_forecasts": {
            "ABLATE_PIP": forecast(outcome_id, rule_id, expected_state="PARTIALLY_SUPPORTED"),
            "ABLATE_EAA": forecast(outcome_id, rule_id, expected_state="PARTIALLY_SUPPORTED"),
            "ABLATE_NLP": forecast(outcome_id, rule_id, expected_state="PARTIALLY_SUPPORTED"),
        },
        "baseline_forecast": forecast(outcome_id, rule_id, expected_state="INDETERMINATE"),
        "falsifiers": ["Declared mechanism fails under the frozen resolution rule"],
        "source_evidence_refs": ["SYN-EV-001"],
    }


def make_prediction_contract(secondary_count=0):
    predictions = [
        make_binary_primary_prediction(),
        make_causal_primary_prediction("P2_EAA_PERSISTENCE_OR_DECAY", "H2_EDGE", "OUT-EAA"),
        make_causal_primary_prediction("P3_NLP_ACTIVATION_OR_FAILURE", "H3_LEVERAGE", "OUT-NLP"),
        make_binary_primary_prediction("P4_INTEGRATED_FORCE_POTENTIAL", "H4_CONJUNCTIVE", "OUT-FORCE"),
    ]
    for index in range(secondary_count):
        item = make_binary_primary_prediction(f"S{index + 1}", "H5_WEAKEST_LINK", f"OUT-SECONDARY-{index + 1}")
        item["role"] = "SECONDARY"
        predictions.append(item)
    return {
        "prediction_contract_id": "SYN-PC-001",
        "case_id": "SYN-001",
        "schema_version": "1.0.0",
        "sealed_at": "2026-08-24T00:10:00Z",
        "evidence_digest_sha256": "0" * 64,
        "predictions": predictions,
        "authority": {"capital_authority": False, "trading_authority": False, "canon_authority": False},
    }


def make_resolution_contract():
    outcomes = ["OUT-PIP", "OUT-EAA", "OUT-NLP", "OUT-FORCE"]
    return {
        "resolution_contract_id": "SYN-RC-001",
        "case_id": "SYN-001",
        "schema_version": "1.0.0",
        "sealed_at": "2026-08-24T00:10:00Z",
        "evidence_digest_sha256": "0" * 64,
        "rules": [
            {
                "resolution_rule_id": f"RULE-{outcome}",
                "outcome_definition_id": outcome,
                "event_definition": f"Resolve {outcome} using prospectively declared evidence",
                "resolution_source_rule": "Use dated non-self-report evidence only",
                "resolution_cutoff_rule": "Use evidence known by the declared settlement horizon",
                "allowed_binary_states": ["YES", "NO", "INDETERMINATE"],
                "allowed_causal_states": ["SUPPORTED", "PARTIALLY_SUPPORTED", "FALSIFIED", "INDETERMINATE"],
                "indeterminate_rule": "Return INDETERMINATE when decisive evidence is unavailable",
            }
            for outcome in outcomes
        ],
        "authority": {"post_seal_rule_mutation_authority": False, "capital_authority": False},
    }


def make_synthetic_evidence_seal():
    value = {
        "evidence_seal_id": "SYN-ES-001",
        "case_id": "SYN-001",
        "schema_version": "1.0.0",
        "sealed_at": "2026-08-24T00:05:00Z",
        "knowledge_cutoff": "2026-08-24T00:00:00Z",
        "evidence_manifest": [
            {"evidence_ref": "SYN-EV-001", "source_type": "non_self_report", "known_as_of": "2026-08-23T23:00:00Z", "description": "Synthetic behavior evidence"}
        ],
        "unknowns": ["Future outcome is unknown"],
        "excluded_future_information": ["Any evidence known after cutoff"],
        "evidence_digest_sha256": "0" * 64,
        "authority": {"future_evidence_writeback_authority": False, "capital_authority": False},
    }
    digestable = deepcopy(value)
    digestable.pop("evidence_digest_sha256")
    value["evidence_digest_sha256"] = yf3.sha256_json(digestable)
    return value


def make_synthetic_preregistration_bundle(evidence=None, optional_horizons=None):
    evidence = evidence or make_synthetic_evidence_seal()
    prediction = make_prediction_contract()
    resolution = make_resolution_contract()
    prediction["evidence_digest_sha256"] = evidence["evidence_digest_sha256"]
    resolution["evidence_digest_sha256"] = evidence["evidence_digest_sha256"]
    value = {
        "preregistration_bundle_id": "SYN-PRB-001",
        "case_id": "SYN-001",
        "schema_version": "1.0.0",
        "sealed_at": "2026-08-24T00:10:00Z",
        "evidence_digest_sha256": evidence["evidence_digest_sha256"],
        "prediction_contract": prediction,
        "resolution_contract": resolution,
        "optional_horizons": [] if optional_horizons is None else optional_horizons,
        "bundle_digest_sha256": "0" * 64,
        "authority": {"post_seal_mutation_authority": False, "clock_start_authority": False, "capital_authority": False},
    }
    digestable = deepcopy(value)
    digestable.pop("bundle_digest_sha256")
    value["bundle_digest_sha256"] = yf3.sha256_json(digestable)
    return value


def make_all_pass_gates():
    return {gate: "PASS" for gate in load_json(PROTOCOL)["promotion_gates"]}


class YF3N0CContractTests(unittest.TestCase):
    def test_all_local_schemas_are_valid_draft_202012(self):
        names = {
            "prospective-case.schema.json",
            "evidence-seal.schema.json",
            "prediction-contract.schema.json",
            "resolution-contract.schema.json",
            "preregistration-bundle.schema.json",
            "settlement-record.schema.json",
            "qualification-state.schema.json",
        }
        self.assertEqual({p.name for p in SCHEMA_DIR.glob("*.json")}, names)
        for path in SCHEMA_DIR.glob("*.json"):
            Draft202012Validator.check_schema(load_json(path))

    def test_protocol_freezes_exact_hypotheses_predictions_and_horizons(self):
        protocol = load_json(PROTOCOL)
        self.assertEqual(protocol["hypotheses"], ["H1_DURATION", "H2_EDGE", "H3_LEVERAGE", "H4_CONJUNCTIVE", "H5_WEAKEST_LINK"])
        self.assertEqual(protocol["primary_prediction_ids"], ["P1_PIP_PERSISTENCE", "P2_EAA_PERSISTENCE_OR_DECAY", "P3_NLP_ACTIVATION_OR_FAILURE", "P4_INTEGRATED_FORCE_POTENTIAL"])
        self.assertEqual(protocol["required_horizons"], ["T90", "T180", "T365"])
        self.assertEqual(protocol["model_variants"], ["FULL", "ABLATE_PIP", "ABLATE_EAA", "ABLATE_NLP", "BASELINE"])

    def test_protocol_has_zero_external_authority(self):
        authority = load_json(PROTOCOL)["authority"]
        self.assertTrue(authority)
        self.assertTrue(all(value is False for value in authority.values()))


class YF3N0CSealTests(unittest.TestCase):
    def test_canonical_hash_is_key_order_independent(self):
        left = {"b": 2, "a": {"y": 2, "x": 1}}
        right = {"a": {"x": 1, "y": 2}, "b": 2}
        self.assertEqual(yf3.sha256_json(left), yf3.sha256_json(right))

    def test_mutating_sealed_payload_breaks_digest(self):
        payload = {"case_id": "SYN-001", "claims": ["a"]}
        digest = yf3.sha256_json(payload)
        mutated = deepcopy(payload)
        mutated["claims"].append("b")
        self.assertFalse(yf3.verify_digest(mutated, digest))

    def test_preregistration_must_share_evidence_digest_and_timestamp(self):
        evidence = make_synthetic_evidence_seal()
        bundle = make_synthetic_preregistration_bundle(evidence)
        yf3.validate_atomic_preregistration(evidence, bundle)
        broken = deepcopy(bundle)
        broken["resolution_contract"]["sealed_at"] = "2026-08-25T00:00:00Z"
        broken["bundle_digest_sha256"] = yf3.sha256_json({k: v for k, v in broken.items() if k != "bundle_digest_sha256"})
        with self.assertRaisesRegex(ValueError, "atomic preregistration timestamp mismatch"):
            yf3.validate_atomic_preregistration(evidence, broken)


class YF3N0CPredictionTests(unittest.TestCase):
    def test_prediction_contract_has_exactly_four_primaries(self):
        contract = make_prediction_contract()
        yf3.validate_prediction_contract(contract, load_json(PROTOCOL))
        primaries = [p for p in contract["predictions"] if p["role"] == "PRIMARY"]
        self.assertEqual([p["prediction_id"] for p in primaries], load_json(PROTOCOL)["primary_prediction_ids"])

    def test_more_than_two_secondary_predictions_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "secondary prediction limit exceeded"):
            yf3.validate_prediction_contract(make_prediction_contract(secondary_count=3), load_json(PROTOCOL))

    def test_full_ablations_and_baseline_share_same_outcome_definition(self):
        prediction = make_binary_primary_prediction()
        yf3.validate_model_comparability(prediction)
        broken = deepcopy(prediction)
        broken["ablation_forecasts"]["ABLATE_EAA"]["outcome_definition_id"] = "DIFFERENT-OUTCOME"
        with self.assertRaisesRegex(ValueError, "model outcome definition mismatch"):
            yf3.validate_model_comparability(broken)

    def test_h5_falsified_primitive_cannot_be_compensated(self):
        state = yf3.force_candidate_state({"PIP": "SUPPORTED", "EAA": "FALSIFIED", "NLP": "SUPPORTED"})
        self.assertEqual(state, "NOT_FULL_FORCE_CANDIDATE")


class YF3N0CResolutionTests(unittest.TestCase):
    def test_blind_packet_omits_forecast_probabilities_and_model_variants(self):
        bundle = make_synthetic_preregistration_bundle()
        packet = yf3.build_blind_resolution_packet(bundle, "T180", [{"evidence_ref": "NEW-001"}])
        text = json.dumps(packet, sort_keys=True)
        self.assertNotIn("probability", text)
        self.assertNotIn("ABLATE_PIP", text)
        self.assertNotIn("BASELINE", text)
        self.assertNotIn("brier", text.lower())

    def test_brier_score_uses_only_yes_or_no(self):
        self.assertAlmostEqual(yf3.brier_score(0.8, "YES"), 0.04)
        self.assertAlmostEqual(yf3.brier_score(0.8, "NO"), 0.64)
        self.assertIsNone(yf3.brier_score(0.8, "INDETERMINATE"))

    def test_indeterminate_cannot_be_promoted_to_support(self):
        with self.assertRaisesRegex(ValueError, "invalid causal settlement state"):
            yf3.validate_causal_settlement("INDETERMINATE_AS_SUPPORT")


class YF3N0CHorizonTests(unittest.TestCase):
    def test_horizon_due_dates_are_fixed_day_offsets(self):
        sealed = "2026-08-24T00:00:00Z"
        self.assertEqual(yf3.horizon_due_at(sealed, "T90").isoformat(), "2026-11-22T00:00:00+00:00")
        self.assertEqual(yf3.horizon_due_at(sealed, "T180").isoformat(), "2027-02-20T00:00:00+00:00")
        self.assertEqual(yf3.horizon_due_at(sealed, "T365").isoformat(), "2027-08-24T00:00:00+00:00")

    def test_t730_is_rejected_when_not_predeclared(self):
        with self.assertRaisesRegex(ValueError, "T730 was not preregistered"):
            yf3.validate_optional_horizon(make_synthetic_preregistration_bundle(optional_horizons=[]), "T730")


class YF3N0CQualificationTests(unittest.TestCase):
    def test_evidence_matrix_has_no_global_accuracy_score(self):
        matrix = yf3.build_evidence_matrix([], [])
        serialized = json.dumps(matrix, sort_keys=True).lower()
        self.assertNotIn("global_accuracy", serialized)
        self.assertNotIn("overall_score", serialized)
        self.assertNotIn("three_non_accuracy", serialized)

    def test_unresolved_required_evidence_yields_insufficient_evidence(self):
        gates = make_all_pass_gates()
        gates["C_G3_PRIMITIVE_DISCRIMINATION"] = "INDETERMINATE"
        gates["C_G4_ABLATION_VALUE"] = "INDETERMINATE"
        gates["C_G5_CROSS_DOMAIN_ROBUSTNESS"] = "INDETERMINATE"
        self.assertEqual(yf3.derive_qualification_outcome(gates), "INSUFFICIENT_EVIDENCE")

    def test_constitutional_breach_blocks_canon_promotion(self):
        gates = make_all_pass_gates()
        gates["C_G6_NO_CONSTITUTIONAL_BREACH"] = "FAIL"
        self.assertEqual(yf3.derive_qualification_outcome(gates), "FIRST_PRINCIPLES_CANON_REJECTED")

    def test_all_pass_is_promotion_ready(self):
        self.assertEqual(yf3.derive_qualification_outcome(make_all_pass_gates()), "CANON_PROMOTION_READY")

    def test_ablation_failure_requires_partial_reframe(self):
        gates = make_all_pass_gates()
        gates["C_G4_ABLATION_VALUE"] = "FAIL"
        self.assertEqual(yf3.derive_qualification_outcome(gates), "PARTIAL_CANON_REFRAME_REQUIRED")


if __name__ == "__main__":
    unittest.main()
