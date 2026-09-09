# YVN1-A0 Human Review Card v0.1

Review only after exact-head `repository-gates` PASS and machine qualification receipt exists.

## Review decisions

1. **YEX0 upstream law** — YEX0 remains binding and YVN1-A0 cannot weaken its authority separation.
2. **Entry boundary** — `ActionContract` is the only lawful execution entry object.
3. **Provider-independent-first** — YVN1-A1 excludes VeighNa; VeighNa is deferred to A2.
4. **Runtime separation** — the future A1 runtime is a separate execution-runtime boundary, not a research module.
5. **Reconciliation independence** — Shadow OMS and Synthetic Broker/Custodian are independent state identities.
6. **Truth law** — Event Ledger is truth; status is projection.
7. **Edge truth** — SQLite WAL is the A1 local operational truth; logs and projections are non-authoritative.
8. **Firewall law** — `UNKNOWN = DENY` applies during normal execution and restart recovery.
9. **Atomicity law** — idempotency reservation and pre-submit persistence precede any provider side effect.
10. **Golden Scenario law** — S01-S10 are frozen before A1; S07 is P0.
11. **Victory law** — A1 success criteria are preregistered before A1 implementation.
12. **Scientific failure allowed** — A1 may settle NO-GO; no silent rescue, threshold relaxation, scenario deletion, or hidden provider substitution.
13. **No execution authority** — A0 creates no VeighNa/broker/paper/live/real-capital authority.
14. **Gate separation** — A0 Human Acceptance does not imply merge, A1, A2, YVN2, or YVN3 authorization.

## Machine evidence required before Human Review

- YVN1-A0 validator PASS;
- YVN1-A0 unittest PASS;
- repository `contracts` PASS;
- repository `governance` PASS;
- exact S01-S10 registry with S07=P0;
- three provider-neutral schemas validate under JSON Schema Draft 2020-12;
- no provider/runtime/broker dependency introduced;
- no authority escalation introduced;
- exact-head scope audit PASS.

## Candidate G2 Human decision token

`ACCEPT_YVN1_A0_DEPLOYMENT_FREEZE`

This token accepts the machine-qualified A0 deployment freeze candidate only.

## Separate G3 merge token

`AUTHORIZE_YVN1_A0_MERGE`

G2 never implies G3.

At both gates, these remain false unless a later dedicated program explicitly changes them:

```text
veighna_invocation_authorized = false
broker_credentials_authorized = false
broker_paper_authorized = false
live_execution_authorized = false
real_capital_movement_authorized = false
a1_runtime_authorized = false
```
