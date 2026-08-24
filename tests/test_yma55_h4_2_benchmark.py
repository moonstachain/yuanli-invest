import json
import unittest
from pathlib import Path

from research_runtime.yma55.benchmark import (
    BENCHMARK_VARIANTS,
    resolve_variant,
    score_variant,
)

ROOT = Path(__file__).resolve().parents[1]
H41 = ROOT / "fixtures" / "replay" / "yma55_h4_1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class H42SameCaseBenchmarkTests(unittest.TestCase):
    def blind_packets(self):
        manifest = load(H41 / "blind_manifest.json")
        return [load(H41 / rel) for rel in manifest["case_files"]]

    def settlements(self):
        return load(H41 / "post_resolution_unblinding.json")["cases"]

    def test_variant_registry_is_frozen_and_non_overclaiming(self):
        self.assertEqual(
            BENCHMARK_VARIANTS,
            (
                "B0_NAIVE_PRIMARY_PRIOR",
                "B1_EVIDENCE_GATED_PRIMARY",
                "B2_COMPETING_NO_BREAKER",
                "B3_H1_H2_FULL_RESOLVER",
                "B4_H1_H2_H3_HISTORICAL_ONLY",
            ),
        )

    def test_b0_is_a_naive_primary_prior_not_a_claimed_old_yma55_replica(self):
        packet = self.blind_packets()[8]  # partial-hydration 1971 case, still role-blind here
        result = resolve_variant(packet, "B0_NAIVE_PRIMARY_PRIOR")
        self.assertEqual(result["resolution"], "PRIMARY_LEADS")
        self.assertEqual(result["baseline_semantics"], "naive_primary_prior")
        self.assertFalse(result["claims_old_framework_replication"])

    def test_b1_adds_evidence_abstention_without_competing_mechanisms(self):
        packet = self.blind_packets()[8]
        result = resolve_variant(packet, "B1_EVIDENCE_GATED_PRIMARY")
        self.assertEqual(result["resolution"], "INSUFFICIENT_EVIDENCE")
        hydrated = self.blind_packets()[0]
        self.assertEqual(resolve_variant(hydrated, "B1_EVIDENCE_GATED_PRIMARY")["resolution"], "PRIMARY_LEADS")

    def test_b3_reproduces_frozen_h41_resolver_outputs(self):
        freeze = load(H41 / "blind_resolution_freeze.json")
        expected = {row["blind_case_id"]: row["resolution"] for row in freeze["resolutions"]}
        for packet in self.blind_packets():
            result = resolve_variant(packet, "B3_H1_H2_FULL_RESOLVER")
            self.assertEqual(result["resolution"], expected[packet["blind_case_id"]])

    def test_b4_does_not_fake_h3_incremental_effect_when_transferability_is_unresolved(self):
        for packet in self.blind_packets():
            b3 = resolve_variant(packet, "B3_H1_H2_FULL_RESOLVER")
            b4 = resolve_variant(packet, "B4_H1_H2_H3_HISTORICAL_ONLY")
            self.assertEqual(b4["resolution"], b3["resolution"])
            self.assertEqual(b4["h3_incremental_status"], "NOT_IDENTIFIABLE_IN_HISTORICAL_ONLY_REPLAY")

    def test_scoring_keeps_accuracy_abstention_and_hard_negative_discrimination_separate(self):
        outputs = [resolve_variant(packet, "B3_H1_H2_FULL_RESOLVER") for packet in self.blind_packets()]
        score = score_variant(outputs, self.settlements())
        self.assertEqual(score["total_cases"], 12)
        self.assertEqual(score["fully_hydrated_cases"], 11)
        self.assertEqual(score["matches"], 10)
        self.assertEqual(score["mismatches"], 1)
        self.assertEqual(score["evidence_abstentions"], 1)
        self.assertEqual(score["fully_hydrated_mechanism_accuracy"], "10/11")
        self.assertIn("hard_negative_discrimination", score)
        self.assertIn("partial_case_forced_resolution", score)
        self.assertNotIn("win_rate", score)
        self.assertNotIn("probability", score)


if __name__ == "__main__":
    unittest.main()
