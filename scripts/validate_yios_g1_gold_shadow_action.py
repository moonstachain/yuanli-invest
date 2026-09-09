from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from scripts.validate_yex0_capital_execution_constitution import validate_bundle as validate_yex0_bundle

ROOT = Path(__file__).resolve().parents[1]
TRIAL = ROOT / "config" / "yios_g1" / "gold_g1_reality_trial.v1.json"
G2 = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G1-HUMAN-ACCEPTANCE-RECEIPT-v1.0.json"
G3 = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G3-SHADOW-ACTION-AUTHORIZATION-RECEIPT-v1.0.json"
PASSPORT = ROOT / "config" / "yios_g1" / "gold_g3_shadow_position_passport.v1.json"
BUNDLE = ROOT / "config" / "yios_g1" / "gold_g3_shadow_action.v1.json"
LEARNING = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G3-LEARNING-RECEIPT-v1.0.json"
PASSPORT_SCHEMA = ROOT / "packages" / "contracts" / "schemas" / "vnext" / "position-passport.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical_hash(obj: dict[str, Any]) -> str:
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def validate_passport(passport: dict[str, Any]) -> None:
    schema = load_json(PASSPORT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(passport), key=lambda e: list(e.path))
    require(not errors, f"position passport schema failure: {errors[0].message if errors else ''}")
    require(passport["target_id"] == "GOLD", "wrong passport target")
    require(passport["primary_engine"] == "ENG-R", "Gold shadow passport must use ENG-R")
    require(passport["lifecycle"]["status"] == "cancelled", "denied passport cannot remain active")
    require(passport["migration_policy"]["graduation_allowed"] is False, "denied passport cannot graduate")
    for key, value in passport["authority"].items():
        require(value is False, f"passport authority escalated: {key}")


def validate_hashes(bundle: dict[str, Any]) -> None:
    contract = dict(bundle["action_contract"])
    recorded_contract_hash = contract.pop("contract_hash")
    require(recorded_contract_hash == canonical_hash(contract), "action contract hash mismatch")

    prior = None
    for event in bundle["execution_events"]:
        require(event["previous_event_hash"] == prior, "event previous hash mismatch")
        probe = dict(event)
        recorded = probe.pop("event_hash")
        require(recorded == canonical_hash(probe), f"event hash mismatch: {event['event_id']}")
        prior = recorded


def validate_research_and_gates(trial: dict[str, Any], g2: dict[str, Any], g3: dict[str, Any]) -> None:
    require(trial["primary_research_settlement_candidate"] == "INDETERMINATE", "source research settlement changed")
    require(trial["hypothesis_results"]["H1_OFFICIAL_DEMAND_STRUCTURAL"]["status"] == "INDETERMINATE", "H1 changed")
    require(g2["decision"] == "ACCEPT_GOLD_G1_RESEARCH_SETTLEMENT", "G2 decision missing")
    accepted = g2["accepted_research_settlement"]
    require(accepted["primary_settlement"] == "INDETERMINATE", "G2 rewrote research settlement")
    require(accepted["acceptance_does_not_convert_indeterminate_to_supported"] is True, "G2 silently promoted research")
    require(accepted["unknown_semantics"] == "DENY", "G2 UNKNOWN semantics drift")
    require(g2["boundaries_preserved"]["capital_admitted_by_g2"] is False, "G2 granted capital authority")
    require(g2["boundaries_preserved"]["shadow_action_authorized_by_g2"] is False, "G2 improperly authorized G3")

    require(g3["decision"] == "AUTHORIZE_GOLD_G1_SHADOW_ACTION", "G3 authorization missing")
    scope = g3["authorized_scope"]
    require(scope["execution_mode"] == "shadow", "G3 is not shadow-only")
    require(scope["internal_synthetic_only"] is True, "G3 is not internal synthetic only")
    require(scope["case_id"] == "YIOS-GOLD-001", "G3 case binding drift")
    require(scope["capital_gate_may_deny"] is True, "G3 incorrectly forces capital pass")
    require(scope["authorization_does_not_force_admission"] is True, "G3 forces capital admission")
    require(scope["unknown_semantics"] == "DENY", "G3 UNKNOWN semantics drift")
    for key, value in g3["boundaries_preserved"].items():
        require(value is False, f"G3 authority escalation: {key}")


