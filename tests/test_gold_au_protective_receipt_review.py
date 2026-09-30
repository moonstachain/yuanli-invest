"""Independent adversarial protocol review; synthetic, no host/broker calls."""
import unittest
from dataclasses import replace
from tests import test_gold_au_receipt_client as fixture_module
from tests.test_gold_au_linked_protection import wired, opened
from tests.test_gold_simnow_strategy import GoldSimNowRuntime, run_once
from tests.test_gold_paper import KEY, NOW
from yuanli_invest.gold_paper import PaperDenied
from yuanli_invest.gold_au_receipt_client import ReceiptWriteAmbiguous, object_hash, ENVIRONMENT, NATIVE_HASH_FIELDS


class ProtectiveReceiptReviewTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_module.ReceiptClientTests()
        self.fixture.setUp()

    def tearDown(self):
        self.fixture.tearDown()

    def test_unknown_submit_ack_keeps_every_write_frozen_after_readback(self):
        client = self.fixture.client("runtime")
        calls = []
        def timeout(*args):
            calls.append(args)
            raise TimeoutError
        client._transport = timeout
        with self.assertRaises(ReceiptWriteAmbiguous):
            client.record_submit_attempt_v2(claim_id="parent-claim", expected_version=1,
                ledger_root_hash=fixture_module.ROOT, ledger_sequence=2)
        self.fixture.reply = self.fixture.coordinator(status="ACCOUNT_READ", claimed=False,
            version=2, phase="SUBMIT_ATTEMPTED", claim_id="parent-claim", pending_claim_id="parent-claim", ledger_sequence=2)
        client._transport = self.fixture.transport
        client.read_account_state_v2()
        self.assertTrue(client.write_frozen)
        with self.assertRaises(ReceiptWriteAmbiguous):
            client.claim_linked_exit_v3(command_id="child-command", contract_hash=fixture_module.ROOT,
                parent_claim_id="parent-claim", broker_evidence_id="native-proof", expected_version=2,
                ledger_root_hash=fixture_module.ROOT, ledger_sequence=3)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(self.fixture.calls), 1)  # Only the independent read.

    def test_linked_child_claim_must_bind_parent_and_one_existing_lot(self):
        for quantity, parent in ((0, "parent-claim"), (1, "wrong-parent")):
            self.fixture.reply = self.fixture.coordinator(position_quantity=quantity,
                position_origin_claim_id=parent)
            with self.subTest(quantity=quantity, parent=parent), self.assertRaises(ReceiptWriteAmbiguous):
                self.fixture.client("runtime").claim_linked_exit_v3(command_id="command-1", contract_hash=fixture_module.ROOT,
                    parent_claim_id="parent-claim", broker_evidence_id="native-proof", expected_version=0,
                    ledger_root_hash=fixture_module.ROOT, ledger_sequence=1)

    def test_paired_terminal_receipt_must_be_frozen_flat_and_unlocked(self):
        for overrides in ({"position_quantity": 1}, {"position_origin_claim_id": "parent-claim"},
                          {"phase": "HELD", "position_quantity": 1, "position_origin_claim_id": "parent-claim"}):
            values = dict(status="PAIR_RECORDED", claimed=False, phase="FROZEN", pending_claim_id=None,
                          position_quantity=0, position_origin_claim_id=None)
            values.update(overrides)
            self.fixture.reply = self.fixture.coordinator(**values)
            with self.subTest(overrides=overrides), self.assertRaises(ReceiptWriteAmbiguous):
                self.fixture.client("runtime").complete_linked_pair_v3(claim_id="claim-1", broker_evidence_id="pair-proof",
                    expected_version=0, ledger_root_hash=fixture_module.ROOT, ledger_sequence=1)

    def test_native_ingest_reply_cannot_change_requested_kind(self):
        facts = {"command_id": "command-1", "claim_id": "claim-1", "instrument": "au2612",
                 "action": "OPEN_LONG", "order_id": "order-1", "order_status": "FILLED",
                 "filled_quantity": 1, "position_quantity": 1, "pending_order_count": 0,
                 "parent_claim_id": None, "parent_order_id": None, "reconciliation": None,
                 **{field: fixture_module.ROOT for field in NATIVE_HASH_FIELDS}}
        self.fixture.reply = {"source": "bound_broker_reader_evidence_v3", "status": "EVIDENCE_RECORDED",
            "evidence_id": "native-proof", "environment": ENVIRONMENT, "account_id": "account-1", "robot_id": 479509,
            "source_sha256": fixture_module.SOURCE, "kind": "PAIRED_TERMINAL", "observed_at": fixture_module.NOW.isoformat(),
            "received_at": fixture_module.NOW.isoformat(), "verified_at": fixture_module.NOW.isoformat(),
            "facts_sha256": object_hash(facts), "facts": facts}
        with self.assertRaises(ReceiptWriteAmbiguous):
            self.fixture.client("broker_reader").ingest_native_evidence_v3(evidence_id="native-proof", kind="NATIVE_ORDER",
                observed_at=fixture_module.NOW.isoformat(), facts=facts)


