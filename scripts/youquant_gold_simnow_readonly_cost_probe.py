"""Standalone Python 3.9 YouQuant CTP read-only acceptance probe.

Official IO API: https://www.youquant.com/bbs-topic/3756 and
https://www.youquant.com/syntax-guide/fun/trade/exchange.io .
Response fields/enums checked against the user's CTP 6.7.13 SDK headers.
No trading authority. No trading methods. No repository imports.
The 30-second bound is for connection polling; synchronous native queries
have no documented per-call timeout and require an external robot watchdog.
"""
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import json
import os
import re
import sys
import time

SCHEMA = "gold2-au-ctp-readonly-cost-candidate.v1"
CONTRACT = "au2612"
SHANGHAI = timezone(timedelta(hours=8))
WINDOW_START = "2026-09-28T09:15:00+08:00"
WINDOW_END = "2026-09-28T09:20:00+08:00"
# SHFE annual notice: Sep25-27 closed; Sep28 reopens. This is one approved
# observation window, not a reusable/inferred exchange calendar.
CALENDAR_SOURCE = "https://www.shfe.com.cn/publicnotice/notice/202512/t20251217_829805.html"
CLAIM_KEY = "GOLD2_CTP_READONLY_COST_ACCEPTANCE_20260928_V1"
RECEIPT_KEY = CLAIM_KEY + "_RECEIPT"
PRIVATE_SALT_KEY = "GOLD2_CTP_READONLY_PRIVATE_IDENTITY_SALT_V1"
METHODS = ("ReqQryInstrumentMarginRate", "ReqQryInstrumentCommissionRate",
           "ReqQryBrokerTradingParams", "ReqQryDepthMarketData")
IDENTITIES = ("InvestorID", "AccountID", "InvestUnitID")
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


def field(value, key):
    return value.get(key) if isinstance(value, Mapping) else getattr(value, key, None)


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


def token(salt, value):
    if value is None or value == "":
        return ""
    if isinstance(value, bool) or not isinstance(value, (str, int)) or len(str(value)) > 128:
        raise ProbeBlocked("IDENTITY_UNREADABLE")
    return "hmac-sha256:" + hmac.new(bytes.fromhex(salt), str(value).encode(), hashlib.sha256).hexdigest()


def private_identity_salt(host, kv):
    """Generate per-robot random privacy salt locally; never include it in output."""
    configured = host.get("GOLD2_PROBE_IDENTITY_SALT")
    if configured not in (None, ""):
        if not isinstance(configured, str) or not re.fullmatch(r"[0-9a-f]{64}", configured):
            raise ProbeBlocked("PRIVATE_IDENTITY_SALT_INVALID")
        return configured
    existing = kv(PRIVATE_SALT_KEY)
    if existing is None:
        generated = os.urandom(32).hex()
        kv(PRIVATE_SALT_KEY, generated)
        existing = kv(PRIVATE_SALT_KEY)
        if existing != generated:
            raise ProbeBlocked("PRIVATE_IDENTITY_SALT_NOT_PERSISTED")
    if not isinstance(existing, str) or not re.fullmatch(r"[0-9a-f]{64}", existing):
        raise ProbeBlocked("PRIVATE_IDENTITY_SALT_INVALID")
    return existing


