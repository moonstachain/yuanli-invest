"""Independent R2/one-shot review using synthetic adapters; no CTP or deployment."""
from copy import deepcopy
from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest
from unittest import mock

from scripts import gold_au_engineering_bootstrap as engineering
from scripts.youquant_gold_simnow_strategy import run_once
from scripts.gold_au_runtime_bootstrap import ProductionGoldSimNowRuntime
from tests.test_gold_paper import KEY, NOW, grant, payload
from tests.test_gold_simnow_strategy import Harness
from yuanli_invest.gold_au_receipt_client import object_hash
from yuanli_invest.gold_paper import PaperDenied, PaperLedger, sign_command


def engineering_envelope(**changes):
    fields = dict(reason="ENGINEERING_TEST", decision_at=NOW.isoformat(),
        issued_at=NOW.isoformat(), not_before_at=NOW.isoformat(),
        expires_at=(NOW + timedelta(seconds=120)).isoformat(),
        exit_not_after_at=(NOW + timedelta(seconds=120)).isoformat(),
        roll_not_after_at=(NOW + timedelta(seconds=120)).isoformat(),
        stop_price="996.02")
    fields.update(changes)
    return sign_command(payload(**fields), KEY)


def preparation(body, **changes):
    value = {"source": "independent_gold2_engineering_preparation_v4", "status": "ENGINEERING_PREPARED",
        "observed_at": NOW.isoformat(), "signer_key_fingerprint": "sha256:" + "f" * 64,
        "command_id": body["command_id"], "contract_hash": body["contract_hash"],
        "account_id": body["account_id"], "robot_id": body["robot_id"],
        "environment": body["environment"], "instrument": body["contract"],
        "round_trip_fee_upper_cny": "80", "strategy_budget_cny": "12500",
        "exit_on_first_verified_fill": True, "counts_as_strategy_return_sample": False,
        "starts_formal_30_day_clock": False}
    value.update(changes)
    value["raw_sha256"] = object_hash(value)
    value["signature"] = "SYNTHETIC_PINNED_CONTROL_PROOF_NOT_REAL_SIGNATURE"
    return value


def synthetic_proof(value):
    return {"status": "SIGNATURE_VERIFIED_WITH_PINNED_KEY", "verified_receipt_sha256": value["raw_sha256"],
        "verified_signer_id": "GOLD2_INDEPENDENT_CONTROL_V4",
        "verified_signer_key_fingerprint": value["signer_key_fingerprint"]}


class EngineeringLimitsReview(unittest.TestCase):
    def validate(self, body=None, fee="80", budget="12500"):
        return engineering.validate_engineering_body(body or engineering_envelope()["payload"],
            fee_upper=fee, strategy_budget=budget)

    def test_r2_total_loss_includes_slippage_buffer_and_fee(self):
        self.validate(fee="800", budget="5000")
        for fee, budget in (("800.00000000001", "5000"), ("80", "4279.99"), ("-1", "12500"), ("NaN", "12500")):
            with self.subTest(fee=fee, budget=budget), self.assertRaises(PaperDenied):
                self.validate(fee=fee, budget=budget)

    def test_exact_one_lot_narrow_stop_and_quote_distance(self):
        for changes in ({"quantity": True}, {"quantity": 2}, {"reason": "ENTRY"},
            {"stop_price": "995.99"}, {"stop_price": "1000.02"}, {"reference_price": "999.91999999999"}):
            with self.subTest(changes=changes), self.assertRaises(PaperDenied):
                self.validate(engineering_envelope(**changes)["payload"])

    def test_deadline_is_positive_at_most_120_seconds_and_bounds_all_expiry(self):
        for changes in ({"exit_not_after_at": NOW.isoformat()},
            {"exit_not_after_at": (NOW+timedelta(seconds=121)).isoformat()},
            {"roll_not_after_at": (NOW+timedelta(seconds=121)).isoformat()},
            {"expires_at": (NOW+timedelta(seconds=121)).isoformat()}):
            with self.subTest(changes=changes), self.assertRaises(PaperDenied):
                self.validate(engineering_envelope(**changes)["payload"])

    def test_same_day_is_beijing_not_utc(self):
        for start, accepted in (("2026-09-29T23:59:30+08:00", False), ("2026-09-29T07:59:30+08:00", True)):
            decision = datetime.fromisoformat(start)
            end = (decision+timedelta(seconds=120)).isoformat()
            body = engineering_envelope(decision_at=start, exit_not_after_at=end, roll_not_after_at=end, expires_at=end)["payload"]
            if accepted:
                self.validate(body)
            else:
                with self.assertRaises(PaperDenied): self.validate(body)

    def test_preparation_is_exact_fresh_pinned_and_never_formal_performance(self):
        body = engineering_envelope()["payload"]
        self.assertEqual(engineering.verified_preparation(preparation(body), synthetic_proof, body, NOW)["command_id"], body["command_id"])
        for changes in ({"command_id": "OTHER"}, {"contract_hash": "sha256:"+"1"*64},
            {"account_id": "OTHER"}, {"robot_id": 9}, {"instrument": "au2702"},
            {"counts_as_strategy_return_sample": True}, {"starts_formal_30_day_clock": True},
            {"exit_on_first_verified_fill": False}, {"observed_at": (NOW-timedelta(seconds=16)).isoformat()},
            {"observed_at": (NOW+timedelta(seconds=1)).isoformat()}):
            with self.subTest(changes=changes), self.assertRaises(PaperDenied):
                engineering.verified_preparation(preparation(body, **changes), synthetic_proof, body, NOW)
        with self.assertRaises(PaperDenied):
            engineering.verified_preparation(preparation(body), lambda value: {"status": "CALLER_ASSERTED"}, body, NOW)


