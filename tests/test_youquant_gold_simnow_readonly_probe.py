"""Offline fake-host tests for the single-editor broker readback probe."""

from datetime import datetime, timedelta, timezone
import ast
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from scripts import youquant_gold_simnow_readonly_probe as probe


NOW = datetime(2026, 9, 29, 1, 2, 3, tzinfo=timezone.utc)
FAKE_ACCOUNT_MARKER = "SIMNOW-PRIVATE-ACCOUNT-476183"
SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "youquant_gold_simnow_readonly_probe.py"


class FakeExchange:
    def __init__(self):
        self.calls = []
        self.connected = True
        self.meta = {"InstrumentID": "au2612", "ExchangeID": "SHFE",
                     "VolumeMultiple": 1000, "PriceTick": 0.02,
                     "DeliveryYear": 2026, "DeliveryMonth": 12, "IsTrading": 1}
        self.account = {"Info": {"InvestorID": FAKE_ACCOUNT_MARKER, "BrokerID": "9999"},
                        "Balance": 4800000, "Equity": 5000000}
        self.positions = [{"ContractType": "au2612", "Type": 1,
                           "Amount": 1, "Margin": 200000}]
        self.orders = [{"Id": "PRIVATE-ORDER-184219"}]
        self.ticker = {"Buy": 999.98, "Last": 1000.0,
                       "Time": int(NOW.timestamp() * 1000) - 5000}

    def IO(self, name):
        self.calls.append("IO")
        if name != "status":
            raise AssertionError("unexpected IO action")
        return self.connected

    def SetContractType(self, contract):
        self.calls.append("SetContractType")
        if contract != "au2612":
            raise AssertionError("unexpected contract")
        return self.meta

    def GetAccount(self):
        self.calls.append("GetAccount")
        return self.account

    def GetPositions(self):
        self.calls.append("GetPositions")
        return self.positions

    def GetOrders(self):
        self.calls.append("GetOrders")
        return self.orders

    def GetTicker(self):
        self.calls.append("GetTicker")
        return self.ticker

    def Buy(self, *args):
        raise AssertionError("read-only probe attempted Buy")

    def Sell(self, *args):
        raise AssertionError("read-only probe attempted Sell")

    def CancelOrder(self, *args):
        raise AssertionError("read-only probe attempted CancelOrder")

    def SetDirection(self, *args):
        raise AssertionError("read-only probe attempted SetDirection")


class FakeClock:
    def __init__(self):
        self.seconds = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.seconds

    def sleep(self, milliseconds):
        self.sleeps.append(milliseconds)
        self.seconds += milliseconds / 1000


