import sys
import unittest
from copy import deepcopy
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from yuanli_invest.gold_paper import PaperDenied, PaperLedger, SIMNOW_FIRST, sign_command  # noqa: E402
from tests.test_gold_paper import KEY, NOW, equity_mark, grant, payload  # noqa: E402
from youquant_gold_simnow_strategy import GoldSimNowRuntime, YouQuantBridge, run_once  # noqa: E402


def api_receipt(method, response, observed_at=NOW):
    canonical = json.dumps(response, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False).encode("utf-8")
    return {"method": method, "observed_at": observed_at.isoformat(),
            "response": response,
            "response_sha256": "sha256:" + hashlib.sha256(canonical).hexdigest()}


class FakeExchange:
    def __init__(self):
        self.account = {
            "Info": {"BrokerID": "9999", "InvestorID": "SIMNOW-TEST-ACCOUNT"},
            "Balance": 4000000,
            "Equity": 5000000,
        }
        self.positions = []
        self.orders = []
        self.direction = None
        self.buy_calls = []
        self.sell_calls = []
        self.cancel_calls = []
        self.fail_buy = False
        self.quote = {"Buy": 989.80, "Last": 989.90, "Time": int(NOW.timestamp() * 1000)}

    def IO(self, name):
        return name == "status"

    def SetContractType(self, contract):
        return {
            "InstrumentID": contract,
            "ExchangeID": "SHFE",
            "VolumeMultiple": 1000,
            "PriceTick": 0.02,
            "DeliveryYear": 2026,
            "DeliveryMonth": 12,
            "IsTrading": 1,
        }

    def GetAccount(self):
        return self.account

    def GetPositions(self):
        return self.positions

    def GetOrders(self):
        return self.orders

    def GetTicker(self):
        return self.quote

    def SetDirection(self, direction):
        self.direction = direction

    def Buy(self, price, qty):
        self.buy_calls.append((self.direction, price, qty))
        if self.fail_buy:
            raise TimeoutError("unknown whether broker received order")
        return "O-OPEN-1"

    def Sell(self, price, qty):
        self.sell_calls.append((self.direction, price, qty))
        return "O-CLOSE-1"

    def CancelOrder(self, order_id):
        self.cancel_calls.append(order_id)
        return True


