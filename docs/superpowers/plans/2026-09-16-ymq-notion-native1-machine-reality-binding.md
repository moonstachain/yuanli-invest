# YMQ-NOTION-NATIVE1 Machine Reality Binding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bind Supabase machine-owned Reality/Evidence state into the existing Notion Native0 Human Work Graph through an auditable transactional outbox, fail-closed transition engine, idempotent Notion projection adapter, durable wake/retry path, and explicit Research-only authority boundaries.

**Architecture:** GitHub remains the Law Plane, `yuanli-invest-runtime` remains the Reality/Evidence ledger, and Notion remains a Human Work Graph / projection surface. Supabase emits append-only projection events into an outbox; a deterministic transition engine decides whether the Human Work state may regress, advance one stage, or only receive a suggestion; a Supabase Edge Function patches only whitelisted Notion machine-owned properties and records immutable delivery receipts. `UNKNOWN/BLOCKED` evidence fails closed, forward automation advances at most one stage, and Shadow/Capital/Execution authority remain denied.

**Tech Stack:** Python 3.12 + `unittest`, PostgreSQL 17 / Supabase, RLS, Supabase Vault, `pg_net`, `pg_cron`, Deno/TypeScript Edge Functions, Notion API/MCP, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-16-ymq-notion-native1-machine-reality-binding-design.md`

## Global Constraints

- Reuse `moonstachain/yuanli-invest`; do not create a second Law Plane.
- Reuse Supabase project `yuanli-invest-runtime` (`tbmoimbdhsrltvospwpu`) and the existing `evidence`, `pit`, `runtime` lineage.
- `Reality > Belief`; `ClaimAuthority <= EvidenceAuthority`; `UNKNOWN = DENY`.
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`.
- Notion is Human Work Graph / projection only; it is not Evidence truth, Canon, Capital Authority, or Execution Authority.
- Automatic forward transitions advance at most one stage; fail-closed regression to `02 EVIDENCE` is allowed from any research stage.
- `AUDIT -> SHADOW` remains denied unless a separate machine-readable Shadow authorization exists; Native1 does not create that authorization.
- No secret literal may be committed. `.env*` remains ignored except `.env.example`.
- Existing user-authored thesis/body content in Notion is never overwritten by the machine adapter.
- Historical runtime rows are not silently reclassified as live events; explicit replays carry `metadata.mode = "REPLAY"`.
- Every production behavior change follows RED -> GREEN -> review -> fresh verification.
- Existing protected workflow job names `contracts` and `governance` must not be renamed.
- No production Supabase migration is applied until repository contract tests for that migration are GREEN.
- No Notion network mutation occurs until the machine-owned schema fields are physically created and read back.
- No wake scheduler is activated until the Edge Function is deployed and the Notion integration secret is provisioned through a human security gate.

## File Map

### GitHub contract / runtime
- Create `config/ymq_notion_native1/machine_reality_binding.v0.1.json` — frozen event types, Notion data-source IDs, whitelisted fields, authority boundaries, retry policy.
- Create `scripts/validate_ymq_notion_native1.py` — static contract validator used by CI.
- Create `runtime/ymq_notion_native1/__init__.py` — package marker.
- Create `runtime/ymq_notion_native1/contracts.py` — typed event and transition dataclasses.
- Create `runtime/ymq_notion_native1/events.py` — deterministic idempotency/source metadata helpers.
- Create `runtime/ymq_notion_native1/transitions.py` — fail-closed state transition evaluator.
- Create `runtime/ymq_notion_native1/notion_projection.py` — pure Notion patch builder and stale-event guard.

### Supabase
- Create `supabase/migrations/20260916_ymq_notion_native1_machine_reality_binding.sql` — outbox, bindings, delivery receipts, trigger emitters, claim/ack RPCs, RLS, indexes.
- Create `supabase/migrations/20260916_ymq_notion_native1_wake_schedule.sql` — `pg_net`/`pg_cron` wake path, applied only after Edge Function + secret gate.
- Create `supabase/functions/ymq-notion-projector/index.ts` — adapter worker for one claimed event at a time.
- Create `supabase/functions/ymq-notion-projector/deno.json` — pinned imports.

### Tests
- Create `tests/test_ymq_notion_native1_contract.py` — config/authority/CI contract.
- Create `tests/test_ymq_notion_native1_supabase_contract.py` — migration/RLS/outbox/RPC structural tests.
- Create `tests/test_ymq_notion_native1_transitions.py` — one-step forward, fail-closed regression, Shadow denial.
- Create `tests/test_ymq_notion_native1_projection.py` — whitelist, stale, idempotent request construction.
- Create `tests/test_ymq_notion_native1_edge_contract.py` — static Edge Function contract / secret-leak checks.

### CI / receipts
- Modify `.github/workflows/ci.yml` — add `python scripts/validate_ymq_notion_native1.py` to existing `contracts` job.
- Create `docs/architecture/ymq_notion_native1/YMQ-NOTION-NATIVE1-MACHINE-QUALIFICATION-RECEIPT-v0.1.md` — final evidence and explicit non-authorizations.

---

### Task 1: Freeze Native1 machine contract and CI validator

**Files:**
- Create: `config/ymq_notion_native1/machine_reality_binding.v0.1.json`
- Create: `scripts/validate_ymq_notion_native1.py`
- Create: `tests/test_ymq_notion_native1_contract.py`

