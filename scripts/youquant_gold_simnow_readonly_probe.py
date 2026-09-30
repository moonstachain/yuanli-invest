"""One-file, read-only GOLD2 probe for a dedicated YouQuant SimNow robot.

Paste this file into a separate Python strategy and let YouQuant call ``main``
once during an AU trading session.  It has no credential, grant, order, cancel,
command, persistence, or import from this repository.  A successful probe is
only a host readback observation, never SimNow environment attestation.
Python 3.9 may run this diagnosis; the production paper runtime still requires
Python 3.12 and this probe never supplies its authority or executes it.
"""

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
import sys
import time


SCHEMA = "gold2-au-simnow-readonly-host-probe.v1"
PROBE_CONTRACT = "au2612"  # Review and change to an eligible dated AU month before use.
MAX_QUOTE_AGE_MS = 15000
CONNECTION_WAIT_SECONDS = 30
CONNECTION_POLL_MS = 1000
CONNECTION_MAX_CHECKS = 1 + CONNECTION_WAIT_SECONDS * 1000 // CONNECTION_POLL_MS
AU_DATED = re.compile(r"^au[0-9]{4}$")
READ_ONLY_METHODS = ("IO", "SetContractType", "GetAccount", "GetPositions",
                     "GetOrders", "GetTicker")
SHANGHAI = timezone(timedelta(hours=8))


class ProbeBlocked(ValueError):
    """Only fixed, non-sensitive reason codes may reach the probe report."""


def _field(value, name):
    if isinstance(value, Mapping):
        return value.get(name)
    return getattr(value, name, None)