class ReadonlyProbeTests(unittest.TestCase):
    def test_single_editor_source_loads_without_host_calls_then_reads_six_methods_once(self):
        host = FakeExchange()
        logs = []
        namespace = {"__name__": "__main__", "exchange": host,
                     "Log": lambda *parts: logs.append(parts),
                     "GetCommand": lambda: self.fail("command polled"),
                     "_G": lambda *args: self.fail("persistent storage touched")}
        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("yuanli_invest", source)
        exec(compile(source, str(SOURCE), "exec"), namespace)
        self.assertEqual(host.calls, [])
        with patch.dict(namespace, {"inspect_host": lambda globals_arg:
                         probe.inspect_host(globals_arg, now=NOW)}):
            result = namespace["main"]()
        self.assertEqual(host.calls, list(probe.READ_ONLY_METHODS))
        self.assertEqual(result["status"], "HOST_READBACK_OBSERVED_UNATTESTED")
        self.assertEqual(result["position_count"], 1)
        self.assertEqual(result["open_order_count"], 1)
        self.assertEqual(result["quote_age_ms"], 5000)
        self.assertEqual(result["order_api_calls"], 0)
        self.assertFalse(result["simnow_first_normal_attested"])
        self.assertFalse(result["paper_authority_enabled"])
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][0], "GOLD2_SIMNOW_READ_ONLY_HOST_PROBE")
        self.assertEqual(json.loads(logs[0][1]), result)
        self.assertNotIn(FAKE_ACCOUNT_MARKER, logs[0][1])
        self.assertNotIn("PRIVATE-ORDER-184219", logs[0][1])
        self.assertRegex(result["selected_readback_sha256"], r"^sha256:[0-9a-f]{64}$")

    def test_python_39_diagnosis_does_not_change_production_version_gate(self):
        host = FakeExchange()
        with patch.object(probe.sys, "version_info", (3, 9, 2)):
            result = probe.inspect_host({"exchange": host}, now=NOW)
        self.assertEqual(result["status"], "HOST_READBACK_OBSERVED_UNATTESTED")
        self.assertEqual(result["python_version"], "3.9.2")
        self.assertEqual(result["production_python_minimum"], "3.12")
        self.assertTrue(result["probe_python_supported"])
        self.assertFalse(result["python_supported"])
        self.assertFalse(result["paper_authority_enabled"])
        self.assertEqual(host.calls, list(probe.READ_ONLY_METHODS))

    def test_waits_for_ctp_connection_before_any_other_broker_read(self):
        host = FakeExchange()
        host.connected = False
        clock = FakeClock()

        def sleep(milliseconds):
            clock.sleep(milliseconds)
            if clock.seconds >= 2:
                host.connected = True

        result = probe.inspect_host({"exchange": host, "Sleep": sleep},
                                    now=NOW, monotonic=clock.monotonic)
        self.assertEqual(result["status"], "HOST_READBACK_OBSERVED_UNATTESTED")
        self.assertEqual(result["connection_checks"], 3)
        self.assertEqual(result["connection_wait_ms"], 2000)
        self.assertEqual(clock.sleeps, [1000, 1000])
        self.assertEqual(host.calls, ["IO", "IO", "IO"] +
                         list(probe.READ_ONLY_METHODS[1:]))
        self.assertEqual(result["attempted_query_methods"],
                         list(probe.READ_ONLY_METHODS))

    def test_ctp_timeout_is_bounded_and_does_not_query_or_log_private_values(self):
        host = FakeExchange()
        host.connected = False
        clock = FakeClock()
        result = probe.inspect_host({"exchange": host, "Sleep": clock.sleep},
                                    now=NOW, monotonic=clock.monotonic)
        self.assertEqual(result["reason_code"], "EXCHANGE_NOT_CONNECTED_TIMEOUT")
        self.assertEqual(result["status"], "HOST_READBACK_BLOCKED")
        self.assertEqual(result["stage"], "connection")
        self.assertEqual(result["connection_checks"], 31)
        self.assertEqual(result["connection_wait_ms"], 30000)
        self.assertEqual(clock.sleeps, [1000] * 30)
        self.assertEqual(host.calls, ["IO"] * 31)
        self.assertEqual(result["order_api_calls"], 0)
        self.assertNotIn(FAKE_ACCOUNT_MARKER, json.dumps(result))

        host = FakeExchange()
        host.connected = False
        result = probe.inspect_host({"exchange": host}, now=NOW)
        self.assertEqual(result["reason_code"], "HOST_SLEEP_UNAVAILABLE")
        self.assertEqual(host.calls, ["IO"])

    def test_unsupported_probe_python_or_invalid_contract_does_not_touch_host(self):
        host = FakeExchange()
        with patch.object(probe.sys, "version_info", (3, 8, 19)):
            result = probe.inspect_host({"exchange": host}, now=NOW)
        self.assertEqual(result["reason_code"], "PROBE_PYTHON_VERSION_UNSUPPORTED")
        self.assertEqual(host.calls, [])
        missing = probe.inspect_host({"exchange": False}, now=NOW)
        self.assertEqual(missing["reason_code"], "EXCHANGE_MISSING")
        self.assertEqual(missing["attempted_query_methods"], [])
        for contract in ("au888", "AU2612", "au2610", "au26xx"):
            with self.subTest(contract=contract):
                result = probe.inspect_host({"exchange": host}, contract=contract, now=NOW)
                self.assertEqual(result["reason_code"], "CONTRACT_NOT_ELIGIBLE_DATED_AU")
                self.assertEqual(host.calls, [])

    def test_metadata_or_account_identity_failure_stops_before_more_queries(self):
        host = FakeExchange()
        host.meta["VolumeMultiple"] = 10
        result = probe.inspect_host({"exchange": host}, now=NOW)
        self.assertEqual(result["reason_code"], "CONTRACT_SPEC_MISMATCH")
        self.assertEqual(host.calls, ["IO", "SetContractType"])
        host = FakeExchange()
        host.account["Info"]["BrokerID"] = "6020"
        result = probe.inspect_host({"exchange": host}, now=NOW)
        self.assertEqual(result["reason_code"], "SIMNOW_BROKER_ID_NOT_OBSERVED")
        self.assertEqual(host.calls, ["IO", "SetContractType", "GetAccount"])
        self.assertNotIn("6020", json.dumps(result))

    def test_failed_or_stale_readbacks_fail_closed_and_redact_provider_exception(self):
        host = FakeExchange()
        host.positions = None
        result = probe.inspect_host({"exchange": host}, now=NOW)
        self.assertEqual(result["reason_code"], "POSITIONS_UNREADABLE")
        self.assertEqual(host.calls[-1], "GetPositions")
        host = FakeExchange()
        host.orders = [{"Status": 0}]
        result = probe.inspect_host({"exchange": host}, now=NOW)
        self.assertEqual(result["reason_code"], "ORDER_ID_UNOBSERVABLE")
        self.assertEqual(host.calls[-1], "GetOrders")
        host = FakeExchange()
        host.ticker["Time"] = int((NOW - timedelta(seconds=16)).timestamp() * 1000)
        result = probe.inspect_host({"exchange": host}, now=NOW)
        self.assertEqual(result["reason_code"], "QUOTE_STALE_OR_FUTURE")
        self.assertEqual(host.calls, list(probe.READ_ONLY_METHODS))
        host = FakeExchange()
        def private_exception():
            raise RuntimeError("broker returned " + FAKE_ACCOUNT_MARKER)
        host.GetOrders = private_exception
        result = probe.inspect_host({"exchange": host}, now=NOW)
        self.assertEqual(result["reason_code"], "HOST_QUERY_EXCEPTION")
        self.assertNotIn(FAKE_ACCOUNT_MARKER, json.dumps(result))

    def test_only_documented_read_only_exchange_methods_appear_in_source_calls(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        methods = {node.func.attr for node in ast.walk(tree)
                   if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                   and isinstance(node.func.value, ast.Name)
                   and node.func.value.id == "exchange"}
        self.assertEqual(methods, set(probe.READ_ONLY_METHODS))
        forbidden = {"Buy", "Sell", "CancelOrder", "SetDirection", "GetCommand",
                     "CommandRobot", "_G"}
        self.assertFalse(methods & forbidden)


if __name__ == "__main__":
    unittest.main()
