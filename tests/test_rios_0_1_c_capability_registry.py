import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_rios_0_1_c_capability_registry.py"
STATE = ROOT / "docs" / "architecture" / "rios" / "0.1-c" / "RIOS-0.1-C-STATE.json"


class RIOS01CBootstrapRedTests(unittest.TestCase):
    def test_validator_entrypoint_runs_primitive_self_check(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), "--self-test-primitives"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)

    def test_initial_state_exists(self):
        self.assertTrue(STATE.exists(), str(STATE))


if __name__ == "__main__":
    unittest.main()
