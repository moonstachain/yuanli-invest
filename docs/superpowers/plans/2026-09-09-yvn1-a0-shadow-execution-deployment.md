# YVN1-A0 Shadow Execution Constitution & Deployment Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the approved YVN1-A0 written design into machine-checkable Shadow Execution constitution, deployment freeze, provider-boundary contracts, Golden Scenario registry, A1 victory law, and Human Review artifacts without creating or running any execution runtime.

**Architecture:** Extend the accepted YEX0 control plane with provider-neutral A0 contracts only. YVN1-A0 freezes `ActionContract -> Firewall -> Orchestrator -> Provider Interface -> Synthetic Reality -> Event Ledger -> Four-Way Reconciliation -> Settlement` as a future A1 runtime design, but A0 itself remains non-runtime and non-provider. The implementation must prove that deployment topology, authority ceiling, failure semantics, and A1 pre-registered victory law are internally consistent and fail closed.

**Tech Stack:** JSON Schema Draft 2020-12, Python 3.12, existing `jsonschema==4.25.1`, unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-09-yvn1-a0-shadow-execution-deployment-design.md`

## Global Constraints

- Upstream authority is `YEX0_ACCEPTED_MERGED`; YVN1-A0 may specialize but never weaken YEX0 laws.
- No VeighNa installation/import/invocation.
- No broker credentials, broker connection, market-data subscription, broker-paper order, live order, or real-capital movement.
- No portfolio weighting, position sizing, or automatic research-to-execution bridge.
- A0 must not create the future `yuanli-execution` repository or any runtime process.
- `UNKNOWN = DENY` remains mandatory.
- `Execution Events = truth`; status is projection only.
- Four-way reconciliation identities remain `capital_intent`, `yuanli_execution`, `execution_engine_oms`, `broker_custodian`.
- `Shadow OMS` and `Synthetic Broker/Custodian State` must be independently materialized identities in the A1 contract.
- A1 deployment target is frozen as Python 3.12 + uv + single process + single host + SQLite WAL + local sandbox + Synthetic Shadow Provider.
- A1 must pre-register exactly S01-S10 as the minimum Golden Scenario set; S07 is P0.
- A1 victory law is frozen before A1 implementation. A0 cannot alter results because no A1 runtime exists yet.
- A0 machine qualification does not authorize A1, A2, YVN2, YVN3, VeighNa, broker-paper, live, or merge.

---

### Task 1: RED contract for A0 scope and authority ceiling

**Files:**
- Create: `tests/test_yvn1_a0_shadow_execution.py`

**Interfaces:**
- Consumes: accepted YEX0 `action-contract.schema.json`, `execution-event.schema.json`, and YEX0 constitution.
- Produces: RED tests that define YVN1-A0 machine requirements before implementation.

- [ ] **Step 1: Create the failing test module exactly as below.**

```python
from pathlib import Path
import copy
import json
import unittest

from scripts import validate_yvn1_a0_shadow_execution as yvn1

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "packages/contracts/schemas/vnext"
CONFIG = ROOT / "config/yvn1/yvn1_a0_shadow_execution.v0.1.json"
SCENARIOS = ROOT / "fixtures/yvn1/yvn1_a0_golden_scenarios.v0.1.json"


