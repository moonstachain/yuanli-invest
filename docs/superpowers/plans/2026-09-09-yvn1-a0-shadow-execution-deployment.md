# YVN1-A0 Shadow Execution Constitution & Deployment Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the approved YVN1-A0 written design into machine-checkable Shadow Execution constitution, deployment freeze, provider-boundary contracts, Golden Scenario registry, A1 victory law, and Human Review artifacts without creating or running any execution runtime.

**Architecture:** Extend the accepted YEX0 control plane with provider-neutral A0 contracts only. YVN1-A0 freezes `ActionContract -> Firewall -> Orchestrator -> Provider Interface -> Synthetic Reality -> Event Ledger -> Four-Way Reconciliation -> Settlement` as a future A1 runtime design, but A0 itself remains non-runtime and non-provider. The implementation must prove that the deployment topology, authority ceiling, failure semantics, and A1 pre-registered victory law are internally consistent and fail closed.

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

- [ ] **Step 1: Write the failing test module** with imports that intentionally fail until the validator and artifacts exist.

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
            "veighna_invocation_authorized",
            "broker_credentials_authorized",
            "broker_connection_authorized",
            "broker_paper_authorized",
            "live_execution_authorized",
            "real_capital_movement_authorized",
            "a1_runtime_authorized",
        ):
            self.assertFalse(config["authority_ceiling"][key], key)

    def test_golden_scenarios_are_exact_and_s07_is_p0(self):
        registry = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        self.assertEqual([s["scenario_id"] for s in registry["scenarios"]], [f"S{i:02d}" for i in range(1, 11)])
        s07 = next(s for s in registry["scenarios"] if s["scenario_id"] == "S07")
        self.assertEqual(s07["priority"], "P0")

    def test_validator_accepts_canonical_a0_bundle(self):
        yvn1.validate_a0()
