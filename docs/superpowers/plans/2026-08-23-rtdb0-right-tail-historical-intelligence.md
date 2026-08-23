# RTDB0｜Right-Tail Historical Intelligence Database Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a governed historical right-tail research testbench in `yuanli-invest` that binds GitHub Canon, an isolated Supabase operational memory, and a Notion human-sensemaking portal, then prove the full chain with one NVIDIA PIT replay before expanding to a 12 Gold + 12 matched-contrast Genesis corpus.

**Architecture:** GitHub remains Semantic/Governance Authority, Supabase becomes queryable Operational Memory, and Notion is a curated Human Projection. The implementation separates historical identity, PIT epistemic state, experimental truth, immutable receipts, and projection/sync; it enforces `Case × PIT`, `Gold × Hard Negative`, four-layer PIT integrity, baseline/ablation replay, and `Receipt = Ledger; Status = Projection` end to end.

**Tech Stack:** Markdown, JSON Schema Draft 2020-12, Python 3.12, `jsonschema==4.25.1`, PostgreSQL 17/Supabase, SQL/RLS/triggers/views, Supabase Edge Functions using Deno/TypeScript and native `fetch`, Notion API/connector, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-23-rtdb0-right-tail-historical-intelligence-design.md`

## Global Constraints

- `GitHub defines; Supabase operates; Notion projects.`
- Authority is one-way; Notion feedback may return only through an explicit future Proposal → Review → Accepted Change flow.
- `ResearchTarget != RightTailCase != RightTailEpisode`.
- `Episode != Thesis` and `Target != Thesis != Position != Book`.
- `Generator Definition != Generator Activation`.
- `EvidenceClaim != Source`.
- `OutcomeObservation != Settlement`.
- `Projection != Research != History != Canon`.
- `Receipt = Ledger; Status = Projection`.
- `Research PASS != Capital PASS`.
- `Claim Authority <= Evidence Authority`.
- No scalar `right_tail_score`, `pnx_score`, `force_score`, or equivalent hidden composite authority.
- Historical epistemic unit: `RightTailEpisode × PITSnapshot`.
- Frozen PIT may be superseded but never silently edited in place.
- Replay admissibility: `evidence.first_available_at <= pit_snapshot.evidence_cutoff`.
- `PIT Integrity = Data Safety + Projection Safety + Page Safety + Navigation Safety`.
- PIT projections preserve `Known != Inferred != Unknown`.
- Mature Gold promotion requires at least one qualified matched hard negative, boundary case, or control.
- Hard negatives require ex-ante matching dimensions and confounders; eventual failure alone never qualifies a pair.
- Replay experiments compare against a simpler baseline and support signal ablation.
- Settlement resolves claims/mechanisms separately from raw return and ends in `REVISION_REQUIRED`, `NO_REVISION_REQUIRED`, or `DESCRIPTIVE_ONLY`.
- RTDB data must not be placed in the existing `yuanli-health` Supabase project.
- Target Supabase project name: `yuanli-invest-data`.
- Creating a billable Supabase project or enabling a billable backup/PITR upgrade requires one explicit owner confirmation of the exact platform-reported cost before the side effect.
- Supabase secrets and Notion tokens never enter GitHub.
- V1 is `GitHub → Supabase → Notion`; automatic Notion → Supabase truth mutation is out of scope.
- Projector may update MACHINE-owned Notion properties but never overwrite human long-form page body after initial template installation.
- Notion projector never automatically hard-deletes pages.
- Full raw Wind market-data warehousing is out of scope.
- No portfolio sizing, BUY/SELL instruction, trading execution, or current alpha recommendation is authorized.
- First production-grade proof: `RTEP-NVDA-GENAI-2022`.
- Bulk Genesis expansion is blocked until NVIDIA E2E passes G1–G6.
- `GENESIS_QUALIFIED` requires G1 Semantic Integrity, G2 PIT Integrity, G3 Experimental Integrity, G4 Reproducibility, G5 Projection Integrity, and G6 Reality Learning.
- `main` remains protected by existing `contracts` and `governance` checks; merge remains a separate owner authorization.

---

## File Structure

### Governance and docs

- Modify: `docs/superpowers/specs/2026-08-23-rtdb0-right-tail-historical-intelligence-design.md`
- Create: `docs/architecture/rtdb0/RTDB0-STATE.json`
- Create: `docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json`
- Create: `docs/architecture/rtdb0/RTDB0-HUMAN-REVIEW-CARD-v0.1.md`
- Create: `docs/rtdb/README.md`
- Create: `docs/rtdb/constitution.md`
- Create: `docs/rtdb/object-model.md`
- Create: `docs/rtdb/pit-protocol.md`
- Create: `docs/rtdb/hard-negative-protocol.md`
- Create: `docs/rtdb/notion-portal.md`
- Create: `docs/rtdb/genesis-set.md`

### JSON contracts and research objects

Follow the existing flat `packages/contracts/schemas/` convention.

- Create: `packages/contracts/schemas/rtdb-right-tail-case.schema.json`
- Create: `packages/contracts/schemas/rtdb-right-tail-episode.schema.json`
- Create: `packages/contracts/schemas/rtdb-right-tail-generator.schema.json`
- Create: `packages/contracts/schemas/rtdb-generator-activation.schema.json`
- Create: `packages/contracts/schemas/rtdb-pit-snapshot.schema.json`
- Create: `packages/contracts/schemas/rtdb-matched-case-pair.schema.json`
- Create: `packages/contracts/schemas/rtdb-replay-experiment.schema.json`
- Create: `packages/contracts/schemas/rtdb-replay-run.schema.json`
- Create: `packages/contracts/schemas/rtdb-settlement.schema.json`
- Create: `packages/contracts/schemas/rtdb-learning-receipt.schema.json`
- Create: `registry/rtdb/right-tail-generators-v0.1.json`
- Create: `reconstructions/rtdb/genesis-manifest-v0.1.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/case.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/episode.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/pit-2022-11-30.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/contrast-pair.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/replay-experiment.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/settlement.json`

### Validators, tests, CI

- Create: `scripts/validate_rtdb0_architecture.py`
- Create: `scripts/validate_rtdb0_notion_manifest.py`
- Create: `tests/test_rtdb0_architecture.py`
- Create: `tests/test_rtdb0_genesis.py`
- Create: `tests/sql/rtdb_schema_contract.sql`
- Modify: `.github/workflows/ci.yml`

### Supabase physical implementation

- Create: `infra/supabase/rtdb/README.md`
- Create: `infra/supabase/rtdb/migrations/202608230001_extensions_and_namespaces.sql`
- Create: `infra/supabase/rtdb/migrations/202608230002_core.sql`
- Create: `infra/supabase/rtdb/migrations/202608230003_epistemic.sql`
- Create: `infra/supabase/rtdb/migrations/202608230004_experiment_and_ledger.sql`
- Create: `infra/supabase/rtdb/migrations/202608230005_roles_rls_and_pit_enforcement.sql`
- Create: `infra/supabase/rtdb/migrations/202608230006_projection_and_sync.sql`
- Create: `infra/supabase/rtdb/migrations/202608230007_notion_projection_views.sql`
- Create: `infra/supabase/rtdb/seeds/right-tail-generators-v0.1.sql`
- Create: `infra/supabase/rtdb/seeds/nvidia-genesis.sql`

### Notion projection and Edge workers

- Create: `infra/supabase/rtdb/projection/notion/notion-rtdb-v1.json`
- Create: `infra/supabase/rtdb/projection/notion/field-ownership-v1.json`
- Create: `infra/supabase/rtdb/functions/_shared/projection.ts`
- Create: `infra/supabase/rtdb/functions/_shared/projection_test.ts`
- Create: `infra/supabase/rtdb/functions/notion-projector/index.ts`
- Create: `infra/supabase/rtdb/functions/notion-reconcile/index.ts`

---

# Battle 0 — Acceptance and Environment Qualification

### Task 0.1: Record written-spec Human Acceptance

**Files:**
- Modify: `docs/superpowers/specs/2026-08-23-rtdb0-right-tail-historical-intelligence-design.md`
- Create: `docs/architecture/rtdb0/RTDB0-STATE.json`
- Create: `tests/test_rtdb0_architecture.py`

**Interfaces:**
- Consumes: user token `ACCEPT_RTDB0_MASTER_WRITTEN_SPEC`; accepted spec commit `8536ce3d6058ee3ac11213f87742cfb61b359bee`.
- Produces: lifecycle state `WRITTEN_SPEC_HUMAN_ACCEPTED` with no billable-project, merge, or Canon-promotion authority.

- [ ] **Step 1: Write RED lifecycle test**

```python
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/architecture/rtdb0/RTDB0-STATE.json"
SPEC = ROOT / "docs/superpowers/specs/2026-08-23-rtdb0-right-tail-historical-intelligence-design.md"

