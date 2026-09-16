# YMQ-NOTION-NATIVE1｜Machine Reality Binding × Event-Driven State Transition

**Status:** WRITTEN_SPEC / AWAITING_HUMAN_REVIEW  
**Date:** 2026-09-16  
**Repository:** `moonstachain/yuanli-invest`  
**Supabase Reality Plane:** `yuanli-invest-runtime` (`tbmoimbdhsrltvospwpu`)  
**Parent initiative:** `YMQ-NOTION-NATIVE0｜Human Intelligence Workbench`

---

## 1. Strategic Goal

Native0 proved that Notion can become a Human Intelligence Workbench through five Human Objects, Relations/Rollups, a 7-step state machine, dashboard views, Skills, and an Agent authority contract.

Native1 must prove a narrower and more important claim:

> **Can machine-owned Reality state from Supabase enter the Notion Human Work Graph without turning Notion into a source of truth, and can material changes in evidence/gates deterministically change or block the human workflow?**

The target loop is:

`Supabase Reality / Evidence → append-only event → fail-closed transition evaluation → Notion projection update → Human review/action → future runtime request`

This is not a Notion redesign and not a Capital/Execution automation project.

---

## 2. Non-Negotiable Authority Constitution

1. `Reality > Belief`.
2. `ClaimAuthority <= EvidenceAuthority`.
3. `UNKNOWN = DENY`.
4. `ResearchAuthority != CapitalAuthority != ExecutionAuthority`.
5. GitHub remains the Law Plane.
6. Supabase remains the runtime Reality/Evidence ledger.
7. Notion remains Human Work Graph / interaction / learning projection only.
8. Hugging Face remains replaceable experiment compute only.
9. A Notion property change MUST NOT grant Canon, Capital, Shadow, or Execution authority.
10. Machine-owned state may block or regress workflow fail-closed; it may not silently promote a research object into real-capital action.
11. `ResearchPass != CapitalPass`.
12. Every machine-to-Notion mutation must carry an immutable event ID, source runtime ID, source git SHA where available, `known_as_of/as_of`, authority, and delivery receipt.

---

## 3. Verified Current State

### 3.1 GitHub

Existing G1 artifacts on `main` already provide:

- `supabase/migrations/20260914_ymq_os0_g1_sovereign_stack.sql`
- `runtime/ymq_gateway/context_compiler.py`
- `runtime/ymq_gateway/router.py`
- `config/ymq_os0/notion_projection_manifest.v0.1.json`
- contract tests for Supabase and gateway authority separation.

Current gateway behavior already denies:

- `UNKNOWN / BLOCKED` evidence,
- Capital/Execution requests,
- position sizing, broker order, and real-capital movement.

Current Notion projection manifest already freezes:

- `role = PROJECTION_ONLY`,
- `canonical_truth = false`,
- `can_grant_authority = false`,
- `capital_authorized = false`,
- `execution_authorized = false`.

### 3.2 Supabase readback at design time

Project `tbmoimbdhsrltvospwpu` is `ACTIVE_HEALTHY`.

Observed row counts:

| Object | Rows |
|---|---:|
| `evidence.claim_receipts` | 0 |
| `runtime.agent_runs` | 1 |
| `runtime.research_projections` | 1 |
| `runtime.learning_deltas` | 0 |
| `runtime.reality_gate_runs` | 7 |

The only current `runtime.research_projections` row is the G1 Founder Intelligence projection:

- `projection_id = 9ef0d7cf-0650-4a33-a25b-4d989023722c`
- `run_id = 46bf317f-43a7-4b74-ad28-e58b2b9a33aa`
- `surface = Notion`
- `projection_type = FOUNDER_INTELLIGENCE`
- `canonical_truth = false`
- `can_grant_authority = false`
- `granted_authority = RESEARCH`
- `evidence_refs = []`
- Notion page ID in payload = `3dc8e1aa-ace4-81d0-b610-efe7b9f73af7`.

No Supabase Edge Functions currently exist.

The prior G1 plan mentioned `runtime.read_agent_context(...)`, but current physical readback shows no routines in schema `runtime`; Native1 MUST NOT assume that function exists.

### 3.3 Notion Native0 physical objects

Native0 currently uses these Human Object data sources:

- Capital Questions: `collection://89ea4be4-bbcf-4101-bb69-8721b3c10441`
- Research Projections: `collection://ba1748d0-ed0e-4e7f-b6a8-3a265210a072`
- Reality Audits: `collection://fe180284-ade7-4cee-98cd-f0fa27c40caf`
- Shadow & Settlements: `collection://95a7de7c-1cb4-45a0-b887-9d3362c2cef2`
- Learning Deltas: `collection://1f3c09c0-6041-4428-abb6-0c816ba31ad1`

Workbench page:

- `3dd8e1aa-ace4-81ce-9d23-d52297da3662`

Founder Desk:

- `3dd8e1aa-ace4-8185-a10a-fd4b5d159cfd`

Native0 currently has `Journey Stage`, `Gate Status`, and `Block Reason`, but the state machine is still human-editable and not yet bound to machine Reality.

---

## 4. Scope

Native1 contains four bounded subsystems:

1. **Machine Reality Outbox** — append-only delivery events in Supabase.
2. **Notion Projection Binding** — deterministic mapping between runtime objects and Notion Human Objects.
3. **Fail-Closed Transition Evaluator** — machine-safe state transitions and regressions.
4. **Notion Projection Adapter** — authenticated, idempotent, auditable delivery into Native0 properties.

Native1 explicitly excludes:

- real-capital actions,
- broker execution,
- portfolio sizing,
- Shadow authorization,
- full Narrative/Herding science completion,
- full Transmission science completion,
- a general-purpose workflow engine,
- replacing Notion with Supabase as the Human UX,
- making Notion the evidence store,
- publishing a Custom Agent,
- building a second YMQ repository.

---

## 5. Architecture Choice

### 5.1 Chosen approach: Transactional Outbox + Projection Adapter

Use an additive Supabase outbox rather than direct database-trigger HTTP calls.

Why:

- database writes and event creation can remain atomic,
- failed Notion writes do not roll back Reality writes,
- retries become explicit and auditable,
- idempotency is enforceable,
- delivery can be replayed without rewriting source events,
- Notion outages cannot contaminate the Reality Plane.

### 5.2 Physical flow

```text
Supabase Reality/Evidence write
        ↓ same DB transaction
runtime.human_projection_events  (append-only outbox)
        ↓
YMQ Notion Projection Adapter    (Supabase Edge Function)
        ↓
validate authority + event + transition
        ↓
resolve runtime ↔ Notion binding
        ↓
Notion Native0 object patch
        ↓
runtime.human_projection_deliveries
        ↓
ACK / RETRY / DEAD
```

The Edge Function is transport/orchestration only. It cannot grant authority.

---

## 6. New Supabase Runtime Objects

All additions are under existing schema `runtime`.

### 6.1 `runtime.human_projection_events`

Purpose: append-only transactional outbox.

Required columns:

- `event_id uuid primary key`
- `event_type text not null`
- `aggregate_type text not null`
- `aggregate_id text not null`
- `source_schema text not null`
- `source_table text not null`
- `source_pk text not null`
- `human_context jsonb not null default '{}'`
- `payload jsonb not null`
- `authority text not null default 'RESEARCH'`
- `known_as_of timestamptz null`
- `git_sha text null`
- `idempotency_key text not null unique`
- `event_status text not null` in `PENDING / IN_FLIGHT / ACKED / RETRY / DEAD`
- `attempt_count integer not null default 0`
- `last_error text null`
- `created_at timestamptz not null default now()`
- `available_after timestamptz not null default now()`
- `acked_at timestamptz null`

Constraints:

- authority may not exceed `RESEARCH`.
- event rows are immutable except delivery-state fields.
- no anon/authenticated write policies.

### 6.2 `runtime.notion_projection_bindings`

Purpose: deterministic identity mapping, never truth storage.

Required columns:

- `binding_id uuid primary key`
- `runtime_object_type text not null`
- `runtime_object_id text not null`
- `notion_object_type text not null`
- `notion_page_id text not null`
- `notion_data_source_id text not null`
- `binding_status text not null` in `ACTIVE / SUPERSEDED / REVOKED`
- `created_by_event_id uuid null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Unique active binding per `(runtime_object_type, runtime_object_id, notion_object_type)`.

### 6.3 `runtime.human_projection_deliveries`

Purpose: immutable delivery receipts.

Required columns:

- `delivery_id uuid primary key`
- `event_id uuid not null`
- `notion_page_id text not null`
- `request_hash text not null`
- `response_hash text null`
- `delivery_status text not null` in `ACKED / RETRY / DEAD`
- `http_status integer null`
- `attempt integer not null`
- `error_class text null`
- `created_at timestamptz not null default now()`

No secrets or full Notion token values may appear in receipts.

---

## 7. Frozen Event Types

Native1 supports only these machine events:

1. `CLAIM_RECEIPT_CREATED`
2. `RESEARCH_PROJECTION_CREATED`
3. `REALITY_GATE_SETTLED`
4. `LEARNING_DELTA_CREATED`
5. `AUTHORITY_DENIED`

Do not create generic catch-all event types in Native1.

### Event emission rules

- `CLAIM_RECEIPT_CREATED`: emitted after an admitted evidence claim receipt is persisted.
- `RESEARCH_PROJECTION_CREATED`: emitted after a research projection is persisted.
- `REALITY_GATE_SETTLED`: emitted when a `runtime.reality_gate_runs` row reaches a terminal gate status.
- `LEARNING_DELTA_CREATED`: emitted after a forward-only learning delta is persisted.
- `AUTHORITY_DENIED`: emitted when the gateway rejects an attempted authority escalation relevant to a bound Human Object.

Historical rows are not silently backfilled as if they were live events. Any replay is explicit and marked `REPLAY` in event payload metadata.

---

## 8. Human Context Contract

Machine events may update a Native0 work item only when a stable Human Context is present.

Frozen request context shape:

```json
{
  "human_context": {
    "surface": "NOTION",
    "capital_question_page_id": "<notion-page-uuid>",
    "research_projection_page_id": "<optional-notion-page-uuid>",
    "workspace_contract": "YMQ-NOTION-NATIVE1-v0.1"
  }
}
```

This context is an address, not authority.

If `capital_question_page_id` is absent or malformed, the event may be persisted but delivery MUST fail closed as `UNBOUND_HUMAN_CONTEXT`; the adapter must not guess the target page.

---

## 9. Notion Machine-Owned Projection Properties

Native1 must avoid silently overwriting user-authored thesis/content fields.

### 9.1 Capital Questions

Machine-owned fields to add or freeze:

- `Machine Evidence Status`
- `Machine Gate Status`
- `Machine Known As Of`
- `Machine Event ID`
- `Machine Source ID`
- `Machine Sync Status`
- `Machine Synced At`
- `Transition Suggestion`
- `Transition Reason`

Existing `Journey Stage`, `Gate Status`, and `Block Reason` remain visible Human Work properties, but Native1 treats their machine-updated values as projections from the transition evaluator. Human edits are not machine truth.

### 9.2 Research Projections

Add/freeze:

- `Runtime Projection ID`
- `Runtime Run ID`
- `Machine Evidence Status`
- `Machine Known As Of`
- `Machine Authority`
- `Machine Event ID`
- `Machine Sync Status`
- `Source Receipt ID`

### 9.3 Reality Audits

Add/freeze:

- `Runtime Gate Run ID`
- `Machine Gate Status`
- `Machine Event ID`
- `Machine Sync Status`

### 9.4 Shadow & Settlements

Native1 may only project `BLOCKED / NOT_AUTHORIZED` unless a future independent Shadow authorization is physically proven.

Add/freeze:

- `Machine Shadow Eligibility`
- `Machine Event ID`
- `Machine Sync Status`

### 9.5 Learning Deltas

Add/freeze:

- `Runtime Learning Delta ID`
- `Machine Effective After`
- `Machine Event ID`
- `Machine Sync Status`

---

## 10. Event-Driven State Transition Constitution

Native1 does NOT pretend every 7-step transition is machine-provable today.

### 10.1 Machine-enforceable transitions now

#### Any stage → EVIDENCE regression

Trigger:

- machine evidence becomes `BLOCKED` or `UNKNOWN`, or
- authority is denied.

Effect:

- `Machine Gate Status = BLOCKED/UNKNOWN`
- `Journey Stage = 02 EVIDENCE`
- `Block Reason` populated from machine reason
- no downstream automatic advance.

This regression is allowed from any research stage because `UNKNOWN = DENY`.

#### TRANSMISSION → AUDIT

Trigger:

- `RESEARCH_PROJECTION_CREATED`,
- admitted evidence status is not `BLOCKED/UNKNOWN`,
- projection payload contains a non-empty defeat condition,
- Human Context is bound.

Effect:

- `Journey Stage = 05 AUDIT`
- `Gate Status = OPEN`
- create or bind a Reality Audit work object.

No claim of scientific PASS is implied.

#### AUDIT → SHADOW

Native1 default: **DENY**.

Allowed only if a future machine-readable Shadow authorization contract exists and the relevant Reality Audit is `PASS`.

Until then:

- `Machine Shadow Eligibility = BLOCKED`
- `Journey Stage` remains `05 AUDIT`
- `Block Reason = SHADOW_NOT_AUTHORIZED`

#### SHADOW → LEARNING

Not active in Native1 unless a real Settlement object exists and a future Shadow authorization exists.

### 10.2 Human-assisted / suggestion-only transitions

The system currently lacks machine-authoritative Narrative and Transmission objects.

Therefore:

- `DISCOVER → EVIDENCE`: human/user task start.
- `EVIDENCE → NARRATIVE`: may be suggested after evidence admission, not auto-certified.
- `NARRATIVE → TRANSMISSION`: suggestion only.

Native1 may populate `Transition Suggestion` and `Transition Reason`; it must not manufacture scientific completion for these stages.

---

## 11. Projection Adapter Contract

Supabase Edge Function name:

`ymq-notion-projector`

### Responsibilities

1. receive or pull exactly one outbox event,
2. load event by ID using service-role server-side access,
3. verify event has `RESEARCH`-or-lower authority,
4. recompute idempotency key / payload hash,
5. resolve the Notion binding or explicit Human Context page ID,
6. evaluate permitted transition,
7. patch only whitelisted Notion properties,
8. write a delivery receipt,
9. ACK or RETRY the event.

### Forbidden behavior

- no direct broker/execution calls,
- no Capital Authority mutation,
- no GitHub Canon write,
- no mutation of evidence source rows,
- no reading or writing Notion secrets into receipts/logs,
- no target-page guessing by title/search,
- no automatic creation of Shadow authorization.

### Authentication

The Edge Function must use a Notion integration credential injected through Supabase secret/environment configuration.

Credential provisioning is a Human Security Gate. The credential MUST NOT be committed to GitHub or placed in Notion pages.

---

## 12. Delivery Semantics

### Idempotency

One machine event may mutate one Notion object at most once per `idempotency_key`.

Repeated delivery after timeout must either:

- detect an ACKed delivery and no-op, or
- resend an identical request safely.

### Retry policy

- 429 / 5xx / transient network errors → exponential retry.
- malformed target / authority violation / schema mismatch → DEAD or BLOCKED, no blind retry.
- maximum retry count must be finite and configured.

### Ordering

Events for the same aggregate are processed in `created_at` order.

A stale event with `known_as_of` older than the latest ACKed event for the same machine-owned field must not overwrite the newer projection.

---

## 13. Failure Modes

| Failure | Required behavior |
|---|---|
| Notion unavailable | Reality write remains committed; outbox RETRY |
| Notion credential invalid | delivery BLOCKED/DEAD; no Reality rollback |
| target page missing | `UNBOUND_HUMAN_CONTEXT`; no title guessing |
| evidence becomes UNKNOWN | regress to EVIDENCE, fail closed |
| stale event arrives late | no overwrite of newer machine state |
| duplicate event | idempotent no-op |
| requested Capital/Execution authority | deny + optional `AUTHORITY_DENIED` event |
| Notion user manually edits machine field | next valid machine projection may overwrite; machine truth remains Supabase |
| schema property renamed/deleted in Notion | adapter fails closed with `SCHEMA_MISMATCH` |

---

## 14. Test Strategy

Implementation follows RED → GREEN → review → fresh verification.

### Repository contract tests

New tests must prove:

1. outbox/binding/delivery DDL exists and is additive,
2. RLS is enabled and no public write policy is created,
3. event authority cannot exceed RESEARCH,
4. idempotency key is unique,
5. transition evaluator regresses to EVIDENCE on UNKNOWN/BLOCKED,
6. adapter denies SHADOW promotion by default,
7. stale events cannot overwrite newer state,
8. duplicate delivery is idempotent,
9. Notion patch whitelist excludes thesis/content/Capital/Execution authority fields,
10. secret literals are absent from repository artifacts.

### Supabase Reality tests

After repository tests pass:

- apply migration to `yuanli-invest-runtime`,
- read back tables, constraints, indexes, RLS,
- run security and performance advisors,
- create secret-free synthetic event,
- verify outbox lifecycle through ACK/RETRY without modifying real Capital/Execution authority.

### Notion Reality proof

Use one explicit DEMO object only.

Expected proof:

1. DEMO Capital Question contains stable page ID.
2. synthetic research event binds to it.
3. adapter writes machine-owned fields only.
4. duplicate event produces no duplicate mutation.
5. synthetic `UNKNOWN` evidence regresses DEMO to EVIDENCE.
6. attempted `AUDIT → SHADOW` remains BLOCKED.
7. Notion is read back and compared with Supabase delivery receipt.

The demo must remain visibly labelled `DEMO`.

---

## 15. GitHub Artifacts Expected in Implementation

Planned additions/modifications after spec approval:

- `config/ymq_notion_native1/machine_reality_binding.v0.1.json`
- `supabase/migrations/20260916_ymq_notion_native1_machine_reality_binding.sql`
- `runtime/ymq_notion_native1/events.py`
- `runtime/ymq_notion_native1/transitions.py`
- `runtime/ymq_notion_native1/notion_projection.py`
- `supabase/functions/ymq-notion-projector/index.ts`
- `supabase/functions/ymq-notion-projector/deno.json`
- `tests/test_ymq_notion_native1_contract.py`
- `tests/test_ymq_notion_native1_transitions.py`
- `tests/test_ymq_notion_native1_projection.py`
- `docs/architecture/ymq_notion_native1/YMQ-NOTION-NATIVE1-MACHINE-QUALIFICATION-RECEIPT-v0.1.md`

No new repository.

---

## 16. Implementation Phases

### G0｜Contract Freeze

Freeze event schema, binding schema, field ownership, transition rules, non-authorizations.

### G1｜Supabase Outbox Reality

Implement additive migration and structural tests; apply only after GREEN.

### G2｜Transition Engine

Implement deterministic fail-closed transition evaluator with no Notion network dependency.

### G3｜Projection Adapter

Implement Notion patch builder and Edge Function transport; secret provisioning remains Human Security Gate.

### G4｜Native0 DEMO Binding

Bind one DEMO Question → Projection → Audit flow and verify machine-owned fields physically update.

### G5｜Adversarial Replay

Test duplicate, stale, UNKNOWN, schema mismatch, Notion outage, and unauthorized Shadow transition.

### G6｜Qualification

Fresh exact-head repository tests + Supabase readback + Notion readback + advisor checks + receipt.

---

## 17. Completion Condition

Native1 may be declared machine-qualified only when all of the following are physically proven:

- additive Supabase outbox/binding/delivery objects exist with RLS,
- deterministic transition tests are GREEN,
- one DEMO event reaches Notion through the adapter and is read back,
- duplicate and stale events are harmless,
- UNKNOWN/BLOCKED evidence regresses or blocks the workflow,
- SHADOW promotion remains denied without independent authorization,
- delivery receipts contain no secrets,
- Notion remains projection-only,
- GitHub protected checks are GREEN on exact head,
- security/performance advisors contain no unaddressed Native1-critical issue.

Final allowed status:

`YMQ_NOTION_NATIVE1_MACHINE_QUALIFIED / NOTION_PROJECTION_ONLY / CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED / SHADOW_NOT_AUTHORIZED`

---

## 18. Explicit Non-Goals / Anti-Claims

Native1 does **not** prove:

- that YMQ predicts markets,
- that Narrative/Herding science has passed,
- that Dynamic Transmission science has passed,
- that Shadow Runtime is authorized,
- that a Custom Agent is published,
- that any research output is fit for live capital,
- that Notion is a source of truth.

The success criterion is narrower:

> **Machine Reality can safely and audibly move Human Work without Human Work becoming Reality.**