**Interfaces:**
- Consumes: Native1 Written Spec and existing G1 Notion projection manifest.
- Produces: `validate_contract(contract: dict) -> list[str]` and a JSON contract consumed by runtime/tests/Edge Function implementation.

- [ ] **Step 1: Write failing contract tests**

Create `tests/test_ymq_notion_native1_contract.py` with tests equivalent to:

```python
import json
import unittest
from pathlib import Path

from scripts.validate_ymq_notion_native1 import validate_contract

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/ymq_notion_native1/machine_reality_binding.v0.1.json"


class Native1ContractTests(unittest.TestCase):
    def test_contract_is_research_only_and_projection_only(self):
        payload = json.loads(CONTRACT.read_text())
        self.assertEqual(payload["authority"]["max_grant"], "RESEARCH")
        self.assertFalse(payload["authority"]["capital_authorized"])
        self.assertFalse(payload["authority"]["execution_authorized"])
        self.assertFalse(payload["authority"]["shadow_authorized"])
        self.assertEqual(payload["notion"]["role"], "PROJECTION_ONLY")

    def test_event_types_are_closed_set(self):
        payload = json.loads(CONTRACT.read_text())
        self.assertEqual(
            set(payload["event_types"]),
            {
                "CLAIM_RECEIPT_CREATED",
                "RESEARCH_PROJECTION_CREATED",
                "REALITY_GATE_SETTLED",
                "LEARNING_DELTA_CREATED",
                "AUTHORITY_DENIED",
            },
        )

    def test_forward_transition_is_single_step(self):
        payload = json.loads(CONTRACT.read_text())
        self.assertEqual(payload["transition_policy"]["max_forward_steps"], 1)
        self.assertEqual(payload["transition_policy"]["fail_closed_stage"], "02 EVIDENCE")

    def test_whitelist_contains_no_authority_or_thesis_fields(self):
        payload = json.loads(CONTRACT.read_text())
        fields = set(payload["notion"]["capital_question_machine_fields"])
        forbidden = {"Thesis", "Capital Authority", "Execution Authority", "Shadow Authorized"}
        self.assertTrue(fields.isdisjoint(forbidden))

    def test_validator_accepts_frozen_contract(self):
        payload = json.loads(CONTRACT.read_text())
        self.assertEqual(validate_contract(payload), [])
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
python -m unittest tests.test_ymq_notion_native1_contract -v
```

Expected: import/file failures because Native1 contract/validator do not yet exist.

- [ ] **Step 3: Create the frozen JSON contract**

Create `config/ymq_notion_native1/machine_reality_binding.v0.1.json` with exactly these top-level sections:

```json
{
  "contract_id": "YMQ-NOTION-NATIVE1-v0.1",
  "authority": {
    "max_grant": "RESEARCH",
    "capital_authorized": false,
    "execution_authorized": false,
    "shadow_authorized": false,
    "unknown_is_deny": true
  },
  "event_types": [
    "CLAIM_RECEIPT_CREATED",
    "RESEARCH_PROJECTION_CREATED",
    "REALITY_GATE_SETTLED",
    "LEARNING_DELTA_CREATED",
    "AUTHORITY_DENIED"
  ],
  "transition_policy": {
    "max_forward_steps": 1,
    "fail_closed_stage": "02 EVIDENCE",
    "transmission_stage": "04 TRANSMISSION",
    "audit_stage": "05 AUDIT",
    "shadow_stage": "06 SHADOW"
  },
  "retry_policy": {
    "max_attempts": 6,
    "base_delay_seconds": 30,
    "max_delay_seconds": 1800
  },
  "notion": {
    "role": "PROJECTION_ONLY",
    "capital_questions_data_source": "collection://89ea4be4-bbcf-4101-bb69-8721b3c10441",
    "research_projections_data_source": "collection://ba1748d0-ed0e-4e7f-b6a8-3a265210a072",
    "reality_audits_data_source": "collection://fe180284-ade7-4cee-98cd-f0fa27c40caf",
    "shadow_settlements_data_source": "collection://95a7de7c-1cb4-45a0-b887-9d3362c2cef2",
    "learning_deltas_data_source": "collection://1f3c09c0-6041-4428-abb6-0c816ba31ad1",
    "capital_question_machine_fields": [
      "Machine Evidence Status",
      "Machine Gate Status",
      "Machine Known As Of",
      "Machine Event ID",
      "Machine Source ID",
      "Machine Sync Status",
      "Machine Synced At",
      "Transition Suggestion",
      "Transition Reason",
      "Journey Stage",
      "Gate Status",
      "Block Reason"
    ]
  }
}
```

- [ ] **Step 4: Implement the static validator**

`validate_contract()` must reject: unknown event types, `max_grant != RESEARCH`, any authorized Capital/Execution/Shadow flag, Notion role other than `PROJECTION_ONLY`, forward steps other than 1, fail-closed stage other than `02 EVIDENCE`, and forbidden authority/thesis fields in the Notion machine whitelist.

Use the existing `scripts/validate_ymq_os0_g1.py` style: return a list of symbolic error strings and print `PASS:` only when empty.

- [ ] **Step 5: Run targeted and full repository tests**

```bash
python -m unittest tests.test_ymq_notion_native1_contract -v
python scripts/validate_ymq_notion_native1.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add config/ymq_notion_native1 scripts/validate_ymq_notion_native1.py tests/test_ymq_notion_native1_contract.py
git commit -m "feat: freeze YMQ Notion Native1 machine contract"
```

---

### Task 2: Implement deterministic transition engine before any network code

