# YQS0｜Yuanli Quant × Supabase Sovereign Research Kernel Architecture v0.1

Status: `candidate_started`

Upstream authority:

- YIP0 / OS vNext remain philosophy and human research grammar authority.
- ME0 remains Return Engine ontology authority.
- ME1 remains state-object authority for `ResearchTarget -> EngineThesis -> PositionPassport -> BookState@PIT`.
- R2.3-B0 remains the universal `ResearchCapability` contract authority.
- Q0 remains the accepted A9 quant/AI research architecture baseline.
- `moonstachain/quant-workspace` remains the current A9 operational canon; YQS0 does not authorize an operational-canon switch.

Base main observed when YQS0 branch was created: `a627587596da721ee94ce982aaa15b754ca14dc5`.

---

## 1. Governing decision

YQS0 freezes a candidate architecture in which Supabase becomes the **Research State Kernel / Operational Memory / Control Plane** for Yuanli Quant, without becoming Canon Authority or heavy-quant compute.

The architecture is deliberately three-part:

```text
GitHub
Normative Authority Plane
law / contract / schema / accepted canon
        |
        v
Supabase
Research State Kernel
state / evidence metadata / PIT / runtime / replay / governance ledger / projection
        |
        +-------------------+
        |                   |
        v                   v
Quant Compute           Agent Runtime
Python / DuckDB         reasoning / synthesis
Polars / ML             evidence organization
Replay / Backtest       structured candidate output
```

Six stable responsibility statements are frozen:

```text
GitHub        = WHAT IS LEGAL
Supabase      = WHAT IS CURRENT
Quant Runtime = WHAT IS COMPUTED
Evidence Vault= WHAT ACTUALLY EXISTED
Agent Runtime = WHAT IS INFERRED
Human Gate    = WHAT IS AUTHORIZED
```

YQS0 therefore rejects both extremes:

- `Supabase-only`: putting Canon, raw market warehouse, heavy backtest, long-running agents and execution into one managed backend.
- `GitHub-only`: using repository files as the operational state database for high-frequency state transitions, runtime receipts, RLS, queueing and human projections.

---

## 2. Non-negotiable invariants

1. **GitHub Canon Authority is not delegated.** Supabase may project accepted Canon and persist operational state; it may not mutate normative GitHub authority.
2. **ME1 identities are reused, not redefined.** `ResearchTarget`, `EngineThesis`, `PositionPassport`, `BookState` keep their accepted semantics.
3. **PIT is enforced at the data-access boundary.** Replay eligibility is not a prompt convention.
4. **Append-first learning and governance.** Historical states, revisions, settlements and authority events are preserved rather than silently overwritten.
5. **Claim Authority <= Evidence Authority.** Supabase evidence metadata supports the rule; it does not relax it.
6. **Research Pass != Capital Pass.** No YQS0 object grants allocation, sizing, buy/sell/hold or execution authority.
7. **Heavy deterministic compute remains external.** Supabase schedules and stores; Python/DuckDB/Polars/ML workers calculate.
8. **Edge Functions are orchestration adapters, not quant HPC.** Long matrix jobs, broad factor scans, large replays and model training remain outside Edge Functions.
9. **Raw evidence is not Git Canon.** Large/vendor/raw evidence remains in Local/NAS/Object Storage with immutable locators and hashes.
10. **No magic score.** State vectors, transitions, evidence and uncertainty remain typed; YQS0 creates no scalar master Force score.
11. **No live execution.** Live broker connectivity and trade execution remain unavailable by design.
12. **No successor-stage smuggling.** YQS0 does not authorize ME2-ME5, QXM3, A9 switch, evidence admission, outcome admission or Registry promotion.

---

## 3. Supabase project boundary

### 3.1 Dedicated project

Target project identity candidate:

`84K-OS / yuanli-invest-runtime`

YQS0 explicitly rejects colocating Yuanli Investment runtime inside `yuanli-health`.

Reason:

- different sovereign domain and RLS model;
- different blast radius;
- independent schema migrations and recovery policy;
- investment runtime may hold manager/market/vendor evidence metadata that must not share an application security boundary with health data.

Creation of the project is **not authorized by YQS0 candidate creation**. Project creation is a post-acceptance implementation action.

### 3.2 Production readiness

A Free-plan project may be used for disposable development experiments only. Before the database becomes a durable PIT/replay/settlement truth store, the implementation gate must explicitly review backup, PITR, compute, Storage backup and availability requirements.

---

## 4. Eight-schema kernel

YQS0 freezes exactly eight application schemas:

```text
core
  identity + thesis + expression state

evidence
  source provenance + claims + support/counterevidence graph

pit
  bitemporal observations + features + lineage

quant
  factor definitions + point-in-time factor health

runtime
  immutable run receipts for external/agent computation

replay
  preregistered cases + future settlement

governance
  append-first operational authority/review events

projection
  non-authoritative human/application read models
```

`public` is not an application-domain schema for YQS0. Any API-exposed convenience surface must be an explicitly reviewed view/RPC projection, not an uncontrolled table dump.

The machine-readable inventory is frozen in `YQS0-OBJECT-INVENTORY-v0.1.json`.

---

## 5. Eighteen core objects

YQS0 freezes eighteen logical objects and no more at the architecture gate:

### core (4)

1. `core.research_targets`
2. `core.engine_theses`
3. `core.position_passports`
4. `core.book_states`

These are operational projections/state records governed by ME1 semantics. Supabase storage of an object does not elevate it above its upstream authority.

### evidence (4)

5. `evidence.sources`
6. `evidence.source_snapshots`
7. `evidence.claims`
8. `evidence.evidence_links`

`evidence_links` types support and counterevidence relationships without making machine retrieval equal to evidence admission.

### pit (3)

9. `pit.observations`
10. `pit.feature_records`
11. `pit.data_lineage`

The PIT subsystem is revision-aware and append-first. A latest-value overwrite cannot erase the historical value that was knowable at a prior cutoff.

### quant (2)

12. `quant.factor_definitions`
13. `quant.factor_states`

Factor formulas/versions are identity objects; factor health is a time-indexed state. Nominal factor count is not treated as independent alpha breadth.

### runtime (1)

14. `runtime.run_receipts`

A run receipt records the exact code/input/runtime/output identity of a computation. The queue itself is infrastructure (`pgmq`/Supabase Queues), not a new research-domain authority object.

### replay (2)

15. `replay.replay_cases`
16. `replay.settlements`

A replay case freezes T0, knowledge cutoff, hypotheses, allowed evidence policy, baseline/ablation references and output contract before outcomes are revealed. Settlement evaluates history but never rewrites the frozen historical package.

### governance (1)

17. `governance.authority_events`

This is an operational governance ledger. It may record review/accept/reject/project/sync events but does not replace immutable GitHub Human Acceptance / Merge receipts.

### projection (1)

18. `projection.change_queue`

The Change Queue is a non-authoritative human read model: what changed, why it matters, which thesis may be affected, and whether Human Review is required.

---

## 6. PIT Law

YQS0 adopts four distinct clocks inherited from ME1 semantics:

```text
recorded_at
known_as_of
knowledge_cutoff
replay_cutoff
```

and adds source/data clocks where applicable:

```text
event_time
period_end
published_at
available_at
captured_at
```

Core law:

```text
known_as_of <= knowledge_cutoff <= replay_cutoff
```

For a replay, an observation or evidence claim is eligible only if its historically knowable timestamp is on or before the frozen knowledge cutoff. `captured_at` is never evidence that something was knowable earlier.

Historical reconstruction is permitted only with explicit reconstruction provenance, source publication/availability evidence, immutable locator/hash and revision lineage. It may reconstruct the historical information set; it may not substitute today’s revised latest value for the historical version.

Replay access should be mediated by PIT-safe SQL functions/RPCs rather than direct unrestricted table queries.

The full machine-checkable law is in `YQS0-PIT-LAW-v0.1.json`.

---

## 7. Authority and RLS model

YQS0 freezes six application roles:

```text
principal
researcher
quant_worker
reviewer
viewer
system
```

Key rules:

- `viewer` reads projection surfaces only.
- `researcher` may create candidate operational research state but cannot create Canon authority.
- `quant_worker` receives only eligible job inputs and may write typed run outputs/receipts; it cannot write authority events.
- `reviewer` may append operational review events; that event does not itself merge or mutate GitHub Canon.
- `system` performs ingestion, queues, projections and Canon sync with least privilege; service-role credentials never appear in a client.
- `principal` is the highest human application role but still cannot bypass the separate GitHub merge/acceptance laws by direct database mutation.

The full matrix is in `YQS0-RLS-AUTHORITY-MATRIX-v0.1.json`.

---

## 8. Quant Worker Contract

Supabase is the **Control Plane**; quant workers are the **Compute Plane**.

```text
Supabase Queue / Runtime Request
          |
          v
External Quant Worker
Python / DuckDB / Polars / NumPy / ML
          |
          v
Typed Output + Run Receipt
          |
          v
Supabase candidate state / replay result
```

