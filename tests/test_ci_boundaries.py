"""Executable workflow contracts: check names and access to external accounts."""
import unittest
from pathlib import Path

import yaml

from scripts.run_checks import historical_change

ROOT = Path(__file__).resolve().parents[1]


class CIBoundaryTests(unittest.TestCase):
    def test_required_jobs_always_exist_on_pull_requests(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
        # YAML 1.1 interprets the key 'on' as True; support both loader versions.
        events = workflow.get("on", workflow.get(True))
        self.assertIn("pull_request", events)
        self.assertIsNone(events["pull_request"])
        for name in ("contracts", "governance"):
            job = workflow["jobs"][name]
            self.assertEqual(job["name"], name)
            self.assertNotIn("if", job)
        contracts = workflow["jobs"]["contracts"]
        self.assertTrue(any("--scope current" in step.get("run", "") for step in contracts["steps"]))

    def test_secret_bearing_jobs_require_manual_trusted_main(self):
        for path in (ROOT / ".github/workflows").glob("*.yml"):
            workflow = yaml.safe_load(path.read_text())
            self.assertNotIn("secrets.", str(workflow.get("env", {})), path.name)
            for name, job in workflow.get("jobs", {}).items():
                if "secrets." not in str(job):
                    continue
                with self.subTest(workflow=path.name, job=name):
                    condition = job.get("if", "")
                    self.assertIn("github.event_name == 'workflow_dispatch'", condition)
                    self.assertIn("github.ref == 'refs/heads/main'", condition)
                    self.assertNotIn("hashFiles", condition)

    def test_current_code_changes_need_no_historical_checkout(self):
        self.assertFalse(historical_change(["src/yuanli_invest/gold.py", "README.md"]))
        for path in ("receipts/source.json", "scripts/validate_q0_architecture.py", "tests/check-scopes.json"):
            self.assertTrue(historical_change([path]))


if __name__ == "__main__":
    unittest.main()
