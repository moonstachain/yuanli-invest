import json
import re
import unittest
from pathlib import Path

from research_runtime.yma55.evidence import admit_evidence, assess_hydration
from research_runtime.yma55.blind import validate_blind_packet

ROOT = Path(__file__).resolve().parents[1]
H4_ROOT = ROOT / "fixtures" / "replay" / "yma55_h4"
H41_ROOT = ROOT / "fixtures" / "replay" / "yma55_h4_1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class H41FixtureIntegrityTests(unittest.TestCase):
    def sources(self):
        data = load(H41_ROOT / "sources.json")
        return {item["source_id"]: item for item in data["sources"]}

    def hydration_packets(self):
        return sorted((H41_ROOT / "hydration").glob("*.json"))

    def test_exact_twelve_hydration_packets_and_blind_cases(self):
        packets = self.hydration_packets()
        self.assertEqual(len(packets), 12)
        blind = load(H41_ROOT / "blind_manifest.json")
        self.assertEqual(len(blind["cases"]), 12)
        ids = [case["blind_case_id"] for case in blind["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {f"H41-B{i:02d}" for i in range(1, 13)})
        for case in blind["cases"]:
            validate_blind_packet(case)

    def test_sealed_mapping_is_one_to_one_and_only_place_with_case_roles(self):
        mapping = load(H41_ROOT / "sealed_mapping.json")
        self.assertEqual(len(mapping["cases"]), 12)
        blind_ids = [item["blind_case_id"] for item in mapping["cases"]]
        episode_ids = [item["episode_id"] for item in mapping["cases"]]
        self.assertEqual(len(blind_ids), len(set(blind_ids)))
        self.assertEqual(len(episode_ids), len(set(episode_ids)))
        self.assertEqual(set(blind_ids), {f"H41-B{i:02d}" for i in range(1, 13)})
        for item in mapping["cases"]:
            self.assertIn(item["case_type"], {"GOLD", "NEAR_MISS", "WRONG_MECHANISM", "WRONG_STRIKE"})

        blind_text = (H41_ROOT / "blind_manifest.json").read_text(encoding="utf-8")
        for token in ("case_type", "settlement", "outcome_class", "GOLD", "NEAR_MISS", "WRONG_MECHANISM", "WRONG_STRIKE"):
            self.assertNotIn(token, blind_text)

    def test_hydration_source_refs_resolve_and_obey_pit_admission(self):
        sources = self.sources()
        for packet_path in self.hydration_packets():
            packet = load(packet_path)
            self.assertEqual(packet["blindness_grade"], "B_PIPELINE_BLIND")
            referenced = packet["admitted_source_ids"] + packet.get("rejected_source_ids", [])
            for source_id in referenced:
                self.assertIn(source_id, sources)

            admitted_records = [sources[source_id] for source_id in packet["admitted_source_ids"]]
            admitted, rejected = admit_evidence(admitted_records, packet["evidence_cutoff"])
            self.assertEqual(len(admitted), len(admitted_records))
            self.assertEqual(rejected, [])
            self.assertTrue(all(item["evidence_tier"] in {"E0", "E1", "E2"} for item in admitted))

            assessed = assess_hydration(admitted)
            self.assertEqual(packet["hydration_status"], assessed["status"])
            self.assertEqual(packet["independent_e1"], assessed["independent_e1"])

    def test_no_placeholder_refs_or_gold_admission_in_h41_packets(self):
        for packet_path in self.hydration_packets():
            packet = load(packet_path)
            text = packet_path.read_text(encoding="utf-8")
            self.assertNotIn("needs_primary_hydration", text)
            self.assertFalse(packet.get("historical_gold_admitted", False))
            self.assertFalse(packet.get("capital_authority", False))
            self.assertTrue(packet.get("admitted_signals") or packet["hydration_status"] != "EVIDENCE_HYDRATED")

    def test_original_h4_fixtures_remain_non_gold(self):
        manifest = load(H4_ROOT / "manifest.json")
        for mechanism in manifest["mechanisms"].values():
            for entry in mechanism["cases"]:
                case = load(ROOT / entry["path"])
                self.assertFalse(case["gold_qualified"])
                self.assertEqual(case["evidence_status"], "needs_primary_hydration")

    def test_blind_manifest_never_exposes_role_bearing_episode_identity_or_paths(self):
        blind = load(H41_ROOT / "blind_manifest.json")
        text = json.dumps(blind, ensure_ascii=False)
        self.assertIsNone(re.search(r"YMA55-H4-", text))
        self.assertNotIn("fixtures/replay/yma55_h4/", text)


if __name__ == "__main__":
    unittest.main()
