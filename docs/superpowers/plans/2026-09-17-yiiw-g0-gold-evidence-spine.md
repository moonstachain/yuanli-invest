# YIIW-G0 Gold Evidence Spine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one production-grade GOLD vertical slice from Wind reality to immutable raw evidence, PIT observation, deterministic GoldState@PIT, Research API, and legacy macro Workbench readback with end-to-end lineage and no authority escalation.

**Architecture:** Reuse the existing `evidence.sources` / `evidence.source_snapshots` / `pit.observations` / private raw-evidence storage substrate. Add only the missing semantic contracts, registries, model-run/state metadata, narrow read API, and Workbench projection. Existing GOLD2 scientific conclusions and G6/G7 runtime remain operational and are wrapped rather than rewritten.

**Tech Stack:** Python 3.12; LinkML 1.11.1; Pydantic 2.13.0; FastAPI 0.135.3; JSON Schema; Supabase PostgreSQL/Storage; stdlib hashing/JSON; existing Wind MCP CLI; Jinja2 legacy Workbench. DuckDB/Polars are explicitly deferred in G0 because the current Gold slice does not require them to prove the truth spine.

**Spec:** `docs/superpowers/specs/2026-09-17-yiiw-g0-gold-evidence-spine-production-backend-skeleton-design.md`

## Global Constraints

- Base implementation work on `origin/main@152c7a2b87ea5d5a196c129d82ab5a4eb18accc7` or a later exact `main` only after confirming no semantic conflict.
- Python runtime is `>=3.12`; use `python3.12` for tests and generators.
- Existing schemas/contracts are immutable historical identities; add successors instead of rewriting old semantics.
- Reuse `evidence.sources`, `evidence.source_snapshots`, `pit.observations`, `runtime.reality_gate_runs`, private Storage, and service-role-only access patterns.
- Do not create a competing raw/PIT truth database.
- Wind remains `EVIDENCE_ONLY`.
- No capital, sizing, execution, broker, VeighNa, accepted-learning, asset-promotion, or Canon-promotion authority may be granted.
- Raw provider bodies and credentials never enter Git, browser payloads, receipts, model prompts, or test fixtures.
- `observed_at`, `known_as_of`, and `retrieved_at` are distinct mandatory semantics.
- Frontend/UI/MCP may read only through the Research API; no direct operational-table access.
- Existing GOLD2 scientific outputs (`DRIFT_CANDIDATE`, `INDETERMINATE`, `UNIDENTIFIABLE`, etc.) are preserved unless a separate scientific gate changes them.
- G0 completion requires the six-part Genesis Reality Proof: `VALUE_MATCH`, `PIT_MATCH`, `LINEAGE_COMPLETE`, `MODEL_REPRODUCIBLE`, `AUTHORITY_VALID`, `UI_READBACK_MATCH`.

---

## File Structure to Lock Before Implementation

### `moonstachain/yuanli-invest`

- Modify: `pyproject.toml` — declare G0 runtime/dev dependencies.
- Create: `packages/contracts/linkml/yiiw-g0.yaml` — semantic source contract for the G0 object kernel.
- Create: `packages/contracts/schemas/yiiw/yiiw-g0.schema.json` — generated/frozen JSON Schema artifact.
- Create: `runtime/yiiw/__init__.py` — package marker only.
- Create: `runtime/yiiw/models.py` — Pydantic runtime contracts and canonical hashing helpers.
- Create: `runtime/yiiw/registries.py` — in-repo registry loader/validation for GOLD mappings and model definitions.
- Create: `runtime/yiiw/storage.py` — raw-evidence storage protocol plus Supabase Storage adapter.
- Create: `runtime/yiiw/providers/wind_gold.py` — Wind query, raw capture, identity normalization, typed failure mapping.
- Create: `runtime/yiiw/analytics/gold_state.py` — deterministic wrapper around accepted GOLD2 state semantics.
- Create: `runtime/yiiw/repository.py` — repository interface plus Supabase service-role implementation.
- Create: `runtime/yiiw/lineage.py` — lineage traversal and completeness validation.
- Create: `api/yiiw/__init__.py` — package marker.
- Create: `api/yiiw/app.py` — FastAPI read surface.
- Modify: `api/openapi.yaml` — add G0 endpoints to the existing internal API contract; do not create a parallel public API.
- Create: `supabase/migrations/20260917_yiiw_g0_truth_spine.sql` — additive registries/model-run/state metadata, RLS, service-role readback RPCs.
- Create: `scripts/yiiw_g0_reality_proof.py` — one-shot live/private Genesis Reality Proof runner.
- Create: `tests/test_yiiw_g0_contracts.py`
- Create: `tests/test_yiiw_g0_migration_contract.py`
- Create: `tests/test_yiiw_g0_wind_adapter.py`
- Create: `tests/test_yiiw_g0_gold_state.py`
- Create: `tests/test_yiiw_g0_api.py`
- Create: `tests/test_yiiw_g0_lineage.py`
- Create: `tests/test_yiiw_g0_governance.py`
- Create: `docs/architecture/yiiw/YIIW-G0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md`
- Create: `docs/architecture/yiiw/YIIW-G0-HUMAN-REVIEW-CARD-v0.1.md`

