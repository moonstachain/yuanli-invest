"""Bounded, provider-neutral GOLD2 broker-paper execution contracts.

This is a *separate* paper-program candidate.  It does not change YEX0's
constitution-only receipt or grant authority to its shadow runtime.  A running
adapter needs an explicit PaperGrant and an independently observed SimNow
identity.  No credential, real-account mode, or network transport lives here.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import json
import re
from typing import Any, Mapping
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
SIMNOW_FIRST = "SIMNOW_FIRST_NORMAL"
PROGRAM = "GOLD2_AU_V1_BROKER_PAPER"
MULTIPLIER = Decimal("1000")
TICK = Decimal("0.02")
EXIT_SUBMISSION_LEAD = timedelta(minutes=15)
ZERO_HASH = "0" * 64
AU_DATED = re.compile(r"^au\d{4}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{7,127}$")
COMMAND_FIELDS = frozenset({
    "schema_version", "program", "command_id", "action_contract_id",
    "execution_intent_id", "capital_admission_id", "human_approval_ref",
    "program_approval_ref", "decision_at", "issued_at", "not_before_at",
    "expires_at", "environment", "account_id", "robot_id", "contract",
    "action", "reason", "quantity", "reference_price", "limit_price",
    "stop_price", "exit_not_after_at", "roll_not_after_at",
    "credit_multiplier", "volatility_multiplier", "max_slippage_bps",
    "evidence_hash", "contract_hash", "live_execution_authorized",
    "real_capital_movement_authorized",
})


class PaperDenied(ValueError):
    """A machine-readable fail-closed decision; never retry blindly."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _time(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise PaperDenied("INVALID_" + field.upper())
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PaperDenied("INVALID_" + field.upper()) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PaperDenied("NAIVE_" + field.upper())
    return parsed.astimezone(timezone.utc)


def _number(value: Any, field: str, *, positive: bool = True) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise PaperDenied("INVALID_" + field.upper())
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise PaperDenied("INVALID_" + field.upper()) from exc
    if not number.is_finite() or (number <= 0 if positive else number < 0):
        raise PaperDenied("INVALID_" + field.upper())
    return number


def _ident(value: Any, field: str) -> None:
    if not isinstance(value, str) or IDENTIFIER.fullmatch(value) is None:
        raise PaperDenied("INVALID_" + field.upper())


def action_hash(payload: Mapping[str, Any]) -> str:
    """Hash every contract field other than its self-reference."""
    return _digest({key: value for key, value in payload.items() if key != "contract_hash"})


def sign_command(payload: Mapping[str, Any], key: bytes) -> dict[str, Any]:
    """Create an exact-field signed ActionContract delivery envelope."""
    if not isinstance(key, bytes) or len(key) < 32:
        raise PaperDenied("WEAK_SIGNING_KEY")
    body = deepcopy(dict(payload))
    if set(body) not in (COMMAND_FIELDS, COMMAND_FIELDS - {"contract_hash"}):
        raise PaperDenied("COMMAND_FIELD_MISMATCH")
    body["contract_hash"] = action_hash(body)
    signature = hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
    return {"payload": body, "signature": "hmac-sha256:" + signature}


def verify_command(envelope: Mapping[str, Any] | str, key: bytes) -> dict[str, Any]:
    """Verify HMAC and content hash before any use of command fields."""
    if isinstance(envelope, str):
        try:
            envelope = json.loads(envelope)
        except (ValueError, TypeError) as exc:
            raise PaperDenied("INVALID_COMMAND_JSON") from exc
    if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "signature"}:
        raise PaperDenied("INVALID_COMMAND_ENVELOPE")
    body = envelope["payload"]
    if not isinstance(body, dict) or set(body) != COMMAND_FIELDS:
        raise PaperDenied("COMMAND_FIELD_MISMATCH")
    if not isinstance(key, bytes) or len(key) < 32:
        raise PaperDenied("WEAK_SIGNING_KEY")
    signature = envelope["signature"]
    if not isinstance(signature, str) or not re.fullmatch(r"hmac-sha256:[0-9a-f]{64}", signature):
        raise PaperDenied("INVALID_SIGNATURE")
    expected = "hmac-sha256:" + hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise PaperDenied("SIGNATURE_MISMATCH")
    if not isinstance(body["contract_hash"], str) or not hmac.compare_digest(body["contract_hash"], action_hash(body)):
        raise PaperDenied("CONTRACT_HASH_MISMATCH")
    return deepcopy(body)