class YVN1A0ContractTests(unittest.TestCase):
    def load_schema(self, name: str) -> dict:
        return json.loads((VNEXT / name).read_text(encoding="utf-8"))

    def test_three_new_schemas_exist(self):
        for name in (
            "execution-plan.schema.json",
            "provider-state.schema.json",
            "shadow-execution-settlement.schema.json",
        ):
            self.assertTrue((VNEXT / name).exists(), name)

    def test_a0_has_zero_runtime_or_broker_authority(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        for key in (
            "veighna_installation_authorized",
            "veighna_invocation_authorized",
            "broker_credentials_authorized",
            "broker_connection_authorized",
            "market_data_subscription_authorized",
            "broker_paper_authorized",
            "live_execution_authorized",
            "real_capital_movement_authorized",
            "a1_runtime_authorized",
        ):
            self.assertFalse(config["authority_ceiling"][key], key)

    def test_golden_scenarios_are_exact_and_s07_is_p0(self):
        registry = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        self.assertEqual(
            [s["scenario_id"] for s in registry["scenarios"]],
            [f"S{i:02d}" for i in range(1, 11)],
        )
        s07 = next(s for s in registry["scenarios"] if s["scenario_id"] == "S07")
        self.assertEqual(s07["priority"], "P0")

    def test_provider_state_sources_are_distinct(self):
        schema = self.load_schema("provider-state.schema.json")
        self.assertEqual(
            set(schema["properties"]["state_source"]["enum"]),
            {"shadow_oms", "synthetic_broker_custodian"},
        )

    def test_execution_plan_cannot_authorize_live(self):
        schema = self.load_schema("execution-plan.schema.json")
        self.assertIs(schema["properties"]["live_execution_authorized"]["const"], False)
        self.assertIs(schema["properties"]["real_capital_movement_authorized"]["const"], False)

    def test_validator_accepts_canonical_a0(self):
        yvn1.validate_a0()


class YVN1A0AdversarialTests(unittest.TestCase):
    def test_authority_escalation_is_rejected(self):
        config = yvn1.load_config()
        for key in (
            "veighna_invocation_authorized",
            "broker_paper_authorized",
            "a1_runtime_authorized",
        ):
            mutated = copy.deepcopy(config)
            mutated["authority_ceiling"][key] = True
            with self.assertRaises(ValueError):
                yvn1.validate_authority_ceiling(mutated)

    def test_s07_cannot_lose_p0_status(self):
        registry = yvn1.load_scenarios()
        mutated = copy.deepcopy(registry)
        next(s for s in mutated["scenarios"] if s["scenario_id"] == "S07")["priority"] = "P1"
        with self.assertRaises(ValueError):
            yvn1.validate_golden_scenarios(mutated)

    def test_s11_cannot_be_silently_added(self):
        registry = yvn1.load_scenarios()
        mutated = copy.deepcopy(registry)
        mutated["scenarios"].append({
            "scenario_id": "S11",
            "priority": "P1",
            "name": "Silent rescue scenario",
            "required_terminal_behavior": "SETTLED",
            "required_invariants": [],
        })
        with self.assertRaises(ValueError):
            yvn1.validate_golden_scenarios(mutated)

    def test_broker_network_dependency_is_rejected(self):
        config = yvn1.load_config()
        mutated = copy.deepcopy(config)
        mutated["deployment_freeze"]["broker_network_dependency"] = True
        with self.assertRaises(ValueError):
            yvn1.validate_deployment_freeze(mutated)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Commit only the RED test.**

```bash
git add tests/test_yvn1_a0_shadow_execution.py
git commit -m "test: define YVN1-A0 shadow deployment contract"
```

- [ ] **Step 3: Open a Draft PR and run `repository-gates`.**

Expected: `contracts` FAIL in unittest discovery because `scripts.validate_yvn1_a0_shadow_execution` and YVN1-A0 artifacts do not yet exist; `governance` remains PASS.

---

### Task 2: Machine-readable A0 constitution and A1 pre-registration

**Files:**
- Create: `config/yvn1/yvn1_a0_shadow_execution.v0.1.json`
- Create: `fixtures/yvn1/yvn1_a0_golden_scenarios.v0.1.json`

**Interfaces:**
- Produces: machine-readable authority ceiling, deployment topology, state machine, Golden Scenario registry, and A1 victory law consumed by later tasks.

- [ ] **Step 1: Create `config/yvn1/yvn1_a0_shadow_execution.v0.1.json` exactly as below.**

```json
{
  "schema_version": "0.1.0",
  "program_id": "YVN1-A0",
  "status": "implementation_candidate",
  "upstream_authority": "YEX0_ACCEPTED_MERGED",
  "entry_object": "ActionContract",
  "provider_policy": "provider_independent_first",
  "future_runtime_identity": "yuanli-execution",
  "execution_state_normal_path": ["RECEIVED", "AUTHORITY_CHECKING", "AUTHORIZED", "PLANNED", "SUBMITTING", "WORKING", "PARTIALLY_FILLED", "FILLED", "RECONCILING", "SETTLED"],
  "blocking_terminal_states": ["DENIED", "EXPIRED", "REJECTED", "CANCELLED", "DRIFTED", "FAIL_CLOSED"],
  "four_way_reconciliation": ["capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"],
  "shadow_external_state_independent": true,
  "truth_model": {
    "events_are_truth": true,
    "status_projection_only": true,
    "hash_chain_required": true,
    "logs_authoritative": false,
    "projections_authoritative": false
  },
  "atomicity_order": ["idempotency_reserved_durably", "pre_submit_event_persisted", "provider_side_effect_attempted", "provider_ack_event_persisted"],
  "deployment_freeze": {
    "python": "3.12",
    "environment": "uv",
    "process_model": "single_process",
    "host_model": "single_host",
    "ledger": "sqlite_wal",
    "filesystem": ["config", "ledger", "artifacts", "logs", "projections", "quarantine"],
    "provider": "synthetic_shadow_provider",
    "public_rpc_required": false,
    "broker_network_dependency": false,
    "kubernetes": false,
    "kafka": false,
    "service_mesh": false,
    "multi_region": false,
    "distributed_microservices": false,
    "production_cloud_failover": false
  },
  "authority_ceiling": {
    "veighna_installation_authorized": false,
    "veighna_invocation_authorized": false,
    "broker_credentials_authorized": false,
    "broker_connection_authorized": false,
    "market_data_subscription_authorized": false,
    "broker_paper_authorized": false,
    "live_execution_authorized": false,
    "real_capital_movement_authorized": false,
    "portfolio_weight_authorized": false,
    "position_sizing_authorized": false,
    "automatic_research_to_execution_authorized": false,
    "a1_runtime_authorized": false,
    "a2_authorized": false,
    "yvn2_authorized": false,
    "yvn3_authorized": false,
    "merge_authorized": false
  },
  "a1_victory_law": {
    "golden_scenarios_required": 10,
    "duplicate_order_submission_max": 0,
    "replay_determinism_required": true,
    "non_drift_scenarios_require_zero_unexplained_deltas": true,
    "s09_s10_must_fail_closed": true,
    "broker_credentials_absent": true,
    "broker_connection_false": true,
    "broker_paper_false": true,
    "live_execution_false": true,
    "real_capital_movement_false": true,
    "pass_status": "YVN1_A1_SHADOW_RUNTIME_REALITY_PASS",
    "no_go_status": "YVN1_A1_SHADOW_RUNTIME_REALITY_NO_GO"
  },
  "a0_machine_status": "YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED",
  "next_human_token": "ACCEPT_YVN1_A0_DEPLOYMENT_FREEZE",
  "merge_token": "AUTHORIZE_YVN1_A0_MERGE"
}
```

- [ ] **Step 2: Create `fixtures/yvn1/yvn1_a0_golden_scenarios.v0.1.json` exactly as below.**

```json
{
  "schema_version": "0.1.0",
  "program_id": "YVN1-A1",
  "registry_status": "preregistered_by_yvn1_a0",
  "scenarios": [
    {"scenario_id": "S01", "priority": "P1", "name": "happy_path_full_fill", "required_terminal_behavior": "SHADOW_EXECUTION_SETTLED", "required_invariants": ["one_provider_submission", "four_way_match", "replay_deterministic"]},
    {"scenario_id": "S02", "priority": "P1", "name": "partial_fill_then_full_fill", "required_terminal_behavior": "SHADOW_EXECUTION_SETTLED_AFTER_FINAL_RECONCILIATION", "required_invariants": ["partial_state_observed", "final_four_way_match", "replay_deterministic"]},
    {"scenario_id": "S03", "priority": "P1", "name": "provider_order_reject", "required_terminal_behavior": "REJECTED", "required_invariants": ["no_unexplained_state", "no_duplicate_submission"]},
    {"scenario_id": "S04", "priority": "P1", "name": "duplicate_action_contract_delivery", "required_terminal_behavior": "SHADOW_EXECUTION_SETTLED", "required_invariants": ["duplicate_order_submission_equals_0", "one_provider_submission"]},
    {"scenario_id": "S05", "priority": "P1", "name": "contract_expired_before_execution", "required_terminal_behavior": "EXPIRED", "required_invariants": ["provider_submission_equals_0"]},
    {"scenario_id": "S06", "priority": "P1", "name": "provider_timeout_before_clear_ack", "required_terminal_behavior": "AMBIGUITY_FAIL_CLOSED_OR_RECONCILED", "required_invariants": ["no_blind_resubmit", "duplicate_order_submission_equals_0"]},
    {"scenario_id": "S07", "priority": "P0", "name": "crash_after_submit_before_ack_persistence", "required_terminal_behavior": "RECOVERED_WITHOUT_DUPLICATE_OR_FAIL_CLOSED", "required_invariants": ["duplicate_order_submission_equals_0", "replay_deterministic", "unknown_equals_deny"]},
    {"scenario_id": "S08", "priority": "P1", "name": "late_fill_after_reconnect", "required_terminal_behavior": "SHADOW_EXECUTION_SETTLED_OR_FAIL_CLOSED", "required_invariants": ["late_reality_recorded", "reconciled_or_explicit_fail_closed"]},
    {"scenario_id": "S09", "priority": "P1", "name": "unknown_external_order", "required_terminal_behavior": "DRIFTED_FAIL_CLOSED", "required_invariants": ["unknown_external_order_detected", "no_further_side_effect"]},
    {"scenario_id": "S10", "priority": "P1", "name": "position_or_cash_drift", "required_terminal_behavior": "DRIFTED_FAIL_CLOSED", "required_invariants": ["position_or_cash_drift_detected", "no_further_side_effect"]}
  ]
}
```

- [ ] **Step 3: Run the focused tests.**

```bash
python -m unittest tests.test_yvn1_a0_shadow_execution -v
```

Expected: still FAIL because schemas and validator do not yet exist.

- [ ] **Step 4: Commit.**

```bash
git add config/yvn1 fixtures/yvn1
git commit -m "feat: freeze YVN1-A0 authority and A1 victory law"
```

---

### Task 3: Provider-neutral schemas for future A1 runtime

**Files:**
- Create: `packages/contracts/schemas/vnext/execution-plan.schema.json`
- Create: `packages/contracts/schemas/vnext/provider-state.schema.json`
- Create: `packages/contracts/schemas/vnext/shadow-execution-settlement.schema.json`

**Interfaces:**
- Consumes: YEX0 ActionContract identity and YVN1-A0 config.
- Produces: A0-only schema contracts; no runtime classes or provider imports.

- [ ] **Step 1: Create `execution-plan.schema.json` exactly as below.**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:yuanli-invest:schema:yvn1-execution-plan:0.1.0",
  "title": "ExecutionPlan",
  "type": "object",
  "additionalProperties": false,
  "required": ["execution_plan_id", "schema_version", "action_contract_id", "execution_intent_id", "created_at", "idempotency_key", "provider_kind", "execution_mode", "scope", "live_execution_authorized", "real_capital_movement_authorized"],
  "properties": {
    "execution_plan_id": {"type": "string", "pattern": "^EP-[A-Z0-9-]+$"},
    "schema_version": {"const": "0.1.0"},
    "action_contract_id": {"type": "string", "pattern": "^AC-[A-Z0-9-]+$"},
    "execution_intent_id": {"type": "string", "pattern": "^EI-[A-Z0-9-]+$"},
    "created_at": {"type": "string", "format": "date-time"},
    "idempotency_key": {"type": "string", "minLength": 8},
    "provider_kind": {"const": "synthetic_shadow"},
    "execution_mode": {"const": "shadow"},
    "scope": {
      "type": "object",
      "additionalProperties": false,
      "required": ["max_quantity_abs", "max_notional", "max_loss", "max_slippage_bps", "allowed_venues"],
      "properties": {
        "max_quantity_abs": {"type": "number", "minimum": 0},
        "max_notional": {"type": "number", "minimum": 0},
        "max_loss": {"type": "number", "minimum": 0},
        "max_slippage_bps": {"type": "number", "minimum": 0},
        "allowed_venues": {"type": "array", "minItems": 1, "uniqueItems": true, "items": {"type": "string", "minLength": 1}}
      }
    },
    "live_execution_authorized": {"const": false},
    "real_capital_movement_authorized": {"const": false}
  }
}
```

- [ ] **Step 2: Create `provider-state.schema.json` exactly as below.**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:yuanli-invest:schema:yvn1-provider-state:0.1.0",
  "title": "ProviderState",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "snapshot_id", "stream_id", "state_source", "as_of", "orders", "trades", "positions", "cash", "provider_health"],
  "properties": {
    "schema_version": {"const": "0.1.0"},
    "snapshot_id": {"type": "string", "pattern": "^PS-[A-Z0-9-]+$"},
    "stream_id": {"type": "string", "minLength": 1},
    "state_source": {"enum": ["shadow_oms", "synthetic_broker_custodian"]},
    "as_of": {"type": "string", "format": "date-time"},
    "orders": {"type": "array", "items": {"type": "object"}},
    "trades": {"type": "array", "items": {"type": "object"}},
    "positions": {"type": "array", "items": {"type": "object"}},
    "cash": {"type": "number"},
    "provider_health": {"enum": ["HEALTHY", "DEGRADED", "UNKNOWN"]}
  }
}
```

