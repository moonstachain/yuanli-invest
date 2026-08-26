# YQS1 Supabase Research Kernel Schema & RLS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a local, testable Supabase/Postgres kernel for the eight YQS0 schemas and eighteen objects, with PIT-safe access, RLS, append-first governance, and no cloud cutover or live-execution authority.

**Architecture:** GitHub remains normative authority and contains migrations/tests. Supabase/Postgres is the operational state kernel. Heavy quant remains external; this plan implements only the database/control-plane kernel and its test harness.

**Tech Stack:** PostgreSQL 17-compatible SQL, Supabase CLI, pgTAP, RLS, pgvector/pgmq/pg_cron only where explicitly required, Python/pytest only for repository-level contract validation.

**Spec:** `docs/superpowers/specs/2026-08-26-yqs0-supabase-sovereign-research-kernel-design.md`

## Global Constraints

- Exactly eight application schemas: `core`, `evidence`, `pit`, `quant`, `runtime`, `replay`, `governance`, `projection`.
- Exactly eighteen YQS0 logical objects; implementation may add indexes, functions, types and queues but may not invent a nineteenth domain table without a new Human Gate.
- `ResearchTarget != EngineThesis != PositionPassport != BookState`.
- `known_as_of <= knowledge_cutoff <= replay_cutoff` for replay-eligible records.
- Replay direct unrestricted application-table access is prohibited.
- All API-exposed tables use RLS and default-deny grants.
- `quant_worker` and `system` cannot append human approval events.
- GitHub Canon cannot be mutated by a database trigger/function.
- No portfolio weight, position sizing, buy/sell/hold or live execution.
- No cloud project creation or production data import is part of this plan.

---

### Task 1: Bootstrap local Supabase kernel

**Files:**
- Create: `supabase/config.toml`
- Create: `supabase/migrations/20260826000100_yqs1_extensions_and_schemas.sql`
- Create: `supabase/tests/yqs1_01_schema_contract_test.sql`

**Interfaces:**
- Consumes: YQS0 eight-schema inventory.
- Produces: local Supabase project with eight empty application schemas and required extension namespaces.

- [ ] **Step 1: Write the failing pgTAP schema test**

```sql
begin;
select plan(10);

select has_schema('core');
select has_schema('evidence');
select has_schema('pit');
select has_schema('quant');
select has_schema('runtime');
select has_schema('replay');
select has_schema('governance');
select has_schema('projection');

select isnt(
  (select count(*)::text from pg_tables where schemaname = 'public'),
  null,
  'public may exist as platform schema but is not a YQS0 domain schema'
);

select is(
  (select count(*)::int from pg_namespace where nspname in ('core','evidence','pit','quant','runtime','replay','governance','projection')),
  8,
  'exactly eight YQS application schemas exist'
);

select * from finish();
rollback;
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `supabase start && supabase test db supabase/tests/yqs1_01_schema_contract_test.sql`

Expected: FAIL because the eight schemas do not exist.

- [ ] **Step 3: Create the schema migration**

```sql
create schema if not exists core;
create schema if not exists evidence;
create schema if not exists pit;
create schema if not exists quant;
create schema if not exists runtime;
create schema if not exists replay;
create schema if not exists governance;
create schema if not exists projection;