class Harness:
    def __init__(self, *, attested=True, persisted=True, terminal=True, anchored=True, claims=None):
        self.exchange = FakeExchange()
        self.now = NOW
        self.kv = {}
        self.command = None
        self.attested = attested
        self.persisted = persisted
        self.anchored = anchored
        self.terminal = terminal
        self.truth = None
        self.anchored_events = []
        self.claims = claims if claims is not None else set()
        self.trend_break = False
        self.risk_available = True
        self.reconciled = True
        self.attestation_mutator = None
        self.bridge = YouQuantBridge(
            exchange=self.exchange,
            get_command=lambda: self.command,
            kv_get=lambda key: self.kv.get(key),
            kv_set=self.write,
            robot_id_get=lambda: 12345,
            account_attestation=self.attestation,
            current_margin=self.margin,
            current_round_trip_fee_upper=self.fees,
            reconciliation_probe=lambda: self.reconciled,
            ledger_anchor=self.anchor if anchored else None,
            atomic_claim=self.claim,
            strategy_equity_mark=lambda: equity_mark(broker_equity=str(self.exchange.account["Equity"]),
                                                    equity=str(self.exchange.account["Equity"])),
            daily_close_history=self.trend_history,
            pd_long_today=1,
            pd_long_yesterday=2,
            terminal_truth=(lambda order_id: self.truth) if terminal else None,
        )
        self.runtime = GoldSimNowRuntime(self.bridge, grant(), KEY, clock=lambda: self.now)

    def claim(self, command_id, contract_hash, account_id, at):
        if command_id in self.claims:
            return {"source": "external_atomic_command_claim", "claimed": False}
        self.claims.add(command_id)
        return {"source": "external_atomic_command_claim", "claimed": True,
                "command_id": command_id, "contract_hash": contract_hash,
                "account_id": account_id, "environment": SIMNOW_FIRST}

    def margin(self, contract):
        if not self.risk_available:
            raise RuntimeError("margin source unavailable")
        return 200000

    def fees(self, contract):
        if not self.risk_available:
            raise RuntimeError("fee source unavailable")
        return 80

    def trend_history(self, contract, now):
        days = []
        day = now.date() - timedelta(days=1)
        while len(days) < 15:
            if day.weekday() < 5:
                days.append(day)
            day -= timedelta(days=1)
        return {"source": "independent_shfe_dated_daily_close_readback",
                "contract": contract, "verified_session_calendar": True,
                "observed_at": now.isoformat(),
                "next_session_date": now.date().isoformat(),
                "last_completed_session_date": days[0].isoformat(),
                "bars": [{"date": day.isoformat(), "close": "900" if self.trend_break and day == days[0] else "1000",
                          "raw_sha256": "sha256:" + "f" * 64} for day in reversed(days)]}

    def write(self, key, value):
        if self.persisted:
            self.kv[key] = value

    def anchor(self, events, root_hash):
        PaperLedger(events).verify_chain()
        if events[:len(self.anchored_events)] != self.anchored_events:
            return {"source": "external_append_only_ledger", "accepted": False, "root_hash": root_hash}
        self.anchored_events = deepcopy(events)
        return {"source": "external_append_only_ledger", "accepted": True, "root_hash": root_hash}

    def attestation(self):
        if not self.attested:
            return None
        platform_response = {"code": 0, "data": {"result": {"all": 1, "platforms": [{
            "id": 24680, "eid": "Futures_CTP",
            "profiles": {"BrokerId": "9999",
                         "TDFront": "tcp://182.254.243.31:30001",
                         "MDFront": "tcp://182.254.243.31:30011"},
        }]}, "error": None}}
        robot_response = {"code": 0, "data": {"result": {"robot": {
            "id": 12345, "status": 1,
            "strategy_exchange_pairs": '[60,[24680],["FUTURES"]]',
        }}, "error": None}}
        result = {
            "source": "youquant_account_and_robot_readback",
            "observed_at": self.now.isoformat(),
            "environment": SIMNOW_FIRST,
            "account_id": "SIMNOW-TEST-ACCOUNT",
            "robot_id": 12345,
            "broker_id": "9999",
            "platform_list_receipt": api_receipt("GetPlatformList", platform_response, self.now),
            "robot_detail_receipt": api_receipt("GetRobotDetail", robot_response, self.now),
        }
        return self.attestation_mutator(result) if self.attestation_mutator else result

    def terminal_truth(self, *, order_id="O-OPEN-1", status="FILLED", position=1, cash="4800000"):
        self.truth = {
            "source": "simnow_order_and_account_readback",
            "observed_at": NOW.isoformat(),
            "environment": SIMNOW_FIRST,
            "account_id": "SIMNOW-TEST-ACCOUNT",
            "contract": "au2612",
            "order_id": order_id,
            "order_status": status,
            "filled_quantity": 1 if status == "FILLED" else 0,
            "position_quantity": position,
            "cash": cash,
            "available": "4500000", "frozen_margin": "0",
        }


def four_legs(*, target=1, order_id="O-OPEN-1", cash="4800000"):
    shared = {"account_id": "SIMNOW-TEST-ACCOUNT", "contract": "au2612",
              "filled_quantity": target, "cash": cash, "available": "4500000",
              "frozen_margin": "0", "order_ids": [order_id], "observed_at": NOW.isoformat()}
    capital = {**shared, "source": "capital_intent_ledger", "raw_sha256": "sha256:" + "a" * 64,
               "target_quantity": target}
    yuanli = {**shared, "source": "yuanli_execution_ledger", "raw_sha256": "sha256:" + "b" * 64,
              "position_quantity": target}
    oms = {**shared, "source": "execution_oms_readback", "raw_sha256": "sha256:" + "c" * 64,
           "position_quantity": target}
    broker = {**shared, "source": "simnow_broker_custodian_readback", "raw_sha256": "sha256:" + "d" * 64,
              "position_quantity": target}
    return capital, yuanli, oms, broker


