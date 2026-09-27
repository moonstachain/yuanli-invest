"""Offline validation of untrusted read-only CTP cost candidate contents.

These receipt hashes prove internal consistency only, not broker authenticity.
This module never creates the formal runtime's executable cost receipt.
Assessor duplicates the audited standalone host probe so that neither host
runtime nor network is loaded by importing this module; parity is tested.
"""
from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
SCHEMA = "gold2-au-ctp-readonly-cost-candidate.v1"

METHODS = ("ReqQryInstrumentMarginRate", "ReqQryInstrumentCommissionRate",
           "ReqQryBrokerTradingParams", "ReqQryDepthMarketData")

FIELDS = {
    METHODS[0]: ("InvestorRange", "BrokerID", "InvestorID", "HedgeFlag",
                 "LongMarginRatioByMoney", "LongMarginRatioByVolume",
                 "ShortMarginRatioByMoney", "ShortMarginRatioByVolume",
                 "IsRelative", "ExchangeID", "InvestUnitID", "InstrumentID"),
    METHODS[1]: ("InvestorRange", "BrokerID", "InvestorID", "OpenRatioByMoney",
                 "OpenRatioByVolume", "CloseRatioByMoney", "CloseRatioByVolume",
                 "CloseTodayRatioByMoney", "CloseTodayRatioByVolume", "ExchangeID",
                 "BizType", "InvestUnitID", "InstrumentID"),
    METHODS[2]: ("BrokerID", "InvestorID", "MarginPriceType", "Algorithm",
                 "AvailIncludeCloseProfit", "CurrencyID", "OptionRoyaltyPriceType",
                 "AccountID"),
    METHODS[3]: ("TradingDay", "ExchangeID", "InstrumentID", "ActionDay",
                 "LastPrice", "PreSettlementPrice", "OpenPrice", "SettlementPrice",
                 "AveragePrice", "UpperLimitPrice", "LowerLimitPrice",
                 "UpdateTime", "UpdateMillisec", "BidPrice1", "AskPrice1"),
}

STRUCTS = dict(zip(METHODS, ("CThostFtdcInstrumentMarginRateField",
    "CThostFtdcInstrumentCommissionRateField", "CThostFtdcBrokerTradingParamsField",
    "CThostFtdcDepthMarketDataField")))

class ProbeBlocked(ValueError):
    pass

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")

def digest(value):
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()

def number(value, positive=False, signed=False):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ProbeBlocked("INVALID_NUMBER")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ProbeBlocked("INVALID_NUMBER")
    if (not parsed.is_finite() or abs(parsed) > Decimal("1e20")
            or (positive and parsed <= 0) or (not signed and parsed < 0)):
        raise ProbeBlocked("INVALID_NUMBER")
    return str(parsed)

def _rows(query, method):
    if query["response_sha256"] != digest(query["decoded_redacted_response"]):
        raise ProbeBlocked("NATIVE_RESPONSE_HASH_MISMATCH")
    rows = []
    for packet in query["decoded_redacted_response"]:
        for item in packet:
            if item["Name"] == "CThostFtdcRspInfoField":
                if type(item["Value"].get("ErrorID")) is not int or item["Value"]["ErrorID"] != 0:
                    raise ProbeBlocked("NATIVE_QUERY_ERROR")
            elif item["Name"] == STRUCTS[method]:
                rows.append(item["Value"])
            else:
                raise ProbeBlocked("UNEXPECTED_NATIVE_STRUCT")
    return rows

