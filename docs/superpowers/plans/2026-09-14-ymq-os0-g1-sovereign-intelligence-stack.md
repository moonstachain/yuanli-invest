# YMQ-OS0-G1 Sovereign Intelligence Stack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing YMQ/YIOS estate into a physically runnable five-plane stack across GitHub, Supabase, Hugging Face, Notion, and a provider-replaceable Agent Runtime without creating a second source of truth or leaking Research Authority into Capital/Execution Authority.

**Architecture:** GitHub remains Law Plane; `yuanli-invest-runtime` remains Reality Ledger and extends the existing `evidence` / `pit` / `runtime` schemas rather than forking them; Hugging Face is replaceable blind compute only; Notion is projection/human experience only; Agent Runtime is a protocol-driven gateway whose outputs remain research projections until separate authority is granted. Cross-plane identities and receipts are bound through immutable run IDs, git SHA, evidence refs, and explicit non-authorizations.

**Tech Stack:** GitHub Actions, Python 3, JSON/YAML contracts, PostgreSQL 17 / Supabase, Deno Edge Functions, Hugging Face Jobs, Notion MCP, JSON Schema.

**Spec:** `docs/superpowers/specs/2026-09-13-ymq-os0-g0-macro-quant-constitution-design.md` and accepted YMQ3-R0/R0A lineage.

## Global Constraints