- [ ] **Step 3: Create `shadow-execution-settlement.schema.json` exactly as below.**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:yuanli-invest:schema:yvn1-shadow-execution-settlement:0.1.0",
  "title": "ShadowExecutionSettlement",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "settlement_id", "action_contract_id", "execution_plan_id", "ledger_root_hash", "final_projected_state", "capital_intent_state", "yuanli_execution_state", "shadow_oms_state", "synthetic_broker_state", "four_way_reconciliation", "failure_classification", "replay_determinism_result", "settlement_status", "non_authorizations"],
  "properties": {
    "schema_version": {"const": "0.1.0"},
    "settlement_id": {"type": "string", "pattern": "^SES-[A-Z0-9-]+$"},
    "action_contract_id": {"type": "string", "pattern": "^AC-[A-Z0-9-]+$"},
    "execution_plan_id": {"type": "string", "pattern": "^EP-[A-Z0-9-]+$"},
    "ledger_root_hash": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
    "final_projected_state": {"enum": ["SETTLED", "REJECTED", "EXPIRED", "DRIFTED", "FAIL_CLOSED"]},
    "capital_intent_state": {"type": "object"},
    "yuanli_execution_state": {"type": "object"},
    "shadow_oms_state": {"type": "object"},
    "synthetic_broker_state": {"type": "object"},
    "four_way_reconciliation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"],
      "properties": {
        "capital_intent": {"type": "string", "enum": ["MATCHED", "SIMULATED_MATCH", "DRIFTED"]},
        "yuanli_execution": {"type": "string", "enum": ["MATCHED", "SIMULATED_MATCH", "DRIFTED"]},
        "execution_engine_oms": {"type": "string", "enum": ["MATCHED", "SIMULATED_MATCH", "DRIFTED"]},
        "broker_custodian": {"type": "string", "enum": ["MATCHED", "SIMULATED_MATCH", "DRIFTED"]}
      }
    },
    "failure_classification": {"type": ["string", "null"]},
    "replay_determinism_result": {"enum": ["PASS", "FAIL", "NOT_RUN"]},
    "settlement_status": {"enum": ["SHADOW_EXECUTION_SETTLED", "SHADOW_EXECUTION_FAIL_CLOSED"]},
    "non_authorizations": {
      "type": "object",
      "additionalProperties": false,
      "required": ["broker_credentials", "broker_connection", "broker_paper", "live_execution", "real_capital_movement"],
      "properties": {
        "broker_credentials": {"const": false},
        "broker_connection": {"const": false},
        "broker_paper": {"const": false},
        "live_execution": {"const": false},
        "real_capital_movement": {"const": false}
      }
    }
  }
}
```

- [ ] **Step 4: Run the focused tests.**

```bash
python -m unittest tests.test_yvn1_a0_shadow_execution -v
```

Expected: schema-existence and schema-authority tests PASS; validator test still FAIL.

- [ ] **Step 5: Commit.**

```bash
git add packages/contracts/schemas/vnext
git commit -m "feat: add YVN1-A0 provider-neutral contracts"
```

---

### Task 4: Fail-closed A0 validator

**Files:**
- Create: `scripts/validate_yvn1_a0_shadow_execution.py`

**Interfaces:**
- Consumes: YVN1-A0 config, scenario registry, three new schemas, accepted YEX0 config.
- Produces: `validate_a0()` plus focused validators used directly by tests.

- [ ] **Step 1: Create the validator exactly as below.**

```python
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
        config["execution_state_normal_path"] == ["RECEIVED", "AUTHORITY_CHECKING", "AUTHORIZED", "PLANNED", "SUBMITTING", "WORKING", "PARTIALLY_FILLED", "FILLED", "RECONCILING", "SETTLED"],
        "normal state path drift",
    )
    require(
        config["blocking_terminal_states"] == ["DENIED", "EXPIRED", "REJECTED", "CANCELLED", "DRIFTED", "FAIL_CLOSED"],
        "terminal state drift",
    )
    require(
        config["four_way_reconciliation"] == ["capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"],
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
        config["atomicity_order"] == ["idempotency_reserved_durably", "pre_submit_event_persisted", "provider_side_effect_attempted", "provider_ack_event_persisted"],
        "atomicity order drift",
    )