def assess_cost_evidence(queries, account_token, contract):
    """Recompute from response projections; never promote them to a live cost receipt."""
    result = {"account_specific_absolute_margin_rate_observed": False,
              "account_specific_commission_rate_observed": False,
              "margin_price_type": None, "rates": {}, "gaps": [],
              "exact_order_margin_proven": False,
              "round_trip_fee_upper_proven": False}
    for method in METHODS:
        query = queries.get(method)
        if not isinstance(query, Mapping):
            result["gaps"].append(method + ":MISSING_RESPONSE")
            continue
        try:
            rows = _rows(query, method)
            if len(rows) != 1:
                raise ProbeBlocked("EXPECTED_SINGLE_RESPONSE_ROW")
            row = rows[0]
            if method == METHODS[3]:
                if row.get("InstrumentID") != contract or row.get("ExchangeID") != "SHFE":
                    raise ProbeBlocked("CONTRACT_IDENTITY_MISMATCH")
                continue
            if row.get("BrokerID") != "9999" or row.get("InvestorID") != account_token:
                raise ProbeBlocked("ACCOUNT_RATE_IDENTITY_UNPROVEN")
            if method == METHODS[2]:
                if row.get("CurrencyID") != "CNY" or str(row.get("MarginPriceType")) not in ("1", "2", "3", "4"):
                    raise ProbeBlocked("MARGIN_PRICE_BASIS_UNPROVEN")
                result["margin_price_type"] = str(row["MarginPriceType"])
                continue
            if (str(row.get("InvestorRange")) != "3" or row.get("InstrumentID") != contract
                    or row.get("ExchangeID") != "SHFE"):
                raise ProbeBlocked("ACCOUNT_CONTRACT_SPECIFIC_RATE_UNPROVEN")
            if method == METHODS[0]:
                if str(row.get("HedgeFlag")) != "1" or row.get("IsRelative") not in (0, False):
                    raise ProbeBlocked("ABSOLUTE_SPECULATIVE_MARGIN_UNPROVEN")
                keys = ("LongMarginRatioByMoney", "LongMarginRatioByVolume",
                        "ShortMarginRatioByMoney", "ShortMarginRatioByVolume")
                result["rates"]["margin"] = {key: number(row.get(key)) for key in keys}
                result["account_specific_absolute_margin_rate_observed"] = True
            else:
                if str(row.get("BizType")) != "1":
                    raise ProbeBlocked("FUTURES_COMMISSION_BUSINESS_UNPROVEN")
                keys = ("OpenRatioByMoney", "OpenRatioByVolume", "CloseRatioByMoney",
                        "CloseRatioByVolume", "CloseTodayRatioByMoney", "CloseTodayRatioByVolume")
                result["rates"]["commission"] = {key: number(row.get(key)) for key in keys}
                result["account_specific_commission_rate_observed"] = True
        except (ProbeBlocked, KeyError, TypeError, ValueError):
            result["gaps"].append(method + ":RESPONSE_NOT_SUFFICIENT")
    result["gaps"].extend(("EXTERNAL_ACCOUNT_AND_FIRST_NORMAL_ROBOT_BINDING_NOT_ATTESTED",
        "ORDER_MARGIN_PRICE_AND_ADDITIONAL_FREEZE_POLICY_NOT_PROVEN",
        "FUTURE_CLOSE_PRICE_AND_ACCOUNT_FEE_UPPER_NOT_PROVEN",
        "NATIVE_QUERY_PER_CALL_TIMEOUT_NOT_DOCUMENTED"))
    return result


def _timestamp(value):
    if not isinstance(value, str):
        raise ProbeBlocked("TIMESTAMP_INVALID")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise ProbeBlocked("TIMESTAMP_INVALID")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ProbeBlocked("TIMESTAMP_INVALID")
    return parsed


