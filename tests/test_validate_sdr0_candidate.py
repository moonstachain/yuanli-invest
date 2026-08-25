import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_sdr0_candidate.py"


class SDR0CandidateValidatorTests(unittest.TestCase):
    def test_sdr0_candidate_validator_passes_repository_contract(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SDR0 candidate validation passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
