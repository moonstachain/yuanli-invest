from copy import deepcopy
from datetime import timedelta
import unittest

from yuanli_invest.gold_au_account_coordinator import AccountCoordinator
from yuanli_invest.gold_paper import PaperDenied, sign_command
from tests.test_gold_paper import KEY, NOW, payload
from tests.test_gold_simnow_strategy import Harness


class ReceiptFixture:
    """Protocol fixture only; remote PostgreSQL is separately verified."""
    account_id = "SIMNOW-TEST-ACCOUNT"
    robot_id = 12345
    source_sha256 = "sha256:" + "a" * 64

    def __init__(self):
        self.state = {"version": 0, "phase": "FLAT", "pending_claim_id": None,
                      "position_origin_claim_id": None, "position_quantity": 0, "command_id": None}
        self.claims = set()
        self.fail_submit = False
        self.fail_claim = False
        self.claim_requests = []
        self.submit_requests = []

    def read_account_state_v2(self):
        return deepcopy(self.state)

    def claim_order_v2(self, **request):
        self.claim_requests.append(request)
        if request["command_id"] in self.claims:
            return {**self.state, "claimed": False}
        self.claims.add(request["command_id"])
        self.state.update(version=self.state["version"] + 1, phase="CLAIMED", pending_claim_id="CLM-FIXTURE-1",
                          command_id=request["command_id"])
        if self.fail_claim:
            raise TimeoutError("request may have committed")
        return {**self.state, "claimed": True}

    def record_submit_attempt_v2(self, **request):
        self.submit_requests.append(request)
        self.state.update(version=self.state["version"] + 1, phase="SUBMIT_ATTEMPTED")
        if self.fail_submit:
            raise TimeoutError("request may have committed")
        return deepcopy(self.state)

    def record_terminal_v2(self, **request):
        self.state.update(version=self.state["version"] + 1, phase="HELD", pending_claim_id=None,
                          position_quantity=1, position_origin_claim_id="CLM-FIXTURE-1")
        return deepcopy(self.state)

    def read_ledger(self, **request):
        return request


def evidence(**request):
    return {"source": "bound_broker_reader_evidence_v2", "status": "EVIDENCE_RECORDED",
            "evidence_id": "EVD-FIXTURE-" + request["kind"]}


def wired(client=None):
    harness = Harness()
    client = client or ReceiptFixture()
    harness.bridge.account_coordinator = AccountCoordinator(client, evidence, harness.bridge.save_ledger)
    harness.bridge.atomic_claim = None
    return harness, client


class CoordinatorIntegrationTests(unittest.TestCase):
    def test_real_read_collection_longer_than_fifteen_seconds_denies_even_with_fresh_account(self):
        harness, _ = wired()
        clocks = iter((NOW, NOW + timedelta(seconds=16), NOW + timedelta(seconds=16)))
        harness.bridge.receipt_validation_clock = lambda: next(clocks)
        with self.assertRaisesRegex(PaperDenied, "COLLECTION_STALE"):
            harness.bridge.snapshot("au2612", NOW)
        self.assertEqual(harness.exchange.buy_calls, [])

    def test_tick_arriving_during_read_uses_read_completion_clock(self):
        harness, _ = wired()
        harness.exchange.quote["Time"] = int((NOW + timedelta(milliseconds=5)).timestamp() * 1000)
        harness.bridge.receipt_validation_clock = lambda: NOW + timedelta(milliseconds=10)
        quote = harness.bridge.quote("au2612", NOW)
        self.assertGreater(quote["bid"], 0)

    def test_production_subledger_rejects_the_legacy_full_broker_balance_mark(self):
        harness, _ = wired()
        harness.bridge.required_equity_scope = "SEGREGATED_GOLD2_PAPER_SUBLEDGER_V1"
        with self.assertRaisesRegex(PaperDenied, "PRODUCTION_STRATEGY_SUBLEDGER_REQUIRED"):
            harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(harness.exchange.buy_calls, [])

    def test_order_api_follows_both_anchored_remote_transitions(self):
        harness, client = wired()
        result = harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(result["status"], "SUBMITTED_PENDING_READBACK")
        self.assertEqual(len(harness.exchange.buy_calls), 1)
        events = harness.bridge.load_ledger().events
        requested = next(e for e in events if e["kind"] == "OrderClaimRequested")
        attempted = next(e for e in events if e["kind"] == "OrderSubmitAttempted")
        self.assertEqual(client.claim_requests[0]["ledger_root_hash"], requested["event_hash"])
        self.assertEqual(client.submit_requests[0]["ledger_root_hash"], attempted["event_hash"])
        self.assertEqual(attempted["data"]["claim_id"], "CLM-FIXTURE-1")
        self.assertEqual(attempted["data"]["source_sha256"], client.source_sha256)

    def test_uncertain_claim_never_calls_buy_and_second_host_cannot_take_account(self):
        first, client = wired()
        client.fail_claim = True
        with self.assertRaisesRegex(PaperDenied, "CLAIM_UNCERTAIN_NO_SUBMIT"):
            first.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(first.exchange.buy_calls, [])
        second, _ = wired(client)
        other = payload(); other["command_id"] = "CMD-OTHER-HOST-0001"
        with self.assertRaisesRegex(PaperDenied, "PENDING_OR_FROZEN"):
            second.runtime.process_command(sign_command(other, KEY), NOW)
        self.assertEqual(second.exchange.buy_calls, [])
        self.assertEqual(len(client.claim_requests), 1)

    def test_uncertain_submit_receipt_is_durable_and_cannot_call_broker(self):
        harness, client = wired()
        client.fail_submit = True
        with self.assertRaisesRegex(PaperDenied, "SUBMIT_RECEIPT_UNCERTAIN_NO_SUBMIT"):
            harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(harness.exchange.buy_calls, [])
        self.assertTrue(harness.bridge.load_ledger().is_frozen())
        self.assertEqual(client.state["phase"], "SUBMIT_ATTEMPTED")

    def test_restart_pending_supports_explicit_readonly_mode(self):
        harness, client = wired()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        coordinator = harness.bridge.account_coordinator
        with self.assertRaisesRegex(PaperDenied, "READONLY_RECOVERY"):
            coordinator.verify_restart(harness.bridge.load_ledger())
        result = coordinator.verify_restart(harness.bridge.load_ledger(), require_idle=False)
        self.assertEqual(result["status"], "RESTART_VERIFIED_READONLY_RECOVERY")
        self.assertEqual(len(harness.exchange.buy_calls), 1)

    def test_terminal_release_requires_independent_evidence_and_last_anchor(self):
        harness, client = wired()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        ledger = harness.bridge.load_ledger()
        harness.bridge.account_coordinator.terminal(payload(), ledger, NOW)
        self.assertEqual(ledger.events[-1]["kind"], "OrderTerminalReconciled")
        self.assertEqual(client.state["phase"], "HELD")

    def test_forged_matched_label_is_not_a_broker_evidence_receipt(self):
        harness, _ = wired()
        harness.bridge.account_coordinator.broker_evidence_reader = lambda **kw: {"status": "MATCHED", "evidence_id": "pretend"}
        with self.assertRaisesRegex(PaperDenied, "EVIDENCE_NOT_ACCEPTED"):
            harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(harness.exchange.buy_calls, [])
