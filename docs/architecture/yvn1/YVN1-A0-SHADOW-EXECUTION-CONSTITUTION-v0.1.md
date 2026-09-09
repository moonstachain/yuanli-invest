# YVN1-A0｜Shadow Execution Constitution v0.1

Status: `IMPLEMENTATION_CANDIDATE`  
Authority ceiling: design/contracts only  
Upstream: `YEX0_ACCEPTED_MERGED`

## 1. Mission

YVN1-A0 freezes the constitutional boundary for Yuanli's first provider-independent Shadow Execution Runtime. It does not execute an order. It defines the law that a later YVN1-A1 runtime must obey.

The lawful future chain is:

```text
ActionContract
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
Four-Way Reconciliation
  ↓
ShadowExecutionSettlement
```

## 2. Upstream YEX0 laws remain binding

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
```

YVN1-A0 may specialize these laws for Shadow execution. It may not weaken or replace them.

## 3. Sole lawful entry object

The only lawful execution entry object is a valid YEX0 `ActionContract`.

Free-form commands such as `BUY NVDA`, `rebalance portfolio`, or `execute thesis` are not execution authority. ChatGPT, Web, Notion, research workers, and human terminals cannot directly invoke a provider order method.

## 4. Future A1 component boundary

A later A1 runtime is limited to six primary responsibilities:

1. Shadow Action Intake
2. Authorization Firewall
3. Execution Orchestrator
4. Provider Interface
5. Synthetic Shadow Provider
6. Reconciliation + Settlement

The Orchestrator depends only on the Provider Interface. It must not depend directly on VeighNa.

## 5. Provider-independent-first law

YVN1-A1 must first prove Yuanli execution semantics without VeighNa.

```text
ShadowProvider
      ↓ replace later
VeighNaProvider
      ↓
VeighNa MainEngine / RiskManager / Gateway
```

VeighNa is reserved for a later independent battle `YVN1-A2｜VeighNa Adapter Shadow Reality Proof`.

## 6. Execution state machine

Normal projection path:

```text
RECEIVED
→ AUTHORITY_CHECKING
→ AUTHORIZED
→ PLANNED
→ SUBMITTING
→ WORKING
→ PARTIALLY_FILLED
→ FILLED
→ RECONCILING
→ SETTLED
```

First-class blocking/terminal states:

```text
DENIED
EXPIRED
REJECTED
CANCELLED
DRIFTED
FAIL_CLOSED
```

State is projection. Event history is truth.

## 7. Event Ledger constitution

```text
Execution Events = truth
Execution Status = projection
```

The future Event Ledger is append-only, hash-chained, and replayable. Logs are not ledger truth. Mutable status fields are not ledger truth.

## 8. Atomicity and idempotency

The frozen side-effect order is:

```text
Idempotency identity reserved durably
→ Pre-submit event persisted
→ Provider side effect attempted
→ Provider acknowledgement/event persisted
```

For the same lawful ActionContract identity and idempotency key:

```text
duplicate_order_submission = 0
```

If a crash creates uncertainty about whether a side effect occurred, the runtime must reconcile. It must not blindly resubmit.

## 9. Four-Way Reconciliation

The four identities are mandatory:

```text
1. Capital Intent Ledger
2. Yuanli Execution Ledger
3. Execution Engine / Shadow OMS
4. Synthetic Broker / Custodian State
```

`Shadow OMS` and `Synthetic Broker/Custodian State` must be independently materialized identities. Self-comparison is inadmissible evidence.

Any unexplained order, fill, position, or cash delta causes:

```text
DRIFTED
→ FAIL_CLOSED
```

## 10. Golden Failure

A material execution incident is knowledge. Any newly discovered failure class must receive an immutable Golden Failure identity and become a regression fixture. Repairing the implementation does not delete historical failure evidence.

## 11. Mother law

```text
NO EXECUTION WITHOUT AUTHORITY
NO SIDE EFFECT WITHOUT IDEMPOTENT IDENTITY
NO STATUS WITHOUT LEDGER
NO SETTLEMENT WITHOUT RECONCILIATION
NO AMBIGUITY WITHOUT FAIL-CLOSED
NO FAILURE WITHOUT LEARNING
```

Execution is not sending orders. Execution is a governed Reality transition whose authority, side effects, evidence, reconciliation, and failure state can be reconstructed after the fact.

## 12. Hard non-authorizations

YVN1-A0 does not authorize:

- VeighNa installation/import/invocation;
- broker credentials or broker connection;
- market-data subscription;
- broker-paper or live order submission;
- real capital movement;
- portfolio weighting or position sizing;
- automatic research-to-execution bridge;
- YVN1-A1 runtime;
- YVN1-A2;
- YVN2 or YVN3;
- creation of a production execution repository;
- merge.

The only pre-human machine settlement is:

`YVN1_A0_DEPLOYMENT_FREEZE_MACHINE_QUALIFIED`
