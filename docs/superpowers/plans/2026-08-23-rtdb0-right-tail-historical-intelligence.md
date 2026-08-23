# RTDB0｜Right-Tail Historical Intelligence Database Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a governed historical right-tail research testbench in `yuanli-invest` that binds GitHub Canon, an isolated Supabase operational memory, and a Notion human-sensemaking portal, then prove the full chain with one NVIDIA PIT replay before expanding to a 12 Gold + 12 matched-contrast Genesis corpus.

**Architecture:** GitHub remains Semantic/Governance Authority, Supabase becomes queryable Operational Memory, and Notion is a curated Human Projection. The implementation separates historical identity, PIT epistemic state, experimental truth, immutable receipts, and projection/sync; it enforces `Case × PIT`, `Gold × Hard Negative`, four-layer PIT integrity, baseline/ablation replay, and `Receipt = Ledger; Status = Projection` end to end.

**Tech Stack:** Markdown, JSON Schema Draft 2020-12, Python 3.12, `jsonschema==4.25.1`, PostgreSQL 17/Supabase, SQL/RLS/triggers/views, Supabase Edge Functions (Deno/TypeScript + native `fetch`), Notion API/connector, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-23-rtdb0-right-tail-historical-intelligence-design.md`

## Global Constraints

- `GitHub defines; Supabase operates; Notion projects.`
- Authority is one-way; Notion feedback may return only as an explicit future Proposal → Review → Accepted Change flow.
- `ResearchTarget != RightTailCase != RightTailEpisode`.
- `Episode != Thesis` and `Target != Thesis != Position != Book`.
- `Generator Definition != Generator Activation`.
- `EvidenceClaim != Source`.
- `OutcomeObservation != Settlement`.
- `Projection != Research != History != Canon`.
- `Receipt = Ledger; Status = Projection`.
- `Research PASS != Capital PASS`.
- `Claim Authority <= Evidence Authority`.
- No scalar `right_tail_score`, PNX score, or equivalent hidden composite authority.
- The historical epistemic unit is `RightTailEpisode × PITSnapshot`.
- Frozen PIT may be superseded but never silently edited in place.
- Replay admissibility requires `evidence.first_available_at <= pit_snapshot.evidence_cutoff`.
- `PIT Integrity = Data Safety + Projection Safety + Page Safety + Navigation Safety`.
- PIT projections preserve `Known != Inferred != Unknown`.
- Mature Gold promotion requires at least one qualified matched hard negative, boundary case, or control.
- Hard negatives must be justified by ex-ante matching dimensions, not selected only because later failure is known.
- Replay experiments must compare against simpler baselines and support signal ablation.
- Settlement resolves claims/mechanisms separately from raw return and ends in `REVISION_REQUIRED`, `NO_REVISION_REQUIRED`, or `DESCRIPTIVE_ONLY`.
- RTDB data must not be placed in the existing `yuanli-health` Supabase project.
- Target Supabase project name is `yuanli-invest-data`; creation is blocked until the platform reports cost and the owner explicitly confirms any billable cost.
- Supabase secrets and Notion tokens never enter GitHub.
- V1 is `GitHub → Supabase → Notion`; there is no automatic Notion → Supabase truth mutation.
- Projector may update MACHINE-owned Notion properties but never overwrite human long-form page body after initial template installation.
- Notion projector never automatically hard-deletes pages.
- Full raw Wind market-data warehousing is out of scope; RTDB stores governed observations, evidence locators/bundles, and research state required for replay.
- No portfolio sizing, BUY/SELL instruction, trading execution, or current alpha recommendation is authorized.
- The first production-grade end-to-end proof is NVIDIA Generative AI Infrastructure 2022; bulk Genesis expansion is blocked until that proof passes G1–G6.
- `GENESIS_QUALIFIED` requires all six gates: Semantic Integrity, PIT Integrity, Experimental Integrity, Reproducibility, Projection Integrity, Reality Learning.
- `main` is protected by `contracts` and `governance`; implementation occurs on an isolated feature branch/worktree and merge remains a separate owner authorization.

---

## File Structure

### Governance / human research docs

- Modify: `docs/superpowers/specs/2026-08-23-rtdb0-right-tail-historical-intelligence-design.md` — record written-spec Human Acceptance only; do not change accepted design semantics.
- Create: `docs/architecture/rtdb0/RTDB0-STATE.json` — lifecycle/status projection for RTDB0.
- Create: `docs/architecture/rtdb0/RTDB0-HUMAN-REVIEW-CARD-v0.1.md` — six-gate final Human Review card.
- Create: `docs/rtdb/README.md` — RTDB operator/navigation entry.
- Create: `docs/rtdb/constitution.md` — constitutional laws copied from the accepted spec.
- Create: `docs/rtdb/object-model.md` — object identities and ERD.
- Create: `docs/rtdb/pit-protocol.md` — PIT evidence-time and freeze/supersede protocol.
- Create: `docs/rtdb/hard-negative-protocol.md` — matching/confounder/admission protocol.
- Create: `docs/rtdb/notion-portal.md` — Notion portal IA, ownership zones, views, and learning journeys.
- Create: `docs/rtdb/genesis-set.md` — Genesis case-family manifest and admission status.

### JSON contracts / registries / Genesis data

Follow the repository’s existing flat `packages/contracts/schemas/` convention rather than introducing a nested incompatible schema layout.

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

### Validators / tests / CI

- Create: `scripts/validate_rtdb0_architecture.py`
- Create: `scripts/validate_rtdb0_notion_manifest.py`
- Create: `tests/test_rtdb0_architecture.py`
- Create: `tests/test_rtdb0_genesis.py`
- Create: `tests/sql/rtdb_schema_contract.sql`
- Modify: `.github/workflows/ci.yml` — install/run RTDB validators and SQL/Edge tests without weakening existing `contracts`/`governance` gates.

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

### Notion projection / Edge worker

- Create: `infra/supabase/rtdb/projection/notion/notion-rtdb-v1.json` — seven database schemas, field ownership, views, and template identifiers.
- Create: `infra/supabase/rtdb/projection/notion/field-ownership-v1.json` — MACHINE/HUMAN/PROPOSAL/DERIVED_NOTION contract.
- Create: `infra/supabase/rtdb/functions/_shared/projection.ts` — canonical machine-payload hashing and patch selection.
- Create: `infra/supabase/rtdb/functions/_shared/projection_test.ts` — deterministic unit tests.
- Create: `infra/supabase/rtdb/functions/notion-projector/index.ts` — outbox worker / Notion API delivery.
- Create: `infra/supabase/rtdb/functions/notion-reconcile/index.ts` — desired-vs-observed verification and repair enqueue.

---

# Battle 0 — Acceptance Recording and Environment Qualification

### Task 0.1: Record written-spec Human Acceptance and create RTDB0 lifecycle state

**Files:**
- Modify: `docs/superpowers/specs/2026-08-23-rtdb0-right-tail-historical-intelligence-design.md`
- Create: `docs/architecture/rtdb0/RTDB0-STATE.json`
- Test: `tests/test_rtdb0_architecture.py`

**Interfaces:**
- Consumes: exact user token `ACCEPT_RTDB0_MASTER_WRITTEN_SPEC` and accepted spec at commit `8536ce3d6058ee3ac11213f87742cfb61b359bee`.
- Produces: machine-readable lifecycle state `WRITTEN_SPEC_HUMAN_ACCEPTED` without authorizing billable project creation, merge, or Canon promotion.

- [ ] **Step 1: Write the RED lifecycle test**

Create `tests/test_rtdb0_architecture.py`:

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

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0LifecycleTests -v
```