def validate_golden_scenarios(registry: dict[str, Any]) -> None:
    require(registry["registry_status"] == "preregistered_by_yvn1_a0", "scenario registry not preregistered")
    scenarios = registry["scenarios"]
    require([s["scenario_id"] for s in scenarios] == [f"S{i:02d}" for i in range(1, 11)], "scenario identity drift")
    s07 = scenarios[6]
    require(s07["priority"] == "P0", "S07 must remain P0")
    require("duplicate_order_submission_equals_0" in s07["required_invariants"], "S07 duplicate invariant missing")
    for sid in ("S09", "S10"):
        scenario = next(s for s in scenarios if s["scenario_id"] == sid)
        require(scenario["required_terminal_behavior"] == "DRIFTED_FAIL_CLOSED", f"{sid} fail-closed drift")


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
        set(provider["properties"]["state_source"]["enum"]) == {"shadow_oms", "synthetic_broker_custodian"},
        "provider-state source identity drift",
    )
    settlement = load_json(VNEXT / "shadow-execution-settlement.schema.json")
    required = set(settlement["properties"]["four_way_reconciliation"]["required"])
    require(required == {"capital_intent", "yuanli_execution", "execution_engine_oms", "broker_custodian"}, "settlement reconciliation drift")


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
```

- [ ] **Step 2: Run focused tests.**

```bash
python -m unittest tests.test_yvn1_a0_shadow_execution -v
```

Expected: PASS.

- [ ] **Step 3: Run the validator directly.**

```bash
python scripts/validate_yvn1_a0_shadow_execution.py
```

Expected output: `YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED`.

- [ ] **Step 4: Commit.**

```bash
git add scripts/validate_yvn1_a0_shadow_execution.py
git commit -m "feat: validate YVN1-A0 deployment freeze"
```

---

### Task 5: Human-readable constitution, deployment freeze, and review card

**Files:**
- Create: `docs/architecture/yvn1/YVN1-A0-SHADOW-EXECUTION-CONSTITUTION-v0.1.md`
- Create: `docs/architecture/yvn1/YVN1-A0-DEPLOYMENT-FREEZE-v0.1.md`
- Create: `docs/architecture/yvn1/YVN1-A0-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Consumes: approved design and machine config.
- Produces: human-reviewable A0 candidate with exact G2/G3 gates.

