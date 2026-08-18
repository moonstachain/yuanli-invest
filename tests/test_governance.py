import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GovernanceTests(unittest.TestCase):
    def test_governance_invariants(self):
        subprocess.run([sys.executable, "scripts/check_governance.py"], cwd=ROOT, check=True)

    def test_leak_guard(self):
        subprocess.run([sys.executable, "scripts/leak_guard.py"], cwd=ROOT, check=True)


if __name__ == "__main__":
    unittest.main()