### `moonstachain/yiru-macro-cockpit` dependent projection task

- Create: `pipelines/yuanli_workbench_adapter.py` — read-only Research API client; no local investment logic.
- Modify: `pipelines/99_render.py` — optionally inject `yuanli_gold` projection when `YUANLI_RESEARCH_API_BASE` is configured.
- Modify: `templates/dashboard.html.j2` — render Gold Research State and Evidence Drawer from API payload only.
- Create: `tests/test_yuanli_workbench_adapter.py` — API-to-template projection contract.

---

### Task 1: Freeze the G0 semantic kernel and runtime contracts

**Files:**
- Modify: `pyproject.toml`
- Create: `packages/contracts/linkml/yiiw-g0.yaml`
- Create: `packages/contracts/schemas/yiiw/yiiw-g0.schema.json`
- Create: `runtime/yiiw/__init__.py`
- Create: `runtime/yiiw/models.py`
- Test: `tests/test_yiiw_g0_contracts.py`

**Interfaces:**
- Produces Pydantic classes: `SourceReceipt`, `Evidence`, `ModelRun`, `StateAtPIT`, `LineageRef`, `AuthorityRef`.
- Produces helper: `canonical_sha256(value: BaseModel | Mapping[str, Any]) -> str`.
- Later tasks consume these exact names.

- [ ] **Step 1: Add dependency declarations only; do not install extra quant engines**

Set `pyproject.toml` runtime dependencies to include exactly the currently qualified runtime versions:

```toml
dependencies = [
  "fastapi==0.135.3",
  "pydantic==2.13.0",
]

[project.optional-dependencies]
dev = [
  "httpx==0.28.1",
  "jsonschema==4.26.0",
  "linkml==1.11.1",
]
```

Do not add DuckDB, Polars, Temporal, Supabase Python SDK, Kafka, or NATS in G0.

Install the declared Python 3.12 environment before running contract generation/tests:

```bash
python3.12 -m pip install -e '.[dev]'
python3.12 -c "import fastapi,pydantic,jsonschema,linkml; print('YIIW_G0_DEPS_OK')"
```

- [ ] **Step 2: Write failing contract tests**

The first tests must prove that time semantics cannot collapse and that forbidden authority cannot validate:

```python
import unittest
from pydantic import ValidationError


class YIIWG0ContractTests(unittest.TestCase):
    def test_evidence_requires_retrieved_at(self):
        with self.assertRaises(ValidationError):
            Evidence(
                evidence_id="EVD-X",
                provider="WIND",
                source_snapshot_id="SNAP-X",
                metric_id="GOLD_SPOT_USD_OZ",
                entity_id="GOLD",
                instrument_id="XAU_SPOT",
                value=4300.0,
                unit="USD/OZ",
                observed_at="2026-09-17T00:00:00Z",
                known_as_of="2026-09-17T00:00:00Z",
                raw_sha256="0" * 64,
                authority="REALITY_EVIDENCE",
                quality_state="VALID",
            )

    def test_state_rejects_capital_authority(self):
        with self.assertRaises(ValidationError):
            StateAtPIT(
                target_id="GOLD",
                as_of="2026-09-17T08:10:00Z",
                knowledge_cutoff="2026-09-17T08:10:00Z",
                evidence_refs=["EVD-GOLD"],
                model_run_refs=["RUN-GOLD"],
                property_drift_state="DRIFT_CANDIDATE",
                expectation_reality_state="INDETERMINATE",
                valuation_state="UNIDENTIFIABLE",
                research_state="WATCH",
                lifecycle_state="未知",
                unknowns=[],
                authority={
                    "research_authorized": True,
                    "capital_authorized": True,
                    "sizing_authorized": False,
                    "execution_authorized": False,
                    "broker_action": False,
                    "veighna_authorized": False,
                    "canon_promotion_authorized": False,
                },
                state_hash="0" * 64,
            )
```