class RTDB0LifecycleTests(unittest.TestCase):
    def test_written_spec_acceptance_is_recorded_without_side_effect_authority(self):
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["state"], "WRITTEN_SPEC_HUMAN_ACCEPTED")
        self.assertEqual(state["human_acceptance"], "ACCEPT_RTDB0_MASTER_WRITTEN_SPEC")
        self.assertFalse(state["supabase_project_creation_authorized"])
        self.assertFalse(state["merge_authorized"])
        self.assertFalse(state["canon_promotion_authorized"])
        self.assertIn("ACCEPT_RTDB0_MASTER_WRITTEN_SPEC", SPEC.read_text(encoding="utf-8"))
```

- [ ] **Step 2: Run RED**

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0LifecycleTests -v
```

Expected: FAIL because RTDB0 state does not yet exist.

- [ ] **Step 3: Create state and record acceptance**

Create `RTDB0-STATE.json` exactly with these initial fields:

```json
{
  "program": "RTDB0",
  "state": "WRITTEN_SPEC_HUMAN_ACCEPTED",
  "human_acceptance": "ACCEPT_RTDB0_MASTER_WRITTEN_SPEC",
  "accepted_spec": "docs/superpowers/specs/2026-08-23-rtdb0-right-tail-historical-intelligence-design.md",
  "accepted_spec_commit": "8536ce3d6058ee3ac11213f87742cfb61b359bee",
  "implementation_planning_authorized": true,
  "supabase_project_creation_authorized": false,
  "merge_authorized": false,
  "canon_promotion_authorized": false
}
```

Change the spec header status to `design_human_accepted` and append `Written-Spec Acceptance: ACCEPT_RTDB0_MASTER_WRITTEN_SPEC`; do not change design sections.

- [ ] **Step 4: Run GREEN**

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0LifecycleTests -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-08-23-rtdb0-right-tail-historical-intelligence-design.md docs/architecture/rtdb0/RTDB0-STATE.json tests/test_rtdb0_architecture.py
git commit -m "RTDB0: record written spec acceptance"
```

### Task 0.2: Qualify exact repository baseline

**Files:**
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Consumes: latest protected `main` exact SHA at execution time.
- Produces: exact base SHA and baseline gate result in RTDB0 state.

- [ ] **Step 1: Create isolated implementation worktree/branch from latest `main`**

Run:

```bash
git fetch origin main
git rev-parse origin/main
git status --short
```

The execution agent writes the exact `git rev-parse origin/main` output into `environment_qualification.base_sha`; empty/null values are forbidden.

- [ ] **Step 2: Run existing baseline gates**

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_repository.py
python scripts/leak_guard.py
python scripts/check_governance.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS on exact base. A pre-existing unrelated failure blocks RTDB implementation until explicitly characterized.

- [ ] **Step 3: Record baseline result**

Add `environment_qualification` with exact base SHA and `contracts_baseline: PASS`, `governance_baseline: PASS`.

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: qualify implementation baseline"
```

### Task 0.3: Resolve Supabase/Notion environments

**Files:**
- Create: `docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Consumes: Supabase organization/cost APIs and current Notion objects.
- Produces: observed external IDs only.

- [ ] **Step 1: Resolve Supabase organization and project cost**

List organizations and request platform cost for new project name `yuanli-invest-data`. If billable, show exact platform-returned cost/cadence and obtain one explicit owner confirmation before project creation.

- [ ] **Step 2: Re-fetch Notion bindings before any write**

Expected current objects from prior inspection are:

```text
原力投研 page: 3c18e1aa-ace4-8127-ae39-f7baa5335115
Knowledge Object Registry database: 08711e2f-ae55-4c60-bf61-dd02dbc8a9b0
Knowledge Object Registry data source: 17e2efd9-c438-4b46-82ff-66e8359b3d02
```

Re-fetch by exact title and verify these identities still resolve under `Yuanli Portal｜原力世界`; if any differs, use the newly observed identity and record the drift rather than assuming the old value.

- [ ] **Step 3: Write environment file with actual connector-returned values**

The file must contain actual Supabase organization ID and verified Notion IDs. Before project creation, `project_ref` and `project_region` are JSON `null`. `cost_confirmation_status` is exactly `NOT_REQUIRED` when the platform reports no incremental billable cost or `CONFIRMED` after explicit owner approval. No fake/sample IDs are committed.

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: bind external environments"
```

---

# Battle 1 — GitHub Canon, Schemas, and Validators

### Task 1.1: Create RTDB constitutional docs

**Files:**
- Create: `docs/rtdb/README.md`
- Create: `docs/rtdb/constitution.md`
- Create: `docs/rtdb/object-model.md`
- Create: `docs/rtdb/pit-protocol.md`
- Create: `docs/rtdb/hard-negative-protocol.md`
- Modify: `tests/test_rtdb0_architecture.py`

**Interfaces:**
- Produces: readable contracts for authority, objects, PIT, and matched-contrast admission.

- [ ] **Step 1: Add RED doc tests**