@dataclass(frozen=True)
class PaperGrant:
    """Separate paper-program authority, never inferred from YEX0 or a signal."""

    program_approval_ref: str
    human_approval_ref: str
    account_id: str
    robot_id: int
    starts_at: str
    expires_at: str
    enabled: bool = False
    environment: str = SIMNOW_FIRST
    strategy_initial_equity: str = "5000000"
    max_risk_fraction: str = "0.005"
    max_drawdown_fraction: str = "0.05"
    max_margin_fraction: str = "0.30"
    max_slippage_bps: str = "20"
    engineering_test_command_id: str | None = None


class PaperLedger:
    """Append-only hash-chained events; projections are never stored as truth."""

    def __init__(self, events: list[dict[str, Any]] | None = None):
        self._events = deepcopy(events or [])
        self.verify_chain()

    @property
    def events(self) -> list[dict[str, Any]]:
        return deepcopy(self._events)

    @property
    def root_hash(self) -> str:
        return self._events[-1]["event_hash"] if self._events else ZERO_HASH

    def verify_chain(self) -> None:
        previous = ZERO_HASH
        for index, event in enumerate(self._events):
            if not isinstance(event, dict) or set(event) != {"sequence", "kind", "command_id", "at", "data", "previous_hash", "event_hash"}:
                raise PaperDenied("LEDGER_EVENT_SHAPE")
            if event["sequence"] != index + 1 or event["previous_hash"] != previous:
                raise PaperDenied("LEDGER_CHAIN_BROKEN")
            _time(event["at"], "event_at")
            material = {key: val for key, val in event.items() if key != "event_hash"}
            if event["event_hash"] != _digest(material):
                raise PaperDenied("LEDGER_HASH_MISMATCH")
            previous = event["event_hash"]

    def append(self, kind: str, command_id: str, at: str, data: Mapping[str, Any]) -> dict[str, Any]:
        _ident(command_id, "command_id")
        _time(at, "event_at")
        if not isinstance(kind, str) or not re.fullmatch(r"[A-Z][A-Za-z]+", kind):
            raise PaperDenied("INVALID_EVENT_KIND")
        if not isinstance(data, Mapping):
            raise PaperDenied("INVALID_EVENT_DATA")
        event = {
            "sequence": len(self._events) + 1,
            "kind": kind,
            "command_id": command_id,
            "at": at,
            "data": deepcopy(dict(data)),
            "previous_hash": self.root_hash,
        }
        event["event_hash"] = _digest(event)
        self._events.append(event)
        return deepcopy(event)

    def command_hashes(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for event in self._events:
            if event["kind"] == "ActionAdmitted":
                old = result.get(event["command_id"])
                new = event["data"].get("contract_hash")
                if old is not None and old != new:
                    raise PaperDenied("IDEMPOTENCY_KEY_CONFLICT")
                result[event["command_id"]] = new
        return result

    def unresolved_submissions(self) -> set[str]:
        attempted: set[str] = set()
        terminal: set[str] = set()
        for event in self._events:
            if event["kind"] == "OrderSubmitAttempted":
                attempted.add(event["command_id"])
            elif event["kind"] in {"OrderRejectedReconciled", "OrderFilledReconciled", "OrderCanceledReconciled"}:
                terminal.add(event["command_id"])
        return attempted - terminal

    def is_frozen(self) -> bool:
        return bool(self.unresolved_submissions()) or any(
            event["kind"] in {"IncidentFrozen", "ReconciliationDrifted"}
            for event in self._events
        )

    def strategy_equity(self, initial: Decimal) -> tuple[Decimal, Decimal]:
        equity = peak = initial
        for event in self._events:
            if event["kind"] == "EquityMarked":
                equity = _number(event["data"].get("equity"), "marked_equity")
                peak = max(peak, equity)
        return equity, peak

    def latest_equity_mark(self) -> Mapping[str, Any] | None:
        marks = [event["data"] for event in self._events if event["kind"] == "EquityMarked"]
        return deepcopy(marks[-1]) if marks else None


def validate_strategy_equity_mark(mark: Mapping[str, Any], provider: Mapping[str, Any],
                                  now: datetime, ledger: PaperLedger | None = None) -> Decimal:
    """Require an independent, freshly reconciled dedicated-strategy mark."""
    if not isinstance(mark, Mapping) or mark.get("source") != "independent_strategy_accounting" or mark.get("reconciled") is not True:
        raise PaperDenied("STRATEGY_EQUITY_MARK_MISSING")
    if (mark.get("environment") != SIMNOW_FIRST or mark.get("account_id") != provider.get("account_id")
            or mark.get("allocation_scope") not in {"DEDICATED_STRATEGY_PAPER_ACCOUNT", "SEGREGATED_GOLD2_PAPER_SUBLEDGER_V1"}):
        raise PaperDenied("STRATEGY_EQUITY_SCOPE_MISMATCH")
    observed = _time(mark.get("observed_at"), "equity_observed_at")
    if not timedelta(0) <= now.astimezone(timezone.utc) - observed <= timedelta(seconds=15):
        raise PaperDenied("STRATEGY_EQUITY_MARK_STALE")
    if not isinstance(mark.get("raw_sha256"), str) or SHA256.fullmatch(mark["raw_sha256"]) is None:
        raise PaperDenied("STRATEGY_EQUITY_EVIDENCE_MISSING")
    equity = _number(mark.get("equity"), "marked_equity")
    broker = _number(mark.get("broker_equity"), "marked_broker_equity")
    if abs(broker - _number(provider.get("broker_equity"), "broker_equity")) > Decimal("0.01"):
        raise PaperDenied("STRATEGY_EQUITY_BROKER_DELTA")
    if mark.get("allocation_scope") == "SEGREGATED_GOLD2_PAPER_SUBLEDGER_V1":
        if ledger is None:
            raise PaperDenied("ACCOUNTING_MARK_LEDGER_PREFIX_MISSING")
        from yuanli_invest.gold_au_strategy_accounting import validate_strategy_subledger_mark
        return validate_strategy_subledger_mark(mark, now, ledger)
    if abs(equity - broker) > Decimal("0.01"):
        raise PaperDenied("STRATEGY_EQUITY_BROKER_DELTA")
    return equity


def _validate_body(body: Mapping[str, Any], grant: PaperGrant, now: datetime) -> None:
    if body["schema_version"] != "1.0.0" or body["program"] != PROGRAM:
        raise PaperDenied("UNAUTHORIZED_PROGRAM")
    for field in ("command_id", "action_contract_id", "execution_intent_id", "capital_admission_id", "human_approval_ref", "program_approval_ref"):
        _ident(body[field], field)
    if type(body["robot_id"]) is not int or body["robot_id"] <= 0:
        raise PaperDenied("INVALID_ROBOT_ID")
    if body["environment"] != SIMNOW_FIRST or body["account_id"] != grant.account_id or body["robot_id"] != grant.robot_id:
        raise PaperDenied("PAPER_IDENTITY_MISMATCH")
    if body["human_approval_ref"] != grant.human_approval_ref or body["program_approval_ref"] != grant.program_approval_ref:
        raise PaperDenied("APPROVAL_REFERENCE_MISMATCH")
    if body["live_execution_authorized"] is not False or body["real_capital_movement_authorized"] is not False:
        raise PaperDenied("LIVE_OR_CAPITAL_FLAG")
    if not isinstance(body["contract"], str) or AU_DATED.fullmatch(body["contract"]) is None:
        raise PaperDenied("NOT_A_DATED_AU_CONTRACT")
    if body["action"] not in {"OPEN_LONG", "CLOSE_LONG"} or type(body["quantity"]) is not int or body["quantity"] != 1:
        raise PaperDenied("ORDER_SCOPE_EXPANSION")
    if body["reason"] not in {"ENTRY", "EXIT_TREND", "EXIT_TIME", "EXIT_STOP", "EXIT_ROLL", "ENGINEERING_TEST"}:
        raise PaperDenied("INVALID_ORDER_REASON")
    if (body["action"] == "OPEN_LONG") != (body["reason"] in {"ENTRY", "ENGINEERING_TEST"}):
        raise PaperDenied("ACTION_REASON_MISMATCH")
    if not isinstance(body["evidence_hash"], str) or SHA256.fullmatch(body["evidence_hash"]) is None:
        raise PaperDenied("MISSING_EVIDENCE_HASH")
    if not grant.enabled or grant.environment != SIMNOW_FIRST:
        raise PaperDenied("PAPER_PROGRAM_DISABLED")
    if (_number(grant.strategy_initial_equity, "strategy_initial_equity") != Decimal("5000000")
            or _number(grant.max_risk_fraction, "max_risk_fraction") > Decimal("0.005")
            or _number(grant.max_drawdown_fraction, "max_drawdown_fraction") > Decimal("0.05")
            or _number(grant.max_margin_fraction, "max_margin_fraction") > Decimal("0.30")
            or _number(grant.max_slippage_bps, "grant_slippage", positive=False) > Decimal("20")):
        raise PaperDenied("PAPER_GRANT_EXCEEDS_FROZEN_V1_LIMITS")
    if body["reason"] == "ENGINEERING_TEST" and body["command_id"] != grant.engineering_test_command_id:
        raise PaperDenied("ENGINEERING_TEST_NOT_EXACTLY_GRANTED")
    decision = _time(body["decision_at"], "decision_at")
    issued = _time(body["issued_at"], "issued_at")
    start = _time(body["not_before_at"], "not_before_at")
    end = _time(body["expires_at"], "expires_at")
    if not (_time(grant.starts_at, "grant_starts_at") <= now <= _time(grant.expires_at, "grant_expires_at")):
        raise PaperDenied("GRANT_NOT_CURRENT")
    if not (decision <= issued <= start <= now <= end <= issued + timedelta(minutes=5)):
        raise PaperDenied("COMMAND_EXPIRED_OR_FUTURE")
    if body["action"] == "OPEN_LONG" and body["reason"] == "ENTRY":
        local_decision = decision.astimezone(SHANGHAI)
        local_now = now.astimezone(SHANGHAI)
        if (local_decision.hour, local_decision.minute) != (8, 30) or local_decision.date() != local_now.date():
            raise PaperDenied("ENTRY_DECISION_WINDOW")
        if not ((9, 0) <= (local_now.hour, local_now.minute) < (9, 5)):
            raise PaperDenied("ENTRY_EXECUTION_WINDOW")
    if body["action"] == "OPEN_LONG":
        local_decision = decision.astimezone(SHANGHAI)
        delivery_year = 2000 + int(body["contract"][2:4])
        delivery_month = int(body["contract"][4:6])
        if not 1 <= delivery_month <= 12 or delivery_year * 12 + delivery_month < local_decision.year * 12 + local_decision.month + 2:
            raise PaperDenied("DELIVERY_TOO_NEAR")
        if _time(grant.expires_at, "grant_expires_at") < max(
            _time(body["exit_not_after_at"], "exit_not_after_at"),
            _time(body["roll_not_after_at"], "roll_not_after_at"),
        ):
            raise PaperDenied("GRANT_EXPIRES_BEFORE_CONTINGENT_EXIT")
    reference = _number(body["reference_price"], "reference_price")
    limit = _number(body["limit_price"], "limit_price")
    if limit % TICK != 0:
        raise PaperDenied("INVALID_TICK_PRICE")
    slippage = _number(body["max_slippage_bps"], "max_slippage_bps", positive=False)
    if slippage > _number(grant.max_slippage_bps, "grant_slippage"):
        raise PaperDenied("SLIPPAGE_SCOPE_EXPANSION")
    allowance = slippage / Decimal("10000")
    if body["action"] == "OPEN_LONG" and limit > reference * (1 + allowance):
        raise PaperDenied("OPEN_LIMIT_TOO_AGGRESSIVE")
    if body["action"] == "CLOSE_LONG" and limit < reference * (1 - allowance):
        raise PaperDenied("CLOSE_LIMIT_TOO_AGGRESSIVE")
    for field in ("credit_multiplier", "volatility_multiplier"):
        if _number(body[field], field) not in {Decimal("0.5"), Decimal("1")}:
            raise PaperDenied("INVALID_RISK_MULTIPLIER")
    for field in ("exit_not_after_at", "roll_not_after_at"):
        deadline = _time(body[field], field)
        if deadline <= decision or deadline > decision + timedelta(days=45):
            raise PaperDenied("INVALID_EXIT_DEADLINE")
    if body["action"] == "OPEN_LONG":
        stop = _number(body["stop_price"], "stop_price")
        if stop % TICK != 0 or stop >= limit:
            raise PaperDenied("INVALID_STOP_PRICE")
    elif body["stop_price"] is not None:
        raise PaperDenied("CLOSE_COMMAND_STOP_SCOPE")


def admit_command(
    envelope: Mapping[str, Any] | str,
    signing_key: bytes,
    grant: PaperGrant,
    provider_snapshot: Mapping[str, Any],
    ledger: PaperLedger,
    now: datetime,
) -> dict[str, Any]:
    """Runtime proof for one paper order. Raises PaperDenied on any unknown.

    provider_snapshot must be produced by an independent broker readback and
    account-identity attestation, not copied from the command or deployment label.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise PaperDenied("NAIVE_NOW")
    now = now.astimezone(timezone.utc)
    ledger.verify_chain()
    body = verify_command(envelope, signing_key)
    _validate_body(body, grant, now)
    if not isinstance(provider_snapshot, Mapping) or provider_snapshot.get("source") != "provider_readback":
        raise PaperDenied("NO_PROVIDER_READBACK")
    if provider_snapshot.get("identity_verified") is not True or provider_snapshot.get("environment") != SIMNOW_FIRST:
        raise PaperDenied("UNVERIFIED_SIMNOW_IDENTITY")
    if provider_snapshot.get("account_id") != body["account_id"] or provider_snapshot.get("robot_id") != body["robot_id"]:
        raise PaperDenied("PROVIDER_IDENTITY_MISMATCH")
    if provider_snapshot.get("connected") is not True or provider_snapshot.get("reconciled") is not True:
        raise PaperDenied("PROVIDER_STATE_UNKNOWN")
    observed_age = now - _time(provider_snapshot.get("observed_at"), "provider_observed_at")
    if observed_age < timedelta(0) or observed_age > timedelta(seconds=15):
        raise PaperDenied("STALE_PROVIDER_STATE")
    meta = provider_snapshot.get("contract_meta")
    validate_au_metadata(meta, body["contract"])
    seen = ledger.command_hashes()
    if body["command_id"] in seen:
        if seen[body["command_id"]] == body["contract_hash"]:
            return {"decision": "DUPLICATE_NO_SUBMIT", "command_id": body["command_id"]}
        raise PaperDenied("IDEMPOTENCY_KEY_CONFLICT")
    if ledger.is_frozen():
        raise PaperDenied("UNRESOLVED_ORDER_OR_DRIFT")
    if provider_snapshot.get("open_order_ids") != []:
        raise PaperDenied("EXTERNAL_OPEN_ORDER")
    positions = provider_snapshot.get("positions")
    if not isinstance(positions, list):
        raise PaperDenied("POSITION_READBACK_UNKNOWN")
    total = Decimal(0)
    for position in positions:
        if not isinstance(position, Mapping) or position.get("contract") != body["contract"] or position.get("side") != "LONG":
            raise PaperDenied("EXTERNAL_OR_SHORT_POSITION")
        total += _number(position.get("quantity"), "position_quantity")
        if position.get("age") not in {"TODAY", "YESTERDAY"}:
            raise PaperDenied("POSITION_AGE_UNKNOWN")
    if body["action"] == "OPEN_LONG":
        mark = ledger.latest_equity_mark()
        validate_strategy_equity_mark(mark, provider_snapshot, now, ledger)
        equity, peak = ledger.strategy_equity(_number(grant.strategy_initial_equity, "strategy_initial_equity"))
        if total != 0 or positions:
            raise PaperDenied("MAX_ONE_LOT")
        if (peak - equity) / peak >= _number(grant.max_drawdown_fraction, "max_drawdown_fraction"):
            raise PaperDenied("DRAWDOWN_STOP")
        stop = _number(body["stop_price"], "stop_price")
        limit = _number(body["limit_price"], "limit_price")
        allowed_loss = equity * _number(grant.max_risk_fraction, "max_risk_fraction")
        allowed_loss *= _number(body["credit_multiplier"], "credit_multiplier")
        allowed_loss *= _number(body["volatility_multiplier"], "volatility_multiplier")
        round_trip_fees = _number(provider_snapshot.get("round_trip_fee_upper_cny"), "round_trip_fee_upper_cny", positive=False)
        if (limit - stop) * MULTIPLIER + round_trip_fees > allowed_loss:
            raise PaperDenied("PLANNED_LOSS_LIMIT")
        margin = _number(provider_snapshot.get("margin_for_one_lot"), "margin_for_one_lot")
        used = _number(provider_snapshot.get("margin_in_use"), "margin_in_use", positive=False)
        available = _number(provider_snapshot.get("available"), "available")
        _number(provider_snapshot.get("broker_equity"), "broker_equity")
        if margin > available or (used + margin) > equity * _number(grant.max_margin_fraction, "max_margin_fraction"):
            raise PaperDenied("MARGIN_LIMIT")
    elif total != 1 or len(positions) != 1:
        raise PaperDenied("CLOSE_POSITION_MISMATCH")
    return {"decision": "ALLOW", "command": body, "position_age": positions[0]["age"] if positions else None}


def close_direction(position_age: str) -> str:
    if position_age == "TODAY":
        return "closebuy_today"
    if position_age == "YESTERDAY":
        return "closebuy"
    raise PaperDenied("POSITION_AGE_UNKNOWN")


def validate_au_metadata(meta: Mapping[str, Any], contract: str) -> None:
    """Reject historical/provider metadata drift before any physical AU order."""
    if not isinstance(meta, Mapping) or not isinstance(contract, str) or AU_DATED.fullmatch(contract) is None:
        raise PaperDenied("CONTRACT_IDENTITY_MISMATCH")
    if meta.get("InstrumentID") != contract or meta.get("ExchangeID") != "SHFE":
        raise PaperDenied("CONTRACT_IDENTITY_MISMATCH")
    if _number(meta.get("VolumeMultiple"), "volume_multiple") != MULTIPLIER or _number(meta.get("PriceTick"), "price_tick") != TICK:
        raise PaperDenied("CONTRACT_SPEC_MISMATCH")
    if meta.get("DeliveryYear") != 2000 + int(contract[2:4]) or meta.get("DeliveryMonth") != int(contract[4:6]):
        raise PaperDenied("CONTRACT_DELIVERY_METADATA_MISMATCH")
    if meta.get("IsTrading") not in {1, True}:
        raise PaperDenied("CONTRACT_NOT_TRADING")


def contingent_exit_reason(position: Mapping[str, Any], quote_price: Any, now: datetime) -> str | None:
    """Cloud-managed stop / roll / 20-day deadlines pre-authorized at entry."""
    if not isinstance(position, Mapping) or position.get("contingent_exit_authorized") is not True:
        raise PaperDenied("NO_CONTINGENT_EXIT_AUTHORITY")
    _ident(position.get("origin_action_contract_id"), "origin_action_contract_id")
    if now.tzinfo is None or now.utcoffset() is None:
        raise PaperDenied("NAIVE_NOW")
    if _number(quote_price, "quote_price") <= _number(position.get("stop_price"), "stop_price"):
        return "EXIT_STOP"
    if now.astimezone(timezone.utc) >= _time(position.get("roll_not_after_at"), "roll_not_after_at") - EXIT_SUBMISSION_LEAD:
        return "EXIT_ROLL"
    if now.astimezone(timezone.utc) >= _time(position.get("exit_not_after_at"), "exit_not_after_at") - EXIT_SUBMISSION_LEAD:
        return "EXIT_TIME"
    return None


def trend_exit_reason(position: Mapping[str, Any], history: Mapping[str, Any],
                      now: datetime) -> str | None:
    """Prior close below the preceding ten closes after five held sessions.

    History must be an independently read SHFE-session list, ending before
    today's 09:00–09:05 exit window. This is a risk-reducing contingent exit.
    """
    if position.get("contingent_exit_authorized") is not True:
        raise PaperDenied("NO_CONTINGENT_EXIT_AUTHORITY")
    local = now.astimezone(SHANGHAI)
    if not ((9, 0) <= (local.hour, local.minute) < (9, 5)):
        return None
    if (not isinstance(history, Mapping)
            or history.get("source") != "independent_shfe_dated_daily_close_readback"
            or history.get("contract") != position.get("contract")
            or history.get("verified_session_calendar") is not True):
        raise PaperDenied("TREND_HISTORY_UNVERIFIED")
    age = now.astimezone(timezone.utc) - _time(history.get("observed_at"), "trend_history_observed_at")
    if not timedelta(0) <= age <= timedelta(seconds=15):
        raise PaperDenied("TREND_HISTORY_STALE")
    bars = history.get("bars")
    if not isinstance(bars, list) or len(bars) < 11:
        raise PaperDenied("TREND_HISTORY_INCOMPLETE")
    if history.get("next_session_date") != local.date().isoformat():
        raise PaperDenied("TREND_SESSION_CALENDAR_MISMATCH")
    parsed: list[tuple[date, Decimal]] = []
    for item in bars:
        if not isinstance(item, Mapping) or not isinstance(item.get("raw_sha256"), str) or SHA256.fullmatch(item["raw_sha256"]) is None:
            raise PaperDenied("TREND_HISTORY_EVIDENCE_MISSING")
        try:
            session = date.fromisoformat(item["date"])
        except (TypeError, ValueError, KeyError) as exc:
            raise PaperDenied("TREND_HISTORY_DATE_INVALID") from exc
        if session >= local.date() or session.weekday() >= 5 or (parsed and session <= parsed[-1][0]):
            raise PaperDenied("TREND_HISTORY_DATE_INVALID")
        parsed.append((session, _number(item.get("close"), "trend_close")))
    if len({day for day, _ in parsed}) != len(parsed):
        raise PaperDenied("TREND_HISTORY_DATE_INVALID")
    if history.get("last_completed_session_date") != parsed[-1][0].isoformat():
        raise PaperDenied("TREND_SESSION_CALENDAR_MISMATCH")
    try:
        entry_day = date.fromisoformat(position["entry_session_date"])
    except (TypeError, ValueError, KeyError) as exc:
        raise PaperDenied("ENTRY_SESSION_DATE_UNKNOWN") from exc
    held_sessions = sum(day >= entry_day for day, _ in parsed)
    if held_sessions < 5:
        return None
    if parsed[-1][1] < min(price for _, price in parsed[-11:-1]):
        return "EXIT_TREND"
    return None


def reconcile_four_way(
    capital_intent: Mapping[str, Any],
    yuanli_execution: Mapping[str, Any],
    execution_oms: Mapping[str, Any],
    broker_custodian: Mapping[str, Any],
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Compare four independent, current evidence legs before clearing freeze."""
    legs = (capital_intent, yuanli_execution, execution_oms, broker_custodian)
    sources = ("capital_intent_ledger", "yuanli_execution_ledger", "execution_oms_readback", "simnow_broker_custodian_readback")
    if as_of is None or as_of.tzinfo is None or as_of.utcoffset() is None:
        return {"status": "DRIFTED", "reason": "RECONCILIATION_TIME_MISSING"}
    if any(not isinstance(leg, Mapping) for leg in legs):
        return {"status": "DRIFTED", "reason": "MISSING_LEDGER_LEG"}
    raw_hashes = []
    for leg, source in zip(legs, sources):
        if leg.get("source") != source:
            return {"status": "DRIFTED", "reason": "LEDGER_SOURCE_IDENTITY_MISMATCH"}
        raw_hash = leg.get("raw_sha256")
        if not isinstance(raw_hash, str) or SHA256.fullmatch(raw_hash) is None:
            return {"status": "DRIFTED", "reason": "LEDGER_EVIDENCE_MISSING"}
        raw_hashes.append(raw_hash)
        try:
            age = as_of.astimezone(timezone.utc) - _time(leg.get("observed_at"), "leg_observed_at")
        except PaperDenied:
            return {"status": "DRIFTED", "reason": "LEDGER_TIME_MISSING"}
        if not timedelta(0) <= age <= timedelta(seconds=30):
            return {"status": "DRIFTED", "reason": "LEDGER_STALE"}
    if len(set(raw_hashes)) != 4:
        return {"status": "DRIFTED", "reason": "CLONED_LEDGER_EVIDENCE"}
    account = capital_intent.get("account_id")
    contract = capital_intent.get("contract")
    if not account or not isinstance(contract, str) or AU_DATED.fullmatch(contract) is None:
        return {"status": "DRIFTED", "reason": "INVALID_CAPITAL_INTENT"}
    if any(leg.get("account_id") != account or leg.get("contract") != contract for leg in legs):
        return {"status": "DRIFTED", "reason": "IDENTITY_DELTA"}
    try:
        target = _number(capital_intent.get("target_quantity"), "target_quantity", positive=False)
        quantities = [_number(leg.get("position_quantity"), "position_quantity", positive=False) for leg in legs[1:]]
        filled = [_number(leg.get("filled_quantity"), "filled_quantity", positive=False) for leg in legs]
        cash = [_number(leg.get("cash"), "cash", positive=False) for leg in legs]
        available = [_number(leg.get("available"), "available", positive=False) for leg in legs]
        frozen = [_number(leg.get("frozen_margin"), "frozen_margin", positive=False) for leg in legs]
        if any(not isinstance(leg.get("order_ids"), list) or
               any(not isinstance(order, str) or not order for order in leg["order_ids"]) for leg in legs):
            raise TypeError("invalid order IDs")
        orders = [set(leg["order_ids"]) for leg in legs]
    except (PaperDenied, KeyError, TypeError):
        return {"status": "DRIFTED", "reason": "INCOMPLETE_LEDGER_LEG"}
    if target not in {Decimal(0), Decimal(1)} or any(q != target for q in quantities):
        return {"status": "DRIFTED", "reason": "POSITION_DELTA"}
    if not (orders[0] == orders[1] == orders[2] == orders[3]):
        return {"status": "DRIFTED", "reason": "ORDER_DELTA"}
    if len(orders[0]) != len(capital_intent["order_ids"]) or any(value != filled[0] for value in filled[1:]):
        return {"status": "DRIFTED", "reason": "FILL_DELTA"}
    if max(cash) - min(cash) > Decimal("0.01"):
        return {"status": "DRIFTED", "reason": "CASH_DELTA"}
    if max(available) - min(available) > Decimal("0.01"):
        return {"status": "DRIFTED", "reason": "AVAILABLE_DELTA"}
    if max(frozen) - min(frozen) > Decimal("0.01"):
        return {"status": "DRIFTED", "reason": "FROZEN_MARGIN_DELTA"}
    return {"status": "MATCHED", "reason": None, "order_ids": sorted(orders[0]),
            "position_quantity": str(target), "filled_quantity": str(filled[0]),
            "cash": str(cash[0]), "available": str(available[0]), "frozen_margin": str(frozen[0])}