- [ ] **Step 3: Run the focused test and verify RED**

Run:

```bash
python3.12 -m unittest tests.test_yiiw_g0_contracts -v
```

Expected: import/module failure because `runtime.yiiw.models` does not yet exist.

- [ ] **Step 4: Implement `yiiw-g0.yaml` and minimal Pydantic models**

LinkML classes must cover the Spec G0 kernel and explicitly type the three timestamps. Pydantic models must use `extra="forbid"` and reject any authority object that enables capital/sizing/execution/broker/VeighNa/Canon promotion.

Canonical hashing must serialize with sorted keys and compact separators before SHA-256.

- [ ] **Step 5: Generate and freeze JSON Schema**

Run:

```bash
gen-json-schema packages/contracts/linkml/yiiw-g0.yaml \
  > packages/contracts/schemas/yiiw/yiiw-g0.schema.json
```

Then validate that the generated file is non-empty JSON and contains `Evidence`, `ModelRun`, and `StateAtPIT` definitions.

- [ ] **Step 6: Run GREEN and full contract regression**

```bash
python3.12 -m unittest tests.test_yiiw_g0_contracts -v
python3.12 -m unittest discover -s tests -p 'test_*.py'
```

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml packages/contracts/linkml packages/contracts/schemas/yiiw runtime/yiiw tests/test_yiiw_g0_contracts.py
git commit -m "YIIW-G0: freeze evidence spine semantic kernel"
```

---

### Task 2: Add the additive Supabase control-plane metadata

**Files:**
- Create: `supabase/migrations/20260917_yiiw_g0_truth_spine.sql`
- Create: `runtime/yiiw/registries.py`
- Test: `tests/test_yiiw_g0_migration_contract.py`

**Interfaces:**
- Reuses existing `evidence.sources`, `evidence.source_snapshots`, `pit.observations`.
- Adds metadata tables only: `evidence.entities`, `evidence.metrics`, `evidence.instruments`, `evidence.provider_mappings`, `runtime.model_definitions`, `runtime.model_runs`, `runtime.research_states`.
- Produces registry lookup: `resolve_provider_metric(provider: str, provider_code: str) -> MetricBinding`.

- [ ] **Step 1: Write migration-contract tests before SQL**

Tests must read the migration text and assert:

```python
assert "create table if not exists evidence.metrics" in sql
assert "create table if not exists runtime.model_runs" in sql
assert "create table if not exists pit.observations" not in sql
assert "enable row level security" in sql
assert "grant execute" in sql
assert "anon" in sql and "authenticated" in sql
```

Also assert the migration seeds the three Genesis bindings:

- `WIND:S0031645 -> GOLD_SPOT_USD_OZ`
- `WIND:G1147404 -> US_LONG_REAL_YIELD`
- `WIND:M0000271 -> DXY`

- [ ] **Step 2: Run RED**

```bash
python3.12 -m unittest tests.test_yiiw_g0_migration_contract -v
```

Expected: missing migration file / missing objects.

- [ ] **Step 3: Implement additive SQL with fail-closed constraints**

Requirements:

```sql
check (authority_ceiling in ('EVIDENCE_ONLY','RESEARCH_ONLY'))
check (known_as_of <= as_of)
check (capital_authorized = false)
check (execution_authorized = false)
```

Do not duplicate `source_snapshots` or `pit.observations`. Use foreign keys to them.

Create narrow service-role functions:

- `public.yiiw_g0_read_state(p_target_id text, p_as_of timestamptz)`
- `public.yiiw_g0_read_evidence(p_evidence_id text)`
- `public.yiiw_g0_read_lineage(p_object_id text)`

Revoke from `public`, `anon`, and `authenticated`; grant only to `service_role`.

- [ ] **Step 4: Implement registry loader against Git/SQL seed semantics**

`runtime/yiiw/registries.py` must expose immutable dataclasses/Pydantic objects for provider mapping and validate unit/PIT semantics before returning a binding.

- [ ] **Step 5: Run GREEN plus existing Supabase contract tests**

```bash
python3.12 -m unittest tests.test_yiiw_g0_migration_contract tests.test_ymq_os0_g1_supabase_contract -v
```

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260917_yiiw_g0_truth_spine.sql runtime/yiiw/registries.py tests/test_yiiw_g0_migration_contract.py
git commit -m "YIIW-G0: add governed truth-spine metadata"
```