- [ ] **Step 1: Write `YVN1-A0-SHADOW-EXECUTION-CONSTITUTION-v0.1.md` with these sections and exact laws:** Mission; YEX0 upstream authority; ActionContract-only entry; six future A1 components; provider-independent-first law; state machine; Event Ledger truth; atomicity/idempotency; four-way reconciliation; Golden Failure; hard non-authorizations; next Human Gate. Include verbatim machine shorthand:

```text
NO EXECUTION WITHOUT AUTHORITY
NO SIDE EFFECT WITHOUT IDEMPOTENT IDENTITY
NO STATUS WITHOUT LEDGER
NO SETTLEMENT WITHOUT RECONCILIATION
NO AMBIGUITY WITHOUT FAIL-CLOSED
NO FAILURE WITHOUT LEARNING
```

- [ ] **Step 2: Write `YVN1-A0-DEPLOYMENT-FREEZE-v0.1.md` with the exact A1 target:** Python 3.12, uv, single process, single host, SQLite WAL, `runtime/{config,ledger,artifacts,logs,projections,quarantine}`, Synthetic Shadow Provider, no public RPC, no broker network dependency. Explicitly state that logs are non-authoritative and projections are disposable. Explicitly reject Kubernetes, Kafka, service mesh, distributed microservices, multi-region, production HA, and real broker gateway for A1.

