"""Daily macro capture is date-bounded and has no broker path."""

from datetime import datetime, date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo

from scripts.gold_macro_daily_worker import run_once
from tests.schedule_timezone_fixture import host_timezone_link

from scripts.install_gold_macro_capture_schedule import render


TZ = ZoneInfo("Asia/Shanghai")


class MacroDailyWorkerTests(unittest.TestCase):
    def test_one_capture_uses_current_day_and_rejects_repeat(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            called = []

            def capture(**kwargs):
                called.append(kwargs)
                kwargs["output_dir"].mkdir()
                (kwargs["output_dir"] / "manifest.json").write_text("{}")
                return {"status": "CAPTURED", "captures": [
                    {"status": "CAPTURED", "provider_series": "DFII10"},
                    {"status": "CAPTURED", "provider_series": "DTWEXBGS"}]}

            at = datetime(2026, 9, 25, 8, 10, 1, tzinfo=TZ)
            result = run_once(root, clock=lambda: at, capture=capture)
            self.assertEqual(result["status"], "CAPTURED")
            self.assertFalse(result["broker_action_authorized"])
            self.assertEqual(called[0]["end_inclusive"], date(2026, 9, 25))
            self.assertEqual((called[0]["end_inclusive"] - called[0]["start"]).days, 180)
            with self.assertRaisesRegex(FileExistsError, "DAILY_CAPTURE_ALREADY_EXISTS"):
                run_once(root, clock=lambda: at, capture=capture)

    def test_schedule_is_read_only_and_does_not_run_on_load(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            with host_timezone_link():
                job = render(root)
            self.assertFalse(job["RunAtLoad"])
            self.assertTrue(job["ProgramArguments"][1].endswith("gold_macro_daily_worker.py"))
            self.assertEqual([row["Weekday"] for row in job["StartCalendarInterval"]],
                             [1, 2, 3, 4, 5])
            self.assertTrue(all(row["Hour"] == 8 and row["Minute"] == 10
                                for row in job["StartCalendarInterval"]))

    def test_schedule_rejects_utc_host_without_mutation(self):
        with TemporaryDirectory() as temporary, host_timezone_link("Etc/UTC"):
            root = Path(temporary)
            root.chmod(0o700)
            with self.assertRaisesRegex(ValueError, "host timezone must be Asia/Shanghai"):
                render(root)
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
