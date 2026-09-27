"""Official-window selection, provenance retention and bounded missing-day capture."""

from datetime import date, datetime, timedelta
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from scripts.gold_au_shfe_archive_worker import (
    ArchiveDenied, CONFIG_SCHEMA, PRIOR_SESSIONS, ROLLING_SCHEMA, prepare_archive, run_once,
)
from scripts.gold_au_shfe_daily_capture import normalize_daily
from tests.schedule_timezone_fixture import host_timezone_link

from scripts.install_gold_au_shfe_archive_schedule import render

SHANGHAI = ZoneInfo("Asia/Shanghai")
MONDAY = date(2026, 9, 28)
AT_MONDAY = datetime(2026, 9, 28, 8, 5, tzinfo=SHANGHAI)
ORIGINAL_CAPTURE = "2026-09-26T00:00:00+00:00"


def official_calendar_fixture():
    # Synthetic protocol fixture: declared planned sessions, never market bars.
    day, sessions = date(2025, 1, 1), []
    while day <= date(2026, 12, 31):
        if day.weekday() < 5 and day != date(2026, 9, 25):
            sessions.append(day.isoformat())
        day += timedelta(days=1)
    return {"covered_years": [2025, 2026], "sessions": sessions,
            "raw_sha256": "c" * 64}


def report_bytes(day, *, price=1000):
    return json.dumps({"report_date": day.replace("-", ""), "o_curinstrument": [
        {"PRODUCTID": "au_f", "DELIVERYMONTH": "2612", "OPENPRICE": price,
         "HIGHESTPRICE": price + 1, "LOWESTPRICE": price - 1, "CLOSEPRICE": price,
         "VOLUME": 100, "OPENINTEREST": 1000},
    ]}, sort_keys=True).encode()


def seed_fixture(root):
    root = root.resolve()
    root.chmod(0o700)
    calendar = official_calendar_fixture()
    prior = [day for day in calendar["sessions"] if day < MONDAY.isoformat()][-PRIOR_SESSIONS:]
    folder = root / "seed"
    raw_dir = folder / "raw"
    raw_dir.mkdir(mode=0o700, parents=True)
    reports = []
    for day in prior:
        raw = report_bytes(day)
        path = raw_dir / ("kx" + day.replace("-", "") + ".dat")
        path.write_bytes(raw)
        row = normalize_daily(raw, day)
        row.update({"raw_file": str(path), "captured_at": ORIGINAL_CAPTURE})
        reports.append(row)
    manifest = {"schema_version": "gold-au-shfe-daily-capture.v1", "mode": "EXECUTE",
                "status": "PARTIAL_FAILURE", "historical_release_time_verified": False,
                "captured_at": ORIGINAL_CAPTURE, "reports": reports,
                "errors": [{"date": "2026-09-25", "error_type": "HTTPError"}]}
    manifest_path = folder / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    config = {"schema_version": CONFIG_SCHEMA,
              "calendar_receipt_path": str(root / "calendar.json"),
              "seed_manifest_paths": [str(manifest_path)]}
    (root / "shfe_archive_sources.json").write_text(json.dumps(config))
    return root, calendar, manifest_path, manifest


def forbidden_fetch(day):
    raise AssertionError("read-only offline preparation unexpectedly fetched " + day)


