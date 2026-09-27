from copy import deepcopy
from datetime import datetime, time
import json
import os
from pathlib import Path
import plistlib
from tempfile import TemporaryDirectory
import unittest

from scripts.gold_au_operations_rehearsal import (EXPECTED, CASE_CONDITIONS, audit_tasks, engineering_test_contract, engineering_acceptance_matrix,
    local_receipt, perform_rehearsal, research_to_rehearsal_signal, verify_local_receipt, verify_rehearsal, write_new_result)
from tests.test_gold_au_research_diagnostic import research_fixture
from tests.test_gold_au_live_snapshot import TZ


def observation(now):
    return {"status": "READY_RESEARCH_OBSERVATION", "observed_at": now.isoformat(), "broker_action_authorized": False,
            "decision_frozen": False, "price_observation": {"eligibility_reference_session": "2026-09-28",
                "last_completed_session": "2026-09-24", "contract": "au2612", "close_above_prior_20_close_high": False,
                "one_lot_2atr_price_risk_cny_excluding_unknown_execution_costs": 35344},
            "macro_observation": {"pass": False, "reason": "MACRO_ADVERSE"},
            "risk_policy_observation": {"indicative_frozen_policy_budget_cny": 12500, "wgc_status": "UNKNOWN"}}


class OperationsRehearsalTests(unittest.TestCase):
    def test_signal_is_explicit_current_clock_rehearsal_without_order_fields(self):
        now = datetime.fromisoformat("2026-09-26T19:00:00+08:00")
        signal = research_to_rehearsal_signal(observation(now), now=now)
        self.assertEqual(signal["purpose"], "REHEARSAL_ONLY")
        self.assertEqual(signal["research_reason"], "NO_BREAKOUT")
        self.assertFalse(signal["actionable_entry"])
        self.assertFalse(signal["broker_order_authorized"])
        for field in ("signal_id", "valid_from", "valid_until", "action_contract"):
            self.assertNotIn(field, signal)
        self.assertEqual(signal["observed_at"], now.isoformat())

    def test_no_valid_research_no_conversion_and_receipt_tamper_denied(self):
        now = datetime.fromisoformat("2026-09-26T19:00:00+08:00")
        research = observation(now)
        for key, value in (("status", "BLOCKED"), ("broker_action_authorized", True), ("decision_frozen", True)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                research_to_rehearsal_signal({**research, key: value}, now=now)
        signal = research_to_rehearsal_signal(research, now=now)
        receipt = local_receipt(signal, research, now=now)
        self.assertTrue(verify_local_receipt(receipt, signal, research))
        receipt["independent_time_authority"] = True
        with self.assertRaises(ValueError): verify_local_receipt(receipt, signal, research)

    def test_loaded_and_zero_runs_are_not_natural_success(self):
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            rows = audit_tasks(directory, as_of=datetime.fromisoformat("2026-09-26T19:00:00+08:00"),
                               launch_dir=directory, observer=lambda _: {"installation": "LOADED", "runs": 0})
            self.assertEqual(len(rows), 4)
            self.assertTrue(all(row["config_status"] == "MISSING_OR_INVALID" for row in rows))
            self.assertTrue(all(row["runs"] == 0 for row in rows))
            self.assertTrue(all(row["natural_morning_success"].startswith("NOT_ESTABLISHED") for row in rows))

    def test_plist_schedule_mismatch_cannot_pass(self):
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for label, (hour, minute, script) in EXPECTED.items():
                executable = directory / "python"; executable.touch()
                worker = directory / script; worker.touch()
                config = {"Label": label, "ProgramArguments": [str(executable), str(worker), "--runtime-dir", str(directory), "--execute"],
                          "RunAtLoad": True, "StartCalendarInterval": [{"Hour": hour, "Minute": minute, "Weekday": w} for w in range(1,6)]}
                (directory / (label + ".plist")).write_bytes(plistlib.dumps(config))
            rows = audit_tasks(directory, as_of=datetime.fromisoformat("2026-09-26T19:00:00+08:00"),
                               launch_dir=directory, observer=lambda _: {})
            self.assertTrue(all(row["config_status"] == "CONFIG_MISMATCH" for row in rows))

    def test_engineering_contract_has_distinct_tight_risk_and_no_authority(self):
        now = datetime.fromisoformat("2026-09-26T19:00:00+08:00")
        contract = engineering_test_contract(signal=research_to_rehearsal_signal(observation(now), now=now), now=now)
        self.assertEqual(contract["maximum_quantity_lots"], 1)
        self.assertEqual(contract["maximum_hold_seconds"], 120)
        self.assertEqual(contract["risk"]["maximum_planned_loss_cny"], "5000")
        self.assertEqual(contract["risk"]["maximum_stop_distance_cny_per_gram"], "4")
        self.assertEqual(contract["risk"]["slippage_ticks_per_side"], 5)
        self.assertFalse(contract["overnight_allowed"])
        self.assertFalse(contract["counts_as_strategy_return_sample"])
        self.assertFalse(contract["frozen_formal_2atr_rule_changed"])
        self.assertFalse(contract["broker_action_authorized"])

    def test_real_public_fixture_full_local_rehearsal_no_runtime_mutation(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary); os.chmod(root, 0o700)
            request, day, _, _ = research_fixture(root)
            request_path = root / "rehearsal-request.json"
            request_path.write_text(json.dumps(request))
            now = datetime.combine(day, time(12), TZ)
            before = {str(path): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            result = perform_rehearsal(request_path, root, now=now, launch_dir=root, observer=lambda _: {"installation":"UNKNOWN"})
            after = {str(path): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(before, after)
            self.assertEqual(result["status"], "REHEARSAL_LOCAL_PIPELINE_VERIFIED_NOT_NATURAL_NOT_SIMNOW")
            self.assertTrue(verify_rehearsal(result))
            self.assertFalse((root / "gold_au_decisions.sqlite").exists())
            self.assertFalse(result["observation_30_days_started"])
            self.assertEqual(result["broker_calls"], 0)
            self.assertFalse(result["receipt"]["independent_time_authority"])
            altered = deepcopy(result); altered["signal"]["breakout"] = not altered["signal"]["breakout"]
            with self.assertRaises(ValueError): verify_rehearsal(altered)
            altered = deepcopy(result); altered["stage_chain"][1]["previous_hash"] = "changed"
            with self.assertRaises(ValueError): verify_rehearsal(altered)
            altered = deepcopy(result); altered["engineering_test_contract"]["maximum_quantity_lots"] = 2
            with self.assertRaises(ValueError): verify_rehearsal(altered)
            output = root / "new-rehearsal"; write_new_result(output, result)
            with self.assertRaises(ValueError): write_new_result(output, result)
            matrix = json.loads((output / "ENGINEERING-acceptance-matrix.json").read_bytes())
            self.assertEqual({item["case_id"] for item in matrix["items"]}, set(CASE_CONDITIONS))
            self.assertEqual(matrix["actual_pass_count"], 0)
            self.assertTrue(all(item["evidence_ref"] is None for item in matrix["items"]))
            self.assertTrue(all(item["offline_evidence"]["kind"] == "REHEARSAL" for item in matrix["items"]))


if __name__ == "__main__": unittest.main()
