# YVN1-A0｜Shadow Execution Constitution & Deployment Freeze — Design

Date: 2026-09-09  
Status: `DESIGN_CANDIDATE / HUMAN_WRITTEN_SPEC_REVIEW_REQUIRED`  
Scope: `YVN1-A0 only`  
Upstream authority: `YEX0_ACCEPTED_MERGED`  
Base main at design start: `ea70b2f1a172e500a0cc8553567f486c93a250d1`

## 0. Purpose

YVN1-A0 freezes the architecture, authority boundary and deployment contract for Yuanli's first provider-independent Shadow Execution Runtime.

It does **not** install or invoke VeighNa, connect to any broker, subscribe to market data, submit paper orders, submit live orders, move real capital, size real positions, or create any broker credential.

The target proof for the next battle is narrower and more fundamental:

> Prove that one previously authorized `ActionContract` can traverse a deterministic, auditable, fail-closed shadow execution loop from intent to simulated reality, reconciliation and settlement under zero broker credential, zero real capital and zero live authority.

The governing chain is:

```text
YEX0 ActionContract
      ↓
Shadow Action Intake
      ↓
Authorization Firewall
      ↓
Execution Orchestrator
      ↓
Provider Interface
      ↓
Synthetic Shadow Provider
      ↓
Synthetic Execution Reality
      ↓
Append-only Event Ledger
      ↓
State Projection
      ↓
Four-way Reconciliation
      ↓
ShadowExecutionSettlement
```

The design objective is not to prove that VeighNa can send orders. The design objective is to prove that Yuanli owns the execution semantics, authority boundaries, ledger truth, failure behavior and reconciliation discipline independently of any execution provider.

---

## 1. Constitutional dependency on YEX0

YVN1-A0 is downstream of the accepted and merged YEX0 constitution.

The following YEX0 laws remain binding and cannot be weakened by YVN1:

```text
ResearchAuthority != CapitalAuthority != ExecutionAuthority
Research Pass != Capital Pass != Execution Pass
PositionPassport != ExecutionAuthority
Intent != Authorization
UNKNOWN = DENY
Receipt = Ledger; Status = Projection
Four-Way Reconciliation is mandatory
ResearchFailure != ExecutionFailure
Execution provider != sovereign authority
Failure is knowledge
No live authority is implied by a shadow proof
```

YVN1-A0 may specialize those laws for shadow execution. It may not rewrite them.

### 1.1 Authority ceiling

YVN1-A0 can authorize only design-level freezing of a future shadow runtime.

It cannot authorize:

```text
VeighNa installation or invocation
Broker credentials
Broker connection
Market-data subscription
Broker-paper order submission
Live order submission
Real-capital movement
Portfolio weighting
Position sizing
Automatic research-to-execution bridge
YVN2 or YVN3
```

### 1.2 Entry object

The only lawful execution entry object is a valid YEX0 `ActionContract`.

The runtime must not accept free-form commands such as:

```text
BUY NVDA
sell 100 shares
rebalance portfolio
execute thesis
```

ChatGPT, Web, Notion, a research model or a human terminal cannot directly call the execution provider. They may only participate upstream in producing or approving objects whose authority is defined by YEX0.

---

## 2. Chosen architecture

Three architecture options were considered.

### Option A — keep execution inside `yuanli-invest`

Rejected as the production direction because it would collapse Canon/Research and Execution Runtime back into one physical authority surface.

### Option B — route execution through a research quant workspace

Acceptable for experiments but rejected as the target architecture because `ResearchCompute == ExecutionRuntime` would become an unnecessary long-term coupling.

### Option C — separate execution runtime boundary

Accepted architecture:

```text
moonstachain/yuanli-invest
  Canon / Contracts / Authority / Human Gates
                ↓
        signed ActionContract
                ↓
future execution runtime boundary
  target identity: yuanli-execution
                ↓
        Provider Interface
                ↓
        ShadowProvider
                ↓
      Synthetic Reality
```

Later, only the provider adapter is replaceable:

```text
ShadowProvider
      ↓ replace
VeighNaProvider
      ↓
VeighNa MainEngine / RiskManager / Gateway
```

### 2.1 Repository law

`yuanli-invest` remains the Canon and Control Plane for YVN1-A0 design artifacts, contracts and acceptance receipts.

Future runtime implementation must live behind a separate execution-runtime boundary. Runtime code must not be silently embedded into research capability modules.