def project_response(raw, method, salt):
    """Preserve whitelisted native response fields, redact identity, never log Info.

    This is a decoded/redacted response projection, not raw transport bytes.
    Unknown fields are intentionally omitted, including potentially sensitive
    error text. ErrorID is kept to distinguish empty/error replies.
    """
    if not isinstance(raw, (list, tuple)) or len(raw) > 100:
        raise ProbeBlocked("NATIVE_RESPONSE_SHAPE")
    result = []
    for packet in raw:
        if not isinstance(packet, (list, tuple)) or len(packet) > 20:
            raise ProbeBlocked("NATIVE_RESPONSE_SHAPE")
        projected_packet = []
        for entry in packet:
            if not isinstance(entry, Mapping) or not isinstance(entry.get("Value"), Mapping):
                raise ProbeBlocked("NATIVE_RESPONSE_SHAPE")
            name = entry.get("Name")
            if name not in (STRUCTS[method], "CThostFtdcRspInfoField"):
                raise ProbeBlocked("UNEXPECTED_NATIVE_STRUCT")
            allowed = ("ErrorID",) if name == "CThostFtdcRspInfoField" else FIELDS[method]
            selected = {}
            for key in allowed:
                if key not in entry["Value"]:
                    continue
                value = entry["Value"][key]
                if key in IDENTITIES:
                    value = token(salt, value)
                elif (value is None or isinstance(value, (str, int, float, bool))):
                    if isinstance(value, str) and len(value) > 128:
                        raise ProbeBlocked("NATIVE_FIELD_TOO_LONG")
                    canonical(value)  # reject nonfinite floats
                else:
                    raise ProbeBlocked("NATIVE_FIELD_TYPE")
                selected[key] = value
            projected_packet.append({"Name": name, "Value": selected})
        result.append(projected_packet)
    if len(canonical(result)) > 65536:
        raise ProbeBlocked("NATIVE_RESPONSE_TOO_LARGE")
    return result


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