create extension if not exists pgcrypto with schema extensions;
create extension if not exists vector with schema extensions;
create extension if not exists pgmq;
create extension if not exists pg_cron;
```

`supabase/config.toml` must use local defaults and must not contain cloud project refs or secrets.

- [ ] **Step 4: Run test and lint**

Run:

```bash
supabase db reset
supabase test db supabase/tests/yqs1_01_schema_contract_test.sql
supabase db lint --level error
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add supabase/config.toml supabase/migrations/20260826000100_yqs1_extensions_and_schemas.sql supabase/tests/yqs1_01_schema_contract_test.sql
git commit -m "feat(yqs1): bootstrap sovereign research kernel schemas"
```

---

### Task 2: Implement the eighteen core tables/views

**Files:**
- Create: `supabase/migrations/20260826000200_yqs1_core_objects.sql`
- Create: `supabase/tests/yqs1_02_object_inventory_test.sql`

**Interfaces:**
- Consumes: eight schemas from Task 1 and `YQS0-OBJECT-INVENTORY-v0.1.json`.
- Produces: eighteen domain objects with stable IDs, timestamps and authority-safe columns.

- [ ] **Step 1: Write object inventory tests**

The pgTAP test must assert presence of exactly these table/view names:

```text
core.research_targets
core.engine_theses
core.position_passports
core.book_states
evidence.sources
evidence.source_snapshots
evidence.claims
evidence.evidence_links
pit.observations
pit.feature_records
pit.data_lineage
quant.factor_definitions
quant.factor_states
runtime.run_receipts
replay.replay_cases
replay.settlements
governance.authority_events
projection.change_queue
```

It must additionally assert that no table named `orders`, `trades`, `positions`, `broker_accounts` or `executions` exists in the eight schemas.

- [ ] **Step 2: Verify inventory test fails**

Run: `supabase test db supabase/tests/yqs1_02_object_inventory_test.sql`

Expected: FAIL because the objects do not exist.

- [ ] **Step 3: Implement IDs and ME1 references**

Use UUID primary keys generated by `gen_random_uuid()` for operational rows, while preserving upstream stable string IDs (`target_id`, `engine_thesis_id`, `position_passport_id`, `book_state_id`) as unique columns.

Required ME1 foreign-key direction:

```text
core.engine_theses.target_id -> core.research_targets.target_id
core.position_passports.engine_thesis_id -> core.engine_theses.engine_thesis_id
core.position_passports.target_id -> core.research_targets.target_id
```

`core.book_states` stores membership as JSONB only in YQS1 if the accepted ME1 membership payload is projected atomically; do not invent a nineteenth membership table.

- [ ] **Step 4: Implement evidence, PIT, quant, runtime, replay and governance tables**

Minimum mandatory columns:

```text
evidence.source_snapshots: source_snapshot_id, source_id, locator, content_hash, published_at, available_at, captured_at, access_classification
pit.observations: observation_id, subject_id, metric_id, event_time, period_end, published_at, available_at, captured_at, known_as_of, value_json, unit, provider, source_snapshot_id, revision_id, previous_revision_id, quality_state
pit.feature_records: feature_record_id, feature_id, subject_id, as_of, known_as_of, knowledge_cutoff, formula_version, code_ref, input_manifest_hash, value_json, unit, quality_state
pit.data_lineage: lineage_id, parent_ref, child_ref, transformation_ref, created_at
quant.factor_definitions: factor_id, version, family, economic_hypothesis, universe_json, domain, horizon, formula_ref, created_at
quant.factor_states: factor_state_id, factor_id, factor_version, as_of, known_as_of, state_json, created_at
runtime.run_receipts: run_receipt_id, job_id, job_type, started_at, ended_at, worker_identity, code_ref, runtime_fingerprint, input_manifest_hash, output_refs_json, output_hashes_json, status, warnings_json, authority_declaration_json
replay.replay_cases: replay_case_id, t0, knowledge_cutoff, replay_cutoff, hypotheses_json, allowed_evidence_policy_json, baseline_refs_json, ablation_refs_json, output_schema_id, frozen_at
replay.settlements: settlement_id, replay_case_id, settlement_as_of, outcome_json, attribution_json, verdict, created_at
governance.authority_events: authority_event_id, event_type, actor_id, actor_role, object_ref, decision_json, source_ref, created_at
```

- [ ] **Step 5: Implement `projection.change_queue` as a view**

The view may consume operational states but must expose `projection_only=true` as a literal column and must not be directly writable.

- [ ] **Step 6: Run tests**

Run:

```bash
supabase db reset
supabase test db supabase/tests/yqs1_01_schema_contract_test.sql
supabase test db supabase/tests/yqs1_02_object_inventory_test.sql
supabase db lint --level error
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add supabase/migrations/20260826000200_yqs1_core_objects.sql supabase/tests/yqs1_02_object_inventory_test.sql
git commit -m "feat(yqs1): add sovereign research kernel objects"
```

---

### Task 3: Enforce PIT-safe replay access

**Files:**
- Create: `supabase/migrations/20260826000300_yqs1_pit_safe_rpc.sql`
- Create: `supabase/tests/yqs1_03_pit_law_test.sql`

**Interfaces:**
- Consumes: `pit.observations`, `pit.feature_records`, replay cutoffs.
- Produces: `pit.get_observations_as_of(...)` and `pit.get_features_as_of(...)` RPCs.

- [ ] **Step 1: Write failing PIT tests**

Create fixtures where one observation is knowable before cutoff and a revised observation becomes knowable after cutoff. Assert the RPC returns only the historically eligible revision.

Also assert records with null `known_as_of` are excluded from replay-safe results.

- [ ] **Step 2: Run test and verify failure**

Run: `supabase test db supabase/tests/yqs1_03_pit_law_test.sql`

Expected: FAIL because PIT RPCs do not exist.

- [ ] **Step 3: Implement PIT RPCs**

Function signatures:

```sql
pit.get_observations_as_of(
  p_subject_id text,
  p_metric_id text,
  p_knowledge_cutoff timestamptz,
  p_replay_cutoff timestamptz
)