class EngineeringRuntimeReview(unittest.TestCase):
    def assembled(self):
        h = Harness(); h.exchange.quote.update(Buy=1000.0, Last=1000.0)
        envelope = engineering_envelope(); body = envelope["payload"]
        g = grant(engineering_test_command_id=body["command_id"])
        runtime = engineering.EngineeringGoldSimNowRuntime(h.bridge, g, KEY,
            body=body, preparation=preparation(body), clock=lambda: h.now)
        return h, runtime, envelope

    def test_exact_engineering_contract_does_not_open_an_alternate_entry_route(self):
        h, runtime, envelope = self.assembled()
        with self.assertRaisesRegex(PaperDenied, "ENGINEERING_CONTRACT_MISMATCH"):
            runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(h.exchange.buy_calls, [])
        formal = ProductionGoldSimNowRuntime(h.bridge, runtime.grant, KEY, clock=lambda: NOW)
        with self.assertRaisesRegex(PaperDenied, "LINKED_PROTECTIVE_EXIT_REAL_ACCEPTANCE_REQUIRED"):
            formal.process_command(envelope, NOW)
        self.assertEqual(h.exchange.buy_calls, [])

    def test_any_previous_close_attempt_consumes_engineering_close_even_after_restart(self):
        h, runtime, envelope = self.assembled()
        ledger = PaperLedger(); ledger.append("OrderSubmitAttempted", "SYNTHETIC-CLOSE", NOW.isoformat(), {"action": "CLOSE_LONG"})
        h.bridge.save_ledger(ledger)
        self.assertEqual(runtime.process_due_safety_exit(NOW)["status"], "ENGINEERING_CLOSE_CONSUMED_READBACK_ONLY")
        restarted = engineering.EngineeringGoldSimNowRuntime(h.bridge, runtime.grant, KEY,
            body=envelope["payload"], preparation=preparation(envelope["payload"]), clock=lambda: h.now)
        self.assertEqual(restarted.process_due_safety_exit(NOW)["status"], "ENGINEERING_CLOSE_CONSUMED_READBACK_ONLY")
        self.assertEqual(h.exchange.sell_calls, [])

    def test_first_verified_fill_immediately_sets_reduction_deadline(self):
        h, runtime, envelope = self.assembled()
        context = {"origin_command_id": envelope["payload"]["command_id"],
            "exit_not_after_at": envelope["payload"]["exit_not_after_at"]}
        with mock.patch.object(engineering.GoldSimNowRuntime, "current_position_context", return_value=context):
            self.assertEqual(datetime.fromisoformat(runtime.current_position_context()["exit_not_after_at"]), NOW)
        with mock.patch.object(engineering.GoldSimNowRuntime, "current_position_context", return_value={**context, "origin_command_id": "FOREIGN"}):
            with self.assertRaisesRegex(PaperDenied, "ENGINEERING_FOREIGN_POSITION"): runtime.current_position_context()

    def test_real_runtime_first_fill_closes_once_and_rejection_remains_frozen(self):
        h, runtime, envelope = self.assembled()
        runtime.process_command(envelope, NOW)
        h.terminal_truth(); h.reconciled = False; h.risk_available = False
        h.exchange.positions = [{"ContractType": "au2612", "Type": 1, "Amount": 1, "Margin": 200000}]
        result = run_once(runtime, NOW)
        self.assertEqual(result["status"], "SAFETY_EXIT_PENDING_READBACK")
        self.assertEqual(result["reason"], "EXIT_ROLL")  # existing 15-minute lead makes 120s roll immediately due
        self.assertEqual(len(h.exchange.buy_calls), 1)
        self.assertEqual(len(h.exchange.sell_calls), 1)
        h.terminal_truth(order_id="O-CLOSE-1", status="REJECTED", position=1)
        self.assertEqual(run_once(runtime, NOW)["status"], "LINKED_SAFETY_CLOSE_FAILED_MANUAL")
        self.assertTrue(h.bridge.load_ledger().is_frozen())
        self.assertEqual(runtime.process_due_safety_exit(NOW)["status"], "ENGINEERING_CLOSE_CONSUMED_READBACK_ONLY")
        self.assertEqual(len(h.exchange.sell_calls), 1)

    def test_fresh_quote_drift_before_claim_or_buy_prevents_submission(self):
        for last in (999.89, 1000.11):
            h, runtime, envelope = self.assembled(); h.exchange.quote["Last"] = last
            with self.subTest(last=last), self.assertRaisesRegex(PaperDenied, "ENGINEERING_FRESH_QUOTE_PRICE_DRIFT"):
                runtime.process_command(envelope, NOW)
            self.assertEqual(h.exchange.buy_calls, [])

        h, runtime, envelope = self.assembled()
        with mock.patch.object(h.bridge, "claim_order", wraps=h.bridge.claim_order) as claimed:
            original = runtime.validate_additional_open_risk
            calls = []
            def race_guard(body, provider, now):
                calls.append(1)
                if len(calls) == 3: h.exchange.quote["Last"] = 1000.11
                return original(body, provider, now)
            with mock.patch.object(runtime, "validate_additional_open_risk", side_effect=race_guard):
                result = runtime.process_command(envelope, NOW)
                self.assertEqual(result["status"], "NOT_SUBMITTED_FROZEN")
                self.assertEqual(result["reason"], "ENGINEERING_FRESH_QUOTE_PRICE_DRIFT")
            self.assertGreaterEqual(len(calls), 3)
            self.assertEqual(h.exchange.buy_calls, [])

    def test_unknown_close_response_is_consumed_and_never_replayed(self):
        h, runtime, envelope = self.assembled()
        runtime.process_command(envelope, NOW)
        h.terminal_truth()
        h.exchange.positions = [{"ContractType": "au2612", "Type": 1, "Amount": 1, "Margin": 200000}]
        def lost_ack(price, quantity):
            h.exchange.sell_calls.append((h.exchange.direction, price, quantity))
            raise RuntimeError("synthetic Sell ACK lost")
        h.exchange.Sell = lost_ack
        result = run_once(runtime, NOW)
        self.assertEqual(result["status"], "SAFETY_EXIT_UNCERTAIN_FROZEN")
        self.assertTrue(h.bridge.load_ledger().is_frozen())
        for _ in range(3):
            self.assertEqual(runtime.process_due_safety_exit(NOW)["status"], "ENGINEERING_CLOSE_CONSUMED_READBACK_ONLY")
        self.assertEqual(len(h.exchange.sell_calls), 1)
    def test_factory_calls_production_checks_and_preserves_restart_readonly_state(self):
        h, runtime, envelope = self.assembled()
        checked = SimpleNamespace(bridge=h.bridge, recovery_readonly=True)
        with mock.patch.object(engineering, "build_runtime", return_value=checked) as factory:
            result = engineering.build_engineering_runtime(engineering_envelope=envelope,
                preparation_receipt=preparation(envelope["payload"]), preparation_verifier=synthetic_proof,
                signing_key=KEY, grant=runtime.grant, clock=lambda: NOW)
        factory.assert_called_once()
        self.assertTrue(result.recovery_readonly)

    def test_expired_empty_queue_halts_without_permanent_idle_loop(self):
        h, runtime, envelope = self.assembled(); h.now = NOW+timedelta(seconds=121)
        sleep = mock.Mock(side_effect=AssertionError("expired engineering case must not idle forever"))
        with mock.patch.object(engineering, "run_once", return_value={"status": "NO_COMMAND"}):
            engineering.serve_engineering(runtime, sleep, mock.Mock())
        sleep.assert_not_called()

    def test_consumed_close_and_unknown_status_halt_without_sleep_or_retry(self):
        for status in ("ENGINEERING_CLOSE_CONSUMED_READBACK_ONLY", "SAFETY_EXIT_UNCERTAIN_FROZEN", "PENDING_MANUAL_BROKER_RECONCILIATION"):
            h, runtime, envelope = self.assembled(); sleep = mock.Mock()
            with mock.patch.object(engineering, "run_once", return_value={"status": status}):
                engineering.serve_engineering(runtime, sleep, mock.Mock())
            sleep.assert_not_called()


if __name__ == "__main__": unittest.main()