- [ ] **Step 3: Write `YVN1-A0-HUMAN-REVIEW-CARD-v0.1.md` with exactly fourteen decisions:**

```text
1. YEX0 laws remain upstream and binding.
2. ActionContract is the only lawful execution entry object.
3. A1 is provider-independent; VeighNa is excluded from A1.
4. A1 future runtime is a separate execution-runtime boundary, not a research module.
5. Shadow OMS and Synthetic Broker/Custodian are independent state identities.
6. Event Ledger is truth; status is projection.
7. SQLite WAL is A1 edge truth; logs/projections are non-authoritative.
8. UNKNOWN = DENY during normal flow and recovery.
9. Idempotency reservation precedes provider side effect.
10. S01-S10 are frozen; S07 is P0.
11. A1 victory law is frozen before A1 implementation.
12. A1 may NO-GO without silent rescue or threshold relaxation.
13. No VeighNa/broker/paper/live/real-capital authority exists in A0.
14. A0 acceptance does not imply merge or A1 authorization.
```

Candidate G2 token: `ACCEPT_YVN1_A0_DEPLOYMENT_FREEZE`. Candidate G3 token: `AUTHORIZE_YVN1_A0_MERGE`.

- [ ] **Step 4: Run the focused tests and direct validator again to ensure documentation changes did not accompany contract drift.**