---

### Task 3: Build the Wind raw-evidence adapter without touching G6/G7 behavior

**Files:**
- Create: `runtime/yiiw/storage.py`
- Create: `runtime/yiiw/providers/__init__.py`
- Create: `runtime/yiiw/providers/wind_gold.py`
- Test: `tests/test_yiiw_g0_wind_adapter.py`

**Interfaces:**
- Produces `RawObjectRef(bucket: str, path: str, sha256: str)`.
- Produces `WindObservation(raw_text: str, provider_code: str, metric_name: str, unit: str, observed_at: datetime, value: float)`.
- Produces `compile_wind_evidence(observation, binding, retrieved_at, snapshot_id) -> Evidence`.

- [ ] **Step 1: Write RED tests using sanitized fixture strings only**

Test that:

- exact provider code is required;
- unit mismatch raises `UNIT_MISMATCH`;
- missing date raises `PIT_MISSING`;
- `raw_sha256` matches the exact raw string;
- raw body never appears in returned `Evidence.model_dump()`;
- provider authority remains `REALITY_EVIDENCE` / `EVIDENCE_ONLY`.

- [ ] **Step 2: Run RED**

```bash
python3.12 -m unittest tests.test_yiiw_g0_wind_adapter -v
```

- [ ] **Step 3: Implement storage protocol**

Define:

```python
class RawEvidenceStore(Protocol):
    def put(self, *, content: bytes, source_id: str, retrieved_at: datetime) -> RawObjectRef:
        raise NotImplementedError
```

Implement a Supabase Storage adapter using HTTP with server-side environment variables only. It must never log authorization headers or raw bodies.

Reuse the existing private bucket `ymq4-raw-evidence` for G0 under prefix `yiiw/gold/`; do not create a second authority bucket in this task.

- [ ] **Step 4: Implement Wind adapter as a separate boundary**

The adapter may reuse parsing knowledge from `scripts/ymq_gold2_live_shadow.py` but must not change that production runner. It invokes the existing local Wind MCP CLI, captures stdout in memory, stores the exact raw bytes privately, then emits normalized `Evidence` after registry resolution.

Typed failures must map to the Spec taxonomy (`AUTH_REJECTED`, `QUOTA_OR_CREDIT_BLOCK`, `METRIC_UNRESOLVED`, `UNIT_MISMATCH`, `PIT_MISSING`, `SOURCE_UNAVAILABLE`).

- [ ] **Step 5: Run GREEN and verify no secrets in diff**

```bash
python3.12 -m unittest tests.test_yiiw_g0_wind_adapter -v
git diff --check
python3 scripts/leak_guard.py
```

- [ ] **Step 6: Commit**

```bash
git add runtime/yiiw/storage.py runtime/yiiw/providers tests/test_yiiw_g0_wind_adapter.py
git commit -m "YIIW-G0: add Wind evidence admission boundary"
```

---

### Task 4: Register deterministic Gold analytics and compile GoldState@PIT

**Files:**
- Create: `runtime/yiiw/analytics/__init__.py`
- Create: `runtime/yiiw/analytics/gold_state.py`
- Test: `tests/test_yiiw_g0_gold_state.py`

**Interfaces:**
- Produces `compile_gold_state(*, evidence: Sequence[Evidence], as_of: datetime, code_sha: str) -> tuple[ModelRun, StateAtPIT]`.
- Consumes accepted GOLD2 configuration/state semantics; does not recompute or reinterpret scientific conclusions.

- [ ] **Step 1: Write determinism and PIT RED tests**

Tests must prove:

```python
run1, state1 = compile_gold_state(evidence=evd, as_of=t0, code_sha="a" * 40)
run2, state2 = compile_gold_state(evidence=evd, as_of=t0, code_sha="a" * 40)
assert run1.output_hash == run2.output_hash
assert state1.state_hash == state2.state_hash
```