pit.get_features_as_of(
  p_subject_id text,
  p_feature_id text,
  p_knowledge_cutoff timestamptz,
  p_replay_cutoff timestamptz
)
```

Both functions must enforce:

```text
known_as_of <= p_knowledge_cutoff <= p_replay_cutoff
```

and select the latest eligible revision **within the historical cutoff**, never the latest current revision.

Functions must set an explicit safe `search_path` and receive only narrowly scoped `EXECUTE` grants.

- [ ] **Step 4: Add append-only revision trigger**

Reject updates to historical PIT identity/value columns after insertion. Corrections must insert a new `revision_id` linked with `previous_revision_id`.

- [ ] **Step 5: Run tests and lint**

Run:

```bash
supabase db reset
supabase test db supabase/tests/yqs1_03_pit_law_test.sql
supabase db lint --level error
```

Expected: PASS, including a future-leakage negative case.

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260826000300_yqs1_pit_safe_rpc.sql supabase/tests/yqs1_03_pit_law_test.sql
git commit -m "feat(yqs1): enforce point-in-time replay access"
```

---

### Task 4: Implement role grants and RLS

**Files:**
- Create: `supabase/migrations/20260826000400_yqs1_rls.sql`
- Create: `supabase/tests/yqs1_04_rls_authority_test.sql`

**Interfaces:**
- Consumes: YQS0 six-role authority matrix.
- Produces: default-deny table privileges, RLS policies and narrow RPC execution rights.

- [ ] **Step 1: Write failing authorization tests**

Tests must prove:

- viewer cannot select `core.engine_theses` directly;
- viewer can read the allowed `projection.change_queue` surface;
- quant worker cannot insert `governance.authority_events`;
- system cannot append an event with `actor_role in ('principal','reviewer')`;
- researcher cannot write `runtime.run_receipts` as a worker;
- PIT consumers use the safe RPC.

- [ ] **Step 2: Verify failure before policies**

Run: `supabase test db supabase/tests/yqs1_04_rls_authority_test.sql`

Expected: FAIL.

- [ ] **Step 3: Implement default-deny grants and RLS**

Revoke broad `public`, `anon`, and `authenticated` access on application schemas/tables. Use app-role claims/functions to map authenticated identities to YQS roles. Keep service credentials backend-only.

- [ ] **Step 4: Protect governance actor type**

Add a check/trigger so `system` and `quant_worker` identities cannot claim a human actor role in `governance.authority_events`.

- [ ] **Step 5: Run tests and lint**

Run:

```bash
supabase db reset
supabase test db supabase/tests/yqs1_04_rls_authority_test.sql
supabase db lint --level error
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260826000400_yqs1_rls.sql supabase/tests/yqs1_04_rls_authority_test.sql
git commit -m "feat(yqs1): enforce sovereign research kernel RLS"
```

---

### Task 5: Implement append-first run receipts and replay settlement guards

**Files:**
- Create: `supabase/migrations/20260826000500_yqs1_append_first_guards.sql`
- Create: `supabase/tests/yqs1_05_ledger_guards_test.sql`

**Interfaces:**
- Consumes: runtime and replay objects.
- Produces: immutable receipt/settlement ledger behavior.

- [ ] **Step 1: Write negative mutation tests**

Attempt `UPDATE` and `DELETE` against an existing `runtime.run_receipts`, `replay.settlements`, and `governance.authority_events` record; tests must expect rejection.

- [ ] **Step 2: Verify failure before guards**

Run: `supabase test db supabase/tests/yqs1_05_ledger_guards_test.sql`

Expected: FAIL because mutations are still possible to privileged test roles.

- [ ] **Step 3: Implement append-first guards**

Create a shared trigger function that rejects `UPDATE`/`DELETE` for the three ledger tables. A rerun or correction creates a new row with a reference in payload metadata; no in-place replacement.

- [ ] **Step 4: Add replay freeze guard**

After `replay.replay_cases.frozen_at` is non-null, reject changes to `t0`, `knowledge_cutoff`, `replay_cutoff`, `hypotheses_json`, `allowed_evidence_policy_json`, `baseline_refs_json`, `ablation_refs_json`, and `output_schema_id`.

