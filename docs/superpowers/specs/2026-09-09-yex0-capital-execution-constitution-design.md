# YEX0｜Yuanli Capital × Execution Constitution — Design

Date: 2026-09-09  
Status: `HUMAN_APPROVED_ARCHITECTURE / IMPLEMENTATION_CANDIDATE`  
Scope: `YEX0 constitution and machine contracts only`  
Repository: `moonstachain/yuanli-invest`

## 0. Purpose

YEX0 defines the authority boundary between Yuanli Research OS, capital allocation, and market execution.

Its purpose is not to build an automated trading system. Its purpose is to make any future transition from research knowledge to capital action explicit, machine-checkable, auditable, reversible where possible, and fail-closed.

The constitutional target is:

`RESEARCH -> CAPITAL ADMISSION -> EXECUTION AUTHORIZATION -> GOVERNED EXECUTION -> REALITY -> RECONCILIATION -> SETTLEMENT`

YEX0 creates no broker connection, no broker credential, no live order, no live position sizing, and no live capital movement authority.

---

## 1. First principles

YEX0 freezes the following separation:

`ResearchAuthority != CapitalAuthority != ExecutionAuthority`

The three domains answer different questions:

1. Research Authority — is a claim epistemically admissible?
2. Capital Authority — may the portfolio assume this risk now?
3. Execution Authority — may a bounded action contract be sent to an execution runtime?

No upstream object may silently inherit downstream authority.

Existing ME1 semantics remain sovereign:

`ResearchTarget != EngineThesis != PositionPassport != BookState`

`PositionPassport` remains a capital-expression research object and MUST retain:

- `portfolio_weight_authority = false`
- `position_sizing_authority = false`
- `trade_execution_authority = false`
- `live_execution_authority = false`

YEX0 extends the chain without mutating that authority:

`ResearchSettlement -> CapitalAdmission -> PositionPassport -> ExecutionIntent -> ActionContract -> ExecutionRuntime -> ExecutionSettlement`

---

## 2. Constitutional laws

YEX0 freezes twelve laws.

### YEX-L1 | Research Pass != Capital Pass

A valid research result cannot allocate capital by itself.

### YEX-L2 | Capital Pass != Execution Pass

A portfolio-level capital admission cannot by itself submit an order.

### YEX-L3 | PositionPassport never grants execution

PositionPassport describes a governed expression candidate. It does not size or execute.

### YEX-L4 | Intent != Authorization

ExecutionIntent expresses the desired capital-state change. It cannot self-authorize.

### YEX-L5 | ActionContract is narrow, expiring, and idempotent

Any executable authorization envelope must bind a single intent, bounded quantity/notional/loss/slippage/venue/time scope, a human approval reference, an idempotency key, and an expiry.

### YEX-L6 | UNKNOWN = DENY

Authorization Firewall outputs only `ALLOW`, `DENY`, or `UNKNOWN`; `UNKNOWN` MUST be treated as `DENY`.

### YEX-L7 | Receipt = Ledger; Status = Projection

Execution truth is append-only event history. Mutable lifecycle status is a derived projection and is never the source of truth.

### YEX-L8 | Four-way reconciliation

Production-grade execution must reconcile four ledgers:

1. Capital Intent Ledger
2. Yuanli Execution Ledger
3. Execution Engine / OMS state
4. Broker / Custodian reality

Any unexplained position, cash, order, fill, or account drift must fail closed.

### YEX-L9 | Research failure != Execution failure

Research settlement and execution settlement are separate causal channels. A losing trade cannot automatically rewrite a research thesis; an execution incident cannot be silently classified as model failure.

### YEX-L10 | Execution adapters are replaceable

Domain, authorization, firewall, ledger, reconciliation, and settlement contracts are execution-provider neutral. VeighNa imports are allowed only in a future provider adapter/runtime layer, not in YEX0 contracts.

### YEX-L11 | Failure is knowledge

Material execution incidents become append-only Golden Failure regression fixtures. Failures may not be deleted merely because an upstream dependency later fixes the defect.

### YEX-L12 | No live authority in YEX0

