"""Pure GOLD2 AU signal-to-paper-command admission gateway.

This builds a signed *candidate* command, never sends it. A separately enabled
paper grant, exact frozen full-filter signal replay, independent current broker
and quote readbacks, official exchange calendar, fees, margin and ledger state
must all agree. Missing evidence fails closed.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import hashlib
import json
import re
from typing import Any, AbstractSet, Callable, Mapping

from .gold_au_strategy import DEFAULT_CONFIG, replay_frozen_signal
from .gold_paper import (
    COMMAND_FIELDS, MULTIPLIER, PROGRAM, SHANGHAI, SIMNOW_FIRST, TICK,
    PaperDenied, PaperGrant, PaperLedger, admit_command, sign_command,
    validate_au_metadata, validate_strategy_equity_mark,
)


_HASH = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")
_REGISTRATION_RECORD_FIELDS = (
    "registry_id", "record_id", "source_ref", "recorded_at",
    "decision_at", "signal_id", "signal_sha256", "frozen_dataset_sha256",
    "parameters_sha256", "forward_decision_id", "forward_decision_sha256",
    "outcome_contracts",
)


def _digest(value: Any) -> str:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True,
                            separators=(",", ":"), allow_nan=False).encode()
    return "sha256:" + hashlib.sha256(serialized).hexdigest()


def _time(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise PaperDenied("GATEWAY_INVALID_" + field.upper())
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PaperDenied("GATEWAY_INVALID_" + field.upper()) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PaperDenied("GATEWAY_NAIVE_" + field.upper())
    return parsed.astimezone(timezone.utc)


def _decimal(value: Any, field: str, *, positive: bool = True) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise PaperDenied("GATEWAY_INVALID_" + field.upper())
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise PaperDenied("GATEWAY_INVALID_" + field.upper()) from exc
    if not number.is_finite() or (number <= 0 if positive else number < 0):
        raise PaperDenied("GATEWAY_INVALID_" + field.upper())
    return number


def _sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or _HASH.fullmatch(value) is None:
        raise PaperDenied("GATEWAY_INVALID_" + field.upper())
    return value.removeprefix("sha256:")


def _fresh(readback: Mapping[str, Any], now: datetime, seconds: int, label: str) -> None:
    observed = _time(readback.get("observed_at"), label + "_observed_at")
    if not timedelta(0) <= now - observed <= timedelta(seconds=seconds):
        raise PaperDenied("GATEWAY_STALE_" + label.upper())


def _price(value: Any, field: str) -> Decimal:
    number = _decimal(value, field)
    if number % TICK:
        raise PaperDenied("GATEWAY_OFF_TICK_" + field.upper())
    return number


def _canonical_sessions(calendar: Mapping[str, Any], decision: datetime,
                        expected_ref: str) -> list[date]:
    if (not isinstance(calendar, Mapping) or calendar.get("source") != "SHFE_OFFICIAL_CALENDAR"
            or calendar.get("verified") is not True or calendar.get("exchange") != "SHFE"
            or calendar.get("source_ref") != expected_ref):
        raise PaperDenied("GATEWAY_UNVERIFIED_EXCHANGE_CALENDAR")
    _sha(calendar.get("raw_sha256"), "calendar_hash")
    if _time(calendar.get("published_at"), "calendar_published_at") > decision or _time(
            calendar.get("retrieved_at"), "calendar_retrieved_at") > decision:
        raise PaperDenied("GATEWAY_CALENDAR_NOT_KNOWN_AT_DECISION")
    if not isinstance(calendar.get("sessions"), list):
        raise PaperDenied("GATEWAY_MISSING_EXCHANGE_SESSIONS")
    try:
        sessions = [date.fromisoformat(item) for item in calendar["sessions"]]
    except (TypeError, ValueError) as exc:
        raise PaperDenied("GATEWAY_INVALID_EXCHANGE_SESSIONS") from exc
    if not sessions or sessions != sorted(set(sessions)):
        raise PaperDenied("GATEWAY_INVALID_EXCHANGE_SESSIONS")
    return sessions


def _check_frozen_dataset_coverage(dataset: Mapping[str, Any], sessions: list[date],
                                   decision: datetime, registered_at: datetime) -> None:
    """A frozen 08:30 input has no future facts and no omitted official session."""
    today = decision.astimezone(SHANGHAI).date()
    raw_days = dataset.get("exchange_sessions")
    if not isinstance(raw_days, list) or not raw_days:
        raise PaperDenied("GATEWAY_DATASET_CALENDAR_MISSING")
    try:
        dataset_days = [date.fromisoformat(value) for value in raw_days]
    except (TypeError, ValueError) as exc:
        raise PaperDenied("GATEWAY_DATASET_CALENDAR_MISMATCH") from exc
    if dataset_days != sorted(set(dataset_days)) or dataset_days[-1] != today:
        raise PaperDenied("GATEWAY_DATASET_CALENDAR_MISMATCH")
    expected = [day for day in sessions if dataset_days[0] <= day <= today]
    if dataset_days != expected:
        raise PaperDenied("GATEWAY_DATASET_CALENDAR_MISMATCH")
    bars = dataset.get("bars")
    observations = dataset.get("observations")
    if not isinstance(bars, list) or not isinstance(observations, list):
        raise PaperDenied("GATEWAY_FROZEN_DATASET_SHAPE")
    bar_days: set[date] = set()
    for row in bars:
        if not isinstance(row, Mapping):
            raise PaperDenied("GATEWAY_FROZEN_DATASET_SHAPE")
        try:
            bar_day = date.fromisoformat(row.get("date"))
        except (TypeError, ValueError) as exc:
            raise PaperDenied("GATEWAY_FROZEN_DATASET_SHAPE") from exc
        if bar_day >= today or bar_day not in dataset_days:
            raise PaperDenied("GATEWAY_POSTDECISION_BAR_IN_FROZEN_DATASET")
        bar_days.add(bar_day)
        for field in ("first_published_at", "retrieved_at", "available_at"):
            if _time(row.get(field), "bar_" + field) > min(decision, registered_at):
                raise PaperDenied("GATEWAY_POSTREGISTRATION_DATA_IN_FROZEN_DATASET")
    base = sessions.index(today)
    minimum = DEFAULT_CONFIG["atr_lookback"] + DEFAULT_CONFIG["volatility_reference_days"] + 1
    if base < minimum or any(day not in bar_days for day in sessions[base - minimum:base]):
        raise PaperDenied("GATEWAY_MISSING_PREREQUISITE_SHFE_BARS")
    for row in observations:
        if not isinstance(row, Mapping):
            raise PaperDenied("GATEWAY_FROZEN_DATASET_SHAPE")
        for field in ("released_at", "retrieved_at", "available_at"):
            if _time(row.get(field), "observation_" + field) > min(decision, registered_at):
                raise PaperDenied("GATEWAY_POSTREGISTRATION_DATA_IN_FROZEN_DATASET")


def _deadlines(sessions: list[date], today: date, contract: str) -> tuple[str, str, bool]:
    try:
        index = sessions.index(today)
    except ValueError as exc:
        raise PaperDenied("GATEWAY_NOT_OFFICIAL_TRADING_DAY") from exc
    if index + 20 >= len(sessions):
        raise PaperDenied("GATEWAY_MISSING_20_FUTURE_SESSIONS")
    max_exit = datetime.combine(sessions[index + 20], time(15), SHANGHAI)
    delivery_year = 2000 + int(contract[2:4])
    delivery_month = int(contract[4:6])
    # Eligibility is delivery_month_index >= current_month_index + 2.
    # A July contract is last eligible in May and must roll by the final May
    # session, before the first ineligible month (June) begins.
    cutoff_month = delivery_year * 12 + delivery_month - 1 - 1
    cutoff_first = date(cutoff_month // 12, cutoff_month % 12 + 1, 1)
    # A far-dated contract requires no calendar projection to its delivery
    # cutoff: the 20-session maximum holding period terminates first.
    if cutoff_first > max_exit.date():
        return max_exit.isoformat(), (max_exit + timedelta(days=1)).isoformat(), False
    eligible = [day for day in sessions if today <= day < cutoff_first]
    if not eligible:
        raise PaperDenied("GATEWAY_NO_SAFE_ROLL_SESSION")
    true_roll = datetime.combine(eligible[-1], time(15), SHANGHAI)
    return max_exit.isoformat(), true_roll.isoformat(), True


def _check_prior_registration(registration: Mapping[str, Any], signal: Mapping[str, Any],
                              frozen_dataset: Mapping[str, Any], sessions: list[date],
                              decision: datetime, now: datetime,
                              verifier: Callable[[Mapping[str, Any]], Mapping[str, Any]]) -> dict[str, Any]:
    """Verify an independently read-back, pre-09:00 immutable signal record.

    The external registry is the authority for recorded_at and append-only
    provenance. This pure gateway never creates or backdates that record.
    """
    if (not isinstance(registration, Mapping)
            or registration.get("schema_version") != "gold-au-signal-registration.v1"
            or registration.get("source") != "independent_append_only_registry_readback"
            or registration.get("registry_kind") != "EXTERNAL_APPEND_ONLY"
            or registration.get("append_only_verified") is not True
            or registration.get("independent_readback_verified") is not True):
        raise PaperDenied("GATEWAY_MISSING_INDEPENDENT_SIGNAL_REGISTRATION")
    for field in ("registry_id", "record_id", "source_ref"):
        if not isinstance(registration.get(field), str) or not registration[field]:
            raise PaperDenied("GATEWAY_INVALID_SIGNAL_REGISTRY_IDENTITY")
    _sha(registration.get("raw_sha256"), "signal_registry_raw_hash")
    _sha(registration.get("registry_root_sha256"), "signal_registry_root_hash")
    recorded = _time(registration.get("recorded_at"), "signal_recorded_at")
    read_back = _time(registration.get("read_back_at"), "signal_read_back_at")
    local_recorded = recorded.astimezone(SHANGHAI)
    if (recorded < decision or local_recorded.date() != decision.astimezone(SHANGHAI).date()
            or local_recorded.time() > time(8, 30, 59)):
        raise PaperDenied("GATEWAY_LATE_SIGNAL_REGISTRATION")
    if not recorded <= read_back <= now or now - read_back > timedelta(seconds=15):
        raise PaperDenied("GATEWAY_STALE_SIGNAL_REGISTRATION_READBACK")
    _check_frozen_dataset_coverage(frozen_dataset, sessions, decision, recorded)
    if (registration.get("decision_at") != signal["as_of"]
            or registration.get("signal_id") != signal["signal_id"]
            or registration.get("signal_sha256") != _digest(dict(signal))
            or registration.get("frozen_dataset_sha256") != _digest(dict(frozen_dataset))
            or registration.get("parameters_sha256") != _digest(DEFAULT_CONFIG)):
        raise PaperDenied("GATEWAY_FROZEN_SIGNAL_REGISTRATION_MISMATCH")
    try:
        today = decision.astimezone(SHANGHAI).date()
        base = sessions.index(today)
    except ValueError as exc:
        raise PaperDenied("GATEWAY_NOT_OFFICIAL_TRADING_DAY") from exc
    if base + 20 >= len(sessions):
        raise PaperDenied("GATEWAY_MISSING_20_FUTURE_SESSIONS")
    outcomes = registration.get("outcome_contracts")
    if not isinstance(outcomes, list) or len(outcomes) != 2:
        raise PaperDenied("GATEWAY_MISSING_PROSPECTIVE_OUTCOME_CONTRACTS")
    by_horizon: dict[int, dict[str, Any]] = {}
    for row in outcomes:
        if not isinstance(row, Mapping) or type(row.get("horizon_trading_days")) is not int:
            raise PaperDenied("GATEWAY_INVALID_PROSPECTIVE_OUTCOME_CONTRACT")
        horizon = row["horizon_trading_days"]
        if horizon in by_horizon:
            raise PaperDenied("GATEWAY_DUPLICATE_PROSPECTIVE_OUTCOME_CONTRACT")
        by_horizon[horizon] = dict(row)
    if set(by_horizon) != {5, 20}:
        raise PaperDenied("GATEWAY_MISSING_PROSPECTIVE_OUTCOME_CONTRACTS")
    contract_ids = []
    for horizon in (5, 20):
        row = by_horizon[horizon]
        contract_id = row.get("outcome_contract_id")
        if (not isinstance(contract_id, str) or not contract_id
                or row.get("session_date") != sessions[base + horizon].isoformat()
                or row.get("decision_id") != registration.get("forward_decision_id")):
            raise PaperDenied("GATEWAY_PROSPECTIVE_OUTCOME_CONTRACT_MISMATCH")
        contract_ids.append(contract_id)
    if len(set(contract_ids)) != 2 or not isinstance(registration.get("forward_decision_id"), str) or not registration["forward_decision_id"]:
        raise PaperDenied("GATEWAY_DUPLICATE_PROSPECTIVE_OUTCOME_CONTRACT")
    _sha(registration.get("forward_decision_sha256"), "forward_decision_hash")
    record_material = {field: registration[field] for field in _REGISTRATION_RECORD_FIELDS}
    if registration["raw_sha256"] != _digest(record_material):
        raise PaperDenied("GATEWAY_SIGNAL_REGISTRY_RAW_HASH_MISMATCH")
    if not callable(verifier):
        raise PaperDenied("GATEWAY_MISSING_EXTERNAL_REGISTRATION_VERIFIER")
    try:
        proof = verifier(dict(registration))
    except Exception as exc:
        raise PaperDenied("GATEWAY_REGISTRATION_INCLUSION_NOT_VERIFIED") from exc
    if (not isinstance(proof, Mapping) or proof.get("status") != "VERIFIED_APPEND_ONLY_INCLUSION"
            or proof.get("registry_id") != registration["registry_id"]
            or proof.get("record_id") != registration["record_id"]
            or proof.get("record_sha256") != registration["raw_sha256"]
            or proof.get("recorded_at") != registration["recorded_at"]
            or proof.get("registry_root_sha256") != registration["registry_root_sha256"]
            or proof.get("read_back_at") != registration["read_back_at"]
            or not isinstance(proof.get("verifier_identity"), str) or not proof["verifier_identity"]):
        raise PaperDenied("GATEWAY_REGISTRATION_INCLUSION_NOT_VERIFIED")
    _sha(proof.get("proof_sha256"), "registration_inclusion_proof_hash")
    verified = _time(proof.get("verified_at"), "registration_verified_at")
    if not read_back <= verified <= now or now - verified > timedelta(seconds=15):
        raise PaperDenied("GATEWAY_STALE_REGISTRATION_VERIFICATION")
    return {"registry_id": registration["registry_id"], "record_id": registration["record_id"],
            "source_ref": registration["source_ref"], "raw_sha256": registration["raw_sha256"],
            "registry_root_sha256": registration["registry_root_sha256"],
            "recorded_at": recorded.isoformat(), "read_back_at": read_back.isoformat(),
            "signal_sha256": registration["signal_sha256"],
            "frozen_dataset_sha256": registration["frozen_dataset_sha256"],
            "parameters_sha256": registration["parameters_sha256"],
            "forward_decision_id": registration["forward_decision_id"],
            "forward_decision_sha256": registration["forward_decision_sha256"],
            "outcome_contracts": [by_horizon[5], by_horizon[20]],
            "inclusion_proof_sha256": proof["proof_sha256"],
            "verifier_identity": proof["verifier_identity"]}


def build_entry_ticket(
    *,
    signal: Mapping[str, Any],
    frozen_dataset: Mapping[str, Any],
    signal_registration_readback: Mapping[str, Any],
    registration_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    grant: PaperGrant,
    provider_snapshot: Mapping[str, Any],
    quote_readback: Mapping[str, Any],
    fee_margin_readback: Mapping[str, Any],
    exchange_calendar: Mapping[str, Any],
    ledger: PaperLedger,
    issued_signal_ids: AbstractSet[str],
    execution_intent_id: str,
    capital_admission_id: str,
    now: datetime,
    signing_key: bytes,
) -> dict[str, Any]:
    """Return a locally signed ticket; no external side effects or transport."""
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise PaperDenied("GATEWAY_NAIVE_NOW")
    now = now.astimezone(timezone.utc)
    local = now.astimezone(SHANGHAI)
    if not (time(9, 0) <= local.time() < time(9, 5)):
        raise PaperDenied("GATEWAY_OUTSIDE_ENTRY_WINDOW")
    if not isinstance(grant, PaperGrant) or not grant.enabled or grant.environment != SIMNOW_FIRST:
        raise PaperDenied("GATEWAY_PAPER_GRANT_DISABLED")
    if (_decimal(grant.strategy_initial_equity, "grant_equity") != Decimal("5000000")
            or _decimal(grant.max_risk_fraction, "grant_risk_fraction") > Decimal("0.005")
            or _decimal(grant.max_drawdown_fraction, "grant_drawdown_fraction") > Decimal("0.05")
            or _decimal(grant.max_margin_fraction, "grant_margin_fraction") > Decimal("0.30")):
        raise PaperDenied("GATEWAY_GRANT_EXCEEDS_FROZEN_LIMITS")
    if not isinstance(ledger, PaperLedger):
        raise PaperDenied("GATEWAY_MISSING_LEDGER")
    ledger.verify_chain()
    if ledger.is_frozen():
        raise PaperDenied("GATEWAY_UNRECONCILED_LEDGER")
    if not isinstance(issued_signal_ids, (set, frozenset)):
        raise PaperDenied("GATEWAY_MISSING_ISSUED_SIGNAL_REGISTER")
    if not isinstance(signal, Mapping) or signal.get("pit_mode") != "strict":
        raise PaperDenied("GATEWAY_NON_STRICT_SIGNAL")
    if signal.get("entry") is not True or signal.get("actionable_entry") is not True:
        raise PaperDenied("GATEWAY_SIGNAL_NOT_ACTIONABLE")
    if signal.get("reason") != "CANDIDATE_ENTRY_SUBJECT_TO_RISK_AND_FILL" or signal.get("requires_gateway_readback") is not True:
        raise PaperDenied("GATEWAY_SIGNAL_SCOPE_MISMATCH")
    signal_id = signal.get("signal_id")
    _sha(signal_id, "signal_id")
    if signal_id in issued_signal_ids:
        raise PaperDenied("GATEWAY_REPEAT_SIGNAL")
    decision = _time(signal.get("as_of"), "decision_at")
    if decision.astimezone(SHANGHAI).date() != local.date() or decision.astimezone(SHANGHAI).time() != time(8, 30):
        raise PaperDenied("GATEWAY_DECISION_TIME_MISMATCH")
    if _time(signal.get("valid_from"), "valid_from").astimezone(SHANGHAI).time() != time(9, 0) or _time(
            signal.get("valid_until"), "valid_until").astimezone(SHANGHAI).time() != time(9, 5):
        raise PaperDenied("GATEWAY_SIGNAL_WINDOW_MISMATCH")
    if not isinstance(frozen_dataset, Mapping):
        raise PaperDenied("GATEWAY_MISSING_FROZEN_DATASET")
    # Strategy output does not encode variant. Recompute it from the exact
    # frozen input so a single-factor/reconstructed signal cannot be relabelled.
    try:
        replay = replay_frozen_signal(frozen_dataset, local.date().isoformat())
    except (TypeError, ValueError) as exc:
        raise PaperDenied("GATEWAY_SIGNAL_REPLAY_FAILED") from exc
    if dict(signal) != replay:
        raise PaperDenied("GATEWAY_SIGNAL_REPLAY_MISMATCH")
    sessions = _canonical_sessions(exchange_calendar, decision, signal["exchange_calendar_ref"])
    registration = _check_prior_registration(signal_registration_readback, signal, frozen_dataset,
                                             sessions, decision, now, registration_verifier)
    if not isinstance(signal.get("contract"), str) or re.fullmatch(r"au\d{4}", signal["contract"]) is None:
        raise PaperDenied("GATEWAY_NOT_DATED_AU")
    contract = signal["contract"]
    if not isinstance(provider_snapshot, Mapping) or provider_snapshot.get("source") != "provider_readback":
        raise PaperDenied("GATEWAY_NO_BROKER_READBACK")
    if (provider_snapshot.get("identity_verified") is not True or provider_snapshot.get("environment") != SIMNOW_FIRST
            or provider_snapshot.get("account_id") != grant.account_id or provider_snapshot.get("robot_id") != grant.robot_id
            or provider_snapshot.get("connected") is not True or provider_snapshot.get("reconciled") is not True):
        raise PaperDenied("GATEWAY_UNVERIFIED_ACCOUNT_OR_STATE")
    _fresh(provider_snapshot, now, 15, "broker")
    validate_au_metadata(provider_snapshot.get("contract_meta"), contract)
    if provider_snapshot.get("positions") != [] or provider_snapshot.get("open_order_ids") != []:
        raise PaperDenied("GATEWAY_EXISTING_POSITION_OR_ORDER")
    if (not isinstance(quote_readback, Mapping) or quote_readback.get("source") != "broker_quote_readback"
            or quote_readback.get("identity_verified") is not True or quote_readback.get("connected") is not True
            or quote_readback.get("environment") != SIMNOW_FIRST
            or quote_readback.get("account_id") != grant.account_id
            or quote_readback.get("robot_id") != grant.robot_id
            or quote_readback.get("exchange") != "SHFE" or quote_readback.get("contract") != contract):
        raise PaperDenied("GATEWAY_UNVERIFIED_QUOTE")
    _sha(quote_readback.get("raw_sha256"), "quote_hash")
    _fresh(quote_readback, now, 5, "quote")
    ask = _price(quote_readback.get("best_ask"), "best_ask")
    bid = _price(quote_readback.get("best_bid"), "best_bid")
    if bid > ask:
        raise PaperDenied("GATEWAY_CROSSED_QUOTE")
    if (not isinstance(fee_margin_readback, Mapping)
            or fee_margin_readback.get("source") != "broker_fee_margin_readback"
            or fee_margin_readback.get("identity_verified") is not True
            or fee_margin_readback.get("environment") != SIMNOW_FIRST
            or fee_margin_readback.get("account_id") != grant.account_id
            or fee_margin_readback.get("contract") != contract):
        raise PaperDenied("GATEWAY_UNVERIFIED_FEES_OR_MARGIN")
    _sha(fee_margin_readback.get("raw_sha256"), "fee_margin_hash")
    _fresh(fee_margin_readback, now, 300, "fee_margin")
    fee_open = _decimal(fee_margin_readback.get("fee_open_per_lot_cny"), "fee_open", positive=False)
    fee_close_today = _decimal(fee_margin_readback.get("fee_close_today_per_lot_cny"), "fee_close_today", positive=False)
    fee_close_yesterday = _decimal(fee_margin_readback.get("fee_close_yesterday_per_lot_cny"), "fee_close_yesterday", positive=False)
    margin = _decimal(fee_margin_readback.get("margin_for_one_lot_cny"), "margin")
    if margin != _decimal(provider_snapshot.get("margin_for_one_lot"), "broker_margin"):
        raise PaperDenied("GATEWAY_MARGIN_READBACK_MISMATCH")
    fee_upper = _decimal(provider_snapshot.get("round_trip_fee_upper_cny"), "broker_fee_upper", positive=False)
    if fee_upper < fee_open + max(fee_close_today, fee_close_yesterday):
        raise PaperDenied("GATEWAY_FEE_READBACK_MISMATCH")
    exit_deadline, roll_deadline, roll_before_exit = _deadlines(sessions, local.date(), contract)
    if _time(roll_deadline, "roll_deadline") <= now:
        raise PaperDenied("GATEWAY_ROLL_DEADLINE_PASSED")
    atr = _decimal(signal.get("atr20_cny_per_gram"), "atr20")
    limit = ask + 5 * TICK
    stop = ((limit - 2 * atr) / TICK).to_integral_value(rounding=ROUND_CEILING) * TICK
    if stop <= 0 or stop >= bid:
        raise PaperDenied("GATEWAY_INVALID_PROTECTIVE_STOP")
    credit = _decimal(signal.get("risk", {}).get("credit_multiplier"), "credit_multiplier")
    volatility = _decimal(signal.get("risk", {}).get("volatility_multiplier"), "volatility_multiplier")
    if credit not in {Decimal("0.5"), Decimal("1")} or volatility not in {Decimal("0.5"), Decimal("1")}:
        raise PaperDenied("GATEWAY_INVALID_RISK_MULTIPLIERS")
    mark = ledger.latest_equity_mark()
    validate_strategy_equity_mark(mark, provider_snapshot, now)
    equity, peak = ledger.strategy_equity(Decimal("5000000"))
    if (peak - equity) / peak >= _decimal(grant.max_drawdown_fraction, "max_drawdown_fraction"):
        raise PaperDenied("GATEWAY_DRAWDOWN_STOP")
    risk_budget = min(_decimal(signal["risk"]["amount_cny"], "signal_risk_budget"),
                      equity * _decimal(grant.max_risk_fraction, "grant_risk_fraction") * credit * volatility)
    planned_loss = (limit - stop) * MULTIPLIER + fee_upper
    if planned_loss > risk_budget:
        raise PaperDenied("GATEWAY_PLANNED_LOSS_LIMIT")
    available = _decimal(provider_snapshot.get("available"), "available")
    margin_used = _decimal(provider_snapshot.get("margin_in_use"), "margin_in_use", positive=False)
    if margin > available or margin_used + margin > equity * _decimal(grant.max_margin_fraction, "grant_margin_fraction"):
        raise PaperDenied("GATEWAY_MARGIN_LIMIT")
    if _decimal(provider_snapshot.get("broker_equity"), "broker_equity") <= 0:
        raise PaperDenied("GATEWAY_BROKER_EQUITY_UNKNOWN")
    evidence = {
        "signal_id": signal_id,
        "signal_evidence_sha256": signal["evidence_sha256"],
        "quote_raw_sha256": quote_readback["raw_sha256"],
        "fee_margin_raw_sha256": fee_margin_readback["raw_sha256"],
        "calendar_raw_sha256": exchange_calendar["raw_sha256"],
        "broker_snapshot_hash": _digest(dict(provider_snapshot)),
        "ledger_root_hash": ledger.root_hash,
        "execution_intent_id": execution_intent_id,
        "capital_admission_id": capital_admission_id,
        "prior_signal_registration": registration,
    }
    ticket_evidence_hash = _digest(evidence)
    stable_id = hashlib.sha256((signal_id + "|" + grant.account_id + "|" + contract).encode()).hexdigest()[:24].upper()
    slippage_bps = ((5 * TICK / ask) * Decimal("10000")).quantize(Decimal("0.000001"), rounding=ROUND_CEILING)
    expires = min(now + timedelta(minutes=5), datetime.combine(local.date(), time(9, 5), SHANGHAI).astimezone(timezone.utc))
    command = {
        "schema_version": "1.0.0", "program": PROGRAM,
        "command_id": "CMD-GOLD2-" + stable_id,
        "action_contract_id": "AC-GOLD2-" + stable_id,
        "execution_intent_id": execution_intent_id,
        "capital_admission_id": capital_admission_id,
        "human_approval_ref": grant.human_approval_ref,
        "program_approval_ref": grant.program_approval_ref,
        "decision_at": decision.isoformat(),
        "issued_at": now.isoformat(), "not_before_at": now.isoformat(), "expires_at": expires.isoformat(),
        "environment": SIMNOW_FIRST, "account_id": grant.account_id, "robot_id": grant.robot_id,
        "contract": contract, "action": "OPEN_LONG", "reason": "ENTRY", "quantity": 1,
        "reference_price": f"{ask:.2f}", "limit_price": f"{limit:.2f}", "stop_price": f"{stop:.2f}",
        "exit_not_after_at": exit_deadline, "roll_not_after_at": roll_deadline,
        "credit_multiplier": str(credit), "volatility_multiplier": str(volatility),
        "max_slippage_bps": str(slippage_bps), "evidence_hash": ticket_evidence_hash,
        "live_execution_authorized": False, "real_capital_movement_authorized": False,
    }
    if set(command) != COMMAND_FIELDS - {"contract_hash"}:
        raise PaperDenied("GATEWAY_COMMAND_SCHEMA_DRIFT")
    envelope = sign_command(command, signing_key)
    admitted = admit_command(envelope, signing_key, grant, provider_snapshot, ledger, now)
    if admitted["decision"] != "ALLOW":
        raise PaperDenied("GATEWAY_REPEAT_COMMAND")
    ticket = {
        "schema_version": "gold-au-gateway-ticket.v1",
        "status": "PREPARED_NOT_SENT",
        "signal_id": signal_id,
        "prior_signal_registration": registration,
        "prepared_at": now.isoformat(),
        "envelope": envelope,
        "evidence": evidence,
        "planned_one_lot_loss_cny": str(planned_loss),
        "allowed_one_lot_loss_cny": str(risk_budget),
        "stop_basis": "WORST_PERMITTED_LIMIT_FILL_MINUS_2_ATR20_ROUNDED_TIGHTER",
        "roll_before_max_hold": roll_before_exit,
        "transport_attempted": False,
    }
    ticket["ticket_hash"] = _digest(ticket)
    return ticket
