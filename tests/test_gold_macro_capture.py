import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.gold_macro_capture import run
from yuanli_invest.gold_macro_capture import MacroSpec, fetch_raw, normalize_raw


CAPTURE = datetime(2026, 9, 25, 0, 30, tzinfo=timezone.utc)


class GoldMacroCaptureTests(unittest.TestCase):
    def test_spec_has_fixed_series_host_and_bounded_interval(self):
        spec = MacroSpec("DTWEXBGS", date(2019, 7, 1), date(2026, 9, 23))
        self.assertEqual(spec.url(), "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS&cosd=2019-07-01&coed=2026-09-23")
        with self.assertRaises(ValueError):
            MacroSpec("DXY", date(2024, 1, 1), date(2024, 2, 1))
        with self.assertRaises(ValueError):
            MacroSpec("DFII10", date(2010, 1, 1), date(2024, 1, 1))

    def test_fetch_accepts_only_exact_csv_response_without_redirect(self):
        spec = MacroSpec("DFII10", date(2026, 9, 17), date(2026, 9, 18))
        raw = b"observation_date,DFII10\n2026-09-17,2.61\n"
        marker = b"\n__YUANLI_GOLD_MACRO_RESPONSE__"

        def runner(argv, **kwargs):
            self.assertEqual(argv[:2], ["curl", "-q"])
            self.assertNotIn("--location", argv)
            self.assertEqual(argv[-1], spec.url())
            return SimpleNamespace(returncode=0, stdout=raw + marker +
                                   b"200|" + spec.url().encode() + b"|application/csv")

        self.assertEqual(fetch_raw(spec, runner=runner), raw)

        def redirected(argv, **kwargs):
            return SimpleNamespace(returncode=0, stdout=raw + marker +
                                   b"200|https://example.com/elsewhere|application/csv")

        with self.assertRaises(ValueError):
            fetch_raw(spec, runner=redirected)

    def test_normalized_h10_keeps_fred_distributor_and_unknown_vintage(self):
        spec = MacroSpec("DTWEXBGS", date(2026, 9, 17), date(2026, 9, 20))
        raw = b"observation_date,DTWEXBGS\n2026-09-17,119.3489\n2026-09-18,119.5133\n2026-09-19,\n"
        capture = normalize_raw(raw, spec, captured_at=CAPTURE)
        self.assertEqual(capture["row_count"], 2)
        self.assertEqual(capture["missing_value_rows"], 1)
        self.assertEqual(capture["source_series"], "FRED:DTWEXBGS")
        self.assertEqual(capture["strategy_series_candidate"], "FED:H10:DTWEXBGS")
        self.assertEqual(capture["identity_mapping_status"], "UNDECLARED")
        self.assertTrue(capture["identity_mapping_required"])
        self.assertEqual(capture["underlying_release"], "FEDERAL_RESERVE_H10")
        self.assertFalse(capture["historical_release_time_verified"])
        self.assertEqual(capture["raw_sha256"], hashlib.sha256(raw).hexdigest())
        row = capture["observations"][0]
        self.assertEqual(row["series"], "FRED:DTWEXBGS")
        self.assertEqual(row["measurement_regime"], "FRED_DTWEXBGS_DISTRIBUTED_H10_BROAD_DOLLAR_DATE_LABEL_NY")
        self.assertEqual(row["observed_on"], "2026-09-17")
        self.assertEqual(row["value"], 119.3489)
        self.assertEqual(row["pit_grade"], "UNKNOWN")
        self.assertEqual(row["vintage_kind"], "UNKNOWN")
        self.assertEqual(row["released_at"], CAPTURE.isoformat())
        self.assertEqual(row["retrieved_at"], CAPTURE.isoformat())
        self.assertEqual(row["available_at"], CAPTURE.isoformat())
        self.assertEqual(row["release_time_basis"], "FIRST_KNOWN_AT_CAPTURE_NOT_ACTUAL_PUBLICATION")

    def test_dfii10_has_exact_identity_but_still_not_pit_verified(self):
        spec = MacroSpec("DFII10", date(2026, 9, 17), date(2026, 9, 18))
        capture = normalize_raw(b"observation_date,DFII10\n2026-09-17,2.61\n2026-09-18,2.68\n", spec,
                                captured_at=CAPTURE)
        self.assertEqual(capture["source_series"], "FRED:DFII10")
        self.assertFalse(capture["identity_mapping_required"])
        self.assertEqual(capture["identity_mapping_status"], "EXACT_SERIES_ID")
        self.assertEqual(capture["underlying_release"], "FEDERAL_RESERVE_H15")
        self.assertEqual(capture["observations"][0]["unit"], "PERCENT")
        self.assertEqual(capture["observations"][0]["pit_grade"], "UNKNOWN")

    def test_rejects_mislabelled_conflicting_and_future_csv(self):
        spec = MacroSpec("DFII10", date(2026, 9, 17), date(2026, 9, 28))
        for raw in (
            b"observation_date,DXY\n2026-09-17,2.61\n",
            b"observation_date,DFII10\n2026-09-17,2.61\n2026-09-17,2.62\n",
            b"observation_date,DFII10\n2026-09-26,2.61\n",
            b"observation_date,DFII10\n2026-09-17,nan\n",
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                normalize_raw(raw, spec, captured_at=CAPTURE)

    def test_dry_run_creates_nothing_and_execution_preserves_raw_hash(self):
        def fake_fetch(spec):
            return (f"observation_date,{spec.provider_series}\n2026-09-17,"
                    f"{'2.61' if spec.provider_series == 'DFII10' else '119.3489'}\n").encode()

        with TemporaryDirectory() as directory:
            target = Path(directory) / "capture"
            kwargs = dict(start=date(2026, 9, 17), end_inclusive=date(2026, 9, 18),
                          output_dir=target, fetch=fake_fetch, now=lambda: CAPTURE)
            planned = run(execute=False, **kwargs)
            self.assertEqual(planned["status"], "DRY_RUN")
            self.assertFalse(target.exists())
            with patch("scripts.gold_macro_capture.time.sleep"):
                result = run(execute=True, **kwargs)
            self.assertEqual(result["status"], "CAPTURED")
            self.assertEqual([capture["row_count"] for capture in result["captures"]], [1, 1])
            self.assertEqual(result["action_authority"], "none")
            on_disk = json.loads((target / "manifest.json").read_text())
            for capture in on_disk["captures"]:
                raw = Path(capture["raw_file"]).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), capture["raw_sha256"])
                self.assertTrue(Path(capture["raw_file"]).is_relative_to(target.resolve()))
            with self.assertRaises(FileExistsError):
                run(execute=True, **kwargs)

    def test_raw_output_inside_worktree_is_rejected(self):
        worktree = Path(__file__).resolve().parents[1]
        with self.assertRaises(ValueError):
            run(start=date(2026, 9, 17), end_inclusive=date(2026, 9, 18),
                output_dir=worktree / "private", execute=False)


if __name__ == "__main__":
    unittest.main()
