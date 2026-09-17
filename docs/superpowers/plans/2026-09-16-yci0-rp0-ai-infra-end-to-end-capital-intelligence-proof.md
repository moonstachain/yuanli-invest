# YCI0-RP0 AI Infra End-to-End Capital Intelligence Proof Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one end-to-end, research-only AI-Infra capital-intelligence loop from PIT-qualified Reality through Brain Context, YMQ compilation, Notion Human Work, Forward Shadow, Settlement, and reusable LearningDelta.

**Architecture:** Reuse the existing YMQ-OS0-G1 Law/Reality/Blind-Lab stack and the accepted Native1 semantics. Add a narrow RP0 contract, adapters, compilers, and receipts around one Capital Question. Keep source truth in Supabase, law in GitHub, contextual memory in Yuanli Brain, human state in Notion, and all Capital/Execution authority with the Human Principal.

**Tech Stack:** Python 3, JSON contracts, Supabase/Postgres, existing `runtime/ymq_gateway`, Wind MCP/adapter boundary, Notion Native0/1 Human Objects, Hugging Face blind evaluation, GitHub Actions CI.

**Spec:** `docs/superpowers/specs/2026-09-16-yci0-rp0-ai-infra-end-to-end-capital-intelligence-proof-design.md`

## Global Constraints