A separate execution repository is the preferred physical target, but creating that repository is **not authorized by YVN1-A0 design approval alone**. Repository creation belongs to the implementation plan and a later explicit action.

---

## 3. Minimal YVN1 shadow runtime

The future A1 runtime contains exactly six primary components.

### 3.1 Shadow Action Intake

Responsibility:

- ingest one YEX0 `ActionContract`;
- verify schema identity and immutable references;
- reserve the contract idempotency identity;
- produce no provider side effect until the firewall has returned `ALLOW`.

It does not infer investment intent and does not modify contract scope.

### 3.2 Authorization Firewall

Pure authority function:

```text
ALLOW | DENY | UNKNOWN
```

Constitutional rule:

```text
UNKNOWN = DENY
```

It must deny or fail closed on at least:

- missing authority references;
- invalid or unknown schema version;
- expired contract;
- scope expansion;
- identity mismatch;
- duplicate idempotency conflict;
- unsupported execution mode;
- live or real-capital flag;
- unknown runtime state;
- unknown reconciliation state.

The firewall is not a market model. It never predicts price or decides whether an investment is attractive.

### 3.3 Execution Orchestrator

Responsibility:

- transform a valid ActionContract into an `ExecutionPlan`;
- drive the execution lifecycle state machine;
- call only the abstract Provider Interface;
- persist execution facts before/after side-effect boundaries according to the atomicity contract;
- stop on `DRIFTED`, `DENIED`, `EXPIRED`, `REJECTED` or `FAIL_CLOSED`.

The orchestrator must not import or depend directly on VeighNa.

### 3.4 Provider Interface

Provider-neutral minimum interface:

```text
submit(plan_or_order) -> provider_ack
cancel(provider_order_ref) -> cancel_ack
query_orders() -> provider_order_state
query_trades() -> provider_trade_state
query_positions() -> provider_position_state
query_account() -> provider_account_state
health() -> provider_health_state
```

The exact language-level interface may evolve in the implementation plan, but the semantic contract is frozen here.

Every provider implementation must be replaceable without changing YEX0 authority contracts, Event Ledger semantics or reconciliation law.

### 3.5 Synthetic Shadow Provider

YVN1-A1 begins with a provider-independent synthetic implementation.

It must not be a trivial `submit -> filled` mock. It must simulate execution-reality events sufficient to exercise lifecycle, replay, idempotency and reconciliation semantics.

Supported event behaviors must include:

```text
Submitted
Accepted
PartialFilled
Filled
Cancelled
Rejected
Delayed
ProviderTimeout
Disconnected
Recovered
LateFill
DuplicateDelivery
UnknownExternalOrder injection
PositionDrift injection
CashDrift injection
```

The Synthetic Provider is not a market simulator. It does not need order-book reconstruction, alpha, price discovery, detailed market-impact curves or realistic P&L modeling in A1.

### 3.6 Reconciliation + Settlement

Responsibility:

- reconcile four independently materialized state identities;
- classify unexplained differences;
- fail closed on unresolved drift;
- produce one `ShadowExecutionSettlement`;
- preserve Research Settlement as a separate upstream causal channel.

---

## 4. Four-way reconciliation in Shadow

YEX0 freezes four reconciliation identities. YVN1-A1 must preserve all four even without a real broker.

```text
1. Capital Intent Ledger
   What Yuanli was authorized to change.

2. Yuanli Execution Ledger
   What the Yuanli execution runtime believes it attempted and observed.

3. Shadow OMS
   What the execution engine believes happened.

4. Synthetic Broker/Custodian State
   What the simulated external account boundary physically contains.
```

### 4.1 Independence invariant

`Shadow OMS` and `Synthetic Broker/Custodian State` must be independently materialized state sources.

They may be generated by one process for A1, but they cannot be the same object, table, in-memory dictionary or direct alias.

Otherwise Four-Way Reconciliation degenerates into self-comparison and is not admissible evidence.

### 4.2 Drift law

Any unexplained divergence in order, fill, position or cash identity causes:

```text
DRIFTED
  ↓
FAIL_CLOSED
```

No further execution side effect may occur until the episode is explicitly resolved or terminated by the test scenario.

---

## 5. Execution state machine

The normal path is frozen as:

```text
RECEIVED
  ↓
AUTHORITY_CHECKING
  ↓
AUTHORIZED
  ↓
PLANNED
  ↓
SUBMITTING
  ↓
WORKING
  ↓
PARTIALLY_FILLED
  ↓
FILLED
  ↓
RECONCILING
  ↓
SETTLED
```