**Files:**
- Create: `runtime/ymq_notion_native1/__init__.py`
- Create: `runtime/ymq_notion_native1/contracts.py`
- Create: `runtime/ymq_notion_native1/transitions.py`
- Create: `tests/test_ymq_notion_native1_transitions.py`

**Interfaces:**
- Consumes: event type, current Journey Stage, machine evidence status, defeat-condition presence, authority-denied flag.
- Produces: `TransitionDecision(action, target_stage, gate_status, block_reason, suggestion, reason)`.

- [ ] **Step 1: Write RED tests for the exact state rules**

Use these cases:

```python
import unittest
from runtime.ymq_notion_native1.transitions import evaluate_transition


class Native1TransitionTests(unittest.TestCase):
    def test_unknown_evidence_regresses_any_stage_to_evidence(self):
        decision = evaluate_transition(
            current_stage="05 AUDIT",
            event_type="CLAIM_RECEIPT_CREATED",
            evidence_status="UNKNOWN",
            has_defeat_condition=False,
            authority_denied=False,
        )
        self.assertEqual(decision.action, "REGRESS")
        self.assertEqual(decision.target_stage, "02 EVIDENCE")
        self.assertEqual(decision.gate_status, "UNKNOWN")

    def test_blocked_evidence_regresses_to_evidence(self):
        decision = evaluate_transition(
            current_stage="04 TRANSMISSION",
            event_type="CLAIM_RECEIPT_CREATED",
            evidence_status="BLOCKED",
            has_defeat_condition=True,
            authority_denied=False,
        )
        self.assertEqual(decision.target_stage, "02 EVIDENCE")
        self.assertEqual(decision.gate_status, "BLOCKED")

    def test_projection_advances_transmission_to_audit_only(self):
        decision = evaluate_transition(
            current_stage="04 TRANSMISSION",
            event_type="RESEARCH_PROJECTION_CREATED",
            evidence_status="LIMITED",
            has_defeat_condition=True,
            authority_denied=False,
        )
        self.assertEqual(decision.action, "ADVANCE")
        self.assertEqual(decision.target_stage, "05 AUDIT")
        self.assertEqual(decision.gate_status, "OPEN")

    def test_projection_from_evidence_only_suggests_audit(self):
        decision = evaluate_transition(
            current_stage="02 EVIDENCE",
            event_type="RESEARCH_PROJECTION_CREATED",
            evidence_status="PASS",
            has_defeat_condition=True,
            authority_denied=False,
        )
        self.assertEqual(decision.action, "SUGGEST")
        self.assertIsNone(decision.target_stage)
        self.assertEqual(decision.suggestion, "05 AUDIT")

    def test_missing_defeat_condition_blocks_audit_advance(self):
        decision = evaluate_transition(
            current_stage="04 TRANSMISSION",
            event_type="RESEARCH_PROJECTION_CREATED",
            evidence_status="PASS",
            has_defeat_condition=False,
            authority_denied=False,
        )
        self.assertEqual(decision.action, "BLOCK")
        self.assertEqual(decision.block_reason, "DEFEAT_CONDITION_REQUIRED")

    def test_shadow_is_denied_in_native1(self):
        decision = evaluate_transition(
            current_stage="05 AUDIT",
            event_type="REALITY_GATE_SETTLED",
            evidence_status="PASS",
            has_defeat_condition=True,
            authority_denied=False,
        )
        self.assertEqual(decision.action, "BLOCK")
        self.assertEqual(decision.block_reason, "SHADOW_NOT_AUTHORIZED")
```

- [ ] **Step 2: Verify RED**

```bash
python -m unittest tests.test_ymq_notion_native1_transitions -v
```

Expected: import failure.

- [ ] **Step 3: Create typed contracts**

`runtime/ymq_notion_native1/contracts.py`:

```python
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ProjectionEvent:
    event_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    authority: str
    known_as_of: datetime | None
    human_context: dict[str, Any]
    payload: dict[str, Any]
    git_sha: str | None = None


@dataclass(frozen=True)
class TransitionDecision:
    action: str
    target_stage: str | None
    gate_status: str | None
    block_reason: str | None
    suggestion: str | None
    reason: str
```

- [ ] **Step 4: Implement `evaluate_transition()` as a pure function**

Rules in this order:

1. `authority_denied` -> `REGRESS` to `02 EVIDENCE`, gate `BLOCKED`, reason `AUTHORITY_DENIED`.
2. evidence `UNKNOWN` -> `REGRESS` to `02 EVIDENCE`, gate `UNKNOWN`.
3. evidence `BLOCKED`/`DENY`/`None` -> `REGRESS` to `02 EVIDENCE`, gate `BLOCKED`.
4. `RESEARCH_PROJECTION_CREATED` + missing defeat condition -> `BLOCK`, reason `DEFEAT_CONDITION_REQUIRED`.
5. `RESEARCH_PROJECTION_CREATED` + current stage `04 TRANSMISSION` + admitted evidence -> one-step `ADVANCE` to `05 AUDIT`, gate `OPEN`.
6. same projection from any earlier stage -> `SUGGEST` `05 AUDIT`, never skip.
7. `REALITY_GATE_SETTLED` while current `05 AUDIT` -> `BLOCK`, reason `SHADOW_NOT_AUTHORIZED`.
8. everything else -> `NOOP`.

- [ ] **Step 5: Run tests**