class RollingSHFEArchiveTests(unittest.TestCase):
    def test_dry_run_selects_official_prior_sessions_without_fetch_or_write(self):
        with TemporaryDirectory() as directory:
            root, calendar, source, _ = seed_fixture(Path(directory))
            output = root / "shfe_archives" / MONDAY.isoformat()
            result = prepare_archive(calendar_receipt=calendar, seed_manifest_paths=[source],
                                     decision_day=MONDAY, observed_at=AT_MONDAY,
                                     output_dir=output, fetch=forbidden_fetch)
            self.assertEqual(result["status"], "DRY_RUN")
            self.assertEqual(result["requested_days"], 273)
            self.assertEqual(result["interval"][-1], "2026-09-24")
            self.assertEqual(result["retained_reports"], 273)
            self.assertEqual(result["new_requests"], 0)
            self.assertFalse(output.exists())

    def test_offline_future_seed_retains_original_capture_hash_and_is_immutable(self):
        with TemporaryDirectory() as directory:
            root, calendar, source, original = seed_fixture(Path(directory))
            observed = datetime(2026, 9, 26, 12, tzinfo=SHANGHAI)
            output = root / "shfe_seeds" / MONDAY.isoformat()
            result = prepare_archive(calendar_receipt=calendar, seed_manifest_paths=[source],
                                     decision_day=MONDAY, observed_at=observed, output_dir=output,
                                     execute=True, fetch=forbidden_fetch, clock=lambda: observed)
            self.assertEqual(result["status"], "CAPTURED")
            self.assertEqual(result["new_requests"], 0)
            self.assertEqual(len(result["reports"]), 273)
            self.assertFalse(result["historical_release_time_verified"])
            for old, new in zip(original["reports"], result["reports"]):
                self.assertEqual(new["captured_at"], old["captured_at"])
                self.assertEqual(new["raw_sha256"], old["raw_sha256"])
                self.assertEqual(Path(new["raw_file"]).read_bytes(), Path(old["raw_file"]).read_bytes())
                self.assertNotIn("first_published_at", new)
                self.assertEqual(Path(new["raw_file"]).stat().st_mode & 0o777, 0o600)
            self.assertEqual((output / "manifest.json").stat().st_mode & 0o777, 0o600)
            with self.assertRaisesRegex(ArchiveDenied, "IMMUTABLE_ARCHIVE_ALREADY_EXISTS"):
                prepare_archive(calendar_receipt=calendar, seed_manifest_paths=[source],
                                decision_day=MONDAY, observed_at=observed, output_dir=output,
                                execute=True, fetch=forbidden_fetch, clock=lambda: observed)

    def test_next_session_reuses_previous_archive_and_fetches_only_one_official_day(self):
        with TemporaryDirectory() as directory:
            root, calendar, source, _ = seed_fixture(Path(directory))
            previous = root / "shfe_archives" / MONDAY.isoformat()
            prepare_archive(calendar_receipt=calendar, seed_manifest_paths=[source],
                            decision_day=MONDAY, observed_at=AT_MONDAY, output_dir=previous,
                            execute=True, fetch=forbidden_fetch, clock=lambda: AT_MONDAY)
            tuesday = datetime(2026, 9, 29, 8, 5, tzinfo=SHANGHAI)
            calls = []

            def fetch(day):
                calls.append(day)
                return report_bytes(day)

            with patch("scripts.gold_au_shfe_archive_worker.load_calendar_receipt", return_value=calendar):
                result = run_once(root, execute=True, clock=lambda: tuesday, fetch=fetch)
            self.assertEqual(calls, ["2026-09-28"])
            self.assertEqual(result["status"], "CAPTURED")
            self.assertEqual(result["retained_reports"], 272)
            manifest = json.loads(Path(result["manifest_path"]).read_text())
            self.assertEqual(manifest["reports"][-1]["captured_at"], tuesday.astimezone(ZoneInfo("UTC")).isoformat())
            self.assertTrue(all(row["captured_at"] == ORIGINAL_CAPTURE for row in manifest["reports"][:-1]))

    def test_tampered_raw_and_future_receipts_stop_before_fetch_and_write(self):
        for kind in ("raw", "capture", "bars"):
            with self.subTest(kind=kind), TemporaryDirectory() as directory:
                root, calendar, source, manifest = seed_fixture(Path(directory))
                if kind == "raw":
                    Path(manifest["reports"][-1]["raw_file"]).write_bytes(b"tampered")
                    expected = "SHFE_RAW_HASH_MISMATCH"
                elif kind == "capture":
                    manifest["reports"][-1]["captured_at"] = "2026-09-29T00:00:00+00:00"
                    expected = "FUTURE_SHFE_SOURCE_REPORT"
                else:
                    manifest["reports"][-1]["bars"][0]["close"] = "999"
                    expected = "SHFE_MANIFEST_RAW_DISAGREEMENT"
                source.write_text(json.dumps(manifest))
                output = root / "shfe_archives" / MONDAY.isoformat()
                with self.assertRaisesRegex(ArchiveDenied, expected):
                    prepare_archive(calendar_receipt=calendar, seed_manifest_paths=[source],
                                    decision_day=MONDAY, observed_at=AT_MONDAY, output_dir=output,
                                    execute=True, fetch_missing=True, fetch=forbidden_fetch)
                self.assertFalse(output.exists())

    def test_six_missing_sessions_fail_before_network(self):
        with TemporaryDirectory() as directory:
            root, calendar, source, manifest = seed_fixture(Path(directory))
            manifest["reports"] = manifest["reports"][:-6]
            source.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ArchiveDenied, "GAP_EXCEEDS_FIVE_REQUESTS"):
                prepare_archive(calendar_receipt=calendar, seed_manifest_paths=[source],
                                decision_day=MONDAY, observed_at=AT_MONDAY,
                                output_dir=root / "shfe_archives" / MONDAY.isoformat(),
                                execute=True, fetch_missing=True, fetch=forbidden_fetch)

    def test_weekend_and_official_holiday_skip_before_network_or_archive_creation(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            root.chmod(0o700)
            weekend = datetime(2026, 9, 26, 8, 5, tzinfo=SHANGHAI)
            result = run_once(root, execute=True, clock=lambda: weekend, fetch=forbidden_fetch)
            self.assertEqual(result["reason"], "WEEKEND")  # no config even read
            root, calendar, _, _ = seed_fixture(root)
            holiday = datetime(2026, 9, 25, 8, 5, tzinfo=SHANGHAI)
            with patch("scripts.gold_au_shfe_archive_worker.load_calendar_receipt", return_value=calendar):
                result = run_once(root, execute=True, clock=lambda: holiday, fetch=forbidden_fetch)
            self.assertEqual(result["reason"], "OFFICIAL_HOLIDAY")
            self.assertFalse((root / "shfe_archives").exists())

    def test_stale_previous_archive_identity_is_rejected_before_fetch(self):
        with TemporaryDirectory() as directory:
            root, calendar, _, _ = seed_fixture(Path(directory))
            previous = root / "shfe_archives" / "2026-09-24"
            previous.mkdir(parents=True)
            (previous / "manifest.json").write_text(json.dumps({
                "rolling_schema_version": ROLLING_SCHEMA, "decision_date": "2026-09-23"}))
            with patch("scripts.gold_au_shfe_archive_worker.load_calendar_receipt", return_value=calendar):
                with self.assertRaisesRegex(ArchiveDenied, "STALE_OR_MISIDENTIFIED_PREVIOUS_ARCHIVE"):
                    run_once(root, execute=True, clock=lambda: AT_MONDAY, fetch=forbidden_fetch)

    def test_conflicting_verified_report_bytes_are_rejected(self):
        with TemporaryDirectory() as directory:
            root, calendar, source, manifest = seed_fixture(Path(directory))
            other = root / "other"
            raw_dir = other / "raw"
            raw_dir.mkdir(parents=True)
            day = manifest["reports"][-1]["date"]
            raw = report_bytes(day, price=1002)
            raw_path = raw_dir / ("kx" + day.replace("-", "") + ".dat")
            raw_path.write_bytes(raw)
            row = normalize_daily(raw, day)
            row.update({"captured_at": ORIGINAL_CAPTURE, "raw_file": str(raw_path)})
            conflict = {**manifest, "reports": [row]}
            other_path = other / "manifest.json"
            other_path.write_text(json.dumps(conflict))
            with self.assertRaisesRegex(ArchiveDenied, "CONFLICTING_OFFICIAL_SHFE_REPORTS"):
                prepare_archive(calendar_receipt=calendar, seed_manifest_paths=[source, other_path],
                                decision_day=MONDAY, observed_at=AT_MONDAY,
                                output_dir=root / "output", fetch=forbidden_fetch)

    def test_wrong_date_fetched_report_is_partial_failure_without_fabricated_day(self):
        with TemporaryDirectory() as directory:
            root, calendar, source, manifest = seed_fixture(Path(directory))
            missing = manifest["reports"].pop()["date"]
            source.write_text(json.dumps(manifest))
            result = prepare_archive(calendar_receipt=calendar, seed_manifest_paths=[source],
                                     decision_day=MONDAY, observed_at=AT_MONDAY,
                                     output_dir=root / "shfe_archives" / MONDAY.isoformat(),
                                     execute=True, fetch_missing=True,
                                     fetch=lambda day: report_bytes("2026-09-23"), clock=lambda: AT_MONDAY)
            self.assertEqual(result["status"], "PARTIAL_FAILURE")
            self.assertEqual(result["errors"], [{"date": missing, "reason": "SHFE_RAW_REPORT_DATE_MISMATCH"}])
            self.assertEqual(len(result["reports"]), 272)

    def test_daily_execution_outside_window_and_late_fetch_fail_closed(self):
        with TemporaryDirectory() as directory:
            root, calendar, source, manifest = seed_fixture(Path(directory))
            with patch("scripts.gold_au_shfe_archive_worker.load_calendar_receipt", return_value=calendar):
                with self.assertRaisesRegex(ArchiveDenied, "OUTSIDE_0805_ARCHIVE_WINDOW"):
                    run_once(root, execute=True, clock=lambda: AT_MONDAY.replace(minute=10), fetch=forbidden_fetch)
            manifest["reports"].pop()
            source.write_text(json.dumps(manifest))
            times = iter([AT_MONDAY, AT_MONDAY.replace(minute=10), AT_MONDAY.replace(minute=10)])
            result = prepare_archive(calendar_receipt=calendar, seed_manifest_paths=[source],
                                     decision_day=MONDAY, observed_at=AT_MONDAY,
                                     output_dir=root / "shfe_archives" / MONDAY.isoformat(),
                                     execute=True, fetch_missing=True, fetch=report_bytes,
                                     clock=lambda: next(times), capture_deadline=AT_MONDAY.replace(minute=10))
            self.assertEqual(result["status"], "PARTIAL_FAILURE")
            self.assertEqual(result["errors"][0]["reason"], "SHFE_CAPTURE_DEADLINE_REACHED")
            self.assertEqual(result["new_requests"], 1)

    def test_schedule_is_0805_weekdays_without_run_at_load(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            root.chmod(0o700)
            with host_timezone_link():
                job = render(root)
            self.assertFalse(job["RunAtLoad"])
            self.assertEqual([row["Weekday"] for row in job["StartCalendarInterval"]], [1, 2, 3, 4, 5])
            self.assertTrue(all(row["Hour"] == 8 and row["Minute"] == 5 for row in job["StartCalendarInterval"]))
            self.assertTrue(job["ProgramArguments"][1].endswith("gold_au_shfe_archive_worker.py"))

    def test_schedule_rejects_utc_host_without_mutation(self):
        with TemporaryDirectory() as temporary, host_timezone_link("Etc/UTC"):
            root = Path(temporary)
            root.chmod(0o700)
            with self.assertRaisesRegex(ValueError, "host timezone must be Asia/Shanghai"):
                render(root)
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
