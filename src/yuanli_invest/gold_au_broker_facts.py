"""Read-only native YouQuant/CTP fact adapters; no trading or default authority.

The supplied exchange is the real host object. Calls are explicitly allowlisted.
External identity, cost-policy and platform/native order bindings must already
be authenticated by their independent readers/verifiers. Hashes establish
integrity, not authenticity. No secret, raw broker reply or account id is logged.
Native synchronous IO has no documented interruption timeout: late replies are
rejected, but the host still needs an external watchdog.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import hashlib
import json
import re
from typing import Any

from .gold_paper import PaperDenied, SHANGHAI, SIMNOW_FIRST, reconcile_four_way, validate_au_metadata

SCHEMA = "gold2-au-broker-facts.v1"
SHA = re.compile(r"sha256:[0-9a-f]{64}\Z")
NATIVE_FIELDS = {
    "ReqQryInstrumentMarginRate": ("CThostFtdcInstrumentMarginRateField", (
        "BrokerID", "InvestorID", "InstrumentID", "ExchangeID", "InvestorRange", "HedgeFlag",
        "IsRelative", "LongMarginRatioByMoney", "LongMarginRatioByVolume", "ShortMarginRatioByMoney",
        "ShortMarginRatioByVolume")),
    "ReqQryInstrumentCommissionRate": ("CThostFtdcInstrumentCommissionRateField", (
        "BrokerID", "InvestorID", "InstrumentID", "ExchangeID", "InvestorRange", "BizType",
        "OpenRatioByMoney", "OpenRatioByVolume", "CloseRatioByMoney", "CloseRatioByVolume",
        "CloseTodayRatioByMoney", "CloseTodayRatioByVolume")),
    "ReqQryBrokerTradingParams": ("CThostFtdcBrokerTradingParamsField", (
        "BrokerID", "InvestorID", "AccountID", "CurrencyID", "MarginPriceType", "Algorithm")),
    "ReqQryDepthMarketData": ("CThostFtdcDepthMarketDataField", (
        "ExchangeID", "InstrumentID", "TradingDay", "ActionDay", "LastPrice", "PreSettlementPrice",
        "AveragePrice", "OpenPrice", "SettlementPrice", "UpperLimitPrice", "LowerLimitPrice",
        "UpdateTime", "UpdateMillisec", "BidPrice1", "AskPrice1")),
    "ReqQryOrder": ("CThostFtdcOrderField", (
        "BrokerID", "InvestorID", "InstrumentID", "ExchangeID", "TradingDay", "OrderSysID",
        "OrderRef", "FrontID", "SessionID", "OrderStatus", "OrderSubmitStatus", "VolumeTotalOriginal",
        "VolumeTraded", "VolumeTotal", "Direction", "CombOffsetFlag", "CombHedgeFlag", "LimitPrice")),
    "ReqQryTrade": ("CThostFtdcTradeField", (
        "BrokerID", "InvestorID", "InstrumentID", "ExchangeID", "TradingDay", "TradeID",
        "OrderSysID", "OrderRef", "Volume", "Price", "Direction", "OffsetFlag", "HedgeFlag")),
    "ReqQryTradingAccount": ("CThostFtdcTradingAccountField", (
        "BrokerID", "AccountID", "CurrencyID", "TradingDay", "Balance", "Available", "FrozenMargin",
        "FrozenCommission", "CurrMargin", "Commission", "CloseProfit", "PositionProfit", "Deposit", "Withdraw")),
    "ReqQryInvestorPosition": ("CThostFtdcInvestorPositionField", (
        "BrokerID", "InvestorID", "InstrumentID", "ExchangeID", "TradingDay", "PosiDirection",
        "HedgeFlag", "PositionDate", "Position", "TodayPosition", "UseMargin", "FrozenMargin")),
}


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                          allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise PaperDenied("BROKER_FACT_NON_CANONICAL") from exc


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def _number(value: Any, *, positive: bool = False) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise PaperDenied("BROKER_FACT_NUMBER_INVALID")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise PaperDenied("BROKER_FACT_NUMBER_INVALID") from exc
    if not result.is_finite() or result < 0 or result > Decimal("1e20") or (positive and result == 0):
        raise PaperDenied("BROKER_FACT_NUMBER_INVALID")
    return result


def _integer(value: Any, *, positive: bool = False) -> int:
    result = _number(value, positive=positive)
    if result != result.to_integral_value():
        raise PaperDenied("BROKER_FACT_QUANTITY_INVALID")
    return int(result)


def _enum(value: Any) -> str:
    # Native CTP char fields are exposed both as one-character strings and
    # numeric ASCII codes (the official IO example shows 48/49).
    if type(value) is int and 0 <= value <= 127:
        value = chr(value)
    if not isinstance(value, str) or len(value) != 1:
        raise PaperDenied("BROKER_FACT_ENUM_INVALID")
    return value


def _time(value: Any) -> datetime:
    try:
        stamp = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError) as exc:
        raise PaperDenied("BROKER_FACT_TIME_INVALID") from exc
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise PaperDenied("BROKER_FACT_TIME_INVALID")
    return stamp.astimezone(timezone.utc)


def _fresh(value: Any, now: datetime, seconds: int) -> datetime:
    stamp = _time(value)
    if not timedelta(0) <= _time(now) - stamp <= timedelta(seconds=seconds):
        raise PaperDenied("BROKER_FACT_STALE_OR_FUTURE")
    return stamp


def _field(value: Any, name: str) -> Any:
    return value.get(name) if isinstance(value, Mapping) else getattr(value, name, None)


def _contract(contract: Any) -> str:
    if not isinstance(contract, str) or not re.fullmatch(r"au[0-9]{4}", contract) or not 1 <= int(contract[-2:]) <= 12:
        raise PaperDenied("BROKER_FACT_CONTRACT_INVALID")
    return contract


def native_rows(raw: Any, method: str) -> tuple[list[dict[str, Any]], str]:
    """Decode documented packets, hash exact decoded response, safely project.

    Extra fields inside the documented struct cannot influence calculations;
    unknown struct names, error packets and incomplete shapes are rejected.
    The first hash is full decoded canonical JSON, never the CTP wire bytes.
    """
    if method not in NATIVE_FIELDS or not isinstance(raw, (list, tuple)) or len(raw) > 1000:
        raise PaperDenied("NATIVE_RESPONSE_SHAPE")
    raw_hash = digest(raw)
    if len(canonical(raw)) > 2_000_000:
        raise PaperDenied("NATIVE_RESPONSE_TOO_LARGE")
    name, fields = NATIVE_FIELDS[method]
    rows = []
    for packet in raw:
        if not isinstance(packet, (list, tuple)) or len(packet) > 1000:
            raise PaperDenied("NATIVE_RESPONSE_SHAPE")
        for entry in packet:
            if not isinstance(entry, Mapping) or not isinstance(entry.get("Value"), Mapping):
                raise PaperDenied("NATIVE_RESPONSE_SHAPE")
            values = entry["Value"]
            if entry.get("Name") == "CThostFtdcRspInfoField":
                if type(values.get("ErrorID")) is not int or values["ErrorID"] != 0:
                    raise PaperDenied("NATIVE_QUERY_ERROR")
            elif entry.get("Name") == name:
                rows.append({key: values[key] for key in fields if key in values})
            else:
                raise PaperDenied("UNEXPECTED_NATIVE_STRUCT")
    return rows, raw_hash


def _exact_row(rows: list[dict]) -> dict:
    if len(rows) != 1:
        raise PaperDenied("NATIVE_EXPECTED_SINGLE_ROW")
    return rows[0]


class BrokerFactsReader:
    """Actual host reader with injectable independently authenticated evidence.

    It never discovers or guesses credentials, funds allocations, order-id
    encodings, or broker policy. Missing real integrations remain blocked.
    Callback consumption alone does not prove the reader was used in production.
    """

    def __init__(self, *, exchange: Any, robot_id: int, clock: Callable[[], datetime],
                 account_attestation_reader: Callable[[], Mapping] | None = None,
                 account_attestation_verifier: Callable[[Mapping, int, datetime], bool] | None = None,
                 account_cost_policy_reader: Callable[[str], Mapping] | None = None,
                 independent_receipt_verifier: Callable[[Mapping], bool] | None = None,
                 order_binding_reader: Callable[[str], Mapping] | None = None,
                 command_order_binding_reader: Callable[[str, str], Mapping] | None = None,
                 history_reader: Callable[[str, datetime], Mapping] | None = None,
                 reconciliation_readers: Mapping[str, Callable[[], Mapping]] | None = None,
                 strategy_equity_reader: Callable[[], Mapping] | None = None,
                 max_read_seconds: int = 15):
        if type(robot_id) is not int or robot_id <= 0 or type(max_read_seconds) is not int or not 1 <= max_read_seconds <= 15:
            raise PaperDenied("BROKER_READER_CONFIG_INVALID")
        self.exchange, self.robot_id, self.clock = exchange, robot_id, clock
        self.attestation_reader = account_attestation_reader
        self.attestation_verifier = account_attestation_verifier
        self.policy_reader, self.receipt_verifier = account_cost_policy_reader, independent_receipt_verifier
        self.binding_reader, self.history_reader = order_binding_reader, history_reader
        self.command_binding_reader = command_order_binding_reader
        self.reconciliation_readers = dict(reconciliation_readers or {})
        self.equity_reader = strategy_equity_reader
        self.max_read_seconds = max_read_seconds
        self.receipts: list[dict[str, Any]] = []
        self.last_cost_receipt: dict | None = None
        self.last_reconciliation_result: dict | None = None

    def _call(self, name: str, *args: Any) -> Any:
        if name not in {"IO", "SetContractType", "GetAccount", "GetPositions", "GetOrders", "GetTicker"}:
            raise PaperDenied("BROKER_READ_METHOD_NOT_ALLOWLISTED")
        if name == "IO" and args != ("status",):
            if len(args) != 3 or args[0] != "api" or args[1] not in NATIVE_FIELDS or not isinstance(args[2], Mapping):
                raise PaperDenied("NATIVE_READ_METHOD_NOT_ALLOWLISTED")
        start = _time(self.clock())
        try:
            raw = getattr(self.exchange, name)(*args)
        except Exception as exc:
            raise PaperDenied("BROKER_READ_FAILED") from exc
        end = _time(self.clock())
        if not timedelta(0) <= end - start <= timedelta(seconds=self.max_read_seconds):
            raise PaperDenied("BROKER_READ_LATE_OR_CLOCK_REVERSED")
        return raw

    def _native(self, method: str, params: Mapping) -> list[dict]:
        start = _time(self.clock())
        raw = self._call("IO", "api", method, dict(params))
        end = _time(self.clock())
        rows, raw_hash = native_rows(raw, method)
        self.receipts.append({"method": method, "request": dict(params), "observed_at": start.isoformat(),
            "available_at": end.isoformat(), "response_sha256": raw_hash,
            "decoded_projection": rows, "projection_sha256": digest(rows),
            "hash_semantics": "FULL_DECODED_CANONICAL_JSON_NOT_CTP_WIRE_BYTES"})
        if len(self.receipts) > 64:
            self.receipts = self.receipts[-64:]
        return rows

    def _identity(self) -> tuple[str, str, Mapping]:
        status = self._call("IO", "status")
        if status is not True and not (type(status) is int and status == 1):
            raise PaperDenied("BROKER_NOT_CONNECTED")
        account = self._call("GetAccount")
        info = _field(account, "Info")
        if not isinstance(info, Mapping) or info.get("BrokerID") != "9999":
            raise PaperDenied("BROKER_ACCOUNT_IDENTITY_MISSING")
        investor, account_id = info.get("InvestorID"), info.get("AccountID")
        if not isinstance(investor, str) or not investor or not isinstance(account_id, str) or not account_id:
            raise PaperDenied("BROKER_ACCOUNT_IDENTITY_MISSING")
        if self.attestation_reader is None or self.attestation_verifier is None:
            raise PaperDenied("INDEPENDENT_ACCOUNT_ATTESTATION_UNWIRED")
        attestation = self.attestation_reader()
        now = _time(self.clock())
        if (not isinstance(attestation, Mapping) or attestation.get("source") != "youquant_account_and_robot_readback"
                or attestation.get("account_id") != investor or attestation.get("broker_id") != "9999"
                or attestation.get("robot_id") != self.robot_id or attestation.get("environment") != SIMNOW_FIRST):
            raise PaperDenied("INDEPENDENT_ACCOUNT_ATTESTATION_MISMATCH")
        _fresh(attestation.get("observed_at"), now, 300)
        # Must verify the exact control-plane API receipts and configured first
        # normal fronts, not a boolean or GetName/9999 supplied by this reader.
        if self.attestation_verifier(attestation, self.robot_id, now) is not True:
            raise PaperDenied("INDEPENDENT_ACCOUNT_ATTESTATION_UNVERIFIED")
        return investor, account_id, attestation

    def account_attestation(self) -> Mapping:
        return self._identity()[2]

    def _scope(self, row: Mapping, investor: str, contract: str | None = None) -> None:
        if row.get("BrokerID") != "9999" or row.get("InvestorID") != investor:
            raise PaperDenied("NATIVE_ACCOUNT_SCOPE_MISMATCH")
        if contract is not None and (row.get("InstrumentID") != contract or row.get("ExchangeID") != "SHFE"):
            raise PaperDenied("NATIVE_CONTRACT_SCOPE_MISMATCH")

    def _verified_external(self, receipt: Any, source: str, investor: str, contract: str) -> Mapping:
        if not isinstance(receipt, Mapping) or receipt.get("source") != source:
            raise PaperDenied("INDEPENDENT_FACT_SOURCE_MISSING")
        if receipt.get("account_id") != investor or receipt.get("contract") != contract or receipt.get("environment") != SIMNOW_FIRST:
            raise PaperDenied("INDEPENDENT_FACT_SCOPE_MISMATCH")
        if self.receipt_verifier is None or self.receipt_verifier(receipt) is not True:
            raise PaperDenied("INDEPENDENT_FACT_AUTHENTICITY_UNVERIFIED")
        _fresh(receipt.get("observed_at"), self.clock(), 15)
        if not isinstance(receipt.get("raw_sha256"), str) or not SHA.fullmatch(receipt["raw_sha256"]):
            raise PaperDenied("INDEPENDENT_FACT_HASH_MISSING")
        return receipt

    def quote(self, contract: str) -> dict:
        contract = _contract(contract)
        meta = self._call("SetContractType", contract)
        validate_au_metadata(meta, contract)
        raw = self._call("GetTicker")
        now = _time(self.clock())
        milliseconds = _field(raw, "Time")
        if type(milliseconds) is not int:
            raise PaperDenied("QUOTE_TIME_INVALID")
        try:
            quote_at = datetime.fromtimestamp(milliseconds / 1000, timezone.utc)
        except (ValueError, OverflowError, OSError) as exc:
            raise PaperDenied("QUOTE_TIME_INVALID") from exc
        _fresh(quote_at, now, 15)
        bid, ask, last = (_number(_field(raw, name), positive=True) for name in ("Buy", "Sell", "Last"))
        if bid > ask:
            raise PaperDenied("QUOTE_CROSSED")
        return {"bid": str(bid), "ask": str(ask), "last": str(last), "time_ms": milliseconds,
                "observed_at": now.isoformat(), "raw_sha256": digest({"Buy": str(bid), "Sell": str(ask), "Last": str(last), "Time": milliseconds})}

    def read_current(self, contract: str) -> dict:
        """Actual whole-account current readbacks, never an order terminal proof."""
        start = _time(self.clock())
        investor, account_id, _ = self._identity()
        contract = _contract(contract)
        account = _exact_row(self._native("ReqQryTradingAccount", {"BrokerID": "9999", "InvestorID": investor,
            "AccountID": account_id, "CurrencyID": "CNY"}))
        account_receipt = self.receipts[-1]
        if account.get("BrokerID") != "9999" or account.get("AccountID") != account_id or account.get("CurrencyID") != "CNY":
            raise PaperDenied("CURRENT_ACCOUNT_SCOPE_MISMATCH")
        positions = self._call("GetPositions")
        pending = self._call("GetOrders")
        if not isinstance(positions, (list, tuple)) or not isinstance(pending, (list, tuple)) or len(positions) > 1000 or len(pending) > 1000:
            raise PaperDenied("CURRENT_READBACK_SHAPE")
        position_projection, order_projection = [], []
        for row in positions:
            symbol = _field(row, "ContractType") or _field(row, "Symbol")
            amount = _integer(_field(row, "Amount"), positive=True)
            if not isinstance(symbol, str) or not symbol or type(_field(row, "Type")) is not int:
                raise PaperDenied("CURRENT_POSITION_UNREADABLE")
            position_projection.append({"contract": symbol, "quantity": str(amount), "type": _field(row, "Type"),
                "margin_cny": str(_number(_field(row, "Margin")))})
        for row in pending:
            order_id = _field(row, "Id")
            if (isinstance(order_id, bool) or not isinstance(order_id, (str, int)) or not str(order_id)
                    or order_id == 0 or (type(order_id) is int and order_id < 0)
                    or any(item["order_id"] == str(order_id) for item in order_projection)):
                raise PaperDenied("CURRENT_ORDER_UNREADABLE")
            total = _integer(_field(row, "Amount"), positive=True)
            filled = _integer(_field(row, "DealAmount"))
            if filled > total:
                raise PaperDenied("CURRENT_ORDER_FILL_INVALID")
            order_projection.append({"order_id": str(order_id), "amount": str(total), "filled_quantity": str(filled)})
        quote = self.quote(contract)
        end = _time(self.clock())
        if end - start > timedelta(seconds=15):
            raise PaperDenied("CURRENT_SNAPSHOT_STALE")
        result = {"schema_version": SCHEMA, "source": "simnow_native_ctp_readonly_facts", "environment": SIMNOW_FIRST,
            "account_id": investor, "contract": contract, "observed_at": start.isoformat(), "available_at": end.isoformat(),
            "broker_trading_day": account.get("TradingDay"), "broker_equity": str(_number(account.get("Balance"))),
            "available": str(_number(account.get("Available"))), "frozen_margin": str(_number(account.get("FrozenMargin"))),
            "account": account, "positions": position_projection, "pending_orders": order_projection,
            "pending_order_count": len(order_projection), "quote": quote, "terminal_history_proven": False,
            "raw_account_sha256": account_receipt["response_sha256"],
            "raw_positions_sha256": digest(position_projection), "raw_orders_sha256": digest(order_projection),
            "collection_hash_semantics": "ACCOUNT_FULL_DECODED_CANONICAL_JSON_POSITIONS_AND_PENDING_ORDERS_CANONICAL_PROJECTIONS"}
        result["raw_sha256"] = digest(result)
        return result

    def read_account_costs(self, contract: str) -> dict:
        """Compute conditional, independently approved one-lot cost bounds.

        A native rate estimate cannot prove order freezing or future close fees.
        No policy or authenticated price/fee bound => no executable callback.
        """
        contract = _contract(contract)
        started = _time(self.clock())
        investor, account_id, _ = self._identity()
        meta = self._call("SetContractType", contract)
        validate_au_metadata(meta, contract)
        request = {"BrokerID": "9999", "InvestorID": investor, "InstrumentID": contract, "ExchangeID": "SHFE"}
        margin = _exact_row(self._native("ReqQryInstrumentMarginRate", {**request, "HedgeFlag": "1"}))
        margin_receipt = self.receipts[-1]
        commission = _exact_row(self._native("ReqQryInstrumentCommissionRate", request))
        commission_receipt = self.receipts[-1]
        params = _exact_row(self._native("ReqQryBrokerTradingParams", {"BrokerID": "9999", "InvestorID": investor, "CurrencyID": "CNY", "AccountID": account_id}))
        params_receipt = self.receipts[-1]
        market = _exact_row(self._native("ReqQryDepthMarketData", {"InstrumentID": contract, "ExchangeID": "SHFE"}))
        market_receipt = self.receipts[-1]
        for row in (margin, commission):
            self._scope(row, investor, contract)
            if _enum(row.get("InvestorRange")) != "3":
                raise PaperDenied("ACCOUNT_SPECIFIC_RATE_REQUIRED")
        self._scope(params, investor)
        if params.get("CurrencyID") != "CNY" or params.get("AccountID") != account_id:
            raise PaperDenied("MARGIN_PARAMETERS_ACCOUNT_MISMATCH")
        if (market.get("InstrumentID") != contract or market.get("ExchangeID") != "SHFE"
                or _enum(margin.get("HedgeFlag")) != "1" or margin.get("IsRelative") not in (0, False)
                or _enum(commission.get("BizType")) != "1"):
            raise PaperDenied("COST_BASIS_UNSUPPORTED")
        price_type = _enum(params.get("MarginPriceType"))
        # SDK 6.7.13: 1=previous settlement, 2=latest (enum named
        # SettlementPrice), 3=average, 4=opening price. Never guess from names.
        basis_key = {"1": "PreSettlementPrice", "2": "LastPrice", "3": "AveragePrice", "4": "OpenPrice"}.get(price_type)
        if basis_key is None:
            raise PaperDenied("MARGIN_PRICE_TYPE_UNSUPPORTED")
        basis = _number(market.get(basis_key), positive=True)
        try:
            market_stamp = datetime.strptime(str(market.get("ActionDay")) + str(market.get("UpdateTime")), "%Y%m%d%H:%M:%S").replace(tzinfo=SHANGHAI)
        except ValueError as exc:
            raise PaperDenied("NATIVE_MARKET_TIME_UNOBSERVABLE") from exc
        millis = _integer(market.get("UpdateMillisec"))
        if millis > 999:
            raise PaperDenied("NATIVE_MARKET_MILLISECOND_INVALID")
        _fresh(market_stamp + timedelta(milliseconds=millis), self.clock(), 15)
        if self.policy_reader is None:
            raise PaperDenied("ACCOUNT_EXECUTION_COST_POLICY_UNWIRED")
        policy = self._verified_external(self.policy_reader(contract), "independent_account_execution_cost_policy", investor, contract)
        expires = _time(policy.get("expires_at"))
        if expires < _time(self.clock()):
            raise PaperDenied("ACCOUNT_COST_POLICY_EXPIRED")
        if (policy.get("account_currency") != "CNY" or type(policy.get("quantity")) is not int or policy.get("quantity") != 1
                or policy.get("covers_additional_order_freeze") is not True
                or policy.get("covers_all_broker_and_exchange_fees") is not True
                or policy.get("covers_future_close_rates") is not True):
            raise PaperDenied("ACCOUNT_COST_POLICY_SCOPE_INCOMPLETE")
        margin_price = _number(policy.get("margin_price_upper_cny_per_gram"), positive=True)
        open_price = _number(policy.get("open_price_upper_cny_per_gram"), positive=True)
        close_price = _number(policy.get("close_price_upper_cny_per_gram"), positive=True)
        upper_limit = _number(market.get("UpperLimitPrice"), positive=True)
        if (margin_price < basis or open_price < upper_limit
                or (price_type != "1" and margin_price < upper_limit)):
            raise PaperDenied("ACCOUNT_COST_PRICE_BOUND_TOO_SMALL")
        def cost(prefix: str, price: Decimal) -> Decimal:
            return price * Decimal("1000") * _number(commission.get(prefix + "RatioByMoney")) + _number(commission.get(prefix + "RatioByVolume"))
        required_margin = margin_price * Decimal("1000") * _number(margin.get("LongMarginRatioByMoney")) + _number(margin.get("LongMarginRatioByVolume"))
        if required_margin <= 0:
            raise PaperDenied("MARGIN_RATE_NOT_POSITIVE")
        required_margin += _number(policy.get("additional_margin_freeze_upper_cny"))
        fee_open, fee_today, fee_yesterday = cost("Open", open_price), cost("CloseToday", close_price), cost("Close", close_price)
        fees = fee_open + max(fee_today, fee_yesterday) + _number(policy.get("additional_round_trip_fee_upper_cny"))
        if fees <= 0 or fees > _number(policy.get("round_trip_fee_upper_cny"), positive=True):
            raise PaperDenied("ACCOUNT_FEE_UPPER_TOO_SMALL")
        finished = _time(self.clock())
        if finished - started > timedelta(seconds=15):
            raise PaperDenied("COST_SNAPSHOT_STALE")
        result = {"schema_version": SCHEMA, "source": "simnow_native_ctp_readonly_facts", "status": "BOUNDED_ACCOUNT_COSTS",
            "environment": SIMNOW_FIRST, "account_id": investor, "contract": contract,
            "observed_at": started.isoformat(), "available_at": finished.isoformat(), "expires_at": expires.isoformat(),
            "margin_basis_type": price_type, "margin_basis_field": basis_key, "observed_margin_basis_price": str(basis),
            "margin_for_one_lot": str(required_margin.quantize(Decimal("0.01"), rounding=ROUND_CEILING)),
            "open_fee_cny": str(fee_open), "close_today_fee_cny": str(fee_today), "close_yesterday_fee_cny": str(fee_yesterday),
            "round_trip_fee_upper_cny": str(_number(policy["round_trip_fee_upper_cny"], positive=True)),
            "policy_sha256": policy["raw_sha256"],
            "native_receipts": [margin_receipt, commission_receipt, params_receipt, market_receipt]}
        result["raw_sha256"] = digest(result)
        self.last_cost_receipt = result
        return result

    def current_margin(self, contract: str) -> str:
        return self.read_account_costs(contract)["margin_for_one_lot"]

    def current_round_trip_fee_upper(self, contract: str) -> str:
        receipt = self.last_cost_receipt
        if receipt is None or receipt.get("contract") != contract:
            receipt = self.read_account_costs(contract)
        _fresh(receipt["observed_at"], self.clock(), 15)
        if _time(receipt["expires_at"]) < _time(self.clock()):
            raise PaperDenied("ACCOUNT_COST_POLICY_EXPIRED")
        return receipt["round_trip_fee_upper_cny"]

    def terminal_truth(self, order_id: str) -> dict:
        """Read native order AND trades; absent pending order never means filled.

        Current-day native queries cannot recover yesterday's missing result.
        Rejections without exchange OrderSysID are currently unsupported.
        """
        started = _time(self.clock())
        investor, account_id, _ = self._identity()
        if self.binding_reader is None:
            raise PaperDenied("PLATFORM_NATIVE_ORDER_BINDING_UNWIRED")
        binding = self.binding_reader(order_id)
        contract = _contract(binding.get("contract") if isinstance(binding, Mapping) else None)
        binding = self._verified_external(binding, "independent_platform_native_order_binding", investor, contract)
        if (not isinstance(order_id, str) or not order_id or binding.get("order_id") != order_id
                or type(binding.get("quantity")) is not int or binding.get("quantity") != 1
                or any(type(binding.get(key)) is not int or binding[key] <= 0 for key in ("front_id", "session_id"))):
            raise PaperDenied("PLATFORM_NATIVE_ORDER_BINDING_MISMATCH")
        # Trading day is broker day, not local date: night session belongs to
        # the next trading day. Obtain it from actual account native readback.
        account = _exact_row(self._native("ReqQryTradingAccount", {"BrokerID": "9999", "InvestorID": investor, "CurrencyID": "CNY", "AccountID": account_id}))
        account_receipt = self.receipts[-1]
        if account.get("BrokerID") != "9999" or account.get("AccountID") != account_id or account.get("CurrencyID") != "CNY":
            raise PaperDenied("TERMINAL_ACCOUNT_SCOPE_MISMATCH")
        if account.get("TradingDay") != binding.get("trading_day"):
            raise PaperDenied("CROSS_DAY_TERMINAL_ARCHIVE_UNAVAILABLE")
        sys_id = binding.get("order_sys_id")
        if not isinstance(sys_id, str) or not sys_id.strip() or len(sys_id) > 21:
            raise PaperDenied("NATIVE_EXCHANGE_ORDER_ID_UNAVAILABLE")
        request = {"BrokerID": "9999", "InvestorID": investor, "InstrumentID": contract, "ExchangeID": "SHFE"}
        orders = self._native("ReqQryOrder", {**request, "OrderSysID": sys_id})
        orders_receipt = self.receipts[-1]
        order = _exact_row(orders)
        self._scope(order, investor, contract)
        if (order.get("OrderSysID") != sys_id or order.get("TradingDay") != binding["trading_day"]
                or order.get("OrderRef") != binding.get("order_ref")
                or order.get("FrontID") != binding.get("front_id") or order.get("SessionID") != binding.get("session_id")):
            raise PaperDenied("TERMINAL_ORDER_BINDING_MISMATCH")
        direction, offset = _enum(order.get("Direction")), _enum(order.get("CombOffsetFlag"))
        if direction != binding.get("direction") or offset != binding.get("offset_flag") or _enum(order.get("CombHedgeFlag")) != "1":
            raise PaperDenied("TERMINAL_ORDER_ACTION_MISMATCH")
        total, filled, remaining = (_integer(order.get(key)) for key in ("VolumeTotalOriginal", "VolumeTraded", "VolumeTotal"))
        if total != 1 or filled not in (0, 1) or remaining != total - filled:
            raise PaperDenied("TERMINAL_ORDER_QUANTITY_MISMATCH")
        status, submit = _enum(order.get("OrderStatus")), _enum(order.get("OrderSubmitStatus"))
        if status == "0" and filled == 1 and submit == "3":
            normalized = "FILLED"
        elif status == "5" and filled == 0 and submit == "3":
            normalized = "CANCELED"
        elif submit == "4" and filled == 0 and status in {"4", "5"}:
            normalized = "REJECTED"
        elif status == "3" and filled == 0 and submit in {"0", "3"}:
            # A positively observed queueing order must remain monitorable.
            # PENDING is deliberately not a settlement/claim-release proof.
            normalized = "PENDING"
        else:
            raise PaperDenied("ORDER_NOT_TERMINAL_OR_UNSUPPORTED")
        trades = self._native("ReqQryTrade", request)
        trades_receipt = self.receipts[-1]
        selected, trade_ids = [], set()
        for trade in trades:
            self._scope(trade, investor, contract)
            if trade.get("OrderSysID") != sys_id:
                continue
            if (trade.get("TradingDay") != binding["trading_day"] or trade.get("OrderRef") != binding["order_ref"]
                    or _enum(trade.get("Direction")) != direction or _enum(trade.get("OffsetFlag")) != offset
                    or _enum(trade.get("HedgeFlag")) != "1"):
                raise PaperDenied("TERMINAL_TRADE_SCOPE_MISMATCH")
            trade_id = trade.get("TradeID")
            if not isinstance(trade_id, str) or not trade_id.strip() or trade_id in trade_ids:
                raise PaperDenied("TERMINAL_TRADE_DUPLICATE_OR_MISSING_ID")
            trade_ids.add(trade_id)
            _number(trade.get("Price"), positive=True)
            selected.append(trade)
        if sum(_integer(t.get("Volume"), positive=True) for t in selected) != filled:
            raise PaperDenied("ORDER_TRADE_FILL_DELTA")
        # Query whole account, rather than letting a contract filter conceal
        # unrelated positions in the dedicated GOLD2 strategy account.
        positions = self._native("ReqQryInvestorPosition", {"BrokerID": "9999", "InvestorID": investor})
        positions_receipt = self.receipts[-1]
        position_quantity = 0
        for position in positions:
            self._scope(position, investor, contract)
            if position.get("TradingDay") != binding["trading_day"] or _enum(position.get("HedgeFlag")) != "1":
                raise PaperDenied("TERMINAL_POSITION_SCOPE_MISMATCH")
            if _enum(position.get("PosiDirection")) != "2":
                raise PaperDenied("UNEXPECTED_NON_LONG_POSITION")
            if _enum(position.get("PositionDate")) not in {"1", "2"}:
                raise PaperDenied("POSITION_DATE_UNSUPPORTED")
            position_quantity += _integer(position.get("Position"))
        if position_quantity > 1:
            raise PaperDenied("POSITION_SCOPE_EXPANDED")
        pending = self._call("GetOrders")
        if not isinstance(pending, (list, tuple)) or len(pending) > 1000:
            raise PaperDenied("TERMINAL_PENDING_ORDERS_UNREADABLE")
        pending_ids = []
        for row in pending:
            key = _field(row, "Id")
            if (isinstance(key, bool) or not isinstance(key, (str, int)) or not str(key)
                    or key == 0 or (type(key) is int and key < 0)):
                raise PaperDenied("TERMINAL_PENDING_ORDERS_UNREADABLE")
            total_pending = _integer(_field(row, "Amount"), positive=True)
            filled_pending = _integer(_field(row, "DealAmount"))
            if filled_pending > total_pending or str(key) in pending_ids:
                raise PaperDenied("TERMINAL_PENDING_ORDERS_UNREADABLE")
            pending_ids.append(str(key))
        if normalized in {"FILLED", "CANCELED", "REJECTED"} and order_id in pending_ids:
            raise PaperDenied("TERMINAL_STILL_PENDING_CONTRADICTION")
        finished = _time(self.clock())
        if finished - started > timedelta(seconds=15):
            raise PaperDenied("TERMINAL_SNAPSHOT_STALE")
        result = {"source": "simnow_order_and_account_readback", "environment": SIMNOW_FIRST,
            "account_id": investor, "contract": contract, "order_id": order_id, "order_status": normalized,
            "observed_at": started.isoformat(), "available_at": finished.isoformat(),
            "filled_quantity": str(filled), "position_quantity": str(position_quantity),
            "cash": str(_number(account.get("Balance"))), "available": str(_number(account.get("Available"))),
            "frozen_margin": str(_number(account.get("FrozenMargin"))), "trades": selected,
            "native_account_projection": account, "native_order_projection": order,
            "binding_sha256": binding["raw_sha256"],
            "native_receipts": [account_receipt, orders_receipt, trades_receipt, positions_receipt],
            "history_scope": "CURRENT_BROKER_TRADING_DAY_ONLY"}
        result["pending_order_count"] = len(pending_ids)
        result["pending_order_ids"] = pending_ids
        # These four exact native response hashes are for coordinator ingestion.
        # This is one broker fact leg; it does not create the other three legs.
        result.update(dict(zip(("raw_account_sha256", "raw_orders_sha256", "raw_trades_sha256", "raw_positions_sha256"),
                              (r["response_sha256"] for r in (account_receipt, orders_receipt, trades_receipt, positions_receipt)))))
        result["raw_sha256"] = digest(result)
        return result

    def native_order_evidence_v3(self, *, command_id: str, claim_id: str, contract: str, action: str) -> dict:
        """Produce V3 native facts from actual host queries, never four parties.

        Unknown submit results need independently signed command/claim-to-order
        mapping. Searching recent orders by price/time is deliberately absent.
        Only a separately isolated reader principal may publish this payload.
        """
        started = _time(self.clock())
        investor, _, identity = self._identity()
        contract = _contract(contract)
        if (not isinstance(command_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", command_id)
                or not isinstance(claim_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", claim_id)
                or action not in {"OPEN_LONG", "CLOSE_LONG"}):
            raise PaperDenied("V3_NATIVE_COMMAND_SCOPE_INVALID")
        if self.command_binding_reader is None:
            raise PaperDenied("V3_COMMAND_NATIVE_ORDER_BINDING_UNWIRED")
        binding = self._verified_external(self.command_binding_reader(command_id, claim_id),
            "independent_command_native_order_binding", investor, contract)
        order_id = binding.get("order_id")
        if (binding.get("command_id") != command_id or binding.get("claim_id") != claim_id
                or binding.get("action") != action or type(binding.get("quantity")) is not int
                or binding["quantity"] != 1 or not isinstance(order_id, str)
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", order_id)
                or not isinstance(binding.get("platform_binding_sha256"), str)
                or not SHA.fullmatch(binding["platform_binding_sha256"])):
            raise PaperDenied("V3_COMMAND_NATIVE_ORDER_BINDING_MISMATCH")
        truth = self.terminal_truth(order_id)
        order = truth["native_order_projection"]
        direction, offset = _enum(order.get("Direction")), _enum(order.get("CombOffsetFlag"))
        if (truth["account_id"] != investor or truth["contract"] != contract
                or truth["binding_sha256"] != binding["platform_binding_sha256"]
                or (action == "OPEN_LONG" and (direction, offset) != ("0", "0"))
                or (action == "CLOSE_LONG" and (direction != "1" or offset not in {"1", "3", "4"}))):
            raise PaperDenied("V3_NATIVE_ACTION_OR_BINDING_MISMATCH")
        completed = _time(self.clock())
        if completed - started > timedelta(seconds=15):
            raise PaperDenied("V3_NATIVE_COLLECTION_STALE")
        facts = {"command_id": command_id, "claim_id": claim_id, "instrument": contract, "action": action,
            "order_id": order_id, "order_status": truth["order_status"],
            "filled_quantity": _integer(truth["filled_quantity"]), "position_quantity": _integer(truth["position_quantity"]),
            "pending_order_count": truth["pending_order_count"], "parent_claim_id": None,
            "parent_order_id": None, "reconciliation": None,
            "order_binding_sha256": digest({"command_binding_sha256": binding["raw_sha256"],
                                             "platform_binding_sha256": truth["binding_sha256"]}),
            "raw_identity_sha256": digest(identity),
            **{k: truth[k] for k in ("raw_account_sha256", "raw_orders_sha256", "raw_trades_sha256", "raw_positions_sha256")}}
        from .gold_au_receipt_client import validate_native_facts
        validate_native_facts(facts, "NATIVE_ORDER")
        return {"source": "independent_native_order_payload_v3", "environment": SIMNOW_FIRST,
                "account_id": investor, "robot_id": self.robot_id, "kind": "NATIVE_ORDER",
                "observed_at": started.isoformat(), "available_at": completed.isoformat(),
                "facts": facts, "facts_sha256": digest(facts)}

    def terminal_truth_with_four_way(self, order_id: str) -> dict:
        """Resolve genuine broker facts and four independently produced legs.

        Native truth is always read first. Missing, invalid or stale independent
        evidence never fabricates the other three legs or rewrites broker truth.
        PENDING remains monitorable. A complete but mismatching proof is DRIFTED.
        This does not ingest receipts or release the coordinator's claim.
        """
        truth = self.terminal_truth(order_id)
        native_hash = truth["raw_sha256"]

        def outcome(status: str, reason: str, legs: list[Mapping] | None = None) -> dict:
            result = dict(truth)
            result["broker_truth_sha256"] = native_hash
            result["reconciliation_status"] = status
            result["reconciliation_reason"] = reason
            if legs is not None:
                labels = ("capital_intent", "yuanli_execution", "execution_oms", "broker_custodian")
                result["four_way"] = {label: dict(leg) for label, leg in zip(labels, legs)}
            result["available_at"] = _time(self.clock()).isoformat()
            result.pop("raw_sha256", None)
            result["raw_sha256"] = digest(result)
            return result

        if truth["order_status"] == "PENDING":
            return outcome("NOT_TERMINAL", "POSITIVE_NATIVE_ORDER_STILL_PENDING")
        sources = ("capital_intent_ledger", "yuanli_execution_ledger", "execution_oms_readback", "simnow_broker_custodian_readback")
        if (set(self.reconciliation_readers) != set(sources)
                or len({id(self.reconciliation_readers[source]) for source in sources}) != 4
                or self.receipt_verifier is None):
            return outcome("UNKNOWN", "FOUR_INDEPENDENT_RECONCILIATION_READERS_UNWIRED")
        try:
            legs = [self.reconciliation_readers[source]() for source in sources]
            completed = _time(self.clock())
            _fresh(truth["observed_at"], completed, 15)
            for source, leg in zip(sources, legs):
                if (not isinstance(leg, Mapping) or leg.get("source") != source
                        or leg.get("environment") != truth["environment"]
                        or leg.get("account_id") != truth["account_id"]
                        or leg.get("contract") != truth["contract"]):
                    return outcome("UNKNOWN", "FOUR_WAY_SOURCE_OR_SCOPE_UNVERIFIED")
                if self.receipt_verifier(leg) is not True:
                    return outcome("UNKNOWN", "FOUR_WAY_RECEIPT_AUTHENTICITY_UNVERIFIED")
                _fresh(leg.get("observed_at"), completed, 30)
                if "available_at" in leg:
                    if not _time(leg["observed_at"]) <= _time(leg["available_at"]) <= completed:
                        return outcome("UNKNOWN", "FOUR_WAY_AVAILABILITY_TIME_UNVERIFIED")
            matched = reconcile_four_way(*legs, as_of=completed)
            self.last_reconciliation_result = matched
            if matched["status"] != "MATCHED":
                missing_or_unverified = {"MISSING_LEDGER_LEG", "LEDGER_SOURCE_IDENTITY_MISMATCH",
                    "LEDGER_EVIDENCE_MISSING", "RECONCILIATION_TIME_MISSING", "LEDGER_TIME_MISSING",
                    "LEDGER_STALE", "CLONED_LEDGER_EVIDENCE", "INVALID_CAPITAL_INTENT", "INCOMPLETE_LEDGER_LEG"}
                return outcome("UNKNOWN" if matched["reason"] in missing_or_unverified else "DRIFTED", str(matched["reason"]))
            # Four agreeing receipts can still refer to a different order or
            # perfectly agree on wrong cash. Bind to the separately read native
            # broker facts rather than treating agreement alone as truth.
            if (matched["order_ids"] != [order_id] or truth.get("pending_order_count") != 0
                    or _number(matched["filled_quantity"]) != _number(truth["filled_quantity"])
                    or _number(matched["position_quantity"]) != _number(truth["position_quantity"])):
                return outcome("DRIFTED", "FOUR_WAY_NATIVE_ORDER_OR_POSITION_DELTA")
            for key in ("cash", "available", "frozen_margin"):
                if abs(_number(matched[key]) - _number(truth[key])) > Decimal("0.01"):
                    return outcome("DRIFTED", "FOUR_WAY_NATIVE_MONEY_DELTA")
            return outcome("MATCHED", "FOUR_INDEPENDENT_RECEIPTS_MATCH_REAL_NATIVE_FACTS", legs)
        except PaperDenied as exc:
            return outcome("UNKNOWN", exc.code)
        except Exception:
            # Do not disclose private upstream exception text or retry a read.
            return outcome("UNKNOWN", "FOUR_WAY_INDEPENDENT_READ_FAILED")

    def daily_close_history(self, contract: str, now: datetime) -> Mapping:
        if self.history_reader is None:
            raise PaperDenied("OFFICIAL_DAILY_HISTORY_READER_UNWIRED")
        result = self.history_reader(_contract(contract), now)
        if not isinstance(result, Mapping) or result.get("source") != "independent_shfe_dated_daily_close_readback":
            raise PaperDenied("OFFICIAL_DAILY_HISTORY_SOURCE_MISMATCH")
        completed = _time(self.clock())
        observed = _fresh(result.get("observed_at"), completed, 15)
        if not observed <= _time(result.get("available_at")) <= completed:
            raise PaperDenied("OFFICIAL_DAILY_HISTORY_AVAILABLE_TIME_INVALID")
        return result

    def reconciliation_probe(self) -> bool:
        sources = ("capital_intent_ledger", "yuanli_execution_ledger", "execution_oms_readback", "simnow_broker_custodian_readback")
        if set(self.reconciliation_readers) != set(sources) or len({id(self.reconciliation_readers[s]) for s in sources}) != 4:
            raise PaperDenied("FOUR_INDEPENDENT_RECONCILIATION_READERS_UNWIRED")
        investor, _, _ = self._identity()
        legs = [self.reconciliation_readers[source]() for source in sources]
        if (self.receipt_verifier is None or any(not isinstance(leg, Mapping) for leg in legs)
                or any(self.receipt_verifier(leg) is not True for leg in legs)):
            raise PaperDenied("FOUR_WAY_RECEIPT_AUTHENTICITY_UNVERIFIED")
        if any(leg.get("environment") != SIMNOW_FIRST or leg.get("account_id") != investor for leg in legs):
            raise PaperDenied("FOUR_WAY_ENVIRONMENT_MISMATCH")
        self.last_reconciliation_result = reconcile_four_way(*legs, as_of=self.clock())
        return self.last_reconciliation_result["status"] == "MATCHED"

    def strategy_equity_mark(self) -> Mapping:
        if self.equity_reader is None:
            raise PaperDenied("STRATEGY_SUBLEDGER_UNWIRED")
        # Root's segregated accounting module owns allocation/fill/fee/NAV
        # validation. This slot must never copy total broker balance into NAV.
        return self.equity_reader()

    def callbacks(self) -> dict[str, Callable]:
        return {name: getattr(self, name) for name in ("account_attestation", "current_margin",
            "current_round_trip_fee_upper", "terminal_truth", "daily_close_history", "reconciliation_probe", "strategy_equity_mark")}
