import unittest

from research_runtime.yma55.blind import build_blind_packet, validate_blind_packet, resolve_blind_packet


class H41BlindFirewallTests(unittest.TestCase):
    def case(self):
        return {
            "episode_id": "YMA55-H4-D-GOLD-TEST",
            "mechanism_family": "MRM-D",
            "case_type": "GOLD",
            "as_of": "2000-01-01",
            "evidence_cutoff": "2000-01-01T23:59:59Z",
            "t0": {
                "world": {"state_summary": "test"},
                "constraint": {"constraint_id": "test"},
                "transmission": {"channels": ["long_yield"]},
                "hypothesis_set": {
                    "hypothesis_set_id": "HS1",
                    "pit_frozen": True,
                    "primary": {
                        "hypothesis_id": "P",
                        "role": "PRIMARY",
                        "predicted_observables": {"long_yield": "DOWN"},
                        "required_conditions": ["disinflation"],
                        "falsifiers": ["inflation_reaccelerates"],
                        "breaker": "long_yield_up",
                    },
                    "alternatives": [{
                        "hypothesis_id": "A1",
                        "role": "ALTERNATIVE",
                        "predicted_observables": {"long_yield": "UP"},
                        "required_conditions": ["reflation"],
                        "falsifiers": ["growth_collapse"],
                        "breaker": "long_yield_down",
                    }],
                    "null": {
                        "hypothesis_id": "N",
                        "role": "NULL",
                        "predicted_observables": {"positioning": "EXTREME"},
                        "required_conditions": ["positioning_extreme"],
                        "falsifiers": ["no_positioning_extreme"],
                        "breaker": "positioning_normal",
                    },
                },
                "transferability_template": {"overall_transferability": "UNRESOLVED"},
            },
            "settlement": {"outcome_class": "RIGHT_MECHANISM_RIGHT_OUTCOME_CANDIDATE"},
        }

    def evidence_packet(self, signals=None):
        return {
            "hydration_status": "EVIDENCE_HYDRATED",
            "blindness_grade": "B_PIPELINE_BLIND",
            "admitted_signals": signals or [],
        }

    def test_blind_packet_removes_role_and_settlement(self):
        case = self.case()
        packet = build_blind_packet("H41-B01", case, self.evidence_packet())
        text = repr(packet)
        self.assertNotIn("case_type", packet)
        self.assertNotIn("settlement", packet)
        self.assertNotIn(case["episode_id"], text)
        self.assertNotIn("GOLD", text)
        validate_blind_packet(packet)

    def test_role_bearing_blind_id_is_rejected(self):
        bad = {"blind_case_id": "H4-GOLD-1982", "mechanism_family": "MRM-D", "t0": {}, "evidence": []}
        with self.assertRaises(ValueError):
            validate_blind_packet(bad)

    def test_primary_breaker_prevents_primary_win(self):
        packet = build_blind_packet(
            "H41-B02",
            self.case(),
            self.evidence_packet([
                {"observable": "long_yield", "state": "UP"},
                {"observable": "reflation", "state": "TRUE"},
            ]),
        )
        result = resolve_blind_packet(packet)
        self.assertNotEqual(result["resolution"], "PRIMARY_LEADS")

    def test_sparse_evidence_stays_insufficient(self):
        packet = build_blind_packet("H41-B03", self.case(), self.evidence_packet([]))
        result = resolve_blind_packet(packet)
        self.assertEqual(result["resolution"], "INSUFFICIENT_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
