from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_yks0_r0_research_estate.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("yks0_r0_validator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class YKS0R0ResearchEstateTests(unittest.TestCase):
    def test_expected_country_and_dimension_sets_are_closed(self):
        module = load_validator()
        self.assertEqual(module.COUNTRIES, {"US", "DE", "JP", "KR", "CN"})
        self.assertEqual(module.DIMENSIONS, {f"K{i:02d}" for i in range(1, 10)})

    def test_pit_and_case_status_sets_are_closed(self):
        module = load_validator()
        self.assertEqual(module.PIT_STATES, {
            "PIT_NATIVE", "PIT_RECONSTRUCTABLE", "CURRENT_ONLY",
            "BACKTEST_OR_RESTATED", "UNKNOWN"
        })
        self.assertEqual(module.CASE_STATES, {
            "CANDIDATE_DESKTOP", "PIT_AUDIT_REQUIRED", "PREREGISTRATION_READY", "REJECTED"
        })

    def test_complete_estate_validates(self):
        module = load_validator()
        result = module.validate_estate(ROOT)
        self.assertEqual(result["status"], "VALID")
        self.assertEqual(result["cells"], 45)
        self.assertEqual(result["hypotheses"], 8)
        self.assertEqual(result["cases"], 50)


if __name__ == "__main__":
    unittest.main()
