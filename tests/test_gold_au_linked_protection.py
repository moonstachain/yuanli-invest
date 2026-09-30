"""Offline native/receipt fixtures; none of these tests claim SimNow acceptance."""
from copy import deepcopy
import unittest
from yuanli_invest.gold_au_account_coordinator import AccountCoordinator
from yuanli_invest.gold_au_receipt_client import object_hash, validate_native_facts, ReceiptDenied
from yuanli_invest.gold_paper import PaperDenied, SIMNOW_FIRST, sign_command
from tests.test_gold_au_account_coordinator import ReceiptFixture, evidence
from tests.test_gold_paper import KEY, NOW, payload
from tests.test_gold_simnow_strategy import Harness, run_once

H = "sha256:" + "f" * 64


def native_facts(body, claim_id, *, order_id="O-OPEN-1", action=None, position=1, status="FILLED"):
    return {"command_id": body["command_id"], "claim_id": claim_id, "instrument": body["contract"],
            "action": action or body["action"], "order_id": order_id, "order_status": status,
            "filled_quantity": 1 if status == "FILLED" else 0, "position_quantity": position,
            "pending_order_count": 1 if status == "PENDING" else 0,
            "parent_claim_id": None, "parent_order_id": None, "reconciliation": None,
            **{k: H for k in ("order_binding_sha256", "raw_identity_sha256", "raw_account_sha256",
                             "raw_orders_sha256", "raw_trades_sha256", "raw_positions_sha256")}}


def pair_facts(body, claim_id, parent_id="CLM-FIXTURE-1"):
    f = native_facts(body, claim_id, order_id="O-CLOSE-1", position=0)
    f.update(parent_claim_id=parent_id, parent_order_id="O-OPEN-1")
    f["reconciliation"] = {p: {"producer_id": "PRODUCER-" + p, "proof_sha256": H,
        "cash_cents": 500000000, "available_cents": 500000000, "frozen_margin_cents": 0,
        "position_quantity": 0, "open_filled_quantity": 1, "close_filled_quantity": 1,
        "parent_order_id": "O-OPEN-1", "child_order_id": "O-CLOSE-1"}
        for p in ("broker", "execution", "ledger", "expected")}
    return f


class V3Fixture(ReceiptFixture):
    write_frozen = False
    def __init__(self):
        super().__init__(); self.link_requests = []; self.pair_requests = []; self.link_fail = False
    def claim_linked_exit_v3(self, **request):
        self.link_requests.append(request)
        if self.link_fail:
            self.state.update(command_id=request["command_id"], pending_claim_id="CLM-CHILD",
                phase="CLAIMED", position_quantity=1, position_origin_claim_id="CLM-FIXTURE-1")
            raise TimeoutError("ack unknown")
        self.state.update(version=self.state["version"] + 1, command_id=request["command_id"],
            pending_claim_id="CLM-CHILD", phase="CLAIMED", position_quantity=1,
            position_origin_claim_id="CLM-FIXTURE-1", freeze_reason="LINKED_EXIT_PAIR_RECONCILIATION_REQUIRED")
        return {**deepcopy(self.state), "claimed": True}
    def complete_linked_pair_v3(self, **request):
        self.pair_requests.append(request)
        self.state.update(version=self.state["version"] + 1, phase="FROZEN", pending_claim_id=None,
            position_quantity=0, position_origin_claim_id=None, freeze_reason="LINKED_EXIT_PAIR_RECONCILED_REVIEW_REQUIRED")
        return deepcopy(self.state)


def wired():
    h = Harness(); c = V3Fixture(); h.native_mutator = None; h.native_available = True; h.pair_available = True
    def reader(**request):
        if request["kind"] in {"PRE_CLAIM", "TERMINAL"}:
            return evidence(**request)
        if not h.native_available or request["kind"] == "PAIRED_TERMINAL" and not h.pair_available:
            raise RuntimeError("independent source unavailable")
        body = request["body"]
        if request["kind"] == "PAIRED_TERMINAL":
            facts = pair_facts(body, request["claim_id"])
        else:
            truth = h.truth or {}
            facts = native_facts(body, request["claim_id"], order_id=truth.get("order_id", "O-OPEN-1"),
                                 status=truth.get("order_status", "FILLED"), position=truth.get("position_quantity", 1))
        if h.native_mutator:
            h.native_mutator(facts)
        return {"source": "bound_broker_reader_evidence_v3", "status": "EVIDENCE_READ",
            "environment": SIMNOW_FIRST, "account_id": c.account_id, "robot_id": c.robot_id,
            "kind": request["kind"], "evidence_id": "EV-NATIVE-" + request["kind"],
            "facts": facts, "facts_sha256": object_hash(facts), "observed_at": NOW.isoformat(),
            "received_at": NOW.isoformat(), "verified_at": NOW.isoformat()}
    h.bridge.account_coordinator = AccountCoordinator(c, reader, h.bridge.save_ledger)
    h.bridge.atomic_claim = None
    return h, c


