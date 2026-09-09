# YVN1-A0｜Deployment Freeze v0.1

Status: `IMPLEMENTATION_CANDIDATE`

## 1. A1 target environment

The future YVN1-A1 synthetic shadow runtime is frozen to:

```text
Python 3.12
uv-managed isolated environment
single process
single runtime host
SQLite WAL
local filesystem sandbox
Synthetic Shadow Provider
no public RPC
no broker network dependency
```

A1 validates execution semantics, not horizontal scale.

## 2. Runtime filesystem contract

```text
runtime/
  config/        immutable run configuration and contract references
  ledger/        append-only operational truth
  artifacts/     settlement and evidence artifacts
  logs/          operational logs; non-authoritative
  projections/   disposable/rebuildable views
  quarantine/    malformed, conflicting, unknown, or drifted inputs
```

`ledger/` is authoritative operational truth.

`logs/` are not the ledger.

`projections/` may be deleted and rebuilt from the ledger.

`quarantine/` is a first-class fail-closed destination.

## 3. Edge truth law

A1 uses SQLite WAL as the local edge truth store because the runtime must remember what it has done even if a network service is unavailable.

Future central Postgres/Supabase audit sync may be added only by a later independent program. Central connectivity must never be required for remembering local execution truth.

## 4. Explicitly rejected A1 infrastructure

The following are out of scope for A1:

```text
Kubernetes
Kafka
service mesh
distributed microservices
multi-region deployment
production cloud failover
real broker gateway
```

No infrastructure may be added merely to resemble a production trading stack.

## 5. Provider boundary

A1 uses only `Synthetic Shadow Provider`.

It may simulate execution events such as accepted, partial fill, filled, reject, timeout, disconnect, reconnect, late fill, duplicate delivery, external-order drift, position drift, and cash drift. It is not an order-book or alpha simulator.

VeighNa is excluded from A1 and reserved for `YVN1-A2` under a separate Human Gate.

## 6. Credential and network freeze

A1 must contain no broker username, password, token, API key, paper credential, live credential, or real market-data permission.

```text
ResearchCredential
!= CapitalCredential
!= ExecutionCredential
!= BrokerCredential
```

YVN1-A0 authorizes none of the broker-facing domains.

## 7. Frozen A1 Golden Scenarios

The minimum registry is exactly S01-S10. S07 `crash_after_submit_before_ack_persistence` is P0. The registry is frozen before A1 implementation and cannot be expanded, dropped, or reweighted to rescue an outcome.

## 8. Frozen A1 victory law

A1 may be declared `YVN1_A1_SHADOW_RUNTIME_REALITY_PASS` only if all ten preregistered scenarios produce their preregistered terminal behavior, duplicate order submissions remain zero, replay is deterministic, non-drift scenarios reconcile without unexplained deltas, S09/S10 fail closed, and all broker/live/real-capital authorities remain absent.

If any required condition fails, the lawful result is `YVN1_A1_SHADOW_RUNTIME_REALITY_NO_GO`.

No silent rescue, threshold relaxation, scenario deletion, or immediate VeighNa substitution is permitted under the same battle identity.