```bash
python -m unittest tests.test_yvn1_a0_shadow_execution -v
python scripts/validate_yvn1_a0_shadow_execution.py
```

Expected: both PASS.

- [ ] **Step 5: Commit.**

```bash
git add docs/architecture/yvn1
git commit -m "docs: freeze YVN1-A0 shadow deployment constitution"
```

---

### Task 6: CI integration, adversarial scope audit, and machine qualification

**Files:**
- Modify: `.github/workflows/ci.yml`
- Create after exact-head GREEN: `docs/architecture/yvn1/YVN1-A0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md`
- Modify: Draft PR body only.

**Interfaces:**
- Consumes: A0 validator, tests, exact PR diff, repository gates.
- Produces: machine-qualified A0 candidate; still no merge or A1 runtime authority.

- [ ] **Step 1: Insert the validator into `.github/workflows/ci.yml` exactly between YEX0 and YIM0 validation.**

```yaml
      - run: python scripts/validate_yex0_capital_execution_constitution.py
      - run: python scripts/validate_yvn1_a0_shadow_execution.py
      - run: python scripts/validate_yim0_methodology_projection.py
```

- [ ] **Step 2: Commit CI wiring.**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: gate YVN1-A0 deployment freeze"
```

- [ ] **Step 3: Run Draft PR CI.** Expected exact-head results:

```text
YVN1-A0 validator PASS
YVN1-A0 unittest PASS
repository contracts PASS
repository governance PASS
```

- [ ] **Step 4: Perform an adversarial changed-file audit.** No executable file may contain any of these provider/runtime signatures:

```text
import vnpy
from vnpy
MainEngine(
send_order(
connect(
subscribe(
```

Also verify no broker secret, endpoint, credential fixture, SQLite database file, process launcher, worker loop, or newly created `yuanli-execution` repository exists. Documentation may mention forbidden signatures only as non-authorization text.

- [ ] **Step 5: Create `YVN1-A0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md` only after exact-head CI is green.** Record exact candidate head SHA, CI run number/id, `contracts` and `governance` conclusions, validator result, unittest result, changed-file audit, and settlement:

```text
YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED
```

The receipt must state exactly:

```text
A1 runtime = NOT AUTHORIZED
A2 = NOT AUTHORIZED
VeighNa = NOT INSTALLED / NOT INVOKED
Broker credentials = NONE
Broker connection = NONE
Market-data subscription = NONE
Paper order = NONE
Live order = NONE
Real capital movement = NONE
Merge = NOT AUTHORIZED
```

- [ ] **Step 6: Commit the receipt.**

```bash
git add docs/architecture/yvn1/YVN1-A0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md
git commit -m "YVN1-A0: record machine qualification"
```

- [ ] **Step 7: Re-run repository gates on the receipt head** so the latest PR head, not the pre-receipt head, is green.

Expected state:

```text
YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED
AWAITING_HUMAN_REVIEW
MERGE_NOT_AUTHORIZED
A1_NOT_AUTHORIZED
```

- [ ] **Step 8: Update the Draft PR body** with reviewed head, latest CI run, settlement, G2 token `ACCEPT_YVN1_A0_DEPLOYMENT_FREEZE`, and explicit statement that merge/A1/A2/VeighNa/broker authority remains false. Keep PR Draft/Open/Not Merged.

---

## Execution boundary after this plan

This plan ends at a machine-qualified A0 candidate. It does **not** include Human Acceptance, merge, post-merge closure, A1 runtime creation, creation of `yuanli-execution`, installation of VeighNa, or any broker/paper/live interaction.

The only lawful next Human Gate after successful execution of this plan is:

```text
ACCEPT_YVN1_A0_DEPLOYMENT_FREEZE
```

A later separate merge token remains:

```text
AUTHORIZE_YVN1_A0_MERGE
```