- [ ] **Step 5: Run tests**

Run:

```bash
supabase db reset
supabase test db supabase/tests/yqs1_05_ledger_guards_test.sql
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260826000500_yqs1_append_first_guards.sql supabase/tests/yqs1_05_ledger_guards_test.sql
git commit -m "feat(yqs1): make runtime and learning ledgers append-first"
```

---

### Task 6: Add local seed fixture and end-to-end kernel test

**Files:**
- Create: `supabase/seed.sql`
- Create: `supabase/tests/yqs1_06_kernel_e2e_test.sql`

**Interfaces:**
- Consumes: all prior migrations.
- Produces: one complete non-trading research path from Target to Thesis to PIT evidence to replay and settlement.

- [ ] **Step 1: Create seed fixture**

Use a synthetic target `YQS1-SYNTH-001` with:

- one ResearchTarget;
- independent C and R EngineTheses;
- no position sizing or live execution;
- two revisions of one observation, with only revision 1 knowable at T0;
- one factor definition/state;
- one frozen replay case;
- one synthetic run receipt;
- one later settlement.

- [ ] **Step 2: Write end-to-end assertions**

Assert:

- one target can host two theses;
- PIT RPC at T0 returns revision 1 and excludes revision 2;
- settlement cannot rewrite the frozen replay case;
- run receipt authority declaration has all capital/execution flags false;
- change queue is projection-only.

- [ ] **Step 3: Run the complete database suite**

Run:

```bash
supabase db reset
supabase test db
supabase db lint --level error
```

Expected: all tests PASS.

- [ ] **Step 4: Commit**

```bash
git add supabase/seed.sql supabase/tests/yqs1_06_kernel_e2e_test.sql
git commit -m "test(yqs1): add sovereign kernel end-to-end fixture"
```

---

### Task 7: Add CI without cloud deployment

**Files:**
- Create: `.github/workflows/yqs1-supabase-kernel.yml`
- Modify: `docs/architecture/yqs0/YQS0-STATE.json`

**Interfaces:**
- Consumes: local Supabase migrations and pgTAP suite.
- Produces: exact-head CI qualification for the YQS1 candidate without applying cloud migrations.

- [ ] **Step 1: Add workflow**

Workflow steps:

```text
checkout
setup Supabase CLI
supabase start
supabase db reset
supabase test db
supabase db lint --level error
pytest -q tests/test_yqs0_supabase_kernel.py
```

The workflow must not contain `supabase link`, `supabase db push`, cloud project refs, database passwords or deployment secrets.

- [ ] **Step 2: Update stage state only after green CI**

Change YQS0 state's next-stage pointer only in a later acceptance/receipt change. Do not write a fabricated successful CI receipt before GitHub returns actual green run metadata.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/yqs1-supabase-kernel.yml
git commit -m "ci(yqs1): validate local Supabase research kernel"
```

---

### Task 8: Prepare YQS1 Human Review package

**Files:**
- Create: `docs/architecture/yqs1/YQS1-HUMAN-REVIEW-CARD-v0.1.md`
- Create: `docs/architecture/yqs1/YQS1-STATE.json`

**Interfaces:**
- Consumes: exact-head green database/contract CI.
- Produces: candidate package for explicit Human Review, not merge or cloud deployment.

- [ ] **Step 1: Record exact tested head and CI identifiers**

Use real GitHub Actions run metadata only.

- [ ] **Step 2: Freeze YQS1 review questions**

Require PASS for schema count, object count, PIT leakage negatives, RLS negatives, append-first guards, ME1 multi-thesis fixture, and absence of live-execution tables/authority.

- [ ] **Step 3: Reserve but do not self-issue acceptance token**

Reserve:

`ACCEPT_YQS1_SUPABASE_RESEARCH_KERNEL_SCHEMA_RLS_IMPLEMENTATION`

- [ ] **Step 4: Commit and stop**

Stop at `candidate_ready_for_human_review`. Do not create a cloud Supabase project or apply migrations without later explicit authorization.

---

## Self-review result

- Spec coverage: all YQS0 frozen decisions map to Tasks 1-8.
- No new domain table beyond the eighteen YQS0 objects is introduced; queues/functions/types/indexes are infrastructure primitives.
- Heavy quant and Agent Runtime are intentionally outside YQS1 and should receive separate downstream implementation plans.
- Cloud creation/deployment and operational cutover remain outside this plan.
