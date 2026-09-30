"""Synthetic decision-log mechanics; no real witness, account, or order."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from tests.test_gold_au_live_snapshot import fixture as live_snapshot_fixture
from yuanli_invest.gold_au_decision_log import DecisionLogDenied, LocalDecisionLog
from yuanli_invest.receipts import canonical_hash


TZ = ZoneInfo("Asia/Shanghai")
DAY = date(2025, 9, 25)
DECISION = datetime.combine(DAY, time(8, 30), TZ)


class MutableClock:
    def __init__(self, value: datetime):
        self.value = value

    def __call__(self) -> datetime:
        return self.value


class SequencedClock:
    def __init__(self, values: list[datetime]):
        self.values = iter(values)

    def __call__(self) -> datetime:
        return next(self.values)


def no_entry_snapshot(as_of: datetime) -> dict:
    dataset = {"bars": [], "observations": []}
    signal = {"as_of": as_of.isoformat(), "pit_mode": "strict",
              "broker_order_authorized": False, "actionable_entry": False,
              "reason": "NO_BREAKOUT", "entry": False}
    return {"schema_version": "gold-au-live-snapshot.v1",
            "status": "READY_STRICT_RESEARCH_SIGNAL", "as_of": as_of.isoformat(),
            "decision_at": as_of.isoformat(), "dataset": dataset,
            "dataset_sha256": canonical_hash(dataset), "signal": signal,
            "source_receipts": {"synthetic": "TEST_ONLY"},
            "broker_action_authorized": False}


class DecisionLogTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "decisions.sqlite"
        self.clock = MutableClock(DECISION + timedelta(seconds=20))
        self.log = LocalDecisionLog(self.path, clock=self.clock)
        self.request = {"schema_version": "gold-au-live-snapshot-request.v1",
                        "decision_date": DAY.isoformat()}

    def test_skipped_live_result_is_full_and_hashed(self):
        receipt = self.log.capture(self.request)
        self.assertEqual(receipt["status"], "LOCAL_CANDIDATE")
        self.assertEqual(receipt["outcome_status"], "SKIPPED")
        self.assertEqual(receipt["outcome_reason"], "MISSING_CALENDAR_RECEIPT_PATH")
        self.assertFalse(receipt["broker_action_authorized"])
        read = self.log.local_readback(DAY.isoformat())
        record = read["record"]
        self.assertEqual(record["request_sha256"], "sha256:" + canonical_hash(self.request))
        self.assertEqual(record["snapshot_sha256"], "sha256:" + canonical_hash(record["snapshot"]))
        self.assertEqual(record["snapshot"]["reason"], "MISSING_CALENDAR_RECEIPT_PATH")
        self.assertEqual(record["snapshot"]["detail"], "")
        self.assertEqual(self.log.verify_chain()["record_count"], 1)
        self.assertFalse(read["independent_readback_verified"])
        self.assertFalse(read["append_only_verified"])
        self.assertTrue(read["external_anchor_required"])

    def test_ready_but_nonactionable_is_recorded(self):
        with patch("yuanli_invest.gold_au_decision_log.prepare_live_snapshot", side_effect=lambda req, as_of: no_entry_snapshot(as_of)):
            receipt = self.log.capture(self.request)
        self.assertEqual(receipt["outcome_status"], "READY_STRICT_RESEARCH_SIGNAL")
        self.assertEqual(receipt["outcome_reason"], "NO_BREAKOUT")
        self.assertFalse(receipt["actionable_entry"])
        self.assertEqual(self.log.local_readback(DAY.isoformat())["record"]["snapshot"]["signal"]["entry"], False)

    def test_real_snapshot_function_ready_result_is_bound_without_order_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request, day, _ = live_snapshot_fixture(root)
            clock = MutableClock(datetime.combine(day, time(8, 30), TZ) + timedelta(seconds=20))
            log = LocalDecisionLog(root / "live_decisions.sqlite", clock=clock)
            result = log.capture(request)
            self.assertEqual(result["outcome_status"], "READY_STRICT_RESEARCH_SIGNAL")
            record = log.local_readback(day.isoformat())["record"]
            self.assertEqual(record["snapshot"]["signal"]["pit_mode"], "strict")
            self.assertEqual(record["snapshot"]["dataset_sha256"],
                             canonical_hash(record["snapshot"]["dataset"]))
            self.assertFalse(result["broker_action_authorized"])

    def test_same_day_repeat_is_rejected_and_first_result_preserved(self):
        first = self.log.capture(self.request)
        with self.assertRaises(DecisionLogDenied) as error:
            self.log.capture(self.request)
        self.assertEqual(error.exception.code, "DUPLICATE_DECISION_DATE")
        self.assertEqual(self.log.verify_chain()["record_count"], 1)
        self.assertEqual(self.log.local_readback(DAY.isoformat())["record_sha256"], first["record_sha256"])

    def test_before_or_after_0830_and_wrong_day_fail_closed(self):
        for clock_value in (DECISION - timedelta(seconds=1), DECISION + timedelta(minutes=1)):
            with self.subTest(clock_value=clock_value):
                self.clock.value = clock_value
                with self.assertRaises(DecisionLogDenied) as error:
                    self.log.capture(self.request)
                self.assertEqual(error.exception.code, "OUTSIDE_0830_DECISION_MINUTE")
        self.clock.value = DECISION + timedelta(seconds=20)
        with self.assertRaises(DecisionLogDenied) as error:
            self.log.capture({**self.request, "decision_date": "2025-09-24"})
        self.assertEqual(error.exception.code, "OUTSIDE_0830_DECISION_MINUTE")
        self.assertEqual(self.log.verify_chain()["record_count"], 0)

    def test_slow_live_snapshot_never_writes_late_record(self):
        slow = LocalDecisionLog(self.path, clock=SequencedClock(
            [DECISION + timedelta(seconds=20), DECISION + timedelta(minutes=1)]))
        with patch("yuanli_invest.gold_au_decision_log.prepare_live_snapshot", side_effect=lambda req, as_of: no_entry_snapshot(as_of)):
            with self.assertRaises(DecisionLogDenied) as error:
                slow.capture(self.request)
        self.assertEqual(error.exception.code, "LATE_SNAPSHOT_RESULT")
        self.assertEqual(self.log.verify_chain()["record_count"], 0)

    def test_crossing_0831_before_commit_rolls_back(self):
        crossing = LocalDecisionLog(self.path, clock=SequencedClock([
            DECISION + timedelta(seconds=20), DECISION + timedelta(seconds=21),
            DECISION + timedelta(seconds=58), DECISION + timedelta(minutes=1)]))
        with patch("yuanli_invest.gold_au_decision_log.prepare_live_snapshot", side_effect=lambda req, as_of: no_entry_snapshot(as_of)):
            with self.assertRaises(DecisionLogDenied) as error:
                crossing.capture(self.request)
        self.assertEqual(error.exception.code, "LATE_DECISION_COMMIT")
        self.assertEqual(self.log.verify_chain()["record_count"], 0)

    def test_update_delete_triggers_and_hash_readback(self):
        self.log.capture(self.request)
        with sqlite3.connect(self.path) as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE decision_records SET record_sha256='tamper'")
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("DELETE FROM decision_records")
            conn.execute("DROP TRIGGER decision_records_no_update")
        with self.assertRaises(DecisionLogDenied) as error:
            self.log.verify_chain()
        self.assertEqual(error.exception.code, "APPEND_ONLY_TRIGGERS_MISSING")
        # Reopening reinstalls the guard, but cannot hide a changed record.
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE decision_records SET record_sha256='tamper'")
        with self.assertRaises(DecisionLogDenied) as error:
            LocalDecisionLog(self.path, clock=self.clock)
        self.assertEqual(error.exception.code, "DECISION_RECORD_CORRUPT")

    def test_insecure_database_and_symlink_are_rejected(self):
        target = self.path.parent / "world-readable.sqlite"
        target.write_bytes(b"")
        target.chmod(0o644)
        with self.assertRaises(DecisionLogDenied) as error:
            LocalDecisionLog(target)
        self.assertEqual(error.exception.code, "INSECURE_LOG_PATH")
        link = self.path.parent / "linked.sqlite"
        link.symlink_to(self.path)
        with self.assertRaises(DecisionLogDenied) as error:
            LocalDecisionLog(link)
        self.assertEqual(error.exception.code, "INVALID_LOG_PATH_OR_ID")

    def test_concurrent_same_day_has_one_atomic_append(self):
        other = LocalDecisionLog(self.path, clock=self.clock)
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = [pool.submit(log.capture, self.request) for log in (self.log, other)]
        results = []
        for future in outcomes:
            try:
                results.append(future.result()["status"])
            except DecisionLogDenied as exc:
                results.append(exc.code)
        self.assertCountEqual(results, ["LOCAL_CANDIDATE", "DUPLICATE_DECISION_DATE"])
        self.assertEqual(self.log.verify_chain()["record_count"], 1)


if __name__ == "__main__":
    unittest.main()
