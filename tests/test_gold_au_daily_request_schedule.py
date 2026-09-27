"""08:25 assembler must remain a separate local-only launchd candidate."""

from pathlib import Path
import plistlib
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock

from scripts.install_gold_au_daily_request_schedule import install, render


class DailyRequestScheduleTests(unittest.TestCase):
    def test_render_runs_weekdays_0825_without_load_trigger(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            job = render(root)
            self.assertFalse(job["RunAtLoad"])
            self.assertTrue(job["ProgramArguments"][1].endswith("gold_au_daily_request.py"))
            self.assertEqual(job["ProgramArguments"][-1], "--execute")
            self.assertEqual([row["Weekday"] for row in job["StartCalendarInterval"]], [1, 2, 3, 4, 5])
            self.assertTrue(all(row["Hour"] == 8 and row["Minute"] == 25 for row in job["StartCalendarInterval"]))

    def test_default_install_only_renders_private_candidate(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            runner = Mock()
            result = install(root, runner=runner)
            self.assertEqual(result["status"], "RENDERED_ONLY")
            runner.assert_not_called()
            destination = Path(result["path"])
            self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
            self.assertEqual(plistlib.loads(destination.read_bytes()), render(root))
            self.assertFalse(result["broker_action_authorized"])

    def test_symlink_or_insecure_runtime_never_mutates_schedule(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            (root / "launchd").symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "INSECURE_OUTPUT_DIRECTORY"):
                install(root)
            root.chmod(0o755)
            with self.assertRaisesRegex(ValueError, "INSECURE_RUNTIME_DIRECTORY"):
                render(root)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