```bash
python -m unittest tests.test_ymq_notion_native1_transitions -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 6: Commit**

```bash
git add runtime/ymq_notion_native1 tests/test_ymq_notion_native1_transitions.py
git commit -m "feat: add fail-closed Native1 transition engine"
```

---

### Task 3: Build pure Notion patch projection and stale-event guard

**Files:**
- Create: `runtime/ymq_notion_native1/events.py`
- Create: `runtime/ymq_notion_native1/notion_projection.py`
- Create: `tests/test_ymq_notion_native1_projection.py`

**Interfaces:**
- Consumes: `ProjectionEvent`, `TransitionDecision`, current Notion `Machine Known As Of`.
- Produces: deterministic Notion property patch; never performs HTTP.

- [ ] **Step 1: Write RED tests**

Cover:

```python
import unittest
from datetime import datetime, timezone
from runtime.ymq_notion_native1.contracts import ProjectionEvent, TransitionDecision
from runtime.ymq_notion_native1.notion_projection import build_capital_question_patch, is_stale


class Native1ProjectionTests(unittest.TestCase):
    def _event(self, when="2026-09-16T00:00:00+00:00"):
        return ProjectionEvent(
            event_id="11111111-1111-1111-1111-111111111111",
            event_type="RESEARCH_PROJECTION_CREATED",
            aggregate_type="RESEARCH_PROJECTION",
            aggregate_id="rp-demo",
            authority="RESEARCH",
            known_as_of=datetime.fromisoformat(when),
            human_context={"surface": "NOTION", "capital_question_page_id": "3dd8e1aaace48121a06edfe05b699035"},
            payload={"evidence_status": "LIMITED", "defeat_condition": "capex decelerates"},
            git_sha="abc123",
        )

    def test_stale_event_is_detected(self):
        event = self._event("2026-09-15T00:00:00+00:00")
        latest = datetime(2026, 9, 16, tzinfo=timezone.utc)
        self.assertTrue(is_stale(event.known_as_of, latest))

    def test_patch_only_contains_machine_whitelist(self):
        event = self._event()
        decision = TransitionDecision("ADVANCE", "05 AUDIT", "OPEN", None, None, "PROJECTION_READY_FOR_AUDIT")
        patch = build_capital_question_patch(event, decision)
        forbidden = {"Thesis", "Capital Authority", "Execution Authority", "Shadow Authorized"}
        self.assertTrue(set(patch).isdisjoint(forbidden))
        self.assertEqual(patch["Journey Stage"], "05 AUDIT")
        self.assertEqual(patch["Gate Status"], "OPEN")
        self.assertEqual(patch["Machine Event ID"], event.event_id)

    def test_suggestion_does_not_change_journey_stage(self):
        event = self._event()
        decision = TransitionDecision("SUGGEST", None, None, None, "05 AUDIT", "INTERMEDIATE_STAGES_REQUIRED")
        patch = build_capital_question_patch(event, decision)
        self.assertNotIn("Journey Stage", patch)
        self.assertEqual(patch["Transition Suggestion"], "05 AUDIT")
```

- [ ] **Step 2: Verify RED**

```bash
python -m unittest tests.test_ymq_notion_native1_projection -v
```

- [ ] **Step 3: Implement deterministic event helpers**

`events.py` must expose:

```python
def canonical_json(payload: dict) -> str: ...
def payload_sha256(payload: dict) -> str: ...
def make_idempotency_key(event_type: str, aggregate_type: str, aggregate_id: str, payload: dict) -> str: ...
```

Use `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False)` and SHA-256.

- [ ] **Step 4: Implement pure patch builder**

`notion_projection.py` must:

- always include `Machine Event ID`, `Machine Source ID`, `Machine Sync Status="SYNCED"`, `Machine Synced At`, and `Machine Known As Of` when present;
- add `Machine Evidence Status` only from machine payload;
- on `REGRESS`, set `Journey Stage="02 EVIDENCE"`, `Gate Status`, `Block Reason`;
- on `ADVANCE`, set only the one permitted target stage and gate;
- on `SUGGEST`, set only `Transition Suggestion` and `Transition Reason`;
- on `BLOCK`, keep Journey Stage unchanged and populate `Block Reason`/`Transition Reason`;
- never add user thesis/body, Capital Authority, Execution Authority, or Shadow authorization fields.

- [ ] **Step 5: Run tests and full regression**

```bash
python -m unittest tests.test_ymq_notion_native1_projection -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 6: Commit**

```bash
git add runtime/ymq_notion_native1/events.py runtime/ymq_notion_native1/notion_projection.py tests/test_ymq_notion_native1_projection.py
git commit -m "feat: add deterministic Notion projection builder"
```

---

### Task 4: Add Supabase transactional outbox, binding, delivery receipts, and service-role RPCs

**Files:**
- Create: `supabase/migrations/20260916_ymq_notion_native1_machine_reality_binding.sql`
- Create: `tests/test_ymq_notion_native1_supabase_contract.py`

**Interfaces:**
- Consumes: existing `evidence.claim_receipts`, `runtime.agent_runs`, `runtime.research_projections`, `runtime.learning_deltas`, `runtime.reality_gate_runs`.
- Produces: `runtime.human_projection_events`, `runtime.notion_projection_bindings`, `runtime.human_projection_deliveries`; public service-role-only claim/ack RPCs.

- [ ] **Step 1: Write structural RED tests**

Assertions must verify the migration text includes:

```python
for table in (
    "runtime.human_projection_events",
    "runtime.notion_projection_bindings",
    "runtime.human_projection_deliveries",
):
    self.assertIn(f"create table if not exists {table}", sql)
    self.assertIn(f"alter table {table} enable row level security", sql)

self.assertIn("check (authority = 'RESEARCH')", sql)
self.assertIn("idempotency_key text not null unique", sql)
self.assertIn("create or replace function public.ymq_native1_claim_projection_event", sql)
self.assertIn("create or replace function public.ymq_native1_finish_projection_event", sql)
self.assertIn("grant execute on function public.ymq_native1_claim_projection_event", sql)
self.assertNotIn("grant insert on runtime.human_projection_events to anon", sql)
self.assertNotIn("grant insert on runtime.human_projection_events to authenticated", sql)
```

Also assert trigger emitters exist for `research_projections`, `learning_deltas`, `claim_receipts`, and `reality_gate_runs`.

- [ ] **Step 2: Verify RED**

```bash
python -m unittest tests.test_ymq_notion_native1_supabase_contract -v
```

- [ ] **Step 3: Implement the additive migration**

The migration must create:

1. `runtime.human_projection_events` with the spec columns and checks.
2. `runtime.notion_projection_bindings` with partial unique index for active bindings.
3. `runtime.human_projection_deliveries` with FK to event and immutable insert-only semantics.
4. RLS enabled on all three; no `anon` or `authenticated` policies.
5. indexes on `(event_status, available_after, created_at)`, `event_id`, and active binding lookup.

Add `runtime.enforce_projection_event_immutability()` BEFORE UPDATE trigger that raises if any of these change: `event_type`, `aggregate_type`, `aggregate_id`, `source_schema`, `source_table`, `source_pk`, `human_context`, `payload`, `authority`, `known_as_of`, `git_sha`, `idempotency_key`, `created_at`. Operational fields may change: `event_status`, `attempt_count`, `last_error`, `available_after`, `acked_at`.

- [ ] **Step 4: Add one-event-at-a-time service-role RPCs**

`public.ymq_native1_claim_projection_event()` must be `SECURITY DEFINER`, use `FOR UPDATE SKIP LOCKED`, select the oldest `PENDING/RETRY` row whose `available_after <= now()`, mark it `IN_FLIGHT`, increment `attempt_count`, and return the event fields.

`public.ymq_native1_finish_projection_event(p_event_id uuid, p_status text, p_error text, p_available_after timestamptz)` must only accept `ACKED/RETRY/DEAD`; ACK sets `acked_at=now()`, RETRY sets `available_after`, DEAD preserves error. Revoke from public/anon/authenticated and grant only to `service_role`.

- [ ] **Step 5: Add source event emitters**

Implement AFTER INSERT trigger functions:

- `runtime.emit_native1_research_projection_event()` — join `runtime.agent_runs` on `NEW.run_id`; human context comes only from `agent_runs.request_payload->'human_context'`; payload includes `projection_id`, `run_id`, `projection_type`, `surface`, `payload`, and any `evidence_status` / `defeat_condition` already present in projection payload.
- `runtime.emit_native1_learning_delta_event()` — join `source_run_id` to `agent_runs` for human context.
- `runtime.emit_native1_claim_receipt_event()` — read optional `NEW.receipt->'human_context'`; if absent, enqueue with `{}` and let adapter fail closed as `UNBOUND_HUMAN_CONTEXT`.
- `runtime.emit_native1_reality_gate_event()` — read optional `NEW.receipt->'human_context'` and emit only terminal statuses `PASS`, `FAIL`, `BLOCKED`, `UNKNOWN`, `SCIENTIFIC_NO_GO`.

Idempotency key format must be deterministic: `<EVENT_TYPE>:<source-pk>:<content-hash-or-source-version>`.

- [ ] **Step 6: Run targeted/full tests**

```bash
python -m unittest tests.test_ymq_notion_native1_supabase_contract -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 7: Commit before touching production Supabase**

```bash
git add supabase/migrations/20260916_ymq_notion_native1_machine_reality_binding.sql tests/test_ymq_notion_native1_supabase_contract.py
git commit -m "feat: add Native1 transactional projection outbox"
```

- [ ] **Step 8: Apply migration to `yuanli-invest-runtime` only after GREEN**

Use the Supabase migration action with project `tbmoimbdhsrltvospwpu` and migration name `ymq_notion_native1_machine_reality_binding`.

- [ ] **Step 9: Physical readback and advisors**

Query `information_schema`, `pg_indexes`, `pg_policies`, and `pg_proc` to prove tables, RLS, constraints, indexes, and service-role-only RPCs. Run Supabase security and performance advisors and record any Native1-critical findings before proceeding.

---

### Task 5: Implement Edge Function adapter contract without activating wake-up yet

**Files:**
- Create: `supabase/functions/ymq-notion-projector/index.ts`
- Create: `supabase/functions/ymq-notion-projector/deno.json`
- Create: `tests/test_ymq_notion_native1_edge_contract.py`

**Interfaces:**
- Consumes: one event from `public.ymq_native1_claim_projection_event`, Native1 transition rules, Notion target page/data-source IDs.
- Produces: one Notion machine-property patch and one immutable `runtime.human_projection_deliveries` receipt; final event status ACK/RETRY/DEAD.

- [ ] **Step 1: Write RED static contract tests**

Assert Edge Function source contains:

- env reads for `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `NOTION_YMQ_NATIVE1_TOKEN`;
- call to RPC `ymq_native1_claim_projection_event`;
- a fixed machine-field whitelist;
- no strings `broker_order`, `position_sizing`, `real_capital_move` as allowed operations;
- explicit `SHADOW_NOT_AUTHORIZED` handling;
- SHA-256 request/response hashing;
- insert into `runtime.human_projection_deliveries` through a service-role RPC or a narrowly scoped public service-role function;
- finish event with ACK/RETRY/DEAD;
- no literal prefix resembling a Notion token (`secret_`) or service role JWT.