And reject any input where `e.known_as_of > as_of`.

Also verify state authority contains only research permissions and retains current qualified GOLD2 labels rather than inventing new ones.

- [ ] **Step 2: Run RED**

```bash
python3.12 -m unittest tests.test_yiiw_g0_gold_state -v
```

- [ ] **Step 3: Implement `GOLD_LIVE_STATE_PROJECTION` wrapper**

For the Genesis proof, the executable model is a deterministic projection over three admitted daily inputs (`gold_price`, `real_rate`, `usd`) plus the versioned accepted GOLD2 research defaults/lineage. Register the broader model definitions (`GOLD_PROPERTY_DRIFT`, `GOLD_EXPECTATION_REALITY`, `GOLD_VALUATION_LENS`, `GOLD_STATE_DELTA`) as metadata, but do not rerun them merely to satisfy G0.

`ModelRun.input_evidence_ids` must be sorted before hashing. `StateAtPIT.evidence_refs` and `model_run_refs` must be explicit.

- [ ] **Step 4: Run GREEN and GOLD2 regressions**

```bash
python3.12 -m unittest tests.test_yiiw_g0_gold_state tests.test_ymq_gold2_compiler tests.test_ymq_gold2_live_shadow tests.test_ymq_gold2_learning_live -v
```

- [ ] **Step 5: Commit**

```bash
git add runtime/yiiw/analytics tests/test_yiiw_g0_gold_state.py
git commit -m "YIIW-G0: compile reproducible GoldState at PIT"
```

---

### Task 5: Add persistence repository and complete lineage traversal

**Files:**
- Create: `runtime/yiiw/repository.py`
- Create: `runtime/yiiw/lineage.py`
- Test: `tests/test_yiiw_g0_lineage.py`

**Interfaces:**
- Repository methods:
  - `save_snapshot(*, source_id: str, retrieved_at: datetime, sha256: str, storage_bucket: str, storage_path: str, request_template: str, runner_commit: str | None) -> str`
  - `save_observation(*, series_id: str, value_numeric: float, observation_date: date, release_date: date, vintage_date: date, known_as_of: date, snapshot_id: str, pit_status: str, measurement_regime: str | None) -> str`
  - `save_model_run(run: ModelRun) -> str`
  - `save_state(state: StateAtPIT) -> str`
  - `get_state(target_id: str, as_of: datetime | None) -> StateAtPIT | None`
  - `get_evidence(evidence_id: str) -> Evidence | None`
  - `get_model_run(model_run_id: str) -> ModelRun | None`
  - `get_lineage(object_id: str) -> dict[str, Any]`
- `validate_lineage_complete(lineage: Mapping[str, Any]) -> None` raises `LINEAGE_INCOMPLETE` on any broken edge.

- [ ] **Step 1: Write RED lineage tests with an in-memory repository fake**

The happy-path graph must be exactly:

`StateAtPIT -> ModelRun -> Evidence -> PIT Observation -> SourceSnapshot -> raw_sha256/storage_path`.

Delete each edge in subtests and assert validation fails closed.

- [ ] **Step 2: Run RED**

```bash
python3.12 -m unittest tests.test_yiiw_g0_lineage -v
```

- [ ] **Step 3: Implement repository protocol and Supabase service-role adapter**

Keep HTTP/DB details behind the repository interface. Browser/UI code must never import this module.

Use existing Supabase URL/service-role environment variables already established by YMQ4/YMQ-OS0; do not add secrets to configuration files.

- [ ] **Step 4: Implement lineage validation**

Lineage output must include IDs/hashes/versions only; raw provider body remains server-side and is never returned by `get_lineage`.

- [ ] **Step 5: Run GREEN**

```bash
python3.12 -m unittest tests.test_yiiw_g0_lineage -v
```

- [ ] **Step 6: Commit**

```bash
git add runtime/yiiw/repository.py runtime/yiiw/lineage.py tests/test_yiiw_g0_lineage.py
git commit -m "YIIW-G0: preserve state to raw-evidence lineage"
```

---

### Task 6: Build the narrow Research API and existing OpenAPI projection

**Files:**
- Create: `api/yiiw/__init__.py`
- Create: `api/yiiw/app.py`
- Modify: `api/openapi.yaml`
- Test: `tests/test_yiiw_g0_api.py`
- Test: `tests/test_yiiw_g0_governance.py`