First-class terminal or blocking states:

```text
DENIED
EXPIRED
REJECTED
CANCELLED
DRIFTED
FAIL_CLOSED
```

### 5.1 State is projection

The state machine is a projection from the Event Ledger.

No mutable `status` field is accepted as execution truth.

Given the same admissible Event Ledger and projector version, state reconstruction must be deterministic.

---

## 6. Event Ledger constitution

### 6.1 Truth model

```text
Execution Events = truth
Execution Status = projection
```

The ledger is append-only and hash-chained.

Each event must contain at least:

```text
event_id
stream_id
sequence
event_type
occurred_at
recorded_at
previous_event_hash
event_hash
idempotency_key
action_contract_id
execution_intent_id
provider_ref when applicable
payload / evidence reference
```

### 6.2 Initial storage target

A1 deployment target:

```text
SQLite + WAL
```

Rationale:

- local durable truth during process/network failure;
- simple atomic transactions;
- deterministic replay;
- no external database dependency for execution truth;
- suitable for the initial single-process runtime.

Analytics and projections may use disposable DuckDB/Parquet outputs later, but they cannot become the operational truth source.

### 6.3 Future central audit sync

A future production architecture may asynchronously sync immutable receipts and audit projections to central Postgres/Supabase.

Central connectivity must not be required for the edge runtime to remember what it has done.

This future sync is outside YVN1-A0/A1 unless separately authorized.

---

## 7. Atomicity and idempotency law

The most dangerous class of execution failure is a side effect that occurred but was not durably remembered before restart.

The design therefore freezes the following semantic boundary:

```text
ActionContract received
      ↓
Idempotency identity reserved durably
      ↓
Pre-submit execution event persisted
      ↓
Provider side effect attempted
      ↓
Provider acknowledgement/event persisted
```

A restart must never reinterpret an already-reserved identical ActionContract as a new independent execution episode.

### 7.1 Duplicate invariant

For the same lawful contract identity and idempotency key:

```text
duplicate_order_submission = 0
```

A duplicate delivery may produce another observation event, but not a second independent provider submission.

### 7.2 Ambiguous side-effect invariant

If the runtime cannot determine whether the provider accepted an action before failure, the system must enter an ambiguity/reconciliation path rather than blindly resubmit.

`UNKNOWN = DENY` remains binding during restart recovery.

---

## 8. Deployment freeze

YVN1-A1 initial runtime environment is frozen to the simplest architecture capable of proving execution semantics.

```text
Python 3.12
uv-managed isolated environment
single process
single runtime host
SQLite WAL
local filesystem sandbox
Synthetic Shadow Provider
no broker network dependency
```

### 8.1 Explicitly rejected infrastructure for A1

Do not introduce:

```text
Kubernetes
Kafka
service mesh
multi-region deployment
distributed microservices
production cloud failover
real broker gateway
```

A1 tests execution law, not horizontal scale.

### 8.2 Runtime filesystem

The runtime must have isolated directories with explicit authority semantics:

```text
runtime/
  config/        immutable run configuration / contract references
  ledger/        append-only operational truth
  artifacts/     settlement and evidence artifacts
  logs/          operational logs; non-authoritative
  projections/   disposable/rebuildable state views
  quarantine/    unknown, malformed, conflicting or drifted inputs
```

`logs/` are not the ledger.

`projections/` may be deleted and rebuilt.

`quarantine/` is a first-class fail-closed destination.

---

## 9. Credential and network boundary

Four credential domains remain logically distinct:

```text
ResearchCredential
!= CapitalCredential
!= ExecutionCredential
!= BrokerCredential
```

YVN1-A1 allows only a local shadow execution capability sufficient to:

- read approved ActionContract fixtures;
- write local ledger events;
- invoke the Synthetic Provider;
- write local settlement artifacts.

A1 must not contain or request:

```text
broker username/password/token
exchange API key
live order permission
broker-paper permission
real market-data permission
real capital movement permission
```

No public RPC endpoint is required for A1.

---

## 10. Golden Scenario Registry

A1 must implement and execute at least the following ten pre-registered scenarios.