- [ ] **Step 2: Verify RED**

```bash
python -m unittest tests.test_ymq_notion_native1_edge_contract -v
```

- [ ] **Step 3: Implement Edge Function imports and startup checks**

`deno.json`:

```json
{
  "imports": {
    "@supabase/supabase-js": "jsr:@supabase/supabase-js@2"
  }
}
```

At startup, require all three environment variables. If `NOTION_YMQ_NATIVE1_TOKEN` is absent, return HTTP 503 with body `{ "status": "CONFIG_BLOCKED", "reason": "NOTION_TOKEN_MISSING" }` without claiming an event.

- [ ] **Step 4: Implement one-event worker semantics**

The function must:

1. authenticate the wake request using `x-ymq-wake-token` against a service-role-only RPC that reads the server-side wake secret;
2. claim exactly one event;
3. reject `authority != RESEARCH` as DEAD and record `AUTHORITY_DENY`;
4. resolve `capital_question_page_id` only from validated human context or an ACTIVE binding; never title-search;
5. fetch current Notion page properties needed for stage/staleness;
6. compute transition locally using the same frozen rules as Python tests;
7. if stale, ACK as no-op with delivery status ACKED and error_class `STALE_NOOP`;
8. PATCH only whitelisted properties;
9. write an immutable delivery receipt with request/response hashes and no token;
10. finish the outbox event ACK/RETRY/DEAD.

Transient retry classes: HTTP 429, 500, 502, 503, 504, fetch timeout/network errors. Backoff: `min(30 * 2^(attempt-1), 1800)` seconds; after attempt 6 -> DEAD.

Permanent failures: `UNBOUND_HUMAN_CONTEXT`, `SCHEMA_MISMATCH`, `AUTHORITY_DENY`, malformed event.

- [ ] **Step 5: Run tests**

```bash
python -m unittest tests.test_ymq_notion_native1_edge_contract -v
python scripts/leak_guard.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 6: Commit**

```bash
git add supabase/functions/ymq-notion-projector tests/test_ymq_notion_native1_edge_contract.py
git commit -m "feat: add Native1 Notion projection adapter"
```

- [ ] **Step 7: Deploy the Edge Function but keep scheduler inactive**

Deploy `ymq-notion-projector` to project `tbmoimbdhsrltvospwpu`. Use JWT verification according to the deployed wake-auth contract; do not disable authentication merely to simplify the demo.

- [ ] **Step 8: Human Security Gate — provision Notion integration token**

The exact secret name is `NOTION_YMQ_NATIVE1_TOKEN`. The value is never pasted into GitHub, Notion pages, logs, receipts, or chat-visible artifacts. Stop at `CONFIG_BLOCKED` until this secret is actually present in the Supabase Edge Function environment.

---

### Task 6: Add machine-owned properties to Native0 Notion objects and bind one explicit DEMO chain

**Files / external objects:**
- Modify Notion data source `Capital Questions` (`collection://89ea4be4-bbcf-4101-bb69-8721b3c10441`).
- Modify Notion data source `Research Projections` (`collection://ba1748d0-ed0e-4e7f-b6a8-3a265210a072`).
- Modify Notion data source `Reality Audits` (`collection://fe180284-ade7-4cee-98cd-f0fa27c40caf`).
- Modify Notion data source `Shadow & Settlements` (`collection://95a7de7c-1cb4-45a0-b887-9d3362c2cef2`).
- Modify Notion data source `Learning Deltas` (`collection://1f3c09c0-6041-4428-abb6-0c816ba31ad1`).
- DEMO Capital Question page: `3dd8e1aa-ace4-8121-a06e-dfe05b699035`.

**Interfaces:**
- Consumes: machine-owned properties from the spec.
- Produces: a stable projection target whose IDs are stored in `runtime.notion_projection_bindings`.

- [ ] **Step 1: Add machine-owned schema fields**

Capital Questions fields:

- `Machine Evidence Status` select: `PASS`, `LIMITED`, `BLOCKED`, `UNKNOWN`.
- `Machine Gate Status` select: `OPEN`, `PASS`, `BLOCKED`, `UNKNOWN`, `NO_GO`.
- `Machine Known As Of` date.
- `Machine Event ID` text.
- `Machine Source ID` text.
- `Machine Sync Status` select: `PENDING`, `SYNCED`, `RETRY`, `DEAD`, `BLOCKED`.
- `Machine Synced At` date.
- `Transition Suggestion` text.
- `Transition Reason` text.

Research Projections:

- `Runtime Projection ID` text.
- `Runtime Run ID` text.
- `Machine Evidence Status` select.
- `Machine Known As Of` date.
- `Machine Authority` select with only `RESEARCH` for Native1 writes.
- `Machine Event ID` text.
- `Machine Sync Status` select.
- `Source Receipt ID` text.

Reality Audits:

- `Runtime Gate Run ID` text.
- `Machine Gate Status` select.
- `Machine Event ID` text.
- `Machine Sync Status` select.

Shadow & Settlements:

