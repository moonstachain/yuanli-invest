import unittest

from research_runtime.yma55.transfer_challenge import (
    TRANSFER_VARIANTS,
    active_prior_allowed,
    build_hypothesis_set_from_transport,
    resolve_transferability_state,
    validate_structural_packet,
    validate_transported_diagnostic,
)


DIMENSION_NAMES = (
    "monetary_regime",
    "fiscal_capacity",
    "market_structure",
    "global_order",
    "policy_toolkit",
)


def dims(overrides=None):
    overrides = overrides or {}
    rows = []
    for name in DIMENSION_NAMES:
        row = {
            "name": name,
            "state": "MATCHED",
            "blocking_if_mismatched": False,
            "mechanism_relevance": "critical" if name in {"monetary_regime", "policy_toolkit"} else "material",
            "evidence_refs": [f"e:{name}"],
        }
        row.update(overrides.get(name, {}))
        rows.append(row)
    return rows


def valid_structural_packet():
    return {
        "schema_version": "0.1.0",
        "opaque_pair_id": "TP-XX",
        "mechanism_family": "MRM-D",
        "structural_evidence_at_t0": {
            "as_of": "1994-01-01T23:59:59Z",
            "dimensions": dims(),
        },
        "transported_diagnostic": {
            "transport_id": "TR-XX",
            "source_prior_ref": "SP-XX",
            "source_mechanism_family": "MRM-D",
            "target_case_ref_opaque": "TC-XX",
            "as_of": "1994-01-01T23:59:59Z",
            "frozen_at": "1994-01-01T23:59:59Z",
            "observation_window_start": "1994-01-02T00:00:00Z",
            "observation_window_end": "1995-01-01T23:59:59Z",
            "target_required_conditions": ["disinflation_persists"],
            "target_expected_observables": {"term_premium": "DOWN", "long_yield": "DOWN"},
            "target_expected_sequence": ["term_premium", "long_yield"],
            "target_feasible_policy_set": ["hold", "ease"],
            "supporting_evidence_refs": ["e:transport"],
            "pit_frozen": True,
            "version": 1,
        },
        "historical_gold_admission": False,
        "capital_authority": False,
    }


class H43TransferabilityContractTests(unittest.TestCase):
    def test_variant_registry_is_frozen(self):
        self.assertEqual(
            TRANSFER_VARIANTS,
            (
                "T0_UNCONDITIONAL_TRANSPORT",
                "T1_TRANSFERABILITY_GATE_ONLY",
                "T2_H3_FULL",
            ),
        )

    def test_blocking_mismatch_forces_non_transferable(self):
        rows = dims({
            "policy_toolkit": {
                "state": "MISMATCHED",
                "blocking_if_mismatched": True,
                "mechanism_relevance": "critical",
            }
        })
        self.assertEqual(resolve_transferability_state(rows), "NON_TRANSFERABLE")

    def test_critical_unknown_forces_unresolved(self):
        rows = dims({"monetary_regime": {"state": "UNKNOWN", "mechanism_relevance": "critical"}})
        self.assertEqual(resolve_transferability_state(rows), "UNRESOLVED")

    def test_multiple_material_partial_dimensions_can_force_weak(self):
        rows = dims({
            "fiscal_capacity": {"state": "PARTIAL"},
            "market_structure": {"state": "PARTIAL"},
            "global_order": {"state": "PARTIAL"},
        })
        self.assertEqual(resolve_transferability_state(rows), "WEAK_TRANSFERABILITY")

    def test_single_material_partial_is_partial(self):
        rows = dims({"market_structure": {"state": "PARTIAL"}})
        self.assertEqual(resolve_transferability_state(rows), "PARTIAL_TRANSFERABILITY")

    def test_all_matched_is_high(self):
        self.assertEqual(resolve_transferability_state(dims()), "HIGH_TRANSFERABILITY")

    def test_only_high_and_partial_receive_active_prior_authority(self):
        self.assertTrue(active_prior_allowed("HIGH_TRANSFERABILITY"))
        self.assertTrue(active_prior_allowed("PARTIAL_TRANSFERABILITY"))
        self.assertFalse(active_prior_allowed("WEAK_TRANSFERABILITY"))
        self.assertFalse(active_prior_allowed("NON_TRANSFERABLE"))
        self.assertFalse(active_prior_allowed("UNRESOLVED"))

    def test_structural_packet_cannot_contain_forward_evidence_or_settlement(self):
        packet = valid_structural_packet()
        packet["forward_observation_stream"] = []
        with self.assertRaises(ValueError):
            validate_structural_packet(packet)

        packet = valid_structural_packet()
        packet["settlement"] = {"expected": "anything"}
        with self.assertRaises(ValueError):
            validate_structural_packet(packet)

    def test_transport_contract_must_be_pre_frozen(self):
        packet = valid_structural_packet()
        packet["transported_diagnostic"]["frozen_at"] = "1994-01-03T00:00:00Z"
        with self.assertRaises(ValueError):
            validate_transported_diagnostic(packet["transported_diagnostic"])

    def test_transport_contract_is_not_source_hypothesis_mutation(self):
        contract = valid_structural_packet()["transported_diagnostic"]
        validate_transported_diagnostic(contract)
        self.assertNotEqual(contract["transport_id"], contract["source_prior_ref"])
        self.assertTrue(contract["pit_frozen"])

    def test_transported_contract_compiles_to_new_hypothesis_identity(self):
        contract = valid_structural_packet()["transported_diagnostic"]
        hypothesis_set = build_hypothesis_set_from_transport(contract)
        self.assertEqual(hypothesis_set.primary.hypothesis_id, "transported:TR-XX")
        self.assertNotEqual(hypothesis_set.primary.hypothesis_id, contract["source_prior_ref"])
        self.assertEqual(dict(hypothesis_set.primary.predicted_observables), contract["target_expected_observables"])
        self.assertEqual(tuple(hypothesis_set.primary.expected_sequence), tuple(contract["target_expected_sequence"]))
        self.assertTrue(hypothesis_set.pit_frozen)

    def test_opaque_pair_id_cannot_bear_historical_role_or_year(self):
        packet = valid_structural_packet()
        packet["opaque_pair_id"] = "D1982-GOLD-TO-1994"
        with self.assertRaises(ValueError):
            validate_structural_packet(packet)


if __name__ == "__main__":
    unittest.main()