| ID | Scenario | Required settlement behavior |
|---|---|---|
| S01 | Happy path full fill | `SHADOW_EXECUTION_SETTLED` |
| S02 | Partial fill then full fill | settle only after final reconciliation |
| S03 | Provider order reject | `REJECTED` with no unexplained state |
| S04 | Duplicate ActionContract delivery | one provider submission only |
| S05 | Contract expires before execution | `EXPIRED` / no provider submission |
| S06 | Provider timeout before clear acknowledgement | ambiguity path; no blind duplicate resubmit |
| S07 | Crash after submit / before acknowledgement persistence | deterministic recovery without duplicate order |
| S08 | Late fill after reconnect | ledger absorbs late reality; final reconcile or fail closed |
| S09 | Unknown external order | `DRIFTED / FAIL_CLOSED` |
| S10 | Position or cash reconciliation drift | `DRIFTED / FAIL_CLOSED` |

### 10.1 P0 scenario

`S07` is P0 because it directly tests whether Event Ledger + Idempotency + Recovery form a real execution safety property rather than a happy-path abstraction.

### 10.2 Golden Failure law

Any material runtime incident discovered outside the original ten scenarios must receive an immutable Golden Failure identity and become a regression fixture.

Fixing the implementation does not delete the historical failure evidence.

---

## 11. YVN1-A1 pre-registered victory law

A0 freezes A1's success criteria before A1 implementation begins.

A1 may settle as `YVN1_A1_SHADOW_RUNTIME_REALITY_PASS` only if all conditions below hold.

### 11.1 Scenario law

```text
10 / 10 pre-registered Golden Scenarios
produce the pre-registered terminal behavior.
```

### 11.2 No duplicate side-effect law

```text
duplicate_order_submission = 0
```

including S04 and S07.

### 11.3 Reconciliation law

For all scenarios not explicitly injecting drift:

```text
unknown_external_orders = 0
unexplained_fills = 0
unexplained_position_delta = 0
unexplained_cash_delta = 0
```

For S09/S10, injected drift must be detected and must terminate in `DRIFTED / FAIL_CLOSED` rather than being silently normalized.

### 11.4 Replay determinism law

Replaying the same ledger with the same projector version must produce exactly the same authoritative projection:

```text
Projection(run_1) == Projection(run_2)
```

for all Golden Scenarios.

### 11.5 Authority law

A1 must prove by code, fixture and validator that:

```text
broker_credentials == absent
broker_connection == false
broker_paper == false
live_execution == false
real_capital_movement == false
```

### 11.6 Failure settlement

A1 is allowed to scientifically fail.

If any frozen victory condition fails, the lawful outcome is:

```text
YVN1_A1_SHADOW_RUNTIME_REALITY_NO_GO
```

not a relaxed threshold, renamed test or silent rescue implementation.

---

## 12. ShadowExecutionSettlement

The primary A1 result is not P&L.

Each execution episode must settle to a machine-readable artifact containing at least:

```text
action_contract_ref
execution_plan_ref
runtime_version / git_sha
ledger_stream_id
ledger_root_hash
final_projected_state
capital_intent_state
yuanli_execution_state
shadow_oms_state
synthetic_broker_state
four_way_reconciliation
failure_classification
execution_quality
replay_determinism_result
settlement_status
non_authorizations
```

Allowed episode-level settlements include:

```text
SHADOW_EXECUTION_SETTLED
SHADOW_EXECUTION_FAIL_CLOSED
```

The battle-level A1 Reality settlement is separate from episode-level settlement.

---

## 13. VeighNa boundary

YVN1-A0 deliberately freezes VeighNa out of A1.

This is an architectural ablation:

> If Yuanli's authority, ledger, state projection, idempotency, reconciliation and settlement cannot exist without VeighNa, Yuanli does not own an Execution OS; it only owns a wrapper around a trading framework.

VeighNa is reserved for a later provider-adapter battle:

```text
YVN1-A2｜VeighNa Adapter Shadow Reality Proof
```

A2 may map the Provider Interface onto VeighNa `MainEngine`, OMS, RiskManager and a paper/shadow provider, subject to a separate design and Human Gate.

YVN1-A0 approval does not authorize VeighNa installation.

---

## 14. Program decomposition

The approved execution roadmap is:

```text
YEX0
Capital × Execution Constitution
        │
        │ ACCEPTED + MERGED
        ▼
YVN1-A0
Shadow Execution Constitution
& Deployment Freeze
        │
        │ Written Spec + Human Gate
        ▼
YVN1-A1
Provider-Independent Synthetic Shadow Runtime
        │
        │ 10 Golden Scenarios
        │ Replay / Reconcile / Fail-Closed
        ▼
YVN1-A2
VeighNa Adapter Shadow Reality Proof
        │
        │ provider ablation
        ▼
YVN2
Broker Paper
        ▼
YVN3
Controlled Live
```