- `Machine Shadow Eligibility` select: `BLOCKED`, `NOT_AUTHORIZED`.
- `Machine Event ID` text.
- `Machine Sync Status` select.

Learning Deltas:

- `Runtime Learning Delta ID` text.
- `Machine Effective After` date.
- `Machine Event ID` text.
- `Machine Sync Status` select.

- [ ] **Step 2: Fetch all five data sources after mutation**

Verify exact property names/types and that no existing human field was deleted or renamed.

- [ ] **Step 3: Create an ACTIVE binding for the DEMO Capital Question**

Insert into `runtime.notion_projection_bindings`:

- `runtime_object_type = 'CAPITAL_QUESTION_DEMO'`
- `runtime_object_id = 'CQ-1'`
- `notion_object_type = 'CAPITAL_QUESTION'`
- `notion_page_id = '3dd8e1aa-ace4-8121-a06e-dfe05b699035'`
- `notion_data_source_id = 'collection://89ea4be4-bbcf-4101-bb69-8721b3c10441'`
- `binding_status = 'ACTIVE'`

- [ ] **Step 4: Read back the binding**

Verify exactly one ACTIVE binding exists for `(CAPITAL_QUESTION_DEMO, CQ-1, CAPITAL_QUESTION)`.

---

### Task 7: Activate durable wake-up only after the secret gate is satisfied

**Files:**
- Create: `supabase/migrations/20260916_ymq_notion_native1_wake_schedule.sql`
- Extend: `tests/test_ymq_notion_native1_supabase_contract.py`

**Interfaces:**
- Consumes: deployed Edge Function and server-side wake secret.
- Produces: automatic polling of durable outbox with retry recovery.

- [ ] **Step 1: Write RED tests for scheduler migration**

Assert SQL contains:

- `create extension if not exists pg_net`;
- `create extension if not exists pg_cron`;
- use of existing installed `supabase_vault` rather than committing a secret;
- a server-side function `runtime.wake_ymq_notion_projector()`;
- a cron schedule no more frequent than once per minute;
- no Notion token literal and no service role key literal.

- [ ] **Step 2: Verify RED**

```bash
python -m unittest tests.test_ymq_notion_native1_supabase_contract -v
```

- [ ] **Step 3: Implement wake-token bootstrap and wake function**

The migration may create a random wake token in Vault only when absent, using server-side randomness. `runtime.wake_ymq_notion_projector()` reads the token through Vault server-side, calls:

`https://tbmoimbdhsrltvospwpu.supabase.co/functions/v1/ymq-notion-projector`

through `net.http_post`, sends only `x-ymq-wake-token`, and uses an empty JSON body. It must not expose the token through a public function.

- [ ] **Step 4: Schedule once-per-minute wake-up**

Create a named cron job `ymq_notion_native1_projector` that calls `runtime.wake_ymq_notion_projector()` every minute. The Edge Function itself claims at most one event per invocation; future throughput scaling is outside Native1.

- [ ] **Step 5: Run tests and commit**

```bash
python -m unittest tests.test_ymq_notion_native1_supabase_contract -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

Commit:

```bash
git add supabase/migrations/20260916_ymq_notion_native1_wake_schedule.sql tests/test_ymq_notion_native1_supabase_contract.py
git commit -m "feat: add durable Native1 projection wake path"
```

- [ ] **Step 6: Apply the wake migration only after the Notion token is confirmed present**

After apply, verify `pg_cron` job exists, `pg_net` is installed, and no secret value is visible in migration/source/log receipts.

---

### Task 8: Run E2E DEMO binding and adversarial replay

**Files / runtime:**
- Use DEMO Capital Question `CQ-1` / Notion page `3dd8e1aa-ace4-8121-a06e-dfe05b699035` only.
- No live Capital/Execution/Shadow object.

**Interfaces:**
- Consumes: outbox + Edge adapter + Notion machine properties.
- Produces: physical Supabase delivery receipts and Notion readback proving safe state movement.

- [ ] **Step 1: Set DEMO precondition**

Set the DEMO Capital Question to `Journey Stage = 04 TRANSMISSION`, `Gate Status = OPEN`, and keep it visibly labeled `DEMO` in title/body. This is a test state, not a scientific conclusion.

- [ ] **Step 2: Emit a synthetic `RESEARCH_PROJECTION_CREATED` event**

Use explicit `metadata.mode = "REPLAY"`; human context must point to the DEMO page; evidence status `LIMITED`; non-empty defeat condition. Do not mutate the existing G1 Founder Intelligence projection row.

- [ ] **Step 3: Verify automatic wake and one-step advance**

Expected Notion readback:

- `Journey Stage = 05 AUDIT`
- `Gate Status = OPEN`
- `Machine Evidence Status = LIMITED`
- exact `Machine Event ID`
- `Machine Sync Status = SYNCED`
- no change to DEMO thesis/body.

Expected Supabase:

- event `ACKED`;
- one delivery row with request/response hashes;
- no secrets in receipt.

- [ ] **Step 4: Replay the identical event**

Expected: unique idempotency key prevents a second business event or adapter produces an ACKed no-op; Notion does not receive duplicate semantic mutation.

- [ ] **Step 5: Inject a stale event**

Create a replay event with `known_as_of` older than the current machine projection. Expected: `STALE_NOOP`, current Notion machine state unchanged.

- [ ] **Step 6: Inject `UNKNOWN` evidence**

Expected fail-closed Notion readback:

- `Journey Stage = 02 EVIDENCE`
- `Machine Gate Status = UNKNOWN`
- `Block Reason` / `Transition Reason` explains `UNKNOWN_DENY`.

- [ ] **Step 7: Attempt `AUDIT -> SHADOW`**

Expected: `Journey Stage` remains `05 AUDIT` if reset for this case; `Machine Shadow Eligibility = BLOCKED/NOT_AUTHORIZED`; reason `SHADOW_NOT_AUTHORIZED`.

- [ ] **Step 8: Simulate retry**

Use a controlled bad Notion target or disabled delivery endpoint on a DEMO event to produce `RETRY`; verify `available_after` is in the future and a later wake attempts it again. Restore valid target and verify eventual ACK. Do not make production objects the retry target.

- [ ] **Step 9: Read back all receipts**

Capture event IDs, delivery IDs, request/response hashes, retry attempt counts, final statuses, and Notion page readback for the qualification receipt.

---

### Task 9: Wire Native1 into protected CI and write qualification receipt

**Files:**
- Modify: `.github/workflows/ci.yml`
- Create: `docs/architecture/ymq_notion_native1/YMQ-NOTION-NATIVE1-MACHINE-QUALIFICATION-RECEIPT-v0.1.md`

**Interfaces:**
- Consumes: Tasks 1-8 tests/readbacks.
- Produces: machine qualification status only; no merge/Capital/Execution/Shadow authority.

- [ ] **Step 1: Modify the existing `contracts` job without renaming it**

Add immediately after `python scripts/validate_ymq_os0_g1.py`:

```yaml
      - run: python scripts/validate_ymq_notion_native1.py
