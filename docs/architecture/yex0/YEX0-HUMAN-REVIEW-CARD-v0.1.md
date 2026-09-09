# YEX0 Human Review Card v0.1

Review only after exact-head `repository-gates` PASS.

## Review decisions

1. **Three-authority separation** — accept `ResearchAuthority != CapitalAuthority != ExecutionAuthority`.
2. **ME1 preservation** — PositionPassport remains non-executable and grants zero portfolio weight, sizing, trade or live authority.
3. **CapitalAdmission boundary** — accepts/rejects bounded portfolio risk admission but never submits orders.
4. **Intent boundary** — ExecutionIntent describes desired state change and cannot self-authorize.
5. **ActionContract boundary** — narrow, expiring, idempotent, human-referenced; YEX0 supports only shadow/broker-paper contracts with live/real-capital flags false.
6. **Firewall law** — `UNKNOWN = DENY`; ambiguity and scope expansion fail closed.
7. **Truth law** — `Receipt = Ledger; Status = Projection`; append-only execution events are truth.
8. **Reconciliation law** — four-way identities are mandatory: Capital Intent, Yuanli Execution, Execution Engine/OMS, Broker/Custodian.
9. **Settlement separation** — Research failure and Execution failure remain distinct causal channels.
10. **Provider neutrality** — VeighNa is a future adapter/runtime candidate, not Capital Authority or Canon.
11. **Security boundary** — Research/Capital/Broker credentials remain separated; no public untrusted provider RPC.
12. **Golden Failure law** — material execution incidents become immutable regression fixtures.
13. **No live authority** — broker credentials, market subscription, paper/live order submission and real capital movement remain unauthorized.
14. **Next-battle boundary** — acceptance/merge of YEX0 may only unlock design of `YVN1-A0`; it does not execute YVN1.

## Machine evidence required before review

- YEX0 validator PASS;
- YEX0 unittest suite PASS;
- repository `contracts` PASS;
- repository `governance` PASS;
- no PositionPassport authority regression;
- no provider/broker dependency introduced;
- no live-execution or real-capital authority introduced.

## Candidate Human decision token

`ACCEPT_YEX0_CAPITAL_EXECUTION_CONSTITUTION`

Acceptance approves the constitution candidate only. Merge remains a separate action unless explicitly authorized.