**Interfaces:**
- Required endpoints:
  - `GET /v1/targets/gold/state?as_of=`
  - `GET /v1/targets/gold/evidence?as_of=`
  - `GET /v1/evidence/{evidence_id}`
  - `GET /v1/model-runs/{model_run_id}`
  - `GET /v1/lineage/{object_id}`
  - `GET /v1/system/health`
- API dependency: repository interface from Task 5.

- [ ] **Step 1: Write API RED tests with FastAPI TestClient and fake repository**

Assert:

- state response includes `as_of`, `knowledge_cutoff`, `evidence_refs`, `model_run_refs`, `authority`, `state_hash`;
- evidence response excludes raw provider body and credentials;
- future `as_of` does not bypass PIT filtering;
- lineage endpoint never returns raw payload;
- no POST/PUT/PATCH/DELETE operational mutation endpoint exists;
- no `execute_sql`/generic query endpoint exists.

- [ ] **Step 2: Run RED**

```bash
python3.12 -m unittest tests.test_yiiw_g0_api tests.test_yiiw_g0_governance -v
```

- [ ] **Step 3: Implement FastAPI app using dependency injection**

`create_app(repository: ResearchRepository) -> FastAPI` must make the app testable without production credentials. Error responses use typed states from the G0 failure taxonomy.

- [ ] **Step 4: Extend existing `api/openapi.yaml`**

Do not create a second top-level API definition. Add the six YIIW paths and reference the frozen G0 response schemas.

- [ ] **Step 5: Run GREEN and repository governance regression**

```bash
python3.12 -m unittest tests.test_yiiw_g0_api tests.test_yiiw_g0_governance -v
python3 scripts/leak_guard.py
```

- [ ] **Step 6: Commit**

```bash
git add api/yiiw api/openapi.yaml tests/test_yiiw_g0_api.py tests/test_yiiw_g0_governance.py
git commit -m "YIIW-G0: expose governed Gold Research API"
```

---

### Task 7: Adapt `yiru-macro-cockpit` as a read-only Workbench projection

**Repository:** `moonstachain/yiru-macro-cockpit`

**Files:**
- Create: `pipelines/yuanli_workbench_adapter.py`
- Modify: `pipelines/99_render.py`
- Modify: `templates/dashboard.html.j2`
- Create: `tests/test_yuanli_workbench_adapter.py`

**Interfaces:**
- `fetch_gold_projection(base_url: str, as_of: str | None = None) -> dict[str, Any]`
- Renderer injects payload under `snap["yuanli_gold"]` only.
- Template renders API values and Evidence Drawer; it performs zero Regime/Gold/advice calculation.

- [ ] **Step 1: Create an isolated worktree from exact `master` and run baseline tests/render smoke**

Do not modify the current production checkout. Record the exact starting SHA in the YIIW receipt.

- [ ] **Step 2: Write RED adapter tests**

Use a local HTTP stub/fake response proving that the adapter preserves API `state_hash`, `evidence_id`, timestamps, provider, model version, and authority ceiling verbatim.

Test that API failure yields a visible `PROJECTION_STALE`/`UNAVAILABLE` projection and never falls back to the legacy hard-coded Gold advice logic.

- [ ] **Step 3: Implement read-only adapter**

Configuration is only through `YUANLI_RESEARCH_API_BASE`; no Supabase/Wind credential may enter this repo.

- [ ] **Step 4: Integrate at render boundary**

Modify `99_render.py` so existing rendering continues unchanged when the env var is absent. When configured, call the Research API and inject `yuanli_gold`.

- [ ] **Step 5: Add Gold Evidence Drawer to template**

The drawer must display only API-provided fields: provider, canonical metric, observed/known/retrieved timestamps, freshness, raw hash, model run/version, conflict state, authority ceiling. It must not display raw provider body.

Remove/visually suppress any conflicting hard-coded Gold allocation/advice on the YIIW Gold surface; do not globally rewrite unrelated legacy tabs in G0.

- [ ] **Step 6: Run GREEN and render smoke**

Render a fixture where `yuanli_gold` is present and assert the HTML contains the exact API `state_hash` and evidence ID. Render without API config and assert legacy render still completes.

- [ ] **Step 7: Commit to a separate `yiru-macro-cockpit` feature branch**

Use a commit message such as:

```bash
git commit -m "YIIW-G0: project governed Gold state into macro workbench"
```