- `Reality > Belief`.
- `ClaimAuthority <= EvidenceAuthority`.
- `UNKNOWN = DENY`.
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`.
- `ResearchPass != CapitalPass`.
- Wind structured MCP = Sensor/Evidence input only.
- Wind Alice = authored knowledge candidate unless independently tied to first-party evidence.
- Supabase = machine Reality/Evidence/runtime ledger.
- Yuanli Brain = Memory/Context/Capability Router, not final investment-answer authority.
- YMQ = Research Decision Compiler.
- Notion = Human Intelligence Workbench, not machine truth.
- HF = Blind Lab only.
- No broker action, portfolio sizing automation, real-capital movement, new Capital Authority, or Execution Authority.
- Replay must respect PIT and `known_as_of`; `recorded_at` cannot substitute for `known_as_of`.
- Automatic forward movement is at most one Human Journey Stage; UNKNOWN/BLOCKED may fail closed to `02 EVIDENCE`.
- A genuine final `YCI0_RP0_END_TO_END_PROVEN` status is forbidden until future Reality settlement and Learning reuse physically occur.

---

### Task 1: Freeze RP0 contract, question object, and metric registry

**Files:**
- Create: `config/yci0_rp0/ai_infra_question.v0.1.json`
- Create: `config/yci0_rp0/ai_infra_reality_contract.v0.1.json`
- Create: `config/yci0_rp0/wind_metric_registry.v0.1.json`
- Create: `scripts/validate_yci0_rp0.py`
- Create: `tests/test_yci0_rp0_contract.py`

**Interfaces:**
- Consumes: accepted RP0 spec.
- Produces: `validate_contract(question, reality_contract, metric_registry) -> list[str]` plus frozen IDs/constants consumed by all later tasks.

- [ ] Write RED tests asserting question id `YCI0-RP0-CQ-001`, theme `AI_INFRA`, authority `RESEARCH`, non-empty prior belief/defeat condition, and zero Capital/Execution authority.
- [ ] Add tests asserting required metric families include US 10Y nominal, US 10Y real yield, DXY/USD proxy, hyperscaler capex/guidance, NVDA data-center revenue, compute supply-normalization proxy, networking proxy, power-equipment proxy, power-availability proxy, market price, and valuation.
- [ ] Add tests asserting every metric definition declares `source_type`, `pit_policy`, `required_timestamps`, `admission_rule`, and `fallback = UNKNOWN`.
- [ ] Run `python -m unittest tests.test_yci0_rp0_contract -v` and confirm RED.
- [ ] Implement the three JSON contracts and validator with exact closed-set authority/state values from the spec.
- [ ] Run targeted tests, `python scripts/validate_yci0_rp0.py`, then full `python -m unittest discover -s tests -p 'test_*.py' -v`.
- [ ] Commit: `feat: freeze YCI0 RP0 contracts and AI Infra metric registry`.

### Task 2: Implement PIT-qualified RealityEvidence normalization

**Files:**
- Create: `runtime/yci0_rp0/__init__.py`
- Create: `runtime/yci0_rp0/contracts.py`
- Create: `runtime/yci0_rp0/evidence_adapter.py`
- Create: `tests/test_yci0_rp0_pit.py`

**Interfaces:**
- Consumes: raw Wind/source observations + Task 1 metric registry.
- Produces: `normalize_observation(raw: dict, metric_spec: dict) -> RealityEvidence` and `pit_eligible(evidence) -> bool`.

- [ ] RED-test that a row lacking `known_as_of` is never PIT-qualified.
- [ ] RED-test that Alice-authored output defaults to `AUTHORED_KNOWLEDGE_CANDIDATE`, not evidence PASS.
- [ ] RED-test current descriptive rows without vintage/release semantics remain usable only as `CURRENT_CONTEXT_ONLY`.
- [ ] RED-test content hash and source locator are deterministic.
- [ ] Implement dataclasses/enums for `RealityEvidence`, evidence status, source type, and PIT admission reason.
- [ ] Implement normalization with `observed_at`, `released_at`, `known_as_of`, `retrieved_at`, `revised_at`, `vintage`, `content_hash`, `authority`.
- [ ] Run targeted/full tests and commit: `feat: add PIT-qualified RP0 evidence normalization`.

### Task 3: Add Supabase RP0 research-object and evidence bindings

**Files:**
- Create: `supabase/migrations/20260916_yci0_rp0_research_loop.sql`
- Create: `tests/test_yci0_rp0_supabase_contract.py`

**Interfaces:**
- Consumes: existing `evidence.sources`, `evidence.source_snapshots`, `evidence.claim_receipts`, `pit.observations`, `runtime.agent_runs`, `runtime.research_projections`, `runtime.reality_gate_runs`, `runtime.learning_deltas`.
- Produces: additive `runtime.capital_questions`, `runtime.context_packs`, `runtime.ai_infra_state_cards`, `runtime.shadow_settlements` only if equivalent tables do not already exist; service-role-only insert/read RPCs; no duplicate evidence ledger.

- [ ] Write structural RED tests for additive tables, FK lineage to existing evidence/run objects, RLS, `authority='RESEARCH'` checks, immutable T0 hashes, and absence of anon/authenticated write grants.
- [ ] Implement migration with indexes on question/stage, known_as_of, source IDs, and review dates.
- [ ] Add `SECURITY DEFINER` service-role-only RPCs for inserting normalized RP0 evidence bindings and frozen shadow records; revoke from public/anon/authenticated.
- [ ] Add immutability trigger for T0 shadow identity/hash fields.
- [ ] Run targeted/full tests and `scripts/leak_guard.py`.
- [ ] Commit before production apply: `feat: add RP0 research-loop persistence`.
- [ ] Apply only to `yuanli-invest-runtime`, then physically read back tables, RLS, policies, indexes, routines, and advisor output.

### Task 4: Build bounded Yuanli Brain Context Pack adapter

**Files:**
- Create: `runtime/yci0_rp0/context_adapter.py`
- Create: `config/yci0_rp0/context_pack_policy.v0.1.json`
- Create: `tests/test_yci0_rp0_context.py`
- Reuse: `runtime/ymq_gateway/context_compiler.py`, `runtime/ymq_gateway/router.py`

**Interfaces:**
- Consumes: CapitalQuestion + bounded Brain retrieval results.
- Produces: `ContextPack` containing historical analogues, Yuanli patterns, prior judgments, hard negatives, prior LearningDeltas, capability recommendations, freshness/provenance summary, and `context_hash`.

- [ ] RED-test that full-vault/unbounded payloads are rejected.
- [ ] RED-test that every context item carries provenance and freshness state.
- [ ] RED-test stale/unproven context cannot upgrade evidence or decision authority.
- [ ] RED-test output has no buy/sell/capital authorization field.
- [ ] Implement a retrieval budget (max items per category, max total items) in policy JSON and deterministic ContextPack hashing.
- [ ] Reuse existing gateway routing rather than cloning it; add only an RP0 adapter that converts routed results into ContextPack.
- [ ] Run targeted/full tests and commit: `feat: add bounded RP0 Brain context pack`.

### Task 5: Implement AI-Infra Reality State Compiler

**Files:**
- Create: `runtime/yci0_rp0/state_compiler.py`
- Create: `tests/test_yci0_rp0_state_compiler.py`

**Interfaces:**
- Consumes: PIT-admitted `RealityEvidence[]`.
- Produces: `compile_reality_state(evidence, as_of) -> RealityStateCard` across financing regime, hyperscaler capex, compute, networking, power/grid, and capital-efficiency dimensions.

- [ ] RED-test Level / Δ / Δ² output for a synthetic three-period series.
- [ ] RED-test insufficient history returns `UNKNOWN` for Δ/Δ² rather than inferred values.
- [ ] RED-test every non-UNKNOWN state retains evidence refs and `known_as_of`.
- [ ] Implement deterministic state enums `ACCELERATING|STABLE|DECELERATING|MIXED|UNKNOWN` and per-dimension confidence.
- [ ] Implement aggregation rule that never upgrades a dimension when required evidence is BLOCKED/UNKNOWN.
- [ ] Run targeted/full tests and commit: `feat: compile RP0 AI Infra reality state`.

### Task 6: Implement Narrative × Transmission and Price × Payoff research compilers

**Files:**
- Create: `runtime/yci0_rp0/narrative_transmission.py`
- Create: `runtime/yci0_rp0/price_payoff.py`
- Create: `runtime/yci0_rp0/projection_compiler.py`
- Create: `tests/test_yci0_rp0_projection_compiler.py`

**Interfaces:**
- Consumes: RealityStateCard + ContextPack + admitted narrative/market evidence.
- Produces: `NarrativeTransmissionCard`, `PricePayoffCard`, then `ResearchProjection`.

- [ ] RED-test Narrative Stage accepts only `D0|D1|D2|D3|D4|UNKNOWN` and always carries `scientific_status=LIMITED`.
- [ ] RED-test Transmission requires a primary chain, current bottleneck, next-bottleneck hypothesis, common-shock branch, and hard-negative branch.
- [ ] RED-test Price/Payoff always carries `scientific_status=RESEARCH`, Bull/Base/Bear/Hard-Negative, defeat condition, survival cost, and S/C/R/X research mapping.
- [ ] RED-test empty defeat condition blocks creation of an audit-eligible ResearchProjection.
- [ ] Implement pure compilers with no network access and no trade/capital fields.
- [ ] Implement `compile_projection(question, reality, context, narrative, payoff) -> ResearchProjection`.
- [ ] Run targeted/full tests and commit: `feat: compile RP0 research projection`.

### Task 7: Bind RP0 to Notion Human Work via Native1 semantics

**Files:**
- Create: `runtime/yci0_rp0/human_projection.py`
- Create: `tests/test_yci0_rp0_human_projection.py`
- Reuse when qualified: Native1 outbox/transition/Notion projection interfaces.
- External objects: Native0 `Capital Questions`, `Research Projections`, `Reality Audits`.

**Interfaces:**
- Consumes: ResearchProjection + machine Reality event + current Human Journey Stage.
- Produces: whitelisted Notion patch and immutable MachineReceipt; never overwrites human-authored thesis/body.

- [ ] RED-test `UNKNOWN/BLOCKED` may regress to `02 EVIDENCE`.
- [ ] RED-test automatic forward movement is at most one stage.
- [ ] RED-test no machine path grants `06 SHADOW`, Capital, or Execution authority.
- [ ] RED-test stale event produces no semantic overwrite.
- [ ] Implement adapter against Native1 contracts if physically qualified; otherwise create an RP0 compatibility adapter that preserves the same accepted semantics without claiming Native1 production qualification.
- [ ] Create/bind only `YCI0-RP0-CQ-001` in Notion, visibly labeled as flagship research proof.
- [ ] Read back exact fields after mutation and record receipt IDs.
- [ ] Run targeted/full tests and commit: `feat: bind RP0 machine reality to human work`.

### Task 8: Freeze Reality Audit and Forward Shadow T0 record

**Files:**
- Create: `runtime/yci0_rp0/audit.py`
- Create: `runtime/yci0_rp0/shadow.py`
- Create: `tests/test_yci0_rp0_shadow.py`
- Create: `docs/architecture/yci0_rp0/receipts/YCI0-RP0-SHADOW-GENESIS-RECEIPT.md`

**Interfaces:**
- Consumes: ResearchProjection + Human Audit.
- Produces: RealityAudit and immutable Shadow T0 bundle with T+30/T+90/T+180 schedule.

- [ ] RED-test Audit requires hard negative, evidence gap, common shock, survival risk, defeat condition, and verdict.
- [ ] RED-test Shadow creation is denied when Audit is not PASS or shadow authority is absent.
- [ ] RED-test T0 evidence/context/projection hashes cannot be mutated after creation.
- [ ] Implement `build_reality_audit(...)` and `freeze_shadow(...)` with zero-capital/zero-execution assertions.
- [ ] Persist one RP0 shadow record only after the existing shadow/replay law permits it; otherwise write `SHADOW_PREREGISTRATION_BLOCKED` receipt rather than bypassing the gate.
- [ ] Schedule review timestamps; do not create fake settlements before calendar time.
- [ ] Run targeted/full tests and commit: `feat: preregister RP0 forward shadow`.

### Task 9: Implement Settlement and LearningDelta reuse path

**Files:**
- Create: `runtime/yci0_rp0/settlement.py`
- Create: `tests/test_yci0_rp0_settlement.py`
- Create: `docs/architecture/yci0_rp0/receipts/YCI0-RP0-SETTLEMENT-STATUS.md`

**Interfaces:**
- Consumes: frozen Shadow + later Reality observations.
- Produces: settlement separating process/outcome verdicts and `LearningDelta` eligible for Brain reuse after Human Review.

- [ ] RED-test future review dates cannot settle early and return `SETTLEMENT_PENDING_REALITY`.
- [ ] RED-test process verdict and outcome verdict remain independent.
- [ ] RED-test LearningDelta requires Old Rule, observed update/failure, failure layer, New Rule, domain, boundary conditions, evidence refs, effective_after, confidence, version.
- [ ] Implement settlement logic and deterministic LearningDelta serialization.
- [ ] Implement Brain reuse query envelope that surfaces LearningDelta with provenance/scope but never auto-promotes it to Canon.
- [ ] For current execution, produce a rehearsal only if real T+30/T+90/T+180 has not elapsed; label it `REPLAY/REHEARSAL`, never final proof.
- [ ] Run targeted/full tests and commit: `feat: add RP0 settlement and learning reuse path`.

### Task 10: Build HF blind ablation and final qualification gates

**Files:**
- Create: `config/yci0_rp0/blind_benchmark.v0.1.json`
- Create: `tests/test_yci0_rp0_benchmark_contract.py`
- Create: `docs/architecture/yci0_rp0/benchmark/README.md`
- Create: `docs/architecture/yci0_rp0/YCI0-RP0-QUALIFICATION-RECEIPT-v0.1.md`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: Tasks 1–9 outputs.
- Produces: blind comparison A=no Brain Context, B=Brain Context, optional C=Brain+structured YMQ compiler; final status receipt.

- [ ] RED-test benchmark freezes identical question/PIT evidence across arms and scores evidence traceability, causal compression, hard-negative coverage, bottleneck migration, trend-vs-payoff separation, defeat-condition quality, uncertainty honesty, and authority discipline.
- [ ] Implement benchmark config and result schema; no score may imply market-prediction superiority from one case.
- [ ] Run HF/replaceable blind job only when the evidence/context bundles are physically available; otherwise status `BENCHMARK_READY_NOT_RUN`.
- [ ] Add `python scripts/validate_yci0_rp0.py` and all RP0 tests to existing protected `contracts`/governance CI without renaming the workflow.
- [ ] Run exact-head full unittest suite, leak guard, governance checks, Supabase advisors, and compare branch scope to main.
- [ ] Write qualification receipt using only physically observed gates. Allowed current terminal states include `SHADOW_PREREGISTERED` and `SETTLEMENT_PENDING_REALITY`; forbid `END_TO_END_PROVEN` until future settlement + Brain reuse are real.
- [ ] Commit: `chore: qualify YCI0 RP0 research-only reality proof`.

---

## Execution Order and Human Gates

1. Tasks 1–2 are pure local contracts and normalization.
2. Task 3 may prepare migration locally; applying to production Supabase is an external side effect and requires the accepted RP0 implementation authority plus fresh readback.
3. Tasks 4–6 remain research-only and may proceed without Notion mutation.
4. Task 7 mutates the single RP0 Notion demo/flagship object only; no broad workspace rewrite.
5. Task 8 may preregister Shadow only under existing shadow/replay authority. Missing authority must fail closed.
6. Task 9 cannot claim real settlement before calendar time.
7. Task 10 cannot claim end-to-end proof before real settlement and Learning reuse.

## Final Fresh Verification

Before any completion claim run:

```bash
python scripts/validate_yci0_rp0.py
python -m unittest discover -s tests -p 'test_yci0_rp0*.py' -v
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/leak_guard.py
```

Then physically read back any changed Supabase/Notion objects and verify exact-head CI. Evidence before assertion.