```python
class RTDB0DocumentationTests(unittest.TestCase):
    def test_constitution_preserves_core_laws(self):
        text = (ROOT / "docs/rtdb/constitution.md").read_text(encoding="utf-8")
        required = [
            "GitHub defines; Supabase operates; Notion projects.",
            "Case × PIT",
            "Gold × Hard Negative",
            "Outcome != Thesis Validation",
            "Receipt = Ledger; Status = Projection",
            "PIT Integrity = Data + Projection + Page + Navigation",
        ]
        for guard in required:
            self.assertIn(guard, text)
        for forbidden in ["right_tail_score", "pnx_score", "force_score"]:
            self.assertNotIn(forbidden, text)
```

- [ ] **Step 2: Run RED**

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0DocumentationTests -v
```

- [ ] **Step 3: Write docs from accepted spec**

`object-model.md` contains:

```text
ResearchTarget → RightTailCase → RightTailEpisode
RightTailEpisode ↔ RightTailGenerator via GeneratorActivation
RightTailEpisode → PITSnapshot → EvidenceClaim/ResearchState
RightTailEpisode ↔ RightTailEpisode via MatchedCasePair
PITSnapshot → ReplayExperiment → ReplayRun → BenchmarkResult
OutcomeObservation → FutureSettlement → LearningReceipt → CapabilityRevision/FailureRegime
```

`pit-protocol.md` defines `effective_at`, `published_at`, `first_available_at`, `retrieved_at`, freeze/supersede, and four-layer leakage protection.

`hard-negative-protocol.md` requires `pair_decided_at`, matching dimensions, confounders, minimum discriminator, and explicit ex-ante validity rationale.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0DocumentationTests -v
git add docs/rtdb tests/test_rtdb0_architecture.py
git commit -m "docs: add RTDB constitutional contracts"
```

### Task 1.2: Add JSON Schema contracts

**Files:**
- Create all ten `packages/contracts/schemas/rtdb-*.schema.json` files listed above.
- Modify: `tests/test_rtdb0_architecture.py`

**Interfaces:**
- Produces: Draft 2020-12 validation for all first-class RTDB objects.

- [ ] **Step 1: Add RED schema-meta test**

```python
from jsonschema import Draft202012Validator

SCHEMA_NAMES = [
    "rtdb-right-tail-case.schema.json",
    "rtdb-right-tail-episode.schema.json",
    "rtdb-right-tail-generator.schema.json",
    "rtdb-generator-activation.schema.json",
    "rtdb-pit-snapshot.schema.json",
    "rtdb-matched-case-pair.schema.json",
    "rtdb-replay-experiment.schema.json",
    "rtdb-replay-run.schema.json",
    "rtdb-settlement.schema.json",
    "rtdb-learning-receipt.schema.json"
]

class RTDB0SchemaTests(unittest.TestCase):
    def test_all_schemas_are_valid_draft_2020_12(self):
        base = ROOT / "packages/contracts/schemas"
        for name in SCHEMA_NAMES:
            schema = json.loads((base / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            Draft202012Validator.check_schema(schema)
```

- [ ] **Step 2: Run RED**

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0SchemaTests -v
```

- [ ] **Step 3: Implement strict schemas**

Every schema uses `additionalProperties: false`, stable `object_key`, explicit enums, and date-time formats. PIT requires `object_key`, `episode_key`, `as_of`, `evidence_cutoff`, `publication_lag_policy`, `data_revision_policy`, `information_set_version`, `snapshot_stage`, `freeze_state`. Matched pair requires `pair_decided_at`, positive/contrast episode keys, matching dimensions, confounders, and primary discriminator hypothesis. Replay run requires Canon revision, capability version, code commit, PIT keys, evidence cutoff, receipt ID, and run status.

- [ ] **Step 4: Add negative validation tests**

Prove an incomplete PIT fails, and recursively fail if any schema introduces `right_tail_score`, `pnx_score`, or `force_score` as a property.

- [ ] **Step 5: Run GREEN and commit**

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0SchemaTests -v
git add packages/contracts/schemas/rtdb-*.schema.json tests/test_rtdb0_architecture.py
git commit -m "feat: add RTDB historical object schemas"
```

### Task 1.3: Add generator registry, Genesis manifest, validator, CI

**Files:**
- Create: `registry/rtdb/right-tail-generators-v0.1.json`
- Create: `reconstructions/rtdb/genesis-manifest-v0.1.json`
- Create: `scripts/validate_rtdb0_architecture.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_rtdb0_architecture.py`

**Interfaces:**
- Produces: deterministic contract gate in existing `contracts` CI job.

- [ ] **Step 1: Write RED registry tests**

Every generator requires:

```text
object_key, name, family, mechanism_definition,
observables_contract, falsifier_contract, boundary_conditions,
causal_mapping, engine_affinity, maturity
```

Genesis manifest must contain exactly these 12 starting case families:

```text
Amazon
Apple
Microsoft Cloud
NVIDIA
Tencent
Moutai
Tesla
Bitcoin
Gold
Paulson Subprime
GLP-1
ASML
```

Each begins with `pair_admission_state: CANDIDATE` until matching review.

- [ ] **Step 2: Implement registry/manifest and validator**

Validator checks schema validity, registry shape, falsifiers/boundaries, forbidden scalar fields, pair completeness before `ACCEPTED`, and PIT-blind future-field prohibition once projection manifest exists.

- [ ] **Step 3: Add CI line after YIM0 validator**

```yaml
      - run: python scripts/validate_rtdb0_architecture.py
```

Do not rename/remove existing checks.

- [ ] **Step 4: Run GREEN and commit**

```bash
python scripts/validate_rtdb0_architecture.py
python -m unittest discover -s tests -p 'test_*.py' -v
git add registry/rtdb reconstructions/rtdb/genesis-manifest-v0.1.json scripts/validate_rtdb0_architecture.py tests/test_rtdb0_architecture.py .github/workflows/ci.yml
git commit -m "RTDB0: add generator and Genesis contract gate"
```

---

# Battle 2 — Supabase Project and Persistence

### Task 2.1: Create isolated `yuanli-invest-data`

**Files:**
- Modify: `docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Produces: live project ref/region only after cost authority is satisfied.

- [ ] **Step 1: Confirm cost state**

Proceed only when the environment file records `NOT_REQUIRED` or `CONFIRMED` according to Task 0.3.

- [ ] **Step 2: Create project using Supabase connector**

Use target name `yuanli-invest-data`, selected observed organization, and a platform-supported region. Record actual returned project ref and region.

- [ ] **Step 3: Record state**

Set `state: SUPABASE_PROJECT_CREATED` and `supabase_project_creation_authorized: true`. Never commit credentials.

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: record isolated Supabase project"
```

### Task 2.2: Create namespace/core migrations, operator README, and generator seed

**Files:**
- Create: `infra/supabase/rtdb/README.md`
- Create: `infra/supabase/rtdb/migrations/202608230001_extensions_and_namespaces.sql`
- Create: `infra/supabase/rtdb/migrations/202608230002_core.sql`
- Create: `infra/supabase/rtdb/seeds/right-tail-generators-v0.1.sql`
- Create: `tests/sql/rtdb_schema_contract.sql`

