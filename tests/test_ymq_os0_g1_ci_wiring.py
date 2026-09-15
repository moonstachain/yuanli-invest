import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci.yml"


class YMQOS0G1CIWiringTests(unittest.TestCase):
    def test_protected_contracts_job_runs_g1_validator(self):
        text = WORKFLOW.read_text()
        self.assertIn("name: contracts", text)
        self.assertIn("python scripts/validate_ymq_os0_g1.py", text)
        self.assertIn("python -m unittest discover -s tests -p 'test_*.py' -v", text)

    def test_protected_check_names_are_not_renamed(self):
        text = WORKFLOW.read_text()
        self.assertIn("contracts:\n    name: contracts", text)
        self.assertIn("governance:\n    name: governance", text)


if __name__ == "__main__":
    unittest.main()