Each job must carry:

- stable `job_id` and idempotency key;
- `job_type` and output schema identity;
- `canon_ref` and `code_ref`;
- exact input manifest + content hashes;
- PIT/replay context when applicable;
- requested capability/model profile;
- explicit runtime/resource policy.

Each run receipt must return:

- code commit/container/runtime fingerprint;
- input manifest/hash;
- start/end timestamps;
- deterministic seed where relevant;
- output object refs and hashes;
- metrics/warnings;
- failure state;
- worker identity;
- authority declaration proving the worker did not grant capital/live-execution authority.

Unknown schema, unresolved engine identity, missing PIT cutoff or mismatched input hash fails closed.

The machine-readable contract is in `YQS0-QUANT-WORKER-CONTRACT-v0.1.json`.

---

## 9. Data placement

YQS0 freezes a three-temperature data strategy.

### Hot｜Supabase Postgres

- current Research State;
- evidence metadata/claims;
- PIT metadata and selected observations/features;
- factor definitions/states;
- replay cases/settlements;
- run receipts;
- governance ledger;
- application projections.

### Warm｜Parquet / object storage

- larger daily market histories;
- feature snapshots;
- fundamental/industry history;
- replay datasets too large for row-oriented hot storage.

### Cold｜Local/NAS immutable evidence vault

- original PDFs/web captures/vendor exports;
- large tick/minute raw feeds;
- restricted third-party data;
- archives requiring independent backup.

Supabase Storage may be an online object layer, but it is not the sole sovereign archive. Database backup/PITR does not by itself constitute object-storage backup.

---

## 10. API and agent boundary

Agent/LLM access is through narrow, typed RPC/tool contracts.

Preferred pattern:

```text
Agent
  -> authorized tool/RPC
  -> PIT/evidence filter
  -> typed rows/state
  -> structured candidate output
  -> runtime.run_receipts
```

Disallowed pattern:

```text
Agent
  -> unrestricted SELECT/UPDATE across application schemas
```

LLMs organize evidence, generate mechanism hypotheses, identify conflicts/falsifiers and synthesize candidate state. Deterministic numeric calculations stay in quant workers.

---

## 11. GitHub ↔ Supabase synchronization law

### GitHub → Supabase

Accepted Canon/contracts/schema metadata may be projected into Supabase by a versioned sync process. Every sync must record source commit SHA and content hash.

### Supabase → GitHub

Runtime findings may create **proposal packages only**. No database trigger, agent or worker may directly mutate accepted Canon or create an acceptance receipt.

```text
Supabase candidate finding
        -> proposal artifact
        -> Human Review
        -> GitHub PR
        -> GitHub acceptance / merge gates
        -> later Canon projection back to Supabase
```

This is the central dual-authority boundary:

> Supabase has operational state authority; GitHub retains normative Canon authority.

---

## 12. Security and privacy baseline

YQS0 requires the implementation phase to provide:

- RLS on every application table exposed through Data API;
- no service-role key in frontend/client code;
- least-privilege database roles for workers;
- Vault/secrets for server-side credentials;
- explicit network/SSL hardening review before production;
- auditability of authority events and run receipts;
- restricted schemas/data classes for third-party manager evidence;
- no health-domain data in the investment project.

This architecture does not authorize importing Zhuoliqi proprietary formulas or restricted raw third-party datasets into a public repository or broadly exposed table.

---

## 13. Architecture success criteria

YQS0 may become `candidate_ready_for_human_review` only if machine validation confirms:

1. exactly eight schemas are frozen;
2. exactly eighteen core objects are frozen;
3. every schema has at least one object;
4. no YQS0 object claims Canon authority;
5. PIT law distinguishes `recorded_at`, `known_as_of`, `knowledge_cutoff`, `replay_cutoff`;
6. historical reconstruction cannot use revised latest values without lineage;
7. the RLS matrix prevents `quant_worker` and `system` from granting human authority;
8. the Quant Worker Contract preserves external heavy compute and run receipts;
9. live execution, trading authority, portfolio weight and position sizing remain false;
10. ME2-ME5 and operational-canon switch remain unauthorized.

Human acceptance token reserved for a later explicit decision:

`ACCEPT_YQS0_SUPABASE_SOVEREIGN_RESEARCH_KERNEL_ARCHITECTURE`

Acceptance would approve the architecture only. It would **not** authorize merge, Supabase project creation, production credentials, migrations, data import, operational cutover or live execution.