class SimNowStrategyTests(unittest.TestCase):
    def test_protocol_template_or_wrong_added_platform_cannot_attest_account(self):
        def template_only(attestation):
            template_response = {"code": 0, "data": {"result": {"exchanges": [{
                "id": 24680, "eid": "Futures_CTP",
                "profiles": {"BrokerId": "9999",
                             "TDFront": "tcp://182.254.243.31:30001",
                             "MDFront": "tcp://182.254.243.31:30011"},
            }]}, "error": None}}
            attestation["platform_list_receipt"] = api_receipt("GetExchangeList", template_response)
            return attestation

        def seven_by_twenty_four(attestation):
            response = attestation["platform_list_receipt"]["response"]
            profiles = response["data"]["result"]["platforms"][0]["profiles"]
            profiles["TDFront"] = "tcp://182.254.243.31:40001"
            profiles["MDFront"] = "tcp://182.254.243.31:40011"
            attestation["platform_list_receipt"] = api_receipt("GetPlatformList", response)
            return attestation

        def opaque_profiles(attestation):
            response = attestation["platform_list_receipt"]["response"]
            response["data"]["result"]["platforms"][0]["profiles"] = "opaque"
            attestation["platform_list_receipt"] = api_receipt("GetPlatformList", response)
            return attestation

        def other_broker_profile(attestation):
            response = attestation["platform_list_receipt"]["response"]
            response["data"]["result"]["platforms"][0]["profiles"]["BrokerId"] = "6020"
            attestation["platform_list_receipt"] = api_receipt("GetPlatformList", response)
            return attestation

        def absent_added_platform(attestation):
            response = attestation["platform_list_receipt"]["response"]
            response["data"]["result"] = {"all": 0, "platforms": []}
            attestation["platform_list_receipt"] = api_receipt("GetPlatformList", response)
            return attestation

        def robot_uses_other_platform(attestation):
            response = attestation["robot_detail_receipt"]["response"]
            response["data"]["result"]["robot"]["strategy_exchange_pairs"] = '[60,[24681],["FUTURES"]]'
            attestation["robot_detail_receipt"] = api_receipt("GetRobotDetail", response)
            return attestation

        def forged_legacy_boolean(attestation):
            del attestation["platform_list_receipt"]
            del attestation["robot_detail_receipt"]
            attestation["first_normal_environment_verified"] = True
            return attestation

        def altered_without_new_hash(attestation):
            response = attestation["platform_list_receipt"]["response"]
            response["data"]["result"]["platforms"][0]["id"] = 24681
            return attestation

        for name, modifier in (
            ("protocol_template", template_only),
            ("seven_by_twenty_four", seven_by_twenty_four),
            ("opaque_profiles", opaque_profiles),
            ("other_broker_profile", other_broker_profile),
            ("absent_added_platform", absent_added_platform),
            ("wrong_robot_platform", robot_uses_other_platform),
            ("legacy_boolean_only", forged_legacy_boolean),
            ("altered_response", altered_without_new_hash),
        ):
            with self.subTest(name=name):
                harness = Harness()
                harness.attestation_mutator = modifier
                self.assertFalse(harness.bridge.snapshot("au2612", NOW)["identity_verified"])
                with self.assertRaises(PaperDenied):
                    harness.runtime.process_command(sign_command(payload(), KEY), NOW)
                self.assertEqual(harness.exchange.buy_calls, [])

    def test_added_platform_json_profiles_may_be_parsed_without_template(self):
        harness = Harness()

        def string_profiles(attestation):
            response = attestation["platform_list_receipt"]["response"]
            platform = response["data"]["result"]["platforms"][0]
            platform["profiles"] = json.dumps(platform["profiles"], sort_keys=True)
            attestation["platform_list_receipt"] = api_receipt("GetPlatformList", response)
            return attestation

        harness.attestation_mutator = string_profiles
        self.assertTrue(harness.bridge.snapshot("au2612", NOW)["identity_verified"])

    def test_runtime_robot_id_must_match_account_robot_detail(self):
        harness = Harness()
        harness.bridge.robot_id_get = lambda: 12346
        self.assertFalse(harness.bridge.snapshot("au2612", NOW)["identity_verified"])
        with self.assertRaises(PaperDenied):
            harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(harness.exchange.buy_calls, [])

    def test_slow_external_claim_cannot_submit_after_entry_window(self):
        harness = Harness()
        original_claim = harness.claim

        def slow_claim(*args):
            receipt = original_claim(*args)
            harness.now = datetime.fromisoformat("2026-09-29T09:05:00.207+08:00")
            harness.exchange.quote["Time"] = int(harness.now.timestamp() * 1000)
            return receipt

        harness.bridge.atomic_claim = slow_claim
        outcome = harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(outcome["status"], "NOT_SUBMITTED_FROZEN")
        self.assertEqual(harness.exchange.buy_calls, [])
        self.assertTrue(any(event["kind"] == "IncidentFrozen" and
                            event["data"].get("class") == "PRE_SUBMIT_DENIED_NO_BROKER_CALL"
                            for event in harness.bridge.load_ledger().events))

    def test_slow_direction_call_cannot_submit_after_entry_window(self):
        harness = Harness()
        original_direction = harness.exchange.SetDirection

        def slow_direction(direction):
            original_direction(direction)
            harness.now = datetime.fromisoformat("2026-09-29T09:05:00.207+08:00")

        harness.exchange.SetDirection = slow_direction
        outcome = harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(outcome["status"], "NOT_SUBMITTED_FROZEN")
        self.assertEqual(harness.exchange.buy_calls, [])

    def test_external_atomic_claim_blocks_concurrent_host_submit(self):
        claims = set()
        first = Harness(claims=claims)
        second = Harness(claims=claims)
        signed = sign_command(payload(), KEY)
        self.assertEqual(first.runtime.process_command(signed, NOW)["status"], "SUBMITTED_PENDING_READBACK")
        with self.assertRaises(PaperDenied) as error:
            second.runtime.process_command(signed, NOW)
        self.assertEqual(error.exception.code, "ATOMIC_CLAIM_DENIED_OR_UNCERTAIN")
        self.assertEqual(first.exchange.buy_calls, [("buy", 1000.02, 1)])
        self.assertEqual(second.exchange.buy_calls, [])

    def test_signed_order_submission_is_durable_before_provider_call(self):
        harness = Harness()
        signed = sign_command(payload(), KEY)
        outcome = harness.runtime.process_command(signed, NOW)
        self.assertEqual(outcome["status"], "SUBMITTED_PENDING_READBACK")
        self.assertEqual(harness.exchange.buy_calls, [("buy", 1000.02, 1)])
        kinds = [event["kind"] for event in harness.bridge.load_ledger().events]
        self.assertEqual(kinds, ["EquityMarked", "ActionAdmitted", "OrderSubmitAttempted", "OrderSubmitted"])
        self.assertEqual(harness.runtime.process_command(signed, NOW)["status"], "DUPLICATE_NO_SUBMIT")
        self.assertEqual(len(harness.exchange.buy_calls), 1)

    def test_no_order_without_account_attestation_or_durable_storage(self):
        for settings, expected in (({"attested": False}, "NO_INDEPENDENT_ACCOUNT_ATTESTATION"), ({"persisted": False}, "LEDGER_PERSISTENCE_UNCERTAIN"), ({"anchored": False}, "NO_EXTERNAL_LEDGER_ANCHOR")):
            harness = Harness(**settings)
            with self.assertRaises(PaperDenied) as error:
                harness.runtime.process_command(sign_command(payload(), KEY), NOW)
            self.assertEqual(error.exception.code, expected)
            self.assertEqual(harness.exchange.buy_calls, [])

    def test_uncertain_submit_freezes_and_never_retries(self):
        harness = Harness()
        harness.exchange.fail_buy = True
        first = harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(first["status"], "SUBMIT_UNCERTAIN_FROZEN")
        self.assertEqual(len(harness.exchange.buy_calls), 1)
        self.assertTrue(harness.bridge.load_ledger().is_frozen())
        again = harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(again["status"], "DUPLICATE_NO_SUBMIT")
        self.assertEqual(len(harness.exchange.buy_calls), 1)

    def test_filled_open_requires_independent_terminal_truth_and_four_legs(self):
        harness = Harness(terminal=False)
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        with self.assertRaises(PaperDenied) as error:
            harness.runtime.settle_order(command_id=payload()["command_id"], order_id="O-OPEN-1", order_status="FILLED", capital_intent=four_legs()[0], yuanli_execution=four_legs()[1], execution_oms=four_legs()[2], broker_custodian=four_legs()[3], now=NOW)
        self.assertEqual(error.exception.code, "NO_INDEPENDENT_TERMINAL_READBACK")
        self.assertTrue(harness.bridge.load_ledger().is_frozen())

        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        harness.terminal_truth()
        legs = four_legs()
        result = harness.runtime.settle_order(command_id=payload()["command_id"], order_id="O-OPEN-1", order_status="FILLED", capital_intent=legs[0], yuanli_execution=legs[1], execution_oms=legs[2], broker_custodian=legs[3], now=NOW)
        self.assertEqual(result["status"], "RECONCILED")
        self.assertFalse(harness.bridge.load_ledger().is_frozen())
        self.assertEqual(harness.runtime.current_position_context()["contract"], "au2612")

    def test_mismatched_terminal_truth_freezes_settlement(self):
        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        harness.terminal_truth(cash="4700000")
        legs = four_legs()
        with self.assertRaises(PaperDenied) as error:
            harness.runtime.settle_order(command_id=payload()["command_id"], order_id="O-OPEN-1", order_status="FILLED", capital_intent=legs[0], yuanli_execution=legs[1], execution_oms=legs[2], broker_custodian=legs[3], now=NOW)
        self.assertEqual(error.exception.code, "TERMINAL_READBACK_MISMATCH")
        self.assertTrue(harness.bridge.load_ledger().is_frozen())

    def test_fractional_terminal_fill_is_not_accepted_for_one_lot(self):
        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        harness.terminal_truth()
        harness.truth["filled_quantity"] = 0.5
        legs = four_legs()
        with self.assertRaises(PaperDenied) as error:
            harness.runtime.settle_order(command_id=payload()["command_id"], order_id="O-OPEN-1", order_status="FILLED", capital_intent=legs[0], yuanli_execution=legs[1], execution_oms=legs[2], broker_custodian=legs[3], now=NOW)
        self.assertEqual(error.exception.code, "TERMINAL_READBACK_MISMATCH")
        self.assertTrue(harness.bridge.load_ledger().is_frozen())

    def test_pre_authorized_stop_uses_today_close_and_no_duplicate(self):
        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        harness.terminal_truth()
        legs = four_legs()
        harness.runtime.settle_order(command_id=payload()["command_id"], order_id="O-OPEN-1", order_status="FILLED", capital_intent=legs[0], yuanli_execution=legs[1], execution_oms=legs[2], broker_custodian=legs[3], now=NOW)
        harness.exchange.positions = [{"ContractType": "au2612", "Type": 1, "Amount": 1, "Margin": 200000}]
        outcome = run_once(harness.runtime, NOW)
        self.assertEqual(outcome["status"], "SAFETY_EXIT_PENDING_READBACK")
        self.assertEqual(outcome["reason"], "EXIT_STOP")
        self.assertEqual(harness.exchange.sell_calls, [("closebuy_today", 989.76, 1)])
        self.assertEqual(len(harness.exchange.buy_calls), 1)
        harness.truth = None
        self.assertEqual(run_once(harness.runtime, NOW)["status"], "PENDING_MANUAL_BROKER_RECONCILIATION")
        self.assertEqual(len(harness.exchange.sell_calls), 1)

    def test_reconciliation_delay_still_protects_confirmed_one_lot_fill(self):
        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        harness.terminal_truth()
        harness.reconciled = False
        harness.risk_available = False
        harness.exchange.positions = [{"ContractType": "au2612", "Type": 1, "Amount": 1, "Margin": 200000}]
        result = run_once(harness.runtime, NOW)
        self.assertEqual(result["status"], "SAFETY_EXIT_PENDING_READBACK")
        self.assertEqual(result["reason"], "EXIT_STOP")
        self.assertEqual(len(harness.exchange.sell_calls), 1)
        kinds = [e["kind"] for e in harness.bridge.load_ledger().events]
        self.assertIn("ProvisionalPositionObserved", kinds)
        self.assertNotIn("ReconciliationMatched", kinds)
        harness.terminal_truth(order_id="O-CLOSE-1", status="PENDING", position=1)
        waiting = run_once(harness.runtime, NOW)
        self.assertEqual(waiting["status"], "LINKED_SAFETY_CLOSE_PENDING_READBACK")
        self.assertEqual(len(harness.exchange.sell_calls), 1)
        harness.terminal_truth(order_id="O-CLOSE-1", status="FILLED", position=0)
        harness.exchange.positions = []
        closed = run_once(harness.runtime, NOW)
        self.assertEqual(closed["status"], "LINKED_SAFETY_CLOSE_CONFIRMED_MANUAL")
        self.assertEqual(len(harness.exchange.sell_calls), 1)
        self.assertIsNone(harness.runtime.current_position_context())
        self.assertTrue(harness.bridge.load_ledger().is_frozen())
        self.assertIn("EmergencyCloseObserved", [e["kind"] for e in harness.bridge.load_ledger().events])
        self.assertEqual(run_once(harness.runtime, NOW)["status"], "LINKED_SAFETY_CLOSE_CONFIRMED_MANUAL")
        self.assertEqual(len(harness.exchange.sell_calls), 1)

    def test_linked_safety_close_rejected_escalates_without_retry(self):
        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        harness.terminal_truth()
        harness.exchange.positions = [{"ContractType": "au2612", "Type": 1, "Amount": 1, "Margin": 200000}]
        self.assertEqual(run_once(harness.runtime, NOW)["status"], "SAFETY_EXIT_PENDING_READBACK")
        harness.terminal_truth(order_id="O-CLOSE-1", status="REJECTED", position=1)
        failed = run_once(harness.runtime, NOW)
        self.assertEqual(failed["status"], "LINKED_SAFETY_CLOSE_FAILED_MANUAL")
        self.assertTrue(harness.bridge.load_ledger().is_frozen())
        self.assertEqual(len(harness.exchange.sell_calls), 1)

    def test_linked_nonterminal_fill_conflict_never_cancels_or_resubmits(self):
        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        harness.terminal_truth()
        harness.exchange.positions = [{"ContractType": "au2612", "Type": 1, "Amount": 1, "Margin": 200000}]
        self.assertEqual(run_once(harness.runtime, NOW)["status"], "SAFETY_EXIT_PENDING_READBACK")
        harness.terminal_truth(order_id="O-CLOSE-1", status="PENDING", position=0)
        outcome = run_once(harness.runtime, NOW)
        self.assertEqual(outcome["status"], "LINKED_SAFETY_CLOSE_NONTERMINAL_CONFLICT_MANUAL")
        self.assertTrue(harness.bridge.load_ledger().is_frozen())
        self.assertEqual(harness.exchange.cancel_calls, [])
        self.assertEqual(len(harness.exchange.sell_calls), 1)

    def test_contingent_stop_survives_grant_revocation_after_filled_entry(self):
        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        harness.terminal_truth()
        harness.runtime.settle_order(command_id=payload()["command_id"], order_id="O-OPEN-1",
                                     order_status="FILLED", capital_intent=four_legs()[0],
                                     yuanli_execution=four_legs()[1], execution_oms=four_legs()[2],
                                     broker_custodian=four_legs()[3], now=NOW)
        harness.runtime.grant = grant(enabled=False, expires_at="2026-09-29T09:00:30+08:00")
        harness.exchange.positions = [{"ContractType": "au2612", "Type": 2, "Amount": 1, "Margin": 200000}]
        result = run_once(harness.runtime, NOW)
        self.assertEqual(result["reason"], "EXIT_STOP")
        self.assertEqual(harness.exchange.sell_calls[0][0], "closebuy")

    def test_cloud_produces_five_session_trend_exit(self):
        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        harness.terminal_truth()
        legs = four_legs()
        harness.runtime.settle_order(command_id=payload()["command_id"], order_id="O-OPEN-1",
                                     order_status="FILLED", capital_intent=legs[0],
                                     yuanli_execution=legs[1], execution_oms=legs[2], broker_custodian=legs[3], now=NOW)
        later = datetime.fromisoformat("2026-10-08T09:01:00+08:00")
        harness.now = later
        harness.trend_break = True
        harness.exchange.quote = {"Buy": 1000.00, "Last": 1000.00, "Time": int(later.timestamp() * 1000)}
        harness.exchange.positions = [{"ContractType": "au2612", "Type": 2, "Amount": 1, "Margin": 200000}]
        result = run_once(harness.runtime, later)
        self.assertEqual(result["status"], "SAFETY_EXIT_PENDING_READBACK")
        self.assertEqual(result["reason"], "EXIT_TREND")
        self.assertEqual(harness.exchange.sell_calls[0][0], "closebuy")

    def test_refresh_pending_settles_only_when_four_independent_legs_arrive(self):
        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        harness.terminal_truth()
        self.assertEqual(harness.runtime.refresh_pending(NOW)["status"], "PENDING_FOUR_WAY_RECONCILIATION")
        harness.truth["four_way"] = dict(zip(
            ("capital_intent", "yuanli_execution", "execution_oms", "broker_custodian"),
            four_legs(),
        ))
        self.assertEqual(harness.runtime.refresh_pending(NOW)["status"], "RECONCILED")
        self.assertEqual(harness.runtime.refresh_pending(NOW)["status"], "NO_PENDING_ORDER")

    def test_expired_pending_order_is_canceled_once_then_waits_for_readback(self):
        harness = Harness()
        harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        later = datetime.fromisoformat("2026-09-29T09:06:00+08:00")
        harness.terminal_truth(status="PENDING", position=0, cash="5000000")
        harness.truth["observed_at"] = later.isoformat()
        self.assertEqual(harness.runtime.refresh_pending(later)["status"], "CANCEL_REQUESTED_PENDING_READBACK")
        self.assertEqual(harness.exchange.cancel_calls, ["O-OPEN-1"])
        self.assertEqual(harness.runtime.refresh_pending(later)["status"], "CANCEL_UNCERTAIN_MANUAL_RECONCILIATION")
        self.assertEqual(harness.exchange.cancel_calls, ["O-OPEN-1"])

    def test_ledger_tamper_and_real_broker_id_stop_all_calls(self):
        harness = Harness()
        harness.exchange.account["Info"]["BrokerID"] = "REAL-BROKER"
        with self.assertRaises(PaperDenied) as error:
            harness.runtime.process_command(sign_command(payload(), KEY), NOW)
        self.assertEqual(error.exception.code, "NOT_SIMNOW_BROKER_ID")
        self.assertEqual(harness.exchange.buy_calls, [])


if __name__ == "__main__":
    unittest.main()
