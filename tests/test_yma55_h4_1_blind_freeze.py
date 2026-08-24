import json
import unittest
from pathlib import Path

from research_runtime.yma55.blind import resolve_blind_packet, validate_blind_packet

ROOT = Path(__file__).resolve().parents[1]
H41_ROOT = ROOT / "fixtures" / "replay" / "yma55_h4_1"
FREEZE = H41_ROOT / "blind_resolution_freeze.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class H41BlindResolutionFreezeTests(unittest.TestCase):
    def test_freeze_is_role_blind_and_exactly_twelve(self):
        freeze = load(FREEZE)
        self.assertEqual(freeze["schema_version"], "0.1.0")
        self.assertEqual(freeze["blindness_grade"], "B_PIPELINE_BLIND")
        self.assertFalse(freeze["historical_role_mapping_exposed"])
        self.assertFalse(freeze["capital_authority"])
        self.assertEqual(len(freeze["resolutions"]), 12)
        ids = [item["blind_case_id"] for item in freeze["resolutions"]]
        self.assertEqual(ids, [f"H41-B{i:02d}" for i in range(1, 13)])
        text = FREEZE.read_text(encoding="utf-8")
        for forbidden in (
            "sealed_mapping",
            "case_type",
            "episode_id",
            "settlement",
            "outcome_class",
            "GOLD",
            "NEAR_MISS",
            "WRONG_MECHANISM",
            "WRONG_STRIKE",
            "YMA55-H4-",
        ):
            self.assertNotIn(forbidden, text)

    def test_freeze_recomputes_from_blind_packets_only(self):
        manifest = load(H41_ROOT / "blind_manifest.json")
        expected = []
        for rel in manifest["case_files"]:
            packet = load(H41_ROOT / rel)
            validate_blind_packet(packet)
            result = resolve_blind_packet(packet)
            expected.append({
                "blind_case_id": result["blind_case_id"],
                "resolution": result["resolution"],
            })
        freeze = load(FREEZE)
        self.assertEqual(freeze["resolutions"], expected)


if __name__ == "__main__":
    unittest.main()
