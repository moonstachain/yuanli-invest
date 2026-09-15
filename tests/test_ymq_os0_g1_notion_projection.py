import json
import unittest
from pathlib import Path

from scripts.validate_ymq_os0_g1 import validate_projection_manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config/ymq_os0/notion_projection_manifest.v0.1.json"


class YMQOS0G1NotionProjectionTests(unittest.TestCase):
    def test_projection_manifest_is_projection_only(self):
        payload = json.loads(MANIFEST.read_text())
        self.assertEqual(validate_projection_manifest(payload), [])
        self.assertEqual(payload["system"], "Notion")
        self.assertEqual(payload["role"], "PROJECTION_ONLY")
        self.assertFalse(payload["canonical_truth"])
        self.assertFalse(payload["can_grant_authority"])
        self.assertFalse(payload["capital_authorized"])
        self.assertFalse(payload["execution_authorized"])

    def test_projection_manifest_points_to_existing_law_and_reality_planes(self):
        payload = json.loads(MANIFEST.read_text())
        self.assertEqual(payload["law_plane"]["repository"], "moonstachain/yuanli-invest")
        self.assertEqual(payload["reality_plane"]["project"], "yuanli-invest-runtime")
        self.assertEqual(payload["reality_plane"]["project_ref"], "tbmoimbdhsrltvospwpu")


if __name__ == "__main__":
    unittest.main()
