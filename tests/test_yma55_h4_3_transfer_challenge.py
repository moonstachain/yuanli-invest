import json
import unittest
from pathlib import Path

from research_runtime.yma55.transfer_challenge import (
    TRANSFER_VARIANTS,
    active_prior_allowed,
    build_hypothesis_set_from_transport,
    resolve_transferability_state,
    run_h43_matrix,
    run_transfer_variant,
    validate_structural_packet,
    validate_transported_diagnostic,
)

ROOT = Path(__file__).resolve().parents[1]
H43 = ROOT / "fixtures" / "replay" / "yma55_h4_3"

DIMENSION_NAMES = (
    "monetary_regime",
    "fiscal_capacity",
    "market_structure",
    "global_order",
    "policy_toolkit",
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


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
        "source_prior_eligible": True,
        "structural_evidence_authority": "CANDIDATE_DERIVED_FROM_H4_H41",
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


class H43FixtureIntegrityTests(unittest.TestCase):
    def manifest(self):
        return load(H43 / "blind_manifest.json")

    def test_exact_six_opaque_pairs_with_one_to_one_files(self):
        manifest = self.manifest()
        self.assertEqual(manifest["pair_ids"], ["TP-01", "TP-02", "TP-03", "TP-04", "TP-05", "TP-06"])
        self.assertEqual(len(manifest["structural_files"]), 6)
        self.assertEqual(len(manifest["observation_files"]), 6)
        for pair_id, structural_rel, observation_rel in zip(
            manifest["pair_ids"], manifest["structural_files"], manifest["observation_files"]
        ):
            structural = load(H43 / structural_rel)
            observation = load(H43 / observation_rel)
            self.assertEqual(structural["opaque_pair_id"], pair_id)
            self.assertEqual(observation["opaque_pair_id"], pair_id)
            validate_structural_packet(structural)

    def test_blind_packets_preserve_identity_and_outcome_firewalls(self):
        forbidden = {
            "source_episode_id",
            "target_episode_id",
            "settlement",
            "expected_h3_settlement",
            "challenge_role",
            "case_type",
        }
        for rel in self.manifest()["structural_files"] + self.manifest()["observation_files"]:
            packet = load(H43 / rel)
            self.assertFalse(forbidden & set(packet))
            self.assertRegex(packet["opaque_pair_id"], r"^TP-\d{2}$")

    def test_structural_packets_are_candidate_derived_not_primary_gold_evidence(self):
        for rel in self.manifest()["structural_files"]:
            packet = load(H43 / rel)
            self.assertEqual(packet["structural_evidence_authority"], "CANDIDATE_DERIVED_FROM_H4_H41")
            self.assertTrue(packet["source_prior_eligible"])
            self.assertFalse(packet["historical_gold_admission"])
            self.assertFalse(packet["capital_authority"])
            dimensions = packet["structural_evidence_at_t0"]["dimensions"]
            self.assertEqual({d["name"] for d in dimensions}, set(DIMENSION_NAMES))
            self.assertEqual(len(dimensions), 5)

    def test_forward_observation_packets_are_post_freeze_and_non_authoritative(self):
        structural_by_id = {
            load(H43 / rel)["opaque_pair_id"]: load(H43 / rel)
            for rel in self.manifest()["structural_files"]
        }
        for rel in self.manifest()["observation_files"]:
            observation = load(H43 / rel)
            structural = structural_by_id[observation["opaque_pair_id"]]
            frozen_at = structural["transported_diagnostic"]["frozen_at"]
            self.assertGreater(observation["observation_stream"][0]["known_at"], frozen_at)
            self.assertFalse(observation["historical_gold_admission"])
            self.assertFalse(observation["capital_authority"])

    def test_sealed_mapping_is_only_identity_and_role_decryption_point(self):
        mapping = load(H43 / "sealed_mapping.json")
        self.assertEqual(len(mapping["pairs"]), 6)
        self.assertEqual({p["opaque_pair_id"] for p in mapping["pairs"]}, set(self.manifest()["pair_ids"]))
        for pair in mapping["pairs"]:
            self.assertIn("source_episode_id", pair)
            self.assertIn("target_episode_id", pair)
            self.assertIn("challenge_role", pair)

    def test_post_resolution_settlement_is_complete_and_non_capital(self):
        settlement = load(H43 / "post_resolution_settlement.json")
        self.assertEqual({p["opaque_pair_id"] for p in settlement["pairs"]}, set(self.manifest()["pair_ids"]))
        self.assertFalse(settlement["historical_gold_admission"])
        self.assertFalse(settlement["capital_authority"])
        self.assertEqual(
            {p["expected_transferability"] for p in settlement["pairs"]},
            {"PARTIAL_TRANSFERABILITY", "NON_TRANSFERABLE", "WEAK_TRANSFERABILITY"},
        )


class H43VariantAndMatrixTests(unittest.TestCase):
    def inputs(self):
        manifest = load(H43 / "blind_manifest.json")
        structural = [load(H43 / rel) for rel in manifest["structural_files"]]
        observations = [load(H43 / rel) for rel in manifest["observation_files"]]
        settlement = load(H43 / "post_resolution_settlement.json")["pairs"]
        return structural, observations, settlement

    def test_t0_exposes_unconditional_transport_overreach(self):
        structural, observations, _ = self.inputs()
        packet = structural[2]  # TP-03 is structurally blocked by a policy-toolkit mismatch.
        result = run_transfer_variant(packet, observations[2], "T0_UNCONDITIONAL_TRANSPORT")
        self.assertEqual(result["authority_settlement"], "ACTIVE_PRIOR_ALLOWED")
        self.assertTrue(result["unsafe_prior_application"])
        self.assertFalse(result["capital_authority"])

    def test_t1_blocks_weak_nontransferable_and_unresolved_without_using_forward_evidence(self):
        structural, observations, _ = self.inputs()
        for index in (2, 4, 5):
            poisoned_observation = dict(observations[index])
            poisoned_observation["settlement"] = "must_not_be_read_by_t1"
            result = run_transfer_variant(structural[index], poisoned_observation, "T1_TRANSFERABILITY_GATE_ONLY")
            self.assertEqual(result["authority_settlement"], "ACTIVE_PRIOR_BLOCKED")
            self.assertEqual(result["observation_settlement"], "NOT_APPLICABLE")
            self.assertFalse(result["weak_prior_active_authority_leak"])

    def test_t2_maintains_compatible_prior_and_detects_two_active_prior_violations(self):
        structural, observations, _ = self.inputs()
        tp01 = run_transfer_variant(structural[0], observations[0], "T2_H3_FULL")
        tp02 = run_transfer_variant(structural[1], observations[1], "T2_H3_FULL")
        tp04 = run_transfer_variant(structural[3], observations[3], "T2_H3_FULL")
        self.assertEqual(tp01["observation_settlement"], "MAINTAIN_PRIOR")
        self.assertEqual(tp02["observation_settlement"], "REOPEN_MECHANISM_COMPETITION")
        self.assertEqual(tp04["observation_settlement"], "REOPEN_MECHANISM_COMPETITION")

    def test_ineligible_source_prior_is_never_laundered_into_active_authority(self):
        packet = valid_structural_packet()
        packet["source_prior_eligible"] = False
        result = run_transfer_variant(packet, {}, "T0_UNCONDITIONAL_TRANSPORT")
        self.assertEqual(result["authority_settlement"], "ACTIVE_PRIOR_BLOCKED")
        self.assertFalse(result["source_prior_laundering_event"])

    def test_matrix_reports_counts_without_probability_or_win_rate(self):
        structural, observations, settlement = self.inputs()
        matrix = run_h43_matrix(structural, observations, settlement)
        self.assertEqual(matrix["pair_count"], 6)
        self.assertEqual(tuple(matrix["variants"]), TRANSFER_VARIANTS)
        self.assertEqual(matrix["metrics"]["T0_UNCONDITIONAL_TRANSPORT"]["unsafe_prior_applications"], 3)
        self.assertEqual(matrix["metrics"]["T1_TRANSFERABILITY_GATE_ONLY"]["correct_structural_blocks"], 3)
        self.assertEqual(matrix["metrics"]["T1_TRANSFERABILITY_GATE_ONLY"]["eligible_prior_violations_missed"], 2)
        self.assertEqual(matrix["metrics"]["T2_H3_FULL"]["eligible_prior_violations_detected"], 2)
        self.assertEqual(matrix["metrics"]["T2_H3_FULL"]["eligible_prior_violations_missed"], 0)
        self.assertEqual(matrix["metrics"]["T2_H3_FULL"]["false_breakers"], 0)
        self.assertEqual(matrix["metrics"]["T2_H3_FULL"]["weak_prior_active_authority_leaks"], 0)
        self.assertEqual(matrix["metrics"]["T2_H3_FULL"]["source_prior_laundering_events"], 0)
        self.assertEqual(matrix["metrics"]["T2_H3_FULL"]["capital_authority_events"], 0)
        self.assertNotIn("win_rate", matrix)
        self.assertNotIn("probability", matrix)


if __name__ == "__main__":
    unittest.main()
