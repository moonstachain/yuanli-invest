from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "benchmarks" / "yios-g1-gold-genesis-canonical-reality-loop-v1.json"
SCHEMA = ROOT / "packages" / "contracts" / "schemas" / "golden-reality-loop-benchmark-registry.schema.json"
G1 = ROOT / "config" / "yios_g1" / "gold_g1_reality_trial.v1.json"
G3 = ROOT / "config" / "yios_g1" / "gold_g3_shadow_action.v1.json"
G4 = ROOT / "config" / "yios_g1" / "gold_g4_shadow_runtime_settlement.v1.json"
G4_RECEIPT = ROOT / "docs" / "architecture" / "yios_g1" / "YIOS-G1-G4-RUNTIME-SETTLEMENT-RECEIPT-v1.0.json"

EXPECTED_LINEAGE = [
    {"stage": "YIOS0", "commit_sha": "61412df120faca8b30d87572175e3be8ed021213"},
    {"stage": "A0", "commit_sha": "fa5dc9bf73b200e5ee91debf6e95e6097fbbc17a"},
    {"stage": "G1", "commit_sha": "6ca14e6edd2d9a48a3f3e1847aff87d77e180634"},
    {"stage": "G3", "commit_sha": "558275fe3fb4dcd13e4809c466b336a9119f02fe"},
    {"stage": "G4", "commit_sha": "b931a65a9a8532cca5d03992575e999015897361"},
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_schema(obj: dict[str, Any]) -> None:
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    require(not errors, f"registry schema failure: {errors[0].message if errors else ''}")


def validate_lineage(obj: dict[str, Any]) -> None:
    require(obj["canon_lineage"] == EXPECTED_LINEAGE, "canonical lineage drift")
    for node in EXPECTED_LINEAGE:
        completed = subprocess.run(
            ["git", "merge-base", "--is-ancestor", node["commit_sha"], "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        require(completed.returncode == 0, f"lineage commit is not an ancestor of HEAD: {node['stage']} {node['commit_sha']}")


def validate_source_settlements(obj: dict[str, Any]) -> None:
    g1 = load_json(G1)
    g3 = load_json(G3)
    g4 = load_json(G4)
    receipt = load_json(G4_RECEIPT)

    frozen = obj["frozen_settlement"]
    require(g1["primary_research_settlement_candidate"] == "INDETERMINATE", "G1 primary settlement changed")
    require(frozen["scientific_primary"] == "INDETERMINATE", "registry scientific settlement changed")

    require(g3["capital_admission"]["decision"] == "deny", "G3 capital admission changed")
    require(frozen["capital_settlement"] == "DENY", "registry capital settlement changed")

    require(g4["capital_admission"]["decision"] == "DENY", "G4 capital admission changed")
    require(g4["execution_settlement"]["status"] == "FAIL_CLOSED", "G4 execution settlement changed")
    require(receipt["runtime_outcome"] == "FAIL_CLOSED_VALID", "G4 runtime outcome changed")
    require(frozen["runtime_settlement"] == "FAIL_CLOSED_VALID", "registry runtime settlement changed")

    require(g4["learning"]["outcome"] == "DENIAL_IS_VALID_EXECUTION_OUTCOME", "G4 learning changed")
    require(receipt["learning_outcome"] == "DENIAL_IS_VALID_EXECUTION_OUTCOME", "G4 receipt learning changed")
    require(frozen["learning"] == "DENIAL_IS_VALID_EXECUTION_OUTCOME", "registry learning changed")


def validate_runtime_invariants(obj: dict[str, Any]) -> None:
    g4 = load_json(G4)
    inv = obj["runtime_invariants"]
    runtime = g4["execution_runtime"]

    require(g4["research_input"]["unknown_semantics"] == "DENY", "UNKNOWN semantics drift")
    require(inv["unknown_semantics"] == "DENY", "registry UNKNOWN semantics drift")
    require(g4["capital_admission"]["max_notional"] == 0, "G4 nonzero max_notional")
    require(g4["capital_admission"]["max_loss"] == 0, "G4 nonzero max_loss")
    require(runtime["quantity_delta"] == 0, "G4 nonzero quantity_delta")
    require(runtime["mode"] == "SHADOW", "G4 escaped SHADOW mode")
    require(runtime["provider"] == "INTERNAL_SYNTHETIC_ONLY", "G4 provider drift")
    for key in ("external_network_used", "oms_invoked", "broker_invoked", "veighna_invoked"):
        require(runtime[key] is False, f"G4 external runtime escalation: {key}")

    event_types = {event["event_type"] for event in runtime["events"]}
    forbidden = {"OrderSubmitted", "OrderAccepted", "PartialFillReceived", "FillReceived"}
    require(not event_types.intersection(forbidden), "G4 emitted forbidden order/fill event")

    recon = g4["execution_settlement"]["reconciliation"]
    require(set(recon) == {"capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"}, "G4 four-way reconciliation incomplete")


def validate_activation_and_authority(obj: dict[str, Any]) -> None:
    require(obj["registry_state"] == "REGISTERED_PENDING_REALITY_ACTIVATION", "registry must not self-declare ACTIVE before post-merge Reality closure")
    require(obj["activation_target"] == "ACTIVE", "wrong activation target")
    require(obj["benchmark_meaning"] == "SYSTEM_REALITY_LOOP_CORRECTNESS_NOT_GOLD_PRICE_PREDICTION", "benchmark meaning drift")
    activation = obj["activation"]
    require(activation["self_activation_authorized"] is False, "registry self-activation is forbidden")
    require(
        activation["required_reality_gates"]
        == ["EXACT_HEAD_CI_SUCCESS", "PROTECTED_MAIN_MERGE", "FRESH_MAIN_READBACK", "POST_MERGE_CI_SUCCESS"],
        "activation gates drift",
    )
    require(activation["effective_state_rule"] == "ACTIVE_IFF_ALL_REQUIRED_REALITY_GATES_PASS", "activation rule drift")
    require(all(value is False for value in obj["non_authorizations"].values()), "benchmark registration escalated downstream authority")


def validate_gold_genesis_benchmark_registry() -> None:
    obj = load_json(REGISTRY)
    validate_schema(obj)
    validate_lineage(obj)
    validate_source_settlements(obj)
    validate_runtime_invariants(obj)
    validate_activation_and_authority(obj)


def main() -> None:
    validate_gold_genesis_benchmark_registry()
    print("GOLD_GENESIS_CANONICAL_REALITY_LOOP_v1_REGISTRY_CONTRACT_VALID")
    print("effective_state=REGISTERED_PENDING_REALITY_ACTIVATION")


if __name__ == "__main__":
    main()