**Interfaces:**
- Produces: seven namespaces, core identity/mechanism/pair tables, and deterministic generator seed sourced from GitHub registry.

- [ ] **Step 1: Write RED SQL assertions**

```sql
do $$ begin
  if to_regnamespace('rt_core') is null then
    raise exception 'missing rt_core schema';
  end if;
  if to_regclass('rt_core.right_tail_episodes') is null then
    raise exception 'missing rt_core.right_tail_episodes';
  end if;
end $$;
```

Also require `rt_epistemic`, `rt_experiment`, `rt_ledger`, `rt_projection`, `rt_sync`, `private`.

- [ ] **Step 2: Run RED against empty PostgreSQL 17**

Expected: FAIL.

- [ ] **Step 3: Implement namespaces/core tables**

Create:

```text
rt_core.research_targets
rt_core.right_tail_cases
rt_core.right_tail_episodes
rt_core.right_tail_generators
rt_core.generator_activations
rt_core.matched_case_pairs
```

Every domain table has UUID PK, unique `object_key`, creation timestamp, and revision metadata. Pair table stores pair type, pair decision timestamp, matching dimensions, confounders, discriminator hypothesis, admission state, and review receipt reference.

- [ ] **Step 4: Generate `right-tail-generators-v0.1.sql` from the accepted registry**

The SQL must reproduce the same object keys and mechanism metadata as `registry/rtdb/right-tail-generators-v0.1.json`; the validator compares the registry keys to seed keys and fails on drift.

- [ ] **Step 5: Write operator README**

Document lexical migration order, seed order, no-Dashboard-drift rule, live negative-test commands, and secret-handling rules.

- [ ] **Step 6: Run GREEN and commit**

```bash
git add infra/supabase/rtdb/README.md infra/supabase/rtdb/migrations/202608230001_extensions_and_namespaces.sql infra/supabase/rtdb/migrations/202608230002_core.sql infra/supabase/rtdb/seeds/right-tail-generators-v0.1.sql tests/sql/rtdb_schema_contract.sql
git commit -m "feat: add RTDB Supabase core schema"
```

### Task 2.3: Add epistemic, experiment, ledger, and retrieval indexes

**Files:**
- Create: `infra/supabase/rtdb/migrations/202608230003_epistemic.sql`
- Create: `infra/supabase/rtdb/migrations/202608230004_experiment_and_ledger.sql`
- Modify: `tests/sql/rtdb_schema_contract.sql`

**Interfaces:**
- Produces: PIT/evidence/outcome, replay/benchmark/settlement, append-only receipts, and structured/full-text retrieval indexes.

- [ ] **Step 1: Extend RED assertions**

Require:

```text
rt_epistemic.pit_snapshots
rt_epistemic.evidence_sources
rt_epistemic.evidence_versions
rt_epistemic.evidence_claims
rt_epistemic.snapshot_evidence
rt_epistemic.outcome_observations
rt_experiment.replay_experiments
rt_experiment.replay_runs
rt_experiment.benchmark_results
rt_experiment.future_settlements
rt_experiment.learning_receipts
rt_ledger.research_receipts
rt_ledger.replay_receipts
rt_ledger.settlement_receipts
rt_ledger.projection_receipts
rt_ledger.sync_receipts
```

- [ ] **Step 2: Implement evidence time semantics**

Evidence versions contain `effective_at`, `published_at`, `first_available_at NOT NULL`, `retrieved_at NOT NULL`. PIT contains `as_of`, `evidence_cutoff`, publication/data-revision policy, information-set version, snapshot stage, freeze state, revision, and `supersedes_id`.

- [ ] **Step 3: Implement experiment lineage**

Replay runs bind exact Canon revision, capability version, code commit, evidence cutoff, PIT IDs, runtime provider, typed result locator, and receipt ID. Settlement is separate from outcome observations and has no mutation path into PIT.

- [ ] **Step 4: Enforce append-only receipts**

Create `private.reject_ledger_mutation()` and attach it to UPDATE/DELETE on all `rt_ledger` receipt tables; exact exception token `RTDB_LEDGER_APPEND_ONLY`.

- [ ] **Step 5: Add V1 retrieval indexes**

Create normal indexes on stable keys/time/FKs and a Postgres full-text GIN index over curated claim text. Do not enable pgvector in V1 migration unless a real semantic-retrieval consumer is introduced; vector similarity remains optional retrieval metadata, never evidence authority.

- [ ] **Step 6: Run GREEN and commit**

```bash
git add infra/supabase/rtdb/migrations/202608230003_epistemic.sql infra/supabase/rtdb/migrations/202608230004_experiment_and_ledger.sql tests/sql/rtdb_schema_contract.sql
git commit -m "feat: add RTDB PIT experiment and ledger persistence"
```

---

# Battle 3 — PIT Enforcement, RLS, Projection, Sync

### Task 3.1: Enforce PIT/freeze and replay-safe access

**Files:**
- Create: `infra/supabase/rtdb/migrations/202608230005_roles_rls_and_pit_enforcement.sql`
- Modify: `tests/sql/rtdb_schema_contract.sql`

**Interfaces:**
- Produces: future-evidence rejection, frozen-PIT immutability, default-deny access, replay-safe read surfaces.

- [ ] **Step 1: Add RED leakage tests**

Insert a PIT with cutoff `2023-04-01T00:00:00Z`, evidence version with `first_available_at = 2023-05-01T00:00:00Z`, then attempt a `snapshot_evidence` link. Expected exact exception token: `RTDB_PIT_EVIDENCE_AFTER_CUTOFF`.

Freeze a PIT and attempt to change `as_of` or `evidence_cutoff`. Expected exact exception token: `RTDB_PIT_FROZEN_IMMUTABLE`.

- [ ] **Step 2: Implement enforcement functions/triggers**

Create:

```text
private.enforce_snapshot_evidence_cutoff()
private.enforce_frozen_pit_immutability()
```

- [ ] **Step 3: Add logical roles/RLS**

Create privilege design for `rt_admin`, `rt_ingest`, `rt_reviewer`, `rt_replay`, `rt_projector`, `rt_reader`. Revoke public/anon access by default. `rt_replay` receives PIT-safe views and replay-write paths, not future-settlement/outcome reads.

- [ ] **Step 4: Run GREEN and commit**

```bash
git add infra/supabase/rtdb/migrations/202608230005_roles_rls_and_pit_enforcement.sql tests/sql/rtdb_schema_contract.sql
git commit -m "feat: enforce RTDB PIT and access boundaries"
```

### Task 3.2: Add durable outbox/map/receipts and seven projection views

**Files:**
- Create: `infra/supabase/rtdb/migrations/202608230006_projection_and_sync.sql`
- Create: `infra/supabase/rtdb/migrations/202608230007_notion_projection_views.sql`
- Modify: `tests/sql/rtdb_schema_contract.sql`

**Interfaces:**
- Produces: desired-state projection contract for Battle 5.

- [ ] **Step 1: Add RED assertions**

Require `rt_sync.projection_outbox`, `rt_sync.notion_projection_map`, `rt_sync.projection_drift`, and these views:

```text
rt_projection.notion_case_projection_v1
rt_projection.notion_episode_projection_v1
rt_projection.notion_generator_projection_v1
rt_projection.notion_pit_blind_projection_v1
rt_projection.notion_contrast_projection_v1
rt_projection.notion_replay_projection_v1
rt_projection.notion_settlement_projection_v1
```

- [ ] **Step 2: Implement outbox**

Allowed event types: `CREATE_OR_UPDATE`, `RELATION_REFRESH`, `DEPRECATE`, `REBUILD`, `VERIFY`. Add `private.claim_projection_jobs(batch_size int)` using `FOR UPDATE SKIP LOCKED`, plus complete/fail functions.

- [ ] **Step 3: Implement projection-map uniqueness**

Unique `(target_database_key, object_key)`. Store desired/applied source revisions and hashes separately, Notion page ID, contract version, last sync/verify timestamps.

- [ ] **Step 4: Implement seven versioned views**

`notion_pit_blind_projection_v1` is physically forbidden from exposing columns whose normalized names contain `future_return`, `settlement_verdict`, `future_settlement`, `final_gold_role`, `post_pit_generator`, `later_engine_transition`, `outcome_observation`.

Every case/episode/generator/replay/settlement view also exposes a boolean `global_registry_eligible`; default false. The flag may be true only for the RTDB portal, accepted Generator objects, accepted Gold/Hard-Negative/Boundary Episodes, selected accepted Replay Dossiers, or material Settlements under the registry eligibility rules. This permits later projection into the existing Knowledge Object Registry without creating an eighth specialized RTDB database.

- [ ] **Step 5: Run GREEN and commit**

```bash
git add infra/supabase/rtdb/migrations/202608230006_projection_and_sync.sql infra/supabase/rtdb/migrations/202608230007_notion_projection_views.sql tests/sql/rtdb_schema_contract.sql
git commit -m "feat: add RTDB projection and sync ledger"
```

### Task 3.3: Deploy, qualify data plane, and record backup status

**Files:**
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`
- Modify: `docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json`

**Interfaces:**
- Produces: live migration qualification and backup/PITR capability record.

- [ ] **Step 1: Apply migrations and generator seed in lexical order**

Use Supabase SQL/migration connector. No Dashboard-only divergence.

- [ ] **Step 2: Run live negative probes inside rollbackable transactions**

Verify exact future-evidence, frozen-PIT, and append-only errors; inspect PIT blind view columns.

- [ ] **Step 3: Inspect backup/PITR status**

Record the platform’s actual daily-backup/PITR capability for the new project. If enabling PITR requires a new billable upgrade, request explicit exact-cost confirmation before changing the plan; otherwise enable the production-appropriate available setting. This side effect follows the same cost rule as project creation.

- [ ] **Step 4: Record migration hashes/live results**

Write project ref, SHA-256 for each applied migration/seed, `pit_negative_tests: PASS`, and backup/PITR status into RTDB0 state/environment.

- [ ] **Step 5: Commit**

```bash
git add docs/architecture/rtdb0/RTDB0-STATE.json docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json
git commit -m "RTDB0: qualify Supabase data plane"
```

---

# Battle 4 — Notion Think-Tank

### Task 4.1: Freeze Notion manifest, ownership, registry eligibility, learning journeys

**Files:**
- Create: `infra/supabase/rtdb/projection/notion/notion-rtdb-v1.json`
- Create: `infra/supabase/rtdb/projection/notion/field-ownership-v1.json`
- Create: `scripts/validate_rtdb0_notion_manifest.py`
- Create: `docs/rtdb/notion-portal.md`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_rtdb0_architecture.py`

**Interfaces:**
- Produces: deterministic `1 + 7` DB, `1 + 6` page-template, global-registry eligibility, and three-journey contract.

- [ ] **Step 1: Write RED manifest tests**

Require exactly these specialized DB keys:

```text
case_registry
episode_library
generator_atlas
pit_snapshot_library
contrast_pair_lab
replay_dossier
reality_settlement
```

Every property must be one of `MACHINE`, `HUMAN`, `PROPOSAL`, `DERIVED_NOTION`.

- [ ] **Step 2: Implement manifests**

Common MACHINE fields:

```text
Object Key
Source Object Type
Source Revision
Projection Revision
Projection State
Last Synced
Sync Status
```

Human long-form body is never MACHINE-owned. Encode template keys `research_passport`, `gold_episode`, `generator`, `pit_blind`, `contrast_pair`, `replay_dossier`, `reality_settlement`.

- [ ] **Step 3: Encode portal doors, learning journeys, and KOR eligibility**

Portal doors:

```text
Thirty-Year Right-Tail Map
Generator Atlas
Gold Case Library
Contrast Lab
PIT Replay Lab
Reality Settlement
From History to Now
```

Learning journeys:

```text
BEGINNER: Map → Case → Generator → Contrast
EXPERT_ENTREPRENEUR: Generator → Value Concentration → Case → Business Transfer
LAB: Generator → PIT → Pair → Replay → Benchmark → Settlement → Revision
```

Global Registry eligibility is explicit and default-deny; PIT snapshots and ordinary runtime runs are not eligible.

- [ ] **Step 4: Implement validator and CI**

Fail on missing ownership, future fields in PIT views, audience-copy duplication, machine ownership of body content, or a second global registry. Add:

```yaml
      - run: python scripts/validate_rtdb0_notion_manifest.py
```

- [ ] **Step 5: Run GREEN and commit**

```bash
python scripts/validate_rtdb0_notion_manifest.py
python -m unittest tests.test_rtdb0_architecture -v
git add infra/supabase/rtdb/projection/notion docs/rtdb/notion-portal.md scripts/validate_rtdb0_notion_manifest.py tests/test_rtdb0_architecture.py .github/workflows/ci.yml
git commit -m "RTDB0: freeze Notion projection manifest"
```

### Task 4.2: Create seven Notion databases and portal