- Reuse the existing `moonstachain/yuanli-invest` Canon; do not create a competing repository as Law Plane.
- Reuse `yuanli-invest-runtime` Supabase and existing `evidence`, `pit`, `runtime` lineage; migrations must be additive and backward compatible.
- `Reality > Belief`; `ClaimAuthority <= EvidenceAuthority`; `UNKNOWN = DENY`.
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`.
- `ResearchPass != CapitalPass` and `PHYSICAL_PASS` may coexist with `SCIENTIFIC_NO_GO`.
- Hugging Face is provider-replaceable compute and receives no Canon, Capital, or Execution authority.
- Notion is a Human Experience projection and may not become the Reality source of truth.
- Agent Runtime may read admitted evidence and write research receipts, but may not issue portfolio sizing, broker orders, or real-capital actions.
- No secret literals in repository artifacts.
- Every production behavior change follows RED -> GREEN -> review -> fresh verification.

---

### Task 1: Cross-plane machine contract and fail-closed validator

**Files:**
- Create: `config/ymq_os0/g1_sovereign_stack.v0.1.json`
- Create: `scripts/validate_ymq_os0_g1.py`
- Create: `tests/test_ymq_os0_g1.py`

**Interfaces:**
- Consumes: existing YMQ-OS0 G0 authority model.
- Produces: `validate_contract(path)`, `validate_runtime_request(payload)`, `validate_projection_manifest(payload)`.

- [ ] Write tests first for five plane roles, provider replaceability, research/capital/execution separation, `UNKNOWN=DENY`, and cross-plane run identity.
- [ ] Run tests and confirm expected failure because G1 implementation does not exist.
- [ ] Implement the minimal contract and validator.
- [ ] Run targeted and full tests to GREEN.
- [ ] Commit.

### Task 2: Reality Ledger additive migration

**Files:**
- Create: `supabase/migrations/20260914_ymq_os0_g1_sovereign_stack.sql`
- Test: `tests/test_ymq_os0_g1_supabase_contract.py`

**Interfaces:**
- Consumes: `evidence.sources`, `evidence.source_snapshots`, `pit.observations`, `runtime.reality_gate_runs`.
- Produces: `runtime.agent_runs`, `runtime.research_projections`, `runtime.learning_deltas`, `evidence.claim_receipts`, `runtime.read_agent_context(...)`.

- [ ] Write failing structural contract tests against expected DDL invariants.
- [ ] Verify RED.
- [ ] Add non-destructive migration with RLS, immutable evidence references, authority columns, and forward-only learning semantics.
- [ ] Verify repository tests GREEN.
- [ ] Apply the same migration to Supabase `yuanli-invest-runtime` only after repository contract is GREEN.
- [ ] Physically read back tables/policies/functions and run security/performance advisors.

### Task 3: Agent Runtime gateway contract

**Files:**
- Create: `runtime/ymq_gateway/contracts.py`
- Create: `runtime/ymq_gateway/context_compiler.py`
- Create: `runtime/ymq_gateway/router.py`
- Create: `tests/test_ymq_gateway.py`

**Interfaces:**
- Consumes: admitted `SourceSnapshot`, `ObservationPIT`, G1 runtime tables.
- Produces: `CompiledContext`, `AgentRequest`, `AgentResponse`, deny reasons and research receipt IDs.

- [ ] RED tests for PIT filtering, evidence authority ceiling, minimum-context selection, provider non-authority, and forbidden capital/execution intents.
- [ ] Verify RED.
- [ ] Implement minimal deterministic compiler/router; no LLM call is required for qualification.
- [ ] Verify GREEN and full regression.

### Task 4: Hugging Face Blind Lab reality proof

**Files:**
- Create: `config/ymq_os0/hf_blind_lab.v0.1.json`
- Create: `docs/architecture/ymq_os0/YMQ-OS0-G1-HF-BLIND-LAB-RECEIPT-v0.1.md`

**Interfaces:**
- Consumes: a synthetic secret-free G1 benchmark fixture.
- Produces: remote compute receipt: image/runtime, command hash, result hash, provider status.

- [ ] Freeze a secret-free benchmark fixture and expected hash locally in GitHub.
- [ ] Run a Hugging Face CPU Job that validates the fixture and emits a deterministic receipt.
- [ ] Read back logs/results.
- [ ] Record exact job ID and hashes; do not claim HF Dataset/Repo write authority unless physically proven.

### Task 5: Notion Founder Intelligence projection

**Files:**
- Create: `config/ymq_os0/notion_projection_manifest.v0.1.json`
- Create: `docs/architecture/ymq_os0/YMQ-OS0-G1-NOTION-PROJECTION-RECEIPT-v0.1.md`

**Interfaces:**
- Consumes: GitHub law references and Supabase runtime status summaries only.
- Produces: one Notion YMQ Founder Intelligence page under the existing `原力投研` portal, with navigation to Macro Reality, Evidence Gate, Reality Audit, Shadow Runtime, Capital Intelligence, Learning/Review.

- [ ] Create projection-manifest tests first; forbid Notion as canonical evidence store or authority grantor.
- [ ] Verify RED then implement manifest.
- [ ] Create/update the Notion page under the existing Yuanli Portal hierarchy.
- [ ] Read back the page and record page ID/URL in the receipt.

### Task 6: Cross-plane qualification and CI

**Files:**
- Modify: `.github/workflows/repository-gates.yml`
- Create: `docs/architecture/ymq_os0/YMQ-OS0-G1-MACHINE-QUALIFICATION-RECEIPT-v0.1.md`

**Interfaces:**
- Consumes: Tasks 1-5 receipts and validators.
- Produces: machine qualification status only; no merge/capital/execution authority.

- [ ] Add RED test proving repository-gates currently do not run G1 validator.
- [ ] Wire `python scripts/validate_ymq_os0_g1.py` and G1 unittest discovery into existing protected `contracts` job without renaming protected checks.
- [ ] Run fresh exact-head CI.
- [ ] Compare branch to main and verify only authorized scope changed.
- [ ] Write qualification receipt with exact Git SHA, Supabase readback facts, HF job ID, Notion page ID, CI run, and explicit non-authorizations.

## Completion Condition

G1 is complete only when all repository tests and protected checks are green, Supabase readback proves the additive runtime objects exist with security controls, HF remote compute has a deterministic secret-free receipt, Notion projection physically exists and is read back, and Agent Runtime contract tests deny capital/execution intents. Final allowed status is `YMQ_OS0_G1_MACHINE_QUALIFIED / CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED`.