No downstream stage is automatically authorized by an upstream PASS.

---

## 15. YVN1-A0 expected implementation artifacts after written-spec approval

A later implementation plan may create Canon artifacts such as:

```text
config/yvn1/yvn1_a0_shadow_execution.v0.1.json

docs/architecture/yvn1/
  YVN1-A0-SHADOW-EXECUTION-CONSTITUTION-v0.1.md
  YVN1-A0-DEPLOYMENT-FREEZE-v0.1.md
  YVN1-A0-HUMAN-REVIEW-CARD-v0.1.md

packages/contracts/schemas/vnext/
  execution-plan.schema.json
  shadow-execution-settlement.schema.json
  provider-state.schema.json

scripts/
  validate_yvn1_a0_shadow_execution.py

tests/
  test_yvn1_a0_shadow_execution.py
```

This list is a design expectation, not implementation authorization. The writing-plans phase may refine file boundaries without weakening the constitutional requirements in this spec.

A1 runtime implementation should occur only after A0 itself is accepted and merged, and should use a separately isolated execution-runtime workstream.

---

## 16. YVN1-A0 machine qualification target

The only valid A0 pre-human machine status is:

```text
YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED
```

It means only that the constitution, provider boundary, deployment topology, Golden Scenarios, A1 victory law and hard non-authorizations are machine-checkable and internally consistent.

It does not mean:

```text
VeighNa ready
Broker ready
Paper trading ready
Live trading ready
Execution production ready
```

Final A0 status after separate Human Review and separately authorized merge may be:

```text
YVN1_A0_DEPLOYMENT_FROZEN
```

Only then may YVN1-A1 be opened as a new independently authorized implementation battle.

---

## 17. Non-goals

YVN1-A0 explicitly does not design or implement:

- market alpha;
- investment thesis generation;
- portfolio optimization;
- actual position sizing;
- P&L attribution as the success metric;
- production order-book simulation;
- real slippage calibration;
- VeighNa integration;
- RiskManager integration;
- broker API integration;
- real market-data ingestion;
- cloud HA;
- distributed execution;
- automatic failover;
- YVN2 or YVN3.

---

## 18. Final design law

The mother principle of YVN1 is:

> Execution is not sending orders. Execution is a governed reality transition whose authority, side effects, evidence, reconciliation and failure state can all be reconstructed after the fact.

Machine shorthand:

```text
NO EXECUTION WITHOUT AUTHORITY
NO SIDE EFFECT WITHOUT IDEMPOTENT IDENTITY
NO STATUS WITHOUT LEDGER
NO SETTLEMENT WITHOUT RECONCILIATION
NO AMBIGUITY WITHOUT FAIL-CLOSED
NO FAILURE WITHOUT LEARNING
```

YVN1-A0 freezes the deployment constitution required to test that law without placing any real order.

---

## 19. Human-gate separation

YVN1-A0 uses four distinct Human Gates. One gate never implies the next.

### Gate G0 — architecture acceptance

Already received:

```text
ACCEPT_YVN1_A0_SHADOW_EXECUTION_DEPLOYMENT_ARCHITECTURE
```

Meaning: the in-chat architecture is accepted strongly enough to be written into this design spec.

It does **not** approve implementation.

### Gate G1 — written-spec acceptance

Required next token:

```text
ACCEPT_YVN1_A0_WRITTEN_SPEC
```

Meaning: this exact written design is approved strongly enough to enter `writing-plans` and prepare the A0 implementation plan.

It does **not** authorize VeighNa installation, A1 runtime execution, broker access, or A0 merge.

### Gate G2 — A0 Human Acceptance after machine qualification

A later candidate token may be frozen by the implementation artifacts as:

```text
ACCEPT_YVN1_A0_DEPLOYMENT_FREEZE
```

This gate may occur only after A0 TDD, validator and repository gates machine-qualify the exact candidate head.

### Gate G3 — A0 merge authorization

A later independent merge token may be frozen as:

```text
AUTHORIZE_YVN1_A0_MERGE
```

Merge authority is never implied by G0, G1 or G2.

Only after a separately authorized merge and post-merge Reality readback may the architecture expose `YVN1-A1` as the next lawful battle.

At every gate, the following remain false unless a later dedicated program explicitly changes them:

```text
veighna_invocation_authorized = false
broker_credentials_authorized = false
broker_paper_authorized = false
live_execution_authorized = false
real_capital_movement_authorized = false
```