**Files:**
- Modify: `docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Produces: live portal under verified `原力投研` parent.

- [ ] **Step 1: Fetch current Notion enhanced-markdown and view-DSL specs**

Do this immediately before writes.

- [ ] **Step 2: Create portal**

Title: `原力历史右尾数据库｜Right-Tail Historical Intelligence`

Hero: `世界如何生成少数极端赢家？`

Callout: `这不是十倍股名单；这是右尾生成机制的历史实验室。`

- [ ] **Step 3: Create seven DB identities before relations**

Record actual database/data-source IDs in environment file immediately after creation.

- [ ] **Step 4: Add relations in second pass**

Case→Episode, Episode↔Generator, Episode→PIT, pair relations, replay relations, settlement relations.

- [ ] **Step 5: Create portal views and `1+6` skeletons**

PIT Blind views hide settlement/outcome/final Gold role. Backend operational views remain separate from Think Tank views. Audience views use existing Yuanli Portal vocabulary `BEGINNER`, `EXPERT_ENTREPRENEUR`, `LAB` rather than inventing new labels.

- [ ] **Step 6: Verify existing Knowledge Object Registry still owns global identity**

No duplicate global registry is created.

- [ ] **Step 7: Commit observed IDs/state**

```bash
git add docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: construct Notion Think Tank"
```

---

# Battle 5 — Projector and Reconciliation

### Task 5.1: Implement canonical machine-payload hashing

**Files:**
- Create: `infra/supabase/rtdb/functions/_shared/projection.ts`
- Create: `infra/supabase/rtdb/functions/_shared/projection_test.ts`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Produces:
  - `canonicalMachinePayload(record, ownership)`
  - `sha256Json(value)`
  - `machinePatch(desired, observed, ownership)`

- [ ] **Step 1: Write RED Deno tests**

```typescript
Deno.test("human fields are excluded from machine payload", () => {
  const record = {"Object Key": "RTEP-NVDA-GENAI-2022", "Primary Engine": "R", "Hero": "human copy"}
  const ownership = {"Object Key": "MACHINE", "Primary Engine": "MACHINE", "Hero": "HUMAN"}
  const payload = canonicalMachinePayload(record, ownership)
  if ("Hero" in payload) throw new Error("human field leaked into machine payload")
})