def _number(value, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ProbeBlocked("INVALID_NUMERIC_READBACK")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ProbeBlocked("INVALID_NUMERIC_READBACK")
    if not parsed.is_finite() or (parsed <= 0 if positive else parsed < 0):
        raise ProbeBlocked("INVALID_NUMERIC_READBACK")
    return parsed


def _digest(selected):
    raw = json.dumps(selected, sort_keys=True, ensure_ascii=False,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _eligible_contract(contract, now):
    if not isinstance(contract, str) or AU_DATED.fullmatch(contract) is None:
        return False
    year, month = 2000 + int(contract[2:4]), int(contract[4:6])
    if not 1 <= month <= 12:
        return False
    local = now.astimezone(SHANGHAI)
    # This checks only the V1 delivery-month distance. It does not choose a
    # liquid contract or replace the frozen 08:30 selector.
    return year * 12 + month >= local.year * 12 + local.month + 2


def _metadata(meta, contract):
    if not isinstance(meta, Mapping):
        raise ProbeBlocked("CONTRACT_METADATA_UNREADABLE")
    if meta.get("InstrumentID") != contract or meta.get("ExchangeID") != "SHFE":
        raise ProbeBlocked("CONTRACT_IDENTITY_MISMATCH")
    if _number(meta.get("VolumeMultiple"), positive=True) != Decimal("1000"):
        raise ProbeBlocked("CONTRACT_SPEC_MISMATCH")
    if _number(meta.get("PriceTick"), positive=True) != Decimal("0.02"):
        raise ProbeBlocked("CONTRACT_SPEC_MISMATCH")
    if (type(meta.get("DeliveryYear")) is not int
            or meta["DeliveryYear"] != 2000 + int(contract[2:4])
            or type(meta.get("DeliveryMonth")) is not int
            or meta["DeliveryMonth"] != int(contract[4:6])):
        raise ProbeBlocked("CONTRACT_DELIVERY_MISMATCH")
    if meta.get("IsTrading") not in (1, True):
        raise ProbeBlocked("CONTRACT_NOT_TRADING")
    return {"instrument": contract, "exchange": "SHFE",
            "multiplier": "1000", "tick": "0.02",
            "delivery_year": meta["DeliveryYear"],
            "delivery_month": meta["DeliveryMonth"], "is_trading": True}


def _account(account):
    info = _field(account, "Info")
    if not isinstance(info, Mapping):
        raise ProbeBlocked("ACCOUNT_INFO_UNREADABLE")
    account_id = info.get("InvestorID") or info.get("AccountID")
    if (not isinstance(account_id, (str, int)) or isinstance(account_id, bool)
            or not str(account_id) or str(account_id) == "0"):
        raise ProbeBlocked("ACCOUNT_ID_UNOBSERVABLE")
    if str(info.get("BrokerID")) != "9999":
        raise ProbeBlocked("SIMNOW_BROKER_ID_NOT_OBSERVED")
    balance = _number(_field(account, "Balance"))
    equity = _number(_field(account, "Equity"), positive=True)
    return {"account_id": str(account_id), "broker_id": "9999",
            "balance": str(balance), "equity": str(equity)}


def _positions(raw, contract):
    if not isinstance(raw, (list, tuple)):
        raise ProbeBlocked("POSITIONS_UNREADABLE")
    selected = []
    non_target = 0
    for item in raw:
        instrument = _field(item, "ContractType") or _field(item, "Symbol")
        kind = _field(item, "Type")
        amount = _number(_field(item, "Amount"), positive=True)
        margin = _number(_field(item, "Margin"))
        if (not isinstance(instrument, str) or not instrument
                or type(kind) is not int or amount != amount.to_integral_value()):
            raise ProbeBlocked("POSITION_SHAPE_UNREADABLE")
        if instrument != contract:
            non_target += 1
        selected.append({"contract": instrument, "type": kind,
                         "amount": str(amount), "margin": str(margin)})
    return selected, non_target


def _orders(raw):
    if not isinstance(raw, (list, tuple)):
        raise ProbeBlocked("ORDERS_UNREADABLE")
    selected = []
    for item in raw:
        order_id = _field(item, "Id")
        if (not isinstance(order_id, (str, int)) or isinstance(order_id, bool)
                or not str(order_id) or str(order_id) == "0"):
            raise ProbeBlocked("ORDER_ID_UNOBSERVABLE")
        selected.append({"id": str(order_id)})
    return selected


def _ticker(raw, now):
    bid = _number(_field(raw, "Buy"), positive=True)
    last = _number(_field(raw, "Last"), positive=True)
    raw_time = _field(raw, "Time")
    if isinstance(raw_time, bool) or not isinstance(raw_time, (str, int)):
        raise ProbeBlocked("QUOTE_TIME_UNREADABLE")
    if not re.fullmatch(r"[0-9]{13}", str(raw_time)):
        raise ProbeBlocked("QUOTE_TIME_UNREADABLE")
    age_ms = int(now.timestamp() * 1000) - int(raw_time)
    if not 0 <= age_ms <= MAX_QUOTE_AGE_MS:
        raise ProbeBlocked("QUOTE_STALE_OR_FUTURE")
    return {"bid": str(bid), "last": str(last), "time_ms": int(raw_time)}, age_ms


def inspect_host(host_globals, contract=PROBE_CONTRACT, now=None, monotonic=None):
    """Call only allowlisted read-only host methods; fail closed."""
    use_live_quote_clock = now is None
    now = now or datetime.now(timezone.utc)
    monotonic = monotonic or time.monotonic
    selected = {}
    attempted = []
    stage = "precheck"
    report = {
        "schema_version": SCHEMA,
        "status": "HOST_READBACK_BLOCKED",
        "reason_code": None,
        "stage": stage,
        "python_version": "%s.%s.%s" % tuple(sys.version_info[:3]),
        "production_python_minimum": "3.12",
        "python_supported": sys.version_info >= (3, 12),
        "probe_python_minimum": "3.9",
        "probe_python_supported": sys.version_info >= (3, 9),
        "contract": contract if isinstance(contract, str) and AU_DATED.fullmatch(contract) else None,
        "attempted_query_methods": attempted,
        "broker_account_identity_attested": False,
        "simnow_first_normal_attested": False,
        "robot_binding_attested": False,
        "paper_authority_enabled": False,
        "order_api_calls": 0,
        "connection_checks": 0,
        "connection_wait_ms": 0,
    }
    try:
        if not report["probe_python_supported"]:
            raise ProbeBlocked("PROBE_PYTHON_VERSION_UNSUPPORTED")
        if not isinstance(host_globals, Mapping) or now.tzinfo is None or now.utcoffset() is None:
            raise ProbeBlocked("HOST_CONTEXT_INVALID")
        if not _eligible_contract(contract, now):
            raise ProbeBlocked("CONTRACT_NOT_ELIGIBLE_DATED_AU")
        exchange = host_globals.get("exchange")
        if exchange is None or exchange is False:
            raise ProbeBlocked("EXCHANGE_MISSING")

        stage = "connection"
        attempted.append("IO")
        deadline = monotonic() + CONNECTION_WAIT_SECONDS
        while True:
            status = exchange.IO("status")
            report["connection_checks"] += 1
            if status is True or (type(status) is int and status == 1):
                break
            remaining_ms = int((deadline - monotonic()) * 1000)
            if remaining_ms <= 0 or report["connection_checks"] >= CONNECTION_MAX_CHECKS:
                raise ProbeBlocked("EXCHANGE_NOT_CONNECTED_TIMEOUT")
            sleeper = host_globals.get("Sleep")
            if not callable(sleeper):
                raise ProbeBlocked("HOST_SLEEP_UNAVAILABLE")
            delay_ms = min(CONNECTION_POLL_MS, remaining_ms)
            sleeper(delay_ms)
            report["connection_wait_ms"] += delay_ms

        stage = "contract_metadata"
        attempted.append("SetContractType")
        selected["metadata"] = _metadata(exchange.SetContractType(contract), contract)

        stage = "account"
        attempted.append("GetAccount")
        selected["account"] = _account(exchange.GetAccount())

        stage = "positions"
        attempted.append("GetPositions")
        selected["positions"], non_target = _positions(exchange.GetPositions(), contract)
        report["position_count"] = len(selected["positions"])
        report["non_target_position_count"] = non_target

        stage = "orders"
        attempted.append("GetOrders")
        selected["orders"] = _orders(exchange.GetOrders())
        report["open_order_count"] = len(selected["orders"])

        stage = "quote"
        attempted.append("GetTicker")
        quote_now = datetime.now(timezone.utc) if use_live_quote_clock else now
        selected["quote"], quote_age_ms = _ticker(exchange.GetTicker(), quote_now)
        report["quote_age_ms"] = quote_age_ms
        report["status"] = "HOST_READBACK_OBSERVED_UNATTESTED"
        report["reason_code"] = "NONE"
        stage = "complete"
    except ProbeBlocked as exc:
        report["reason_code"] = str(exc)
    except Exception:
        # Never expose exception text: providers may include account details.
        report["reason_code"] = "HOST_QUERY_EXCEPTION"
    report["stage"] = stage
    report["selected_readback_sha256"] = _digest(selected)
    return report


def main():
    report = inspect_host(globals())
    rendered = json.dumps(report, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"))
    logger = globals().get("Log")
    if callable(logger):
        logger("GOLD2_SIMNOW_READ_ONLY_HOST_PROBE", rendered)
    else:
        print(rendered)
    return report
