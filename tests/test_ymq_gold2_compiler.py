import unittest

from scripts import ymq_gold2_compiler as gold2


class Gold2ConstitutionTests(unittest.TestCase):
    def test_constitution_preserves_b3_scientific_no_go(self):
        c = gold2.load_constitution()
        gold2.validate_constitution(c)
        self.assertEqual(
            c["upstream_authority"]["dynamic_beta_settlement"],
            "DYNAMIC_BETA_DOES_NOT_BEAT_B2",
        )
        self.assertFalse(c["authority"]["capital_authorized"])
        self.assertFalse(c["authority"]["execution_authorized"])
        self.assertFalse(c["authority"]["live_scheduler_authorized"])

    def test_constitution_rejects_b3_success_laundering(self):
        c = gold2.load_constitution()
        c["upstream_authority"]["dynamic_beta_settlement"] = "DYNAMIC_BETA_BEATS_B2"
        with self.assertRaises(ValueError):
            gold2.validate_constitution(c)

    def test_constitution_rejects_execution_authority(self):
        c = gold2.load_constitution()
        c["authority"]["execution_authorized"] = True
        with self.assertRaises(ValueError):
            gold2.validate_constitution(c)


class Gold2UnifiedStateTests(unittest.TestCase):
    def base_state(self):
        c = gold2.load_constitution()
        return {field: "UNKNOWN" for field in c["unified_state"]["required_fields"]} | {
            "as_of": "2024-01-31",
            "known_as_of_max": "2024-01-31",
            "source_panel": "gold_core_monthly_v0.1",
            "property_drift_state": "INSUFFICIENT_EVIDENCE",
            "expectation_reality_state": "INDETERMINATE",
            "valuation_state": "UNIDENTIFIABLE",
            "engine_state": {"C": "UNKNOWN", "R": "UNKNOWN", "X": "UNKNOWN", "S": "UNKNOWN"},
            "lifecycle_state": "未知",
            "falsifiers": [],
            "unknowns": ["official_demand"],
            "authority_state": {
                "research_authorized": True,
                "capital_authorized": False,
                "sizing_authorized": False,
                "execution_authorized": False,
                "broker_action": False,
            },
        }

    def test_state_passes_with_pit_and_zero_execution_authority(self):
        gold2.validate_unified_state(self.base_state())

    def test_state_rejects_future_leakage(self):
        state = self.base_state()
        state["known_as_of_max"] = "2024-02-01"
        with self.assertRaises(ValueError):
            gold2.validate_unified_state(state)

    def test_state_rejects_trade_authority(self):
        state = self.base_state()
        state["authority_state"]["capital_authorized"] = True
        with self.assertRaises(ValueError):
            gold2.validate_unified_state(state)


class Gold2ResearchCompilerTests(unittest.TestCase):
    def test_property_drift_is_not_alpha_claim(self):
        state = gold2.classify_property_drift(
            coefficient_distance=0.8,
            dominant_factor_match_share=0.4,
            residual_bias_ratio=0.2,
            independent_evidence_count=2,
        )
        self.assertEqual(state, "DRIFT_CANDIDATE")
        self.assertNotIn("ALPHA", state)

    def test_property_drift_can_confirm_research_only(self):
        state = gold2.classify_property_drift(
            coefficient_distance=1.2,
            dominant_factor_match_share=0.25,
            residual_bias_ratio=0.35,
            independent_evidence_count=3,
        )
        self.assertEqual(state, "DRIFT_CONFIRMED_RESEARCH_ONLY")

    def test_property_drift_fails_to_insufficient_evidence(self):
        state = gold2.classify_property_drift(
            coefficient_distance=2.0,
            dominant_factor_match_share=0.1,
            residual_bias_ratio=0.8,
            independent_evidence_count=1,
        )
        self.assertEqual(state, "INSUFFICIENT_EVIDENCE")

    def test_property_stability_requires_joint_diagnostics(self):
        state = gold2.classify_property_drift(
            coefficient_distance=0.2,
            dominant_factor_match_share=0.8,
            residual_bias_ratio=0.1,
            independent_evidence_count=2,
        )
        self.assertEqual(state, "STABLE_PROPERTY")

    def test_expectation_reality_labels(self):
        self.assertEqual(gold2.classify_expectation_reality(0.8, 0.2, True), "REALITY_LED")
        self.assertEqual(gold2.classify_expectation_reality(0.2, 0.8, True), "EXPECTATION_LED")
        self.assertEqual(gold2.classify_expectation_reality(0.8, 0.8, True), "CONFIRMED")
        self.assertEqual(gold2.classify_expectation_reality(0.8, -0.8, True), "DIVERGENT")
        self.assertEqual(gold2.classify_expectation_reality(0.8, 0.8, False), "INDETERMINATE")

    def test_valuation_requires_multiple_lenses(self):
        self.assertEqual(
            gold2.classify_valuation({"MACRO_FAIR_VALUE_LENS": "UNDERPRICED"}),
            "UNIDENTIFIABLE",
        )
        self.assertEqual(
            gold2.classify_valuation({
                "MACRO_FAIR_VALUE_LENS": "UNDERPRICED",
                "MONETARY_REGIME_PREMIUM_LENS": "UNDERPRICED",
                "REFLEXIVITY_POSITIONING_LENS": "FAIR",
            }),
            "UNDERPRICED",
        )


class Gold2ReplayAndHumanTests(unittest.TestCase):
    def test_replay_packet_rejects_post_t0_evidence(self):
        packet = {
            "t0": "2024-01-31",
            "known_as_of_max": "2024-02-01",
            "frozen_label": "DRIFT_CANDIDATE",
        }
        with self.assertRaises(ValueError):
            gold2.validate_replay_packet(packet)

    def test_machine_does_not_fabricate_human_judgments(self):
        obj = gold2.build_triangulation(
            machine_state_judgment={"state": "WATCH", "known_as_of": "2026-09-16"}
        )
        self.assertEqual(obj["ray_regime_judgment"], "PENDING_HUMAN_EVIDENCE")
        self.assertEqual(obj["yiru_timing_judgment"], "PENDING_HUMAN_EVIDENCE")

    def test_live_shadow_packet_is_non_actionable(self):
        packet = gold2.build_live_shadow_packet(
            as_of="2026-09-16",
            state="WATCH",
            lifecycle="等",
        )
        self.assertFalse(packet["capital_authorized"])
        self.assertFalse(packet["sizing_authorized"])
        self.assertFalse(packet["execution_authorized"])
        self.assertFalse(packet["broker_action"])


if __name__ == "__main__":
    unittest.main()
