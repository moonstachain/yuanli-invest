import unittest

from research_runtime.yma55.prior_violation import evaluate_prior_violation
from research_runtime.yma55.types import (
    MechanismHypothesis,
    MechanismHypothesisSet,
    TransferabilityAssessment,
    TransferabilityDimension,
)


def primary(predicted=None, sequence=("term_premium", "long_yield")):
    return MechanismHypothesis(
        hypothesis_id="primary",
        role="PRIMARY",
        mechanism_family="MRM-D",
        causal_chain=("constraint", "reaction", "term_premium", "duration"),
        required_conditions=("constraint_binding",),
        predicted_observables=predicted or {"term_premium": "UP", "long_yield": "DOWN"},
        expected_sequence=sequence,
        expected_horizon="3-18m",
        falsifiers=("required_sign_reversal",),
        breaker="primary_required_condition_break",
        supporting_evidence_refs=("e:1",),
        contradicting_evidence_refs=(),
    )


def hypothesis_set(pit_frozen=True, predicted=None, sequence=("term_premium", "long_yield")):
    alt = MechanismHypothesis(
        hypothesis_id="alt",
        role="ALTERNATIVE",
        mechanism_family="MRM-D",
        causal_chain=("growth_shock", "safe_haven", "duration"),
        required_conditions=("growth_shock",),
        predicted_observables={"long_yield": "DOWN"},
        expected_sequence=("growth", "long_yield"),
        expected_horizon="1-12m",
        falsifiers=("growth_reacceleration",),
        breaker="growth_shock_absent",
        supporting_evidence_refs=("e:2",),
        contradicting_evidence_refs=(),
    )
    null = MechanismHypothesis(
        hypothesis_id="null",
        role="NULL",
        mechanism_family="FLOW_NULL",
        causal_chain=("positioning", "price_move"),
        required_conditions=("flow_extreme",),
        predicted_observables={"positioning": "EXTREME"},
        expected_sequence=("positioning", "price_move"),
        expected_horizon="days-weeks",
        falsifiers=("no_flow_extreme",),
        breaker="flow_normalizes",
        supporting_evidence_refs=("e:3",),
        contradicting_evidence_refs=(),
    )
    return MechanismHypothesisSet(
        hypothesis_set_id="mhs",
        as_of="1982-01-01",
        primary=primary(predicted, sequence),
        alternatives=(alt,),
        null=null,
        pit_frozen=pit_frozen,
    )


def transferable():
    dims = tuple(
        TransferabilityDimension(name, "MATCHED", False, (f"e:{name}",), mechanism_relevance="critical")
        for name in ("monetary_regime", "fiscal_capacity", "market_structure", "global_order", "policy_toolkit")
    )
    return TransferabilityAssessment(
        assessment_id="ta",
        historical_episode_ref="ep",
        current_case_ref="current",
        mechanism_ref="MRM-D",
        as_of="2026-08-24",
        dimensions=dims,
        overall_transferability="HIGH_TRANSFERABILITY",
    )


class PriorViolationTests(unittest.TestCase):
    def test_missing_pit_freeze_is_not_evaluable(self):
        record = evaluate_prior_violation(transferable(), hypothesis_set(pit_frozen=False), {}, "2026-08-24")
        self.assertEqual(record.status, "NOT_EVALUABLE")
        self.assertEqual(record.posterior_effect, "NO_CHANGE")

    def test_compatible_timing_surprise_is_not_breaker(self):
        observations = {
            "observables": {"term_premium": "UP", "long_yield": "DOWN"},
            "observed_sequence": ("term_premium", "long_yield"),
            "timing_surprise": True,
            "window_closed": False,
        }
        record = evaluate_prior_violation(transferable(), hypothesis_set(), observations, "2026-08-24")
        self.assertEqual(record.status, "SURPRISE_ONLY")
        self.assertIsNone(record.violation_type)
        self.assertEqual(record.posterior_effect, "NO_CHANGE")

    def test_opposite_required_sign_is_sign_violation(self):
        observations = {
            "observables": {"term_premium": "DOWN", "long_yield": "DOWN"},
            "observed_sequence": ("term_premium", "long_yield"),
            "window_closed": True,
        }
        record = evaluate_prior_violation(transferable(), hypothesis_set(), observations, "2026-08-24")
        self.assertEqual(record.violation_type, "SIGN_VIOLATION")
        self.assertEqual(record.posterior_effect, "MAJOR_DOWNGRADE")

    def test_wrong_sequence_is_sequence_violation(self):
        observations = {
            "observables": {"term_premium": "UP", "long_yield": "DOWN"},
            "observed_sequence": ("long_yield", "term_premium"),
            "window_closed": True,
        }
        record = evaluate_prior_violation(transferable(), hypothesis_set(), observations, "2026-08-24")
        self.assertEqual(record.violation_type, "SEQUENCE_VIOLATION")
        self.assertEqual(record.research_response, "REOPEN_MECHANISM_COMPETITION")

    def test_policy_response_outside_feasible_set_is_policy_violation(self):
        observations = {
            "observables": {"term_premium": "UP", "long_yield": "DOWN"},
            "observed_sequence": ("term_premium", "long_yield"),
            "policy_reaction": "financial_repression",
            "feasible_policy_set": ("tighten", "hold"),
            "window_closed": True,
        }
        record = evaluate_prior_violation(transferable(), hypothesis_set(), observations, "2026-08-24")
        self.assertEqual(record.violation_type, "POLICY_REACTION_VIOLATION")
        self.assertEqual(record.posterior_effect, "SHIFT_TO_ALTERNATIVE_REVIEW")

    def test_missing_confirmation_after_window_is_cross_asset_violation(self):
        observations = {
            "observables": {"term_premium": "UP"},
            "observed_sequence": ("term_premium",),
            "window_closed": True,
        }
        record = evaluate_prior_violation(transferable(), hypothesis_set(), observations, "2026-08-24")
        self.assertEqual(record.violation_type, "CROSS_ASSET_CONFIRMATION_VIOLATION")
        self.assertEqual(record.research_response, "REOPEN_MECHANISM_COMPETITION")

    def test_record_contains_no_trade_action(self):
        observations = {
            "observables": {"term_premium": "DOWN", "long_yield": "DOWN"},
            "observed_sequence": ("term_premium", "long_yield"),
            "window_closed": True,
        }
        record = evaluate_prior_violation(transferable(), hypothesis_set(), observations, "2026-08-24")
        self.assertFalse(hasattr(record, "trade_action"))
        self.assertFalse(hasattr(record, "position_size"))


if __name__ == "__main__":
    unittest.main()
