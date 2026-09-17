# YIIW-G0｜Gold Evidence Spine × Production Backend Skeleton

Status: **DESIGN_ACCEPTED_PENDING_WRITTEN_SPEC_HUMAN_REVIEW**  
Design acceptance: user approved in chat on 2026-09-17  
Upstream baseline: `origin/main@152c7a2b87ea5d5a196c129d82ab5a4eb18accc7`  
Scope: one GOLD vertical slice only.  
Out of scope: Temporal claim lifecycle, Next.js rewrite, FactSet live integration, portfolio sizing, trading, broker/VeighNa execution, automatic Canon promotion.

---

## 0｜Mother Question

Can one real Gold market fact move from provider reality to the human screen through a single governed spine:

`Provider → Raw Evidence → PIT Observation → Deterministic Analytics → GoldState@PIT → Research API → Workbench Readback`

while preserving provenance, point-in-time semantics, model reproducibility, authority boundaries and end-to-end auditability?

Success is not “the code runs.” Success is a **Genesis Reality Proof** in which a displayed Gold state can be traced back to the exact provider receipt and deterministically reproduced from admitted inputs.

---

## 1｜Controlling Principles

1. `Raw Data != Evidence`.
2. `Evidence != Truth`.
3. `Generated != Authorized`.
4. `Price Up != Thesis Proven`.
5. `Learning != Canon`.
6. `UI never owns Truth`.
7. `MCP never owns Truth`.
8. `Every State must be Point-in-Time`.
9. `Every deterministic analytic must be reproducible from versioned inputs`.
10. `Research pass != Capital pass`.

The implementation must preserve current Yuanli authority boundaries: research only; no capital, sizing, execution, broker, VeighNa or Canon authority.

---

## 2｜Existing Assets Reused, Not Replaced

YIIW-G0 is additive. It must reuse the existing operational estate instead of creating a parallel truth stack.

### Existing evidence/PIT substrate

Reuse:

- `evidence.sources`
- `evidence.source_snapshots`
- `pit.observations`
- `runtime.reality_gate_runs`
- private Supabase Storage bucket pattern (`ymq4-raw-evidence`)
- service-role-only ingest/readback RPC pattern

These already establish the important distinction between raw source snapshot and PIT observation.

### Existing sovereign runtime substrate

Reuse:

- `evidence.claim_receipts`
- `runtime.agent_runs`
- `runtime.research_projections`
- `runtime.learning_deltas`
- `runtime/ymq_gateway/context_compiler.py`

YIIW-G0 does not alter their existing authority contracts.

### Existing Gold runtime

Reuse and progressively wrap:

- `scripts/ymq_gold2_live_shadow.py`
- `scripts/ymq_gold2_compiler.py`
- `scripts/ymq_gold2_property_drift.py`
- `scripts/ymq_gold2_learning_live.py`
- `config/ymq_gold2/*`

The G6/G7 live shadow remains operational throughout G0 unless a separately approved production migration is required.

---

## 3｜Architectural Decision: One Spine, Three Stores

YIIW-G0 uses three distinct persistence roles.

### A. Control Plane — Supabase PostgreSQL

Stores identity, lineage, model-run metadata, research state references, authority and audit metadata.

Postgres answers:

- What is this object?
- Which model/source produced it?
- What was known at the time?
- Which version produced it?
- Who or what is allowed to mutate it?

### B. Raw Evidence Store — private object storage

Stores immutable raw provider payloads and document bodies outside Git.

Required properties:

- private bucket only;
- content-addressed or hash-verifiable path;
- SHA-256 recorded in Postgres;
- no public policy;
- no secret or raw payload committed to Git.

### C. Quant History — Parquet + DuckDB

Stores/replays time-series and derived research panels efficiently.

G0 uses this only where it materially simplifies PIT replay or deterministic compilation. It must not create a second authority database. The metadata/lineage authority remains Postgres/GitHub.

---

## 4｜Yuanli Investment Metamodel v0.1 Scope

G0 freezes only the minimum semantic kernel needed for the Evidence Spine.

### Objects admitted in G0

- `SourceReceipt`
- `SourceSnapshot`
- `Evidence`
- `Entity`
- `Metric`
- `Instrument`
- `ModelDefinition`
- `ModelRun`
- `ResearchTarget`
- `StateAtPIT`
- `LineageRef`
- `AuthorityRef`

### Explicitly deferred

- Claim lifecycle
- Falsifier workflow
- Settlement workflow
- Learning admission
- Position / portfolio objects
- trading / execution objects

Those belong to later YIIW gates.

### Contract implementation

Semantic authority chain:

`LinkML → JSON Schema → Pydantic runtime model → API validation`

Postgres is persistence, not semantic authority. GitHub holds the versioned contract.

Existing JSON schemas remain immutable historical contracts. G0 adds successor contracts instead of rewriting old schema identity in place.

---

## 5｜Gold Evidence Object

A successful provider observation must compile into an Evidence object with at least:

```json
{
  "evidence_id": "EVD-GOLD-...",
  "provider": "WIND",
  "source_snapshot_id": "...",
  "metric_id": "GOLD_SPOT_USD_OZ",
  "entity_id": "GOLD",
  "instrument_id": "XAU_SPOT",
  "value": 4328.2,
  "unit": "USD/OZ",
  "observed_at": "...",
  "known_as_of": "...",
  "retrieved_at": "...",
  "raw_sha256": "...",
  "authority": "REALITY_EVIDENCE",
  "quality_state": "VALID"
}
```

The three time concepts are distinct and mandatory:

- `observed_at` — when the economic/market observation applies;
- `known_as_of` — earliest time the system may legally know/use it in PIT research;
- `retrieved_at` — when Yuanli actually fetched it.

No compiler may silently collapse these fields.

---

## 6｜Provider Ingestion Flow

For the G0 Gold slice, Wind remains the live provider already proven in GOLD2.

Flow:

`Wind CLI response`
→ capture raw response privately
→ calculate SHA-256
→ persist immutable raw object
→ register `source_snapshot`
→ resolve provider code to Yuanli `Metric/Instrument`
→ normalize timestamps/units
→ write `pit.observation`
→ emit normalized `Evidence`

Provider authority remains `EVIDENCE_ONLY`.

If identity, unit, timestamp or PIT semantics cannot be resolved, the ingest must fail closed with a typed reason; it must not fabricate missing semantics.

---

## 7｜Registry Design

G0 introduces/normalizes six registries as machine-readable contracts:

1. Entity Registry
2. Metric Registry
3. Instrument Registry
4. Source Registry
5. Model Registry
6. Authority Registry / policy references

Example provider mapping:

`WIND:S0031645 → Metric:GOLD_SPOT_USD_OZ → Instrument:XAU_SPOT → ResearchTarget:GOLD`

A provider code is not the canonical metric identity.

Registry records must support:

- canonical id;
- aliases/provider mappings;
- unit;
- frequency;
- PIT semantics;
- source authority ceiling;
- transform rules;
- deprecation/successor references.

---

## 8｜Deterministic Analytics Registry

Existing GOLD2 analytics are progressively registered rather than rewritten.

Genesis ModelDefinitions:

- `GOLD_STATE_COMPILER`
- `GOLD_PROPERTY_DRIFT`
- `GOLD_EXPECTATION_REALITY`
- `GOLD_VALUATION_LENS`
- `GOLD_STATE_DELTA`

Each `ModelRun` must preserve:

- `model_id`
- `model_version`
- `code_sha`
- `parameter_hash`
- `input_evidence_ids`
- `known_as_of`
- `started_at/completed_at`
- `output_hash`
- `run_status`

A displayed state must be reproducible from the same versioned inputs.

LLMs are prohibited from performing these deterministic calculations in the authoritative path.

---

## 9｜GoldState@PIT

G0 does not invent a new investment thesis ontology. It produces a research state projection compatible with current GOLD2 and ME1 boundaries.

Minimum fields:

- `target_id = GOLD`
- `as_of`
- `knowledge_cutoff`
- `evidence_refs`
- `model_run_refs`
- `property_drift_state`
- `expectation_reality_state`
- `valuation_state`
- `research_state`
- `lifecycle_state`
- `unknowns`
- `authority`
- `state_hash`

The state is append-first and Point-in-Time. A later run may supersede a prior projection but may not rewrite what was known in history.

---

## 10｜Research API v0.1

The first API surface is read-focused and narrow.

Required endpoints:

- `GET /v1/targets/gold/state?as_of=`
- `GET /v1/targets/gold/evidence?as_of=`
- `GET /v1/evidence/{evidence_id}`
- `GET /v1/model-runs/{model_run_id}`
- `GET /v1/lineage/{object_id}`
- `GET /v1/system/health`

Implementation target: FastAPI + Pydantic contracts.

The API is the only supported application-facing entry point for the G0 slice. Frontend, future MCP tools and future Copilot must not query operational tables directly.

No generic `execute_sql`, `query_postgres`, or unrestricted data-write API is allowed.

---

## 11｜Workbench Readback

G0 intentionally does not rewrite the full legacy `macro.html` frontend in Next.js.

The initial proof uses a thin Workbench adapter/projection so the existing human experience can read from the new Research API.

The Gold surface must display at least:

- current Gold price/state;
- Real Yield and DXY inputs;
- PIT/as-of context;
- source freshness;
- model version/status;
- evidence links.

### Evidence Drawer

Clicking a displayed metric/state must expose:

- provider;
- canonical metric identity;
- raw snapshot hash;
- observed / known-as-of / retrieved timestamps;
- source freshness;
- transform/normalization rule;
- consuming model run;
- alternative source/conflict state if any;
- authority ceiling.

The UI is a projection only; it must contain no hidden trading/advice logic.

---

## 12｜Failure Semantics

G0 must fail closed with typed states rather than silent fallback.

Minimum taxonomy:

