import unittest

from research_runtime.yma55.types import (
    HUMAN_KERNEL,
    MechanismHypothesis,
    MechanismHypothesisSet,
    TransferabilityAssessment,
    TransferabilityDimension,
)
from research_runtime.yma55.validation import (
    assert_no_capital_outputs,
    validate_hypothesis_set,
    validate_transferability,
)


def hypothesis(hypothesis_id: str, role: str = "PRIMARY") -> MechanismHypothesis:
    return MechanismHypothesis(
        hypothesis_id=hypothesis_id,
        role=role,
        mechanism_family="MRM-D",
        causal_chain=("binding_constraint", "policy_reaction", "term_premium", "duration_payoff"),
        required_conditions=("constraint_binding",),
        predicted_observables={"long_yield": "DOWN"},
        expected_sequence=("policy_reaction", "long_yield"),
        expected_horizon="3-18m",
        falsifiers=("inflation_reacceleration",),
        breaker="required_sign_reversal",
        supporting_evidence_refs=("evidence:demo",),
        contradicting_evidence_refs=(),
    )


class YMA55H4ContractTests(unittest.TestCase):
    def test_human_kernel_is_exactly_five_layers(self):
        self.assertEqual(
            HUMAN_KERNEL,
            ("WORLD", "CONSTRAINT", "TRANSMISSION", "MECHANISM", "SETTLEMENT"),
        )

    def test_hypothesis_set_requires_primary_alternative_and_null(self):
        invalid = MechanismHypothesisSet(
            hypothesis_set_id="mhs-1",
            as_of="1982-01-01",
            primary=hypothesis("p"),
            alternatives=(hypothesis("a", "ALTERNATIVE"),),
            null=None,
            pit_frozen=True,
        )
        with self.assertRaises(ValueError):
            validate_hypothesis_set(invalid)

    def test_hypothesis_set_rejects_more_than_three_alternatives(self):
        invalid = MechanismHypothesisSet(
            hypothesis_set_id="mhs-2",
            as_of="1982-01-01",
            primary=hypothesis("p"),
            alternatives=tuple(hypothesis(f"a{i}", "ALTERNATIVE") for i in range(4)),
            null=hypothesis("n", "NULL"),
            pit_frozen=True,
        )
        with self.assertRaises(ValueError):
            validate_hypothesis_set(invalid)

    def test_blocking_transferability_mismatch_forces_non_transferable(self):
        dimensions = (
            TransferabilityDimension("monetary_regime", "MISMATCHED", True, ("e1",)),
            TransferabilityDimension("fiscal_capacity", "MATCHED", False, ("e2",)),
            TransferabilityDimension("market_structure", "MATCHED", False, ("e3",)),
            TransferabilityDimension("global_order", "PARTIAL", False, ("e4",)),
            TransferabilityDimension("policy_toolkit", "MATCHED", False, ("e5",)),
        )
        assessment = TransferabilityAssessment(
            assessment_id="ta-1",
            historical_episode_ref="ep-1",
            current_case_ref="current-1",
            mechanism_ref="MRM-D",
            as_of="2026-08-24",
            dimensions=dimensions,
            overall_transferability="HIGH_TRANSFERABILITY",
        )
        with self.assertRaises(ValueError):
            validate_transferability(assessment)

    def test_capital_outputs_are_prohibited(self):
        for field in ("position_size", "target_weight", "buy", "sell", "hold", "trade_action"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    assert_no_capital_outputs({field: "anything"})


if __name__ == "__main__":
    unittest.main()