def validate_fail_closed_chain(bundle: dict[str, Any], passport: dict[str, Any], learning: dict[str, Any]) -> None:
    research = bundle["research_settlement"]
    admission = bundle["capital_admission"]
    intent = bundle["execution_intent"]
    contract = bundle["action_contract"]
    settlement = bundle["execution_settlement"]

    require(research["primary_settlement"] == "INDETERMINATE", "bundle rewrote research settlement")
    require(research["unknown_semantics"] == "DENY", "bundle UNKNOWN semantics drift")
    require(admission["decision"] == "deny", "INDETERMINATE research must deny capital in this case")
    require(admission["risk_budget"] == {"max_notional": 0, "max_loss": 0}, "denied admission has nonzero risk budget")
    require(all(v is False for v in admission["authority"].values()), "capital admission gained authority")

    require(intent["quantity_delta"] == 0, "denied capital created nonzero intent")
    require(all(intent["limits"][key] == 0 for key in ("max_quantity_abs", "max_notional", "max_loss", "max_slippage_bps")), "intent has nonzero limits")
    require(intent["self_execution_authorized"] is False, "intent self-authorized")

    require(contract["execution_mode"] == "shadow", "action contract escaped shadow mode")
    require(all(contract["scope"][key] == 0 for key in ("max_quantity_abs", "max_notional", "max_loss", "max_slippage_bps")), "contract has nonzero scope")
    require(contract["live_execution_authorized"] is False, "contract authorized live execution")
    require(contract["real_capital_movement_authorized"] is False, "contract authorized real capital")

    event_types = [event["event_type"] for event in bundle["execution_events"]]
    forbidden_events = {"ActionContractGranted", "FirewallPassed", "PlanCreated", "OrderSubmitted", "OrderAccepted", "PartialFillReceived", "FillReceived"}
    require(not forbidden_events.intersection(event_types), "denied chain reached an executable event")
    require("ExecutionFailureObserved" in event_types, "fail-closed event missing")
    require(event_types[-1] == "SettlementClosed", "execution ledger not closed")

    require(settlement["status"] == "FAIL_CLOSED", "denied chain did not settle FAIL_CLOSED")
    recon = settlement["reconciliation"]
    require(set(recon) == {"capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"}, "four-way reconciliation incomplete")
    require(recon["capital_intent"]["status"] == "MATCHED", "capital intent reconciliation mismatch")
    require(recon["yuanli_execution"]["status"] == "SIMULATED_MATCH", "Yuanli shadow reconciliation mismatch")
    require(recon["execution_engine_oms"]["status"] == "NOT_APPLICABLE", "OMS should not be invoked")
    require(recon["broker_custodian"]["status"] == "NOT_APPLICABLE", "broker should not be connected")
    require(settlement["drift"] == {"unknown_external_orders": 0, "unexplained_fills": 0, "unexplained_position_delta": 0, "unexplained_cash_delta": 0}, "unexpected execution drift")
    require(settlement["authority"]["grants_new_capital_authority"] is False, "settlement granted capital authority")
    require(settlement["authority"]["grants_new_execution_authority"] is False, "settlement granted execution authority")
    require(bundle["chain_result"] == "FAIL_CLOSED_AT_CAPITAL_ADMISSION", "wrong chain result")
    require(all(value is False for value in bundle["non_authorizations"].values()), "bundle escalated downstream authority")

    require(passport["position_passport_id"] == admission["position_passport_id"], "passport/admission mismatch")
    require(learning["learning_outcome"] == "DENIAL_IS_VALID_EXECUTION_OUTCOME", "wrong learning outcome")
    require(learning["observed_chain"]["capital_admission"] == "DENY", "learning rewrote capital result")
    require(learning["observed_chain"]["execution_settlement"] == "FAIL_CLOSED", "learning rewrote execution settlement")
    require(all(value is False for value in learning["authority_changes"].values()), "learning granted authority")


def validate_yios_g1_gold_shadow_action() -> None:
    trial = load_json(TRIAL)
    g2 = load_json(G2)
    g3 = load_json(G3)
    passport = load_json(PASSPORT)
    bundle = load_json(BUNDLE)
    learning = load_json(LEARNING)

    validate_research_and_gates(trial, g2, g3)
    validate_passport(passport)
    validate_yex0_bundle(bundle)
    validate_hashes(bundle)
    validate_fail_closed_chain(bundle, passport, learning)


def main() -> None:
    validate_yios_g1_gold_shadow_action()
    print("YIOS_G1_G3_GOLD_SHADOW_ACTION_FAIL_CLOSED_VALID")


if __name__ == "__main__":
    main()
