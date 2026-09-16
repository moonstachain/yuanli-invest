import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Gold2ConfigAuthorityTests(unittest.TestCase):
    def test_human_template_does_not_fabricate_people(self):
        data = json.loads((ROOT / "config/ymq_gold2/gold2_human_triangulation.template.json").read_text())
        self.assertEqual(data["ray_regime_judgment"]["status"], "PENDING_HUMAN_EVIDENCE")
        self.assertEqual(data["yiru_timing_judgment"]["status"], "PENDING_HUMAN_EVIDENCE")
        for ref in data["candidate_source_refs"]:
            self.assertEqual(ref["speaker_identity"], "PENDING_HUMAN_ADJUDICATION")
        self.assertFalse(data["authority"]["capital_authorized"])
        self.assertFalse(data["authority"]["execution_authorized"])

    def test_live_shadow_contract_is_not_activated(self):
        data = json.loads((ROOT / "config/ymq_gold2/gold2_live_shadow.v0.1.json").read_text())
        self.assertEqual(data["status"], "CONTRACT_FROZEN_NOT_ACTIVATED")
        authority = data["authority"]
        self.assertFalse(authority["live_scheduler_authorized"])
        self.assertFalse(authority["capital_authorized"])
        self.assertFalse(authority["sizing_authorized"])
        self.assertFalse(authority["execution_authorized"])
        self.assertFalse(authority["broker_action"])
        self.assertFalse(authority["veighna_authorized"])
        self.assertFalse(authority["canon_promotion_authorized"])


if __name__ == "__main__":
    unittest.main()
