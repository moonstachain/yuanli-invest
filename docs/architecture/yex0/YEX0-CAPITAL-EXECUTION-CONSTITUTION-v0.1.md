# YEX0｜Yuanli Capital × Execution Constitution v0.1

Status: `IMPLEMENTATION_CANDIDATE`  
Authority: `constitution candidate only`  
Live execution authority: `FALSE`

## 1. Mission

YEX0 defines how a Yuanli research result may, in a future separately authorized program, cross into capital and execution without collapsing epistemic authority, capital authority and execution authority into one system.

The governing chain is:

```text
Research Settlement
  ↓
Capital Admission
  ↓
PositionPassport
  ↓
ExecutionIntent
  ↓
Human Execution Authorization / ActionContract
  ↓
Capital Action Gateway
  ↓
Execution Runtime
  ↓
Execution Provider Adapter
  ↓
Market / Broker Reality
  ↓
Execution Event Ledger
  ↓
Four-Way Reconciliation
  ↓
Execution Settlement
```

YEX0 defines the law and contracts. It does not run this chain against a broker.

## 2. Three-authority constitution

`ResearchAuthority != CapitalAuthority != ExecutionAuthority`

### Research Authority

Answers: is the research claim admissible under evidence, PIT, baseline, falsifier and settlement law?

A Research PASS cannot size a position or move capital.

### Capital Authority

Answers: should the portfolio assume a bounded risk exposure now, under survival and portfolio constraints?

CapitalAdmission is independent of research settlement. It may reject an epistemically valid thesis.

### Execution Authority

Answers: may a narrow, expiring, idempotent ActionContract be presented to an execution runtime?

Execution authority may be narrower than capital authority and cannot expand it.

## 3. Existing ME1 boundary is preserved

Existing ME1 objects remain distinct:

`ResearchTarget != EngineThesis != PositionPassport != BookState`

PositionPassport remains non-executable. Its four authority fields must remain false:

- portfolio weight authority;
- position sizing authority;
- trade execution authority;
- live execution authority.

YEX0 adds downstream objects rather than changing PositionPassport into an order instruction.

## 4. New YEX0 objects

### CapitalAdmission

Portfolio-level gate referencing Research Settlement and PositionPassport. It records a bounded risk budget and human decision, but grants no order-submission or live authority.

### ExecutionIntent

Provider-neutral statement of the desired capital-state transition: instrument, direction, quantity delta, notional/loss/slippage bounds, venue scope, time window and idempotency key.

Intent is not authorization.

### ActionContract

Narrow execution authorization envelope. It binds one intent, one capital admission and one human approval reference. Its scope may only equal or shrink the intent. In YEX0 v0.1, supported modes are `shadow` and `broker_paper`; live and real-capital flags remain false.

### ExecutionEvent

Append-only execution truth event. Events form a logical sequence and hash chain. Mutable status is derived from events and is never the truth source.

### ExecutionSettlement

Closes one execution episode against physical or simulated reality after reconciliation. It records execution quality separately from the upstream research outcome and grants no new authority.

## 5. Authorization Firewall

The future firewall is a pure authority/scope function, not a market-prediction function.

```text
ALLOW | DENY | UNKNOWN
```

Constitutional rule:

`UNKNOWN = DENY`

Mandatory denial conditions include missing references, expiry, scope expansion, identity mismatch, unauthorized mode, live/real-capital flags, duplicate-key conflict and ambiguous runtime/reconciliation state.

## 6. Receipt = Ledger; Status = Projection

Execution truth is event history such as:

```text
IntentCreated
CapitalAdmissionObserved
ActionContractGranted
FirewallPassed
PlanCreated
OrderSubmitted
OrderAccepted
FillReceived
PositionObserved
AccountObserved
ReconciliationMatched
SettlementClosed
```

Statuses such as `AUTHORIZED`, `FILLED`, `RECONCILED`, `DRIFTED` and `SETTLED` are projections reconstructed from the ledger.

## 7. Four-way reconciliation

Production invariant:

1. Capital Intent Ledger — what Yuanli was allowed to change;
2. Yuanli Execution Ledger — what Yuanli believes it attempted/observed;
3. Execution Engine / OMS — what the execution runtime believes happened;
4. Broker / Custodian — what physically exists at the account boundary.

Any unexplained order, fill, position or cash delta triggers `DRIFTED` / `FAIL_CLOSED` and freezes further execution.

YVN1 Shadow may simulate external legs while preserving all four reconciliation identities.

## 8. Research settlement and execution settlement remain separate

A trade P&L or execution incident cannot silently rewrite a research thesis.

Research settlement answers whether the investment claim survived Reality.

Execution settlement answers whether an approved action was executed faithfully, including fill, slippage, latency, rejection, provider reliability and reconciliation quality.

`ResearchFailure != ExecutionFailure`

## 9. Execution provider boundary

YEX0 is provider-neutral. Domain, authorization, firewall, ledger and reconciliation contracts must not depend on VeighNa.

A future provider adapter may implement:

```text
Yuanli Execution Runtime
  -> VeighNa adapter
  -> VeighNa MainEngine / RiskManager / Paper or Broker Gateway
```

VeighNa remains an execution engine candidate, not the research brain, capital authority, public API or source of Canon truth.

## 10. Security constitution

- Research credentials != Capital credentials != Broker credentials.
- Research workers never hold broker trading credentials.
- ChatGPT/Web/Notion cannot directly invoke provider order methods.
- Provider RPC is private/localhost or private-subnet only; untrusted public access is prohibited.
- Every future ActionContract is narrow, expiring, hashed and idempotent.
- Duplicate delivery must not create duplicate order submission.
- Ambiguous authority or ambiguous Reality fails closed.

## 11. Golden Failure Constitution

Material execution incidents are knowledge and must become immutable regression identities, including authorization bypass, duplicate delivery, expiry failure, scope escalation, replay divergence, unknown external order, fill mismatch, position/cash drift, reconnect ambiguity, late-event ambiguity and provider runtime defects.

A closed incident may be fixed operationally; its regression evidence is not deleted.

## 12. Current machine boundary

YEX0 v0.1 is allowed to machine-qualify only the constitution and provider-neutral contracts.

It explicitly does not authorize:

- portfolio weighting or position sizing;
- VeighNa installation or invocation;
- broker credentials;
- market-data subscriptions;
- paper-broker or live orders;
- real capital movement;
- YVN1/YVN2/YVN3 runtime;
- automatic Canon promotion or merge.

The only successful YEX0 machine settlement is:

`YEX0_CONSTITUTION_MACHINE_QUALIFIED`

After separate Human Review and merge, the next lawful battle is:

`YVN1-A0｜Shadow Execution Constitution & Deployment Freeze`
