import copy
import json
import unittest
from pathlib import Path

from scripts import validate_yma55_h4_reference as h4

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "fixtures/replay/yma55_h4/manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def first_case():
    manifest = load(MANIFEST)
    entry = manifest["mechanisms"]["MRM-D"]["cases"][0]
    return load(ROOT / entry["path"])


class YMA55H4ValidatorTests(unittest.TestCase):
    def assert_rejected(self, fn, *args):
        with self.assertRaises(ValueError):
            fn(*args)

    def test_repository_h4_reference_passes(self):
        h4.main()

    def test_missing_null_is_rejected(self):
        case = first_case()
        case["t0"]["hypothesis_set"].pop("null")
        self.assert_rejected(h4.validate_case_contract, case)

    def test_zero_alternatives_is_rejected(self):
        case = first_case()
        case["t0"]["hypothesis_set"]["alternatives"] = []
        self.assert_rejected(h4.validate_case_contract, case)

    def test_unhydrated_case_cannot_claim_gold_qualification(self):
        case = first_case()
        case["gold_qualified"] = True
        self.assert_rejected(h4.validate_case_contract, case)

    def test_t0_runner_payload_cannot_contain_settlement(self):
        case = first_case()
        runner_input = copy.deepcopy(case["t0"])
        runner_input["settlement"] = case["settlement"]
        self.assert_rejected(h4.validate_runner_input, runner_input)

    def test_prior_violation_cannot_encode_sell_action(self):
        self.assert_rejected(
            h4.validate_research_only_payload,
            {"posterior_effect": "PRIMARY_BREAK", "trade_action": "sell"},
        )

    def test_non_transferable_prior_cannot_remain_active(self):
        self.assert_rejected(
            h4.validate_prior_application,
            {"overall_transferability": "NON_TRANSFERABLE", "prior_application_state": "ACTIVE"},
        )

    def test_wrong_mechanism_lucky_outcome_cannot_score_epistemic_success(self):
        self.assert_rejected(
            h4.validate_settlement_semantics,
            {
                "outcome_class": "WRONG_MECHANISM_LUCKY_DIRECTION_CANDIDATE",
                "epistemic_success": True,
                "mechanism_resolution": "wrong",
                "expression_resolution": "profitable",
            },
        )

    def test_unresolved_case_cannot_be_forced_resolved(self):
        self.assert_rejected(
            h4.validate_settlement_semantics,
            {
                "outcome_class": "UNRESOLVED",
                "epistemic_success": True,
                "mechanism_resolution": "primary_confirmed",
                "expression_resolution": "unresolved",
            },
        )


if __name__ == "__main__":
    unittest.main()
