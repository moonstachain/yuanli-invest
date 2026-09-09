from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "packages" / "contracts" / "schemas" / "vnext"
CONFIG = ROOT / "config" / "yex0" / "yex0_constitution.v0.1.json"
FIXTURE = ROOT / "fixtures" / "yex0" / "yex0_positive_bundle.v0.1.json"
POSITION_PASSPORT = VNEXT / "position-passport.schema.json"

SCHEMAS = {
    "capital_admission": VNEXT / "capital-admission.schema.json",
    "execution_intent": VNEXT / "execution-intent.schema.json",
    "action_contract": VNEXT / "action-contract.schema.json",
    "execution_event": VNEXT / "execution-event.schema.json",
    "execution_settlement": VNEXT / "execution-settlement.schema.json",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_fixture_bundle() -> dict[str, Any]:
    return load_json(FIXTURE)


def validate_constitution() -> None:
    c = load_json(CONFIG)
    require(c["program_id"] == "YEX0", "wrong program id")
    require(
        c["authority_separation"] == ["ResearchAuthority", "CapitalAuthority", "ExecutionAuthority"],
        "authority separation drift",
    )
    require(c["firewall"]["unknown_semantics"] == "DENY", "UNKNOWN must mean DENY")
    require(set(c["execution_modes"]) == {"shadow", "broker_paper"}, "unexpected execution mode")
    require(c["live_execution_authorized"] is False, "YEX0 cannot authorize live execution")
    require(c["real_capital_movement_authorized"] is False, "YEX0 cannot authorize real capital movement")
    require(
        c["four_way_reconciliation"]
        == ["capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"],
        "four-way reconciliation drift",
    )
    required_laws = {
        "RESEARCH_PASS_NE_CAPITAL_PASS",
        "CAPITAL_PASS_NE_EXECUTION_PASS",
        "POSITION_PASSPORT_NE_EXECUTION_AUTHORITY",
        "INTENT_NE_AUTHORIZATION",
        "UNKNOWN_EQUALS_DENY",
        "RECEIPT_EQUALS_LEDGER_STATUS_EQUALS_PROJECTION",
        "FOUR_WAY_RECONCILIATION",
        "RESEARCH_FAILURE_NE_EXECUTION_FAILURE",
        "NO_LIVE_AUTHORITY_IN_YEX0",
    }
    require(required_laws.issubset(set(c["laws"])), "constitutional law missing")


def validate_schema_shapes(bundle: dict[str, Any]) -> None:
    checker = FormatChecker()
    for name, path in SCHEMAS.items():
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=checker)
        if name == "execution_event":
            for event in bundle["execution_events"]:
                errors = sorted(validator.iter_errors(event), key=lambda e: list(e.path))
                require(not errors, f"execution event schema failure: {errors[0].message if errors else ''}")
        else:
            errors = sorted(validator.iter_errors(bundle[name]), key=lambda e: list(e.path))
            require(not errors, f"{name} schema failure: {errors[0].message if errors else ''}")


def validate_position_passport_authority() -> None:
    schema = load_json(POSITION_PASSPORT)
    authority = schema["properties"]["authority"]["properties"]
    for key in (
        "portfolio_weight_authority",
        "position_sizing_authority",
        "trade_execution_authority",
        "live_execution_authority",
    ):
        require(authority[key].get("const") is False, f"PositionPassport authority escalated: {key}")


def validate_reference_integrity(bundle: dict[str, Any]) -> None:
    admission = bundle["capital_admission"]
    intent = bundle["execution_intent"]
    contract = bundle["action_contract"]
    settlement = bundle["execution_settlement"]
    events = bundle["execution_events"]

    require(intent["capital_admission_id"] == admission["capital_admission_id"], "intent/admission mismatch")
    require(intent["position_passport_id"] == admission["position_passport_id"], "passport mismatch")
    require(contract["execution_intent_id"] == intent["execution_intent_id"], "contract/intent mismatch")
    require(contract["capital_admission_id"] == admission["capital_admission_id"], "contract/admission mismatch")
    require(settlement["execution_intent_id"] == intent["execution_intent_id"], "settlement/intent mismatch")
    require(settlement["action_contract_id"] == contract["action_contract_id"], "settlement/contract mismatch")
    for event in events:
        require(event["execution_intent_id"] == intent["execution_intent_id"], "event/intent mismatch")
        require(event["action_contract_id"] == contract["action_contract_id"], "event/contract mismatch")
        require(event["stream_id"] == settlement["stream_id"], "event/stream mismatch")


def validate_authority_integrity(bundle: dict[str, Any]) -> None:
    validate_position_passport_authority()
    admission = bundle["capital_admission"]
    intent = bundle["execution_intent"]
    contract = bundle["action_contract"]
    settlement = bundle["execution_settlement"]

    for key in ("order_submission_authority", "live_execution_authority", "real_capital_movement_authority"):
        require(admission["authority"].get(key) is False, f"capital admission authority escalated: {key}")
    require(intent.get("self_execution_authorized") is False, "intent self-authorized")
    require(contract.get("live_execution_authorized") is False, "live execution authorized")
    require(contract.get("real_capital_movement_authorized") is False, "real capital movement authorized")
    require(contract["execution_mode"] in {"shadow", "broker_paper"}, "invalid execution mode")
    require(
        settlement["authority"]["grants_new_capital_authority"] is False,
        "settlement grants capital authority",
    )
    require(
        settlement["authority"]["grants_new_execution_authority"] is False,
        "settlement grants execution authority",
    )