def validate_candidate(receipt, *, as_of, expected_investor_token=None):
    """Validate consistency and timing; explicitly retain external-attestation gaps."""
    if not isinstance(receipt, dict) or receipt.get("schema_version") != SCHEMA:
        raise ProbeBlocked("CANDIDATE_SCHEMA_INVALID")
    expected_fields = {"schema_version", "status", "reason_code", "observed_at", "available_at",
        "contract", "calendar_source", "window_start", "window_end", "order_api_calls",
        "paper_authority_enabled", "simnow_first_normal_attested", "robot_binding_attested",
        "account_identity_attested", "connection_checks", "connection_wait_ms", "native_queries",
        "quote_clock", "full_terminal_order_history_observed", "contract_metadata", "account",
        "positions", "pending_orders", "quote", "quote_observed_at", "cost_assessment", "receipt_sha256"}
    if set(receipt) != expected_fields:
        raise ProbeBlocked("CANDIDATE_FIELDS_INVALID")
    if receipt.get("status") != "READBACK_OBSERVED_UNATTESTED" or receipt.get("reason_code") != "NONE":
        raise ProbeBlocked("SUCCESSFUL_READBACK_REQUIRED")
    for name in ("paper_authority_enabled", "simnow_first_normal_attested", "robot_binding_attested",
                 "account_identity_attested", "full_terminal_order_history_observed"):
        if receipt.get(name) is not False:
            raise ProbeBlocked("AUTHORITY_OR_ATTESTATION_FORBIDDEN")
    if type(receipt.get("order_api_calls")) is not int or receipt["order_api_calls"] != 0:
        raise ProbeBlocked("ORDER_API_CALLS_FORBIDDEN")
    if (receipt.get("calendar_source") != "https://www.shfe.com.cn/publicnotice/notice/202512/t20251217_829805.html"
            or receipt.get("quote_clock") != "PROVIDER_TICKER_TIME"):
        raise ProbeBlocked("OBSERVATION_SOURCE_INVALID")
    checks, wait_ms = receipt.get("connection_checks"), receipt.get("connection_wait_ms")
    if (type(checks) is not int or not 1 <= checks <= 31 or type(wait_ms) is not int
            or not 0 <= wait_ms <= 30000 or wait_ms > (checks - 1) * 1000
            or (checks > 1 and wait_ms <= 0)):
        raise ProbeBlocked("CONNECTION_COUNTERS_INVALID")
    unsigned = dict(receipt)
    reported_hash = unsigned.pop("receipt_sha256", None)
    if reported_hash != digest(unsigned):
        raise ProbeBlocked("CANDIDATE_HASH_MISMATCH")
    cutoff = _timestamp(as_of) if isinstance(as_of, str) else as_of
    if not isinstance(cutoff, datetime) or cutoff.tzinfo is None:
        raise ProbeBlocked("AS_OF_INVALID")
    observed, available = _timestamp(receipt.get("observed_at")), _timestamp(receipt.get("available_at"))
    start, end = _timestamp(receipt.get("window_start")), _timestamp(receipt.get("window_end"))
    if (start.isoformat() != "2026-09-28T09:15:00+08:00" or end.isoformat() != "2026-09-28T09:20:00+08:00"
            or not start <= observed < end or not observed <= available <= end or available > cutoff):
        raise ProbeBlocked("CANDIDATE_TIME_NOT_AVAILABLE")
    contract = receipt.get("contract")
    if contract != "au2612":
        raise ProbeBlocked("ACCEPTANCE_CONTRACT_MISMATCH")
    account = receipt.get("account")
    if (not isinstance(account, dict) or account.get("broker_id") != "9999" or
            set(account) != {"investor_token", "broker_id", "available_cash_cny", "equity_cny", "frozen_cash_cny"}):
        raise ProbeBlocked("ACCOUNT_UNREADABLE")
    investor = account.get("investor_token")
    if not isinstance(investor, str) or not re.fullmatch(r"hmac-sha256:[0-9a-f]{64}", investor):
        raise ProbeBlocked("REDACTED_IDENTITY_INVALID")
    if expected_investor_token is not None and investor != expected_investor_token:
        raise ProbeBlocked("EXPECTED_ACCOUNT_TOKEN_MISMATCH")
    number(account.get("available_cash_cny"))
    number(account.get("equity_cny"), positive=True)
    number(account.get("frozen_cash_cny"))
    for key in ("positions", "pending_orders"):
        rows = receipt.get(key)
        if not isinstance(rows, list) or len(rows) > 100:
            raise ProbeBlocked("POSITIONS_OR_ORDERS_INVALID")
        for row in rows:
            if not isinstance(row, dict):
                raise ProbeBlocked("POSITIONS_OR_ORDERS_INVALID")
            if key == "positions":
                if (set(row) != {"contract", "type", "amount", "margin_cny"} or not isinstance(row["contract"], str)
                        or len(row["contract"]) > 32 or type(row["type"]) is not int):
                    raise ProbeBlocked("POSITION_INVALID")
                amount = Decimal(number(row["amount"], positive=True))
                if amount != amount.to_integral_value():
                    raise ProbeBlocked("POSITION_INVALID")
                number(row["margin_cny"])
            else:
                if (set(row) != {"order_token", "price", "amount", "deal_amount"}
                        or not isinstance(row["order_token"], str)
                        or not re.fullmatch(r"hmac-sha256:[0-9a-f]{64}", row["order_token"])):
                    raise ProbeBlocked("ORDER_INVALID")
                number(row["price"])
                amount = Decimal(number(row["amount"], positive=True))
                dealt = Decimal(number(row["deal_amount"]))
                if amount != amount.to_integral_value() or dealt != dealt.to_integral_value() or dealt > amount:
                    raise ProbeBlocked("PENDING_ORDER_QUANTITY_INVALID")
    meta = receipt.get("contract_metadata")
    if not isinstance(meta, dict) or meta.get("InstrumentID") != contract or meta.get("ExchangeID") != "SHFE":
        raise ProbeBlocked("METADATA_IDENTITY_INVALID")
    if (Decimal(number(meta.get("VolumeMultiple"))) != 1000 or Decimal(number(meta.get("PriceTick"))) != Decimal("0.02")
            or meta.get("DeliveryYear") != 2026 or meta.get("DeliveryMonth") != 12 or meta.get("IsTrading") not in (1, True)):
        raise ProbeBlocked("METADATA_SPEC_INVALID")
    quote = receipt.get("quote")
    if not isinstance(quote, dict) or type(quote.get("time_ms")) is not int:
        raise ProbeBlocked("QUOTE_UNREADABLE")
    for key in ("bid", "ask", "last"):
        number(quote.get(key), positive=True)
    if Decimal(quote["bid"]) > Decimal(quote["ask"]):
        raise ProbeBlocked("CROSSED_POSITIVE_QUOTE_INVALID")
    quote_observed = _timestamp(receipt.get("quote_observed_at"))
    if (not observed <= quote_observed <= available
            or not 0 <= int(quote_observed.timestamp() * 1000) - quote["time_ms"] <= 15000
            or not 0 <= int(available.timestamp() * 1000) - quote["time_ms"] <= 120000):
        # Receipt may include subsequent slow native queries. This bound is a
        # content check, not permission to use the quote as a new live order.
        raise ProbeBlocked("CANDIDATE_QUOTE_TOO_OLD")
    queries = receipt.get("native_queries")
    if not isinstance(queries, dict) or set(queries) != set(METHODS):
        raise ProbeBlocked("NATIVE_QUERIES_INCOMPLETE")
    for method, query in queries.items():
        if not isinstance(query, dict):
            raise ProbeBlocked("NATIVE_QUERY_SHAPE")
        if "query_error" in query:
            if query != {"query_error": "NATIVE_QUERY_FAILED_OR_UNREADABLE"}:
                raise ProbeBlocked("NATIVE_ERROR_SHAPE")
            continue
        if set(query) != {"request", "observed_at", "decoded_redacted_response", "response_sha256", "hash_semantics"}:
            raise ProbeBlocked("NATIVE_QUERY_FIELDS_INVALID")
        if query.get("hash_semantics") != "DECODED_REDACTED_CANONICAL_JSON_NOT_WIRE_BYTES":
            raise ProbeBlocked("NATIVE_HASH_SEMANTICS_INVALID")
        if not observed <= _timestamp(query.get("observed_at")) <= available:
            raise ProbeBlocked("NATIVE_QUERY_TIME_INVALID")
        response = query.get("decoded_redacted_response")
        if not isinstance(response, list) or len(response) > 100:
            raise ProbeBlocked("NATIVE_RESPONSE_SHAPE")
        for packet in response:
            if not isinstance(packet, list) or len(packet) > 20:
                raise ProbeBlocked("NATIVE_RESPONSE_SHAPE")
            for entry in packet:
                if not isinstance(entry, dict) or set(entry) != {"Name", "Value"} or not isinstance(entry["Value"], dict):
                    raise ProbeBlocked("NATIVE_RESPONSE_SHAPE")
                name = entry["Name"]
                allowed = ("ErrorID",) if name == "CThostFtdcRspInfoField" else FIELDS[method] if name == STRUCTS[method] else ()
                if not allowed or not set(entry["Value"]) <= set(allowed):
                    raise ProbeBlocked("NATIVE_RESPONSE_FIELDS_INVALID")
                for key, value in entry["Value"].items():
                    if key in ("InvestorID", "AccountID", "InvestUnitID") and value != "" and not (isinstance(value, str) and re.fullmatch(r"hmac-sha256:[0-9a-f]{64}", value)):
                        raise ProbeBlocked("UNREDACTED_IDENTITY_FORBIDDEN")
        if query.get("response_sha256") != digest(response):
            raise ProbeBlocked("NATIVE_RESPONSE_HASH_MISMATCH")
        request = query.get("request")
        if not isinstance(request, dict) or (method != METHODS[3] and request.get("InvestorID") != investor):
            raise ProbeBlocked("NATIVE_REQUEST_IDENTITY_INVALID")
        expected_request = {"InstrumentID": contract, "ExchangeID": "SHFE"}
        if method != METHODS[3]:
            expected_request.update({"BrokerID": "9999", "InvestorID": investor})
        if method == METHODS[0]:
            expected_request["HedgeFlag"] = "1"
        if method == METHODS[2]:
            expected_request = {"BrokerID": "9999", "InvestorID": investor, "CurrencyID": "CNY"}
        if request != expected_request:
            raise ProbeBlocked("NATIVE_REQUEST_FIELDS_INVALID")
    recomputed = assess_cost_evidence(queries, investor, contract)
    if receipt.get("cost_assessment") != recomputed:
        raise ProbeBlocked("COST_ASSESSMENT_MISMATCH")
    return {"schema_version": "gold2-au-ctp-cost-content-validation.v1",
            "receipt_sha256": reported_hash, "content_consistent": True,
            "external_authenticity_verified": False, "paper_authority_enabled": False,
            "available_at": available.isoformat(), "account_token": investor,
            "cost_assessment": recomputed}


def load_candidate(path, *, as_of, expected_investor_token=None):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ProbeBlocked("SYMLINK_PATH_FORBIDDEN")
    with path.open("rb") as stream:
        raw = stream.read(262145)
    if len(raw) > 262144:
        raise ProbeBlocked("CANDIDATE_TOO_LARGE")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ProbeBlocked("DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    def invalid_constant(value):
        raise ProbeBlocked("NONFINITE_JSON")
    try:
        receipt = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProbeBlocked("CANDIDATE_JSON_INVALID")
    return receipt, validate_candidate(receipt, as_of=as_of, expected_investor_token=expected_investor_token)
