"""GOLD2 AU SimNow-only YouQuant execution adapter (no stored credentials).

The platform bridge wraps YouQuant's documented GetCommand, _G, CTP exchange
methods.  The execution core is :mod:`yuanli_invest.gold_paper`; deploy both
stdlib-only modules together.  There is deliberately no default grant, HMAC
key, account attestation, or automatic startup: the strategy is inert until
the separately approved paper program supplies each of them.

YouQuant references:
https://www.youquant.com/user-guide/%E6%89%A9%E5%B1%95api%E6%8E%A5%E5%8F%A3
https://www.youquant.com/syntax-guide/fun/futures/exchange.setdirection
https://www.youquant.com/syntax-guide/fun/global/_g
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_FLOOR
import hashlib
import json
import sys
from typing import Any, Callable, Mapping

from yuanli_invest.gold_paper import (
    PaperDenied,
    PaperGrant,
    PaperLedger,
    SHANGHAI,
    SIMNOW_FIRST,
    admit_command,
    close_direction,
    contingent_exit_reason,
    reconcile_four_way,
    trend_exit_reason,
    validate_strategy_equity_mark,
    validate_au_metadata,
)


STORAGE_KEY = "GOLD2_SIMNOW_PAPER_LEDGER_V1"
# V1 candidate allowlist. The 2026-09-25 SimNow product page and current
# YouQuant preset match these fronts; recheck the official page and active host
# connection before a PaperGrant. A platform template is not account proof.
SIMNOW_FIRST_TD_FRONT = "182.254.243.31:30001"
SIMNOW_FIRST_MD_FRONT = "182.254.243.31:30011"


def _field(obj: Any, name: str) -> Any:
    return obj.get(name) if isinstance(obj, Mapping) else getattr(obj, name, None)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _api_result(receipt: Any, method: str, now: datetime) -> Mapping[str, Any] | None:
    """Check a separately captured account API response, not a template label."""
    if not isinstance(receipt, Mapping) or receipt.get("method") != method:
        return None
    try:
        observed = datetime.fromisoformat(str(receipt.get("observed_at")).replace("Z", "+00:00"))
        response = receipt.get("response")
        response_hash = "sha256:" + hashlib.sha256(json.dumps(
            response, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False).encode("utf-8")).hexdigest()
    except (TypeError, ValueError, OverflowError):
        return None
    if (observed.tzinfo is None or not 0 <= (now - observed).total_seconds() <= 300
            or receipt.get("response_sha256") != response_hash
            or not isinstance(response, Mapping) or type(response.get("code")) is not int
            or response.get("code") != 0):
        return None
    data = response.get("data")
    if not isinstance(data, Mapping) or data.get("error") is not None:
        return None
    result = data.get("result")
    return result if isinstance(result, Mapping) else None


def _front(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return value.removeprefix("tcp://")


def _verified_added_ctp_binding(attestation: Mapping[str, Any], robot_id: Any,
                                now: datetime) -> bool:
    """Bind one running robot to a current account-added CTP object and fronts.

    GetExchangeList is the vendor-wide protocol template and is never accepted
    here.  GetPlatformList is the authenticated account's *added* objects.
    """
    platforms_result = _api_result(attestation.get("platform_list_receipt"),
                                   "GetPlatformList", now)
    robot_result = _api_result(attestation.get("robot_detail_receipt"),
                               "GetRobotDetail", now)
    if platforms_result is None or robot_result is None:
        return False
    platforms = platforms_result.get("platforms")
    robot = robot_result.get("robot")
    if (not isinstance(platforms, list) or not isinstance(robot, Mapping)
            or type(platforms_result.get("all")) is not int
            or platforms_result["all"] != len(platforms)
            or type(robot_id) is not int or robot.get("id") != robot_id
            or robot.get("status") != 1):
        return False
    try:
        period, platform_ids, pairs = json.loads(robot.get("strategy_exchange_pairs"))
    except (TypeError, ValueError):
        return False
    if (type(period) is not int or period <= 0
            or not isinstance(platform_ids, list) or len(platform_ids) != 1
            or not isinstance(pairs, list) or len(pairs) != 1
            or pairs[0] not in {"FUTURES", "FUTURES_CTP"}
            or type(platform_ids[0]) is not int or platform_ids[0] <= 0):
        return False
    matching = [item for item in platforms if isinstance(item, Mapping)
                and type(item.get("id")) is int and item.get("id") == platform_ids[0]
                and item.get("eid") == "Futures_CTP"]
    if len(matching) != 1:
        return False
    profiles = matching[0].get("profiles")
    if isinstance(profiles, str):
        try:
            profiles = json.loads(profiles)
        except ValueError:
            return False
    if not isinstance(profiles, Mapping):
        return False
    return (_front(profiles.get("TDFront")) == SIMNOW_FIRST_TD_FRONT
            and _front(profiles.get("MDFront")) == SIMNOW_FIRST_MD_FRONT
            and str(profiles.get("BrokerId")) == "9999")


class _PreSubmitSuppressed(PaperDenied):
    """The broker order API was not called after a final admission check."""


def _entry_window_has_room(now: datetime, *, seconds: int) -> None:
    if now.tzinfo is None or now.utcoffset() is None:
        raise PaperDenied("NAIVE_NOW")
    local = now.astimezone(SHANGHAI)
    cutoff = local.replace(hour=9, minute=5, second=0, microsecond=0)
    if cutoff - local <= timedelta(seconds=seconds):
        raise PaperDenied("ENTRY_WINDOW_INSUFFICIENT")


class YouQuantBridge:
    """Wrap YouQuant calls; attestation/risk/reconciliation are injected.

    The account attestation must include recent *account-added* GetPlatformList
    and GetRobotDetail responses binding this running robot to one CTP object
    whose configured trade/market fronts match the frozen first-normal pair.
    GetExchangeList is only a platform-wide template; a label, BrokerID 9999,
    command field or GetName cannot by itself establish paper identity.
    """

    def __init__(
        self,
        *,
        exchange: Any,
        get_command: Callable[[], Any],
        kv_get: Callable[[str], Any],
        kv_set: Callable[[str, str], Any],
        robot_id_get: Callable[[], Any],
        account_attestation: Callable[[], Mapping[str, Any] | None],
        current_margin: Callable[[str], Any],
        current_round_trip_fee_upper: Callable[[str], Any],
        reconciliation_probe: Callable[[], bool],
        ledger_anchor: Callable[[list[dict[str, Any]], str], Mapping[str, Any] | None] | None,
        atomic_claim: Callable[[str, str, str, str], Mapping[str, Any] | None] | None = None,
        strategy_equity_mark: Callable[[], Mapping[str, Any] | None] | None = None,
        daily_close_history: Callable[[str, datetime], Mapping[str, Any] | None] | None = None,
        pd_long_today: int,
        pd_long_yesterday: int,
        terminal_truth: Callable[[str], Mapping[str, Any] | None] | None = None,
        account_coordinator: Any = None,
        receipt_validation_clock: Callable[[], datetime] | None = None,
        required_equity_scope: str | None = None,
    ):
        self.exchange = exchange
        self.get_command = get_command
        self.kv_get = kv_get
        self.kv_set = kv_set
        self.robot_id_get = robot_id_get
        self.account_attestation = account_attestation
        self.current_margin = current_margin
        self.current_round_trip_fee_upper = current_round_trip_fee_upper
        self.reconciliation_probe = reconciliation_probe
        self.ledger_anchor = ledger_anchor
        self.atomic_claim = atomic_claim
        self.account_coordinator = account_coordinator
        self.receipt_validation_clock = receipt_validation_clock
        self.required_equity_scope = required_equity_scope
        self.strategy_equity_mark = strategy_equity_mark
        self.daily_close_history = daily_close_history
        self.pd_long_today = pd_long_today
        self.pd_long_yesterday = pd_long_yesterday
        self.terminal_truth = terminal_truth

    def load_ledger(self) -> PaperLedger:
        saved = self.kv_get(STORAGE_KEY)
        if saved is None:
            return PaperLedger()
        if not isinstance(saved, str):
            raise PaperDenied("PERSISTED_LEDGER_INVALID")
        try:
            events = json.loads(saved)
        except (TypeError, ValueError) as exc:
            raise PaperDenied("PERSISTED_LEDGER_INVALID") from exc
        if not isinstance(events, list):
            raise PaperDenied("PERSISTED_LEDGER_INVALID")
        return PaperLedger(events)

    def save_ledger(self, ledger: PaperLedger) -> None:
        """Persist locally and anchor externally before an order API call.

        YouQuant _G survives restart but is mutable and local to the host.  It
        is never treated as an immutable receipt without an external append-only
        anchor that verifies the event prefix and acknowledges the root hash.
        """
        ledger.verify_chain()
        if self.ledger_anchor is None:
            raise PaperDenied("NO_EXTERNAL_LEDGER_ANCHOR")
        serialized = json.dumps(ledger.events, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        self.kv_set(STORAGE_KEY, serialized)
        if self.kv_get(STORAGE_KEY) != serialized:
            raise PaperDenied("LEDGER_PERSISTENCE_UNCERTAIN")
        try:
            receipt = self.ledger_anchor(ledger.events, ledger.root_hash)
        except Exception as exc:
            raise PaperDenied("LEDGER_ANCHOR_UNCERTAIN") from exc
        if not isinstance(receipt, Mapping) or receipt.get("source") != "external_append_only_ledger" or receipt.get("accepted") is not True or receipt.get("root_hash") != ledger.root_hash:
            raise PaperDenied("LEDGER_ANCHOR_UNCERTAIN")

    def claim_order(self, command_id: str, contract_hash: str, account_id: str, now: datetime,
                    *, body: Mapping[str, Any] | None = None, ledger: PaperLedger | None = None) -> None:
        """External atomic, permanent one-shot claim across all strategy hosts."""
        if self.account_coordinator is not None:
            if body is None or ledger is None:
                raise PaperDenied("ACCOUNT_COORDINATOR_CONTEXT_MISSING")
            self.account_coordinator.claim(body, ledger, now)
            return
        if self.atomic_claim is None:
            raise PaperDenied("NO_EXTERNAL_ATOMIC_CLAIM")
        try:
            receipt = self.atomic_claim(command_id, contract_hash, account_id, now.isoformat())
        except Exception as exc:
            raise PaperDenied("ATOMIC_CLAIM_UNCERTAIN") from exc
        if (not isinstance(receipt, Mapping) or receipt.get("source") != "external_atomic_command_claim"
                or receipt.get("claimed") is not True or receipt.get("command_id") != command_id
                or receipt.get("contract_hash") != contract_hash or receipt.get("account_id") != account_id
                or receipt.get("environment") != SIMNOW_FIRST):
            raise PaperDenied("ATOMIC_CLAIM_DENIED_OR_UNCERTAIN")

    def prepare_submit(self, command_id: str, ledger: PaperLedger) -> None:
        if self.account_coordinator is not None:
            self.account_coordinator.prepare_submit(command_id, ledger)

    def submit_attempt_data(self, command_id: str, data: Mapping[str, Any]) -> dict[str, Any]:
        if self.account_coordinator is not None:
            return self.account_coordinator.submission_data(command_id, data)
        return dict(data)

    def record_account_terminal(self, body: Mapping[str, Any], ledger: PaperLedger, now: datetime) -> None:
        if self.account_coordinator is not None:
            self.account_coordinator.terminal(body, ledger, now)

    def append_equity_mark(self, ledger: PaperLedger, provider: Mapping[str, Any], now: datetime) -> None:
        if self.strategy_equity_mark is None:
            raise PaperDenied("STRATEGY_EQUITY_MARK_MISSING")
        try:
            mark = self.strategy_equity_mark()
        except Exception as exc:
            raise PaperDenied("STRATEGY_EQUITY_MARK_MISSING") from exc
        checked_at = self.receipt_validation_clock() if self.receipt_validation_clock else now
        if self.required_equity_scope and (not isinstance(mark, Mapping) or mark.get("allocation_scope") != self.required_equity_scope):
            raise PaperDenied("PRODUCTION_STRATEGY_SUBLEDGER_REQUIRED")
        validate_strategy_equity_mark(mark, provider, checked_at, ledger)
        ledger.append("EquityMarked", "CMD-GOLD2-EQUITY-" + hashlib.sha256(now.isoformat().encode()).hexdigest()[:16].upper(),
                      now.isoformat(), mark)
        self.save_ledger(ledger)

    def snapshot(self, contract: str, now: datetime, *, for_exit: bool = False) -> dict[str, Any]:
        read_started = self.receipt_validation_clock() if self.receipt_validation_clock else now
        try:
            connected = bool(self.exchange.IO("status"))
            meta = self.exchange.SetContractType(contract) if connected else None
            account = self.exchange.GetAccount() if connected else None
            positions_raw = self.exchange.GetPositions() if connected else None
            orders_raw = self.exchange.GetOrders() if connected else None
            attestation = self.account_attestation()
            robot_id = self.robot_id_get()
        except Exception as exc:
            raise PaperDenied("PROVIDER_READBACK_FAILED") from exc
        checked_at = self.receipt_validation_clock() if self.receipt_validation_clock else now
        if not connected or not isinstance(meta, Mapping) or account is None or positions_raw is None or orders_raw is None:
            raise PaperDenied("PROVIDER_READBACK_FAILED")
        if not isinstance(positions_raw, (list, tuple)) or not isinstance(orders_raw, (list, tuple)):
            raise PaperDenied("PROVIDER_READBACK_FAILED")
        info = _field(account, "Info")
        if not isinstance(info, Mapping):
            raise PaperDenied("ACCOUNT_IDENTITY_UNOBSERVABLE")
        observed_account_id = info.get("InvestorID") or info.get("AccountID")
        broker_id = info.get("BrokerID")
        if not observed_account_id or str(broker_id) != "9999":
            raise PaperDenied("NOT_SIMNOW_BROKER_ID")
        if not isinstance(attestation, Mapping):
            raise PaperDenied("NO_INDEPENDENT_ACCOUNT_ATTESTATION")
        attested_at = attestation.get("observed_at")
        try:
            attested = datetime.fromisoformat(str(attested_at).replace("Z", "+00:00"))
        except ValueError as exc:
            raise PaperDenied("ATTESTATION_TIME_INVALID") from exc
        if attested.tzinfo is None or not (checked_at - attested).total_seconds() >= 0 or (checked_at - attested).total_seconds() > 300:
            raise PaperDenied("ATTESTATION_STALE")
        identity_verified = (
            attestation.get("source") == "youquant_account_and_robot_readback"
            and attestation.get("environment") == SIMNOW_FIRST
            and str(attestation.get("account_id")) == str(observed_account_id)
            and attestation.get("robot_id") == robot_id
            and attestation.get("broker_id") == "9999"
            and _verified_added_ctp_binding(attestation, robot_id, checked_at)
        )
        positions: list[dict[str, Any]] = []
        margin_in_use = Decimal("0")
        for item in positions_raw:
            ptype = _field(item, "Type")
            if ptype == self.pd_long_today:
                side, age = "LONG", "TODAY"
            elif ptype == self.pd_long_yesterday:
                side, age = "LONG", "YESTERDAY"
            else:
                side, age = "UNKNOWN", "UNKNOWN"
            positions.append({
                "contract": _field(item, "ContractType") or _field(item, "Symbol"),
                "side": side,
                "age": age,
                "quantity": _field(item, "Amount"),
            })
            margin = _field(item, "Margin")
            if margin is None and not for_exit:
                raise PaperDenied("POSITION_MARGIN_UNKNOWN")
            if margin is not None:
                margin_in_use += Decimal(str(margin))
        order_ids = []
        for order in orders_raw:
            order_id = _field(order, "Id")
            if not order_id:
                raise PaperDenied("OPEN_ORDER_ID_UNKNOWN")
            order_ids.append(str(order_id))
        if for_exit:
            # A protective close needs fresh broker identity, order and position
            # readback. Missing admission-only fee/margin or four-way accounting
            # must not disable a previously authorized risk-reducing exit.
            required_margin = None
            round_trip_fees = None
            reconciled = False
        else:
            try:
                required_margin = self.current_margin(contract)
                round_trip_fees = self.current_round_trip_fee_upper(contract)
                reconciled = self.reconciliation_probe()
            except Exception as exc:
                raise PaperDenied("INDEPENDENT_RISK_OR_RECONCILIATION_MISSING") from exc
            if reconciled is not True or required_margin is None or round_trip_fees is None:
                raise PaperDenied("INDEPENDENT_RISK_OR_RECONCILIATION_MISSING")
        finished = self.receipt_validation_clock() if self.receipt_validation_clock else now
        if not 0 <= (finished - read_started).total_seconds() <= 15:
            raise PaperDenied("PROVIDER_READBACK_COLLECTION_STALE")
        return {
            "source": "provider_readback",
            "identity_verified": identity_verified,
            "environment": attestation.get("environment"),
            "account_id": str(observed_account_id),
            "robot_id": robot_id,
            "connected": connected,
            "reconciled": reconciled,
            "observed_at": read_started.isoformat(),
            "available_at": finished.isoformat(),
            "contract_meta": dict(meta),
            "positions": positions,
            "open_order_ids": order_ids,
            "margin_for_one_lot": str(required_margin),
            "round_trip_fee_upper_cny": str(round_trip_fees),
            "margin_in_use": str(margin_in_use),
            "available": _field(account, "Balance"),
            "broker_equity": _field(account, "Equity"),
        }

    def submit(self, contract: str, action: str, limit_price: str, position_age: str | None,
               *, pre_buy_guard: Callable[[], None] | None = None,
               pre_buy_clock_guard: Callable[[], None] | None = None) -> str:
        """One attempt only. An exception or absent ID is an uncertain submit."""
        meta = self.exchange.SetContractType(contract)
        validate_au_metadata(meta, contract)
        if action == "OPEN_LONG":
            if pre_buy_guard is None or pre_buy_clock_guard is None:
                raise PaperDenied("OPEN_PRE_SUBMIT_GUARDS_MISSING")
            pre_buy_guard()
            self.exchange.SetDirection("buy")
            pre_buy_clock_guard()
            order_id = self.exchange.Buy(float(limit_price), 1)
        elif action == "CLOSE_LONG":
            self.exchange.SetDirection(close_direction(position_age or "UNKNOWN"))
            order_id = self.exchange.Sell(float(limit_price), 1)
        else:
            raise PaperDenied("INVALID_ORDER_ACTION")
        if order_id in (None, False, "", 0):
            raise PaperDenied("ORDER_ID_UNKNOWN_AFTER_SUBMIT")
        return str(order_id)

    def cancel_order(self, order_id: str) -> None:
        result = self.exchange.CancelOrder(order_id)
        if result in (None, False, 0, ""):
            raise PaperDenied("CANCEL_RESULT_UNKNOWN")

    def quote(self, contract: str, now: datetime) -> dict[str, Decimal]:
        meta = self.exchange.SetContractType(contract)
        validate_au_metadata(meta, contract)
        try:
            ticker = self.exchange.GetTicker()
            bid = Decimal(str(_field(ticker, "Buy")))
            last = Decimal(str(_field(ticker, "Last")))
            tick_ms = int(_field(ticker, "Time"))
            tick_at = datetime.fromtimestamp(tick_ms / 1000, timezone.utc)
        except (TypeError, ValueError, ArithmeticError) as exc:
            raise PaperDenied("QUOTE_UNAVAILABLE") from exc
        checked_at = self.receipt_validation_clock() if self.receipt_validation_clock else now
        if bid <= 0 or last <= 0 or not 0 <= (checked_at - tick_at).total_seconds() <= 15:
            raise PaperDenied("STALE_OR_INVALID_QUOTE")
        return {"bid": bid, "last": last}

    def verified_trend_history(self, contract: str, entry_session_date: str,
                               now: datetime) -> Mapping[str, Any]:
        if self.daily_close_history is None:
            raise PaperDenied("NO_TREND_EXIT_DATA_PRODUCER")
        try:
            history = self.daily_close_history(contract, now)
        except Exception as exc:
            raise PaperDenied("TREND_HISTORY_UNAVAILABLE") from exc
        # This validates source, recency, exact dated contract, session calendar,
        # close values and evidence before a position can rely on the producer.
        checked_at = self.receipt_validation_clock() if self.receipt_validation_clock else now
        trend_exit_reason({"contingent_exit_authorized": True, "contract": contract,
                           "entry_session_date": entry_session_date}, history, checked_at)
        return history


class GoldSimNowRuntime:
    """Durable one-command-at-a-time paper OMS boundary."""

    def __init__(self, bridge: YouQuantBridge, grant: PaperGrant, signing_key: bytes,
                 *, clock: Callable[[], datetime] | None = None):
        self.bridge = bridge
        self.grant = grant
        self.signing_key = signing_key
        self.clock = clock or _utc_now
        self.recovery_readonly = False
        self.production_entry_block_reason = None

    def validate_open_evidence(self, body: Mapping[str, Any], now: datetime) -> None:
        self.bridge.verified_trend_history(body["contract"],
            datetime.fromisoformat(body["decision_at"]).astimezone(SHANGHAI).date().isoformat(), now)

    def validate_additional_open_risk(self, body, provider, now) -> None:
        """A narrower independent engineering policy may add admission checks."""
        return None

    def process_command(self, envelope: Mapping[str, Any] | str, now: datetime | None = None) -> dict[str, Any]:
        now = now or self.clock()
        ledger = self.bridge.load_ledger()
        # The authenticated command is needed only to identify the contract for
        # an independent provider readback; admit_command repeats verification.
        from yuanli_invest.gold_paper import verify_command
        body = verify_command(envelope, self.signing_key)
        if body["action"] == "OPEN_LONG" and self.production_entry_block_reason:
            raise PaperDenied(self.production_entry_block_reason)
        provider = self.bridge.snapshot(body["contract"], now)
        if body["action"] == "OPEN_LONG" and body["command_id"] not in ledger.command_hashes():
            self.validate_open_evidence(body, now)
            self.bridge.append_equity_mark(ledger, provider, now)
        if self.bridge.receipt_validation_clock:
            now = self.clock()
        admitted = admit_command(envelope, self.signing_key, self.grant, provider, ledger, now)
        if admitted["decision"] == "DUPLICATE_NO_SUBMIT":
            return {"status": "DUPLICATE_NO_SUBMIT", "ledger_root": ledger.root_hash}
        # run_once may have spent time on pending-order and safety checks before
        # passing its initial timestamp. Recheck with an independent wall clock
        # before the irreversible external claim, then again just before Buy.
        before_claim_ledger = PaperLedger(ledger.events)
        if body["action"] == "OPEN_LONG":
            before_claim = self.clock()
            fresh_provider = self.bridge.snapshot(body["contract"], before_claim)
            self.bridge.quote(body["contract"], before_claim)
            if self.bridge.receipt_validation_clock:
                before_claim = self.clock()
            self.validate_additional_open_risk(body, fresh_provider, before_claim)
            before_claim = self.clock()
            admit_command(envelope, self.signing_key, self.grant,
                          fresh_provider, before_claim_ledger, before_claim)
            if body["reason"] == "ENTRY":
                _entry_window_has_room(before_claim, seconds=2)
        command_id = body["command_id"]
        at = now.isoformat()
        self.bridge.claim_order(command_id, body["contract_hash"], body["account_id"], now, body=body, ledger=ledger)
        ledger.append("ActionAdmitted", command_id, at, {"contract_hash": body["contract_hash"], "body": body})
        self.bridge.save_ledger(ledger)
        ledger.append("OrderSubmitAttempted", command_id, at, self.bridge.submit_attempt_data(command_id,
                      {"contract": body["contract"], "action": body["action"]}))
        self.bridge.save_ledger(ledger)  # durable before any order API call
        self.bridge.prepare_submit(command_id, ledger)
        last_provider: dict[str, Any] = {}

        def pre_buy_guard() -> None:
            try:
                checked_at = self.clock()
                fresh = self.bridge.snapshot(body["contract"], checked_at)
                self.bridge.quote(body["contract"], checked_at)
                if self.bridge.receipt_validation_clock:
                    checked_at = self.clock()
                self.validate_additional_open_risk(body, fresh, checked_at)
                checked_at = self.clock()
                admit_command(envelope, self.signing_key, self.grant,
                              fresh, before_claim_ledger, checked_at)
                if body["reason"] == "ENTRY":
                    _entry_window_has_room(checked_at, seconds=1)
                last_provider.clear()
                last_provider.update(fresh)
            except PaperDenied as exc:
                raise _PreSubmitSuppressed(exc.code) from exc

        def pre_buy_clock_guard() -> None:
            try:
                checked_at = self.clock()
                self.validate_additional_open_risk(body, last_provider, checked_at)
                checked_at = self.clock()
                admit_command(envelope, self.signing_key, self.grant,
                              last_provider, before_claim_ledger, checked_at)
                if body["reason"] == "ENTRY":
                    _entry_window_has_room(checked_at, seconds=1)
            except PaperDenied as exc:
                raise _PreSubmitSuppressed(exc.code) from exc

        try:
            order_id = self.bridge.submit(body["contract"], body["action"], body["limit_price"],
                                          admitted["position_age"],
                                          pre_buy_guard=pre_buy_guard if body["action"] == "OPEN_LONG" else None,
                                          pre_buy_clock_guard=pre_buy_clock_guard if body["action"] == "OPEN_LONG" else None)
        except _PreSubmitSuppressed as exc:
            ledger.append("IncidentFrozen", command_id, self.clock().isoformat(),
                          {"class": "PRE_SUBMIT_DENIED_NO_BROKER_CALL", "reason": exc.code})
            self.bridge.save_ledger(ledger)
            return {"status": "NOT_SUBMITTED_FROZEN", "reason": exc.code,
                    "ledger_root": ledger.root_hash}
        except Exception as exc:
            ledger.append("IncidentFrozen", command_id, at, {"class": "SUBMIT_RESULT_UNCERTAIN", "detail": type(exc).__name__})
            self.bridge.save_ledger(ledger)
            return {"status": "SUBMIT_UNCERTAIN_FROZEN", "ledger_root": ledger.root_hash}
        ledger.append("OrderSubmitted", command_id, at, {"order_id": order_id})
        self.bridge.save_ledger(ledger)
        return {"status": "SUBMITTED_PENDING_READBACK", "order_id": order_id, "ledger_root": ledger.root_hash}

    def settle_order(
        self,
        *,
        command_id: str,
        order_id: str,
        order_status: str,
        capital_intent: Mapping[str, Any],
        yuanli_execution: Mapping[str, Any],
        execution_oms: Mapping[str, Any],
        broker_custodian: Mapping[str, Any],
        now: datetime | None = None,
    ) -> dict[str, Any]:
        """Apply independently observed terminal order and four-way snapshots."""
        now = now or _utc_now()
        ledger = self.bridge.load_ledger()
        matching = [e for e in ledger.events if e["command_id"] == command_id]
        submitted = [e for e in matching if e["kind"] == "OrderSubmitted"]
        admitted = [e for e in matching if e["kind"] == "ActionAdmitted"]
        if len(submitted) != 1 or submitted[0]["data"].get("order_id") != order_id or len(admitted) != 1:
            raise PaperDenied("SETTLEMENT_ORDER_REFERENCE_MISMATCH")
        if order_status not in {"FILLED", "REJECTED", "CANCELED"}:
            raise PaperDenied("ORDER_NOT_TERMINAL")
        if self.bridge.terminal_truth is None:
            raise PaperDenied("NO_INDEPENDENT_TERMINAL_READBACK")
        truth = self.bridge.terminal_truth(order_id)
        if self.bridge.receipt_validation_clock:
            now = self.clock()
        if not isinstance(truth, Mapping) or truth.get("source") != "simnow_order_and_account_readback":
            raise PaperDenied("NO_INDEPENDENT_TERMINAL_READBACK")
        try:
            truth_at = datetime.fromisoformat(str(truth["observed_at"]).replace("Z", "+00:00"))
        except (KeyError, ValueError) as exc:
            raise PaperDenied("TERMINAL_READBACK_TIME_INVALID") from exc
        if truth_at.tzinfo is None or not 0 <= (now - truth_at).total_seconds() <= 30:
            raise PaperDenied("TERMINAL_READBACK_STALE")
        body = admitted[0]["data"]["body"]
        if (
            truth.get("account_id") != self.grant.account_id
            or truth.get("environment") != SIMNOW_FIRST
            or truth.get("contract") != body["contract"]
            or truth.get("order_id") != order_id
            or truth.get("order_status") != order_status
        ):
            raise PaperDenied("TERMINAL_READBACK_MISMATCH")
        # One SHFE AU lot is indivisible: terminal readback must be exactly 0
        # or 1.  A fractional/partial/unknown value is an execution incident.
        expected_filled = Decimal("1") if order_status == "FILLED" else Decimal("0")
        try:
            actual_filled = Decimal(str(truth.get("filled_quantity")))
            actual_position = Decimal(str(truth.get("position_quantity")))
            actual_cash = Decimal(str(truth.get("cash")))
            actual_available = Decimal(str(truth.get("available")))
            actual_frozen = Decimal(str(truth.get("frozen_margin")))
            claimed_position = Decimal(str(broker_custodian.get("position_quantity")))
            claimed_cash = Decimal(str(broker_custodian.get("cash")))
            claimed_available = Decimal(str(broker_custodian.get("available")))
            claimed_frozen = Decimal(str(broker_custodian.get("frozen_margin")))
            claimed_filled = Decimal(str(broker_custodian.get("filled_quantity")))
        except (ValueError, TypeError, ArithmeticError) as exc:
            raise PaperDenied("TERMINAL_READBACK_INCOMPLETE") from exc
        if (actual_filled != expected_filled or actual_filled != claimed_filled or actual_position != claimed_position
                or abs(actual_cash - claimed_cash) > Decimal("0.01")
                or abs(actual_available - claimed_available) > Decimal("0.01")
                or abs(actual_frozen - claimed_frozen) > Decimal("0.01")):
            raise PaperDenied("TERMINAL_READBACK_MISMATCH")
        result = reconcile_four_way(capital_intent, yuanli_execution, execution_oms, broker_custodian, as_of=now)
        at = now.isoformat()
        if result["status"] != "MATCHED":
            ledger.append("ReconciliationDrifted", command_id, at, result)
            self.bridge.save_ledger(ledger)
            return {"status": "DRIFTED_FROZEN", "reason": result["reason"]}
        expected_position = int(
            (order_status == "FILLED" and body["action"] == "OPEN_LONG")
            or (order_status != "FILLED" and body["action"] == "CLOSE_LONG")
        )
        if result["position_quantity"] != str(expected_position):
            ledger.append("ReconciliationDrifted", command_id, at, {"reason": "OUTCOME_POSITION_MISMATCH"})
            self.bridge.save_ledger(ledger)
            return {"status": "DRIFTED_FROZEN", "reason": "OUTCOME_POSITION_MISMATCH"}
        ledger.append("ReconciliationMatched", command_id, at, {"order_id": order_id, "root": result})
        terminal = {"FILLED": "OrderFilledReconciled", "REJECTED": "OrderRejectedReconciled", "CANCELED": "OrderCanceledReconciled"}[order_status]
        ledger.append(terminal, command_id, at, {"order_id": order_id})
        if order_status == "FILLED" and body["action"] == "OPEN_LONG":
            ledger.append("PositionContextStored", command_id, at, {
                "contract": body["contract"],
                "contingent_exit_authorized": True,
                "origin_action_contract_id": body["action_contract_id"],
                "origin_contract_hash": body["contract_hash"],
                "evidence_hash": body["evidence_hash"],
                "stop_price": body["stop_price"],
                "roll_not_after_at": body["roll_not_after_at"],
                "exit_not_after_at": body["exit_not_after_at"],
                "entry_session_date": datetime.fromisoformat(body["decision_at"]).astimezone(SHANGHAI).date().isoformat(),
                "origin_command_id": command_id,
            })
        elif order_status == "FILLED" and body["action"] == "CLOSE_LONG":
            ledger.append("PositionContextCleared", command_id, at, {"contract": body["contract"]})
        self.bridge.save_ledger(ledger)
        self.bridge.record_account_terminal({**body, "command_id": command_id}, ledger, now)
        return {"status": "RECONCILED", "ledger_root": ledger.root_hash}

    def current_position_context(self) -> dict[str, Any] | None:
        context = None
        for event in self.bridge.load_ledger().events:
            if event["kind"] in {"PositionContextStored", "ProvisionalPositionObserved"}:
                context = dict(event["data"])
            elif event["kind"] in {"PositionContextCleared", "EmergencyCloseObserved"}:
                context = None
        return context

    def _refresh_linked_emergency_close(self, ledger: PaperLedger, pending: set[str],
                                        now: datetime) -> dict[str, Any]:
        """Read the protective close first while its filled open remains unsettled.

        This cannot clear the unmatched four-way freeze. A confirmed close is
        recorded as broker observation and escalated for manual reconciliation;
        it is never mislabeled as an automatically reconciled trade.
        """
        admitted = {e["command_id"]: e for e in ledger.events
                    if e["kind"] == "ActionAdmitted" and e["command_id"] in pending}
        submitted = {e["command_id"]: e for e in ledger.events
                     if e["kind"] == "OrderSubmitted" and e["command_id"] in pending}
        if len(admitted) != 2 or len(submitted) != 2:
            raise PaperDenied("MULTIPLE_UNLINKED_PENDING_ORDERS")
        opens = [cid for cid in pending if admitted[cid]["data"].get("body", {}).get("action") == "OPEN_LONG"]
        closes = [cid for cid in pending if admitted[cid]["data"].get("body", {}).get("action") == "CLOSE_LONG"]
        if len(opens) != 1 or len(closes) != 1:
            raise PaperDenied("MULTIPLE_UNLINKED_PENDING_ORDERS")
        open_id, close_id = opens[0], closes[0]
        original = admitted[open_id]["data"]["body"]
        protective = admitted[close_id]["data"]["body"]
        open_order_id = submitted[open_id]["data"].get("order_id")
        close_order_id = submitted[close_id]["data"].get("order_id")
        linked = (
            admitted[close_id]["data"].get("authority") == "SIGNED_ENTRY_CONTINGENT_EXIT"
            and protective.get("origin_command_id") == open_id
            and protective.get("origin_order_id") == open_order_id
            and protective.get("origin_action_contract_id") == original.get("action_contract_id")
            and protective.get("contract") == original.get("contract")
            and close_order_id not in {None, open_order_id}
            and any(e["kind"] == "ProvisionalPositionObserved" and e["command_id"] == open_id
                    for e in ledger.events)
        )
        if not linked:
            raise PaperDenied("MULTIPLE_UNLINKED_PENDING_ORDERS")
        if any(e["kind"] == "EmergencyCloseObserved" and e["command_id"] == close_id for e in ledger.events):
            if self.bridge.account_coordinator is not None:
                try:
                    self.bridge.account_coordinator.complete_linked_pair(
                        {**protective, "command_id": close_id}, ledger, now)
                except PaperDenied as exc:
                    return {"status": "LINKED_SAFETY_CLOSE_FLAT_PAIR_PENDING", "reason": exc.code,
                            "order_id": close_order_id}
                return {"status": "LINKED_PAIR_RECONCILED_ACCOUNT_FROZEN", "order_id": close_order_id}
            return {"status": "LINKED_SAFETY_CLOSE_CONFIRMED_MANUAL", "order_id": close_order_id}
        if any(e["kind"] == "EmergencyCloseFailedObserved" and e["command_id"] == close_id for e in ledger.events):
            return {"status": "LINKED_SAFETY_CLOSE_FAILED_MANUAL", "order_id": close_order_id}
        if self.bridge.terminal_truth is None:
            return {"status": "LINKED_SAFETY_CLOSE_READBACK_UNAVAILABLE", "order_id": close_order_id}
        truth = self.bridge.terminal_truth(close_order_id)
        if self.bridge.receipt_validation_clock:
            now = self.clock()
        if not isinstance(truth, Mapping) or truth.get("source") != "simnow_order_and_account_readback":
            return {"status": "LINKED_SAFETY_CLOSE_READBACK_UNAVAILABLE", "order_id": close_order_id}
        if (truth.get("order_id") != close_order_id or truth.get("account_id") != self.grant.account_id
                or truth.get("environment") != SIMNOW_FIRST or truth.get("contract") != original.get("contract")):
            raise PaperDenied("LINKED_CLOSE_READBACK_IDENTITY_MISMATCH")
        try:
            observed = datetime.fromisoformat(str(truth["observed_at"]).replace("Z", "+00:00"))
        except (KeyError, ValueError) as exc:
            raise PaperDenied("LINKED_CLOSE_READBACK_TIME_INVALID") from exc
        if observed.tzinfo is None or not 0 <= (now - observed).total_seconds() <= 30:
            return {"status": "LINKED_SAFETY_CLOSE_READBACK_STALE", "order_id": close_order_id}
        status = truth.get("order_status")
        if status not in {"FILLED", "REJECTED", "CANCELED"}:
            try:
                interim_filled = Decimal(str(truth.get("filled_quantity")))
                interim_position = Decimal(str(truth.get("position_quantity")))
            except (TypeError, ValueError, ArithmeticError):
                return {"status": "LINKED_SAFETY_CLOSE_READBACK_INCOMPLETE", "order_id": close_order_id}
            if interim_filled != 0 or interim_position != 1:
                ledger.append("IncidentFrozen", close_id, now.isoformat(),
                              {"class": "LINKED_SAFETY_CLOSE_NONTERMINAL_CONFLICT",
                               "filled_quantity": str(interim_filled), "position_quantity": str(interim_position)})
                self.bridge.save_ledger(ledger)
                return {"status": "LINKED_SAFETY_CLOSE_NONTERMINAL_CONFLICT_MANUAL", "order_id": close_order_id}
            expiry = datetime.fromisoformat(protective["expires_at"])
            if now >= expiry:
                if any(e["kind"] == "CancelAttempted" and e["command_id"] == close_id for e in ledger.events):
                    return {"status": "LINKED_SAFETY_CLOSE_CANCEL_UNCERTAIN_MANUAL", "order_id": close_order_id}
                ledger.append("CancelAttempted", close_id, now.isoformat(), {"order_id": close_order_id})
                self.bridge.save_ledger(ledger)
                try:
                    self.bridge.cancel_order(close_order_id)
                except Exception as exc:
                    ledger.append("IncidentFrozen", close_id, now.isoformat(),
                                  {"class": "LINKED_SAFETY_CLOSE_CANCEL_UNCERTAIN", "detail": type(exc).__name__})
                    self.bridge.save_ledger(ledger)
                    return {"status": "LINKED_SAFETY_CLOSE_CANCEL_UNCERTAIN_MANUAL", "order_id": close_order_id}
                ledger.append("CancelRequested", close_id, now.isoformat(), {"order_id": close_order_id})
                self.bridge.save_ledger(ledger)
                return {"status": "LINKED_SAFETY_CLOSE_CANCEL_REQUESTED_MANUAL", "order_id": close_order_id}
            return {"status": "LINKED_SAFETY_CLOSE_PENDING_READBACK", "order_id": close_order_id}
        try:
            filled = Decimal(str(truth.get("filled_quantity")))
            position = Decimal(str(truth.get("position_quantity")))
            cash = Decimal(str(truth.get("cash")))
            available = Decimal(str(truth.get("available")))
            frozen = Decimal(str(truth.get("frozen_margin")))
        except (TypeError, ValueError, ArithmeticError):
            return {"status": "LINKED_SAFETY_CLOSE_READBACK_INCOMPLETE", "order_id": close_order_id}
        if cash < 0 or available < 0 or frozen < 0:
            return {"status": "LINKED_SAFETY_CLOSE_READBACK_INCOMPLETE", "order_id": close_order_id}
        if status == "FILLED" and filled == 1 and position == 0:
            provider = self.bridge.snapshot(original["contract"], now, for_exit=True)
            if (provider["identity_verified"] is not True or provider["account_id"] != self.grant.account_id
                    or provider["robot_id"] != self.grant.robot_id or provider["positions"] != []
                    or provider["open_order_ids"] != []):
                return {"status": "LINKED_SAFETY_CLOSE_BROKER_CONFLICT_MANUAL", "order_id": close_order_id}
            ledger.append("EmergencyCloseObserved", close_id, now.isoformat(), {
                "order_id": close_order_id, "origin_command_id": open_id,
                "filled_quantity": "1", "position_quantity": "0",
                "cash": str(cash), "available": str(available), "frozen_margin": str(frozen),
                "source": truth["source"], "observed_at": truth["observed_at"],
            })
            ledger.append("IncidentFrozen", close_id, now.isoformat(),
                          {"class": "EMERGENCY_CLOSE_CONFIRMED_OPEN_FOUR_WAY_UNRECONCILED"})
            self.bridge.save_ledger(ledger)
            return {"status": "LINKED_SAFETY_CLOSE_CONFIRMED_MANUAL", "order_id": close_order_id}
        ledger.append("EmergencyCloseFailedObserved", close_id, now.isoformat(), {
            "order_id": close_order_id, "status": status,
            "filled_quantity": str(filled), "position_quantity": str(position),
        })
        ledger.append("IncidentFrozen", close_id, now.isoformat(),
                      {"class": "EMERGENCY_CLOSE_NOT_CONFIRMED"})
        self.bridge.save_ledger(ledger)
        return {"status": "LINKED_SAFETY_CLOSE_FAILED_MANUAL", "order_id": close_order_id}

    def refresh_pending(self, now: datetime | None = None) -> dict[str, Any]:
        """Read external truth for one in-flight order; never resubmit it."""
        now = now or _utc_now()
        ledger = self.bridge.load_ledger()
        pending = ledger.unresolved_submissions()
        if not pending:
            return {"status": "NO_PENDING_ORDER"}
        if self.bridge.account_coordinator is not None:
            missing_ids = [cid for cid in pending if not any(e["kind"] == "OrderSubmitted"
                           and e["command_id"] == cid for e in ledger.events)]
            if missing_ids:
                try:
                    recovered = self.bridge.account_coordinator.recover_uncertain_submission(ledger, now)
                except PaperDenied as exc:
                    return {"status": "UNCERTAIN_SUBMISSION_READONLY_LOCKED", "reason": exc.code}
                if recovered["status"] != "UNCERTAIN_ORDER_ID_RECOVERED_READONLY":
                    return recovered
                ledger = self.bridge.load_ledger()
        if len(pending) == 2:
            return self._refresh_linked_emergency_close(ledger, pending, now)
        if len(pending) != 1:
            raise PaperDenied("MULTIPLE_UNRESOLVED_ORDERS")
        command_id = next(iter(pending))
        submitted = [
            e for e in ledger.events
            if e["kind"] == "OrderSubmitted" and e["command_id"] == command_id
        ]
        if len(submitted) != 1 or self.bridge.terminal_truth is None:
            return {"status": "PENDING_MANUAL_BROKER_RECONCILIATION", "command_id": command_id}
        order_id = submitted[0]["data"]["order_id"]
        truth = self.bridge.terminal_truth(order_id)
        if self.bridge.receipt_validation_clock:
            now = self.clock()
        if not isinstance(truth, Mapping) or truth.get("source") != "simnow_order_and_account_readback":
            return {"status": "PENDING_MANUAL_BROKER_RECONCILIATION", "command_id": command_id}
        if truth.get("order_id") != order_id:
            raise PaperDenied("TERMINAL_READBACK_MISMATCH")
        admitted = [e for e in ledger.events if e["kind"] == "ActionAdmitted" and e["command_id"] == command_id]
        if len(admitted) != 1:
            raise PaperDenied("PENDING_ACTION_REFERENCE_MISMATCH")
        body = admitted[0]["data"].get("body", {})
        if truth.get("account_id") != self.grant.account_id or truth.get("environment") != SIMNOW_FIRST or truth.get("contract") != body.get("contract"):
            raise PaperDenied("TERMINAL_READBACK_MISMATCH")
        try:
            truth_at = datetime.fromisoformat(str(truth["observed_at"]).replace("Z", "+00:00"))
        except (KeyError, ValueError) as exc:
            raise PaperDenied("TERMINAL_READBACK_TIME_INVALID") from exc
        if truth_at.tzinfo is None or not 0 <= (now - truth_at).total_seconds() <= 30:
            raise PaperDenied("TERMINAL_READBACK_STALE")
        status = truth.get("order_status")
        if status not in {"FILLED", "REJECTED", "CANCELED"}:
            deadline = body.get("expires_at")
            if deadline and now >= datetime.fromisoformat(deadline):
                if any(e["kind"] == "CancelAttempted" and e["command_id"] == command_id for e in ledger.events):
                    return {"status": "CANCEL_UNCERTAIN_MANUAL_RECONCILIATION", "command_id": command_id}
                ledger.append("CancelAttempted", command_id, now.isoformat(), {"order_id": order_id})
                self.bridge.save_ledger(ledger)
                try:
                    self.bridge.cancel_order(order_id)
                except Exception as exc:
                    ledger.append("IncidentFrozen", command_id, now.isoformat(), {"class": "CANCEL_RESULT_UNCERTAIN", "detail": type(exc).__name__})
                    self.bridge.save_ledger(ledger)
                    return {"status": "CANCEL_UNCERTAIN_FROZEN", "command_id": command_id}
                ledger.append("CancelRequested", command_id, now.isoformat(), {"order_id": order_id})
                self.bridge.save_ledger(ledger)
                return {"status": "CANCEL_REQUESTED_PENDING_READBACK", "command_id": command_id}
            return {"status": "PENDING_PROVIDER_ORDER", "command_id": command_id}
        legs = truth.get("four_way")
        if not isinstance(legs, Mapping) or set(legs) != {
            "capital_intent", "yuanli_execution", "execution_oms", "broker_custodian"
        }:
            if status == "FILLED" and body.get("action") == "OPEN_LONG":
                if Decimal(str(truth.get("filled_quantity"))) != 1 or Decimal(str(truth.get("position_quantity"))) != 1:
                    raise PaperDenied("PROVISIONAL_FILL_MISMATCH")
                if not any(e["kind"] == "ProvisionalPositionObserved" and e["command_id"] == command_id
                           for e in ledger.events):
                    ledger.append("ProvisionalPositionObserved", command_id, now.isoformat(), {
                        "contract": body["contract"], "contingent_exit_authorized": True,
                        "origin_action_contract_id": body["action_contract_id"],
                        "origin_contract_hash": body["contract_hash"], "origin_command_id": command_id,
                        "origin_order_id": order_id, "evidence_hash": body["evidence_hash"],
                        "stop_price": body["stop_price"], "roll_not_after_at": body["roll_not_after_at"],
                        "exit_not_after_at": body["exit_not_after_at"],
                        "entry_session_date": datetime.fromisoformat(body["decision_at"]).astimezone(SHANGHAI).date().isoformat(),
                        "provisional": True,
                    })
                    self.bridge.save_ledger(ledger)
            return {"status": "PENDING_FOUR_WAY_RECONCILIATION", "command_id": command_id}
        return self.settle_order(
            command_id=command_id,
            order_id=order_id,
            order_status=status,
            capital_intent=legs["capital_intent"],
            yuanli_execution=legs["yuanli_execution"],
            execution_oms=legs["execution_oms"],
            broker_custodian=legs["broker_custodian"],
            now=now,
        )

    def due_safety_exit(self, quote_price: Any, now: datetime | None = None) -> str | None:
        """Tell the execution loop which pre-authorized safety exit is due.

        The call is read-only. Submission still needs a fresh narrow ActionContract
        or an independently reviewed contingent-exit procedure; this method must
        never be wired directly to exchange.Sell.
        """
        context = self.current_position_context()
        if context is None:
            return None
        return contingent_exit_reason(context, quote_price, now or _utc_now())

    def process_due_safety_exit(self, now: datetime | None = None) -> dict[str, Any]:
        """Submit one bounded pre-authorized exit if stop/roll/time is due.

        Entry's signed ActionContract grants this contingent *risk-reducing*
        close only for its exact contract and one lot.  A missing context,
        uncertain prior order, identity mismatch, or stale quote never submits.
        """
        now = now or _utc_now()
        ledger = self.bridge.load_ledger()
        context = self.current_position_context()
        if context is None:
            return {"status": "NO_ACTIVE_POSITION"}
        provisional = context.get("provisional") is True
        if provisional:
            incidents = [e for e in ledger.events if e["kind"] in {"IncidentFrozen", "ReconciliationDrifted"}]
            recovered = any(e["kind"] == "OrderSubmitted" and e["command_id"] == context.get("origin_command_id")
                            and e["data"].get("recovered_readonly") is True for e in ledger.events)
            only_recovered_uncertainty = (recovered and self.bridge.account_coordinator is not None
                and self.bridge.account_coordinator.supports_linked_protection
                and all(e["kind"] == "IncidentFrozen" and e["command_id"] == context.get("origin_command_id")
                        and e["data"].get("class") == "SUBMIT_RESULT_UNCERTAIN" for e in incidents))
            if (ledger.unresolved_submissions() != {context.get("origin_command_id")}
                    or (incidents and not only_recovered_uncertainty)
                    or self.bridge.terminal_truth is None):
                raise PaperDenied("PROVISIONAL_EXIT_PENDING_MISMATCH")
            truth = self.bridge.terminal_truth(context["origin_order_id"])
            if self.bridge.receipt_validation_clock:
                now = self.clock()
            if (not isinstance(truth, Mapping) or truth.get("source") != "simnow_order_and_account_readback"
                    or truth.get("order_id") != context["origin_order_id"] or truth.get("order_status") != "FILLED"
                    or truth.get("account_id") != self.grant.account_id or truth.get("environment") != SIMNOW_FIRST
                    or truth.get("contract") != context["contract"]
                    or Decimal(str(truth.get("filled_quantity"))) != 1
                    or Decimal(str(truth.get("position_quantity"))) != 1):
                raise PaperDenied("PROVISIONAL_EXIT_TRUTH_MISSING")
            truth_at = datetime.fromisoformat(str(truth.get("observed_at")).replace("Z", "+00:00"))
            if truth_at.tzinfo is None or not 0 <= (now - truth_at).total_seconds() <= 30:
                raise PaperDenied("PROVISIONAL_EXIT_TRUTH_STALE")
        elif ledger.is_frozen():
            raise PaperDenied("UNRESOLVED_ORDER_OR_DRIFT")
        # Signed entry contingent risk-reducing authority survives a later
        # grant expiry/disable; the existing lot must still be closable.
        contract = context["contract"]
        provider = self.bridge.snapshot(contract, now, for_exit=True)
        if (provider["identity_verified"] is not True or provider["connected"] is not True
                or provider["account_id"] != self.grant.account_id or provider["robot_id"] != self.grant.robot_id):
            raise PaperDenied("SAFETY_EXIT_IDENTITY_UNKNOWN")
        if provider["open_order_ids"] != [] or len(provider["positions"]) != 1:
            raise PaperDenied("SAFETY_EXIT_POSITION_UNKNOWN")
        position = provider["positions"][0]
        if position["contract"] != contract or position["side"] != "LONG" or Decimal(str(position["quantity"])) != 1:
            raise PaperDenied("SAFETY_EXIT_POSITION_UNKNOWN")
        age = position["age"]
        close_direction(age)
        quote = self.bridge.quote(contract, now)
        if self.bridge.receipt_validation_clock:
            now = self.clock()
        reason = contingent_exit_reason(context, quote["last"], now)
        if reason is None:
            try:
                history = self.bridge.verified_trend_history(contract, context["entry_session_date"], now)
                reason = trend_exit_reason(context, history, now)
            except PaperDenied as exc:
                return {"status": "TREND_EXIT_DATA_UNKNOWN", "reason": exc.code}
        if reason is None:
            return {"status": "NO_EXIT_DUE"}
        origin = context["origin_action_contract_id"]
        prefix = "CMD-SAFETY-" + hashlib.sha256(origin.encode()).hexdigest()[:16].upper()
        attempts = sum(
            1 for event in ledger.events
            if event["kind"] == "OrderSubmitAttempted" and event["command_id"].startswith(prefix)
        )
        if attempts >= 3:
            raise PaperDenied("SAFETY_EXIT_ATTEMPT_LIMIT")
        command_id = prefix + "-" + str(attempts + 1)
        limit = ((quote["bid"] - Decimal("0.04")) / Decimal("0.02")).to_integral_value(rounding=ROUND_FLOOR) * Decimal("0.02")
        if limit <= 0:
            raise PaperDenied("SAFETY_EXIT_PRICE_UNKNOWN")
        at = now.isoformat()
        derived = {
            "action": "CLOSE_LONG", "contract": contract, "reason": reason,
            "origin_action_contract_id": origin, "evidence_hash": context["evidence_hash"],
            "origin_command_id": context.get("origin_command_id"),
            "origin_order_id": context.get("origin_order_id"),
            "limit_price": str(limit), "stop_price": None,
            "expires_at": (now + timedelta(minutes=5)).isoformat(),
        }
        contract_hash = "sha256:" + hashlib.sha256(json.dumps(derived, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if provisional and self.bridge.account_coordinator is not None:
            if attempts:
                raise PaperDenied("LINKED_PROTECTIVE_EXIT_ALREADY_CONSUMED")
            self.bridge.account_coordinator.claim_linked_exit(
                {**derived, "command_id": command_id, "contract_hash": contract_hash}, ledger, now)
        else:
            self.bridge.claim_order(command_id, contract_hash, self.grant.account_id, now,
                                    body={**derived, "command_id": command_id, "contract_hash": contract_hash}, ledger=ledger)
        ledger.append("ActionAdmitted", command_id, at, {"contract_hash": contract_hash, "body": derived, "authority": "SIGNED_ENTRY_CONTINGENT_EXIT"})
        if reason == "EXIT_STOP" and quote["last"] < Decimal(str(context["stop_price"])):
            ledger.append("GapBeyondStop", command_id, at, {"last": str(quote["last"]), "stop": context["stop_price"]})
        self.bridge.save_ledger(ledger)
        ledger.append("OrderSubmitAttempted", command_id, at, self.bridge.submit_attempt_data(command_id,
                      {"contract": contract, "action": "CLOSE_LONG", "reason": reason}))
        self.bridge.save_ledger(ledger)
        self.bridge.prepare_submit(command_id, ledger)
        try:
            order_id = self.bridge.submit(contract, "CLOSE_LONG", str(limit), age)
        except Exception as exc:
            ledger.append("IncidentFrozen", command_id, at, {"class": "SAFETY_EXIT_SUBMIT_UNCERTAIN", "detail": type(exc).__name__})
            self.bridge.save_ledger(ledger)
            return {"status": "SAFETY_EXIT_UNCERTAIN_FROZEN", "reason": reason}
        ledger.append("OrderSubmitted", command_id, at, {"order_id": order_id})
        self.bridge.save_ledger(ledger)
        return {"status": "SAFETY_EXIT_PENDING_READBACK", "reason": reason, "order_id": order_id}


def run_once(runtime: GoldSimNowRuntime, now: datetime | None = None) -> dict[str, Any]:
    """Monitor the held lot first, then poll a new signed command."""
    now = now or _utc_now()
    pending = runtime.refresh_pending(now)
    if pending["status"] != "NO_PENDING_ORDER":
        if pending["status"] == "PENDING_FOUR_WAY_RECONCILIATION":
            # A broker-confirmed fill may precede four-way settlement. The
            # pending order remains frozen for new entries, but a signed-entry
            # contingent close can still protect the observed one-lot position.
            if runtime.bridge.account_coordinator is not None:
                if not runtime.bridge.account_coordinator.supports_linked_protection:
                    return {"status": "READONLY_RECOVERY_PROTECTIVE_CLOSE_NOT_ADMITTED",
                            "command_id": pending.get("command_id")}
            emergency = runtime.process_due_safety_exit(now)
            if emergency["status"] not in {"NO_ACTIVE_POSITION", "NO_EXIT_DUE"}:
                return emergency
        return pending
    if runtime.recovery_readonly:
        return {"status": "READONLY_RECOVERY_NO_NEW_COMMANDS"}
    safety = runtime.process_due_safety_exit(now)
    if safety["status"] not in {"NO_ACTIVE_POSITION", "NO_EXIT_DUE"}:
        return safety
    command = runtime.bridge.get_command()
    if not command:
        return {"status": "NO_COMMAND"}
    return runtime.process_command(command, now)


def serve(runtime: GoldSimNowRuntime, sleep: Callable[[int], Any], log: Callable[..., Any]) -> None:
    """YouQuant polling loop; any unknown state halts instead of retrying."""
    if not isinstance(runtime, GoldSimNowRuntime):
        raise PaperDenied("RUNTIME_NOT_CONFIGURED")
    while True:
        try:
            result = run_once(runtime)
            if result["status"].startswith("LINKED_SAFETY_CLOSE_") and result["status"].endswith("_MANUAL"):
                log("GOLD2_PAPER_MANUAL_RECONCILIATION_REQUIRED", result["status"])
                return
        except PaperDenied as exc:
            log("GOLD2_PAPER_HALTED", exc.code)
            return
        except Exception as exc:
            log("GOLD2_PAPER_HALTED", "UNEXPECTED_" + type(exc).__name__)
            return
        sleep(1000)


def main() -> None:
    """YouQuant entrypoint; requires an injected, separately authorized runtime.

    A deployment package must bundle this file and yuanli_invest.gold_paper,
    then supply GOLD2_SIMNOW_RUNTIME with actual readback/ledger callbacks.  No
    credentials or paper authority are embedded in repository source.
    """
    # Enforce the production interpreter contract before looking up or using
    # any injected runtime, host callback, or broker object. Diagnostic source
    # may load on older Python, but it cannot enter this production loop.
    if sys.version_info < (3, 12):
        raise PaperDenied("PYTHON_VERSION_UNSUPPORTED")
    runtime = globals().get("GOLD2_SIMNOW_RUNTIME")
    sleep = globals().get("Sleep")
    log = globals().get("Log")
    if not isinstance(runtime, GoldSimNowRuntime) or not callable(sleep) or not callable(log):
        raise PaperDenied("RUNTIME_NOT_CONFIGURED")
    bootstrap = sys.modules.get("scripts.gold_au_runtime_bootstrap")
    production_type = getattr(bootstrap, "ProductionGoldSimNowRuntime", None)
    if production_type is None or not isinstance(runtime, production_type):
        raise PaperDenied("PRODUCTION_V2_FACTORY_REQUIRED")
    bridge = getattr(runtime, "bridge", None)
    if (bridge is None or getattr(bridge, "account_coordinator", None) is None
            or getattr(bridge, "atomic_claim", None) is not None
            or getattr(bridge, "required_equity_scope", None) != "SEGREGATED_GOLD2_PAPER_SUBLEDGER_V1"
            or not callable(getattr(bridge, "receipt_validation_clock", None))):
        raise PaperDenied("PRODUCTION_V2_WIRING_REQUIRED")
    serve(runtime, sleep, log)
