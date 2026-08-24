import json
import re
import unittest
from datetime import datetime
from pathlib import Path

from research_runtime.yma55.evidence import admit_evidence, assess_hydration
from research_runtime.yma55.blind import validate_blind_packet

ROOT = Path(__file__).resolve().parents[1]
H4_ROOT = ROOT / "fixtures" / "replay" / "yma55_h4"
H41_ROOT = ROOT / "fixtures" / "replay" / "yma55_h4_1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dt(value: str):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class H41FixtureIntegrityTests(unittest.TestCase):
    def sources(self):
        index = load(H41_ROOT / "sources.json")
        rows = []
        for rel in index["source_files"]:
            rows.extend(load(H41_ROOT / rel)["sources"])
        ids = [row["source_id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        return {item["source_id"]: item for item in rows}

    def hydration_packets(self):
        return sorted((H41_ROOT / "hydration").glob("*.json"))

    def blind_cases(self):
        manifest = load(H41_ROOT / "blind_manifest.json")
        cases = [load(H41_ROOT / rel) for rel in manifest["case_files"]]
        return manifest, cases

    def test_exact_twelve_hydration_packets_and_blind_cases(self):
        packets = self.hydration_packets()
        self.assertEqual(len(packets), 12)
        manifest, cases = self.blind_cases()
        self.assertEqual(len(manifest["case_files"]), 12)
        self.assertEqual(len(cases), 12)
        ids = [case["blind_case_id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {f"H41-B{i:02d}" for i in range(1, 13)})
        for case in cases:
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

        manifest, cases = self.blind_cases()
        blind_text = json.dumps({"manifest": manifest, "cases": cases}, ensure_ascii=False)
        for token in ("case_type", "settlement", "outcome_class", "GOLD", "NEAR_MISS", "WRONG_MECHANISM", "WRONG_STRIKE"):
            self.assertNotIn(token, blind_text)

    def test_t0_hydration_and_forward_observation_stream_obey_separate_cutoffs(self):
        sources = self.sources()
        for packet_path in self.hydration_packets():
            packet = load(packet_path)
            self.assertEqual(packet["blindness_grade"], "B_PIPELINE_BLIND")
            self.assertLess(dt(packet["evidence_cutoff"]), dt(packet["resolver_cutoff"]))

            t0_ids = packet["t0_source_ids"]
            observation_ids = packet["observation_source_ids"]
            rejected_ids = packet.get("rejected_source_ids", [])
            for source_id in t0_ids + observation_ids + rejected_ids:
                self.assertIn(source_id, sources)

            t0_records = [sources[source_id] for source_id in t0_ids]
            admitted_t0, rejected_t0 = admit_evidence(t0_records, packet["evidence_cutoff"])
            self.assertEqual(len(admitted_t0), len(t0_records))
            self.assertEqual(rejected_t0, [])
            self.assertTrue(all(item["evidence_tier"] in {"E0", "E1", "E2"} for item in admitted_t0))

            assessed = assess_hydration(admitted_t0)
            self.assertEqual(packet["hydration_status"], assessed["status"])
            self.assertEqual(packet["independent_e1"], assessed["independent_e1"])

            observation_records = [sources[source_id] for source_id in observation_ids]
            admitted_obs, rejected_obs = admit_evidence(observation_records, packet["resolver_cutoff"])
            self.assertEqual(len(admitted_obs), len(observation_records))
            self.assertEqual(rejected_obs, [])
            for source in observation_records:
                self.assertGreater(dt(source["published_at"]), dt(packet["evidence_cutoff"]))
                self.assertLessEqual(dt(source["published_at"]), dt(packet["resolver_cutoff"]))
                self.assertIn(source["evidence_tier"], {"E0", "E1", "E2"})

            known_times = [dt(item["known_at"]) for item in packet["observation_stream"]]
            self.assertEqual(known_times, sorted(known_times))
            for item in packet["observation_stream"]:
                self.assertGreater(dt(item["known_at"]), dt(packet["evidence_cutoff"]))
                self.assertLessEqual(dt(item["known_at"]), dt(packet["resolver_cutoff"]))
                self.assertIn(item["source_id"], observation_ids)

    def test_no_placeholder_refs_or_gold_admission_in_h41_packets(self):
        for packet_path in self.hydration_packets():
            packet = load(packet_path)
            text = packet_path.read_text(encoding="utf-8")
            self.assertNotIn("needs_primary_hydration", text)
            self.assertFalse(packet.get("historical_gold_admitted", False))
            self.assertFalse(packet.get("capital_authority", False))
            self.assertTrue(packet.get("t0_signals") or packet["hydration_status"] != "EVIDENCE_HYDRATED")
            self.assertTrue(packet.get("observation_stream"))

    def test_original_h4_fixtures_remain_non_gold(self):
        manifest = load(H4_ROOT / "manifest.json")
        for mechanism in manifest["mechanisms"].values():
            for entry in mechanism["cases"]:
                case = load(ROOT / entry["path"])
                self.assertFalse(case["gold_qualified"])
                self.assertEqual(case["evidence_status"], "needs_primary_hydration")

    def test_blind_manifest_never_exposes_role_bearing_episode_identity_or_paths(self):
        manifest, cases = self.blind_cases()
        text = json.dumps({"manifest": manifest, "cases": cases}, ensure_ascii=False)
        self.assertIsNone(re.search(r"YMA55-H4-", text))
        self.assertNotIn("fixtures/replay/yma55_h4/", text)


if __name__ == "__main__":
    unittest.main()
