from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "packages" / "contracts" / "schemas" / "vnext"
CONFIG = ROOT / "config" / "yvn1" / "yvn1_a0_shadow_execution.v0.1.json"
SCENARIOS = ROOT / "fixtures" / "yvn1" / "yvn1_a0_golden_scenarios.v0.1.json"
YEX0 = ROOT / "config" / "yex0" / "yex0_constitution.v0.1.json"

SCHEMA_PATHS = [
    VNEXT / "execution-plan.schema.json",
    VNEXT / "provider-state.schema.json",
    VNEXT / "shadow-execution-settlement.schema.json",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_config() -> dict[str, Any]:
    return load_json(CONFIG)


def load_scenarios() -> dict[str, Any]:
    return load_json(SCENARIOS)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_upstream_yex0() -> None:
    yex0 = load_json(YEX0)
    require(yex0["program_id"] == "YEX0", "YEX0 upstream missing")
    require(yex0["live_execution_authorized"] is False, "YEX0 live boundary drift")
    require(yex0["real_capital_movement_authorized"] is False, "YEX0 capital boundary drift")
    require(yex0["firewall"]["unknown_semantics"] == "DENY", "YEX0 UNKNOWN law drift")


def validate_authority_ceiling(config: dict[str, Any]) -> None:
    require(config["program_id"] == "YVN1-A0", "wrong program id")
    require(config["upstream_authority"] == "YEX0_ACCEPTED_MERGED", "wrong upstream authority")
    require(config["entry_object"] == "ActionContract", "entry object drift")
    require(config["provider_policy"] == "provider_independent_first", "provider policy drift")
    for key, value in config["authority_ceiling"].items():
        require(value is False, f"A0 authority escalated: {key}")


def validate_deployment_freeze(config: dict[str, Any]) -> None:
    d = config["deployment_freeze"]
    expected = {
        "python": "3.12",
        "environment": "uv",
        "process_model": "single_process",
        "host_model": "single_host",
        "ledger": "sqlite_wal",
        "provider": "synthetic_shadow_provider",
        "public_rpc_required": False,
        "broker_network_dependency": False,
        "kubernetes": False,
        "kafka": False,
        "service_mesh": False,
        "multi_region": False,
        "distributed_microservices": False,
        "production_cloud_failover": False,
    }
    for key, value in expected.items():
        require(d[key] == value, f"deployment drift: {key}")
    require(
        d["filesystem"] == ["config", "ledger", "artifacts", "logs", "projections", "quarantine"],
        "runtime filesystem drift",
    )


def validate_state_and_reconciliation_laws(config: dict[str, Any]) -> None:
    require(
        config["execution_state_normal_path"]
        == ["RECEIVED", "AUTHORITY_CHECKING", "AUTHORIZED", "PLANNED", "SUBMITTING", "WORKING", "PARTIALLY_FILLED", "FILLED", "RECONCILING", "SETTLED"],
        "normal state path drift",
    )
    require(
        config["blocking_terminal_states"]
        == ["DENIED", "EXPIRED", "REJECTED", "CANCELLED", "DRIFTED", "FAIL_CLOSED"],
        "terminal state drift",
    )
    require(
        config["four_way_reconciliation"]
        == ["capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"],
        "four-way reconciliation drift",
    )
    require(config["shadow_external_state_independent"] is True, "shadow external states aliased")
    truth = config["truth_model"]
    require(truth["events_are_truth"] is True, "events not truth")
    require(truth["status_projection_only"] is True, "status promoted to truth")
    require(truth["hash_chain_required"] is True, "hash chain not required")
    require(truth["logs_authoritative"] is False, "logs promoted to truth")
    require(truth["projections_authoritative"] is False, "projection promoted to truth")
    require(
        config["atomicity_order"]
        == ["idempotency_reserved_durably", "pre_submit_event_persisted", "provider_side_effect_attempted", "provider_ack_event_persisted"],
        "atomicity order drift",
    )


def validate_golden_scenarios(registry: dict[str, Any]) -> None:
    require(registry["program_id"] == "YVN1-A1", "wrong scenario program id")
    require(registry["registry_status"] == "preregistered_by_yvn1_a0", "scenario registry not preregistered")
    scenarios = registry["scenarios"]
    require([s["scenario_id"] for s in scenarios] == [f"S{i:02d}" for i in range(1, 11)], "scenario identity drift")
    s07 = scenarios[6]
    require(s07["priority"] == "P0", "S07 must remain P0")
    require("duplicate_order_submission_equals_0" in s07["required_invariants"], "S07 duplicate invariant missing")
    require("replay_deterministic" in s07["required_invariants"], "S07 replay invariant missing")
    require("unknown_equals_deny" in s07["required_invariants"], "S07 unknown-deny invariant missing")
    for sid in ("S09", "S10"):
        scenario = next(s for s in scenarios if s["scenario_id"] == sid)
        require(scenario["required_terminal_behavior"] == "DRIFTED_FAIL_CLOSED", f"{sid} fail-closed drift")
        require("no_further_side_effect" in scenario["required_invariants"], f"{sid} side-effect freeze missing")


def validate_a1_victory_law(config: dict[str, Any], registry: dict[str, Any]) -> None:
    law = config["a1_victory_law"]
    require(law["golden_scenarios_required"] == len(registry["scenarios"]) == 10, "scenario count law drift")
    require(law["duplicate_order_submission_max"] == 0, "duplicate side-effect law drift")
    require(law["replay_determinism_required"] is True, "replay determinism not required")
    require(law["non_drift_scenarios_require_zero_unexplained_deltas"] is True, "reconciliation law weakened")
    require(law["s09_s10_must_fail_closed"] is True, "drift scenarios not fail-closed")
    for key in ("broker_credentials_absent", "broker_connection_false", "broker_paper_false", "live_execution_false", "real_capital_movement_false"):
        require(law[key] is True, f"A1 authority victory law weakened: {key}")
    require(law["pass_status"] == "YVN1_A1_SHADOW_RUNTIME_REALITY_PASS", "A1 PASS status drift")
    require(law["no_go_status"] == "YVN1_A1_SHADOW_RUNTIME_REALITY_NO_GO", "A1 NO-GO status drift")


def validate_schema_contracts() -> None:
    for path in SCHEMA_PATHS:
        require(path.exists(), f"schema missing: {path.name}")
        Draft202012Validator.check_schema(load_json(path))

    plan = load_json(VNEXT / "execution-plan.schema.json")
    require(plan["properties"]["provider_kind"]["const"] == "synthetic_shadow", "A0 provider drift")
    require(plan["properties"]["execution_mode"]["const"] == "shadow", "A0 mode drift")
    require(plan["properties"]["live_execution_authorized"]["const"] is False, "live authority introduced")
    require(plan["properties"]["real_capital_movement_authorized"]["const"] is False, "capital authority introduced")

    provider = load_json(VNEXT / "provider-state.schema.json")
    require(
        set(provider["properties"]["state_source"]["enum"])
        == {"shadow_oms", "synthetic_broker_custodian"},
        "provider-state source identity drift",
    )

    settlement = load_json(VNEXT / "shadow-execution-settlement.schema.json")
    required = set(settlement["properties"]["four_way_reconciliation"]["required"])
    require(
        required == {"capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"},
        "settlement reconciliation drift",
    )
    nonauth = settlement["properties"]["non_authorizations"]["properties"]
    for key in ("broker_credentials", "broker_connection", "broker_paper", "live_execution", "real_capital_movement"):
        require(nonauth[key]["const"] is False, f"settlement authority escalated: {key}")


def validate_a0() -> None:
    validate_upstream_yex0()
    config = load_config()
    registry = load_scenarios()
    validate_authority_ceiling(config)
    validate_deployment_freeze(config)
    validate_state_and_reconciliation_laws(config)
    validate_golden_scenarios(registry)
    validate_a1_victory_law(config, registry)
    validate_schema_contracts()
    require(config["a0_machine_status"] == "YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED", "A0 machine status drift")
    require(config["next_human_token"] == "ACCEPT_YVN1_A0_DEPLOYMENT_FREEZE", "G2 token drift")
    require(config["merge_token"] == "AUTHORIZE_YVN1_A0_MERGE", "G3 token drift")
    print("YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED")


if __name__ == "__main__":
    validate_a0()
