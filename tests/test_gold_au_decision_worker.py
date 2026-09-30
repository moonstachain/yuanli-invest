"""The scheduled entry must record missing input without implying trade authority."""

from datetime import datetime
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo

from scripts.gold_au_decision_worker import run_once
from tests.schedule_timezone_fixture import host_timezone_link

from scripts.install_gold_au_decision_schedule import render
from yuanli_invest.gold_au_decision_log import DecisionLogDenied, LocalDecisionLog


AT_DECISION = datetime(2026, 9, 25, 8, 30, 1, tzinfo=ZoneInfo("Asia/Shanghai"))


class DecisionWorkerTests(unittest.TestCase):
    def test_missing_request_is_one_explicit_skip(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            receipt = run_once(root, clock=lambda: AT_DECISION)
            self.assertEqual(receipt["input_status"], "MISSING_DAILY_REQUEST")
            self.assertEqual(receipt["outcome_status"], "SKIPPED")
            self.assertFalse(receipt["broker_action_authorized"])
            log = LocalDecisionLog(root / "gold_au_decisions.sqlite", clock=lambda: AT_DECISION)
            self.assertEqual(log.verify_chain()["record_count"], 1)
            with self.assertRaisesRegex(DecisionLogDenied, "DUPLICATE_DECISION_DATE"):
                run_once(root, clock=lambda: AT_DECISION)

    def test_invalid_request_is_skipped_and_disclosed(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            requests = root / "requests"
            requests.mkdir(mode=0o700)
            (requests / "2026-09-25.json").write_text(json.dumps({
                "schema_version": "gold-au-live-snapshot-request.v1",
                "decision_date": "2026-09-24",
            }))
            receipt = run_once(root, clock=lambda: AT_DECISION)
            self.assertEqual(receipt["input_status"], "INVALID_DAILY_REQUEST")
            self.assertEqual(receipt["outcome_status"], "SKIPPED")

    def test_runtime_directory_must_be_private(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o755)
            with self.assertRaisesRegex(DecisionLogDenied, "INSECURE_RUNTIME_DIRECTORY"):
                run_once(root, clock=lambda: AT_DECISION)

    def test_schedule_only_invokes_read_only_worker_at_0830(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            with host_timezone_link():
                job = render(root)
            self.assertEqual([item["Weekday"] for item in job["StartCalendarInterval"]],
                             [1, 2, 3, 4, 5])
            self.assertTrue(all(item["Hour"] == 8 and item["Minute"] == 30
                                for item in job["StartCalendarInterval"]))
            self.assertFalse(job["RunAtLoad"])
            self.assertTrue(job["ProgramArguments"][1].endswith("gold_au_decision_worker.py"))

    def test_schedule_rejects_utc_host_without_mutation(self):
        with TemporaryDirectory() as temporary, host_timezone_link("Etc/UTC"):
            root = Path(temporary)
            root.chmod(0o700)
            with self.assertRaisesRegex(ValueError, "host timezone must be Asia/Shanghai"):
                render(root)
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