Deno.test("canonical hash ignores object key order", async () => {
  const a = await sha256Json({a: 1, b: 2})
  const b = await sha256Json({b: 2, a: 1})
  if (a !== b) throw new Error("hash is not canonical")
})
```

- [ ] **Step 2: Run RED**

```bash
deno test infra/supabase/rtdb/functions/_shared/projection_test.ts
```

- [ ] **Step 3: Implement pure deterministic functions**

Canonical JSON recursively sorts object keys before SHA-256. `machinePatch` returns changed MACHINE fields only.

- [ ] **Step 4: Run GREEN**

- [ ] **Step 5: Add Deno to existing `contracts` job without renaming job**

Use `denoland/setup-deno@v2`, then run the focused test.

- [ ] **Step 6: Commit**

```bash
git add infra/supabase/rtdb/functions/_shared .github/workflows/ci.yml
git commit -m "feat: add deterministic RTDB projection core"
```

### Task 5.2: Implement idempotent Notion projector including selected KOR projection

**Files:**
- Create: `infra/supabase/rtdb/functions/notion-projector/index.ts`
- Modify: `infra/supabase/rtdb/functions/_shared/projection_test.ts`

**Interfaces:**
- Consumes: outbox, seven projection views, ownership manifest, Notion secret, projection map, verified KOR ID.
- Produces: CREATE/PATCH/NOOP/DEPRECATE/RELATION_REFRESH plus append-only receipts; eligible accepted objects may also project identity metadata into existing KOR.

- [ ] **Step 1: Add RED decision tests**

Expected decisions:

```text
no mapping                      → CREATE
mapping + same machine hash     → NOOP
mapping + changed machine hash  → PATCH
missing relation target         → DEPENDENCY_WAIT
schema mismatch                 → BLOCKED_SCHEMA
auth failure                    → BLOCKED_AUTH
duplicate key mapping           → BLOCKED_CONFLICT
source deprecated               → DEPRECATE state, never hard delete
```

Also prove `global_registry_eligible=false` never writes KOR and eligible=true can enqueue an identity-only KOR projection after specialized-page identity exists.

- [ ] **Step 2: Implement worker flow**

```text
claim job
→ load projection record
→ load ownership/target contract
→ compute desired machine hash
→ lookup map
→ create or patch machine properties
→ relation refresh only after dependency mappings exist
→ selected KOR identity projection when eligible
→ verify observed machine state
→ append projection/sync receipt
→ complete or classify job
```

Use native `fetch` for Notion. Never log tokens or authorization headers.

- [ ] **Step 3: Implement retry classification**

Network/429/5xx → `RETRYABLE`; dependency missing → `DEPENDENCY_WAIT`; property mismatch → `BLOCKED_SCHEMA`; 401/403 → `BLOCKED_AUTH`; duplicate identity → `BLOCKED_CONFLICT`; exhausted retry policy → `DEAD_LETTER`.

- [ ] **Step 4: Run Deno tests and commit**

```bash
deno test infra/supabase/rtdb/functions/_shared/projection_test.ts
git add infra/supabase/rtdb/functions/notion-projector infra/supabase/rtdb/functions/_shared/projection_test.ts
git commit -m "feat: add idempotent RTDB Notion projector"
```

### Task 5.3: Implement reconciliation and schedule

**Files:**
- Create: `infra/supabase/rtdb/functions/notion-reconcile/index.ts`
- Modify: `infra/supabase/rtdb/functions/_shared/projection_test.ts`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Produces: drift evidence/repair jobs; no blind rewrites.

- [ ] **Step 1: Add RED drift tests**

Detect `MISSING_PROJECTION`, `PAYLOAD_DRIFT`, `RELATION_DRIFT`, `CONTRACT_VERSION_DRIFT`, `SCHEMA_DRIFT`. Human body differences are never payload drift.

- [ ] **Step 2: Implement reconcile worker**

Compare page existence, machine properties, applied revision/hash, relation integrity, and contract version. Insert drift records and enqueue repair events only.

- [ ] **Step 3: Schedule once daily with `pg_cron` + `pg_net`**

Store callable secret in Supabase Vault/Edge secrets, never SQL literals/GitHub.

- [ ] **Step 4: Deploy projector/reconcile and run smoke test**

Create one disposable projection object. First projector run = CREATE. Second = NOOP. Edit Human Zone paragraph in Notion, rerun = paragraph unchanged. Induce one machine-property drift, reconcile = drift record + repair event.

- [ ] **Step 5: Record qualification and commit**

State records `idempotency: PASS`, `human_body_preservation: PASS`, `schema_drift_fail_closed: PASS`, `pit_projection_leakage: 0`.

```bash
git add infra/supabase/rtdb/functions/notion-reconcile infra/supabase/rtdb/functions/_shared/projection_test.ts docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "feat: add RTDB projection reconciliation"
```

---

# Battle 6 — NVIDIA Genesis E2E

### Task 6.1: Build source-aware NVIDIA Case × PIT bundle

**Files:**
- Create NVIDIA files listed under File Structure.
- Create/modify: `tests/test_rtdb0_genesis.py`

**Interfaces:**
- Produces: `RTCASE-NVDA`, `RTEP-NVDA-GENAI-2022`, `PIT-NVDA-GENAI-20221130`, one boundary contrast.

- [ ] **Step 1: Write RED schema/PIT tests**

Require PIT key `PIT-NVDA-GENAI-20221130` and evidence cutoff `2022-11-30T23:59:59Z`. If primary-source timestamp verification shows that a selected same-day item was not available by that cutoff, exclude the item; do not move the cutoff later merely to admit it.

- [ ] **Step 2: Collect primary/authoritative historical sources with publication-time verification**

Every source record captures locator, publication time, first-available time, retrieval time, and supported/refuted claim. NVIDIA filings/earnings materials, CUDA/developer-platform releases, and contemporaneous primary company/product announcements are eligible primary sources. Secondary commentary is external context only.

- [ ] **Step 3: Freeze Known/Inferred/Unknown separately**

PIT contains no 2023+ earnings/outcome evidence.

- [ ] **Step 4: Create Cisco 2000 as explicit `BOUNDARY_CROSS_ERA` contrast**

Research question: structural truth/value concentration can coexist with price prepayment. The pair must state that dates/business mechanics differ and list confounders. If ex-ante matching review rejects Cisco as primary contrast, retain Cisco as a boundary case and admit a better contrast through the same protocol.

- [ ] **Step 5: Run tests and commit**

```bash
python -m unittest tests.test_rtdb0_genesis -v
git add reconstructions/rtdb/nvidia-genai-2022 tests/test_rtdb0_genesis.py
git commit -m "data: add NVIDIA RTDB Genesis PIT bundle"
```

### Task 6.2: Seed NVIDIA and prove live PIT enforcement

**Files:**
- Create: `infra/supabase/rtdb/seeds/nvidia-genesis.sql`
- Modify: `tests/test_rtdb0_genesis.py`

**Interfaces:**
- Produces: live case/episode/generator activations/PIT/evidence/pair objects.

- [ ] **Step 1: Generate deterministic seed SQL from validated JSON**

Use stable-object-key upsert for mutable identity records and insert/revision semantics for frozen PIT/receipts. Never update frozen PIT in place.

- [ ] **Step 2: Apply seed**

Verify FKs and object-key uniqueness.

- [ ] **Step 3: Run deliberate future-evidence negative**

Attempt one post-cutoff evidence link; expect `RTDB_PIT_EVIDENCE_AFTER_CUTOFF`; rollback fixture.

- [ ] **Step 4: Freeze PIT and attempt cutoff mutation**

Expect `RTDB_PIT_FROZEN_IMMUTABLE`.

- [ ] **Step 5: Commit seed**

```bash
git add infra/supabase/rtdb/seeds/nvidia-genesis.sql tests/test_rtdb0_genesis.py
git commit -m "data: seed NVIDIA RTDB Genesis case"
```

### Task 6.3: Run baseline, Yuanli replay, ablation, settlement

**Files:**
- Create: `reconstructions/rtdb/nvidia-genai-2022/replay-experiment.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/settlement.json`
- Modify: `tests/test_rtdb0_genesis.py`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Produces: first auditable experiment/settlement chain.

- [ ] **Step 1: Write RED replay-contract tests**

Require capability/version, Canon revision/hash, PIT IDs, hypothesis, baseline ID, metrics, leakage policy, success criteria, settlement verdict, capability-delta state.

- [ ] **Step 2: Bind exact execution versions**

No `latest` aliases. Record exact Git SHA, capability version, PIT bundle hash, provider/runtime ID.

- [ ] **Step 3: Run pre-registered simple baseline `BASE-RTDB-XS-V1`**

Baseline rule is intentionally simpler than the Yuanli capability and uses only three PIT-safe questions:

```text
B1 structural value-pool expansion supported?      YES / NO / UNKNOWN
B2 operating economics improving or resilient?     YES / NO / UNKNOWN
B3 price prepayment risk not disqualifying?         YES / NO / UNKNOWN
```

Baseline emits `ADMIT` only when B1=YES, B2=YES, and B3=YES; any NO emits `REJECT`; otherwise `UNDERIDENTIFIED`. It does not use ecosystem/network/bottleneck/optionality features.

- [ ] **Step 4: Run accepted Yuanli capability replay**

Use the currently accepted capability implementation that can evaluate structural/value-concentration evidence at this PIT. If no qualified runtime exists, emit `UNDERIDENTIFIED`/`REPLAY_INVALID` and stop Gold promotion rather than simulate output.

- [ ] **Step 5: Ablate one major generator family**

Remove ecosystem-control observables, rerun, and record whether discrimination changes.

- [ ] **Step 6: Create separate settlement**

Post-PIT outcomes live only in settlement/outcome objects. Verdict must be one of `SUPPORTED`, `CONTRADICTED`, `UNRESOLVED`, `RIGHT_OUTCOME_WRONG_MECHANISM`, `WRONG_OUTCOME_RIGHT_MECHANISM`; capability delta exactly one of `REVISION_REQUIRED`, `NO_REVISION_REQUIRED`, `DESCRIPTIVE_ONLY`.

- [ ] **Step 7: Re-run identical inputs for reproducibility**

Same Canon revision, capability version, code commit, PIT, evidence bundle, and provider mode must reproduce typed output within declared tolerance. Record both receipt IDs.

- [ ] **Step 8: Commit**

```bash
git add reconstructions/rtdb/nvidia-genai-2022/replay-experiment.json reconstructions/rtdb/nvidia-genai-2022/settlement.json tests/test_rtdb0_genesis.py docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: run NVIDIA Genesis replay settlement"
```

### Task 6.4: Project NVIDIA into Notion and qualify G1–G6

**Files:**
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Produces: Case, Gold Episode, Generator, PIT Blind, Contrast, Replay Dossier, Settlement pages linked by stable Object Keys.

- [ ] **Step 1: Enqueue topologically**

Case + Generator → Episode → PIT + Contrast → Replay → Settlement → relation refresh → selected KOR identity projection.

- [ ] **Step 2: Run projector to convergence**

Every Object Key maps to exactly one Notion page; applied source revision/hash equals desired state.

- [ ] **Step 3: Verify PIT Blind has zero future leakage**

No settlement verdict, 2023+ outcome, final Gold result, or post-PIT generator activation.

- [ ] **Step 4: Human-body preservation test**

Edit one Human Zone paragraph, rerun projector twice; paragraph remains unchanged; second unchanged-machine run is NOOP.

- [ ] **Step 5: Verify Reveal Reality is separate**

Link title does not disclose verdict before entry.

- [ ] **Step 6: Record G1–G6 result**

Only mark `nvidia_genesis_e2e: PASS` if all six pass; record exact receipts and `pit_leakage_violations: 0`.

- [ ] **Step 7: Commit**

```bash
git add docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: qualify NVIDIA Genesis E2E"
```

---

# Battle 7 — Genesis Expansion and Final Human Review

### Task 7.1: Create Genesis-set doc and settle 12 matched-contrast admissions

**Files:**
- Modify: `reconstructions/rtdb/genesis-manifest-v0.1.json`
- Create: `docs/rtdb/genesis-set.md`
- Modify: `tests/test_rtdb0_genesis.py`

**Interfaces:**
- Produces: each Gold family has an accepted contrast or explicit `PAIR_BLOCKED`; blocked families are not discrimination-grade Gold.

- [ ] **Step 1: Add RED coverage test**

```python
class RTDB0GenesisCoverageTests(unittest.TestCase):
    def test_each_gold_has_accepted_contrast_or_explicit_block(self):
        manifest = json.loads((ROOT / "reconstructions/rtdb/genesis-manifest-v0.1.json").read_text(encoding="utf-8"))
        for item in manifest["gold_case_families"]:
            self.assertIn(item["pair_admission_state"], {"ACCEPTED", "PAIR_BLOCKED"})
            if item["pair_admission_state"] == "ACCEPTED":
                self.assertGreaterEqual(len(item["accepted_contrast_keys"]), 1)
