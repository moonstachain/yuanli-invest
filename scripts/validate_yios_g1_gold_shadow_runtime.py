from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TRIAL = ROOT / "config" / "yios_g1" / "gold_g1_reality_trial.v1.json"
G3 = ROOT / "config" / "yios_g1" / "gold_g3_shadow_action.v1.json"
RUNTIME = ROOT / "config" / "yios_g1" / "gold_g4_shadow_runtime_settlement.v1.json"
RECEIPT = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G4-RUNTIME-SETTLEMENT-RECEIPT-v1.0.json"
DESIGN = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G4-GOLD-SHADOW-RUNTIME-SETTLEMENT-v1.0.md"
LEARNING = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G4-LEARNING-DELTA-v1.0.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_lineage(trial: dict[str, Any], g3: dict[str, Any], runtime: dict[str, Any]) -> None:
    require(trial["primary_research_settlement_candidate"] == "INDETERMINATE", "G1 primary settlement was rewritten")
    require(trial["hypothesis_results"]["H1_OFFICIAL_DEMAND_STRUCTURAL"]["status"] == "INDETERMINATE", "H1 was rewritten")
    require(g3["research_settlement"]["primary_settlement"] == "INDETERMINATE", "G3 rewrote G1 settlement")
    require(g3["capital_admission"]["decision"] == "deny", "G3 did not preserve capital denial")
    require(g3["chain_result"] == "FAIL_CLOSED_AT_CAPITAL_ADMISSION", "G3 chain result drift")
    require(runtime["research_input"]["primary_settlement"] == "INDETERMINATE", "G4 rewrote research input")
    require(runtime["research_input"]["unknown_semantics"] == "DENY", "UNKNOWN semantics drift")


def validate_runtime(runtime: dict[str, Any]) -> None:
    admission = runtime["capital_admission"]
    require(admission["decision"] == "DENY", "INDETERMINATE research escaped capital denial")
    require(admission["max_notional"] == 0 and admission["max_loss"] == 0, "denied capital has nonzero risk budget")

    execution = runtime["execution_runtime"]
    require(execution["mode"] == "SHADOW", "G4 escaped shadow mode")
    require(execution["provider"] == "INTERNAL_SYNTHETIC_ONLY", "G4 used external provider")
    require(execution["quantity_delta"] == 0, "shadow runtime created quantity")
    require(execution["max_notional"] == 0 and execution["max_loss"] == 0, "shadow runtime created risk")
    for flag in ("external_network_used", "oms_invoked", "broker_invoked", "veighna_invoked"):
        require(execution[flag] is False, f"external execution boundary violated: {flag}")

    event_types = [event["event_type"] for event in execution["events"]]
    for forbidden in ("OrderSubmitted", "OrderAccepted", "PartialFillReceived", "FillReceived"):
        require(forbidden not in event_types, f"forbidden execution event present: {forbidden}")
    require("ExecutionFailureObserved" in event_types, "fail-closed observation missing")
    require(event_types[-1] == "SettlementClosed", "runtime ledger did not close")

    settlement = runtime["execution_settlement"]
    require(settlement["status"] == "FAIL_CLOSED", "runtime did not settle fail-closed")
    recon = settlement["reconciliation"]
    require(set(recon) == {"capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"}, "four-way reconciliation incomplete")
    require(recon["capital_intent"]["status"] == "MATCHED", "capital intent mismatch")
    require(recon["yuanli_execution"]["status"] == "SIMULATED_MATCH", "Yuanli shadow mismatch")
    require(recon["execution_engine_oms"]["status"] == "NOT_APPLICABLE" and recon["execution_engine_oms"]["invoked"] is False, "OMS should be N/A")
    require(recon["broker_custodian"]["status"] == "NOT_APPLICABLE" and recon["broker_custodian"]["connected"] is False, "broker should be N/A")
    require(all(value == 0 for value in settlement["drift"].values()), "runtime settlement contains unexplained drift")

    require(runtime["learning"]["outcome"] == "DENIAL_IS_VALID_EXECUTION_OUTCOME", "learning outcome drift")
    for key, value in runtime["authority"].items():
        require(value is False, f"G4 authority escalation: {key}")
    for key, value in runtime["non_authorizations"].items():
        require(value is False, f"G4 non-authorization flipped: {key}")


def validate_receipt(receipt: dict[str, Any]) -> None:
    require(receipt["runtime_outcome"] == "FAIL_CLOSED_VALID", "receipt runtime outcome drift")
    require(receipt["scientific_input"] == "INDETERMINATE", "receipt rewrote scientific input")
    require(receipt["capital_admission"] == "DENY", "receipt rewrote capital admission")
    require(receipt["execution_settlement"] == "FAIL_CLOSED", "receipt rewrote execution settlement")
    require(receipt["learning_outcome"] == "DENIAL_IS_VALID_EXECUTION_OUTCOME", "receipt learning drift")
    for key, value in receipt["authority_changes"].items():
        require(value is False, f"receipt granted authority: {key}")
    require(receipt["benchmark_activation_authorized_by_receipt"] is False, "runtime receipt self-activated benchmark")


def validate_documents() -> None:
    design = DESIGN.read_text(encoding="utf-8")
    learning = LEARNING.read_text(encoding="utf-8")
    for token in (
        "Research Settlement != Capital Admission != Execution Authority",
        "FAIL_CLOSED",
        "No YVN1-A1",
        "No VeighNa",
        "No broker",
        "No live execution",
        "No real capital movement",
    ):
        require(token in design, f"G4 design missing invariant: {token}")
    for token in ("UNKNOWN = DENY", "Denial is a valid execution outcome", "cannot rewrite the scientific settlement"):
        require(token in learning, f"G4 learning delta missing invariant: {token}")


def validate_yios_g1_gold_shadow_runtime() -> None:
    trial = load_json(TRIAL)
    g3 = load_json(G3)
    runtime = load_json(RUNTIME)
    receipt = load_json(RECEIPT)
    validate_lineage(trial, g3, runtime)
    validate_runtime(runtime)
    validate_receipt(receipt)
    validate_documents()


def main() -> None:
    validate_yios_g1_gold_shadow_runtime()
    print("YIOS_G1_G4_GOLD_SHADOW_RUNTIME_FAIL_CLOSED_VALID")


if __name__ == "__main__":
    main()
