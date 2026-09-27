"""Offline prospective AU paper-trade outcome contract, separate from G6 research.

The decision must be frozen at 08:30 and independently registered before its
09:00 entry window. Broker fills and D+5/D+20 marks are later facts. This
module validates supplied records and calculates outcomes; it never accesses
an account, authenticates a registry, sends an order, or proves investment edge.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal, InvalidOperation
import re
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from .receipts import canonical_hash
from .time import instant

SHANGHAI = ZoneInfo("Asia/Shanghai")
AU = re.compile(r"au\d{2}(0[1-9]|1[0-2])\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
MULTIPLIER = Decimal("1000")
DATA_MODES = {"SYNTHETIC_ENGINEERING_ONLY", "REAL_PAPER_OBSERVATIONS"}


def _time(value: Any, field: str) -> datetime:
    try:
        return instant(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be timezone-aware timestamp") from exc


def _day(value: Any, field: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO date") from exc


def _decimal(value: Any, field: str, *, positive: bool = False, nonnegative: bool = False) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError(f"{field} must be decimal")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} must be decimal") from exc
    if not number.is_finite() or (positive and number <= 0) or (nonnegative and number < 0):
        raise ValueError(f"{field} out of range")
    return number


def _identity(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        raise ValueError(f"{field} required")
    return value


def _sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or SHA.fullmatch(value) is None:
        raise ValueError(f"{field} must be lowercase SHA256")
    return value


def _contract(value: Any) -> str:
    if not isinstance(value, str) or AU.fullmatch(value) is None:
        raise ValueError("dated auYYMM contract required")
    return value


def _mode(value: Any) -> str:
    if value not in DATA_MODES:
        raise ValueError("explicit paper data_mode required")
    return value


def _validate_decision(decision: Mapping[str, Any]) -> tuple[date, datetime, datetime]:
    if decision.get("schema_version") != "gold-au-forward-decision.v2":
        raise ValueError("unsupported prospective decision contract")
    for field in ("decision_id", "signal_id", "strategy_version", "baseline_id"):
        _identity(decision.get(field), field)
    _contract(decision.get("contract"))
    if decision.get("action") != "OPEN_LONG" or decision.get("quantity") != 1:
        raise ValueError("only one-lot long entry is in scope")
    if decision.get("environment") != "SIMNOW_FIRST_NORMAL":
        raise ValueError("only SimNow first normal environment is in scope")
    _mode(decision.get("data_mode"))
    _sha(decision.get("evidence_sha256"), "evidence_sha256")
    _sha(decision.get("parameters_sha256"), "parameters_sha256")
    decision_at = _time(decision.get("decision_at"), "decision_at")
    local = decision_at.astimezone(SHANGHAI)
    if local.timetz().replace(tzinfo=None) != time(8, 30):
        raise ValueError("decision must be frozen at 08:30 Asia/Shanghai")
    if local.weekday() >= 5:
        raise ValueError("decision cannot be on weekend")
    if _time(decision.get("evidence_known_as_of"), "evidence_known_as_of") > decision_at:
        raise ValueError("post-decision evidence")
    if decision.get("horizons_trading_days") != [5, 20]:
        raise ValueError("horizons must be frozen at 5 and 20 exchange sessions")
    if decision.get("engineering_test") not in {True, False}:
        raise ValueError("engineering_test boolean required")
    return local.date(), decision_at, datetime.combine(local.date(), time(9, 0), SHANGHAI).astimezone(timezone.utc)


def _validate_registration(registration: Mapping[str, Any], decision: Mapping[str, Any],
                           decision_at: datetime, entry_start: datetime) -> None:
    if registration.get("decision_sha256") != canonical_hash(decision):
        raise ValueError("registration does not bind frozen decision bytes")
    for field in ("registry_id", "record_id", "source_ref"):
        _identity(registration.get(field), field)
    _sha(registration.get("raw_sha256"), "registration.raw_sha256")
    recorded = _time(registration.get("recorded_at"), "recorded_at")
    local_recorded = recorded.astimezone(SHANGHAI)
    if (not decision_at <= recorded < entry_start
            or local_recorded.date() != decision_at.astimezone(SHANGHAI).date()
            or local_recorded.timetz().replace(tzinfo=None) > time(8, 30, 59)):
        raise ValueError("decision registration must be complete by 08:30:59 before entry")
    if registration.get("verification") != "EXTERNAL_READBACK_REQUIRED":
        raise ValueError("offline registration cannot self-authenticate")
    kind = registration.get("registry_kind")
    if kind not in {"EXTERNAL_RECORD", "SYNTHETIC_FIXTURE"}:
        raise ValueError("registry_kind required")
    if decision["data_mode"] == "REAL_PAPER_OBSERVATIONS" and kind != "EXTERNAL_RECORD":
        raise ValueError("real-paper decision cannot use synthetic registry")


def _calendar(payload: Any) -> tuple[list[date], dict[str, Any]]:
    if not isinstance(payload, Mapping):
        raise ValueError("exchange_calendar object required")
    for field in ("source_ref", "calendar_id"):
        _identity(payload.get(field), f"calendar.{field}")
    _sha(payload.get("raw_sha256"), "calendar.raw_sha256")
    if payload.get("source_kind") not in {"SHFE_OFFICIAL", "SYNTHETIC_FIXTURE"}:
        raise ValueError("calendar.source_kind required")
    sessions = payload.get("sessions")
    if not isinstance(sessions, list) or not sessions:
        raise ValueError("nonempty exchange sessions required")
    days = [_day(item, "calendar.session") for item in sessions]
    if days != sorted(set(days)) or any(day.weekday() >= 5 for day in days):
        raise ValueError("exchange sessions must be unique ordered weekdays")
    return days, dict(payload)


def _validate_fill(row: Mapping[str, Any], decision: Mapping[str, Any], registered_at: datetime) -> dict[str, Any]:
    for field in ("fill_id", "broker_order_id", "broker_trade_id", "broker_source_ref", "broker_ledger_ref"):
        _identity(row.get(field), f"fill.{field}")
    _identity(row.get("reference_source_ref"), "fill.reference_source_ref")
    _sha(row.get("reference_raw_sha256"), "fill.reference_raw_sha256")
    if row.get("decision_id") != decision["decision_id"]:
        raise ValueError("broker fill decision identity mismatch")
    if row.get("environment") != "SIMNOW_FIRST_NORMAL" or row.get("data_mode") != decision["data_mode"]:
        raise ValueError("broker fill mode/environment mismatch")
    if row.get("broker_source_kind") not in {"EXTERNAL_RECORD", "SYNTHETIC_FIXTURE"}:
        raise ValueError("broker fill source kind required")
    if decision["data_mode"] == "REAL_PAPER_OBSERVATIONS" and row["broker_source_kind"] != "EXTERNAL_RECORD":
        raise ValueError("real-paper fill cannot use synthetic broker record")
    _contract(row.get("contract"))
    if row.get("action") not in {"OPEN_LONG", "CLOSE_LONG"} or row.get("quantity") != 1:
        raise ValueError("fill must be one lot OPEN_LONG/CLOSE_LONG")
    _sha(row.get("raw_sha256"), "fill.raw_sha256")
    fill_at = _time(row.get("fill_at"), "fill_at")
    retrieved = _time(row.get("retrieved_at"), "fill.retrieved_at")
    reconciled = _time(row.get("reconciled_at"), "fill.reconciled_at") if row.get("reconciled_at") else None
    if fill_at <= registered_at or retrieved < fill_at or (reconciled is not None and reconciled < retrieved):
        raise ValueError("fill clocks conflict with prospective registration")
    if row.get("reconciliation_state") not in {"RECONCILED", "PENDING"}:
        raise ValueError("fill reconciliation_state required")
    if (row["reconciliation_state"] == "RECONCILED") != (reconciled is not None):
        raise ValueError("fill reconciliation clock/state conflict")
    price = _decimal(row.get("price_cny_per_gram"), "fill.price", positive=True)
    reference = _decimal(row.get("reference_price_cny_per_gram"), "fill.reference_price", positive=True)
    fee = _decimal(row.get("fee_cny"), "fill.fee", nonnegative=True)
    return {**dict(row), "_at": fill_at, "_retrieved": retrieved, "_reconciled": reconciled,
            "_price": price, "_reference": reference, "_fee": fee}


def _validate_snapshot(row: Mapping[str, Any], due_day: date, horizon: int,
                       decision: Mapping[str, Any], outcome_contract_id: str) -> dict[str, Any]:
    if row.get("horizon_trading_days") != horizon or row.get("session_date") != due_day.isoformat():
        raise ValueError("outcome snapshot does not match exchange-session horizon")
    if row.get("decision_id") != decision["decision_id"] or row.get("data_mode") != decision["data_mode"]:
        raise ValueError("outcome identity/mode mismatch")
    if row.get("outcome_contract_id") != outcome_contract_id:
        raise ValueError("outcome does not match preregistered contract ID")
    for field in ("snapshot_id", "source_ref", "broker_ledger_ref"):
        _identity(row.get(field), f"outcome.{field}")
    _sha(row.get("raw_sha256"), "outcome.raw_sha256")
    if row.get("vintage_kind") != "FIRST_RELEASE":
        raise ValueError("only frozen first outcome snapshot can settle")
    if row.get("source_kind") not in {"EXTERNAL_RECORD", "SYNTHETIC_FIXTURE"}:
        raise ValueError("outcome source_kind required")
    if decision["data_mode"] == "REAL_PAPER_OBSERVATIONS" and row["source_kind"] != "EXTERNAL_RECORD":
        raise ValueError("real-paper outcome cannot use synthetic source")
    observed = _time(row.get("observed_at"), "outcome.observed_at")
    local = observed.astimezone(SHANGHAI)
    if local.date() != due_day or local.timetz().replace(tzinfo=None) != time(15, 0):
        raise ValueError("outcome must mark exchange horizon at 15:00 Asia/Shanghai")
    published = _time(row.get("published_at"), "outcome.published_at")
    retrieved = _time(row.get("retrieved_at"), "outcome.retrieved_at")
    available = _time(row.get("available_at"), "outcome.available_at")
    if not observed <= published <= retrieved <= available:
        raise ValueError("outcome clock order invalid")
    if row.get("broker_reconciled") not in {True, False}:
        raise ValueError("outcome broker_reconciled boolean required")
    broker_fill_ids = row.get("broker_fill_ids")
    if (not isinstance(broker_fill_ids, list) or not broker_fill_ids or
            any(not isinstance(item, str) or not item for item in broker_fill_ids) or
            len(set(broker_fill_ids)) != len(broker_fill_ids)):
        raise ValueError("outcome broker_fill_ids must name unique included fills")
    mark = row.get("mark_price_cny_per_gram")
    contract = row.get("mark_contract")
    if (mark is None) != (contract is None):
        raise ValueError("mark price and contract must both be present or absent")
    if mark is not None:
        _contract(contract)
        _decimal(mark, "outcome.mark_price", positive=True)
        _identity(row.get("mark_source_ref"), "outcome.mark_source_ref")
        _sha(row.get("mark_raw_sha256"), "outcome.mark_raw_sha256")
    return {**dict(row), "_observed": observed, "_available": available}


def _money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01")))


def _replay(fills: list[dict[str, Any]], mark: dict[str, Any], *, as_of: datetime) -> dict[str, Any] | None:
    opening: dict[str, Any] | None = None
    cash = Decimal("0")
    fees = Decimal("0")
    slippage = Decimal("0")
    included: list[str] = []
    last_close_at: datetime | None = None
    for fill in fills:
        if fill["_at"] > mark["_observed"]:
            break
        if fill["_retrieved"] > as_of or fill["_reconciled"] is None or fill["_reconciled"] > as_of:
            return None
        if fill["action"] == "OPEN_LONG":
            if opening is not None:
                raise ValueError("duplicate overlapping long entry")
            opening = fill
            slippage += (fill["_price"] - fill["_reference"]) * MULTIPLIER
        else:
            if opening is None or fill["contract"] != opening["contract"]:
                raise ValueError("unpaired or wrong-contract long close")
            cash += (fill["_price"] - opening["_price"]) * MULTIPLIER
            slippage += (fill["_reference"] - fill["_price"]) * MULTIPLIER
            opening = None
            last_close_at = fill["_at"]
        cash -= fill["_fee"]
        fees += fill["_fee"]
        included.append(fill["fill_id"])
    if not included:
        return None
    if set(included) != set(mark["broker_fill_ids"]):
        return None
    mark_price = mark["mark_price_cny_per_gram"]
    if opening is None:
        if mark_price is not None:
            raise ValueError("flat account cannot use an open-contract mark")
        unrealized = Decimal("0")
    else:
        if mark["mark_contract"] != opening["contract"] or mark_price is None:
            raise ValueError("open position requires matching marked AU contract")
        unrealized = (_decimal(mark_price, "outcome.mark_price", positive=True) - opening["_price"]) * MULTIPLIER
    net = cash + unrealized
    return {"net_pnl_cny": _money(net), "actual_fill_gross_pnl_cny": _money(net + fees),
            "fees_cny": _money(fees), "slippage_vs_reference_cny": _money(slippage),
            "reference_gross_pnl_cny": _money(net + fees + slippage),
            "open_contract_at_horizon": opening["contract"] if opening else None,
            "included_fill_ids": included,
            "last_close_at": last_close_at.isoformat() if last_close_at else None}


def settle_forward(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Adjudicate one frozen decision as of now; absent external facts stay pending."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("decision"), Mapping):
        raise ValueError("decision object required")
    decision = payload["decision"]
    decision_day, decision_at, entry_start = _validate_decision(decision)
    as_of = _time(payload.get("as_of"), "as_of")
    if as_of < decision_at:
        raise ValueError("as_of predates decision")
    result: dict[str, Any] = {
        "schema_version": "gold-au-forward-settlement.v2",
        "decision_id": decision["decision_id"], "decision_sha256": canonical_hash(decision),
        "as_of": as_of.isoformat(), "data_mode": decision["data_mode"],
        "engineering_test": decision["engineering_test"],
        "calendar_id": None, "calendar_sha256": None,
        "external_authenticity": "UNVERIFIED_OFFLINE_DECLARATIONS",
        "investment_effectiveness_proven": False, "broker_action_authorized": False,
        "cash_baseline_net_pnl_cny": "0.00", "horizons": {},
    }
    registration = payload.get("registration")
    if not isinstance(registration, Mapping):
        result["status"] = "PENDING_INDEPENDENT_REGISTRATION"
        return result
    _validate_registration(registration, decision, decision_at, entry_start)
    result["registry_ref"] = {"registry_id": registration["registry_id"], "record_id": registration["record_id"]}
    if payload.get("exchange_calendar") is None:
        result["status"] = "PENDING_CALENDAR_COVERAGE"
        return result
    sessions, calendar = _calendar(payload["exchange_calendar"])
    result["calendar_id"] = calendar["calendar_id"]
    result["calendar_sha256"] = calendar["raw_sha256"]
    if calendar["source_kind"] == "SYNTHETIC_FIXTURE" and decision["data_mode"] == "REAL_PAPER_OBSERVATIONS":
        raise ValueError("real-paper settlement cannot use synthetic calendar")
    if decision_day not in sessions:
        result["status"] = "PENDING_CALENDAR_COVERAGE"
        return result
    base = sessions.index(decision_day)
    if len(sessions) <= base + 20:
        result["status"] = "PENDING_CALENDAR_COVERAGE"
        return result
    due = {5: sessions[base + 5], 20: sessions[base + 20]}
    contracts = registration.get("outcome_contracts")
    if not isinstance(contracts, list) or len(contracts) != 2:
        raise ValueError("D+5 and D+20 outcome contracts must be preregistered")
    by_horizon: dict[int, str] = {}
    for row in contracts:
        if not isinstance(row, Mapping) or type(row.get("horizon_trading_days")) is not int:
            raise ValueError("invalid preregistered outcome contract")
        horizon = row["horizon_trading_days"]
        contract_id = row.get("outcome_contract_id")
        if (horizon not in due or horizon in by_horizon or row.get("decision_id") != decision["decision_id"]
                or row.get("session_date") != due[horizon].isoformat()
                or not isinstance(contract_id, str) or not contract_id):
            raise ValueError("preregistered outcome contract does not match exchange calendar")
        by_horizon[horizon] = contract_id
    if set(by_horizon) != {5, 20} or len(set(by_horizon.values())) != 2:
        raise ValueError("two distinct preregistered outcome contracts required")
    for horizon, day in due.items():
        result["horizons"][str(horizon)] = {"session_date": day.isoformat(),
                                            "outcome_contract_id": by_horizon[horizon],
                                            "status": "NOT_DUE"}
    rows = payload.get("broker_fills", [])
    if not isinstance(rows, list):
        raise ValueError("broker_fills array required")
    if any(not isinstance(row, Mapping) for row in rows):
        raise ValueError("broker fill must be object")
    fills = [_validate_fill(row, decision, _time(registration["recorded_at"], "recorded_at")) for row in rows]
    if len({r["fill_id"] for r in fills}) != len(fills) or len({r["broker_trade_id"] for r in fills}) != len(fills):
        raise ValueError("duplicate broker fill identity")
    fills.sort(key=lambda row: (row["_at"], row["fill_id"]))
    if not fills:
        result["status"] = "PENDING_BROKER_FILL"
        return result
    first = fills[0]
    if first["action"] != "OPEN_LONG" or first["contract"] != decision["contract"]:
        raise ValueError("first fill must open frozen decision contract")
    if not entry_start <= first["_at"] <= datetime.combine(decision_day, time(9, 5), SHANGHAI).astimezone(timezone.utc):
        raise ValueError("entry fill outside frozen 09:00-09:05 window")
    result["entry_fill_id"] = first["fill_id"]
    result["entry_at"] = first["fill_at"]
    if first["_reconciled"] is None or first["_reconciled"] > as_of:
        result["status"] = "PENDING_BROKER_RECONCILIATION"
        return result
    snapshots = payload.get("outcome_snapshots", [])
    if not isinstance(snapshots, list):
        raise ValueError("outcome_snapshots array required")
    by_horizon: dict[int, dict[str, Any]] = {}
    for row in snapshots:
        if not isinstance(row, Mapping) or row.get("horizon_trading_days") not in due:
            raise ValueError("unexpected outcome horizon")
        horizon = row["horizon_trading_days"]
        if horizon in by_horizon:
            raise ValueError("duplicate horizon snapshot")
        by_horizon[horizon] = _validate_snapshot(row, due[horizon], horizon, decision,
                                                 result["horizons"][str(horizon)]["outcome_contract_id"])
    settled = 0
    for horizon, due_day in due.items():
        item = result["horizons"][str(horizon)]
        mark_time = datetime.combine(due_day, time(15, 0), SHANGHAI).astimezone(timezone.utc)
        if as_of < mark_time:
            continue
        snapshot = by_horizon.get(horizon)
        if snapshot is None or snapshot["_available"] > as_of:
            item["status"] = "PENDING_OUTCOME_SNAPSHOT"
            continue
        next_session = sessions[base + horizon + 1] if len(sessions) > base + horizon + 1 else None
        if next_session is None:
            item["status"] = "PENDING_CALENDAR_COVERAGE"
            continue
        capture_deadline = datetime.combine(next_session, time(8, 30), SHANGHAI).astimezone(timezone.utc)
        if snapshot["_available"] > capture_deadline:
            item["status"] = "PENDING_LATE_OUTCOME_CAPTURE"
            continue
        if not snapshot["broker_reconciled"]:
            item["status"] = "PENDING_BROKER_RECONCILIATION"
            continue
        computation = _replay(fills, snapshot, as_of=as_of)
        if computation is None:
            item["status"] = "PENDING_BROKER_RECONCILIATION"
            continue
        item.update(computation)
        item["snapshot_id"] = snapshot["snapshot_id"]
        item["snapshot_sha256"] = snapshot["raw_sha256"]
        item["status"] = "SETTLED_PROSPECTIVE_PAPER_OUTCOME"
        if horizon == 20 and computation["open_contract_at_horizon"] is not None:
            item["policy_violation"] = "POSITION_STILL_OPEN_AT_DAY_20_MARK"
        settled += 1
    result["status"] = "SETTLED_BOTH_HORIZONS" if settled == 2 else "PARTIALLY_SETTLED" if settled else "PENDING_OUTCOMES"
    return result


def _one_year_later(first: date) -> date:
    try:
        return first.replace(year=first.year + 1)
    except ValueError:  # February 29
        return first.replace(year=first.year + 1, day=28)


def assess_program(receipts: list[Mapping[str, Any]], *, as_of: str) -> dict[str, Any]:
    """Eligibility gate for later expert review; it never certifies alpha."""
    now = _time(as_of, "as_of").astimezone(SHANGHAI).date()
    if not isinstance(receipts, list):
        raise ValueError("receipts array required")
    seen_decisions: set[str] = set()
    seen_fills: set[str] = set()
    complete = []
    for row in receipts:
        if not isinstance(row, Mapping) or row.get("schema_version") != "gold-au-forward-settlement.v2":
            raise ValueError("only v2 settlement receipts accepted")
        decision_id = _identity(row.get("decision_id"), "decision_id")
        if decision_id in seen_decisions:
            raise ValueError("duplicate decision in program assessment")
        seen_decisions.add(decision_id)
        fill_id = row.get("entry_fill_id")
        if fill_id is not None:
            if fill_id in seen_fills:
                raise ValueError("duplicate entry fill in program assessment")
            seen_fills.add(fill_id)
        if (row.get("data_mode") != "REAL_PAPER_OBSERVATIONS" or row.get("engineering_test") is True
                or row.get("status") != "SETTLED_BOTH_HORIZONS"):
            continue
        horizon20 = row["horizons"]["20"]
        if horizon20.get("status") != "SETTLED_PROSPECTIVE_PAPER_OUTCOME" or horizon20.get("policy_violation"):
            continue
        entry_at = _time(row.get("entry_at"), "entry_at")
        close_text = horizon20.get("last_close_at")
        if not close_text:
            continue
        close_at = _time(close_text, "last_close_at")
        if close_at <= entry_at:
            raise ValueError("exit predates entry")
        complete.append((entry_at, close_at, decision_id))
    complete.sort()
    independent = []
    latest_close: datetime | None = None
    for entry, close, decision_id in complete:
        if latest_close is None or entry >= latest_close:
            independent.append(decision_id)
            latest_close = close
    first = complete[0][0].astimezone(SHANGHAI).date() if complete else None
    months_ready = first is not None and now >= _one_year_later(first)
    count_ready = len(independent) >= 30
    sample_gate = bool(months_ready and count_ready)
    return {"schema_version": "gold-au-program-assessment-gate.v2",
            "prospective_sample_gate_met": sample_gate,
            # No offline mapping can independently authenticate the referenced
            # registry, broker and exchange records. External readback must
            # happen before an investment committee may treat this as evidence.
            "eligible_for_investment_review": False,
            "investment_effectiveness_proven": False,
            "complete_real_paper_entries": len(complete), "independent_entries": len(independent),
            "minimum_12_months_met": months_ready, "minimum_30_independent_entries_met": count_ready,
            "first_complete_entry_date": first.isoformat() if first else None,
            "reason": "EXTERNAL_READBACK_AND_BLIND_BENCHMARK_REVIEW_REQUIRED" if sample_gate else "INSUFFICIENT_PROSPECTIVE_SAMPLE"}
