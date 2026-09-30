"""No network: native response proof boundaries, once-only operation and redaction."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import ast
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts import youquant_gold_simnow_readonly_cost_probe as probe
from scripts import gold_au_ctp_cost_evidence_import as importer
from yuanli_invest.gold_au_ctp_cost_evidence import (
    FROZEN_WINDOWS, ProbeBlocked, load_candidate, validate_candidate,
)

NOW = datetime(2026, 9, 28, 1, 15, 5, tzinfo=timezone.utc)
ACCOUNT = "PRIVATE_ACCOUNT_472913"
SALT = "74" * 32


class Exchange:
    def __init__(self):
        self.calls = []
        self.connected = True
        base = {"BrokerID": "9999", "InvestorID": ACCOUNT, "InvestorRange": "3",
                "InstrumentID": "au2612", "ExchangeID": "SHFE"}
        margin = dict(base, HedgeFlag="1", LongMarginRatioByMoney=0.2, LongMarginRatioByVolume=0,
                      ShortMarginRatioByMoney=0.2, ShortMarginRatioByVolume=0, IsRelative=0)
        commission = dict(base, BizType="1", OpenRatioByMoney=0, OpenRatioByVolume=10,
                          CloseRatioByMoney=0, CloseRatioByVolume=10,
                          CloseTodayRatioByMoney=0, CloseTodayRatioByVolume=0)
        params = {"BrokerID": "9999", "InvestorID": ACCOUNT, "CurrencyID": "CNY", "MarginPriceType": "1"}
        depth = {"InstrumentID": "au2612", "ExchangeID": "SHFE", "TradingDay": "20260928",
                 "PreSettlementPrice": 1000, "UpdateTime": "09:15:00", "UpdateMillisec": 0}
        self.rows = dict(zip(probe.METHODS, (margin, commission, params, depth)))

    def IO(self, *args):
        self.calls.append(args)
        if args == ("status",):
            return self.connected
        if args == ("mode", 0):
            return True
        if args[0] != "api" or args[1] not in probe.METHODS:
            raise AssertionError("nonallowlisted IO operation")
        method = args[1]
        if method != probe.METHODS[3]:
            assert args[2]["InvestorID"] == ACCOUNT
        return [[{"Name": probe.STRUCTS[method], "Value": self.rows[method]},
                 {"Name": "CThostFtdcRspInfoField", "Value": {"ErrorID": 0, "ErrorMsg": "PRIVATE_ERROR_TEXT"}}]]

    def SetContractType(self, contract):
        self.calls.append(("SetContractType", contract))
        return {"InstrumentID": contract, "ExchangeID": "SHFE", "VolumeMultiple": 1000,
                "PriceTick": 0.02, "DeliveryYear": 2026, "DeliveryMonth": 12, "IsTrading": 1,
                "LongMarginRatio": 0.01}

    def GetAccount(self):
        self.calls.append(("GetAccount",))
        return {"Info": {"InvestorID": ACCOUNT, "BrokerID": "9999", "Password": "PRIVATE_PASSWORD"},
                "Balance": 5000000, "Equity": 5000000, "FrozenBalance": 0}

    def GetPositions(self):
        self.calls.append(("GetPositions",))
        return [{"ContractType": "au2612", "Type": 1, "Amount": 1, "Margin": 200000}]

    def GetOrders(self):
        self.calls.append(("GetOrders",))
        return [{"Id": "PRIVATE_ORDER_7782", "Price": 999, "Amount": 1, "DealAmount": 0}]

    def GetTicker(self):
        self.calls.append(("GetTicker",))
        return {"Buy": 1000, "Sell": 1000.02, "Last": 1000, "Time": int(NOW.timestamp() * 1000) - 5000}

    def __getattr__(self, name):
        if name in ("Buy", "Sell", "CancelOrder", "SetDirection"):
            raise AssertionError("trading API accessed")
        raise AttributeError(name)


def host(exchange=None):
    values = {}
    def kv(key, *args):
        if args:
            values[key] = args[0]
        return values.get(key)
    return {"exchange": exchange or Exchange(), "_G": kv, "Sleep": lambda ms: None,
            "GOLD2_PROBE_IDENTITY_SALT": SALT}


def shifted_to_reviewed_29th(original):
    """A synthetic receipt tests the importer contract, never a live readback."""
    result = deepcopy(original)
    one_day = timedelta(days=1)
    for key in ("observed_at", "available_at", "quote_observed_at"):
        result[key] = (datetime.fromisoformat(result[key]) + one_day).isoformat()
    for query in result["native_queries"].values():
        if "observed_at" in query:
            query["observed_at"] = (datetime.fromisoformat(query["observed_at"]) + one_day).isoformat()
    result["quote"]["time_ms"] += 86400000
    result["window_start"], result["window_end"], result["calendar_source"] = FROZEN_WINDOWS["2026-09-29"]
    result["native_queries"][probe.METHODS[3]]["decoded_redacted_response"][0][0]["Value"]["TradingDay"] = "20260929"
    depth = result["native_queries"][probe.METHODS[3]]
    depth["response_sha256"] = probe.digest(depth["decoded_redacted_response"])
    result.pop("receipt_sha256")
    result["receipt_sha256"] = probe.digest(result)
    return result


class EvidenceTests(unittest.TestCase):
    def test_native_account_specific_readback_export_and_offline_parity(self):
        context = host()
        result = probe.inspect_host(context, now=NOW)
        self.assertEqual(result["status"], "READBACK_OBSERVED_UNATTESTED")
        assessment = result["cost_assessment"]
        self.assertTrue(assessment["account_specific_absolute_margin_rate_observed"])
        self.assertTrue(assessment["account_specific_commission_rate_observed"])
        self.assertFalse(assessment["exact_order_margin_proven"])
        self.assertFalse(assessment["round_trip_fee_upper_proven"])
        validated = validate_candidate(result, as_of=NOW)
        self.assertEqual(validated["cost_assessment"], assessment)
        self.assertFalse(validated["external_authenticity_verified"])
        rendered = json.dumps(result)
        for secret in (ACCOUNT, SALT, "PRIVATE_ERROR_TEXT", "PRIVATE_PASSWORD", "PRIVATE_ORDER_7782"):
            self.assertNotIn(secret, rendered)
        self.assertNotIn("LongMarginRatio", result["contract_metadata"])
        self.assertEqual(len(context["exchange"].calls), 11)
        self.assertEqual(result["order_api_calls"], 0)

    def test_holiday_and_outside_window_never_touch_exchange(self):
        for now in (datetime(2026, 9, 26, 1, 15, tzinfo=timezone.utc),
                    datetime(2026, 9, 28, 1, 20, tzinfo=timezone.utc)):
            context = host()
            result = probe.inspect_host(context, now=now)
            self.assertEqual(result["reason_code"], "OUTSIDE_APPROVED_OFFICIAL_SESSION_WINDOW")
            self.assertEqual(context["exchange"].calls, [])

    def test_once_only_marker_blocks_second_attempt(self):
        context = host()
        probe.inspect_host(context, now=NOW)
        count = len(context["exchange"].calls)
        repeated = probe.inspect_host(context, now=NOW)
        self.assertEqual(repeated["reason_code"], "ACCEPTANCE_ALREADY_ATTEMPTED")
        self.assertEqual(len(context["exchange"].calls), count)

    def test_bounded_connection_does_not_query_account_on_timeout(self):
        context = host()
        context["exchange"].connected = False
        elapsed = [0.0]
        def sleep(ms):
            elapsed[0] += ms / 1000
        context["Sleep"] = sleep
        result = probe.inspect_host(context, now=NOW, monotonic=lambda: elapsed[0])
        self.assertEqual(result["reason_code"], "CONNECTION_TIMEOUT")
        self.assertEqual(result["connection_checks"], 31)
        self.assertEqual(result["connection_wait_ms"], 30000)
        self.assertTrue(all(call == ("status",) for call in context["exchange"].calls))

    def test_generic_wrong_investor_relative_or_product_margin_cannot_prove_account_cost(self):
        for key, value in (("InvestorRange", "1"), ("InvestorID", "OTHER_ACCOUNT"),
                           ("IsRelative", 1), ("InstrumentID", "au")):
            exchange = Exchange()
            exchange.rows[probe.METHODS[0]][key] = value
            result = probe.inspect_host(host(exchange), now=NOW)
            self.assertFalse(result["cost_assessment"]["account_specific_absolute_margin_rate_observed"])
            self.assertTrue(validate_candidate(result, as_of=NOW)["content_consistent"])

    def test_failed_or_malformed_cost_response_retains_explicit_gap(self):
        exchange = Exchange()
        exchange.rows[probe.METHODS[1]]["OpenRatioByVolume"] = float("nan")
        result = probe.inspect_host(host(exchange), now=NOW)
        self.assertEqual(result["status"], "READBACK_OBSERVED_UNATTESTED")
        self.assertFalse(result["cost_assessment"]["account_specific_commission_rate_observed"])
        self.assertTrue(validate_candidate(result, as_of=NOW)["content_consistent"])

    def test_quote_and_salt_checks_fail_closed(self):
        context = host()
        context["GOLD2_PROBE_IDENTITY_SALT"] = "invalid"
        self.assertEqual(probe.inspect_host(context, now=NOW)["reason_code"], "PRIVATE_IDENTITY_SALT_INVALID")
        self.assertEqual(context["exchange"].calls, [])
        exchange = Exchange()
        exchange.GetTicker = lambda: {"Buy": 1000, "Sell": 1000, "Last": 1000, "Time": 0}
        self.assertEqual(probe.inspect_host(host(exchange), now=NOW)["reason_code"], "QUOTE_STALE_OR_FUTURE")
        self.assertFalse(any(call[0] == "api" for call in exchange.calls))

    def test_random_salt_is_created_read_back_and_never_exported_without_user_input(self):
        context = host()
        del context["GOLD2_PROBE_IDENTITY_SALT"]
        result = probe.inspect_host(context, now=NOW)
        salt = context["_G"](probe.PRIVATE_SALT_KEY)
        self.assertRegex(salt, r"^[0-9a-f]{64}$")
        self.assertNotIn(salt, json.dumps(result))
        self.assertEqual(result["account"]["investor_token"], probe.token(salt, ACCOUNT))
        self.assertEqual(probe.private_identity_salt(context, context["_G"]), salt)
        self.assertTrue(validate_candidate(result, as_of=NOW)["content_consistent"])

    def test_private_salt_write_failure_blocks_before_any_exchange_call(self):
        context = host()
        del context["GOLD2_PROBE_IDENTITY_SALT"]
        context["_G"] = lambda *args: None
        result = probe.inspect_host(context, now=NOW)
        self.assertEqual(result["reason_code"], "PRIVATE_IDENTITY_SALT_NOT_PERSISTED")
        self.assertEqual(context["exchange"].calls, [])

    def test_tamper_future_availability_authority_and_unredacted_native_identity_rejected(self):
        original = probe.inspect_host(host(), now=NOW)
        bad = deepcopy(original)
        bad["quote"]["ask"] = "1"
        with self.assertRaises(ProbeBlocked):
            validate_candidate(bad, as_of=NOW)
        with self.assertRaises(ProbeBlocked):
            validate_candidate(original, as_of=datetime(2026, 9, 28, 0, 30, tzinfo=timezone.utc))
        bad = deepcopy(original)
        bad["paper_authority_enabled"] = True
        with self.assertRaises(ProbeBlocked):
            validate_candidate(bad, as_of=NOW)
        bad = deepcopy(original)
        query = bad["native_queries"][probe.METHODS[0]]
        query["decoded_redacted_response"][0][0]["Value"]["InvestorID"] = ACCOUNT
        query["response_sha256"] = probe.digest(query["decoded_redacted_response"])
        bad.pop("receipt_sha256")
        bad["receipt_sha256"] = probe.digest(bad)
        with self.assertRaises(ProbeBlocked):
            validate_candidate(bad, as_of=NOW)

    def test_bounded_strict_file_reader_and_symlink_denial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = probe.inspect_host(host(), now=NOW)
            path = root / "candidate.json"
            path.write_text(json.dumps(result))
            receipt, validation = load_candidate(path, as_of=NOW)
            self.assertEqual(receipt, result)
            self.assertTrue(validation["content_consistent"])
            linked = root / "linked.json"
            linked.symlink_to(path)
            with self.assertRaises(ProbeBlocked):
                load_candidate(linked, as_of=NOW)
            path.write_text('{"schema_version":"x","schema_version":"y"}')
            with self.assertRaises(ProbeBlocked):
                load_candidate(path, as_of=NOW)
            path.write_bytes(b" " * 262145)
            with self.assertRaises(ProbeBlocked):
                load_candidate(path, as_of=NOW)

    def test_standalone_python39_source_has_no_order_or_command_calls(self):
        path = Path(probe.__file__)
        tree = ast.parse(path.read_text(), feature_version=(3, 9))
        forbidden = {"Buy", "Sell", "CancelOrder", "SetDirection", "GetCommand", "_C"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id if isinstance(node.func, ast.Name) else None
                self.assertNotIn(name, forbidden)
        context = {"__name__": "test_host", "exchange": Exchange()}
        exec(compile(tree, str(path), "exec"), context)
        self.assertEqual(context["exchange"].calls, [])

    def test_import_is_offline_dry_by_default_and_preserves_new_private_bundle_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            path = root / "candidate.json"
            path.write_text(json.dumps(probe.inspect_host(host(), now=NOW)))
            target = root / "accepted"
            args = [str(path), "--as-of", NOW.isoformat(), "--output-dir", str(target)]
            with redirect_stdout(io.StringIO()):
                self.assertEqual(importer.main(args), 0)
            self.assertFalse(target.exists())
            with redirect_stdout(io.StringIO()):
                self.assertEqual(importer.main(args + ["--execute"]), 0)
                self.assertEqual(importer.main(args + ["--execute"]), 2)
            self.assertEqual(set(p.name for p in target.iterdir()), {"candidate.json", "content-validation.json"})
            self.assertEqual(target.stat().st_mode & 0o777, 0o700)
            self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600 for p in target.iterdir()))

    def test_second_frozen_window_requires_explicit_selection_and_exact_source(self):
        next_day = shifted_to_reviewed_29th(probe.inspect_host(host(), now=NOW))
        next_as_of = NOW + timedelta(days=1)
        with self.assertRaisesRegex(ProbeBlocked, "OBSERVATION_SOURCE_INVALID"):
            validate_candidate(next_day, as_of=next_as_of)
        result = validate_candidate(next_day, as_of=next_as_of,
                                    expected_window="2026-09-29")
        self.assertTrue(result["content_consistent"])
        self.assertEqual(result["expected_window"], "2026-09-29")
        self.assertFalse(result["external_authenticity_verified"])
        old = probe.inspect_host(host(), now=NOW)
        self.assertEqual(validate_candidate(old, as_of=NOW)["expected_window"], "2026-09-28")
        with self.assertRaises(ProbeBlocked):
            validate_candidate(old, as_of=NOW, expected_window="2026-09-29")
        with self.assertRaisesRegex(ProbeBlocked, "FROZEN_WINDOW_UNSUPPORTED"):
            validate_candidate(next_day, as_of=next_as_of, expected_window="2026-09-30")
        for key, value in (("calendar_source", FROZEN_WINDOWS["2026-09-28"][2]),
                           ("window_start", "2026-09-29T09:14:59+08:00"),
                           ("window_end", "2026-09-29T09:20:01+08:00")):
            bad = deepcopy(next_day)
            bad[key] = value
            bad.pop("receipt_sha256")
            bad["receipt_sha256"] = probe.digest(bad)
            with self.assertRaises(ProbeBlocked):
                validate_candidate(bad, as_of=next_as_of,
                                   expected_window="2026-09-29")

    def test_importer_requires_explicit_second_window_without_writing_on_reject(self):
        next_day = shifted_to_reviewed_29th(probe.inspect_host(host(), now=NOW))
        next_as_of = (NOW + timedelta(days=1)).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            receipt = root / "synthetic-next-day.json"
            receipt.write_text(json.dumps(next_day))
            output = root / "accepted"
            args = [str(receipt), "--as-of", next_as_of, "--output-dir", str(output)]
            with redirect_stdout(io.StringIO()):
                self.assertEqual(importer.main(args + ["--execute"]), 2)
            self.assertFalse(output.exists())
            with redirect_stdout(io.StringIO()):
                self.assertEqual(importer.main(args + ["--expected-window", "2026-09-29", "--execute"]), 0)
            self.assertEqual(set(p.name for p in output.iterdir()),
                             {"candidate.json", "content-validation.json"})
            validation = json.loads((output / "content-validation.json").read_text())
            self.assertEqual(validation["expected_window"], "2026-09-29")
            self.assertFalse(validation["external_authenticity_verified"])

    def test_even_rehashed_assessment_cannot_claim_exact_order_cost_or_authority(self):
        result = probe.inspect_host(host(), now=NOW)
        result["cost_assessment"]["exact_order_margin_proven"] = True
        result.pop("receipt_sha256")
        result["receipt_sha256"] = probe.digest(result)
        with self.assertRaises(ProbeBlocked):
            validate_candidate(result, as_of=NOW)

    def test_same_decoded_input_assessor_implementation_is_identical(self):
        # Changes to the separately deployable file must not silently drift
        # from the offline verifier's rates/identity proof boundaries.
        from yuanli_invest import gold_au_ctp_cost_evidence as validator
        source_tree = ast.parse(Path(probe.__file__).read_text())
        validator_tree = ast.parse(Path(validator.__file__).read_text())
        for name in ("canonical", "digest", "number", "_rows", "assess_cost_evidence"):
            original = next(node for node in source_tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
            copied = next(node for node in validator_tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
            self.assertEqual(ast.dump(original, include_attributes=False), ast.dump(copied, include_attributes=False))

    def test_inflight_native_reply_after_window_stops_all_subsequent_reads(self):
        exchange = Exchange()
        current = [NOW]
        original_io = exchange.IO
        def io_call(*args):
            response = original_io(*args)
            if args[0] == "api":
                current[0] = datetime.fromisoformat(probe.WINDOW_END) + timedelta(microseconds=1)
            return response
        exchange.IO = io_call
        context = host(exchange)
        result = probe.inspect_host(context, now=NOW, clock=lambda: current[0])
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["reason_code"], "OBSERVATION_WINDOW_EXCEEDED")
        self.assertEqual([call[1] for call in exchange.calls if call[0] == "api"], [probe.METHODS[0]])
        self.assertEqual(result["native_queries"], {})
        self.assertFalse(result["paper_authority_enabled"])
        with self.assertRaises(ProbeBlocked):
            validate_candidate(result, as_of=current[0])

    def test_window_at_end_never_starts_a_new_read_and_late_account_stops_positions(self):
        for late_stage in ("ticker", "account"):
            exchange = Exchange()
            current = [NOW]
            original = exchange.GetTicker if late_stage == "ticker" else exchange.GetAccount
            def late_return():
                value = original()
                current[0] = datetime.fromisoformat(probe.WINDOW_END)
                if late_stage == "account":
                    current[0] += timedelta(microseconds=1)
                else:
                    value["Time"] = int(current[0].timestamp() * 1000) - 5000
                return value
            if late_stage == "ticker":
                exchange.GetTicker = late_return
            else:
                exchange.GetAccount = late_return
            result = probe.inspect_host(host(exchange), now=NOW, clock=lambda: current[0])
            self.assertEqual(result["reason_code"], "OBSERVATION_WINDOW_EXCEEDED")
            self.assertFalse(any(call[0] == "api" for call in exchange.calls))
            if late_stage == "account":
                self.assertFalse(any(call[0] in ("GetPositions", "GetOrders", "GetTicker") for call in exchange.calls))

    def test_rehashed_after_window_receipt_native_observation_or_future_quote_rejected(self):
        original = probe.inspect_host(host(), now=NOW)
        end = datetime.fromisoformat(probe.WINDOW_END)
        variants = []
        late = deepcopy(original)
        late["available_at"] = (end + timedelta(microseconds=1)).isoformat()
        variants.append(late)
        late_native = deepcopy(original)
        late_native["native_queries"][probe.METHODS[0]]["observed_at"] = (end + timedelta(seconds=1)).isoformat()
        variants.append(late_native)
        future_quote = deepcopy(original)
        future_quote["quote"]["time_ms"] = int(NOW.timestamp() * 1000) + 1
        variants.append(future_quote)
        for result in variants:
            result.pop("receipt_sha256")
            result["receipt_sha256"] = probe.digest(result)
            with self.assertRaises(ProbeBlocked):
                validate_candidate(result, as_of=end + timedelta(minutes=1))

    def test_crossed_quote_and_pending_quantity_are_rejected_on_host_and_offline(self):
        exchange = Exchange()
        original = exchange.GetTicker
        def crossed():
            quote = original()
            quote["Buy"] = 1001
            return quote
        exchange.GetTicker = crossed
        self.assertEqual(probe.inspect_host(host(exchange), now=NOW)["reason_code"], "CROSSED_POSITIVE_QUOTE_INVALID")
        exchange = Exchange()
        exchange.GetOrders = lambda: [{"Id": "PRIVATE_ORDER_7782", "Price": 999, "Amount": 1, "DealAmount": 2}]
        self.assertEqual(probe.inspect_host(host(exchange), now=NOW)["reason_code"], "PENDING_ORDER_QUANTITY_INVALID")
        original = probe.inspect_host(host(), now=NOW)
        crossed_receipt = deepcopy(original)
        crossed_receipt["quote"]["bid"] = "1001"
        bad_order = deepcopy(original)
        bad_order["pending_orders"][0]["deal_amount"] = "2"
        fractional_order = deepcopy(original)
        fractional_order["pending_orders"][0]["amount"] = "1.5"
        for result in (crossed_receipt, bad_order, fractional_order):
            result.pop("receipt_sha256")
            result["receipt_sha256"] = probe.digest(result)
            with self.assertRaises(ProbeBlocked):
                validate_candidate(result, as_of=NOW)

    def test_fixed_source_clock_and_counter_bounds_cannot_be_rehashed_into_valid_receipt(self):
        original = probe.inspect_host(host(), now=NOW)
        for key, value in (("calendar_source", "https://example.org/calendar"), ("quote_clock", "LOCAL_GUESS"),
                           ("connection_checks", 0), ("connection_checks", 32), ("connection_checks", True),
                           ("connection_wait_ms", -1), ("connection_wait_ms", 30001), ("connection_wait_ms", 1000)):
            result = deepcopy(original)
            result[key] = value
            result.pop("receipt_sha256")
            result["receipt_sha256"] = probe.digest(result)
            with self.assertRaises(ProbeBlocked):
                validate_candidate(result, as_of=NOW)


if __name__ == "__main__":
    unittest.main()
