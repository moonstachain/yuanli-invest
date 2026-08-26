# YQS0 Supabase Sovereign Research Kernel Design

## Goal

Freeze a minimal, machine-checkable architecture for using Supabase as Yuanli Quant's operational research kernel while preserving GitHub Canon authority, ME1 state semantics, PIT integrity and the external heavy-compute boundary.

## Existing authority to preserve

- `docs/architecture/YUANLI-QUANT-AI-EQUITY-RESEARCH-SYSTEM-v1.md` remains the Q0 architecture lineage and already freezes point-in-time, evidence-before-opinion, state-not-score, deterministic-quant/probabilistic-reasoning and no-live-execution principles.
- ME1 is already accepted/merged and owns the semantic chain `ResearchTarget -> EngineThesis -> PositionPassport -> BookState@PIT`.
- `docs/architecture/CANON-STATUS.json` states that `moonstachain/quant-workspace` remains A9 operational canon and that the switch is not authorized.
- YQS0 is a parallel infrastructure/runtime architecture candidate. It is not ME2 and cannot authorize ME2-ME5.

## Design decisions

### D1. Control plane / compute plane split

Supabase owns operational state, metadata, scheduling interfaces, replay definitions, governance ledger and projections. External workers own factor computation, backtest, replay compute, ML and large numerical workloads.

### D2. Dual authority

- GitHub: normative authority for law, accepted schemas/contracts, Canon, acceptance and merge receipts.
- Supabase: operational authority for current state, runtime receipts, replay/settlement records and non-authoritative projections.

Supabase-to-GitHub is proposal-only until Human Review and normal GitHub gates occur.

### D3. Dedicated Supabase project

Investment and health are separate sovereign domains. Target project candidate is `84K-OS/yuanli-invest-runtime`; YQS0 does not create it.

### D4. Eight schemas

Exactly:

1. `core`
2. `evidence`
3. `pit`
4. `quant`
5. `runtime`
6. `replay`
7. `governance`
8. `projection`

No application-domain table is frozen under `public`.

### D5. Eighteen logical objects

Exactly:

- `core.research_targets`
- `core.engine_theses`
- `core.position_passports`
- `core.book_states`
- `evidence.sources`
- `evidence.source_snapshots`
- `evidence.claims`
- `evidence.evidence_links`
- `pit.observations`
- `pit.feature_records`
- `pit.data_lineage`
- `quant.factor_definitions`
- `quant.factor_states`
- `runtime.run_receipts`
- `replay.replay_cases`
- `replay.settlements`
- `governance.authority_events`
- `projection.change_queue`

This is an architecture inventory, not yet SQL DDL.

### D6. PIT enforcement

Required clocks are `recorded_at`, `known_as_of`, `knowledge_cutoff`, `replay_cutoff`, with `known_as_of <= knowledge_cutoff <= replay_cutoff`.

Replay is fail-closed when knowability is not established. Historical reconstruction must preserve publication/availability evidence and revision lineage. Current revised values cannot silently replace historical versions.

### D7. RLS roles

Exactly:

- `principal`
- `researcher`
- `quant_worker`
- `reviewer`
- `viewer`
- `system`

No database role can create a GitHub acceptance receipt or merge. `quant_worker` and `system` cannot act as Human Review identities.

### D8. Quant worker contract

External workers consume scoped jobs, record immutable run receipts, and fail closed on unknown schema, unresolved authority, PIT failure or input hash mismatch. Workers cannot write human authority or live execution.

### D9. Data temperature

- Hot: Supabase Postgres operational state and metadata.
- Warm: Parquet/object storage for larger histories and feature datasets.
- Cold: Local/NAS immutable restricted/raw evidence archive.

Supabase Storage is not the sole sovereign backup for important raw evidence.

### D10. No implementation authority in YQS0

YQS0 candidate creation does not authorize:

- Supabase project creation;
- plan upgrade;
- credentials;
- migrations;
- data import;
- Edge Function deployment;
- Quant Worker connection;
- A9 operational-canon switch;
- Registry/evidence/outcome promotion;
- portfolio sizing or live execution;
- ME2-ME5/QXM3.

## Machine qualification

A validator must fail unless:

- eight exact schema names exist;
- eighteen unique objects exist;
- all eight schemas are represented;
- all objects have `canon_authority=false`;
- PIT clocks and ten laws are present;
- the RLS role set is exact;
- `quant_worker` and `system` hard-deny human approval/live execution;
- worker contract says `heavy_compute_in_edge_functions=false` and `live_execution_authorized=false`;
- YQS0 state keeps all implementation/successor authority false.

## Deliverables

- architecture narrative;
- object inventory;
- PIT law;
- RLS authority matrix;
- Quant Worker contract;
- stage state;
- Human Review card;
- validator + unit test;
- implementation plan for YQS1;
- draft PR for Human Review.