```

Do not create or reference `.github/workflows/repository-gates.yml`; the real protected workflow file is `.github/workflows/ci.yml` and its workflow name is `repository-gates`.

- [ ] **Step 2: Run exact-head tests through PR CI**

Required GREEN:

- `contracts`
- `governance`
- full `python -m unittest discover -s tests -p 'test_*.py' -v` inside contracts
- `scripts/leak_guard.py`

- [ ] **Step 3: Run Supabase advisors after all DDL is applied**

Record security and performance advisor output. A Native1-critical RLS/policy/foreign-key/index issue blocks qualification.

- [ ] **Step 4: Compare branch to `main`**

Verify only authorized Native1 scope plus the approved spec/plan changed. No unrelated YMQ3/YMQ4 scientific files, Capital execution files, or production secrets.

- [ ] **Step 5: Write qualification receipt**

Receipt must include:

- exact Git head SHA;
- PR number;
- Supabase project ref;
- migration names and physical table/RLS/index readback;
- Edge Function version/deploy state;
- wake scheduler proof;
- DEMO Notion page ID;
- event IDs/delivery IDs from success, duplicate, stale, UNKNOWN, Shadow-denial, and retry cases;
- exact CI run IDs/status;
- advisor results;
- explicit statement that Notion is projection-only;
- explicit `CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED / SHADOW_NOT_AUTHORIZED`.

Allowed final status only when every proof is physical:

`YMQ_NOTION_NATIVE1_MACHINE_QUALIFIED / NOTION_PROJECTION_ONLY / CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED / SHADOW_NOT_AUTHORIZED`

If Notion secret provisioning or any E2E proof is missing, use:

`YMQ_NOTION_NATIVE1_IMPLEMENTED / QUALIFICATION_BLOCKED_<REASON>`

- [ ] **Step 6: Commit final receipt and CI wiring**

```bash
git add .github/workflows/ci.yml docs/architecture/ymq_notion_native1/YMQ-NOTION-NATIVE1-MACHINE-QUALIFICATION-RECEIPT-v0.1.md
git commit -m "docs: qualify YMQ Notion Native1 machine reality binding"
```

---

## Plan Self-Review Result

### Spec coverage

- Transactional outbox: Task 4.
- Runtime↔Notion binding: Tasks 4 and 6.
- Delivery receipts/idempotency: Tasks 4, 5, 8.
- Fail-closed regression: Tasks 2, 3, 8.
- One-step forward transition: Tasks 2, 3, 8.
- Shadow deny-by-default: Tasks 2, 5, 8.
- Machine-owned Notion fields: Task 6.
- Durable wake + retry: Tasks 5, 7, 8.
- No secret literals: Tasks 5, 7, 9 plus governance leak guard.
- Exact-head CI/advisors/receipt: Task 9.
- No silent historical backfill: Tasks 4 and 8 use explicit REPLAY metadata.

### Placeholder scan

No `TBD`, `TODO`, “implement later”, or undefined production behavior remains. The only deliberate external gate is the named human security action to provision `NOTION_YMQ_NATIVE1_TOKEN`; qualification is explicitly blocked until physically satisfied.

### Type / naming consistency

- Stages are exactly `01 DISCOVER` through `07 LEARNING`; fail-closed target is `02 EVIDENCE`; automatic research advance is only `04 TRANSMISSION -> 05 AUDIT`.
- Event types match the Written Spec closed set.
- Supabase object names match the Written Spec.
- Notion data-source IDs and DEMO page ID match Native0 readback.
- CI file is the physically verified `.github/workflows/ci.yml`, not the stale G1 plan filename.

## Completion Condition

The plan is complete when repository implementation, Supabase physical readback, Notion DEMO readback, durable wake/retry, adversarial replay, exact-head protected CI, and qualification receipt all agree. A successful demo does not create Capital, Execution, or Shadow authority and does not upgrade Notion into a source of truth.
