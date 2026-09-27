"""Adversarial proof-boundary tests; no network, credentials or order methods."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import unittest
from unittest.mock import patch

from yuanli_invest.gold_au_broker_facts import (
    BrokerFactsReader, NATIVE_FIELDS, canonical, digest, native_rows,
)
from yuanli_invest.gold_au_official_exit_history import OfficialDailyHistoryReader
from yuanli_invest.gold_paper import PaperDenied, SIMNOW_FIRST
from scripts.youquant_gold_simnow_strategy import _verified_added_ctp_binding

NOW = datetime(2026, 9, 28, 1, 15, 5, tzinfo=timezone.utc)
INVESTOR = "DIAGNOSTIC-INVESTOR"
ACCOUNT = "DIAGNOSTIC-CASH-ACCOUNT"
CONTRACT = "au2612"
KEY = b"test-evidence-verifier-not-a-real-host-key"


def signed(row):
    row = deepcopy(row)
    row["raw_sha256"] = digest(row)
    row["signature"] = hmac.new(KEY, canonical(row), hashlib.sha256).hexdigest()
    return row


def verified(row):
    if not isinstance(row, dict):
        return False
    body = {k: v for k, v in row.items() if k != "signature"}
    expected = hmac.new(KEY, canonical(body), hashlib.sha256).hexdigest()
    return hmac.compare_digest(str(row.get("signature")), expected)


def api(method, result):
    response = {"code": 0, "data": {"result": result}}
    return {"method": method, "observed_at": NOW.isoformat(), "response": response,
            "response_sha256": digest(response)}


def attestation():
    return {"source": "youquant_account_and_robot_readback", "environment": SIMNOW_FIRST,
        "account_id": INVESTOR, "broker_id": "9999", "robot_id": 479509, "observed_at": NOW.isoformat(),
        "platform_list_receipt": api("GetPlatformList", {"all": 1, "platforms": [{"id": 7,
            "eid": "Futures_CTP", "profiles": {"TDFront": "tcp://182.254.243.31:30001",
                "MDFront": "tcp://182.254.243.31:30011", "BrokerId": "9999"}}]}),
        "robot_detail_receipt": api("GetRobotDetail", {"robot": {"id": 479509, "status": 1,
            "strategy_exchange_pairs": json.dumps([60, [7], ["FUTURES_CTP"]])}})}


def policy():
    return signed({"source": "independent_account_execution_cost_policy", "environment": SIMNOW_FIRST,
        "account_id": INVESTOR, "contract": CONTRACT, "observed_at": NOW.isoformat(),
        "expires_at": (NOW + timedelta(minutes=1)).isoformat(), "quantity": 1, "account_currency": "CNY",
        "covers_additional_order_freeze": True, "covers_all_broker_and_exchange_fees": True,
        "covers_future_close_rates": True, "margin_price_upper_cny_per_gram": "1100",
        "open_price_upper_cny_per_gram": "1100", "close_price_upper_cny_per_gram": "1500",
        "additional_margin_freeze_upper_cny": "50", "additional_round_trip_fee_upper_cny": "2",
        "round_trip_fee_upper_cny": "30"})


def binding():
    return signed({"source": "independent_platform_native_order_binding", "environment": SIMNOW_FIRST,
        "account_id": INVESTOR, "contract": CONTRACT, "observed_at": NOW.isoformat(), "quantity": 1,
        "order_id": "platform-111", "order_sys_id": "      77", "order_ref": "9", "front_id": 3,
        "session_id": 4, "trading_day": "20260928", "direction": "0", "offset_flag": "0"})


class HostExchange:
    def __init__(self):
        self.calls = []
        self.status = True
        base = {"BrokerID": "9999", "InvestorID": INVESTOR, "InstrumentID": CONTRACT,
                "ExchangeID": "SHFE", "InvestorRange": "3"}
        self.rows = {
            "ReqQryInstrumentMarginRate": [dict(base, HedgeFlag="1", IsRelative=0,
                LongMarginRatioByMoney="0.2", LongMarginRatioByVolume="0",
                ShortMarginRatioByMoney="0.2", ShortMarginRatioByVolume="0")],
            "ReqQryInstrumentCommissionRate": [dict(base, BizType="1", OpenRatioByMoney="0",
                OpenRatioByVolume="10", CloseRatioByMoney="0", CloseRatioByVolume="10",
                CloseTodayRatioByMoney="0", CloseTodayRatioByVolume="0")],
            "ReqQryBrokerTradingParams": [{"BrokerID": "9999", "InvestorID": INVESTOR,
                "AccountID": ACCOUNT, "CurrencyID": "CNY", "MarginPriceType": "1", "Algorithm": "1"}],
            "ReqQryDepthMarketData": [{"InstrumentID": CONTRACT, "ExchangeID": "SHFE", "TradingDay": "20260928",
                "ActionDay": "20260928", "UpdateTime": "09:15:05", "UpdateMillisec": 0,
                "LastPrice": "1000", "PreSettlementPrice": "990", "AveragePrice": "999",
                "OpenPrice": "998", "UpperLimitPrice": "1100", "LowerLimitPrice": "900"}],
            "ReqQryTradingAccount": [{"BrokerID": "9999", "AccountID": ACCOUNT, "CurrencyID": "CNY",
                "TradingDay": "20260928", "Balance": "10000000", "Available": "9750000", "FrozenMargin": "0"}],
            "ReqQryOrder": [dict(base, TradingDay="20260928", OrderSysID="      77", OrderRef="9",
                FrontID=3, SessionID=4, OrderStatus="0", OrderSubmitStatus="3", VolumeTotalOriginal=1,
                VolumeTraded=1, VolumeTotal=0, Direction="0", CombOffsetFlag="0", CombHedgeFlag="1", LimitPrice="1000")],
            "ReqQryTrade": [dict(base, TradingDay="20260928", TradeID=" trade1", OrderSysID="      77",
                OrderRef="9", Volume=1, Price="1000", Direction="0", OffsetFlag="0", HedgeFlag="1")],
            "ReqQryInvestorPosition": [dict(base, TradingDay="20260928", PosiDirection="2", HedgeFlag="1",
                PositionDate="1", Position=1, TodayPosition=1, UseMargin="250000", FrozenMargin="0")],
        }
        self.pending, self.positions = [], []
        self.ticker = {"Time": int(NOW.timestamp() * 1000), "Buy": "999.98", "Sell": "1000.02", "Last": "1000"}

    def IO(self, *args):
        self.calls.append(("IO", *args))
        if args == ("status",):
            return self.status
        if len(args) != 3 or args[0] != "api" or args[1] not in NATIVE_FIELDS:
            raise AssertionError("unapproved native operation")
        method = args[1]
        name = NATIVE_FIELDS[method][0]
        return [[{"Name": name, "Value": deepcopy(row)} for row in self.rows[method]] +
                [{"Name": "CThostFtdcRspInfoField", "Value": {"ErrorID": 0}}]]

    def GetAccount(self):
        self.calls.append(("GetAccount",))
        return {"Info": {"BrokerID": "9999", "InvestorID": INVESTOR, "AccountID": ACCOUNT}}

    def SetContractType(self, contract):
        self.calls.append(("SetContractType", contract))
        return {"InstrumentID": contract, "ExchangeID": "SHFE", "VolumeMultiple": 1000, "PriceTick": .02,
                "DeliveryYear": 2026, "DeliveryMonth": 12, "IsTrading": 1}

    def GetTicker(self):
        self.calls.append(("GetTicker",))
        return self.ticker

    def GetOrders(self):
        self.calls.append(("GetOrders",))
        return self.pending

    def GetPositions(self):
        self.calls.append(("GetPositions",))
        return self.positions


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.host = HostExchange()
        self.attestation, self.policy, self.binding = attestation(), policy(), binding()
        self.reader = BrokerFactsReader(exchange=self.host, robot_id=479509, clock=lambda: NOW,
            account_attestation_reader=lambda: self.attestation,
            account_attestation_verifier=_verified_added_ctp_binding,
            account_cost_policy_reader=lambda _: self.policy, independent_receipt_verifier=verified,
            order_binding_reader=lambda _: self.binding)

    def test_current_read_is_real_call_orchestration_and_empty_orders_not_terminal(self):
        result = self.reader.read_current(CONTRACT)
        self.assertEqual(result["pending_order_count"], 0)
        self.assertFalse(result["terminal_history_proven"])
        self.assertEqual(result["broker_equity"], "10000000")
        self.assertIn(("GetPositions",), self.host.calls)
        self.assertIn(("GetOrders",), self.host.calls)
        self.host.rows["ReqQryOrder"] = []
        with self.assertRaisesRegex(PaperDenied, "NATIVE_EXPECTED_SINGLE_ROW"):
            self.reader.terminal_truth("platform-111")

    def test_current_account_hash_is_exact_account_not_quote_or_later_read(self):
        method = "ReqQryTradingAccount"
        expected = digest([[{"Name": NATIVE_FIELDS[method][0], "Value": self.host.rows[method][0]},
                            {"Name": "CThostFtdcRspInfoField", "Value": {"ErrorID": 0}}]])
        original_quote = self.reader.quote
        def quote_with_unrelated_native_receipt(contract):
            # A later observed market receipt must never replace the already
            # captured account's full canonical decoded response hash.
            self.reader._native("ReqQryDepthMarketData", {"InstrumentID": contract, "ExchangeID": "SHFE"})
            return original_quote(contract)
        self.reader.quote = quote_with_unrelated_native_receipt
        result = self.reader.read_current(CONTRACT)
        self.assertEqual(result["raw_account_sha256"], expected)
        self.assertNotEqual(expected, result["quote"]["raw_sha256"])
        self.assertNotEqual(expected, self.reader.receipts[-1]["response_sha256"])
        self.assertEqual(result["raw_orders_sha256"], digest(result["pending_orders"]))
        self.assertEqual(result["raw_positions_sha256"], digest(result["positions"]))

    def test_cost_receipts_are_exact_named_native_reads_not_policy_callback_tail(self):
        def policy_with_unrelated_native_read(_):
            self.reader._native("ReqQryTradingAccount", {"BrokerID": "9999", "InvestorID": INVESTOR,
                "AccountID": ACCOUNT, "CurrencyID": "CNY"})
            return self.policy
        self.reader.policy_reader = policy_with_unrelated_native_read
        result = self.reader.read_account_costs(CONTRACT)
        self.assertEqual([row["method"] for row in result["native_receipts"]], [
            "ReqQryInstrumentMarginRate", "ReqQryInstrumentCommissionRate", "ReqQryBrokerTradingParams", "ReqQryDepthMarketData"])
        for receipt in result["native_receipts"]:
            method = receipt["method"]
            expected = digest([[{"Name": NATIVE_FIELDS[method][0], "Value": row} for row in self.host.rows[method]] +
                               [{"Name": "CThostFtdcRspInfoField", "Value": {"ErrorID": 0}}]])
            self.assertEqual(receipt["response_sha256"], expected)

    def test_terminal_native_hashes_survive_later_pending_callback_read(self):
        original_pending = self.host.GetOrders
        def pending_with_unrelated_native_read():
            self.reader._native("ReqQryDepthMarketData", {"InstrumentID": CONTRACT, "ExchangeID": "SHFE"})
            return original_pending()
        self.host.GetOrders = pending_with_unrelated_native_read
        truth = self.reader.terminal_truth("platform-111")
        methods = ("ReqQryTradingAccount", "ReqQryOrder", "ReqQryTrade", "ReqQryInvestorPosition")
        self.assertEqual([row["method"] for row in truth["native_receipts"]], list(methods))
        for label, method in zip(("account", "orders", "trades", "positions"), methods):
            expected = digest([[{"Name": NATIVE_FIELDS[method][0], "Value": row} for row in self.host.rows[method]] +
                               [{"Name": "CThostFtdcRspInfoField", "Value": {"ErrorID": 0}}]])
            self.assertEqual(truth[f"raw_{label}_sha256"], expected)

    def test_account_attestation_no_identity_synthesis(self):
        self.assertEqual(self.reader.account_attestation(), self.attestation)
        self.reader.attestation_reader = None
        with self.assertRaisesRegex(PaperDenied, "ATTESTATION_UNWIRED"):
            self.reader.read_current(CONTRACT)

    def test_wrong_identity_stops_before_native(self):
        self.attestation["account_id"] = "other"
        with self.assertRaisesRegex(PaperDenied, "ATTESTATION_MISMATCH"):
            self.reader.current_margin(CONTRACT)
        self.assertFalse(any(len(call) > 1 and call[1] == "api" for call in self.host.calls))

    def test_control_receipt_hash_tamper_and_wrong_front(self):
        self.attestation["platform_list_receipt"]["response"]["data"]["result"]["platforms"][0]["profiles"]["TDFront"] = "unapproved:1"
        with self.assertRaisesRegex(PaperDenied, "ATTESTATION_UNVERIFIED"):
            self.reader.account_attestation()

    def test_future_and_stale_attestation(self):
        for shift in (1, -301):
            with self.subTest(shift=shift):
                self.attestation["observed_at"] = (NOW + timedelta(seconds=shift)).isoformat()
                with self.assertRaisesRegex(PaperDenied, "STALE_OR_FUTURE"):
                    self.reader.account_attestation()

    def test_late_host_return_rejected_without_followup(self):
        times = iter([NOW, NOW + timedelta(seconds=16)])
        self.reader.clock = lambda: next(times)
        with self.assertRaisesRegex(PaperDenied, "READ_LATE"):
            self.reader._call("GetAccount")
        self.assertEqual(self.host.calls, [("GetAccount",)])

    def test_read_allowlist_rejects_trading_and_password_method(self):
        for name, args in (("Buy", (1000, 1)), ("CancelOrder", ("1",)), ("IO", ("api", "ReqUserPasswordUpdate", {}))):
            with self.assertRaises(PaperDenied):
                self.reader._call(name, *args)
        self.assertEqual(self.host.calls, [])

    def test_quote_future_stale_crossed_and_nan(self):
        for mutation in ({"Time": int((NOW + timedelta(seconds=1)).timestamp()*1000)},
                         {"Time": int((NOW - timedelta(seconds=16)).timestamp()*1000)},
                         {"Buy": "1001", "Sell": "1000"}, {"Last": "NaN"}):
            with self.subTest(mutation=mutation):
                original = deepcopy(self.host.ticker)
                self.host.ticker.update(mutation)
                with self.assertRaises(PaperDenied):
                    self.reader.quote(CONTRACT)
                self.host.ticker = original

    def test_exact_native_full_hash_and_unknown_fields_cannot_override(self):
        method = "ReqQryInstrumentMarginRate"
        raw = [[{"Name": NATIVE_FIELDS[method][0], "Value": {"InvestorID": INVESTOR,
                "unrecognized_margin_override": 0}}]]
        rows, raw_hash = native_rows(raw, method)
        self.assertEqual(rows, [{"InvestorID": INVESTOR}])
        self.assertEqual(raw_hash, digest(raw))
        self.assertNotEqual(raw_hash, digest(rows))

    def test_unknown_struct_and_error_packet_rejected(self):
        for packet in (("MadeUpCostField", {}), ("CThostFtdcRspInfoField", {"ErrorID": 23})):
            with self.assertRaises(PaperDenied):
                native_rows([[{"Name": packet[0], "Value": packet[1]}]], "ReqQryOrder")

    def test_cost_rates_and_account_policy_derive_bounds(self):
        cost = self.reader.read_account_costs(CONTRACT)
        self.assertEqual(cost["margin_for_one_lot"], "220050.00")
        self.assertEqual(cost["round_trip_fee_upper_cny"], "30")
        self.assertEqual(cost["open_fee_cny"], "10")
        self.assertEqual(cost["close_today_fee_cny"], "0")
        self.assertEqual(cost["close_yesterday_fee_cny"], "10")
        self.assertEqual(cost["margin_basis_field"], "PreSettlementPrice")
        body = {k: v for k,v in cost.items() if k != "raw_sha256"}
        self.assertEqual(cost["raw_sha256"], digest(body))
        self.assertEqual(self.reader.current_round_trip_fee_upper(CONTRACT), "30")

    def test_native_ascii_char_enums_supported(self):
        self.host.rows["ReqQryInstrumentMarginRate"][0].update(InvestorRange=51, HedgeFlag=49)
        self.host.rows["ReqQryInstrumentCommissionRate"][0].update(InvestorRange=51, BizType=49)
        self.host.rows["ReqQryBrokerTradingParams"][0]["MarginPriceType"] = 49
        self.assertEqual(self.reader.read_account_costs(CONTRACT)["status"], "BOUNDED_ACCOUNT_COSTS")

    def test_cost_policy_unwired_and_unsigned_fail_closed(self):
        self.reader.policy_reader = None
        with self.assertRaisesRegex(PaperDenied, "POLICY_UNWIRED"):
            self.reader.current_margin(CONTRACT)
        self.reader.policy_reader = lambda _: {**self.policy, "round_trip_fee_upper_cny": "1"}
        with self.assertRaisesRegex(PaperDenied, "AUTHENTICITY_UNVERIFIED"):
            self.reader.current_margin(CONTRACT)

    def test_fees_too_small_even_signed_fail(self):
        self.policy = signed({**{k:v for k,v in self.policy.items() if k not in {"signature", "raw_sha256"}},
                              "round_trip_fee_upper_cny": "10"})
        with self.assertRaisesRegex(PaperDenied, "FEE_UPPER_TOO_SMALL"):
            self.reader.current_margin(CONTRACT)

    def test_order_margin_estimate_does_not_substitute_missing_freeze_policy(self):
        self.policy = signed({**{k:v for k,v in self.policy.items() if k not in {"signature", "raw_sha256"}},
                              "covers_additional_order_freeze": False})
        with self.assertRaisesRegex(PaperDenied, "POLICY_SCOPE_INCOMPLETE"):
            self.reader.current_margin(CONTRACT)

    def test_wrong_account_and_relative_or_generic_margin_rejected(self):
        for mutation in ({"InvestorID": "another"}, {"InvestorRange": "1"}, {"IsRelative": True}, {"HedgeFlag": "2"}):
            with self.subTest(mutation=mutation):
                saved = deepcopy(self.host.rows["ReqQryInstrumentMarginRate"])
                self.host.rows["ReqQryInstrumentMarginRate"][0].update(mutation)
                with self.assertRaises(PaperDenied):
                    self.reader.current_margin(CONTRACT)
                self.host.rows["ReqQryInstrumentMarginRate"] = saved

    def test_wrong_contract_and_currency_rejected(self):
        self.host.rows["ReqQryInstrumentCommissionRate"][0]["InstrumentID"] = "au2702"
        with self.assertRaisesRegex(PaperDenied, "CONTRACT_SCOPE_MISMATCH"):
            self.reader.current_margin(CONTRACT)

    def test_market_time_and_price_caps_are_mandatory(self):
        self.host.rows["ReqQryDepthMarketData"][0]["UpdateTime"] = "09:16:00"
        with self.assertRaisesRegex(PaperDenied, "STALE_OR_FUTURE"):
            self.reader.current_margin(CONTRACT)
        self.host.rows["ReqQryDepthMarketData"][0]["UpdateTime"] = "09:15:05"
        self.policy = signed({**{k:v for k,v in self.policy.items() if k not in {"signature", "raw_sha256"}},
                              "open_price_upper_cny_per_gram": "1000"})
        with self.assertRaisesRegex(PaperDenied, "PRICE_BOUND_TOO_SMALL"):
            self.reader.current_margin(CONTRACT)

    def test_terminal_native_order_trades_positions_account_all_read(self):
        truth = self.reader.terminal_truth("platform-111")
        self.assertEqual(truth["order_status"], "FILLED")
        self.assertEqual(truth["filled_quantity"], "1")
        self.assertEqual(truth["position_quantity"], "1")
        self.assertEqual(truth["pending_order_count"], 0)
        self.assertEqual(truth["history_scope"], "CURRENT_BROKER_TRADING_DAY_ONLY")
        self.assertEqual(len(truth["native_receipts"]), 4)
        for name in ("account", "orders", "trades", "positions"):
            self.assertRegex(truth[f"raw_{name}_sha256"], r"^sha256:[0-9a-f]{64}$")

    def test_no_platform_order_id_guess_and_cross_day_unknown(self):
        self.reader.binding_reader = None
        with self.assertRaisesRegex(PaperDenied, "BINDING_UNWIRED"):
            self.reader.terminal_truth("77")
        self.reader.binding_reader = lambda _: self.binding
        self.host.rows["ReqQryTradingAccount"][0]["TradingDay"] = "20260929"
        with self.assertRaisesRegex(PaperDenied, "CROSS_DAY_TERMINAL_ARCHIVE_UNAVAILABLE"):
            self.reader.terminal_truth("platform-111")

    def test_filled_order_missing_trade_never_terminal(self):
        self.host.rows["ReqQryTrade"] = []
        with self.assertRaisesRegex(PaperDenied, "ORDER_TRADE_FILL_DELTA"):
            self.reader.terminal_truth("platform-111")

    def test_trade_duplicates_wrong_scope_and_noninteger(self):
        for mode in ("duplicate", "wrong_scope", "fractional"):
            original = deepcopy(self.host.rows["ReqQryTrade"])
            if mode == "duplicate":
                self.host.rows["ReqQryTrade"] *= 2
            elif mode == "wrong_scope":
                self.host.rows["ReqQryTrade"][0]["InvestorID"] = "other"
            else:
                self.host.rows["ReqQryTrade"][0]["Volume"] = .5
            with self.assertRaises(PaperDenied):
                self.reader.terminal_truth("platform-111")
            self.host.rows["ReqQryTrade"] = original

    def test_canceled_has_zero_actual_trades(self):
        self.host.rows["ReqQryOrder"][0].update(OrderStatus="5", VolumeTraded=0, VolumeTotal=1)
        self.host.rows["ReqQryTrade"] = []
        self.host.rows["ReqQryInvestorPosition"] = []
        self.assertEqual(self.reader.terminal_truth("platform-111")["order_status"], "CANCELED")

    def test_pending_empty_cannot_override_nonterminal_native(self):
        self.host.rows["ReqQryOrder"][0].update(OrderStatus="3", VolumeTraded=0, VolumeTotal=1)
        self.host.rows["ReqQryTrade"] = []
        self.host.rows["ReqQryInvestorPosition"] = []
        truth = self.reader.terminal_truth("platform-111")
        self.assertEqual(truth["order_status"], "PENDING")
        self.assertEqual(truth["filled_quantity"], "0")
        self.assertEqual(truth["pending_order_count"], 0)

    def test_positive_pending_readback_remains_monitorable_not_terminal(self):
        self.host.rows["ReqQryOrder"][0].update(OrderStatus="3", VolumeTraded=0, VolumeTotal=1)
        self.host.rows["ReqQryTrade"] = []
        self.host.rows["ReqQryInvestorPosition"] = []
        self.host.pending = [{"Id": "platform-111", "Amount": 1, "DealAmount": 0}]
        truth = self.reader.terminal_truth("platform-111")
        self.assertEqual(truth["order_status"], "PENDING")
        self.assertEqual(truth["pending_order_count"], 1)

    def test_terminal_still_in_pending_is_contradiction(self):
        self.host.pending = [{"Id": "platform-111", "Amount": 1, "DealAmount": 1}]
        with self.assertRaisesRegex(PaperDenied, "STILL_PENDING_CONTRADICTION"):
            self.reader.terminal_truth("platform-111")

    def test_position_short_or_more_than_one_blocked(self):
        self.host.rows["ReqQryInvestorPosition"][0]["PosiDirection"] = "3"
        with self.assertRaisesRegex(PaperDenied, "NON_LONG"):
            self.reader.terminal_truth("platform-111")

    def test_unwired_reconciliation_and_subledger_fail_closed(self):
        with self.assertRaisesRegex(PaperDenied, "RECONCILIATION_READERS_UNWIRED"):
            self.reader.reconciliation_probe()
        with self.assertRaisesRegex(PaperDenied, "SUBLEDGER_UNWIRED"):
            self.reader.strategy_equity_mark()
        self.assertEqual(len(self.reader.callbacks()), 7)

    def reconciliation_legs(self):
        sources = ("capital_intent_ledger", "yuanli_execution_ledger", "execution_oms_readback", "simnow_broker_custodian_readback")
        legs = [signed({"source": source, "environment": SIMNOW_FIRST, "account_id": INVESTOR,
            "contract": CONTRACT, "observed_at": NOW.isoformat(), "target_quantity": 1, "position_quantity": 1,
            "filled_quantity": 1, "cash": "10000000", "available": "9750000", "frozen_margin": "0",
            "order_ids": ["platform-111"], "native_evidence_reference": source + "-independently-observed"}) for source in sources]
        self.reader.reconciliation_readers = {source: (lambda leg=leg: leg) for source, leg in zip(sources, legs)}
        return sources, legs

    def test_four_authenticated_independent_reconciliation_inputs(self):
        self.reconciliation_legs()
        self.assertTrue(self.reader.reconciliation_probe())
        self.assertEqual(self.reader.last_reconciliation_result["status"], "MATCHED")

    def test_four_way_drift_is_not_cleared(self):
        sources, legs = self.reconciliation_legs()
        leg = signed({**{k:v for k,v in legs[-1].items() if k not in {"raw_sha256", "signature"}}, "cash": "9999999"})
        self.reader.reconciliation_readers[sources[-1]] = lambda: leg
        self.assertFalse(self.reader.reconciliation_probe())
        self.assertEqual(self.reader.last_reconciliation_result["reason"], "CASH_DELTA")

    def test_same_reader_callback_and_forged_leg_rejected(self):
        sources, legs = self.reconciliation_legs()
        same = lambda: legs[0]
        self.reader.reconciliation_readers = dict.fromkeys(sources, same)
        with self.assertRaisesRegex(PaperDenied, "READERS_UNWIRED"):
            self.reader.reconciliation_probe()
        sources, legs = self.reconciliation_legs()
        legs[0]["cash"] = "1"
        with self.assertRaisesRegex(PaperDenied, "AUTHENTICITY_UNVERIFIED"):
            self.reader.reconciliation_probe()

    def test_reconciliation_matching_foreign_account_still_rejected(self):
        sources, legs = self.reconciliation_legs()
        changed = [signed({**{k:v for k,v in leg.items() if k not in {"raw_sha256", "signature"}},
                          "account_id": "foreign-account"}) for leg in legs]
        self.reader.reconciliation_readers = {source: (lambda leg=leg: leg) for source, leg in zip(sources, changed)}
        with self.assertRaisesRegex(PaperDenied, "ENVIRONMENT_MISMATCH"):
            self.reader.reconciliation_probe()

    def test_boolean_quantity_and_missing_equity_slot_not_promoted(self):
        self.policy = signed({**{k:v for k,v in self.policy.items() if k not in {"signature", "raw_sha256"}}, "quantity": True})
        with self.assertRaisesRegex(PaperDenied, "POLICY_SCOPE_INCOMPLETE"):
            self.reader.current_margin(CONTRACT)

    def test_native_unsupported_margin_type_not_guessed(self):
        self.host.rows["ReqQryBrokerTradingParams"][0]["MarginPriceType"] = "9"
        with self.assertRaisesRegex(PaperDenied, "MARGIN_PRICE_TYPE_UNSUPPORTED"):
            self.reader.current_margin(CONTRACT)

    def test_terminal_with_four_way_without_sources_preserves_real_truth_unknown(self):
        truth = self.reader.terminal_truth_with_four_way("platform-111")
        self.assertEqual(truth["order_status"], "FILLED")
        self.assertEqual(truth["reconciliation_status"], "UNKNOWN")
        self.assertNotIn("four_way", truth)
        self.assertRegex(truth["broker_truth_sha256"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(truth["raw_sha256"], digest({k:v for k,v in truth.items() if k != "raw_sha256"}))

    def test_terminal_with_four_genuine_signed_legs_matches_native(self):
        _, legs = self.reconciliation_legs()
        truth = self.reader.terminal_truth_with_four_way("platform-111")
        self.assertEqual(truth["reconciliation_status"], "MATCHED")
        self.assertEqual(set(truth["four_way"]), {"capital_intent", "yuanli_execution", "execution_oms", "broker_custodian"})
        self.assertEqual(list(truth["four_way"].values()), legs)
        self.assertEqual(truth["cash"], "10000000")

    def test_pending_kept_without_reading_four_way_producers(self):
        self.host.rows["ReqQryOrder"][0].update(OrderStatus="3", VolumeTraded=0, VolumeTotal=1)
        self.host.rows["ReqQryTrade"] = []
        self.host.rows["ReqQryInvestorPosition"] = []
        count = []
        self.reader.reconciliation_readers = {"capital_intent_ledger": lambda: count.append("called")}
        truth = self.reader.terminal_truth_with_four_way("platform-111")
        self.assertEqual(truth["order_status"], "PENDING")
        self.assertEqual(truth["reconciliation_status"], "NOT_TERMINAL")
        self.assertNotIn("four_way", truth)
        self.assertEqual(count, [])

    def test_four_way_forged_and_missing_legs_never_constructed(self):
        sources, legs = self.reconciliation_legs()
        legs[0]["cash"] = "1"
        truth = self.reader.terminal_truth_with_four_way("platform-111")
        self.assertEqual(truth["reconciliation_status"], "UNKNOWN")
        self.assertNotIn("four_way", truth)
        del self.reader.reconciliation_readers[sources[0]]
        self.assertEqual(self.reader.terminal_truth_with_four_way("platform-111")["reconciliation_status"], "UNKNOWN")

    def test_four_way_wrong_identity_source_future_and_stale_remain_unknown(self):
        for mutation in ({"account_id": "other"}, {"source": "made-up-source"}, {"contract": "au2702"},
                         {"observed_at": (NOW+timedelta(seconds=1)).isoformat()},
                         {"observed_at": (NOW-timedelta(seconds=31)).isoformat()}):
            sources, legs = self.reconciliation_legs()
            changed = signed({**{k:v for k,v in legs[-1].items() if k not in {"raw_sha256", "signature"}}, **mutation})
            self.reader.reconciliation_readers[sources[-1]] = lambda: changed
            with self.subTest(mutation=mutation):
                truth = self.reader.terminal_truth_with_four_way("platform-111")
                self.assertEqual(truth["reconciliation_status"], "UNKNOWN")
                self.assertNotIn("four_way", truth)

    def test_four_agreeing_sources_with_wrong_native_cash_are_drifted(self):
        sources, legs = self.reconciliation_legs()
        changed = [signed({**{k:v for k,v in leg.items() if k not in {"raw_sha256", "signature"}}, "cash": "10000001"}) for leg in legs]
        self.reader.reconciliation_readers = {source: (lambda leg=leg: leg) for source, leg in zip(sources, changed)}
        truth = self.reader.terminal_truth_with_four_way("platform-111")
        self.assertEqual(truth["reconciliation_status"], "DRIFTED")
        self.assertEqual(truth["reconciliation_reason"], "FOUR_WAY_NATIVE_MONEY_DELTA")
        self.assertNotIn("four_way", truth)

    def test_four_agreeing_sources_with_wrong_order_are_drifted(self):
        sources, legs = self.reconciliation_legs()
        changed = [signed({**{k:v for k,v in leg.items() if k not in {"raw_sha256", "signature"}}, "order_ids": ["other-order"]}) for leg in legs]
        self.reader.reconciliation_readers = {source: (lambda leg=leg: leg) for source, leg in zip(sources, changed)}
        truth = self.reader.terminal_truth_with_four_way("platform-111")
        self.assertEqual(truth["reconciliation_status"], "DRIFTED")
        self.assertEqual(truth["reconciliation_reason"], "FOUR_WAY_NATIVE_ORDER_OR_POSITION_DELTA")

    def test_four_way_cash_drift_or_same_raw_hash_never_matched(self):
        sources, legs = self.reconciliation_legs()
        changed = signed({**{k:v for k,v in legs[-1].items() if k not in {"raw_sha256", "signature"}}, "cash": "9999999"})
        self.reader.reconciliation_readers[sources[-1]] = lambda: changed
        truth = self.reader.terminal_truth_with_four_way("platform-111")
        self.assertEqual(truth["reconciliation_reason"], "CASH_DELTA")
        sources, legs = self.reconciliation_legs()
        changed = []
        for leg in legs:
            value = deepcopy(leg)
            value["raw_sha256"] = "sha256:"+"a"*64
            value["signature"] = hmac.new(KEY, canonical({k:v for k,v in value.items() if k != "signature"}), hashlib.sha256).hexdigest()
            changed.append(value)
        self.reader.reconciliation_readers = {source: (lambda leg=leg: leg) for source, leg in zip(sources, changed)}
        truth = self.reader.terminal_truth_with_four_way("platform-111")
        self.assertEqual(truth["reconciliation_reason"], "CLONED_LEDGER_EVIDENCE")
        self.assertNotIn("four_way", truth)

    def test_four_way_independent_source_failure_does_not_log_or_synthesize(self):
        sources, _ = self.reconciliation_legs()
        def failed_source():
            raise RuntimeError("private-key-and-account-details-must-not-leak")
        self.reader.reconciliation_readers[sources[1]] = failed_source
        truth = self.reader.terminal_truth_with_four_way("platform-111")
        self.assertEqual(truth["reconciliation_status"], "UNKNOWN")
        self.assertEqual(truth["reconciliation_reason"], "FOUR_WAY_INDEPENDENT_READ_FAILED")
        self.assertNotIn("private-key", canonical(truth).decode())


class HistoryReaderTests(unittest.TestCase):
    def setUp(self):
        days = []
        day = datetime(2026, 9, 8, tzinfo=timezone.utc).date()
        while day < NOW.date():
            if day.weekday() < 5:
                days.append(day.isoformat())
            day += timedelta(days=1)
        # This test isolates raw-byte binding from the separately tested
        # official annual notice parser. No generated calendar is deployed.
        self.days = days[-11:]
        self.calendar = {"sessions": days + ["2026-09-28"], "covered_years": [2026], "raw_sha256": "a"*64}
        self.snapshots = []
        for day in self.days:
            raw = canonical({"report_date": day.replace("-", ""), "o_curinstrument": [{"PRODUCTID": "au_f",
                "DELIVERYMONTH": "2612", "OPENPRICE": "1000", "HIGHESTPRICE": "1001", "LOWESTPRICE": "999",
                "CLOSEPRICE": "1000", "VOLUME": "10", "OPENINTEREST": "50"}]})
            self.snapshots.append({"report_date": day, "source_url": "https://www.shfe.com.cn/data/dailydata/kx/kx"+day.replace("-", "")+".dat",
                "obtained_at": "2026-09-28T00:00:00+00:00", "available_at": "2026-09-28T00:00:00+00:00",
                "raw_bytes": raw, "raw_sha256": "sha256:"+hashlib.sha256(raw).hexdigest()})
        self.reader = OfficialDailyHistoryReader(calendar_path="not-a-deployed-test-path", clock=lambda: NOW,
            snapshot_reader=lambda days: self.snapshots, count=11)

    def read(self):
        with patch("yuanli_invest.gold_au_official_calendar.load_calendar_receipt", return_value=self.calendar):
            return self.reader(CONTRACT, NOW)

    def test_completed_history_binds_calendar_rawbytes_and_contract(self):
        result = self.read()
        self.assertEqual(len(result["bars"]), 11)
        self.assertEqual(result["last_completed_session_date"], self.days[-1])
        self.assertEqual(result["next_session_date"], "2026-09-28")
        self.assertTrue(result["verified_session_calendar"])

    def test_future_obtained_snapshot_rejected(self):
        self.snapshots[0]["obtained_at"] = (NOW+timedelta(seconds=1)).isoformat()
        self.snapshots[0]["available_at"] = self.snapshots[0]["obtained_at"]
        with self.assertRaisesRegex(PaperDenied, "NOT_COMPLETED_OR_FUTURE"):
            self.read()

    def test_raw_hash_tamper_rejected(self):
        self.snapshots[0]["raw_bytes"] += b" "
        with self.assertRaisesRegex(PaperDenied, "RAW_HASH_MISMATCH"):
            self.read()

    def test_wrong_embedded_date_even_correct_hash_rejected(self):
        payload = json.loads(self.snapshots[0]["raw_bytes"])
        payload["report_date"] = "20260928"
        self.snapshots[0]["raw_bytes"] = canonical(payload)
        self.snapshots[0]["raw_sha256"] = "sha256:"+hashlib.sha256(self.snapshots[0]["raw_bytes"]).hexdigest()
        with self.assertRaisesRegex(PaperDenied, "RAW_DATE_MISMATCH"):
            self.read()

    def test_source_domain_and_missing_session_rejected(self):
        self.snapshots[0]["source_url"] = "https://unverified.invalid/fake.dat"
        with self.assertRaisesRegex(PaperDenied, "URL_MISMATCH"):
            self.read()
        self.snapshots = self.snapshots[:-1]
        with self.assertRaisesRegex(PaperDenied, "INCOMPLETE"):
            self.read()


if __name__ == "__main__":
    unittest.main()