def inspect_host(host, contract=CONTRACT, now=None, monotonic=None, clock=None):
    clock = clock or ((lambda: now) if now is not None else (lambda: datetime.now(timezone.utc)))
    now = now or clock()
    monotonic = monotonic or time.monotonic
    window_start, window_end = datetime.fromisoformat(WINDOW_START), datetime.fromisoformat(WINDOW_END)
    latest_stamp = now

    def require_window(completed=False):
        nonlocal latest_stamp
        stamp = clock()
        if not isinstance(stamp, datetime) or stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ProbeBlocked("OBSERVATION_CLOCK_INVALID")
        if stamp < latest_stamp:
            raise ProbeBlocked("OBSERVATION_CLOCK_MOVED_BACKWARDS")
        latest_stamp = stamp
        if stamp > window_end or (not completed and stamp == window_end):
            raise ProbeBlocked("OBSERVATION_WINDOW_EXCEEDED")
        if stamp < window_start:
            raise ProbeBlocked("OUTSIDE_APPROVED_OFFICIAL_SESSION_WINDOW")
        return stamp

    def read(method, *args):
        require_window()
        try:
            return method(*args)
        finally:
            # A synchronous IO(api) cannot be forcibly interrupted here. Reject
            # its late return, including an exception, before any further read.
            require_window(completed=True)

    result = {"schema_version": SCHEMA, "status": "BLOCKED", "reason_code": None,
              "observed_at": now.isoformat(), "available_at": None,
              "contract": contract, "calendar_source": CALENDAR_SOURCE,
              "window_start": WINDOW_START, "window_end": WINDOW_END,
              "order_api_calls": 0, "paper_authority_enabled": False,
              "simnow_first_normal_attested": False, "robot_binding_attested": False,
              "account_identity_attested": False, "connection_checks": 0,
              "connection_wait_ms": 0, "native_queries": {},
              "quote_clock": "PROVIDER_TICKER_TIME", "full_terminal_order_history_observed": False}
    try:
        if sys.version_info < (3, 9) or not isinstance(host, Mapping) or now.tzinfo is None:
            raise ProbeBlocked("HOST_CONTEXT_UNSUPPORTED")
        if not window_start <= now < window_end:
            raise ProbeBlocked("OUTSIDE_APPROVED_OFFICIAL_SESSION_WINDOW")
        if not re.fullmatch(r"au[0-9]{4}", contract) or not 1 <= int(contract[4:]) <= 12:
            raise ProbeBlocked("CONTRACT_INVALID")
        local = now.astimezone(SHANGHAI)
        if (2000 + int(contract[2:4])) * 12 + int(contract[4:]) < local.year * 12 + local.month + 2:
            raise ProbeBlocked("CONTRACT_TOO_NEAR_DELIVERY")
        kv = host.get("_G")
        if not callable(kv):
            raise ProbeBlocked("ONCE_ONLY_STORAGE_REQUIRED")
        if kv(CLAIM_KEY) is not None:
            raise ProbeBlocked("ACCEPTANCE_ALREADY_ATTEMPTED")
        salt = private_identity_salt(host, kv)
        kv(CLAIM_KEY, "CLAIMED")
        if kv(CLAIM_KEY) != "CLAIMED":
            raise ProbeBlocked("ONCE_ONLY_CLAIM_NOT_PERSISTED")
        exchange = host.get("exchange")
        if exchange is None:
            raise ProbeBlocked("EXCHANGE_MISSING")
        deadline = monotonic() + 30
        while True:
            connected = read(exchange.IO, "status")
            result["connection_checks"] += 1
            if connected is True or (type(connected) is int and connected == 1):
                break
            remaining = int((deadline - monotonic()) * 1000)
            if remaining <= 0 or result["connection_checks"] >= 31:
                raise ProbeBlocked("CONNECTION_TIMEOUT")
            if not callable(host.get("Sleep")):
                raise ProbeBlocked("HOST_SLEEP_REQUIRED")
            delay = min(1000, remaining)
            host["Sleep"](delay)
            result["connection_wait_ms"] += delay
        read(exchange.IO, "mode", 0)  # documented immediate quote/read mode
        meta = read(exchange.SetContractType, contract)
        if (not isinstance(meta, Mapping) or meta.get("InstrumentID") != contract
                or meta.get("ExchangeID") != "SHFE" or number(meta.get("VolumeMultiple")) != "1000"
                or Decimal(number(meta.get("PriceTick"))) != Decimal("0.02")
                or type(meta.get("DeliveryYear")) is not int or meta["DeliveryYear"] != 2000 + int(contract[2:4])
                or type(meta.get("DeliveryMonth")) is not int or meta["DeliveryMonth"] != int(contract[4:])
                or meta.get("IsTrading") not in (1, True)):
            raise ProbeBlocked("CONTRACT_METADATA_MISMATCH")
        result["contract_metadata"] = {key: meta[key] for key in
            ("InstrumentID", "ExchangeID", "VolumeMultiple", "PriceTick", "DeliveryYear", "DeliveryMonth", "IsTrading")}
        account = read(exchange.GetAccount)
        info = field(account, "Info")
        if not isinstance(info, Mapping) or str(info.get("BrokerID")) != "9999":
            raise ProbeBlocked("BROKER_ACCOUNT_UNREADABLE")
        # CTP InvestorID is needed for account-specific requests; AccountID alone
        # must not be guessed to be the investor code.
        investor = info.get("InvestorID")
        if not isinstance(investor, (str, int)) or isinstance(investor, bool) or not str(investor):
            raise ProbeBlocked("INVESTOR_ID_UNOBSERVABLE")
        account_token = token(salt, investor)
        result["account"] = {"investor_token": account_token, "broker_id": "9999",
            "available_cash_cny": number(field(account, "Balance")),
            "equity_cny": number(field(account, "Equity"), positive=True),
            "frozen_cash_cny": number(field(account, "FrozenBalance"))}
        positions = read(exchange.GetPositions)
        orders = read(exchange.GetOrders)
        if not isinstance(positions, (list, tuple)) or not isinstance(orders, (list, tuple)) or max(len(positions), len(orders)) > 100:
            raise ProbeBlocked("POSITIONS_OR_PENDING_ORDERS_UNREADABLE")
        result["positions"] = []
        for pos in positions:
            symbol = field(pos, "ContractType") or field(pos, "Symbol")
            kind, amount = field(pos, "Type"), number(field(pos, "Amount"), positive=True)
            if not isinstance(symbol, str) or len(symbol) > 32 or type(kind) is not int or Decimal(amount) != Decimal(amount).to_integral_value():
                raise ProbeBlocked("POSITION_SHAPE_UNREADABLE")
            result["positions"].append({"contract": symbol, "type": kind, "amount": amount,
                                       "margin_cny": number(field(pos, "Margin"))})
        result["pending_orders"] = []
        for order in orders:
            order_id = field(order, "Id")
            if order_id in (None, "", 0):
                raise ProbeBlocked("ORDER_ID_UNREADABLE")
            amount = Decimal(number(field(order, "Amount"), positive=True))
            dealt = Decimal(number(field(order, "DealAmount")))
            if amount != amount.to_integral_value() or dealt != dealt.to_integral_value() or dealt > amount:
                raise ProbeBlocked("PENDING_ORDER_QUANTITY_INVALID")
            result["pending_orders"].append({"order_token": token(salt, order_id),
                "price": number(field(order, "Price")), "amount": str(amount), "deal_amount": str(dealt)})
        quote = read(exchange.GetTicker)
        quote_time = field(quote, "Time")
        quote_now = latest_stamp
        if type(quote_time) is not int or not 0 <= int(quote_now.timestamp() * 1000) - quote_time <= 15000:
            raise ProbeBlocked("QUOTE_STALE_OR_FUTURE")
        result["quote"] = {"bid": number(field(quote, "Buy"), positive=True),
                           "ask": number(field(quote, "Sell"), positive=True),
                           "last": number(field(quote, "Last"), positive=True), "time_ms": quote_time}
        result["quote_observed_at"] = quote_now.isoformat()
        if Decimal(result["quote"]["bid"]) > Decimal(result["quote"]["ask"]):
            raise ProbeBlocked("CROSSED_POSITIVE_QUOTE_INVALID")
        for method in METHODS:
            # CTP query flow limits vary by front. Space the four read requests;
            # never retry a rejected/unknown response or submit an order.
            if method != METHODS[0]:
                if not callable(host.get("Sleep")):
                    result["native_queries"][method] = {"query_error": "NATIVE_QUERY_FAILED_OR_UNREADABLE"}
                    continue
                host["Sleep"](1100)
            params = {"InstrumentID": contract, "ExchangeID": "SHFE"}
            if method != METHODS[3]:
                params.update({"BrokerID": "9999", "InvestorID": str(investor)})
            if method == METHODS[0]:
                params["HedgeFlag"] = "1"
            if method == METHODS[2]:
                params = {"BrokerID": "9999", "InvestorID": str(investor), "CurrencyID": "CNY"}
            try:
                response = project_response(read(exchange.IO, "api", method, params), method, salt)
                stamp = require_window(completed=True)
                safe_params = {key: token(salt, value) if key in IDENTITIES else value for key, value in params.items()}
                result["native_queries"][method] = {"request": safe_params, "observed_at": stamp.isoformat(),
                    "decoded_redacted_response": response, "response_sha256": digest(response),
                    "hash_semantics": "DECODED_REDACTED_CANONICAL_JSON_NOT_WIRE_BYTES"}
            except Exception as exc:
                if isinstance(exc, ProbeBlocked) and str(exc) in (
                        "OBSERVATION_WINDOW_EXCEEDED", "OUTSIDE_APPROVED_OFFICIAL_SESSION_WINDOW",
                        "OBSERVATION_CLOCK_INVALID", "OBSERVATION_CLOCK_MOVED_BACKWARDS"):
                    raise
                # Do not downgrade a late/ineligible observation into a query
                # gap and continue submitting subsequent read requests.
                require_window(completed=True)
                if latest_stamp >= window_end:
                    raise ProbeBlocked("OBSERVATION_WINDOW_EXCEEDED")
                result["native_queries"][method] = {"query_error": "NATIVE_QUERY_FAILED_OR_UNREADABLE"}
        result["cost_assessment"] = assess_cost_evidence(result["native_queries"], account_token, contract)
        result["status"], result["reason_code"] = "READBACK_OBSERVED_UNATTESTED", "NONE"
    except ProbeBlocked as exc:
        result["reason_code"] = str(exc)
    except Exception:
        result["reason_code"] = "HOST_READBACK_EXCEPTION"
    stamp = clock()
    if result["status"] == "READBACK_OBSERVED_UNATTESTED" and not now <= stamp <= window_end:
        result["status"], result["reason_code"] = "BLOCKED", "OBSERVATION_WINDOW_EXCEEDED"
    result["available_at"] = stamp.isoformat()
    result["receipt_sha256"] = digest(result)
    return result


def main():
    result = inspect_host(globals())
    if result["reason_code"] != "ACCEPTANCE_ALREADY_ATTEMPTED" and callable(globals().get("_G")):
        globals()["_G"](RECEIPT_KEY, result)
    rendered = canonical(result).decode("utf-8")
    logger = globals().get("Log")
    if callable(logger):
        logger("GOLD2_CTP_READONLY_COST_CANDIDATE", rendered)
    else:
        print(rendered)
    return result