class ProtectiveRestartReviewTests(unittest.TestCase):
    """Persisted offline fixtures, never evidence of real broker acceptance."""
    def restart(self, harness):
        harness.runtime = GoldSimNowRuntime(harness.bridge, harness.runtime.grant, KEY, clock=lambda: NOW)
        harness.runtime.recovery_readonly = True

    def test_restart_after_child_submission_never_sells_twice(self):
        h, c = wired(); opened(h)
        self.assertEqual(run_once(h.runtime, NOW)["status"], "SAFETY_EXIT_PENDING_READBACK")
        self.restart(h); h.truth = None
        for _ in range(3):
            self.assertEqual(run_once(h.runtime, NOW)["status"], "LINKED_SAFETY_CLOSE_READBACK_UNAVAILABLE")
        self.assertEqual(len(h.exchange.sell_calls), 1)
        self.assertEqual(len(c.link_requests), 1)

    def test_restart_after_unknown_child_claim_never_reclaims_or_sells(self):
        h, c = wired(); opened(h); c.link_fail = True
        with self.assertRaises(PaperDenied): run_once(h.runtime, NOW)
        self.restart(h)
        for _ in range(2):
            with self.assertRaises(PaperDenied): run_once(h.runtime, NOW)
        self.assertEqual(len(c.link_requests), 1)
        self.assertEqual(h.exchange.sell_calls, [])

    def test_unknown_sell_ack_requires_native_readback_and_never_second_sell(self):
        h, c = wired(); opened(h)
        def sell(price, quantity):
            h.exchange.sell_calls.append((h.exchange.direction, price, quantity))
            raise TimeoutError("synthetic unknown acknowledgement")
        h.exchange.Sell = sell
        self.assertEqual(run_once(h.runtime, NOW)["status"], "SAFETY_EXIT_UNCERTAIN_FROZEN")
        self.restart(h); h.native_available = False
        self.assertEqual(run_once(h.runtime, NOW)["status"], "UNCERTAIN_SUBMISSION_READONLY_LOCKED")
        h.native_available = True
        h.terminal_truth(order_id="O-CLOSE-1", position=0); h.exchange.positions = []
        self.assertEqual(run_once(h.runtime, NOW)["status"], "LINKED_SAFETY_CLOSE_CONFIRMED_MANUAL")
        self.assertEqual(run_once(h.runtime, NOW)["status"], "LINKED_PAIR_RECONCILED_ACCOUNT_FROZEN")
        self.assertEqual(len(h.exchange.sell_calls), 1)
        self.assertEqual(len(c.link_requests), 1)
        self.assertTrue(h.bridge.load_ledger().is_frozen())

    def test_expired_disabled_entry_grant_retains_exact_reducing_authority(self):
        h, c = wired(); opened(h)
        h.runtime.grant = replace(h.runtime.grant, enabled=False, expires_at="2026-09-29T08:00:00+08:00")
        self.assertEqual(run_once(h.runtime, NOW)["status"], "SAFETY_EXIT_PENDING_READBACK")
        self.assertEqual(len(h.exchange.buy_calls), 1)
        self.assertEqual(len(h.exchange.sell_calls), 1)


if __name__ == "__main__": unittest.main()
