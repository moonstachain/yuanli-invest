import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "packages" / "contracts" / "schemas" / "yf3n0"
ARCH = ROOT / "docs" / "architecture" / "yf3n0"
PROTOCOL = ARCH / "YF3N0-C-PROTOCOL-v0.1.json"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


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
        self.assertEqual(protocol["hypotheses"], [
            "H1_DURATION",
            "H2_EDGE",
            "H3_LEVERAGE",
            "H4_CONJUNCTIVE",
            "H5_WEAKEST_LINK",
        ])
        self.assertEqual(protocol["primary_prediction_ids"], [
            "P1_PIP_PERSISTENCE",
            "P2_EAA_PERSISTENCE_OR_DECAY",
            "P3_NLP_ACTIVATION_OR_FAILURE",
            "P4_INTEGRATED_FORCE_POTENTIAL",
        ])
        self.assertEqual(protocol["required_horizons"], ["T90", "T180", "T365"])
        self.assertEqual(protocol["model_variants"], [
            "FULL", "ABLATE_PIP", "ABLATE_EAA", "ABLATE_NLP", "BASELINE"
        ])

    def test_protocol_has_zero_external_authority(self):
        authority = load_json(PROTOCOL)["authority"]
        self.assertTrue(authority)
        self.assertTrue(all(value is False for value in authority.values()))


if __name__ == "__main__":
    unittest.main()