def opened(h):
    h.runtime.process_command(sign_command(payload(), KEY), NOW)
    h.terminal_truth()
    h.exchange.positions = [{"ContractType": "au2612", "Type": 1, "Amount": 1, "Margin": 200000}]


class LinkedProtectionTests(unittest.TestCase):
    def test_native_filled_parent_missing_fourway_can_claim_one_reduction(self):
        h, c = wired(); opened(h)
        self.assertEqual(run_once(h.runtime, NOW)["status"], "SAFETY_EXIT_PENDING_READBACK")
        self.assertEqual(len(h.exchange.buy_calls), 1); self.assertEqual(len(h.exchange.sell_calls), 1)
        self.assertEqual(c.state["position_origin_claim_id"], "CLM-FIXTURE-1")
        self.assertEqual(c.state["pending_claim_id"], "CLM-CHILD")
        self.assertEqual(len(h.bridge.load_ledger().unresolved_submissions()), 2)
        h.truth = None
        self.assertEqual(run_once(h.runtime, NOW)["status"], "LINKED_SAFETY_CLOSE_READBACK_UNAVAILABLE")
        self.assertEqual(len(h.exchange.sell_calls), 1)

    def test_unavailable_reader_and_wrong_parent_fill_never_sell(self):
        for mutation in (lambda f: f.update(position_quantity=0), lambda f: f.update(order_id="OTHER-ORDER"),
                         lambda f: f.update(order_status="PENDING", filled_quantity=0, pending_order_count=1)):
            h, c = wired(); opened(h); h.native_mutator = mutation
            with self.assertRaises(PaperDenied): run_once(h.runtime, NOW)
            self.assertEqual(h.exchange.sell_calls, [])
        h, c = wired(); opened(h); h.native_available = False
        with self.assertRaisesRegex(PaperDenied, "EVIDENCE_UNAVAILABLE"): run_once(h.runtime, NOW)
        self.assertEqual(h.exchange.sell_calls, [])

    def test_unknown_child_claim_ack_never_calls_sell_or_reclaims(self):
        h, c = wired(); opened(h); c.link_fail = True
        with self.assertRaisesRegex(PaperDenied, "CLAIM_UNCERTAIN_NO_SUBMIT"): run_once(h.runtime, NOW)
        self.assertEqual(h.exchange.sell_calls, [])
        with self.assertRaises(PaperDenied): run_once(h.runtime, NOW)
        self.assertEqual(len(c.link_requests), 1)

    def test_child_rejected_or_canceled_never_automatically_retries(self):
        for status in ("REJECTED", "CANCELED"):
            h, c = wired(); opened(h); run_once(h.runtime, NOW)
            h.terminal_truth(order_id="O-CLOSE-1", status=status, position=1)
            self.assertEqual(run_once(h.runtime, NOW)["status"], "LINKED_SAFETY_CLOSE_FAILED_MANUAL")
            self.assertEqual(run_once(h.runtime, NOW)["status"], "LINKED_SAFETY_CLOSE_FAILED_MANUAL")
            self.assertEqual(c.state["pending_claim_id"], "CLM-CHILD")
            self.assertEqual(len(h.exchange.sell_calls), 1)

    def test_flat_native_close_does_not_substitute_for_paired_fourway(self):
        h, c = wired(); opened(h); run_once(h.runtime, NOW)
        h.terminal_truth(order_id="O-CLOSE-1", position=0); h.exchange.positions = []; h.pair_available = False
        self.assertEqual(run_once(h.runtime, NOW)["status"], "LINKED_SAFETY_CLOSE_CONFIRMED_MANUAL")
        self.assertEqual(run_once(h.runtime, NOW)["status"], "LINKED_SAFETY_CLOSE_FLAT_PAIR_PENDING")
        self.assertEqual(c.state["pending_claim_id"], "CLM-CHILD")
        self.assertEqual(c.pair_requests, [])

    def test_true_paired_fourway_consumes_both_pending_but_keeps_book_frozen(self):
        h, c = wired(); opened(h); run_once(h.runtime, NOW)
        h.terminal_truth(order_id="O-CLOSE-1", position=0); h.exchange.positions = []
        run_once(h.runtime, NOW)
        self.assertEqual(run_once(h.runtime, NOW)["status"], "LINKED_PAIR_RECONCILED_ACCOUNT_FROZEN")
        self.assertEqual(c.state["phase"], "FROZEN"); self.assertIsNone(c.state["pending_claim_id"])
        self.assertEqual(h.bridge.load_ledger().unresolved_submissions(), set())
        self.assertTrue(h.bridge.load_ledger().is_frozen())
        with self.assertRaises(PaperDenied):
            h.runtime.process_command(sign_command(payload(command_id="CMD-NEW-OPEN"), KEY), NOW)
        self.assertEqual(len(h.exchange.buy_calls), 1)

    def test_pair_requires_four_distinct_producers_and_matching_cash(self):
        for mutation in (lambda f: f["reconciliation"]["broker"].update(cash_cents=1),
                         lambda f: f["reconciliation"]["broker"].update(producer_id="PRODUCER-ledger")):
            h, c = wired(); opened(h); run_once(h.runtime, NOW)
            h.terminal_truth(order_id="O-CLOSE-1", position=0); h.exchange.positions = []
            run_once(h.runtime, NOW); h.native_mutator = mutation
            self.assertEqual(run_once(h.runtime, NOW)["status"], "LINKED_SAFETY_CLOSE_FLAT_PAIR_PENDING")
            self.assertEqual(c.pair_requests, [])

    def test_order_api_unknown_result_reads_exact_native_binding_without_retry(self):
        h, c = wired(); h.exchange.fail_buy = True
        self.assertEqual(h.runtime.process_command(sign_command(payload(), KEY), NOW)["status"], "SUBMIT_UNCERTAIN_FROZEN")
        h.terminal_truth(); h.exchange.positions = [{"ContractType": "au2612", "Type": 1, "Amount": 1, "Margin": 200000}]
        self.assertEqual(run_once(h.runtime, NOW)["status"], "SAFETY_EXIT_PENDING_READBACK")
        self.assertEqual(len(h.exchange.buy_calls), 1); self.assertEqual(len(h.exchange.sell_calls), 1)
        recovered = [e for e in h.bridge.load_ledger().events if e["kind"] == "OrderSubmitted" and e["data"].get("recovered_readonly")]
        self.assertEqual(len(recovered), 1)

    def test_frozen_receipt_client_observes_native_id_without_any_write_or_unfreeze(self):
        h, c = wired(); h.exchange.fail_buy = True
        h.runtime.process_command(sign_command(payload(), KEY), NOW); h.terminal_truth(); c.write_frozen = True
        count = len(h.bridge.load_ledger().events)
        result = run_once(h.runtime, NOW)
        self.assertEqual(result["status"], "UNCERTAIN_ORDER_ID_OBSERVED_CLIENT_WRITE_FROZEN")
        self.assertEqual(len(h.bridge.load_ledger().events), count); self.assertTrue(c.write_frozen)
        self.assertEqual(h.exchange.sell_calls, [])

    def test_recovered_native_fact_bool_and_unknown_status_are_denied(self):
        for mutation in (lambda f: f.update(filled_quantity=True), lambda f: f.update(order_status="UNKNOWN")):
            h, c = wired(); h.exchange.fail_buy = True
            h.runtime.process_command(sign_command(payload(), KEY), NOW); h.terminal_truth(); h.native_mutator = mutation
            self.assertEqual(run_once(h.runtime, NOW)["status"], "UNCERTAIN_SUBMISSION_READONLY_LOCKED")
            self.assertEqual(len(h.exchange.buy_calls), 1); self.assertEqual(h.exchange.sell_calls, [])

if __name__ == "__main__": unittest.main()
