"""Fixed GOLD2 paper allocation, replayed from the immutable execution ledger.

This is accounting, not a broker connector. Native readers must supply complete
trade/settlement evidence. A larger SimNow balance remains unallocated; no cash
is moved and unexplained account changes never become strategy profit.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
import re
from typing import Any, Mapping

from yuanli_invest.gold_paper import PaperDenied, PaperGrant, PaperLedger, SIMNOW_FIRST, SHA256, _digest, _time

SCOPE = "SEGREGATED_GOLD2_PAPER_SUBLEDGER_V1"
INITIAL = Decimal("5000000")
MULTIPLE = Decimal("1000")
CENT = Decimal("0.01")
KINDS = {"StrategyAllocationInitialized", "StrategyFillBooked", "StrategySettlementBooked"}


def number(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise PaperDenied("ACCOUNTING_NUMBER_INVALID")
    try:
        result = Decimal(str(value))
    except ArithmeticError:
        raise PaperDenied("ACCOUNTING_NUMBER_INVALID") from None
    if not result.is_finite():
        raise PaperDenied("ACCOUNTING_NUMBER_INVALID")
    return result


def evidence(value: Any) -> None:
    if not isinstance(value, str) or SHA256.fullmatch(value) is None:
        raise PaperDenied("ACCOUNTING_NATIVE_EVIDENCE_MISSING")


def initialize_allocation(ledger: PaperLedger, snapshot: Mapping[str, Any], grant: PaperGrant,
                          now: datetime, persist) -> dict[str, Any]:
    """Create the virtual allocation from a real verified flat readback once.

    Caller supplies BrokerFactsReader.read_current, not an account label or an
    artificial starting balance. Persist must anchor the exact immutable event
    externally before any production runtime can consume it.
    """
    ledger.verify_chain()
    if ledger.events or not callable(persist):
        raise PaperDenied("ACCOUNTING_BASELINE_ALREADY_STARTED_OR_UNANCHORED")
    if (grant.environment != SIMNOW_FIRST or grant.strategy_initial_equity != "5000000"
            or snapshot.get("source") != "simnow_native_ctp_readonly_facts"
            or snapshot.get("environment") != SIMNOW_FIRST or snapshot.get("account_id") != grant.account_id
            or snapshot.get("positions") != [] or snapshot.get("pending_orders") != []
            or type(snapshot.get("pending_order_count")) is not int or snapshot["pending_order_count"] != 0
            or number(snapshot.get("broker_equity")) < INITIAL
            or not _time(grant.starts_at, "grant_starts") <= now <= _time(grant.expires_at, "grant_expires")):
        raise PaperDenied("ACCOUNTING_REAL_FLAT_BASELINE_REQUIRED")
    observed = _time(snapshot.get("observed_at"), "baseline_observed")
    available = _time(snapshot.get("available_at"), "baseline_available")
    if not observed <= available <= now or now - observed > timedelta(seconds=15):
        raise PaperDenied("ACCOUNTING_BASELINE_STALE")
    if snapshot.get("raw_sha256") != _digest({k: v for k, v in snapshot.items() if k != "raw_sha256"}):
        raise PaperDenied("ACCOUNTING_BASELINE_HASH_INVALID")
    for field in ("raw_account_sha256", "raw_positions_sha256", "raw_orders_sha256"):
        evidence(snapshot.get(field))
    event = ledger.append("StrategyAllocationInitialized", "CMD-GOLD2-ALLOCATION-" + _digest(snapshot)[7:23].upper(),
        now.isoformat(), {"initial_equity": str(INITIAL), "broker_equity": snapshot["broker_equity"],
            "environment": SIMNOW_FIRST, "account_id": grant.account_id, "position_quantity": 0,
            "pending_order_count": 0, "approval_ref": grant.human_approval_ref,
            "observed_at": snapshot["observed_at"], "raw_sha256": _digest(snapshot)})
    try:
        persist(ledger)
    except Exception as exc:
        # The in-memory event is intentionally retained. Never recreate the
        # baseline after an ambiguous append; inspect external readback first.
        raise PaperDenied("ACCOUNTING_ALLOCATION_ANCHOR_UNCERTAIN") from exc
    return {"status": "ALLOCATION_INITIALIZED_NOT_EXECUTION_ADMITTED", "ledger_root_hash": ledger.root_hash,
            "event_hash": event["event_hash"], "initial_equity": str(INITIAL)}


def replay(journal: list[dict[str, Any]]) -> dict[str, Any]:
    previous_sequence = 0
    previous_at = None
    allocation = None
    realized = fees = Decimal(0)
    position = None
    trades: dict[str, str] = {}
    settlements: dict[str, str] = {}
    for event in journal:
        if (set(event) != {"sequence", "kind", "command_id", "at", "data", "previous_hash", "event_hash"}
                or type(event["sequence"]) is not int or event["sequence"] <= previous_sequence
                or event["kind"] not in KINDS
                or event["event_hash"] != _digest({k: v for k, v in event.items() if k != "event_hash"})):
            raise PaperDenied("ACCOUNTING_JOURNAL_INVALID")
        at = _time(event["at"], "accounting_event_at")
        if previous_at is not None and at < previous_at:
            raise PaperDenied("ACCOUNTING_JOURNAL_TIME_REVERSED")
        previous_at = at
        previous_sequence = event["sequence"]
        data = event["data"]
        if event["kind"] == "StrategyAllocationInitialized":
            if allocation is not None or number(data.get("initial_equity")) != INITIAL:
                raise PaperDenied("ACCOUNTING_ALLOCATION_CONFLICT")
            if (data.get("environment") != SIMNOW_FIRST or data.get("position_quantity") != 0
                    or type(data.get("position_quantity")) is not int
                    or type(data.get("pending_order_count")) is not int
                    or data.get("pending_order_count") != 0 or not data.get("account_id")
                    or not data.get("approval_ref") or number(data.get("broker_equity")) < INITIAL):
                raise PaperDenied("ACCOUNTING_BASELINE_NOT_FLAT_OR_FUNDED")
            evidence(data.get("raw_sha256"))
            allocation = data
        elif event["kind"] in {"StrategyFillBooked", "StrategySettlementBooked"}:
            if allocation is None:
                raise PaperDenied("ACCOUNTING_ALLOCATION_MISSING")
            if data.get("account_id") != allocation["account_id"] or data.get("environment") != SIMNOW_FIRST:
                raise PaperDenied("ACCOUNTING_IDENTITY_MISMATCH")
            evidence(data.get("raw_sha256"))
            if event["kind"] == "StrategyFillBooked":
                key = data.get("trade_id")
                if not isinstance(key, str) or not key or type(data.get("quantity")) is not int or data.get("quantity") != 1:
                    raise PaperDenied("ACCOUNTING_TRADE_INVALID")
                fingerprint = _digest(data)
                if key in trades:
                    if trades[key] != fingerprint:
                        raise PaperDenied("ACCOUNTING_TRADE_ID_CONFLICT")
                    continue
                price, fee = number(data.get("price")), number(data.get("fee_cny"))
                if price <= 0 or price % Decimal("0.02") or fee < 0 or fee % CENT:
                    raise PaperDenied("ACCOUNTING_TRADE_INVALID")
                action = data.get("action")
                contract = data.get("contract")
                if not isinstance(contract, str) or re.fullmatch(r"au\d{4}", contract) is None:
                    raise PaperDenied("ACCOUNTING_TRADE_INVALID")
                if action == "OPEN_LONG" and position is None:
                    position = {"contract": contract, "basis_price": price, "entry_price": price}
                elif action == "CLOSE_LONG" and position and position["contract"] == contract:
                    realized += (price - position["basis_price"]) * MULTIPLE
                    position = None
                else:
                    raise PaperDenied("ACCOUNTING_POSITION_TRANSITION_INVALID")
                fees += fee
                trades[key] = fingerprint
            else:
                key = data.get("settlement_id")
                if not isinstance(key, str) or not key:
                    raise PaperDenied("ACCOUNTING_SETTLEMENT_INVALID")
                fingerprint = _digest(data)
                if key in settlements:
                    if settlements[key] != fingerprint:
                        raise PaperDenied("ACCOUNTING_SETTLEMENT_ID_CONFLICT")
                    continue
                price, actual = number(data.get("settlement_price")), number(data.get("variation_pnl_cny"))
                if price <= 0 or price % Decimal("0.02"):
                    raise PaperDenied("ACCOUNTING_SETTLEMENT_INVALID")
                expected = Decimal(0) if position is None else (price - position["basis_price"]) * MULTIPLE
                if (actual % CENT or abs(actual - expected) > CENT
                        or type(data.get("position_quantity")) is not int or data.get("position_quantity") != int(position is not None)):
                    raise PaperDenied("ACCOUNTING_SETTLEMENT_PNL_MISMATCH")
                if position is not None:
                    if data.get("contract") != position["contract"]:
                        raise PaperDenied("ACCOUNTING_SETTLEMENT_CONTRACT_MISMATCH")
                    position["basis_price"] = price
                realized += actual
                settlements[key] = fingerprint
    if allocation is None:
        raise PaperDenied("ACCOUNTING_ALLOCATION_MISSING")
    return {"allocation": allocation, "realized": realized, "fees": fees,
            "position": position, "trade_ids": sorted(trades), "settlement_ids": sorted(settlements),
            }


def build_strategy_equity_mark(ledger: PaperLedger, snapshot: Mapping[str, Any], now: datetime) -> dict[str, Any]:
    """Reconcile a complete independently captured account since allocation.

    Snapshot lists are authoritative native histories since baseline, not the
    runtime's own desired fills. Missing cross-day archives block this mark.
    """
    ledger.verify_chain()
    journal = [e for e in ledger.events if e["kind"] in KINDS]
    state = replay(journal)
    baseline = state["allocation"]
    if (snapshot.get("source") != "simnow_strategy_accounting_readback"
            or snapshot.get("environment") != SIMNOW_FIRST
            or snapshot.get("account_id") != baseline["account_id"]
            or snapshot.get("history_complete") is not True
            or snapshot.get("external_cashflows_cny") != "0"
            or snapshot.get("pending_order_count") != 0):
        raise PaperDenied("ACCOUNTING_READBACK_INCOMPLETE")
    age = now - _time(snapshot.get("observed_at"), "accounting_observed_at")
    if not timedelta(0) <= age <= timedelta(seconds=15):
        raise PaperDenied("ACCOUNTING_READBACK_STALE")
    if any(_time(e["at"], "accounting_event_at") > now - age for e in journal):
        raise PaperDenied("ACCOUNTING_JOURNAL_AFTER_READBACK")
    for field in ("account_raw_sha256", "trades_raw_sha256", "settlements_raw_sha256", "positions_raw_sha256"):
        evidence(snapshot.get(field))
    if len({snapshot[field] for field in ("account_raw_sha256", "trades_raw_sha256", "settlements_raw_sha256", "positions_raw_sha256")}) != 4:
        raise PaperDenied("ACCOUNTING_EVIDENCE_SCOPES_COLLAPSED")
    if snapshot.get("trade_ids") != state["trade_ids"] or snapshot.get("settlement_ids") != state["settlement_ids"]:
        raise PaperDenied("ACCOUNTING_UNASSIGNED_NATIVE_ACTIVITY")
    for kind, field, id_field in (("StrategyFillBooked", "trade_facts", "trade_id"),
                                  ("StrategySettlementBooked", "settlement_facts", "settlement_id")):
        native = snapshot.get(field)
        booked = {e["data"][id_field]: e["data"] for e in journal if e["kind"] == kind}
        if (not isinstance(native, list) or any(not isinstance(row, dict) or id_field not in row for row in native)
                or len(native) != len(booked)
                or {row[id_field]: row for row in native} != booked):
            raise PaperDenied("ACCOUNTING_NATIVE_AMOUNTS_NOT_BOUND")
    position = state["position"]
    if (type(snapshot.get("position_quantity")) is not int or type(snapshot.get("pending_order_count")) is not int
            or snapshot.get("position_quantity") != int(position is not None)):
        raise PaperDenied("ACCOUNTING_POSITION_DRIFT")
    floating = Decimal(0)
    if position:
        if snapshot.get("contract") != position["contract"]:
            raise PaperDenied("ACCOUNTING_POSITION_DRIFT")
        mark_price = number(snapshot.get("mark_price"))
        if mark_price <= 0 or mark_price % Decimal("0.02"):
            raise PaperDenied("ACCOUNTING_MARK_PRICE_INVALID")
        floating = (mark_price - position["basis_price"]) * MULTIPLE
    pnl = state["realized"] + floating - state["fees"]
    broker_equity = number(snapshot.get("broker_equity"))
    if broker_equity % CENT:
        raise PaperDenied("ACCOUNTING_BROKER_EQUITY_PRECISION")
    if abs(broker_equity - number(baseline["broker_equity"]) - pnl) > CENT:
        raise PaperDenied("ACCOUNTING_UNEXPLAINED_BROKER_DELTA")
    equity = INITIAL + pnl
    if equity <= 0:
        raise PaperDenied("ACCOUNTING_EQUITY_NONPOSITIVE")
    proof = {"journal": journal, "ledger_root_hash": ledger.root_hash,
             "ledger_sequence": len(ledger.events), "snapshot": dict(snapshot)}
    return {"source": "independent_strategy_accounting", "allocation_scope": SCOPE,
            "environment": SIMNOW_FIRST, "account_id": baseline["account_id"],
            "observed_at": snapshot["observed_at"], "reconciled": True, "equity": str(equity),
            "broker_equity": str(broker_equity), "unallocated_equity": str(number(baseline["broker_equity"]) - INITIAL),
            "realized_pnl_cny": str(state["realized"]), "floating_pnl_cny": str(floating),
            "fees_cny": str(state["fees"]), "proof": proof, "raw_sha256": _digest(proof)}


def validate_strategy_subledger_mark(mark: Mapping[str, Any], now: datetime, ledger: PaperLedger) -> Decimal:
    proof = mark.get("proof")
    if not isinstance(proof, Mapping) or set(proof) != {"journal", "snapshot", "ledger_root_hash", "ledger_sequence"} or mark.get("raw_sha256") != _digest(proof):
        raise PaperDenied("ACCOUNTING_MARK_PROOF_INVALID")
    ledger.verify_chain()
    sequence = proof["ledger_sequence"]
    if type(sequence) is not int or not 0 < sequence <= len(ledger.events):
        raise PaperDenied("ACCOUNTING_MARK_LEDGER_PREFIX_MISSING")
    prefix = PaperLedger(ledger.events[:sequence])
    if (prefix.root_hash != proof["ledger_root_hash"]
            or [e for e in prefix.events if e["kind"] in KINDS] != proof["journal"]
            or [e for e in ledger.events[sequence:] if e["kind"] in KINDS]):
        raise PaperDenied("ACCOUNTING_MARK_LEDGER_PREFIX_MISMATCH")
    rebuilt = build_strategy_equity_mark(prefix, proof["snapshot"], now)
    if dict(mark) != rebuilt:
        raise PaperDenied("ACCOUNTING_MARK_REPLAY_MISMATCH")
    return number(rebuilt["equity"])