def validate_scope_integrity(bundle: dict[str, Any]) -> None:
    intent = bundle["execution_intent"]
    contract = bundle["action_contract"]
    limits = intent["limits"]
    scope = contract["scope"]
    for key in ("max_quantity_abs", "max_notional", "max_loss", "max_slippage_bps"):
        require(scope[key] <= limits[key], f"action contract expands {key}")
    require(set(scope["allowed_venues"]).issubset(set(intent["allowed_venues"])), "action contract expands venues")
    admission = bundle["capital_admission"]
    require(contract["execution_mode"] in admission["mode_eligibility"], "action mode not capital-admitted")
    require(abs(intent["quantity_delta"]) <= limits["max_quantity_abs"], "intent quantity exceeds own limit")
    require(limits["max_notional"] <= admission["risk_budget"]["max_notional"], "intent exceeds capital notional budget")
    require(limits["max_loss"] <= admission["risk_budget"]["max_loss"], "intent exceeds capital loss budget")


def validate_time_integrity(bundle: dict[str, Any]) -> None:
    admission = bundle["capital_admission"]
    intent = bundle["execution_intent"]
    contract = bundle["action_contract"]
    a = admission["lifecycle"]

    require(parse_time(a["created_at"]) <= parse_time(a["valid_from"]) < parse_time(a["expires_at"]), "invalid admission window")
    require(parse_time(intent["created_at"]) <= parse_time(intent["valid_from"]) < parse_time(intent["expires_at"]), "invalid intent window")
    require(parse_time(contract["issued_at"]) < parse_time(contract["expires_at"]), "invalid action-contract window")
    require(parse_time(contract["issued_at"]) >= parse_time(intent["valid_from"]), "contract issued before intent validity")
    require(parse_time(contract["expires_at"]) <= parse_time(intent["expires_at"]), "contract outlives intent")
    require(parse_time(intent["expires_at"]) <= parse_time(a["expires_at"]), "intent outlives capital admission")


def validate_ledger_integrity(bundle: dict[str, Any]) -> None:
    events = bundle["execution_events"]
    require(events, "empty event ledger")
    event_ids: set[str] = set()
    idem: set[str] = set()
    prior_hash = None
    prior_recorded = None
    for expected_sequence, event in enumerate(events, start=1):
        require(event["sequence"] == expected_sequence, "non-monotonic event sequence")
        require(event.get("append_only") is True, "event ledger is not append-only")
        require(event["event_id"] not in event_ids, "duplicate event id")
        require(event["idempotency_key"] not in idem, "duplicate event idempotency key")
        require(event["previous_event_hash"] == prior_hash, "event hash chain broken")
        require(event["event_hash"].startswith("sha256:") and len(event["event_hash"]) == 71, "invalid event hash")
        occurred = parse_time(event["occurred_at"])
        recorded = parse_time(event["recorded_at"])
        require(recorded >= occurred, "event recorded before occurrence")
        if prior_recorded is not None:
            require(recorded >= prior_recorded, "recorded-at sequence regressed")
        event_ids.add(event["event_id"])
        idem.add(event["idempotency_key"])
        prior_hash = event["event_hash"]
        prior_recorded = recorded
    require(bundle["execution_settlement"].get("projection_is_truth") is False, "projection declared as truth")
    require(events[-1]["event_type"] == "SettlementClosed", "ledger not closed by settlement event")


def validate_reconciliation_integrity(bundle: dict[str, Any]) -> None:
    settlement = bundle["execution_settlement"]
    recon = settlement["reconciliation"]
    required = {"capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"}
    require(set(recon) == required, "four-way reconciliation incomplete")
    allowed_match = {"MATCHED", "SIMULATED_MATCH"}
    if settlement["status"] == "SETTLED":
        for key in required:
            require(recon[key]["status"] in allowed_match, f"unsettled reconciliation leg: {key}")
    drift = settlement["drift"]
    require(drift["unknown_external_orders"] == 0, "unknown external order")
    require(drift["unexplained_fills"] == 0, "unexplained fill")
    require(drift["unexplained_position_delta"] == 0, "unexplained position drift")
    require(drift["unexplained_cash_delta"] == 0, "unexplained cash drift")
    require(settlement["research_outcome_ref"] is not None, "research and execution settlement channels not linked")
    require("execution_quality" in settlement, "execution quality missing")


def validate_idempotency_integrity(bundle: dict[str, Any]) -> None:
    intent = bundle["execution_intent"]
    contract = bundle["action_contract"]
    require(intent["idempotency_key"] != contract["idempotency_key"], "intent and action contract idempotency keys must be distinct")
    require(len(intent["idempotency_key"]) >= 8 and len(contract["idempotency_key"]) >= 8, "weak idempotency key")


def validate_bundle(bundle: dict[str, Any]) -> None:
    validate_constitution()
    validate_schema_shapes(bundle)
    validate_reference_integrity(bundle)
    validate_authority_integrity(bundle)
    validate_scope_integrity(bundle)
    validate_time_integrity(bundle)
    validate_ledger_integrity(bundle)
    validate_reconciliation_integrity(bundle)
    validate_idempotency_integrity(bundle)


def main() -> None:
    bundle = load_fixture_bundle()
    validate_bundle(bundle)
    print("YEX0_CONSTITUTION_MACHINE_QUALIFIED")


if __name__ == "__main__":
    main()