Expected: FAIL because `RTDB0-STATE.json` does not exist and the accepted spec has not yet recorded the acceptance token.

- [ ] **Step 3: Record the acceptance without expanding authority**

Set `RTDB0-STATE.json` to this exact semantic shape:

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

Update the spec header to `Status: design_human_accepted` and append a short `Written-Spec Acceptance` section containing the exact token; do not rewrite design sections.

- [ ] **Step 4: Run focused tests**

Run:

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0LifecycleTests -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-08-23-rtdb0-right-tail-historical-intelligence-design.md docs/architecture/rtdb0/RTDB0-STATE.json tests/test_rtdb0_architecture.py
git commit -m "RTDB0: record written spec acceptance"
```

### Task 0.2: Qualify exact repository head and existing gates before implementation

**Files:**
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Consumes: current feature branch exact head and protected `main` exact head.
- Produces: `environment_qualification` receipt data; implementation proceeds only when baseline `contracts` and `governance` are green or an unrelated pre-existing failure is explicitly recorded as blocking.

- [ ] **Step 1: Rebase/worktree from the latest protected `main` before implementation**

Execution-time rule:

```text
feature base == latest main exact SHA
```

If `main` advanced after plan creation, create/rebase the implementation worktree before changing production artifacts; do not silently implement on stale architecture.

- [ ] **Step 2: Run existing repository gates before adding RTDB code**

Run:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_repository.py
python scripts/leak_guard.py
python scripts/check_governance.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all existing checks PASS on exact base.

- [ ] **Step 3: Record base SHA and baseline qualification**

Add to `RTDB0-STATE.json`:

```json
"environment_qualification": {
  "base_sha": "<exact execution-time SHA written by the worker>",
  "contracts_baseline": "PASS",
  "governance_baseline": "PASS"
}
```

The worker must replace the example with the actual SHA returned at execution time; a missing/empty SHA fails validation.

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: qualify implementation baseline"
```

### Task 0.3: Resolve external environments; stop only for Supabase billable-cost confirmation

**Files:**
- Create after live resolution: `docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Consumes: Supabase organization/project-cost APIs; Notion search/fetch of the existing `原力投研` parent and existing global Knowledge Object Registry.
- Produces: environment bindings for later deployment without hard-coding guessed external IDs.

- [ ] **Step 1: Resolve Supabase organization and target project cost**

Use the Supabase management connector to list organizations, select the organization already hosting the user’s Yuanli projects unless the owner specifies another, and call the platform cost-estimation action for project name `yuanli-invest-data`.

If the returned cost is non-zero/billable, present the exact amount/cadence and request the one required explicit cost confirmation. Do not create the project before that confirmation.

- [ ] **Step 2: Resolve Notion parent and global registry**

Search Notion for exact title `原力投研` under `Yuanli Portal｜原力世界` and exact database `Knowledge Object Registry`. Fetch both and record their returned page/database/data-source identifiers. Do not create RTDB databases yet.

- [ ] **Step 3: Write environment binding only with observed IDs**

Create `RTDB0-ENVIRONMENT.json` with keys:

```json
{
  "supabase": {
    "organization_id": "observed-value",
    "project_name": "yuanli-invest-data",
    "project_ref": null,
    "project_region": null,
    "cost_confirmation_status": "PENDING_OR_CONFIRMED"
  },
  "notion": {
    "investment_parent_page_id": "observed-value",
    "knowledge_object_registry_id": "observed-value"
  }
}
```

`project_ref` remains JSON `null` until the project is actually created; literal strings such as `TBD` are forbidden.

- [ ] **Step 4: Commit environment bindings**

```bash
git add docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: bind external environments"
```

---

# Battle 1 — GitHub Canon, Object Contracts, and Fail-Closed Validators

### Task 1.1: Create RTDB constitution and operator docs

**Files:**
- Create: `docs/rtdb/README.md`
- Create: `docs/rtdb/constitution.md`
- Create: `docs/rtdb/object-model.md`
- Create: `docs/rtdb/pit-protocol.md`
- Create: `docs/rtdb/hard-negative-protocol.md`
- Modify: `tests/test_rtdb0_architecture.py`

**Interfaces:**
- Consumes: accepted Master Spec.
- Produces: human-readable authoritative RTDB0 contracts that do not create portfolio/trading authority.

- [ ] **Step 1: Add RED documentation-contract tests**

Add tests that require all five files and exact invariant strings:

```python
class RTDB0DocumentationTests(unittest.TestCase):
    def test_constitution_preserves_core_laws(self):
        text = (ROOT / "docs/rtdb/constitution.md").read_text(encoding="utf-8")
        for guard in [
            "GitHub defines; Supabase operates; Notion projects.",
            "Case × PIT",
            "Gold × Hard Negative",
            "Outcome != Thesis Validation",
            "Receipt = Ledger; Status = Projection",
            "PIT Integrity = Data + Projection + Page + Navigation",
        ]:
            self.assertIn(guard, text)
        self.assertNotIn("right_tail_score", text)
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0DocumentationTests -v
```

Expected: FAIL because docs do not exist.

- [ ] **Step 3: Write the five docs directly from the accepted spec**

`object-model.md` must contain the ERD chain:

```text
ResearchTarget → RightTailCase → RightTailEpisode
RightTailEpisode ↔ RightTailGenerator via GeneratorActivation
RightTailEpisode → PITSnapshot → EvidenceClaim/ResearchState
RightTailEpisode ↔ RightTailEpisode via MatchedCasePair
PITSnapshot → ReplayExperiment → ReplayRun → BenchmarkResult
OutcomeObservation → FutureSettlement → LearningReceipt → CapabilityRevision/FailureRegime
```

`pit-protocol.md` must define `effective_at`, `published_at`, `first_available_at`, `retrieved_at`, freeze/supersede, and four-layer leakage protection.

`hard-negative-protocol.md` must require `pair_decided_at`, matching dimensions, confounders, minimum discriminator, and an explicit reason the pair is valid ex ante.

- [ ] **Step 4: Run tests**

Run:

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0DocumentationTests -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/rtdb tests/test_rtdb0_architecture.py
git commit -m "docs: add RTDB constitutional contracts"
```

### Task 1.2: Add JSON Schema contracts for historical objects

**Files:**
- Create the ten `packages/contracts/schemas/rtdb-*.schema.json` files listed in File Structure.
- Modify: `tests/test_rtdb0_architecture.py`

**Interfaces:**
- Consumes: existing repository Draft 2020-12 JSON Schema conventions and `jsonschema==4.25.1`.
- Produces: machine validation for RTDB domain objects.

- [ ] **Step 1: Add a RED schema-meta test**

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
    "rtdb-learning-receipt.schema.json",
]