Do not merge the cockpit branch yet.

---

### Task 8: Run the live Genesis Reality Proof and publish machine qualification

**Files:**
- Create: `scripts/yiiw_g0_reality_proof.py`
- Create: `docs/architecture/yiiw/YIIW-G0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md`
- Create: `docs/architecture/yiiw/YIIW-G0-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Runner exit `0` only if all six gates pass.
- Runner writes private runtime evidence outside Git; committed receipt contains IDs, hashes, statuses, SHAs, timestamps, and authority results only.

- [ ] **Step 1: Implement preflight that refuses to run unless local secrets/providers are available without printing them**

Preflight checks:

- Wind CLI exists;
- Supabase URL/service-role credentials exist;
- private storage bucket is reachable;
- G0 schema/migration is applied;
- Research API can start locally;
- no forbidden authority flag is enabled.

- [ ] **Step 2: Apply the additive Supabase migration after local/CI contract tests are green**

Use the existing governed Supabase deployment path. Read back schema/RLS/RPC state before continuing. If the migration conflicts with existing live schema, stop fail-closed and record the exact conflict; do not invent an alternate schema.

- [ ] **Step 3: Execute one live/private Gold slice**

Acquire the three minimum daily inputs through the G0 Wind adapter, persist raw bodies privately, normalize Evidence, compile/persist `ModelRun` and `StateAtPIT`, then read them back through the Research API.

Do not alter the currently loaded G6/G7 launchd job or its runtime directory.

- [ ] **Step 4: Verify the six Genesis gates programmatically**

The runner must produce:

```json
{
  "VALUE_MATCH": "PASS",
  "PIT_MATCH": "PASS",
  "LINEAGE_COMPLETE": "PASS",
  "MODEL_REPRODUCIBLE": "PASS",
  "AUTHORITY_VALID": "PASS",
  "UI_READBACK_MATCH": "PASS"
}
```

`MODEL_REPRODUCIBLE` requires a second deterministic compile from the exact evidence IDs/version and identical output hash.

`UI_READBACK_MATCH` requires the cockpit projection payload to match the Research API state hash/evidence IDs; a manually copied HTML value does not count.

- [ ] **Step 5: Run final verification on exact heads**

For `yuanli-invest`:

```bash
python3.12 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/leak_guard.py
git diff --check origin/main...HEAD
git status --short
```

For `yiru-macro-cockpit`, run its repository test suite plus an explicit render smoke and `git diff --check`.

- [ ] **Step 6: Write qualification and Human Review artifacts**

Machine receipt must record:

- exact repo SHAs for both repositories;
- live evidence IDs/snapshot IDs/raw SHA hashes;
- model ID/version/code SHA/parameter hash;
- state hash;
- API readback hash;
- Workbench readback hash or exact state/evidence IDs;
- six gate results;
- all authority denials;
- unresolved unknowns/failures.

Human Review Card must stop at:

`AWAITING_HUMAN_ACCEPTANCE_YIIW_G0`

No merge, production UI promotion, Temporal G1, or cross-asset expansion occurs automatically.

- [ ] **Step 7: Open Draft PR(s) and stop**

Open one Draft PR in `yuanli-invest` and one dependent Draft PR in `yiru-macro-cockpit` if Task 7 changed that repository. Cross-link the PRs and include the exact Genesis Reality Proof receipt.

Stop at Human Gate.

---

## Final Self-Review Checklist for the Executor

Before claiming implementation complete, verify all of the following:

- [ ] No new competing raw/PIT truth store exists.
- [ ] No legacy schema identity was silently rewritten.
- [ ] All three time semantics remain distinct end to end.
- [ ] Raw Wind body is present only in private object storage, never Git/API/UI.
- [ ] Same evidence/version/parameters reproduce the same state hash.
- [ ] State lineage reaches the raw snapshot hash with no missing edge.
- [ ] Research API is the only app-facing data path.
- [ ] Workbench contains no new investment/advice calculation.
- [ ] Existing GOLD2 G6/G7 runtime still passes regression and remains independently operational.
- [ ] All forbidden authority flags remain false.
- [ ] No Temporal, Next.js rewrite, FactSet live integration, Kafka, Kubernetes, or cross-asset scope creep entered G0.
- [ ] All six Genesis Reality Proof gates are machine-PASS before Human Review.
