import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.validate_r2_gold_pack import EXPECTED_COUNTS, assert_registry_contains_r2_baseline


class R2RegistryExtensionCompatibilityTests(unittest.TestCase):
    def test_later_governed_registry_growth_does_not_rewrite_r2_baseline(self):
        registry_index = json.loads((ROOT / "registry" / "registry-index.json").read_text(encoding="utf-8"))
        observed = {item["name"]: item["entry_count"] for item in registry_index["registries"]}
        assert_registry_contains_r2_baseline(observed)
        self.assertEqual(EXPECTED_COUNTS["theories"], 19)
        self.assertEqual(EXPECTED_COUNTS["hypotheses"], 12)
        self.assertGreaterEqual(observed["theories"], EXPECTED_COUNTS["theories"])
        self.assertGreaterEqual(observed["hypotheses"], EXPECTED_COUNTS["hypotheses"])

    def test_missing_r2_baseline_entry_still_fails_closed(self):
        truncated = dict(EXPECTED_COUNTS)
        truncated["theories"] = EXPECTED_COUNTS["theories"] - 1
        with self.assertRaises(AssertionError):
            assert_registry_contains_r2_baseline(truncated)


if __name__ == "__main__":
    unittest.main()
