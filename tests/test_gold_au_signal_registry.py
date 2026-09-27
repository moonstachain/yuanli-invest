"""Synthetic preregistration mechanics; no external timestamp authority."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import tempfile
import unittest

from tests.test_gold_au_gateway import case
from yuanli_invest.gold_au_gateway import build_entry_ticket
from yuanli_invest.gold_au_signal_registry import (
    ANCHOR_STATUS, LocalSignalRegistry, RegistryDenied,
)
from yuanli_invest.gold_au_strategy import DEFAULT_CONFIG, evaluate_current_snapshot_signal
from yuanli_invest.gold_paper import PaperDenied
from yuanli_invest.receipts import canonical_hash


def forward_decision(args: dict) -> dict:
    signal = args["signal"]
    return {"schema_version": "gold-au-forward-decision.v2",
            "decision_id": "FWD-GOLD2-SYNTHETIC-PREREG-001",
            "signal_id": signal["signal_id"],
            "strategy_version": "gold-au-strategy.v1", "baseline_id": "CASH",
            "contract": signal["contract"], "action": "OPEN_LONG", "quantity": 1,
            "environment": "SIMNOW_FIRST_NORMAL", "data_mode": "SYNTHETIC_ENGINEERING_ONLY",
            "decision_at": signal["as_of"], "evidence_known_as_of": signal["as_of"],
            "evidence_sha256": signal["evidence_sha256"],
            "parameters_sha256": canonical_hash(DEFAULT_CONFIG),
            "horizons_trading_days": [5, 20], "engineering_test": True}


class MutableClock:
    def __init__(self, value: datetime):
        self.value = value

    def __call__(self) -> datetime:
        return self.value


class SignalRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "prereg.sqlite"
        self.args = case()
        self.decision = datetime.fromisoformat(self.args["signal"]["as_of"])
        self.clock = MutableClock(self.decision + timedelta(seconds=20))
        self.registry = LocalSignalRegistry(self.path, clock=self.clock)

    def register(self, registry: LocalSignalRegistry | None = None) -> dict:
        registry = registry or self.registry
        return registry.register(signal=self.args["signal"],
                                 frozen_dataset=self.args["frozen_dataset"],
                                 forward_decision=forward_decision(self.args),
                                 exchange_calendar=self.args["exchange_calendar"])

    def anchor(self, candidate: dict) -> dict:
        return {"status": ANCHOR_STATUS, "registry_id": candidate["registry_id"],
                "record_id": candidate["record_id"],
                "record_sha256": candidate["raw_sha256"],
                "registry_root_sha256": candidate["registry_root_sha256"],
                "recorded_at": candidate["recorded_at"],
                "anchor_received_at": (self.decision + timedelta(seconds=21)).isoformat(),
                "verifier_identity": "SYNTHETIC_EXTERNAL_ANCHOR_TEST_ONLY",
                "proof_sha256": "sha256:" + "c" * 64,
                "verified_at": self.clock.value.isoformat()}

    def test_current_snapshot_registry_and_gateway_share_exact_frozen_replay(self):
        self.args = case(current_snapshot=True)
        record = self.register()
        self.assertFalse(record["broker_action_authorized"])
        self.clock.value = self.args["now"]
        receipt, verifier = self.registry.gateway_adapter(record["record_id"], anchor_verifier=self.anchor)
        ticket = build_entry_ticket(**{**self.args, "signal_registration_readback": receipt,
                                       "registration_verifier": verifier})
        self.assertEqual(ticket["status"], "PREPARED_NOT_SENT")
        self.assertFalse(ticket["transport_attempted"])

    def test_current_research_policy_future_input_and_metadata_tamper_are_rejected(self):
        self.args = case(current_snapshot=True)
        self.args["frozen_dataset"]["execution_cost_status"] = "DEFERRED_TO_EXECUTION_GATE"
        self.args["signal"] = evaluate_current_snapshot_signal(self.args["frozen_dataset"], as_of=self.decision)
        with self.assertRaises(RegistryDenied) as error:
            self.register()
        self.assertEqual(error.exception.code, "NONACTIONABLE_SIGNAL")
        self.args = case(current_snapshot=True)
        future = (self.decision + timedelta(seconds=1)).isoformat()
        self.args["frozen_dataset"]["bars"][0].update(retrieved_at=future, available_at=future)
        with self.assertRaises(RegistryDenied) as error:
            self.register()
        self.assertEqual(error.exception.code, "POSTDECISION_INPUT")
        self.args = case(current_snapshot=True)
        self.args["frozen_dataset"]["purpose"] = "FORGED_CURRENT_SCOPE"
        with self.assertRaises(RegistryDenied) as error:
            self.register()
        self.assertEqual(error.exception.code, "SIGNAL_REPLAY_MISMATCH")
        self.args = case(current_snapshot=True)
        self.args["signal"]["price_knowledge_at"] = future
        with self.assertRaises(RegistryDenied) as error:
            self.register()
        self.assertEqual(error.exception.code, "SIGNAL_REPLAY_MISMATCH")
        self.args = case(current_snapshot=True)
        self.args["signal"]["as_of"] = (self.decision - timedelta(days=1)).isoformat()
        with self.assertRaises(RegistryDenied) as error:
            self.register()
        self.assertEqual(error.exception.code, "LATE_SIGNAL_REGISTRATION")
        self.assertEqual(self.registry.verify_chain()["record_count"], 0)

    def test_0830_record_binds_signal_dataset_forward_decision_and_outcomes(self):
        result = self.register()
        self.assertEqual(result["status"], "LOCAL_CANDIDATE")
        self.assertFalse(result["broker_action_authorized"])
        self.assertEqual(self.registry.verify_chain()["record_count"], 1)
        self.clock.value = self.args["now"]
        receipt = self.registry.local_readback(result["record_id"])
        self.assertEqual(receipt["signal_sha256"], "sha256:" + canonical_hash(self.args["signal"]))
        self.assertEqual(receipt["frozen_dataset_sha256"],
                         "sha256:" + canonical_hash(self.args["frozen_dataset"]))
        self.assertEqual(receipt["parameters_sha256"], "sha256:" + canonical_hash(DEFAULT_CONFIG))
        self.assertEqual(receipt["forward_decision_sha256"],
                         "sha256:" + canonical_hash(forward_decision(self.args)))
        self.assertEqual([row["horizon_trading_days"] for row in receipt["outcome_contracts"]], [5, 20])
        self.assertEqual(receipt["outcome_contracts"][0]["session_date"],
                         self.args["exchange_calendar"]["sessions"][
                             self.args["exchange_calendar"]["sessions"].index(
                                 self.decision.date().isoformat()) + 5])
        args = {**self.args, "signal_registration_readback": receipt,
                "registration_verifier": lambda _: {}}
        with self.assertRaises(PaperDenied) as error:
            build_entry_ticket(**args)
        self.assertEqual(error.exception.code, "GATEWAY_MISSING_INDEPENDENT_SIGNAL_REGISTRATION")

    def test_attested_adapter_matches_gateway_readback_and_verifier(self):
        record = self.register()
        self.clock.value = self.args["now"]
        receipt, verifier = self.registry.gateway_adapter(record["record_id"],
                                                          anchor_verifier=self.anchor)
        self.assertEqual(receipt["registry_kind"], "EXTERNAL_APPEND_ONLY")
        self.assertEqual(verifier(receipt)["status"], "VERIFIED_APPEND_ONLY_INCLUSION")
        args = {**self.args, "signal_registration_readback": receipt,
                "registration_verifier": verifier}
        ticket = build_entry_ticket(**args)
        self.assertEqual(ticket["status"], "PREPARED_NOT_SENT")
        self.assertEqual(ticket["prior_signal_registration"]["record_id"], record["record_id"])

    def test_late_or_unattested_record_fails_closed(self):
        self.clock.value = self.decision + timedelta(minutes=1)
        with self.assertRaises(RegistryDenied) as error:
            self.register()
        self.assertEqual(error.exception.code, "LATE_SIGNAL_REGISTRATION")
        self.clock.value = self.decision + timedelta(seconds=20)
        record = self.register()
        self.clock.value = self.args["now"]
        with self.assertRaises(RegistryDenied) as error:
            self.registry.gateway_adapter(record["record_id"], anchor_verifier=None)
        self.assertEqual(error.exception.code, "EXTERNAL_ANCHOR_REQUIRED")

    def test_forward_decision_cannot_substitute_strategy_version_or_baseline(self):
        original = forward_decision(self.args)
        for field, replacement in (("strategy_version", "gold-au-strategy.v2"),
                                   ("baseline_id", "AU_BUY_HOLD")):
            changed = {**original, field: replacement}
            with self.subTest(field=field), self.assertRaises(RegistryDenied) as error:
                self.registry.register(signal=self.args["signal"],
                                       frozen_dataset=self.args["frozen_dataset"],
                                       forward_decision=changed,
                                       exchange_calendar=self.args["exchange_calendar"])
            self.assertEqual(error.exception.code, "FORWARD_DECISION_SIGNAL_MISMATCH")
        self.assertEqual(self.registry.verify_chain()["record_count"], 0)

    def test_late_anchor_wrong_hash_and_receipt_tampering_are_rejected(self):
        record = self.register()
        self.clock.value = self.args["now"]

        def late(candidate: dict) -> dict:
            return {**self.anchor(candidate), "anchor_received_at": self.args["now"].isoformat()}

        def wrong_hash(candidate: dict) -> dict:
            return {**self.anchor(candidate), "record_sha256": "sha256:" + "d" * 64}

        with self.assertRaises(RegistryDenied) as error:
            self.registry.gateway_adapter(record["record_id"], anchor_verifier=late)
        self.assertEqual(error.exception.code, "LATE_EXTERNAL_ANCHOR")
        with self.assertRaises(RegistryDenied) as error:
            self.registry.gateway_adapter(record["record_id"], anchor_verifier=wrong_hash)
        self.assertEqual(error.exception.code, "EXTERNAL_ANCHOR_NOT_VERIFIED")
        receipt, verifier = self.registry.gateway_adapter(record["record_id"],
                                                          anchor_verifier=self.anchor)
        altered = {**receipt, "recorded_at": self.decision.isoformat()}
        with self.assertRaises(RegistryDenied) as error:
            verifier(altered)
        self.assertEqual(error.exception.code, "REGISTRATION_READBACK_MISMATCH")

    def test_sql_tamper_breaks_readback_and_update_trigger_blocks_normal_mutation(self):
        record = self.register()
        with sqlite3.connect(self.path) as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE signal_records SET raw_sha256=? WHERE record_id=?",
                             ("sha256:" + "b" * 64, record["record_id"]))
            conn.execute("DROP TRIGGER signal_records_no_update")
            conn.execute("UPDATE signal_records SET raw_sha256=? WHERE record_id=?",
                         ("sha256:" + "b" * 64, record["record_id"]))
        with self.assertRaises(RegistryDenied) as error:
            self.registry.local_readback(record["record_id"])
        self.assertEqual(error.exception.code, "REGISTRY_RECORD_CORRUPT")

    def test_concurrent_registration_is_one_shot_even_with_identical_payload(self):
        other = LocalSignalRegistry(self.path, clock=self.clock)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.register, registry) for registry in (self.registry, other)]
        outcomes = []
        for future in futures:
            try:
                outcomes.append(future.result()["status"])
            except RegistryDenied as exc:
                outcomes.append(exc.code)
        self.assertCountEqual(outcomes, ["LOCAL_CANDIDATE", "DUPLICATE_DECISION_OR_SIGNAL"])
        self.assertEqual(self.registry.verify_chain()["record_count"], 1)

    def test_commit_crossing_0831_rolls_back(self):
        stamps = iter([self.decision + timedelta(seconds=58),
                       self.decision + timedelta(seconds=59),
                       self.decision + timedelta(minutes=1)])
        crossing = LocalSignalRegistry(self.path, clock=lambda: next(stamps))
        with self.assertRaises(RegistryDenied) as error:
            self.register(crossing)
        self.assertEqual(error.exception.code, "LATE_SIGNAL_REGISTRATION")
        self.assertEqual(self.registry.verify_chain()["record_count"], 0)


if __name__ == "__main__":
    unittest.main()