```

- [ ] **Step 2: Research every pair through hard-negative protocol**

Starting candidates may include Amazon↔Webvan, Apple↔Nokia/BlackBerry, Tencent↔Renren, and validated boundary/negative analogues for remaining families. Record matching dimensions, confounders, minimum discriminator, pair-decision date, and review receipt. No defensible pair → `PAIR_BLOCKED`.

- [ ] **Step 3: Write `genesis-set.md`**

For all 12 families, show Gold episode scope, candidate/accepted contrast, PIT milestones, pair admission state, replay state, settlement state, and explicit blockers. It is a status/readability projection, not a second source of truth.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest tests.test_rtdb0_genesis.RTDB0GenesisCoverageTests -v
git add reconstructions/rtdb/genesis-manifest-v0.1.json docs/rtdb/genesis-set.md tests/test_rtdb0_genesis.py
git commit -m "data: settle RTDB Genesis contrast coverage"
```

### Task 7.2: Expand PIT/replay coverage case-family by case-family

**Files:**
- Add remaining case-family directories under `reconstructions/rtdb/`.
- Reuse existing schemas/migrations/projector; do not invent parallel object types.
- Modify: `tests/test_rtdb0_genesis.py`

**Interfaces:**
- Produces: 3–5 meaningful PITs per admitted Gold episode where evidence supports them.

- [ ] **Step 1: Create PITs only at meaningful epistemic milestones**

Allowed roles: `SEED`, `EVIDENCE`, `IGNITION`, `EXPANSION`, `MATURITY`, `BREAK`, `POST_MORTEM`.

- [ ] **Step 2: Reject evidence lacking defensible `first_available_at`**

Do not infer availability from the period described by the data.

- [ ] **Step 3: Seed/freeze through the same Supabase path**

No manual Dashboard bypass.

- [ ] **Step 4: Run replay/benchmark/settlement only where runtime is actually qualified**

Unavailable capability → blocked/underidentified, never synthetic success.

- [ ] **Step 5: Project curated objects only**

No raw evidence warehouse mirror and no every-run log mirror into Notion.

- [ ] **Step 6: Run integrated tests**

```bash
python scripts/validate_rtdb0_architecture.py
python scripts/validate_rtdb0_notion_manifest.py
python -m unittest tests.test_rtdb0_architecture tests.test_rtdb0_genesis -v
deno test infra/supabase/rtdb/functions/_shared/projection_test.ts
```

- [ ] **Step 7: Commit in independently reviewable case-family batches**

Use descriptive case-family commit messages; preserve research lineage.

### Task 7.3: Run six acceptance gates and prepare Human Review card

**Files:**
- Create: `docs/architecture/rtdb0/RTDB0-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`
- Modify: `scripts/validate_rtdb0_architecture.py`

**Interfaces:**
- Produces: final machine qualification without merge authority.

- [ ] **Step 1: Extend validator for G1–G6**

Hard-fail G2 on any PIT leakage; hard-fail G5 on human-body overwrite; hard-fail G3 on silent missing contrast.

- [ ] **Step 2: Run full repository gates and exact-head GitHub checks**

Require existing `contracts` and `governance` green on PR head.

- [ ] **Step 3: Build Human Review Card**

Include exact commit SHA, non-secret Supabase ref, migration hashes, backup/PITR status, PIT leakage count, replay receipts, projection receipts, Notion portal IDs, unresolved/blocked cases, and capability deltas.

- [ ] **Step 4: Set final machine-qualified state only when all six pass**

State: `GENESIS_QUALIFIED_READY_FOR_HUMAN_REVIEW`; `merge_authorized: false`; `canon_promotion_authorized: false`.

- [ ] **Step 5: Commit**

```bash
git add docs/architecture/rtdb0 scripts/validate_rtdb0_architecture.py
git commit -m "RTDB0: prepare Genesis Human Review"
```

### Task 7.4: Create one implementation PR and stop at merge authority

**Files:** none required beyond completed implementation.

**Interfaces:**
- Produces: one reviewable PR to protected `main`.

- [ ] **Step 1: Compare implementation head to current main**

No unrelated files and no accepted YIP0/ME0/ME1 authority rewrite.

- [ ] **Step 2: Create PR**

Title: `RTDB0: build right-tail historical intelligence testbench`

Body includes authority boundary, six gates, NVIDIA receipts, non-secret environment bindings, blocked Genesis pairs, exact-head CI status, and `MERGE NOT AUTHORIZED BY IMPLEMENTATION PLAN`.

- [ ] **Step 3: Require exact-head protected checks green**

`contracts` and `governance` must pass.

- [ ] **Step 4: Stop for final Human Review / merge authorization**

No protected-branch merge and no final Canon promotion without explicit owner authorization.

---

## Final Verification Matrix

| Requirement | Required evidence |
|---|---|
| GitHub remains semantic authority | Spec, constitution, migrations, manifests in repo |
| Supabase isolated from health | Observed `yuanli-invest-data` project ref |
| Case/episode separation | Schemas + NVIDIA objects |
| PIT evidence cutoff | DB negative test + live receipt |
| Frozen PIT immutability | DB negative test + live receipt |
| Gold × contrast discipline | Genesis manifest + pair review |
| Baseline/ablation | Replay/benchmark receipts |
| Outcome != settlement | Separate tables/objects |
| Receipt append-only | SQL mutation-negative tests |
| Structured/full-text retrieval | Index contract + query smoke test |
| Seven Notion DBs | Live IDs in environment file |
| Research Passport + six templates | Manifest + live portal |
| Three learning journeys | Manifest + live audience views |
| Existing KOR preserved | Verified KOR ID + eligibility projection test |
| Human body preserved | Projector smoke-test receipt |
| Idempotent projection | CREATE then NOOP proof |
| PIT blind no future fields | SQL view audit + Notion inspection |
| Daily reconciliation | Scheduled job + reconcile receipt |
| Backup/PITR status | Environment/state record |
| NVIDIA E2E | G1–G6 evidence |
| 12+12 quality | Accepted pairs or explicit blocks |
| Protected CI | Exact-head `contracts` + `governance` green |

## Final Stop Conditions

Execution stops rather than improvises if:

- billable Supabase creation or backup/PITR upgrade lacks explicit exact-cost confirmation;
- exact main baseline fails before RTDB changes and cannot be proven unrelated;
- a PIT source lacks defensible `first_available_at`;
- a Gold/contrast pair cannot be justified ex ante;
- a required replay capability is not actually runtime-qualified;
- observed Notion schema differs from approved manifest;
- convergence would overwrite HUMAN content;
- PIT blind path exposes future outcome/settlement data;
- protected `contracts` or `governance` fails at PR exact head;
- protected-branch merge or destructive external action lacks explicit owner authority.