- `SOURCE_UNAVAILABLE`
- `AUTH_REJECTED`
- `QUOTA_OR_CREDIT_BLOCK`
- `ENTITY_UNRESOLVED`
- `METRIC_UNRESOLVED`
- `UNIT_MISMATCH`
- `PIT_MISSING`
- `PIT_FUTURE_LEAK`
- `RAW_PERSIST_FAILED`
- `SCHEMA_INVALID`
- `MODEL_INPUT_INCOMPLETE`
- `MODEL_REPRODUCIBILITY_FAIL`
- `LINEAGE_INCOMPLETE`
- `PROJECTION_STALE`

A failure in downstream projection must not mutate or invalidate an already admitted raw evidence object.

---

## 13｜Security and Authority

G0 preserves the following hard denials:

- capital authorization: false
- sizing authorization: false
- execution authorization: false
- broker action: false
- VeighNa authorization: false
- accepted learning authorization: false unless governed elsewhere
- automatic asset promotion: false
- automatic Canon promotion: false

Secrets never enter Git, receipts, browser payloads or model context.

Operational database schemas remain service-role/server-side. Public/UI clients receive only narrow API projections.

---

## 14｜Testing Strategy

Implementation must be TDD-first.

### Contract tests

Validate LinkML/JSON Schema/Pydantic equivalence for the G0 object set.

### PIT tests

Prove:

- no `known_as_of > task_as_of` evidence can enter state compilation;
- observed/known/retrieved semantics do not collapse;
- revised observations preserve prior PIT history.

### Lineage tests

Given a `StateAtPIT`, the system must traverse:

`State → ModelRun → Evidence → PIT Observation → SourceSnapshot → Raw Hash`.

### Determinism tests

Same model version + same parameters + same evidence ids must produce the same output hash.

### Governance tests

Prove that no G0 path grants capital/execution/Canon authority and that UI/MCP do not have direct DB write authority.

### Reality test

One live/private Gold observation must complete the full readback chain without exposing secrets or raw provider payload in Git.

---

## 15｜Genesis Reality Proof Acceptance

G0 is complete only when one real Gold fact passes all six acceptance gates:

1. `VALUE_MATCH` — Workbench value matches admitted provider evidence.
2. `PIT_MATCH` — as-of/known-as-of semantics are valid with no future leakage.
3. `LINEAGE_COMPLETE` — UI state traces to raw source hash.
4. `MODEL_REPRODUCIBLE` — deterministic state reproduces from exact inputs/version.
5. `AUTHORITY_VALID` — evidence/provider/model/UI authority ceilings are preserved.
6. `UI_READBACK_MATCH` — Workbench reads the same Research API object, not a parallel calculation.

Machine qualification must produce a receipt covering these six gates.

---

## 16｜Explicit Non-Goals for G0

G0 must not expand into:

- Next.js full-site rewrite;
- live FactSet procurement/integration;
- 20-provider source fabric;
- portfolio optimization;
- automated trading;
- Temporal claim lifecycle;
- Kafka/Kubernetes platform engineering;
- unrestricted agent mesh;
- full historical migration;
- redesign of GOLD2 scientific conclusions.

Gold remains the single Genesis Asset for this slice.

---

## 17｜Expected Implementation Layout

The implementation plan may refine exact filenames, but responsibility boundaries should remain:

```text
packages/contracts/linkml/        # semantic source contract
packages/contracts/schemas/yiiw/  # generated/frozen JSON schemas
runtime/yiiw/                     # Pydantic models + compiler/services
runtime/yiiw/providers/           # Wind adapter boundary
runtime/yiiw/analytics/           # deterministic Gold analytics wrappers
api/yiiw/                         # FastAPI read surface
supabase/migrations/              # additive control-plane schema/RPC
scripts/                          # qualification/reality proof runners
tests/                            # TDD + governance + replay tests
docs/architecture/yiiw/           # receipts/review cards
```

Existing GOLD2 files remain authoritative for their current accepted semantics unless explicitly superseded through a later Human Gate.

---

## 18｜Program Sequencing After G0

Only after the G0 Truth Spine is accepted:

- `YIIW-G1｜Claim Lifecycle × Temporal × Settlement`
- `YIIW-G2｜Context Compiler × GBrain × MCP × Copilot`
- `YIIW-G3｜Next.js Research Workbench`
- `YIIW-G4｜Cross-Asset Replication`
- `YIIW-G5｜14-Day Human × Machine Blind Test`

This sequencing protects the program from building interaction or agent complexity on top of an unproven truth substrate.

---

## 19｜Human Review Contract

Before implementation planning, Human Review should confirm all of the following:

1. One Gold vertical slice is sufficient for G0.
2. Existing Supabase evidence/PIT tables are reused rather than replaced.
3. LinkML is semantic authority; Pydantic is runtime validation; Postgres is persistence.
4. Raw provider payloads remain private object-store evidence and out of Git.
5. Research API is the only supported application-facing entry point.
6. Existing `macro.html` is adapted for readback before any full Next.js rewrite.
7. Temporal is deferred to G1.
8. No capital, sizing, trading, broker, VeighNa or Canon authority is granted.
9. Existing GOLD2 scientific conclusions are preserved; G0 hardens lineage and serving, not the thesis result.
10. Completion requires the six-part Genesis Reality Proof, not a code-complete claim.

If accepted, the next step is a detailed implementation plan followed by isolated TDD execution.
