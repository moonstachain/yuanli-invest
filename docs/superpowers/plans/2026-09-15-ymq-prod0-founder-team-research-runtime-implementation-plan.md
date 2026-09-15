# YMQ-PROD0-G1｜Founder Team Research Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the accepted YMQ-PROD0 design into a production-capable Founder Team Research Runtime for 5–20 users, preserving point-in-time truth, Dual-Key research governance, deterministic machine gates, event-semantic auditability, and explicit `CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED` boundaries.

**Architecture:** Extend the existing `moonstachain/yuanli-invest` G1 sovereign stack rather than creating a competing system. GitHub remains Law Plane; Supabase/PostgreSQL remains the canonical Reality Ledger; `runtime/ymq_gateway` remains the research-only gateway; n8n becomes the disposable orchestration runtime; Quant/HF remain compute-only; Cockpit is added as the operational experience surface; Notion remains projection-only. Canonical mutations pass through versioned mutation contracts that atomically write Domain Object + Event + Receipt and are idempotent.

**Tech Stack:** Python 3.12, standard-library `unittest`, JSON Schema 2020-12 via `jsonschema==4.25.1`, PostgreSQL 17 / Supabase, SQL RPC / Deno Edge Functions where platform RPC is insufficient, n8n workflows, GitHub Actions, Hugging Face Jobs, Notion MCP/API, Next.js + React + TypeScript for `apps/cockpit`, Vercel for Cockpit deployment.

**Spec:** `docs/superpowers/specs/2026-09-15-ymq-prod0-founder-team-research-runtime-design.md`

## Global Constraints

