import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeterminismTests(unittest.TestCase):
    def test_manifest_repeats_exactly(self):
        spec = importlib.util.spec_from_file_location("build_manifest", ROOT / "scripts" / "build_manifest.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        self.assertEqual(module.build(), module.build())


if __name__ == "__main__":
    unittest.main()