YEX0 may define contracts for future shadow/paper execution, but all live-execution and real-capital-movement authority remains false.

---

## 3. Canonical object boundaries

YEX0 creates five new candidate machine contracts.

### 3.1 CapitalAdmission

Purpose: independent portfolio-level permission to consider a bounded expression candidate.

Required semantics:

- references a Research Settlement and PositionPassport;
- records capital-book / risk-budget scope;
- records validity window and human decision reference;
- may permit only `shadow` or future separately authorized `broker_paper` stages in v1;
- cannot authorize order submission;
- cannot authorize real capital movement;
- cannot authorize live execution.

### 3.2 ExecutionIntent

Purpose: transport-neutral description of the desired capital-state transition.

Required semantics:

- references CapitalAdmission and PositionPassport;
- one instrument and direction per intent in v1;
- quantity delta / max notional / max loss / max slippage;
- allowed venue set;
- `created_at`, `valid_from`, `expires_at`;
- unique idempotency key;
- self-authorization prohibited.

ExecutionIntent answers `what outcome is desired`, not `how orders will be sliced`.

### 3.3 ActionContract

Purpose: narrow authorization envelope consumed by a future Capital Action Gateway / Execution Runtime.

Required semantics:

- exactly one ExecutionIntent;
- explicit human approval reference;
- contract hash;
- bounded action scope equal to or narrower than the intent;
- expiry;
- idempotency key;
- execution mode limited to `shadow` or `broker_paper` in v1;
- `live_execution_authorized = false`;
- `real_capital_movement_authorized = false`.

### 3.4 ExecutionEvent

Purpose: append-only truth object for event-sourced execution history.

Required semantics:

- monotonic logical sequence within stream;
- unique event ID and idempotency key;
- links intent, action contract, and optional authorization identity;
- `occurred_at` and `recorded_at` kept distinct;
- previous-event hash and event hash;
- append-only flag;
- defined event taxonomy including intent, authorization, firewall, plan, order, fill, observation, reconciliation, failure, and settlement events.

State labels such as `AUTHORIZED`, `FILLED`, `RECONCILED`, and `SETTLED` are projections only.

### 3.5 ExecutionSettlement

Purpose: close an execution episode against physical reality without mutating research settlement.

Required semantics:

- references intent, action contract, event stream, and execution mode;
- records four-way reconciliation results;
- explicitly separates `research_outcome_ref` from `execution_quality`;
- records unexplained order/position/cash drift;
- supports `SETTLED`, `DRIFTED`, `FAIL_CLOSED`, `INDETERMINATE`;
- cannot grant new capital or execution authority.

---

## 4. Authorization Firewall contract

YEX0 freezes the firewall as a pure decision boundary.

Conceptual interface:

```text
firewall.evaluate(
    intent,
    action_contract,
    runtime_state,
    market_state
) -> ALLOW | DENY | UNKNOWN
```

Mandatory rules:

- missing reference => `DENY`;
- expired intent or contract => `DENY`;
- intent/contract identity mismatch => `DENY`;
- scope expansion => `DENY`;
- duplicate idempotency key with non-identical payload => `DENY`;
- unknown runtime or reconciliation state => `UNKNOWN`, which is treated as `DENY`;
- any live / real-capital flag under YEX0 => `DENY`.

No price prediction or strategy logic belongs in this firewall.

---

## 5. Event and projection model

Canonical event progression may include:

```text
IntentCreated
CapitalAdmissionObserved
ActionContractGranted
FirewallPassed
PlanCreated
OrderSubmitted
OrderAccepted
PartialFillReceived
FillReceived
PositionObserved
AccountObserved
ReconciliationMatched
ExecutionFailureObserved
SettlementClosed
```

Derived lifecycle projections may include:

```text
CREATED
AUTH_PENDING
AUTHORIZED
FIREWALL_PASSED
PLANNED
SUBMITTED
ACCEPTED
PARTIAL_FILL
FILLED
RECONCILING
RECONCILED
SETTLED
BLOCKED
EXPIRED
REJECTED
CANCELLED
UNKNOWN
DRIFTED
FAIL_CLOSED
```