- Reuse the existing `moonstachain/yuanli-invest` Canon; do not create a competing Law Plane.
- Reuse the existing `evidence`, `pit`, and `runtime` Supabase lineage; PROD0 migrations are additive and backward compatible.
- Preserve current G1 objects: `evidence.sources`, `evidence.source_snapshots`, `pit.observations`, `runtime.reality_gate_runs`, `evidence.claim_receipts`, `runtime.agent_runs`, `runtime.research_projections`, `runtime.learning_deltas`.
- `Reality > Belief`; `ClaimAuthority <= EvidenceAuthority`; `UNKNOWN = DENY`.
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`; `ResearchPass != CapitalPass`.
- No workflow, Copilot output, human role, compute provider, or projection surface may create Capital or Execution authority in PROD0.
- Frozen ResearchCase versions, admitted/revoked evidence receipts, gate results, projections, settlements, events, and receipts are append-only or superseding; historical facts are never overwritten.
- Every canonical mutation is idempotent and atomically commits Domain Object + Event + Receipt.
- n8n may orchestrate canonical mutations but may not directly become the sovereign writer or hold business state that cannot be recovered from Supabase.
- Runtime may be rebuilt from Reality; Reality may never be rebuilt from n8n transient state.
- Browser clients hold no sovereign credentials.
- No secret literal is committed to GitHub.
- High-authority workflow drift fails closed.
- Integrity outranks availability.
- Every production behavior change follows RED -> GREEN -> review -> fresh verification.
- No production deployment, Supabase migration application, n8n activation, external secret creation, or live user rollout occurs without the explicit human gate defined for that task.

## Repository Reality Baseline

The executor must start from the accepted design branch and independently re-read these artifacts before changing code:

- `config/ymq_os0/g1_sovereign_stack.v0.1.json`
- `runtime/ymq_gateway/contracts.py`
- `runtime/ymq_gateway/context_compiler.py`
- `runtime/ymq_gateway/router.py`
- `supabase/migrations/20260914_ymq_os0_g1_sovereign_stack.sql`
- `supabase/migrations/20260914_ymq_os0_g1_fk_index_hardening.sql`
- `api/openapi.yaml`
- `.github/workflows/ci.yml`
- `tests/test_ymq_gateway.py`
- `tests/test_ymq_os0_g1_supabase_contract.py`

Current verified repository facts at plan time:

- Python floor is `>=3.12`.
- Existing CI protected job names are `contracts` and `governance`; they must not be renamed.
- Existing gateway denies Capital/Execution intents and filters future/unknown evidence.
- Existing G1 Reality tables enable RLS and deliberately expose no anon/authenticated write policies.
- Existing API surface is read-only research plus `/copilot/query`; PROD0 mutation APIs must not silently repurpose these read endpoints.
- No Cockpit application directory exists yet; the implementation will add `apps/cockpit` as a new product surface inside the same repository.
- No canonical `n8n/` directory exists yet; PROD0 will add one to hold approved workflow manifests/exports and drift hashes. Live n8n remains replaceable runtime, not Law.

## File Ownership Map

| Area | Canonical paths | Responsibility |
|---|---|---|
| PROD0 machine law | `config/ymq_prod0/`, `packages/contracts/schemas/ymq-prod0-*.schema.json` | authority, event, workflow, state and deployment contracts |
| Validators | `scripts/validate_ymq_prod0_*.py` | fail-closed repository qualification |
| Domain runtime | `runtime/ymq_prod0/` | pure deterministic state/idempotency/gate/reconciliation logic |
| Existing research gateway | `runtime/ymq_gateway/` | contextual research routing; never Capital/Execution |
| Reality Ledger | `supabase/migrations/20260915_ymq_prod0_*.sql` | additive domain tables, events, receipts, RPCs, read models, RLS |
| n8n Law artifacts | `n8n/ymq_prod0/` | approved workflow manifests/exports and hashes |
| API contract | `api/openapi.yaml` | versioned Cockpit read/mutation API contract |
| Cockpit | `apps/cockpit/` | Today, Themes, Evidence & Gate, Review & Learning, contextual Copilot |
| Tests | `tests/test_ymq_prod0_*.py`, `apps/cockpit/**/*.test.tsx` | RED/GREEN contract and UX tests |
| Production receipts | `docs/architecture/ymq_prod0/` | stage-gate, deployment, recovery and 90-day reality receipts |
| CI | `.github/workflows/ci.yml` | exact-head qualification without renaming protected jobs |

---

## Campaign A｜Trust Foundation — Day 0–14

### Task 1: Freeze PROD0 machine constitution and repository validator

**Files:**
- Create: `config/ymq_prod0/prod0_constitution.v0.1.json`
- Create: `packages/contracts/schemas/ymq-prod0-constitution.schema.json`
- Create: `scripts/validate_ymq_prod0_constitution.py`
- Create: `tests/test_ymq_prod0_constitution.py`

**Interfaces:**
- Consumes: `config/ymq_os0/g1_sovereign_stack.v0.1.json` authority laws.
- Produces: `validate_constitution(payload: dict) -> list[str]` and a machine-readable constitution consumed by every later task.

- [ ] **Step 1: Write failing tests for inherited sovereignty laws and new PROD0 planes**

```python
class PROD0ConstitutionTests(unittest.TestCase):
    def test_prod0_inherits_non_authorizations(self):
        payload = json.loads(CONSTITUTION.read_text())
        self.assertEqual(payload["authority_boundary"], "RESEARCH_ONLY")
        self.assertFalse(payload["capital_authorized"])
        self.assertFalse(payload["execution_authorized"])

    def test_runtime_is_not_law_or_truth(self):
        payload = json.loads(CONSTITUTION.read_text())
        self.assertEqual(payload["planes"]["law"]["provider"], "GitHub")
        self.assertEqual(payload["planes"]["reality"]["provider"], "Supabase")
        self.assertEqual(payload["planes"]["runtime"]["authority"], "RESEARCH_ORCHESTRATION_ONLY")
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_ymq_prod0_constitution -v`

Expected: FAIL because PROD0 constitution/schema/validator do not exist.

- [ ] **Step 3: Add the minimal constitution**

The JSON must freeze exactly these planes/roles: Human Principal, Cockpit Experience, GitHub Law, Supabase Reality, n8n/YuanliGateway Runtime, Quant/HF Compute, Notion Projection. It must explicitly encode `unknown_is_deny`, `research_not_capital`, `research_not_execution`, `founder_cannot_override_case_gate`, `history_append_only`, `idempotent_mutations`, and `runtime_disposable` as `true`.

- [ ] **Step 4: Implement validator and schema validation**

```python
def validate_constitution(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("authority_boundary") != "RESEARCH_ONLY":
        errors.append("research_only_required")
    if payload.get("capital_authorized") is not False:
        errors.append("capital_must_remain_denied")
    if payload.get("execution_authorized") is not False:
        errors.append("execution_must_remain_denied")
    if payload.get("laws", {}).get("runtime_disposable") is not True:
        errors.append("runtime_disposable_required")
    return errors
```

- [ ] **Step 5: Run GREEN and full regression**

Run:

```bash
python scripts/validate_ymq_prod0_constitution.py
python -m unittest tests.test_ymq_prod0_constitution -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all commands exit 0.

- [ ] **Step 6: Commit**

```bash
git add config/ymq_prod0 packages/contracts/schemas/ymq-prod0-constitution.schema.json scripts/validate_ymq_prod0_constitution.py tests/test_ymq_prod0_constitution.py
git commit -m "YMQ-PROD0-G1｜Freeze production research constitution"
```

---

### Task 2: Add canonical ResearchCase domain model and immutability contract

**Files:**
- Create: `supabase/migrations/20260915090000_ymq_prod0_research_domain.sql`
- Create: `tests/test_ymq_prod0_research_domain.py`
- Create: `packages/contracts/schemas/ymq-prod0-research-case.schema.json`

**Interfaces:**
- Consumes: existing evidence/PIT lineage.
- Produces: `research.battles`, `research.cases`, `research.case_versions`, `research.case_evidence_links`, `research.review_decisions`.

- [ ] **Step 1: Write structural RED tests**

Tests must assert:

```python
required_tables = (
    "research.battles",
    "research.cases",
    "research.case_versions",
    "research.case_evidence_links",
    "research.review_decisions",
)
```

and verify the migration contains `create schema if not exists research`, RLS enablement on all five tables, a unique `(case_id, version_no)` constraint, `supersedes_version_id`, author/reviewer separation check, and no statement that drops/recreates existing `evidence`, `pit`, or `runtime` schemas.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_ymq_prod0_research_domain -v`

Expected: FAIL because migration does not exist.

- [ ] **Step 3: Implement additive DDL**

Required semantics:

```sql
create schema if not exists research;

create table if not exists research.cases (
  case_id uuid primary key default gen_random_uuid(),
  battle_id uuid not null references research.battles(battle_id),
  case_key text not null unique,
  created_by uuid not null,
  created_at timestamptz not null default now(),
  lifecycle_status text not null default 'DRAFT'
);

create table if not exists research.case_versions (
  case_version_id uuid primary key default gen_random_uuid(),
  case_id uuid not null references research.cases(case_id),
  version_no integer not null check (version_no >= 1),
  as_of timestamptz not null,
  question text not null,
  thesis text not null,
  hypotheses jsonb not null,
  falsifiers jsonb not null,
  canon_sha text not null,
  content_hash text not null check (content_hash ~ '^[0-9a-f]{64}$'),
  supersedes_version_id uuid references research.case_versions(case_version_id),
  created_by uuid not null,
  created_at timestamptz not null default now(),
  unique (case_id, version_no)
);
```

`review_decisions` must reject `reviewer_id = case_version.created_by` through the versioned mutation RPC in Task 5, even if a direct SQL FK cannot express the cross-table check cleanly.

- [ ] **Step 4: Add append-only protection**

Create triggers/functions that reject UPDATE/DELETE on frozen `case_versions` and review decisions after finalization. Do not make mutable draft rows masquerade as frozen history; drafts remain in `cases`/separate draft fields until W2 freeze.

- [ ] **Step 5: Run GREEN and migration contract regression**

Run:

```bash
python -m unittest tests.test_ymq_prod0_research_domain -v
python -m unittest tests.test_ymq_os0_g1_supabase_contract -v
```

Expected: PASS.

- [ ] **Step 6: Commit repository-only DDL; do not apply to production yet**

```bash
git add supabase/migrations/20260915090000_ymq_prod0_research_domain.sql packages/contracts/schemas/ymq-prod0-research-case.schema.json tests/test_ymq_prod0_research_domain.py
git commit -m "YMQ-PROD0-G1｜Add immutable research case domain"
```

**Human Gate A2:** production Supabase application remains unauthorized until Tasks 2–5 are repository-GREEN together.

---

### Task 3: Add event ledger, workflow runs, compute runs and settlement objects

**Files:**
- Create: `supabase/migrations/20260915093000_ymq_prod0_event_runtime.sql`
- Create: `tests/test_ymq_prod0_event_runtime.py`
- Create: `packages/contracts/schemas/ymq-prod0-event.schema.json`

**Interfaces:**
- Produces: `runtime.events`, `runtime.workflow_runs`, `runtime.compute_runs`, `runtime.research_gate_runs`, `runtime.reality_settlements`, and append-only event semantics.

- [ ] **Step 1: Write RED tests for event invariants**

Tests must assert the DDL includes:

```text
runtime.events
UNIQUE idempotency key scoped by capability
correlation_id
causation_event_id
canon_sha
workflow_contract_sha
input_hash
output_hash
receipt_id
RLS
append-only UPDATE/DELETE rejection
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_ymq_prod0_event_runtime -v`

- [ ] **Step 3: Implement event/runtime DDL**

`runtime.events` must include `event_id`, `event_type`, `event_version`, `occurred_at`, `recorded_at`, `workspace_id`, `battle_id`, `research_case_id`, `case_version_id`, `correlation_id`, `causation_event_id`, `run_id`, `actor_type`, `actor_id`, `actor_role`, `authority`, `canon_sha`, `workflow_contract_sha`, `evidence_refs`, `input_hash`, `output_hash`, `idempotency_key`, `status`, `receipt_id`, and `payload`.

Use a uniqueness constraint equivalent to:

```sql
unique (capability_id, idempotency_key)
```

so retries cannot create a second canonical event for the same logical capability action.

- [ ] **Step 4: Make `workflow_runs` technical, not epistemic**

Allowed run states: `STARTED`, `WAITING`, `SUCCEEDED`, `RETRYABLE`, `DENIED`, `FAILED`, `DEAD_LETTER`. Do not store research truth only inside n8n execution IDs.

- [ ] **Step 5: Run GREEN**

Run: `python -m unittest tests.test_ymq_prod0_event_runtime -v`

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260915093000_ymq_prod0_event_runtime.sql packages/contracts/schemas/ymq-prod0-event.schema.json tests/test_ymq_prod0_event_runtime.py
git commit -m "YMQ-PROD0-G1｜Add event semantic runtime ledger"
```

---

### Task 4: Implement deterministic PROD0 state machine and idempotency primitives

**Files:**
- Create: `runtime/ymq_prod0/__init__.py`
- Create: `runtime/ymq_prod0/contracts.py`
- Create: `runtime/ymq_prod0/state_machine.py`
- Create: `runtime/ymq_prod0/idempotency.py`
- Create: `tests/test_ymq_prod0_state_machine.py`

**Interfaces:**
- Produces:
  - `CaseState`
  - `GateState`
  - `WorkflowStatus`
  - `next_case_state(current, event_type, gate_state=None) -> CaseState`
  - `make_idempotency_key(capability_id, case_id, case_version, operation, input_hash) -> str`

- [ ] **Step 1: Write RED tests for legal and illegal transitions**

```python
self.assertEqual(next_case_state(CaseState.DRAFT, "CASE_FROZEN"), CaseState.EVIDENCE_PENDING)
with self.assertRaises(IllegalTransition):
    next_case_state(CaseState.DRAFT, "PROJECTION_PUBLISHED")
```

- [ ] **Step 2: Write RED deterministic-key test**

```python
k1 = make_idempotency_key("W2", "case-1", 1, "freeze", "a" * 64)
k2 = make_idempotency_key("W2", "case-1", 1, "freeze", "a" * 64)
self.assertEqual(k1, k2)
self.assertRegex(k1, r"^[0-9a-f]{64}$")
```

- [ ] **Step 3: Run RED**

Run: `python -m unittest tests.test_ymq_prod0_state_machine -v`

- [ ] **Step 4: Implement enums and transition table**

Allowed case states are exactly:

```text
DRAFT
EVIDENCE_PENDING
REVIEW_PENDING
COMPUTE_PENDING
MACHINE_GATE_PENDING
READY
READY_WITH_LIMITATIONS
INDETERMINATE
BLOCKED
SCIENTIFIC_NO_GO
PROJECTION_PUBLISHED
SETTLEMENT_DUE
SETTLED
LEARNING_CREATED
```

There is no `FORCE_PASS` state or transition.

- [ ] **Step 5: Implement SHA-256 idempotency**

Use canonical JSON/string concatenation with fixed field order. The same logical request returns the same key across processes.

- [ ] **Step 6: Run GREEN and gateway regression**

```bash
python -m unittest tests.test_ymq_prod0_state_machine -v
python -m unittest tests.test_ymq_gateway -v
```

- [ ] **Step 7: Commit**

```bash
git add runtime/ymq_prod0 tests/test_ymq_prod0_state_machine.py
git commit -m "YMQ-PROD0-G1｜Add deterministic research state machine"
```

---

### Task 5: Add canonical mutation RPC contract with atomic Domain + Event + Receipt writes

**Files:**
- Create: `supabase/migrations/20260915100000_ymq_prod0_mutation_rpc.sql`
- Create: `runtime/ymq_prod0/mutations.py`
- Create: `tests/test_ymq_prod0_mutation_contract.py`
- Modify: `api/openapi.yaml`

**Interfaces:**
- Consumes: Tasks 2–4.
- Produces canonical mutation operations:
  - `freeze_case_version`
  - `record_review_decision`
  - `record_compute_run`
  - `settle_research_gate`
  - `publish_research_projection`
  - `record_reality_settlement`
  - `record_learning_delta`

- [ ] **Step 1: Write RED structural tests proving n8n cannot be the business writer**

Tests must require every mutation RPC to accept `idempotency_key`, `canon_sha`, `workflow_contract_sha`, `actor_id`, `actor_role`, `correlation_id`, and `input_hash`, and to return `event_id` + `receipt_id`.

- [ ] **Step 2: Add OpenAPI mutation namespace**

Add explicit `/runtime/mutations/...` endpoints or RPC envelope references. Keep existing read-only paths intact; do not convert `/evidence/{id}` or `/theses` into write APIs.

- [ ] **Step 3: Implement SQL transaction functions**

For each mutation, the function must:

```text
validate identity/scope
validate state transition
check idempotency
insert/return domain object
insert event
insert receipt/result reference
commit atomically
```

If the same `(capability_id, idempotency_key)` already succeeded, return the prior receipt without creating a new domain record/event.

- [ ] **Step 4: Enforce author != reviewer in `record_review_decision`**

Reject with deterministic reason `SEPARATION_OF_DUTIES_DENY` when reviewer equals version author.

- [ ] **Step 5: Extend Python mutation request types**

```python
@dataclass(frozen=True)
class MutationRequest:
    capability_id: str
    actor_id: str
    actor_role: str
    canon_sha: str
    workflow_contract_sha: str
    correlation_id: str
    idempotency_key: str
    input_hash: str
    payload: dict[str, Any]
```

- [ ] **Step 6: Run GREEN**

```bash
python -m unittest tests.test_ymq_prod0_mutation_contract -v
python -m unittest discover -s tests -p 'test_ymq_prod0_*.py' -v
```

- [ ] **Step 7: Commit**

```bash
git add supabase/migrations/20260915100000_ymq_prod0_mutation_rpc.sql runtime/ymq_prod0/mutations.py tests/test_ymq_prod0_mutation_contract.py api/openapi.yaml
git commit -m "YMQ-PROD0-G1｜Add sovereign mutation gateway contract"
```

**Human Gate A5:** after repository GREEN, separately request permission to apply Tasks 2, 3 and 5 migrations to STAGING. Do not apply PROD yet.

---

## Campaign B｜Seven Capability Workflows

### Task 6: Freeze seven workflow contracts and GitHub/n8n drift model

**Files:**
- Create: `config/ymq_prod0/workflows/w1_signal_observer.v0.1.json`
- Create: `config/ymq_prod0/workflows/w2_case_genesis.v0.1.json`
- Create: `config/ymq_prod0/workflows/w3_evidence_admission.v0.1.json`
- Create: `config/ymq_prod0/workflows/w4_compute_dispatcher.v0.1.json`
- Create: `config/ymq_prod0/workflows/w5_dual_key_gate.v0.1.json`
- Create: `config/ymq_prod0/workflows/w6_projection_publisher.v0.1.json`
- Create: `config/ymq_prod0/workflows/w7_settlement_learning.v0.1.json`
- Create: `packages/contracts/schemas/ymq-prod0-workflow.schema.json`
- Create: `scripts/validate_ymq_prod0_workflows.py`
- Create: `tests/test_ymq_prod0_workflow_contracts.py`

**Interfaces:**
- Produces canonical `capability_id`, authority tier, trigger, input schema, output schema, allowed mutation RPC, retry class, and `workflow_contract_sha` for W1–W7.

- [ ] **Step 1: Write RED tests for all seven IDs and authority tiers**

Required mapping:

```text
W1 SIGNAL_OBSERVER        Tier 1 / READ-PROPOSE
W2 CASE_GENESIS           Tier 2 / RESEARCH_STATE
W3 EVIDENCE_ADMISSION     Tier 3 / EPISTEMIC_AUTHORITY
W4 COMPUTE_DISPATCHER     Tier 2 / COMPUTE_ONLY
W5 DUAL_KEY_GATE          Tier 3 / EPISTEMIC_AUTHORITY
W6 PROJECTION_PUBLISHER   Tier 2 / PROJECTION_ONLY
W7 SETTLEMENT_LEARNING    Tier 3 / EPISTEMIC_AUTHORITY
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_ymq_prod0_workflow_contracts -v`

- [ ] **Step 3: Write contracts with explicit mutation allowlists**

Examples: W3 may call evidence admission/revocation RPCs but not projection publishing; W5 may call only gate settlement; W6 may publish a projection only from READY/READY_WITH_LIMITATIONS; W7 may settle and create forward-only learning deltas.

- [ ] **Step 4: Add validator that hashes canonical JSON**

The validator prints a stable SHA-256 for every workflow contract. Store the expected hash in the approved workflow export manifest created by later deployment steps.

- [ ] **Step 5: Run GREEN and commit**

```bash
python scripts/validate_ymq_prod0_workflows.py
python -m unittest tests.test_ymq_prod0_workflow_contracts -v
git add config/ymq_prod0/workflows packages/contracts/schemas/ymq-prod0-workflow.schema.json scripts/validate_ymq_prod0_workflows.py tests/test_ymq_prod0_workflow_contracts.py
git commit -m "YMQ-PROD0-G1｜Freeze seven workflow contracts"
```

---

### Task 7: Implement W2 Case Genesis, W3 Evidence Admission and W5 Dual-Key Gate as fail-closed reference handlers

**Files:**
- Create: `runtime/ymq_prod0/workflows/__init__.py`
- Create: `runtime/ymq_prod0/workflows/case_genesis.py`
- Create: `runtime/ymq_prod0/workflows/evidence_admission.py`
- Create: `runtime/ymq_prod0/workflows/dual_key_gate.py`
- Create: `tests/test_ymq_prod0_high_authority_workflows.py`

**Interfaces:**
- Consumes: `MutationRequest`, state machine, existing G1 evidence semantics.
- Produces pure deterministic decisions used by n8n and mutation RPCs.

- [ ] **Step 1: Write RED Case Genesis tests**

Reject missing question, hypotheses, falsifiers, researcher signature, Canon SHA, or stable signal references. A successful decision returns event type `CASE_FROZEN` and next state `EVIDENCE_PENDING`.

- [ ] **Step 2: Write RED Evidence Admission tests**

Require provenance, known-as-of/PIT time, rights metadata, evidence authority, claim authority, and content hash. If evidence status is UNKNOWN or claim authority exceeds evidence authority, return BLOCKED/DENY rather than guessing.

- [ ] **Step 3: Write RED Dual-Key tests**

```python
result = settle_dual_key_gate(case_version=version, researcher_signed=True, review=review, evidence=evidence, compute_receipts=receipts)
self.assertIn(result.state, {GateState.READY, GateState.READY_WITH_LIMITATIONS, GateState.INDETERMINATE, GateState.BLOCKED, GateState.SCIENTIFIC_NO_GO})
self.assertNotEqual(result.state.value, "FORCE_PASS")
```

Also test author == reviewer -> `SEPARATION_OF_DUTIES_DENY`.

- [ ] **Step 4: Run RED**

Run: `python -m unittest tests.test_ymq_prod0_high_authority_workflows -v`

- [ ] **Step 5: Implement minimal deterministic handlers**

No LLM calls belong in these handlers. They validate contracts and return typed decisions only.

- [ ] **Step 6: Run GREEN and full authority regression**

```bash
python -m unittest tests.test_ymq_prod0_high_authority_workflows -v
python -m unittest tests.test_ymq_gateway -v
python -m unittest tests.test_ymq_os0_g1 -v
```

- [ ] **Step 7: Commit**

```bash
git add runtime/ymq_prod0/workflows tests/test_ymq_prod0_high_authority_workflows.py
git commit -m "YMQ-PROD0-G1｜Implement fail-closed research gates"
```

---

### Task 8: Implement W1 Signal Observer and W4 Compute Dispatcher reference logic

**Files:**
- Create: `runtime/ymq_prod0/workflows/signal_observer.py`
- Create: `runtime/ymq_prod0/workflows/compute_dispatcher.py`
- Create: `tests/test_ymq_prod0_signal_compute.py`

**Interfaces:**
- W1 produces proposal-only `SIGNAL_OBSERVED`; it cannot freeze a Thesis.
- W4 produces a dispatch plan with stable `compute_run_id`, dispatch-once semantics and poll-many provider state.

- [ ] **Step 1: Write RED W1 tests**

Test deterministic priority bucket from explicit inputs and ensure output contains no Research PASS, Capital, or Execution authority.

- [ ] **Step 2: Write RED W4 duplicate-dispatch test**

The same compute idempotency key must return the existing provider run when one exists; a provider timeout after accepted dispatch changes state to `WAITING`/poll, not a second create call.

- [ ] **Step 3: Run RED**

Run: `python -m unittest tests.test_ymq_prod0_signal_compute -v`

- [ ] **Step 4: Implement pure dispatch planner**

```python
@dataclass(frozen=True)
class ComputeDispatchPlan:
    compute_run_id: str
    action: Literal["DISPATCH", "POLL", "RETURN_EXISTING", "DENY"]
    provider: str
    reason: str
```

- [ ] **Step 5: Run GREEN and commit**

```bash
python -m unittest tests.test_ymq_prod0_signal_compute -v
git add runtime/ymq_prod0/workflows tests/test_ymq_prod0_signal_compute.py
git commit -m "YMQ-PROD0-G1｜Add signal and compute workflow logic"
```

---

### Task 9: Implement W6 Projection Publisher and W7 Settlement & Learning reference logic

**Files:**
- Create: `runtime/ymq_prod0/workflows/projection_publisher.py`
- Create: `runtime/ymq_prod0/workflows/settlement_learning.py`
- Create: `tests/test_ymq_prod0_projection_settlement.py`

**Interfaces:**
- W6 may publish only from READY/READY_WITH_LIMITATIONS and produces Research Projection only.
- W7 restores T0 snapshot, compares T1 Reality, returns `SUPPORTED | PARTIAL | FALSIFIED | INDETERMINATE`, then creates forward-only learning proposal.

- [ ] **Step 1: Write RED W6 authority tests**

Assert INDETERMINATE/BLOCKED/SCIENTIFIC_NO_GO cannot publish normal projection, and published payload cannot set `canonical_truth=true`, `can_grant_authority=true`, Capital, or Execution fields.

- [ ] **Step 2: Write RED T0 replay tests**

Settlement inputs must include original CaseVersion ID, T0 evidence refs, T0 projection, T0 price snapshot reference and T0 Canon SHA. A missing T0 artifact yields INDETERMINATE/BLOCKED, never reconstructed hindsight.

- [ ] **Step 3: Run RED**

Run: `python -m unittest tests.test_ymq_prod0_projection_settlement -v`

- [ ] **Step 4: Implement W6/W7 decisions**

Learning deltas include one of the frozen failure classes: `SOURCE_COVERAGE`, `TRANSMISSION_MODEL`, `NARRATIVE_LAG`, `PRICE_MISREAD`, `REGIME_MISCLASSIFICATION`, `WEAK_FALSIFIER`, `PIT_LEAKAGE`, `REVIEWER_BIAS`, or `NONE`.

- [ ] **Step 5: Run GREEN and commit**

```bash
python -m unittest tests.test_ymq_prod0_projection_settlement -v
git add runtime/ymq_prod0/workflows tests/test_ymq_prod0_projection_settlement.py
git commit -m "YMQ-PROD0-G1｜Add projection settlement and learning logic"
```

---

### Task 10: Add Runtime Reconciler and drift detector

**Files:**
- Create: `runtime/ymq_prod0/reconciler.py`
- Create: `runtime/ymq_prod0/drift.py`
- Create: `scripts/validate_ymq_prod0_runtime_drift.py`
- Create: `tests/test_ymq_prod0_reconciler.py`
- Create: `n8n/ymq_prod0/README.md`

**Interfaces:**
- Detects WorkflowRun without Event, Event without Receipt, Projection without Gate, Gate without Review, Compute without Hash, expired pending runs, duplicate-idempotency anomalies, n8n/GitHub drift and Notion projection lag.
- May recommend safe repair of transient projection/runtime state; may never fabricate Evidence, Gate PASS, Projection authority, or history.

- [ ] **Step 1: Write RED reconciliation classification tests**

Each anomaly must classify as `SAFE_RETRY`, `PROJECTION_RESYNC`, `INCIDENT`, or `AUTHORITY_FREEZE`.

- [ ] **Step 2: Write RED drift test**

For W3/W5/W7, live hash != approved hash must produce `AUTHORITY_FREEZE`. Tier-1 Notion notification drift produces `INCIDENT`/degraded status but does not corrupt Reality.

- [ ] **Step 3: Implement reconciler/drift logic**

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest tests.test_ymq_prod0_reconciler -v`

- [ ] **Step 5: Commit**

```bash
git add runtime/ymq_prod0/reconciler.py runtime/ymq_prod0/drift.py scripts/validate_ymq_prod0_runtime_drift.py tests/test_ymq_prod0_reconciler.py n8n/ymq_prod0/README.md
git commit -m "YMQ-PROD0-G1｜Add runtime reconciliation and drift controls"
```

---

## Campaign C｜n8n Physical Runtime — Staging First

### Task 11: Build seven n8n workflows in STAGING and export approved definitions

**Files:**
- Create after physical build: `n8n/ymq_prod0/w1_signal_observer.json`
- Create: `n8n/ymq_prod0/w2_case_genesis.json`
- Create: `n8n/ymq_prod0/w3_evidence_admission.json`
- Create: `n8n/ymq_prod0/w4_compute_dispatcher.json`
- Create: `n8n/ymq_prod0/w5_dual_key_gate.json`
- Create: `n8n/ymq_prod0/w6_projection_publisher.json`
- Create: `n8n/ymq_prod0/w7_settlement_learning.json`
- Create: `config/ymq_prod0/n8n_deployment_manifest.v0.1.json`
- Create: `tests/test_ymq_prod0_n8n_exports.py`

**Interfaces:**
- Consumes workflow contracts from Task 6 and canonical mutation endpoints from Task 5.
- Produces disabled/unpublished STAGING workflows first; production activation requires a later human gate.

- [ ] **Step 1: In the authorized n8n STAGING project, create credentials with least privilege**

Create separate credentials/identities for runtime mutation API, read-only Reality queries, HF/compute dispatch, Notion projection and notifications. Do not place Supabase service-role or n8n admin secrets inside workflow JSON exports.

- [ ] **Step 2: Build W1**

Nodes: Schedule Trigger + manual test trigger -> read-only source/reality call -> deterministic signal transform/call -> canonical event mutation -> response/receipt logging. W1 has no gate or projection mutation credential.

- [ ] **Step 3: Build W2**

Webhook/Execute Workflow input -> schema validation -> Case Genesis contract call -> canonical `freeze_case_version` mutation -> receipt output.

- [ ] **Step 4: Build W3**

Execute Workflow input -> candidate evidence retrieval -> independent reviewer input/HITL -> evidence validation -> admitted/limited/blocked mutation -> receipt. Configure no fallback branch that turns validator errors into PASS.

- [ ] **Step 5: Build W4**

Input -> `ComputeDispatchPlan` -> dispatch once -> persist provider_run_id -> wait/poll -> verify result hash -> canonical compute receipt. Retried executions query existing run before any provider create call.

- [ ] **Step 6: Build W5**

Input -> retrieve frozen version + researcher signature + review + evidence receipts + required compute receipts -> deterministic gate handler -> canonical gate mutation -> receipt. No human override node exists.

- [ ] **Step 7: Build W6**

Gate event trigger -> verify READY/READY_WITH_LIMITATIONS -> canonical projection mutation -> Cockpit read-model refresh -> Notion projection sync. If Notion fails, write projection sync pending status and keep canonical projection valid.

- [ ] **Step 8: Build W7**

Scheduled/falsifier/manual authorized trigger -> restore T0 package -> retrieve T1 Reality -> deterministic settlement -> canonical settlement + learning delta -> queue capability-change proposal. Do not modify Canon.

- [ ] **Step 9: Export all workflow definitions and strip runtime secrets/IDs that should not be canonical**

Store normalized JSON definitions in `n8n/ymq_prod0/` and record live workflow IDs only in deployment manifest fields that are explicitly non-secret.

- [ ] **Step 10: Write/export contract tests**

`tests/test_ymq_prod0_n8n_exports.py` must reject embedded credential values, missing capability IDs, direct canonical-table writes, missing workflow-contract hashes, and Tier-3 workflows lacking fail-closed error branches.

- [ ] **Step 11: Run GREEN**

```bash
python scripts/leak_guard.py
python -m unittest tests.test_ymq_prod0_n8n_exports -v
python scripts/validate_ymq_prod0_runtime_drift.py --manifest config/ymq_prod0/n8n_deployment_manifest.v0.1.json --exports n8n/ymq_prod0
```

- [ ] **Step 12: Commit exports only after readback from n8n confirms exact definitions**

```bash
git add n8n/ymq_prod0 config/ymq_prod0/n8n_deployment_manifest.v0.1.json tests/test_ymq_prod0_n8n_exports.py
git commit -m "YMQ-PROD0-G1｜Freeze staging n8n workflow exports"
```

**Human Gate C11:** workflows remain inactive/unpublished in production. STAGING physical calls may use only staging/synthetic data until Stage Gate P0 passes.

---

## Campaign D｜Cockpit Product Surface

### Task 12: Create Cockpit application shell and typed API client

**Files:**
- Create: `apps/cockpit/package.json`
- Create: `apps/cockpit/tsconfig.json`
- Create: `apps/cockpit/next.config.ts`
- Create: `apps/cockpit/src/app/layout.tsx`
- Create: `apps/cockpit/src/app/page.tsx`
- Create: `apps/cockpit/src/lib/api.ts`
- Create: `apps/cockpit/src/lib/types.ts`
- Create: `apps/cockpit/src/app/page.test.tsx`

**Interfaces:**
- Consumes read models/API only; browser never receives sovereign mutation credentials.
- Produces navigation shell for TODAY, THEMES, EVIDENCE & GATE, REVIEW & LEARNING and contextual Copilot.

- [ ] **Step 1: Initialize a minimal Next.js/TypeScript app inside `apps/cockpit`**

Use React 19-compatible Next.js, TypeScript strict mode, Vitest + Testing Library. Do not add a second backend or database ORM in Cockpit.

- [ ] **Step 2: Write RED shell test**

```tsx
render(<Home />)
expect(screen.getByText("TODAY")).toBeInTheDocument()
expect(screen.getByText("THEMES")).toBeInTheDocument()
expect(screen.getByText("EVIDENCE & GATE")).toBeInTheDocument()
expect(screen.getByText("REVIEW & LEARNING")).toBeInTheDocument()
```

- [ ] **Step 3: Implement shell with server-side API boundary**

`src/lib/api.ts` reads only `COCKPIT_API_BASE_URL` and server-scoped session/auth configuration. It does not expose Supabase service role, n8n admin token, HF write token or Notion integration secret to client bundles.

- [ ] **Step 4: Run GREEN**

```bash
cd apps/cockpit
npm ci
npm test -- --run
npm run build
```

- [ ] **Step 5: Commit**

```bash
git add apps/cockpit
git commit -m "YMQ-PROD0-G1｜Create founder research cockpit shell"
```

---

### Task 13: Implement Cockpit read models and four workspaces

**Files:**
- Create: `supabase/migrations/20260915110000_ymq_prod0_read_models.sql`
- Create: `tests/test_ymq_prod0_read_models.py`
- Create: `apps/cockpit/src/app/today/page.tsx`
- Create: `apps/cockpit/src/app/themes/page.tsx`
- Create: `apps/cockpit/src/app/evidence-gate/page.tsx`
- Create: `apps/cockpit/src/app/review-learning/page.tsx`
- Create: `apps/cockpit/src/components/AttentionCard.tsx`
- Create: `apps/cockpit/src/components/GatePanel.tsx`
- Create: `apps/cockpit/src/components/SettlementCard.tsx`
- Create: `apps/cockpit/src/components/*.test.tsx`

**Interfaces:**
- Produces rebuildable read models: `current_case_state`, `today_attention_queue`, `battle_summary`, `reviewer_queue`, `settlement_queue`, `founder_escalations`.

- [ ] **Step 1: Write RED SQL tests proving read models contain no canonical mutation**

The migration may create views/materialized views/functions for reads but must not duplicate authoritative ResearchCase/Gate/Projection rows.

- [ ] **Step 2: Implement Today read model**

Every item returns `what_changed`, `why_it_matters`, `evidence_status`, `current_belief`, `falsifier`, `owner`, `next_action`, and priority bucket P0/P1/P2/P3.

- [ ] **Step 3: Implement Themes read model for the same 11-step cognitive order across battles**

- [ ] **Step 4: Implement Evidence & Gate view**

Expose Source Authority, four relevant clocks, provenance, PIT/revision/rights/hash, claims supported, `does_not_prove`, and gate dimensions. Do not expose an override control.

- [ ] **Step 5: Implement Review & Learning view**

Show T0 belief/evidence/projection next to T1 observed Reality and settlement result.

- [ ] **Step 6: Run backend and frontend GREEN**

```bash
python -m unittest tests.test_ymq_prod0_read_models -v
cd apps/cockpit && npm test -- --run && npm run build
```

- [ ] **Step 7: Commit**

```bash
git add supabase/migrations/20260915110000_ymq_prod0_read_models.sql tests/test_ymq_prod0_read_models.py apps/cockpit/src
git commit -m "YMQ-PROD0-G1｜Add cockpit attention and learning surfaces"
```

---

### Task 14: Extend contextual Founder Copilot without authority leakage

**Files:**
- Modify: `runtime/ymq_gateway/contracts.py`
- Modify: `runtime/ymq_gateway/context_compiler.py`
- Modify: `runtime/ymq_gateway/router.py`
- Create: `runtime/ymq_prod0/copilot.py`
- Modify: `api/openapi.yaml`
- Create: `apps/cockpit/src/components/ContextualCopilot.tsx`
- Create: `tests/test_ymq_prod0_copilot.py`

**Interfaces:**
- Consumes current `battle_id`, `case_id`, T0, admitted Evidence refs, Gate state, Canon SHA and current Research Projection.
- Produces research-only answers/intents: Evidence, Transmission, Price/Consensus, Falsifier, Research Projection implications.

- [ ] **Step 1: Write RED authority tests**

Queries that request position size, broker order or real capital movement must be denied by the existing router even when context and evidence are PASS.

- [ ] **Step 2: Write RED context-minimality tests**

Only admitted evidence known at/before the requested `as_of` enters context. Current/future evidence is excluded during T0 replay.

- [ ] **Step 3: Implement intent compiler**

Map the five default prompts to capability calls, not free-form authority:

```text
为什么？ -> EVIDENCE
然后呢？ -> TRANSMISSION
市场知道了吗？ -> PRICE_CONSENSUS
什么会证明我们错？ -> FALSIFIER
这对资本意味着什么？ -> RESEARCH_PROJECTION_ONLY
```

- [ ] **Step 4: Implement UI component that always displays case context and Gate status**

- [ ] **Step 5: Run GREEN**

```bash
python -m unittest tests.test_ymq_prod0_copilot -v
python -m unittest tests.test_ymq_gateway -v
cd apps/cockpit && npm test -- --run && npm run build
```

- [ ] **Step 6: Commit**

```bash
git add runtime/ymq_gateway runtime/ymq_prod0/copilot.py api/openapi.yaml apps/cockpit/src/components/ContextualCopilot.tsx tests/test_ymq_prod0_copilot.py
git commit -m "YMQ-PROD0-G1｜Add contextual research copilot"
```

---

## Campaign E｜Identity, Security, Operations and Recovery

### Task 15: Add principal/RBAC/scoped machine identity contracts

**Files:**
- Create: `config/ymq_prod0/rbac.v0.1.json`
- Create: `packages/contracts/schemas/ymq-prod0-rbac.schema.json`
- Create: `supabase/migrations/20260915113000_ymq_prod0_identity_rls.sql`
- Create: `tests/test_ymq_prod0_rbac.py`

**Interfaces:**
- Human roles: FOUNDER, RESEARCHER, EVIDENCE_REVIEWER, OPERATOR.
- Machine identities: `svc_n8n_runtime`, `svc_quant_runner`, `svc_hf_dispatch`, `svc_projection_sync`, `svc_reconciler`, `svc_ci_migration`.
- Authorization key: `principal_id + role + scope`.

- [ ] **Step 1: Write RED tests for role/scope matrix**

Researcher may create/freeze own case within battle scope but cannot review own version; Reviewer can admit/reject/downgrade evidence but not author the same frozen thesis; Operator has runtime administration but no research authority; Founder may propose/approve Canon changes but may not force a case gate PASS.

- [ ] **Step 2: Implement RLS/scoped RPC grants**

Keep canonical tables unavailable to browser direct writes. Prefer versioned RPC grants over broad table grants.

- [ ] **Step 3: Test machine identities for least privilege**

`svc_projection_sync` cannot write evidence/gates; `svc_hf_dispatch` cannot publish projection; `svc_n8n_runtime` cannot bypass allowed mutation RPC list.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest tests.test_ymq_prod0_rbac -v
git add config/ymq_prod0/rbac.v0.1.json packages/contracts/schemas/ymq-prod0-rbac.schema.json supabase/migrations/20260915113000_ymq_prod0_identity_rls.sql tests/test_ymq_prod0_rbac.py
git commit -m "YMQ-PROD0-G1｜Add scoped principal and machine identity law"
```

---

### Task 16: Add deployment, secret metadata, drift, observability and incident contracts

**Files:**
- Create: `config/ymq_prod0/credentials.v0.1.json`
- Create: `config/ymq_prod0/slo.v0.1.json`
- Create: `config/ymq_prod0/incidents.v0.1.json`
- Create: `packages/contracts/schemas/ymq-prod0-deployment-receipt.schema.json`
- Create: `runtime/ymq_prod0/health.py`
- Create: `tests/test_ymq_prod0_operations.py`
- Create: `docs/architecture/ymq_prod0/YMQ-PROD0-OPERATIONS-RUNBOOK-v0.1.md`

**Interfaces:**
- Defines credential metadata/lifecycle without secret literals, deployment receipt, SLOs, SEV-0..3, Break Glass, capability kill switch and recovery order.

- [ ] **Step 1: Write RED secret-law test**

Credential metadata may contain `credential_id`, provider, owner, purpose, scope, environment, created/rotation timestamps, status and dependent capabilities, but no fields/values matching token/key/password literals. Re-run `scripts/leak_guard.py`.

- [ ] **Step 2: Freeze SLOs**

Encode: daily refresh by 08:45 >=99%; P0/P1 workflow completion >=99.5%; qualified projection to Cockpit p95 <60s; due settlement within 48h >=95%; undetected Canon drift = 0; silent authority escalation = 0; canonical mutation without receipt = 0.

- [ ] **Step 3: Freeze incidents**

SEV-0 sovereignty -> immediate affected-capability freeze; SEV-1 truth-integrity -> freeze downstream authority and reconcile; SEV-2 runtime -> degraded mode; SEV-3 projection -> resync without invalidating Reality.

- [ ] **Step 4: Implement `health.py` traffic-light evaluation**

Return separate Infrastructure, Workflow, Data Integrity and Research Integrity states; never collapse into one misleading numeric score.

- [ ] **Step 5: Write runbook with exact response order**

`Contain -> Preserve Evidence -> Freeze Authority -> Reconcile Reality -> Recover Runtime -> Resume -> Settle Incident -> Learn`.

- [ ] **Step 6: Run GREEN and commit**

```bash
python scripts/leak_guard.py
python -m unittest tests.test_ymq_prod0_operations -v
git add config/ymq_prod0 packages/contracts/schemas/ymq-prod0-deployment-receipt.schema.json runtime/ymq_prod0/health.py tests/test_ymq_prod0_operations.py docs/architecture/ymq_prod0/YMQ-PROD0-OPERATIONS-RUNBOOK-v0.1.md
git commit -m "YMQ-PROD0-G1｜Freeze production operations and incident controls"
```

---

### Task 17: Add disaster recovery and Reality-first restore proof

**Files:**
- Create: `runtime/ymq_prod0/recovery.py`
- Create: `tests/test_ymq_prod0_recovery.py`
- Create: `docs/architecture/ymq_prod0/YMQ-PROD0-RECOVERY-DRILL-v0.1.md`

**Interfaces:**
- Consumes canonical events/receipts/current process states.
- Produces `RecoveryAction` sequence for incomplete processes without relying on n8n execution memory.

- [ ] **Step 1: Write RED recovery test**

Given canonical W4 `COMPUTE_DISPATCHED` event + provider_run_id but no `COMPUTE_SETTLED`, recovery must propose POLL existing run, not create a new one.

Given canonical projection + Notion sync failure, recovery proposes `PROJECTION_RESYNC` only.

Given event missing receipt, recovery proposes `AUTHORITY_FREEZE/INCIDENT`, not fabricated receipt.

- [ ] **Step 2: Implement recovery planner**

Recovery order is `Reality -> Runtime -> Read Models -> Projection`.

- [ ] **Step 3: Run GREEN and commit**

```bash
python -m unittest tests.test_ymq_prod0_recovery -v
git add runtime/ymq_prod0/recovery.py tests/test_ymq_prod0_recovery.py docs/architecture/ymq_prod0/YMQ-PROD0-RECOVERY-DRILL-v0.1.md
git commit -m "YMQ-PROD0-G1｜Add reality-first recovery planner"
```

---

## Campaign F｜Three Flagship Battles and 90-Day Reality Experiment

### Task 18: Freeze three Battle configurations and secret-free pilot fixtures

**Files:**
- Create: `config/ymq_prod0/battles/ai_infrastructure.v0.1.json`
- Create: `config/ymq_prod0/battles/gold_global_money.v0.1.json`
- Create: `config/ymq_prod0/battles/china_policy_manufacturing.v0.1.json`
- Create: `fixtures/ymq_prod0/ai_infra_case_pack.json`
- Create: `fixtures/ymq_prod0/gold_case_pack.json`
- Create: `fixtures/ymq_prod0/china_case_pack.json`
- Create: `tests/test_ymq_prod0_battles.py`

**Interfaces:**
- Battles share one ResearchCase contract and one seven-workflow runtime; they differ only in source/compute requirements and domain-specific fields.

- [ ] **Step 1: Write RED transferability tests**

Each config must define evidence classes, required compute classes, priority inputs and settlement horizons without redefining gate authority or state machine.

- [ ] **Step 2: Create AI fixture pack**

Include cases spanning Reality Shift, Transmission, Narrative, Price/Payoff and Hard Negative. The fixture is secret-free and deterministic; it does not claim current market truth.

- [ ] **Step 3: Create Gold and China fixture packs**

Gold stresses long-cycle/regime/cross-asset causality; China stresses policy text, revisions, historical PIT and corpus provenance.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest tests.test_ymq_prod0_battles -v
git add config/ymq_prod0/battles fixtures/ymq_prod0 tests/test_ymq_prod0_battles.py
git commit -m "YMQ-PROD0-G1｜Freeze three flagship battle fixtures"
```

---

### Task 19: Wire PROD0 qualification into existing protected CI without renaming jobs

**Files:**
- Modify: `.github/workflows/ci.yml`
- Create: `scripts/validate_ymq_prod0.py`
- Create: `tests/test_ymq_prod0_ci_contract.py`

**Interfaces:**
- Preserves protected job names `contracts` and `governance`.
- Produces a single fail-closed repository qualification entrypoint.

- [ ] **Step 1: Write RED CI contract test**

Assert `.github/workflows/ci.yml` contains `python scripts/validate_ymq_prod0.py` inside the existing `contracts` job and still has job names `contracts` and `governance`.

- [ ] **Step 2: Implement top-level validator**

It invokes constitution, workflow/export/drift validators and structural checks. It does not call production services or require secrets in PR CI.

- [ ] **Step 3: Add Cockpit build job only if branch protection does not require a single-job topology**

Preferred: add a new non-protected `cockpit` job running `npm ci`, tests and build. Do not rename or replace the existing protected jobs.

- [ ] **Step 4: Run local/fresh repository verification**

```bash
python scripts/validate_ymq_prod0.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/leak_guard.py
cd apps/cockpit && npm ci && npm test -- --run && npm run build
```

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/ci.yml scripts/validate_ymq_prod0.py tests/test_ymq_prod0_ci_contract.py
git commit -m "YMQ-PROD0-G1｜Wire production runtime qualification into CI"
```

---

### Task 20: Execute Day-14 P0 Trust Foundation gate in STAGING

**Files:**
- Create: `docs/architecture/ymq_prod0/YMQ-PROD0-P0-TRUST-RECEIPT-v0.1.md`
- Create: `fixtures/ymq_prod0/p0_fault_drill.json`

**Interfaces:**
- Consumes Tasks 1–19 and a dedicated STAGING environment.
- Produces verdict `P0_PASS` or `P0_NO_GO`; it does not authorize production rollout by itself.

- [ ] **Step 1: Apply additive migrations to STAGING only after explicit human authorization**

Read back schemas, constraints, RLS policies and RPC grants after application.

- [ ] **Step 2: Run duplicate-idempotency drill**

Submit the same Case Freeze request twice. Verify one CaseVersion/Event/Receipt exists and the second response references the same canonical receipt.

- [ ] **Step 3: Run separation-of-duties drill**

Author attempts self-review -> deterministic DENY; independent reviewer -> accepted review path.

- [ ] **Step 4: Run n8n-loss recovery drill**

Interrupt a W4/W6 staging run after canonical state is persisted; reconstruct next action from Supabase using Runtime Reconciler.

- [ ] **Step 5: Run workflow drift drill**

Alter a STAGING copy of W5 definition without updating GitHub hash. Verify `AUTHORITY_FREEZE`; restore the approved definition and verify requalification.

- [ ] **Step 6: Run secret and browser-boundary audit**

Inspect exported workflow JSON, Cockpit bundle/env exposure and repo leak guard. Verify no sovereign secret is exposed.

- [ ] **Step 7: Record P0 receipt**

Receipt must include exact Git SHA, migration hashes, workflow IDs + approved hashes, test commands/results, staging identifiers, recovery drill evidence and explicit `CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED`.

- [ ] **Step 8: Human Gate P0**

Only a human-approved `P0_PASS` allows P1 AI Infrastructure Alpha. Otherwise stop and remediate; do not widen users or Battles.

---

### Task 21: Execute Day-15–30 AI Infrastructure One-Battle Alpha

**Files:**
- Create: `docs/architecture/ymq_prod0/YMQ-PROD0-G1-AI-ALPHA-RECEIPT-v0.1.md`
- Create/update: `config/ymq_prod0/pilot/ai_alpha_roster.v0.1.json` with non-secret principal IDs/roles/scopes only.

**Interfaces:**
- Real users: 1 Founder, 2 Researchers, 1–2 Evidence Reviewers, 1 Operator; roles may overlap operationally except Author != Reviewer for same frozen version.

- [ ] **Step 1: Onboard 3–5 users into Cockpit and scoped identities**

- [ ] **Step 2: Run 8–12 real AI Infrastructure ResearchCases through the full runtime**

Include Reality Shift, Transmission, Narrative, Price/Payoff and Hard Negative cases.

- [ ] **Step 3: Require 100% independent Dual-Key review on qualified cases**

- [ ] **Step 4: Require at least one legitimate LIMITED/INDETERMINATE/BLOCKED outcome**

Do not manufacture a negative outcome merely to satisfy the metric; if all cases genuinely qualify, record that and flag it for gate-health review rather than falsifying evidence.

- [ ] **Step 5: Sample T0 reconstruction**

For each sampled case, rebuild original CaseVersion, evidence refs, projection, price reference and Canon SHA without consulting future evidence.

- [ ] **Step 6: Verify Founder is not routine approver and core work occurs in Cockpit**

- [ ] **Step 7: Record `G1_ONE_BATTLE_REALITY_PROOF` verdict**

A fail on sovereignty, T0 reconstruction, receipt completeness or Dual-Key independence blocks P2 regardless of user satisfaction.

---

### Task 22: Execute Day-31–60 Three-Battle Shadow Operations

**Files:**
- Create: `docs/architecture/ymq_prod0/YMQ-PROD0-G2-THREE-BATTLE-RECEIPT-v0.1.md`
- Create: `config/ymq_prod0/pilot/three_battle_metrics.v0.1.json`

**Interfaces:**
- Adds Gold / Global Money and China Policy / New Manufacturing to the same contracts/runtime.

- [ ] **Step 1: Activate battle scopes without creating new workflow families**

- [ ] **Step 2: Run daily operating rhythm**

08:00–09:00 machine refresh; 09:00 Today Intelligence; 09:15–12:00 Research Window; 14:00–16:00 Evidence Review; 17:00 Runtime Settlement.

- [ ] **Step 3: Run Weekly Reality Review**

Discuss only major Reality shift, research upgrade, falsification, Learning Delta and Canon/strategic escalation; work-status reporting comes from the system.

- [ ] **Step 4: Measure initial G2 targets**

Canonical mutation with receipt = 100%; silent authority escalation = 0; Gate bypass = 0; T0 reconstruction >=95%; P0/P1 queue on time >=85%; due settlement >=80%; qualified cases Dual-Key reviewed =100%; Founder routine approval <20%.

- [ ] **Step 5: Record cross-battle failure modes explicitly**

If China evidence/PIT cannot meet threshold while AI/Gold can, produce NARROW candidate rather than weakening evidence law.

- [ ] **Step 6: Human Gate G2**

Approve P3 only if the Runtime works across the accepted scope without authority erosion.

---

### Task 23: Execute Day-61–90 Founder Team Production and final Reality Settlement

**Files:**
- Create: `docs/architecture/ymq_prod0/YMQ-PROD0-90D-REALITY-SETTLEMENT-v0.1.md`
- Create: `config/ymq_prod0/pilot/day90_verdict.v0.1.json`

**Interfaces:**
- Users: 5–20 Founder Team.
- Allowed final verdicts: SCALE, NARROW, REFRAME, KILL.

- [ ] **Step 1: Enter feature freeze**

Only P0/P1 defects, security/integrity issues and severe usability blockers may change product behavior during the final 30-day evidence window.

- [ ] **Step 2: Measure stable L1 adoption**

Detect Shadow Workflow: core research in chat/Excel/Notion followed by backfill is L0 and must not be counted as Runtime adoption.

- [ ] **Step 3: Compute RSRR**

`RSRR = due qualified decision-relevant cases completing Reality Settlement + Learning Closure on time / due qualified decision-relevant cases`; target >=85%.

- [ ] **Step 4: Establish DRCR baseline and Founder Attention Compression evidence**

Do not optimize Founder involvement toward zero; verify routine noise is compressed while Canon/strategic unknowns remain visible.

- [ ] **Step 5: Run final seven-question Reality Review**

Answer with evidence: Did Reality remain trustworthy? Did Dual-Key create independent judgment? Did n8n reduce work rather than add workflow burden? Did three Battles fit the same Research Contract? Did the team actually work through Cockpit? Did qualified beliefs face Reality Settlement? Did Founder attention move toward higher-leverage decisions?

- [ ] **Step 6: Apply pre-registered verdict rules**

`SCALE` only if sovereignty, integrity, adoption, cross-battle transfer, settlement and Founder leverage pass. `NARROW` when selected Battles/evidence environments pass. `REFRAME` when integrity works but work-unit/UX hypothesis is wrong. `KILL` when complexity tax exceeds capability gain, T0 cannot be restored, Settlement remains <50%, Dual-Key is governance theater, or Founder becomes a bigger bottleneck.

- [ ] **Step 7: Final allowed qualification**

Only if all required gates pass may the receipt state:

`YMQ_PROD0_OPERATIONALLY_QUALIFIED / CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED`

A SCALE verdict may propose `YMQ-PROD1｜Research → Shadow Capital`, but PROD0 itself does not authorize Shadow Capital implementation or any broker action.

---

## Execution Order and Review Gates

Execute strictly in this dependency order:

`Task 1 -> Tasks 2/3 -> Task 4 -> Task 5 -> Task 6 -> Tasks 7/8/9 -> Task 10 -> Task 11 STAGING -> Tasks 12/13/14 -> Tasks 15/16/17 -> Task 18 -> Task 19 -> Task 20 P0 -> Task 21 G1 -> Task 22 G2 -> Task 23 Day90`.

Tasks 7, 8 and 9 may be developed in parallel after Tasks 1–6 are merged into the implementation branch because they consume frozen contracts and do not share mutable implementation files except `runtime/ymq_prod0/workflows/__init__.py`; coordinate that file or add exports in a final integration commit.

No STAGING mutation deployment occurs before Tasks 1–10 are repository-GREEN. No production migration/workflow activation occurs before P0 human approval. No Battle expansion occurs before G1 human approval. No Founder Team production expansion occurs before G2 human approval.

## Verification Matrix

Before every campaign gate, run at minimum:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_ymq_os0_g1.py
python scripts/validate_ymq_prod0_constitution.py
python scripts/validate_ymq_prod0_workflows.py
python scripts/validate_ymq_prod0.py
python scripts/leak_guard.py
python -m unittest discover -s tests -p 'test_*.py' -v
cd apps/cockpit && npm ci && npm test -- --run && npm run build
```

For deployed stages also require physical readback of Supabase schemas/policies/functions, n8n workflow definitions/hashes, provider receipts and Cockpit deployment SHA. Do not infer deployed state from repository state alone.

## Rollback Boundaries

- Database migrations are additive. Rollback of behavior is by disabling/revoking new capability paths and deploying a new forward migration if schema correction is required; do not destructively drop historical PROD0 records.
- n8n rollback restores the last approved export/hash and runs drift readback before re-enabling Tier-3 workflows.
- Cockpit rollback may redeploy the prior Vercel/Git SHA because Cockpit is not Reality.
- Notion projection rollback/resync never modifies canonical Reality.
- HF/Quant compute outputs are re-runnable from immutable input/hash contracts; failed compute never upgrades authority.
- A SEV-0/SEV-1 event freezes affected capabilities before service restoration.

## Definition of Done for the Implementation Program

Repository completion is not operational qualification. Code is implementation-complete only when exact-head tests/builds are GREEN and the resulting artifacts are reviewed. Product completion is achieved only after the 90-day Reality Experiment produces an evidence-backed verdict. The only successful PROD0 terminal qualification is:

`YMQ_PROD0_OPERATIONALLY_QUALIFIED / CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED`

Any earlier state must be named precisely, for example `REPOSITORY_GREEN`, `STAGING_PHYSICAL_PASS`, `P0_PASS`, `G1_ONE_BATTLE_PASS`, or `G2_THREE_BATTLE_PASS`; none implies production operational qualification.

## Self-Review Checklist

Before starting execution, verify the plan against the Written Spec:

- All four Cockpit workspaces and contextual Copilot have implementation tasks.
- All seven workflows have frozen contracts, deterministic reference logic, physical n8n implementation and exported hashes.
- ResearchCase/CaseVersion, review, events, workflow/compute runs, gates, projections, settlements and learning are represented in canonical storage.
- Domain Object + Event + Receipt atomicity and idempotency are covered by tests.
- Author != Reviewer and Founder-no-force-pass are covered by tests/contracts.
- Capital/Execution non-authorization is inherited and re-tested.
- DEV/STAGING/PROD separation and production human gates are explicit.
- Secrets, RBAC, machine identities, SLOs, incidents, kill switch, recovery and drift are covered.
- Three Battles and 90-day SCALE/NARROW/REFRAME/KILL verdicts are covered.
- No task requires Notion, n8n, Cockpit or Agent memory to reconstruct canonical history.
- No task silently changes Canon from a Learning Delta.