```

- [ ] **Step 2: Commit only the RED test.**

```bash
git add tests/test_yvn1_a0_shadow_execution.py
git commit -m "test: define YVN1-A0 shadow deployment contract"
```

- [ ] **Step 3: Open a Draft PR from the implementation branch and run `repository-gates`.**

Expected: `contracts` FAIL in unittest discovery because `scripts.validate_yvn1_a0_shadow_execution` and YVN1-A0 artifacts do not yet exist; `governance` should remain PASS.

---

### Task 2: Machine-readable A0 constitution and A1 pre-registration

**Files:**
- Create: `config/yvn1/yvn1_a0_shadow_execution.v0.1.json`
- Create: `fixtures/yvn1/yvn1_a0_golden_scenarios.v0.1.json`

**Interfaces:**
- Produces: machine-readable authority ceiling, deployment topology, state machine, provider boundary, Golden Scenario registry, and A1 victory law consumed by Tasks 3-5.

- [ ] **Step 1: Create `yvn1_a0_shadow_execution.v0.1.json`** with these exact machine invariants:

```json
{
  "schema_version": "0.1.0",
  "program_id": "YVN1-A0",
  "status": "implementation_candidate",
  "upstream_authority": "YEX0_ACCEPTED_MERGED",
  "entry_object": "ActionContract",
  "provider_policy": "provider_independent_first",
  "future_runtime_identity": "yuanli-execution",
  "execution_state_normal_path": ["RECEIVED","AUTHORITY_CHECKING","AUTHORIZED","PLANNED","SUBMITTING","WORKING","PARTIALLY_FILLED","FILLED","RECONCILING","SETTLED"],
  "blocking_terminal_states": ["DENIED","EXPIRED","REJECTED","CANCELLED","DRIFTED","FAIL_CLOSED"],
  "four_way_reconciliation": ["capital_intent","yuanli_execution","execution_engine_oms","broker_custodian"],
  "shadow_external_state_independent": true,
  "truth_model": {"events_are_truth": true, "status_projection_only": true, "hash_chain_required": true},
  "atomicity_order": ["idempotency_reserved_durably","pre_submit_event_persisted","provider_side_effect_attempted","provider_ack_event_persisted"],
  "deployment_freeze": {
    "python": "3.12",
    "environment": "uv",
    "process_model": "single_process",
    "host_model": "single_host",
    "ledger": "sqlite_wal",
    "filesystem": ["config","ledger","artifacts","logs","projections","quarantine"],
    "provider": "synthetic_shadow_provider",
    "broker_network_dependency": false
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

- [ ] **Step 2: Create `yvn1_a0_golden_scenarios.v0.1.json`** with exactly S01-S10 and no extra scenario IDs. Required terminal semantics must match the written spec: S01 settled, S02 partial-then-settle, S03 rejected, S04 one submission, S05 expired/no submission, S06 ambiguity/no blind resubmit, S07 crash-recovery/no duplicate, S08 late-fill reconcile-or-fail-closed, S09 drift/fail-closed, S10 drift/fail-closed.

- [ ] **Step 3: Run only the new tests.**

```bash
python -m unittest tests.test_yvn1_a0_shadow_execution -v
```

Expected: still FAIL because schemas and validator are not yet implemented.

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

- [ ] **Step 1: Define `ExecutionPlan`** as provider-neutral and non-self-authorizing. Required fields: `execution_plan_id`, `schema_version`, `action_contract_id`, `execution_intent_id`, `created_at`, `idempotency_key`, `provider_kind`, `execution_mode`, `scope`, `live_execution_authorized`, `real_capital_movement_authorized`. Freeze `provider_kind` to `synthetic_shadow` in A0 fixtures, `execution_mode` to `shadow`, and both authority booleans to `const:false`.

- [ ] **Step 2: Define `ProviderState`** with an explicit `state_source` enum of `shadow_oms` or `synthetic_broker_custodian`, plus `snapshot_id`, `stream_id`, `as_of`, `orders`, `trades`, `positions`, `cash`, `provider_health`. The schema must not allow a single object to claim both source identities.

- [ ] **Step 3: Define `ShadowExecutionSettlement`** requiring separate embedded or referenced states for `capital_intent`, `yuanli_execution`, `shadow_oms`, `synthetic_broker_custodian`, plus `ledger_root_hash`, `final_projected_state`, `four_way_reconciliation`, `failure_classification`, `replay_determinism_result`, `settlement_status`, and `non_authorizations`. Allowed episode settlements are only `SHADOW_EXECUTION_SETTLED` and `SHADOW_EXECUTION_FAIL_CLOSED`.

- [ ] **Step 4: Add focused schema assertions to the test file.**

```python
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
```

- [ ] **Step 5: Run new tests.**

```bash
python -m unittest tests.test_yvn1_a0_shadow_execution -v
```

Expected: schema tests PASS; validator test still FAIL.

- [ ] **Step 6: Commit.**

```bash
git add packages/contracts/schemas/vnext tests/test_yvn1_a0_shadow_execution.py
git commit -m "feat: add YVN1-A0 provider-neutral contracts"
```

---

### Task 4: Fail-closed A0 validator

**Files:**
- Create: `scripts/validate_yvn1_a0_shadow_execution.py`
- Modify: `tests/test_yvn1_a0_shadow_execution.py`

**Interfaces:**
- Consumes: YVN1-A0 config, scenario registry, three new schemas, accepted YEX0 config/schemas.
- Produces: `validate_a0()` plus focused validators for authority, topology, scenarios, victory law, and non-authorizations.

- [ ] **Step 1: Implement validator entry points** with exact names:

```python
def validate_authority_ceiling(config: dict) -> None: ...
def validate_deployment_freeze(config: dict) -> None: ...
def validate_state_and_reconciliation_laws(config: dict) -> None: ...
def validate_golden_scenarios(registry: dict) -> None: ...
def validate_a1_victory_law(config: dict, registry: dict) -> None: ...
def validate_schema_contracts() -> None: ...
def validate_a0() -> None: ...
```

`validate_a0()` must print `YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED` only after every check succeeds.

- [ ] **Step 2: Fail closed on authority escalation.** Add tests that mutate `veighna_invocation_authorized`, `broker_paper_authorized`, or `a1_runtime_authorized` to `true` and assert `ValueError`.

```python
def test_authority_escalation_is_rejected(self):
    config = yvn1.load_config()
    for key in ("veighna_invocation_authorized", "broker_paper_authorized", "a1_runtime_authorized"):
        mutated = copy.deepcopy(config)
        mutated["authority_ceiling"][key] = True
        with self.assertRaises(ValueError):
            yvn1.validate_authority_ceiling(mutated)
```

- [ ] **Step 3: Fail closed on scenario drift.** Reject missing S07, extra S11, S07 not P0, or altered S09/S10 fail-closed semantics.

- [ ] **Step 4: Fail closed on topology drift.** Reject deployment values other than Python 3.12, uv, single process, single host, SQLite WAL, synthetic provider, no broker network dependency. Reject missing `quarantine` or a truth model in which logs/projections become authoritative.

- [ ] **Step 5: Fail closed on reconciliation self-comparison.** Require the config and schemas to preserve independent `shadow_oms` and `synthetic_broker_custodian` identities; reject any declared alias/equality flag.

- [ ] **Step 6: Run focused tests.**

```bash
python -m unittest tests.test_yvn1_a0_shadow_execution -v
```

Expected: PASS.

- [ ] **Step 7: Commit.**

```bash
git add scripts/validate_yvn1_a0_shadow_execution.py tests/test_yvn1_a0_shadow_execution.py
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
- Produces: human-reviewable A0 candidate with exact non-authorizations and G2/G3 gates.

- [ ] **Step 1: Write the Constitution** around these immutable laws: ActionContract-only entry; provider-independent first; UNKNOWN=DENY; no state truth outside Event Ledger; four independent reconciliation identities; no blind resubmit after ambiguous side effect; Failure is Knowledge; no downstream authority implied.

- [ ] **Step 2: Write Deployment Freeze** with the exact A1 target: Python 3.12, uv, single process, single host, SQLite WAL, `runtime/{config,ledger,artifacts,logs,projections,quarantine}`, Synthetic Shadow Provider, no public RPC, no broker network dependency. Explicitly reject Kubernetes, Kafka, service mesh, distributed microservices, multi-region, production HA, and real broker gateway for A1.

- [ ] **Step 3: Write the Human Review Card** with exactly these review decisions:

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
12. A1 may NO-GO without rescue-model substitution.
13. No VeighNa/broker/paper/live/real-capital authority exists in A0.
14. A0 acceptance does not imply merge or A1 authorization.
```

Candidate G2 token: `ACCEPT_YVN1_A0_DEPLOYMENT_FREEZE`. Candidate G3 token: `AUTHORIZE_YVN1_A0_MERGE`.

- [ ] **Step 4: Commit.**

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

- [ ] **Step 1: Wire the validator into CI** immediately after YEX0 validation and before YIM0/full unittest discovery.

```yaml
      - run: python scripts/validate_yex0_capital_execution_constitution.py
      - run: python scripts/validate_yvn1_a0_shadow_execution.py
      - run: python scripts/validate_yim0_methodology_projection.py
```

- [ ] **Step 2: Run Draft PR CI.**

Expected exact-head results:

```text
YVN1-A0 validator PASS
YVN1-A0 unittest PASS
repository contracts PASS
repository governance PASS
```

- [ ] **Step 3: Perform adversarial scope audit on changed files.** The PR must contain none of the following implementation signatures:

```text
import vnpy
from vnpy
MainEngine(
send_order(
connect(
subscribe(
broker password/token/API key
real provider endpoint
runtime process launcher
SQLite database creation
execution worker
```

Note: documentation may mention these strings as explicit non-authorizations; the audit must distinguish prose from executable imports/calls.

- [ ] **Step 4: Verify no new runtime repository or cloud resource was created.** A0 remains Canon/contract work only.

- [ ] **Step 5: Write the Machine Qualification Receipt** recording exact candidate head SHA, CI run id/number, `contracts`/`governance` conclusions, validator status, unit-test status, changed-file audit, and the settlement:

```text
YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED
```

The receipt must explicitly state:

```text
A1 runtime = NOT AUTHORIZED
VeighNa = NOT INSTALLED / NOT INVOKED
Broker credentials = NONE
Broker connection = NONE
Paper order = NONE
Live order = NONE
Real capital movement = NONE
Merge = NOT AUTHORIZED
```

- [ ] **Step 6: Re-run repository gates on the receipt head** so the latest PR head, not the pre-receipt head, is green.

- [ ] **Step 7: Leave the PR Draft/Open/Not Merged** and move to the G2 Human Review Gate only.

Expected current state:

```text
YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED
AWAITING_HUMAN_REVIEW
MERGE_NOT_AUTHORIZED
A1_NOT_AUTHORIZED
```

- [ ] **Step 8: Commit the receipt and PR metadata update.**

```bash
git add docs/architecture/yvn1/YVN1-A0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md .github/workflows/ci.yml
git commit -m "YVN1-A0: record machine qualification"
```

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