class RTDB0SchemaTests(unittest.TestCase):
    def test_all_rtdb_schemas_are_draft_2020_12_valid(self):
        base = ROOT / "packages/contracts/schemas"
        for name in SCHEMA_NAMES:
            schema = json.loads((base / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            Draft202012Validator.check_schema(schema)
```

- [ ] **Step 2: Run and verify RED**

Run:

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0SchemaTests -v
```

Expected: FAIL on missing schemas.

- [ ] **Step 3: Implement minimal strict schemas**

Each schema uses `additionalProperties: false`, stable `object_key`, explicit enums, ISO date-time formats, and does not define any universal PNX/right-tail scalar.

The PIT schema must require at least:

```json
{
  "required": [
    "object_key",
    "episode_key",
    "as_of",
    "evidence_cutoff",
    "publication_lag_policy",
    "data_revision_policy",
    "information_set_version",
    "snapshot_stage",
    "freeze_state"
  ]
}
```

The matched-pair schema must require `pair_decided_at`, `positive_episode_key`, `contrast_episode_key`, `matching_dimensions`, `confounders`, and `primary_discriminator_hypothesis`.

The replay-run schema must require `canon_revision`, `capability_version`, `code_commit`, `pit_snapshot_keys`, `evidence_cutoff`, `research_receipt_id`, and `run_status`.

- [ ] **Step 4: Add negative tests for forbidden scalar authority and missing PIT cutoff**

Instantiate Draft202012Validator with a valid fixture and prove:

```python
with self.assertRaises(Exception):
    Draft202012Validator(pit_schema).validate({"object_key": "PIT-X"})
```

Also recursively scan schema property names and fail if any schema introduces `right_tail_score`, `pnx_score`, or `force_score` as a normative output.

- [ ] **Step 5: Run tests**

Run:

```bash
python -m unittest tests.test_rtdb0_architecture.RTDB0SchemaTests -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add packages/contracts/schemas/rtdb-*.schema.json tests/test_rtdb0_architecture.py
git commit -m "feat: add RTDB historical object schemas"
```

### Task 1.3: Add generator registry, Genesis manifest, validator, and CI gate

**Files:**
- Create: `registry/rtdb/right-tail-generators-v0.1.json`
- Create: `reconstructions/rtdb/genesis-manifest-v0.1.json`
- Create: `scripts/validate_rtdb0_architecture.py`
- Modify: `tests/test_rtdb0_architecture.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: deterministic fail-closed RTDB architecture validation integrated into existing `contracts` job.

- [ ] **Step 1: Write RED tests for generator and Genesis registries**

Require generator records to have:

```text
object_key, name, family, mechanism_definition,
observables_contract, falsifier_contract, boundary_conditions,
causal_mapping, engine_affinity, maturity
```

Require Genesis manifest to list exactly the 12 accepted starting case families and mark pair status separately from case-family status.

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python -m unittest tests.test_rtdb0_architecture -v
```

Expected: FAIL on missing registry/manifest.

- [ ] **Step 3: Create the registry and Genesis manifest**

The initial generator registry includes the accepted families from the spec; every entry has an explicit falsifier and boundary condition. Engine affinity is an array of `C`, `R`, `X`, never a score.

The Genesis manifest contains:

```text
Amazon, Apple, Microsoft Cloud, NVIDIA, Tencent, Moutai,
Tesla, Bitcoin, Gold, Paulson Subprime, GLP-1, ASML
```

and a separate `pair_admission_state` initialized to `CANDIDATE` until ex-ante matching is reviewed.

- [ ] **Step 4: Implement `validate_rtdb0_architecture.py`**

The validator must:

1. load all RTDB JSON schemas with `Draft202012Validator.check_schema`;
2. validate generator/Genesis JSON structure;
3. assert no `right_tail_score` / `pnx_score` / `force_score` normative fields;
4. assert every generator has falsifier/boundary conditions;
5. assert all Genesis pairs remain non-accepted unless matching/confounder fields are complete;
6. assert PIT blind projection manifest, once created, contains no future fields;
7. emit non-zero exit status on any violation.

- [ ] **Step 5: Add the validator to CI**

In `.github/workflows/ci.yml` `contracts` job, add immediately after YIM0 validator:

```yaml
      - run: python scripts/validate_rtdb0_architecture.py
```

Do not remove or rename existing protected checks.

- [ ] **Step 6: Run full contracts baseline**

Run:

```bash
python scripts/validate_rtdb0_architecture.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add registry/rtdb reconstructions/rtdb/genesis-manifest-v0.1.json scripts/validate_rtdb0_architecture.py tests/test_rtdb0_architecture.py .github/workflows/ci.yml
git commit -m "RTDB0: add generator and Genesis contract gate"
```

---

# Battle 2 — Supabase Project and Physical Persistence

### Task 2.1: Create the isolated Supabase project after cost confirmation

**Files:**
- Modify after creation: `docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Consumes: Task 0.3 organization/cost resolution and explicit owner confirmation when required.
- Produces: isolated project ref for `yuanli-invest-data`.

- [ ] **Step 1: Confirm creation authority**

Proceed only if `cost_confirmation_status` is `CONFIRMED` for any billable plan or the platform explicitly reports zero incremental billable cost.

- [ ] **Step 2: Create `yuanli-invest-data` in the selected organization**

Use the Supabase connector project-creation action with the confirmed organization and platform-supported region. Prefer the same operational region as existing Yuanli infrastructure when the platform offers it; record the actual chosen region rather than assuming one.

- [ ] **Step 3: Record returned project ref/region and move state**

Set:

```json
"state": "SUPABASE_PROJECT_CREATED",
"supabase_project_creation_authorized": true
```

and replace `project_ref` / `project_region` nulls in `RTDB0-ENVIRONMENT.json` with observed values.

- [ ] **Step 4: Commit the environment receipt only; never commit credentials**

```bash
git add docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: record isolated Supabase project"
```

### Task 2.2: Create namespace/core migrations and RED SQL contract test

**Files:**
- Create: `infra/supabase/rtdb/migrations/202608230001_extensions_and_namespaces.sql`
- Create: `infra/supabase/rtdb/migrations/202608230002_core.sql`
- Create: `tests/sql/rtdb_schema_contract.sql`

**Interfaces:**
- Produces: `rt_core`, `rt_epistemic`, `rt_experiment`, `rt_ledger`, `rt_projection`, `rt_sync`, `private` and core case/episode/generator/pair tables.

- [ ] **Step 1: Write SQL assertions before migrations**

`tests/sql/rtdb_schema_contract.sql` must fail unless these namespaces and relations exist. Use `to_regnamespace()` / `to_regclass()` and raise exceptions, e.g.:

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

- [ ] **Step 2: Verify RED in local/staging Postgres**

Run migrations against an empty PostgreSQL 17 database only after proving `rtdb_schema_contract.sql` fails first.

Expected: FAIL on missing schemas/tables.

- [ ] **Step 3: Implement namespaces and core tables**

`202608230001...sql` creates `pgcrypto` if available and the seven namespaces.

`202608230002_core.sql` creates at minimum:

```sql
rt_core.research_targets
rt_core.right_tail_cases
rt_core.right_tail_episodes
rt_core.right_tail_generators
rt_core.generator_activations
rt_core.matched_case_pairs
```

Every domain table has `id uuid primary key default gen_random_uuid()`, unique `object_key text not null`, `created_at timestamptz not null default now()`, and revision metadata. `matched_case_pairs` stores `pair_decided_at`, JSONB arrays for structured matching-dimension descriptors only when a fully normalized child table is not justified in V1, and explicit `pair_admission_state`.

- [ ] **Step 4: Run SQL contract test**

Expected: PASS for namespaces/core objects.

- [ ] **Step 5: Commit**

```bash
git add infra/supabase/rtdb/migrations/202608230001_extensions_and_namespaces.sql infra/supabase/rtdb/migrations/202608230002_core.sql tests/sql/rtdb_schema_contract.sql
git commit -m "feat: add RTDB Supabase core schema"
```

### Task 2.3: Add epistemic, experiment, and immutable ledger migrations

**Files:**
- Create: `infra/supabase/rtdb/migrations/202608230003_epistemic.sql`
- Create: `infra/supabase/rtdb/migrations/202608230004_experiment_and_ledger.sql`
- Modify: `tests/sql/rtdb_schema_contract.sql`

**Interfaces:**
- Produces: PIT/evidence/outcome tables, replay/benchmark/settlement tables, and append-only receipt tables.

- [ ] **Step 1: Extend SQL test with RED assertions**

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

- [ ] **Step 2: Verify RED**

Apply only Tasks 2.2 migrations and run SQL test. Expected: FAIL on missing epistemic/experiment objects.

- [ ] **Step 3: Implement epistemic time fields and experiment lineage**

Evidence versions contain:

```sql
effective_at timestamptz,
published_at timestamptz,
first_available_at timestamptz not null,
retrieved_at timestamptz not null
```

PIT snapshots contain `as_of`, `evidence_cutoff`, publication/data-revision policy, `information_set_version`, `snapshot_stage`, `freeze_state`, `revision`, `supersedes_id`.

Replay runs bind `canon_revision`, `capability_version`, `code_commit`, `evidence_cutoff`, and receipt ID. Settlement tables never own/write PIT mutable fields.

- [ ] **Step 4: Make receipt tables append-only**

Create `private.reject_ledger_mutation()` and attach `before update or delete` triggers to all `rt_ledger.*_receipts` tables that `raise exception 'RTDB_LEDGER_APPEND_ONLY'`.

- [ ] **Step 5: Run SQL tests**

Expected: PASS, including a transaction that inserts a receipt then proves UPDATE/DELETE raises `RTDB_LEDGER_APPEND_ONLY`.

- [ ] **Step 6: Commit**

```bash
git add infra/supabase/rtdb/migrations/202608230003_epistemic.sql infra/supabase/rtdb/migrations/202608230004_experiment_and_ledger.sql tests/sql/rtdb_schema_contract.sql
git commit -m "feat: add RTDB PIT experiment and ledger persistence"
```

---

# Battle 3 — PIT Enforcement, Roles/RLS, Projection, and Sync Ledger

### Task 3.1: Enforce PIT admission and freeze/supersede at database level

**Files:**
- Create: `infra/supabase/rtdb/migrations/202608230005_roles_rls_and_pit_enforcement.sql`
- Modify: `tests/sql/rtdb_schema_contract.sql`

**Interfaces:**
- Produces: fail-closed evidence cutoff, frozen PIT immutability, logical roles, default-deny external access, and replay-safe access surfaces.

- [ ] **Step 1: Add RED PIT leakage tests**

Test fixture:

```text
PIT cutoff:       2023-04-01T00:00:00Z
Evidence available: 2023-05-01T00:00:00Z
```

Attempting to insert the link into `snapshot_evidence` must fail with exact error code/message token `RTDB_PIT_EVIDENCE_AFTER_CUTOFF`.

Also freeze a snapshot and prove attempts to update `as_of`, `evidence_cutoff`, publication policy, or information-set version fail with `RTDB_PIT_FROZEN_IMMUTABLE`.

- [ ] **Step 2: Verify RED**

Run test before migration; it must fail because enforcement functions do not exist.

- [ ] **Step 3: Implement enforcement triggers**

Create:

```text
private.enforce_snapshot_evidence_cutoff()
private.enforce_frozen_pit_immutability()
```

The first queries `evidence_versions.first_available_at` and `pit_snapshots.evidence_cutoff`. The second compares OLD/NEW only for frozen epistemic fields and permits non-semantic workflow metadata that the contract explicitly marks mutable.

- [ ] **Step 4: Add roles and RLS**

Create logical roles/privilege model for `rt_admin`, `rt_ingest`, `rt_reviewer`, `rt_replay`, `rt_projector`, `rt_reader`. Revoke public/anon access by default. `rt_replay` gets only PIT-safe views and write authority to replay result/receipt paths, not future-settlement tables.

For Supabase platform roles, RLS policies expose only explicit projection/read paths; backend secret-key use by Edge Functions is documented as temporary privilege debt until projector-specific database credentials are available.

- [ ] **Step 5: Run SQL tests including role visibility**

Prove PIT failures, ledger immutability, and that replay-facing views omit settlement/outcome columns.

- [ ] **Step 6: Commit**

```bash
git add infra/supabase/rtdb/migrations/202608230005_roles_rls_and_pit_enforcement.sql tests/sql/rtdb_schema_contract.sql
git commit -m "feat: enforce RTDB PIT and access boundaries"
```

### Task 3.2: Implement projection/outbox/map/receipt storage and seven Notion-safe views

**Files:**
- Create: `infra/supabase/rtdb/migrations/202608230006_projection_and_sync.sql`
- Create: `infra/supabase/rtdb/migrations/202608230007_notion_projection_views.sql`
- Modify: `tests/sql/rtdb_schema_contract.sql`

**Interfaces:**
- Produces: durable desired-state projection infrastructure consumed by Battle 5.

- [ ] **Step 1: Add RED assertions for sync objects/views**

Require:

```text
rt_sync.projection_outbox
rt_sync.notion_projection_map
rt_sync.projection_drift
rt_ledger.projection_receipts
rt_ledger.sync_receipts
rt_projection.notion_case_projection_v1
rt_projection.notion_episode_projection_v1
rt_projection.notion_generator_projection_v1
rt_projection.notion_pit_blind_projection_v1
rt_projection.notion_contrast_projection_v1
rt_projection.notion_replay_projection_v1
rt_projection.notion_settlement_projection_v1
```

- [ ] **Step 2: Implement durable outbox**

`projection_outbox` includes `object_key`, `object_type`, target, contract version, source revision, desired hash, event type enum/check (`CREATE_OR_UPDATE`, `RELATION_REFRESH`, `DEPRECATE`, `REBUILD`, `VERIFY`), status, attempt count, available/claimed timestamps, last error class.

Add `private.claim_projection_jobs(batch_size int)` using `for update skip locked` and `private.complete_projection_job(...)` / `private.fail_projection_job(...)` functions.

- [ ] **Step 3: Implement projection map uniqueness**

Enforce unique `(target_database_key, object_key)`. Store desired/applied source revision and hashes separately, plus Notion page ID and contract version.

- [ ] **Step 4: Create seven versioned projection views**

The PIT blind view must expose only PIT-safe fields. Add a SQL test that inspects `information_schema.columns` and fails if the blind view contains any of:

```text
future_return
settlement_verdict
future_settlement
final_gold_role
post_pit_generator
later_engine_transition
outcome_observation
```

- [ ] **Step 5: Run SQL tests**

Expected: PASS, including outbox claim idempotency and blind-view negative column audit.

- [ ] **Step 6: Commit**

```bash
git add infra/supabase/rtdb/migrations/202608230006_projection_and_sync.sql infra/supabase/rtdb/migrations/202608230007_notion_projection_views.sql tests/sql/rtdb_schema_contract.sql
git commit -m "feat: add RTDB projection and sync ledger"
```

### Task 3.3: Deploy migrations to staging/project and record migration receipts

**Files:**
- Create/modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Consumes: exact migration files from Tasks 2–3.
- Produces: live Supabase schema with migration hashes recorded in RTDB0 state; no Dashboard-only schema edits.

- [ ] **Step 1: Apply migrations in lexical order through the Supabase SQL/migration connector**

Never paste a divergent Dashboard-only schema. Calculate/store each migration file SHA-256 in the deployment receipt.

- [ ] **Step 2: Execute live PIT and ledger negative probes**

On the live project, insert disposable transaction fixtures and verify the same exact failures as CI: future evidence rejected, frozen PIT mutation rejected, receipt mutation rejected, blind projection lacks future fields. Roll back fixtures.

- [ ] **Step 3: Record live qualification**

Set `database_qualification` with project ref, applied migration hashes, and `pit_negative_tests: PASS`.

- [ ] **Step 4: Commit receipt metadata**

```bash
git add docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: qualify Supabase data plane"
```

---

# Battle 4 — Notion Think-Tank Construction

### Task 4.1: Encode the 1+7 Notion schema and ownership manifest before creating databases

**Files:**
- Create: `infra/supabase/rtdb/projection/notion/notion-rtdb-v1.json`
- Create: `infra/supabase/rtdb/projection/notion/field-ownership-v1.json`
- Create: `scripts/validate_rtdb0_notion_manifest.py`
- Create: `docs/rtdb/notion-portal.md`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_rtdb0_architecture.py`

**Interfaces:**
- Produces: deterministic seven-database manifest and projection ownership contract.

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

Require every property to declare one ownership class from `MACHINE`, `HUMAN`, `PROPOSAL`, `DERIVED_NOTION`.

- [ ] **Step 2: Implement the manifest**

The manifest must encode database title, parent binding key (`investment_parent_page_id`), property names/types, relation target keys, audience, required front-end views, and template key.

Machine-owned common properties include:

```text
Object Key
Source Object Type
Source Revision
Projection Revision
Projection State
Last Synced
Sync Status
```

Human body fields such as Hero/Teaching Hook/Editorial Summary remain HUMAN and are excluded from machine hash.

- [ ] **Step 3: Encode `1 + 6` template identifiers and portal doors**

Templates:

```text
research_passport
gold_episode
generator
pit_blind
contrast_pair
replay_dossier
reality_settlement
```

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

- [ ] **Step 4: Implement validator and CI hook**

`validate_rtdb0_notion_manifest.py` fails if:

- a DB/property lacks ownership;
- PIT views expose future fields;
- one object is duplicated per audience instead of shared;
- projector is allowed to own page-body content;
- KOR is redefined as a second RTDB global registry.

Add CI line:

```yaml
      - run: python scripts/validate_rtdb0_notion_manifest.py
```

- [ ] **Step 5: Run tests/validator**

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add infra/supabase/rtdb/projection/notion docs/rtdb/notion-portal.md scripts/validate_rtdb0_notion_manifest.py tests/test_rtdb0_architecture.py .github/workflows/ci.yml
git commit -m "RTDB0: freeze Notion projection manifest"
```

### Task 4.2: Create seven Notion databases and RTDB portal from the manifest

**Files:**
- Modify after live creation: `docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Consumes: resolved Notion parent and manifest.
- Produces: live specialized DBs, portal page, views, and template skeletons; preserves existing Knowledge Object Registry as global identity authority.

- [ ] **Step 1: Fetch current Notion enhanced-markdown and view-DSL specs immediately before writes**

Use the Notion connector documentation resources required by the platform; do not guess property/view syntax.

- [ ] **Step 2: Create the RTDB portal under the observed `原力投研` parent**

Title:

```text
原力历史右尾数据库｜Right-Tail Historical Intelligence
```

Hero question:

```text
世界如何生成少数极端赢家？
```

Callout:

```text
这不是十倍股名单；这是右尾生成机制的历史实验室。
```

- [ ] **Step 3: Create the seven databases exactly once**

Use exact manifest titles/properties. After each creation, record Notion database/data-source IDs in `RTDB0-ENVIRONMENT.json` under stable DB keys.

- [ ] **Step 4: Add relations only after all seven identities exist**

This is the live counterpart of two-pass projection. Create Case→Episode, Episode↔Generator, Episode→PIT, Pair relations, Replay relations, Settlement relations only after target DB IDs are known.

- [ ] **Step 5: Create portal views and template skeletons**

Build the D4 views and `1+6` skeletons. PIT Blind views must hide settlement/future outcome/final Gold role. Backend operational views remain separated from front-end Think Tank views.

- [ ] **Step 6: Verify no existing global registry was replaced**

Fetch `Knowledge Object Registry` and prove it still exists as the global directory. RTDB specialized DBs may later project selected eligible objects into it; they do not supplant it.

- [ ] **Step 7: Record live Notion qualification and commit IDs**

```bash
git add docs/architecture/rtdb0/RTDB0-ENVIRONMENT.json docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: construct Notion Think Tank"
```

---

# Battle 5 — Idempotent Supabase → Notion Projector and Reconciliation

### Task 5.1: Implement deterministic machine-payload hashing and patch selection with RED Deno tests

**Files:**
- Create: `infra/supabase/rtdb/functions/_shared/projection.ts`
- Create: `infra/supabase/rtdb/functions/_shared/projection_test.ts`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Produces:
  - `canonicalMachinePayload(record, ownership): Record<string, unknown>`
  - `sha256Json(value): Promise<string>`
  - `machinePatch(desired, observed, ownership): Record<string, unknown>`
- Consumed by both Edge Functions.

- [ ] **Step 1: Write RED Deno tests**

Tests must prove:

```typescript
Deno.test("human fields are excluded from machine payload", async () => {
  const record = { "Object Key": "RTEP-NVDA-GENAI-2022", "Primary Engine": "R", "Hero": "human copy" }
  const ownership = { "Object Key": "MACHINE", "Primary Engine": "MACHINE", "Hero": "HUMAN" }
  const payload = canonicalMachinePayload(record, ownership)
  if ("Hero" in payload) throw new Error("human field leaked into machine payload")
})

Deno.test("same machine payload hashes identically regardless of key order", async () => {
  const a = await sha256Json({a: 1, b: 2})
  const b = await sha256Json({b: 2, a: 1})
  if (a !== b) throw new Error("hash is not canonical")
})
```

- [ ] **Step 2: Run RED**

Run:

```bash
deno test infra/supabase/rtdb/functions/_shared/projection_test.ts
```

Expected: FAIL because implementation is absent.

- [ ] **Step 3: Implement pure functions with no network dependencies**

Canonical JSON sorts object keys recursively before hashing with `crypto.subtle.digest("SHA-256", ...)`. `machinePatch` returns only changed MACHINE properties; HUMAN/PROPOSAL/DERIVED_NOTION are ignored.

- [ ] **Step 4: Run GREEN**

Expected: PASS.

- [ ] **Step 5: Add Deno setup/test to CI without changing protected job names**

Add `denoland/setup-deno@v2` to the `contracts` job and run the focused Deno test. Existing Python checks remain intact.

- [ ] **Step 6: Commit**

```bash
git add infra/supabase/rtdb/functions/_shared .github/workflows/ci.yml
git commit -m "feat: add deterministic RTDB projection core"
```

### Task 5.2: Implement Notion projector worker

**Files:**
- Create: `infra/supabase/rtdb/functions/notion-projector/index.ts`
- Modify: `infra/supabase/rtdb/functions/_shared/projection_test.ts`

**Interfaces:**
- Consumes: `projection_outbox`, seven `rt_projection.notion_*_v1` views, ownership manifest, Notion token secret, projection map.
- Produces: idempotent CREATE/PATCH/NOOP/DEPRECATE/RELATION_REFRESH operations plus append-only sync/projection receipts.

- [ ] **Step 1: Add RED tests for decision logic**

Cover:

```text
mapping absent                  → CREATE
mapping exists + same hash      → NOOP
mapping exists + changed hash   → PATCH machine fields only
dependency page missing         → DEPENDENCY_WAIT
Notion schema mismatch          → BLOCKED_SCHEMA
one key mapped to two pages     → BLOCKED_CONFLICT
deprecated source               → set projection state; never hard-delete
```

Keep network calls behind functions that can be replaced with in-memory fakes in tests.

- [ ] **Step 2: Implement worker flow**

Exact flow:

```text
claim jobs
→ load projection row by object_key
→ load ownership/target contract
→ calculate desired machine hash
→ lookup projection map
→ create identity page when absent
→ patch machine properties when changed
→ refresh relations only after target mappings exist
→ verify observed machine state
→ append projection/sync receipt
→ complete or classify job
```

Use native `fetch` for Notion REST calls. Tokens are read only from Edge Function secrets. Never log secret values or full sensitive headers.

- [ ] **Step 3: Implement fail-closed error classification**

Map network/429/5xx to `RETRYABLE`; missing dependencies to `DEPENDENCY_WAIT`; property/schema incompatibility to `BLOCKED_SCHEMA`; auth failures to `BLOCKED_AUTH`; duplicate identity to `BLOCKED_CONFLICT`; exhaustion beyond configured retry policy to `DEAD_LETTER`.

- [ ] **Step 4: Run Deno tests**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add infra/supabase/rtdb/functions/notion-projector infra/supabase/rtdb/functions/_shared/projection_test.ts
git commit -m "feat: add idempotent RTDB Notion projector"
```

### Task 5.3: Implement daily reconciliation worker

**Files:**
- Create: `infra/supabase/rtdb/functions/notion-reconcile/index.ts`
- Modify: `infra/supabase/rtdb/functions/_shared/projection_test.ts`

**Interfaces:**
- Produces: drift evidence and repair jobs; never blindly rewrites all pages.

- [ ] **Step 1: Add RED drift tests**

Test detection of:

```text
MISSING_PROJECTION
PAYLOAD_DRIFT
RELATION_DRIFT
CONTRACT_VERSION_DRIFT
SCHEMA_DRIFT
```

and prove HUMAN body differences are not reported as payload drift.

- [ ] **Step 2: Implement reconciliation**

For each published desired projection, compare map/page existence, machine-owned properties, applied source revision/hash, relation integrity, and contract version. Insert `rt_sync.projection_drift` and enqueue `VERIFY`/repair events; do not patch directly inside reconciliation.

- [ ] **Step 3: Schedule daily invocation in Supabase**

Use `pg_cron` + `pg_net` to invoke the reconcile Edge Function once daily. Store the callable secret in Supabase Vault/Edge Function secrets, never literal SQL/GitHub. The schedule is infrastructure, not research authority.

- [ ] **Step 4: Deploy Edge Functions and run staging smoke test**

Create one disposable projection object, run projector twice, verify first operation CREATE and second NOOP, edit a HUMAN page-body paragraph, run projector again, verify paragraph survives unchanged.

- [ ] **Step 5: Record projection qualification**

Update RTDB0 state with `idempotency: PASS`, `human_body_preservation: PASS`, `schema_drift_fail_closed: PASS`, `pit_projection_leakage: 0`.

- [ ] **Step 6: Commit**

```bash
git add infra/supabase/rtdb/functions/notion-reconcile infra/supabase/rtdb/functions/_shared/projection_test.ts docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "feat: add RTDB projection reconciliation"
```

---

# Battle 6 — NVIDIA Generative AI 2022 Genesis E2E Proof

### Task 6.1: Build source-aware NVIDIA historical bundle and one cross-era boundary contrast

**Files:**
- Create: `reconstructions/rtdb/nvidia-genai-2022/case.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/episode.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/pit-2022-11-30.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/contrast-pair.json`
- Create/modify: `tests/test_rtdb0_genesis.py`

**Interfaces:**
- Produces: first validated `Case × PIT` bundle and a boundary comparison designed to test structural truth versus price prepayment.

- [ ] **Step 1: Write RED Genesis schema tests**

Load each object through the corresponding JSON Schema and assert the NVIDIA PIT uses exact cutoff `2022-11-30T23:59:59Z` unless primary-source availability verification during execution requires an earlier conservative cutoff. Any change must be recorded in the object’s revision reason rather than silently adjusted.

- [ ] **Step 2: Research only primary/authoritative historical evidence with publication-time verification**

For every evidence source record, capture `source_locator`, `published_at`, `first_available_at`, retrieval date, and claim supported/refuted. Candidate evidence types include NVIDIA filings/earnings materials, CUDA/developer-platform releases, and contemporaneous primary product/company announcements. Secondary commentary may be stored only as external context, not as primary claim authority.

- [ ] **Step 3: Freeze the NVIDIA GenAI episode and PIT**

Episode key:

```text
RTEP-NVDA-GENAI-2022
```

PIT key:

```text
PIT-NVDA-GENAI-20221130
```

PIT stores Known/Inferred/Unknown separately and excludes 2023 earnings/outcome evidence by construction.

- [ ] **Step 4: Create the Cisco 2000 boundary contrast explicitly as cross-era, not same-date twin**

The pair must be labeled `BOUNDARY_CROSS_ERA` and state the research question: structural truth and value concentration can coexist with price prepayment. It must not claim Cisco and NVIDIA shared the same historical date or identical business mechanics.

If ex-ante matching review rejects Cisco as the primary contrast, retain it as a boundary case and admit a better matched contrast through the same protocol; do not force the pair for narrative convenience.

- [ ] **Step 5: Run Genesis tests**

Expected: PASS schema validation, no post-cutoff evidence, explicit pair-type/confounders, no outcome field in PIT.

- [ ] **Step 6: Commit**

```bash
git add reconstructions/rtdb/nvidia-genai-2022 tests/test_rtdb0_genesis.py
git commit -m "data: add NVIDIA RTDB Genesis PIT bundle"
```

### Task 6.2: Seed NVIDIA objects into Supabase and prove PIT fail-closed behavior live

**Files:**
- Create: `infra/supabase/rtdb/seeds/nvidia-genesis.sql`
- Modify: `tests/test_rtdb0_genesis.py`

**Interfaces:**
- Produces: live case/episode/generator activations/PIT/evidence/pair objects with stable Object Keys.

- [ ] **Step 1: Generate deterministic seed SQL from validated JSON objects**

Seed uses upsert only on stable `object_key` for mutable pre-freeze identity records and insert-only revision semantics for frozen PIT/receipts. It never overwrites a frozen PIT.

- [ ] **Step 2: Apply seed to staging/live RTDB project**

Verify all FKs and unique object keys.

- [ ] **Step 3: Attempt one deliberate future-evidence link**

Use an evidence version with `first_available_at` after the 2022-11-30 cutoff and verify live database rejects it with `RTDB_PIT_EVIDENCE_AFTER_CUTOFF`. Roll back the deliberate negative fixture.

- [ ] **Step 4: Freeze the PIT and prove mutation rejection**

Attempt to change cutoff and verify `RTDB_PIT_FROZEN_IMMUTABLE`.

- [ ] **Step 5: Commit seed**

```bash
git add infra/supabase/rtdb/seeds/nvidia-genesis.sql tests/test_rtdb0_genesis.py
git commit -m "data: seed NVIDIA RTDB Genesis case"
```

### Task 6.3: Define and run the first replay / benchmark / ablation / settlement chain

**Files:**
- Create: `reconstructions/rtdb/nvidia-genai-2022/replay-experiment.json`
- Create: `reconstructions/rtdb/nvidia-genai-2022/settlement.json`
- Modify: `tests/test_rtdb0_genesis.py`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Consumes: accepted capability contracts available at execution-time main; if a capability is not runtime-ready, the replay is marked `UNDERIDENTIFIED` rather than fabricating output.
- Produces: first auditable replay/benchmark/ablation receipt and explicit settlement/capability delta.

- [ ] **Step 1: Write RED replay contract tests**

Require experiment fields: capability ID/version, Canon revision/hash, positive/contrast PIT IDs, hypothesis, simple baseline, metrics, leakage policy, success criteria. Require settlement verdict and capability-delta state.

- [ ] **Step 2: Bind exact runtime versions**

Use execution-time GitHub SHA, actual capability version(s), exact PIT evidence bundle hash, and provider/runtime ID. No `latest` aliases.

- [ ] **Step 3: Run simple baseline first**

The baseline must use a smaller observable set than the Yuanli capability, e.g. a pre-registered simple concentration/market-share/valuation heuristic suitable to the question. Record baseline output before inspecting full-capability result.

- [ ] **Step 4: Run capability replay and ablation**

Run the relevant accepted capability chain under the frozen PIT. Remove at least one major generator observable family (e.g. ecosystem control) and rerun to measure whether discrimination changes. If runtime capability is unavailable, record `REPLAY_INVALID`/`UNDERIDENTIFIED` and stop Gold promotion rather than simulating success.

- [ ] **Step 5: Create settlement without mutating PIT**

Use post-PIT outcome observations only in the separate settlement object. Resolve original claims as `SUPPORTED`, `CONTRADICTED`, `UNRESOLVED`, or mechanism/outcome-mismatch verdict. End with exactly one capability delta: `REVISION_REQUIRED`, `NO_REVISION_REQUIRED`, or `DESCRIPTIVE_ONLY`.

- [ ] **Step 6: Re-run same replay inputs to test reproducibility**

Same Canon revision, capability version, code commit, PIT snapshot, evidence bundle, and provider mode must reproduce the typed result/receipt within the capability’s declared deterministic tolerance. Record both receipt IDs and comparison.

- [ ] **Step 7: Update G1–G4/G6 provisional qualification state**

Do not mark `GENESIS_QUALIFIED` yet; Projection Integrity G5 requires Notion proof in Task 6.4.

- [ ] **Step 8: Commit**

```bash
git add reconstructions/rtdb/nvidia-genai-2022/replay-experiment.json reconstructions/rtdb/nvidia-genai-2022/settlement.json tests/test_rtdb0_genesis.py docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: run NVIDIA Genesis replay settlement"
```

### Task 6.4: Project NVIDIA E2E into Notion and verify human/PIT protections

**Files:**
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`

**Interfaces:**
- Produces: live Case, Gold Episode, Generator, PIT Blind, Contrast, Replay Dossier, and Settlement projection linked by stable Object Keys.

- [ ] **Step 1: Enqueue NVIDIA projection objects in topological order**

Case + Generator → Episode → PIT + Contrast → Replay → Settlement → relation refresh.

- [ ] **Step 2: Run projector to convergence**

Verify each Object Key maps to exactly one Notion page and applied source revision/hash equals desired state.

- [ ] **Step 3: Inspect PIT Blind projection manually and via manifest audit**

There must be no future settlement verdict, 2023+ outcome, final Gold result, or future generator activation in the blind page/properties/view.

- [ ] **Step 4: Edit a Human Zone paragraph and rerun projector twice**

Expected: first rerun NOOP/PATCH only machine fields if needed; human paragraph remains byte-for-byte unchanged in Notion. Second rerun must be NOOP for unchanged machine payload.

- [ ] **Step 5: Verify Reveal Reality is a separate Settlement page**

The relation/link title must not contain verdict text that leaks the answer before entry.

- [ ] **Step 6: Mark NVIDIA E2E proof PASS only if G1–G6 all pass**

Record `nvidia_genesis_e2e: PASS`, exact receipts, Notion page IDs, and `pit_leakage_violations: 0`.

- [ ] **Step 7: Commit qualification receipt**

```bash
git add docs/architecture/rtdb0/RTDB0-STATE.json
git commit -m "RTDB0: qualify NVIDIA Genesis E2E"
```

---

# Battle 7 — 12+12 Genesis Expansion, Final Qualification, and Human Review

### Task 7.1: Promote matched pairs only after ex-ante review

**Files:**
- Modify: `reconstructions/rtdb/genesis-manifest-v0.1.json`
- Modify: `docs/rtdb/genesis-set.md`
- Modify: `tests/test_rtdb0_genesis.py`

**Interfaces:**
- Produces: 12 Gold case-family/episode entries each with at least one accepted contrast or an explicit `PAIR_BLOCKED` state; no silent pair gaps.

- [ ] **Step 1: Add RED coverage test**

```python
class RTDB0GenesisCoverageTests(unittest.TestCase):
    def test_each_gold_has_qualified_contrast_or_is_blocked(self):
        manifest = json.loads((ROOT / "reconstructions/rtdb/genesis-manifest-v0.1.json").read_text())
        for item in manifest["gold_case_families"]:
            self.assertIn(item["pair_admission_state"], {"ACCEPTED", "PAIR_BLOCKED"})
            if item["pair_admission_state"] == "ACCEPTED":
                self.assertGreaterEqual(len(item["accepted_contrast_keys"]), 1)
```

- [ ] **Step 2: Research/validate each pair using the hard-negative protocol**

Starting candidates may include Amazon↔Webvan, Apple↔Nokia/BlackBerry, Tencent↔Renren, and suitable boundary/negative analogues for other Gold families. Every admitted pair records ex-ante matching dimensions, confounders, and minimum discriminator. If no defensible contrast exists, mark `PAIR_BLOCKED` and do not promote that Gold to discrimination-grade.

- [ ] **Step 3: Run coverage test**

Expected: PASS only when all 12 are either defensibly paired or transparently blocked.

- [ ] **Step 4: Commit**

```bash
git add reconstructions/rtdb/genesis-manifest-v0.1.json docs/rtdb/genesis-set.md tests/test_rtdb0_genesis.py
git commit -m "data: settle RTDB Genesis contrast coverage"
```

### Task 7.2: Expand PIT/evidence/replay coverage incrementally with quality gates

**Files:**
- Add case-family directories under `reconstructions/rtdb/` for the remaining Genesis families.
- Add corresponding seed/replay records through existing contracts; do not create new schema families unless a validated need appears.
- Modify: `tests/test_rtdb0_genesis.py`

**Interfaces:**
- Produces: approximately 3–5 meaningful PITs per admitted Gold episode and replay/settlement coverage sufficient for final gate evaluation.

- [ ] **Step 1: For each case family, create PITs only at meaningful epistemic milestones**

Allowed milestone roles include `SEED`, `EVIDENCE`, `IGNITION`, `EXPANSION`, `MATURITY`, `BREAK`, `POST_MORTEM`; a milestone label does not substitute for evidence-cutoff discipline.

- [ ] **Step 2: Validate every evidence bundle before seeding**

Reject evidence with missing `first_available_at`; do not infer availability from the period the data describes.

- [ ] **Step 3: Seed and freeze accepted PITs through the same Supabase path**

Never bypass migrations/constraints with manual dashboard writes.

- [ ] **Step 4: Run replay/benchmark/settlement only where the capability/runtime is actually qualified**

Unavailable capabilities produce `UNDERIDENTIFIED`/blocked coverage, not fabricated success.

- [ ] **Step 5: Project curated Gold objects to Notion**

Do not project raw evidence warehouse rows or every runtime run. Project accepted/review-worthy dossiers only.

- [ ] **Step 6: Run all architecture/Genesis tests**

```bash
python scripts/validate_rtdb0_architecture.py
python scripts/validate_rtdb0_notion_manifest.py
python -m unittest tests.test_rtdb0_architecture tests.test_rtdb0_genesis -v
deno test infra/supabase/rtdb/functions/_shared/projection_test.ts
```

Expected: PASS.

- [ ] **Step 7: Commit in small case-family batches**

Use one commit per independently reviewable case-family batch, e.g.:

```bash
git commit -m "data: add Amazon RTDB Genesis replay"
git commit -m "data: add Apple RTDB Genesis replay"
```

Do not squash away individual research lineage before review.

### Task 7.3: Run six Gold Acceptance Gates and create final Human Review package

**Files:**
- Create: `docs/architecture/rtdb0/RTDB0-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `docs/architecture/rtdb0/RTDB0-STATE.json`
- Modify: `scripts/validate_rtdb0_architecture.py`

**Interfaces:**
- Produces: final machine qualification and Human Review package; does not authorize protected-branch merge by itself.

- [ ] **Step 1: Extend validator with six-gate checks**

Machine-checkable dimensions:

```text
G1 Semantic Integrity
G2 PIT Integrity
G3 Experimental Integrity
G4 Reproducibility
G5 Projection Integrity
G6 Reality Learning
```

Any PIT leakage violation hard-fails G2. Any projector human-body overwrite hard-fails G5. Any Gold silently lacking contrast hard-fails G3 unless explicitly `PAIR_BLOCKED` and therefore not Gold-promoted.

- [ ] **Step 2: Run full repository CI locally/through PR exact head**

Run all existing repository gates plus RTDB validators and Deno tests. Then fetch GitHub exact-head status and require protected `contracts` + `governance` green.

- [ ] **Step 3: Build Human Review Card**

The card presents evidence for each gate: exact commit SHA, Supabase project ref (non-secret), migration hashes, PIT leakage count, replay receipts, projection receipts, Notion portal IDs, unresolved/blocked cases, and capability deltas.

- [ ] **Step 4: Set state to machine-qualified, not merged**

If all six gates pass:

```json
{
  "state": "GENESIS_QUALIFIED_READY_FOR_HUMAN_REVIEW",
  "gates": {
    "G1": "PASS",
    "G2": "PASS",
    "G3": "PASS",
    "G4": "PASS",
    "G5": "PASS",
    "G6": "PASS"
  },
  "merge_authorized": false,
  "canon_promotion_authorized": false
}
```

If any gate fails, preserve the actual failure state; do not partially label the system `GENESIS_QUALIFIED`.

- [ ] **Step 5: Commit final qualification package**

```bash
git add docs/architecture/rtdb0 scripts/validate_rtdb0_architecture.py
git commit -m "RTDB0: prepare Genesis Human Review"
```

### Task 7.4: Create/update a single implementation PR and stop at Human Review / merge authority

**Files:**
- No new production files required.

**Interfaces:**
- Produces: one reviewable PR from implementation branch to protected `main` with complete Battle 0–7 evidence.

- [ ] **Step 1: Compare implementation head to current `main`**

Verify no unrelated files changed and no accepted YIP0/ME0/ME1 authority was rewritten.

- [ ] **Step 2: Create/update PR**

PR title:

```text
RTDB0: build right-tail historical intelligence testbench
```

PR body must include: authority boundary, six gates, NVIDIA E2E receipts, Supabase/Notion non-secret bindings, unresolved/blocked Genesis pairs, CI exact-head status, and explicit statement `MERGE NOT AUTHORIZED BY IMPLEMENTATION PLAN`.

- [ ] **Step 3: Fetch exact-head protected checks**

Require `contracts` and `governance` green on PR head. If any check is pending/failing, report exact status and remain blocked.

- [ ] **Step 4: Stop for final Human Review / merge authorization**

Do not merge protected `main`, do not declare final Canon promotion, and do not convert blocked cases into Gold without owner review.

---

## Final Verification Matrix

Before claiming RTDB0 implementation complete, verify all of the following in one final pass:

| Requirement | Evidence |
|---|---|
| GitHub remains semantic authority | Spec/constitution + migration/projection manifests in repo |
| Supabase isolated from health project | Observed project ref for `yuanli-invest-data` |
| Case/episode separation | JSON schemas + seeded NVIDIA objects |
| PIT evidence cutoff | DB trigger negative test + live receipt |
| Frozen PIT immutability | DB trigger negative test + live receipt |
| Gold × contrast discipline | Genesis manifest + pair review evidence |
| Baseline/ablation replay | Replay experiment/run/benchmark receipts |
| Outcome != settlement | Separate outcome/settlement tables + JSON objects |
| Receipt append-only | SQL mutation-negative tests |
| Seven Notion DBs | Live IDs in environment binding |
| One Research Passport + six templates | Notion manifest + live portal |
| Human body preserved | Projector smoke test receipt |
| Idempotent projection | CREATE then NOOP proof |
| PIT blind no future fields | SQL view audit + Notion inspection |
| Daily reconciliation | pg_cron/job + reconcile receipt |
| NVIDIA E2E | G1–G6 evidence |
| 12+12 Genesis quality | admitted pairs or explicit blocks; no silent gaps |
| Protected CI | exact-head `contracts` + `governance` green |

## Final Stop Conditions

Execution must stop rather than improvise if any of these occur:

- Supabase project creation is billable and explicit cost confirmation has not been received.
- Exact `main` baseline is failing before RTDB changes and the failure cannot be proven unrelated.
- A PIT source lacks a defensible `first_available_at`.
- A Gold/contrast pair cannot be justified ex ante.
- A runtime capability required by a replay is not actually available/qualified.
- Notion schema observed at runtime differs from the approved manifest.
- Projector would need to overwrite HUMAN content to converge.
- Any PIT blind path exposes future outcome/settlement data.
- Protected `contracts` or `governance` checks fail at PR exact head.
- A protected-branch merge or destructive external action lacks explicit owner authority.