Projection state must be reproducible from the immutable event stream.

---

## 6. Four-way reconciliation constitution

The long-term reconciliation equation is:

`Approved Intent -> Yuanli Ledger -> Execution Engine / OMS -> Broker Reality -> Account / Position Reality`

The four ledgers are:

1. `capital_intent`
2. `yuanli_execution`
3. `execution_engine_oms`
4. `broker_custodian`

Fail-closed conditions include at minimum:

- unknown external order;
- unexplained fill;
- unexplained position delta;
- unexplained cash delta;
- missing or conflicting order identity;
- settlement attempted before reconciliation;
- stale broker/account observation beyond the contract tolerance.

YVN1 Shadow may initially exercise a reduced two-party physical fixture while preserving this four-way contract as the production invariant.

---

## 7. Deployment boundary

YEX0 defines boundaries only.

Future physical separation:

```text
Research OS
  -> Research Settlement
  -> Capital Admission Gate
  -> PositionPassport
  -> ExecutionIntent
  -> Human Capital Authorization
  -> ActionContract
  -> Capital Action Gateway
  -> Yuanli Execution Runtime
  -> Execution Adapter (e.g. VeighNa)
  -> Risk Manager
  -> Broker / Venue
  -> Reality Events
  -> Execution Ledger
  -> Reconciliation
  -> Execution Settlement
```

`quant-workspace` remains research/quant compute and is not granted execution-sovereign authority by YEX0.

VeighNa is a future execution-provider adapter/runtime candidate, not the Control Plane and not the capital authority.

---

## 8. Security invariants

YEX0 freezes:

- Research credentials != Capital credentials != Broker credentials.
- Broker credentials may never be present in research workers.
- Execution-provider RPC must not be exposed as an untrusted public interface.
- Public-facing ChatGPT/Web/Notion layers cannot directly call provider execution methods.
- Every future ActionContract must be narrow, expiring, hashed, and replay-safe.
- Duplicate delivery must not imply duplicate order submission.
- Any ambiguity in authority or reality fails closed.

---

## 9. Golden Failure registry contract

YEX0 defines an incident taxonomy for future YVN programs:

- authorization bypass attempt;
- duplicate intent / duplicate delivery;
- stale or expired authorization;
- scope escalation;
- runtime restart / replay divergence;
- unknown external order;
- order/fill identity mismatch;
- position drift;
- cash drift;
- provider reconnect ambiguity;
- event ordering / late-event ambiguity;
- execution-provider runtime defect.

Every admitted incident receives an immutable `GF-*` identity and a regression fixture before the program may claim closure.

---

## 10. Machine qualification

YEX0 implementation must include:

1. machine-readable constitution config;
2. five JSON Schemas;
3. fail-closed validator;
4. positive fixture bundle;
5. negative tests covering authority escalation, live flags, expiry/scope rules, projection/ledger confusion, and reconciliation incompleteness;
6. repository CI integration.

The validator MUST assert that the pre-existing PositionPassport still grants zero execution authority.

---

## 11. Explicit non-authorizations

YEX0 does NOT authorize:

- creation of broker or exchange credentials;
- VeighNa installation or invocation;
- real market-data subscription;
- broker paper order submission;
- live order submission;
- portfolio weighting or position sizing;
- autonomous capital movement;
- YVN1/YVN2/YVN3 runtime execution;
- Canon promotion or merge merely because CI passes.

`Research Pass != Capital Pass != Execution Pass` remains binding.

---

## 12. Settlement gate

YEX0 may be considered machine-qualified only when:

- constitution and all five schemas exist;
- PositionPassport authority remains all false;
- validator passes positive fixture;
- every hard-negative authority attack fails closed;
- repository `contracts` and `governance` checks pass on exact PR head;
- no broker/provider/live-execution dependency is introduced.

Machine qualification yields only:

`YEX0_CONSTITUTION_MACHINE_QUALIFIED`

It does not imply merge or any execution runtime authority.

After a separate Human Review and merge, the next lawful battle is:

`YVN1-A0｜Shadow Execution Constitution & Deployment Freeze`
