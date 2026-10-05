# QXM-F Financial Mechanics Capability Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the Qin Xiaoming Financial Mechanics research line by giving every QXM object an explicit governed disposition, reality-testing the priority capabilities against preregistered baselines, settling capability authority, and canonizing the reusable External Research Compiler.

**Architecture:** QXM-F is one terminal program with six sequential gates: G0 closes QXM2; G1 performs selective Registry admission; G2 preregisters hypotheses and formalizes benchmarks; G3 creates provider mappings, implementation objects, and PIT/held-out reality proofs; G4 settles each capability and optionally builds `FM-GOLD-01`; G5 freezes the External Research Compiler and archives QXM as `ERC-GOLD-CASE-001`. Each gate uses its own branch/PR, machine qualification, Human Gate where epistemic judgment is required, and a separate merge authority. `Receipt = Ledger; State = Projection` remains binding.

**Tech Stack:** Python 3.12, JSON Schema Draft 2020-12, `jsonschema==4.25.1`, `unittest`, Git/GitHub, GitHub Actions `repository-gates`, provider-neutral JSON contracts, and licensed Wind execution through an external authorized runtime with receipt-only return to GitHub.

**Spec:** `docs/superpowers/specs/2026-08-21-qxm-f-financial-mechanics-capability-closure-design.md`

**Written spec approval:** `ACCEPT_QXM_F_WRITTEN_DESIGN_SPEC`

## Global Constraints

- QXM-F start authority does not imply QXM2 merge authority. G0 requires the literal token `AUTHORIZE_QXM2_MERGE`.
- `Claim Authority <= Evidence Authority`.
- `Person is provenance; capability is the durable runtime asset`.
- `Receipt = Ledger; State = Projection`.
- Theory support is not hypothesis support; hypothesis support is not capability qualification.
- Benchmark specification is not benchmark PASS; benchmark PASS is not capability promotion.
- Registry admission, hypothesis preregistration, benchmark creation, benchmark execution, capability promotion, production runtime, and trading authority are independent authorities.
- R1 ID rules are immutable. Breaking semantic changes require a new ID or explicit major version.
- R1 lifecycle order remains binding: `concept -> specified -> implemented -> replicated -> benchmark_passed -> shadow_qualified -> canon -> deprecated`. QXM-F may not skip a maturity state without a migration receipt.
- The six QXM identities remain the only program subjects: Fundamental Driver Decomposition; Three-Statement Integrity & Cash Conversion; Credit & Balance-Sheet Transmission profile; Opportunity-Cost / Discount-Rate Bridge profile; Stress Exit Liquidity; Return Source Attribution.
- Priority is `3 + 2 + 1`: Tier 1 = CAP-P-003, CAP-P-004, CAP-CROSS-001; Tier 2 = CAP-R-01 credit profile and CAP-S-004; Tier 3 = CAP-V-01 discount-rate profile.
- Discount-Rate Bridge remains `interpretation_only` unless a preregistered predictive benchmark later earns stronger authority.
- Return Source Attribution is tested as a learning/attribution capability using held-out episode reconstruction and thesis-fidelity, not forced into a forecasting task.
- Every executed complex capability must face a simpler baseline under the same PIT/held-out rules.
- `No stable incremental information over a simpler baseline -> no predictive Capability promotion`.
- QXM-F does not target 6/6 promotion. `REJECT_OR_REDESIGN`, `INTERPRETATION_ONLY`, `KEEP_SHADOW`, and `DEFER_DATA_INSUFFICIENT` are legitimate research outcomes.
- Provider-specific fields belong in `ProviderAdapter`; canonical economic fields remain provider-neutral.
- No licensed raw Wind dataset is committed to GitHub. GitHub stores contracts, hashes, metadata, metrics, receipts, and failure evidence only.
- No target price, buy/sell/hold instruction, recommended weight, position size, broker action, or live execution is authorized anywhere in QXM-F.
- In an API-only harness where local `git worktree` cannot reach GitHub, an isolated GitHub branch plus exact-head PR CI may substitute for local worktree isolation. Never write directly to `main`.

## Existing Repository Contracts This Plan Must Reuse

- Theory schema: `packages/contracts/schemas/theory-object.schema.json`.
- Hypothesis schema: `packages/contracts/schemas/hypothesis-object.schema.json`.
- Factor schema: `packages/contracts/schemas/factor-object.schema.json`.
- Algorithm schema: `packages/contracts/schemas/algorithm-object.schema.json`.
- Benchmark schema: `packages/contracts/schemas/benchmark-object.schema.json`.
- Provider schema: `packages/contracts/schemas/provider-adapter.schema.json`.
- Capability schema: `packages/contracts/schemas/research-capability.schema.json`.
- Skill schema: `packages/contracts/schemas/skill-contract.schema.json`.
- Registry topology and counts: `registry/registry-index.json` plus each `registry/*/_index.json`.
- Current Registry pack-file convention: each registry may add a versioned pack whose `objects[]` entries independently validate against the corresponding single-object schema.

## Program State Machine

```text
G0_WAITING_QXM2_MERGE_AUTHORITY
  -> G0_QXM2_ACCEPTED_MERGED
  -> G1_SELECTIVE_ADMISSION_READY_FOR_HUMAN_REVIEW
  -> G1_ADMITTED_MERGED
  -> G2_PREREGISTRATION_READY_FOR_HUMAN_REVIEW
  -> G2_PREREGISTERED_MERGED
  -> G3_PROVIDER_PROTOCOL_READY_FOR_HUMAN_REVIEW
  -> G3_REALITY_PROOF_EXECUTION_AUTHORIZED
  -> G3_REALITY_PROOF_READY_FOR_HUMAN_REVIEW
  -> G3_RESULTS_MERGED
  -> G4_SETTLEMENT_READY_FOR_HUMAN_REVIEW
  -> G4_SETTLED_MERGED
  -> G5_CLOSURE_READY_FOR_HUMAN_REVIEW
  -> QXM_PROJECT_CLOSED
```

No transition is inferred. Each state transition must cite the exact prior receipt and exact-head CI run.

---

### Task 1: G0 — Close QXM2 under its already-defined merge authority

**Files:**
- Create after semantic merge: `docs/architecture/qxm2/QXM2-MERGE-RECEIPT-v0.1.json`
- Modify after semantic merge: `docs/architecture/qxm2/QXM2-STATE.json`
- Modify after semantic merge: `scripts/validate_qxm2_evidence_hardening.py`
- Modify after semantic merge: `tests/test_qxm2_evidence_hardening.py`

**Interfaces:**
- Consumes: QXM2 PR #38, Human Acceptance Receipt, QXM2 state `human_accepted_ready_for_merge`, final merge-readiness CI.
- Produces: QXM2 `accepted_merged` on `main` plus immutable merge receipt.

- [ ] **Step 1: Check the authority token before doing any mutation**

Require the literal user authorization:

```text
AUTHORIZE_QXM2_MERGE
```

If absent, stop Task 1 and report `G0_WAITING_QXM2_MERGE_AUTHORITY`. Do not merge PR #38.

- [ ] **Step 2: Re-fetch PR #38 and exact-head CI**

Require `open`, `merged=false`, `mergeable=true`. Record the freshly returned `head_sha` as `semantic_merge_head_sha`. Fetch workflow runs for that exact SHA and require current required checks `contracts=success` and `governance=success`, plus the QXM2 validator and full unit tests successful in the corresponding `repository-gates` run.

At plan-freeze time the merge-candidate head is `846a9c2166d770ca0a0471fc35a9cacc1b9590ea` with repository-gates Run #230 / id `32462649431`; execution must use the newly fetched values, not assume the plan-freeze values remain current.

- [ ] **Step 3: Re-audit changed paths**

Reject the semantic merge if any PR path begins with:

```python
PROHIBITED = (
    "registry/theories/",
    "registry/hypotheses/",
    "registry/benchmarks/",
    "registry/capabilities/",
    "canon/",
)
```

- [ ] **Step 4: Squash merge PR #38 with expected-head protection**

Call the merge operation with `merge_method="squash"` and set `expected_head_sha` to the `semantic_merge_head_sha` captured in Step 2. Do not substitute a SHA from this plan document.

- [ ] **Step 5: Create `qxm2/post-merge-closure-v0.1` from the semantic merge commit**

The branch contains only merge bookkeeping and validator hardening.

- [ ] **Step 6: Write a RED merged-state test**

```python
def test_qxm2_accepted_merged_requires_merge_receipt():
    state = load_json(QXM2 / "QXM2-STATE.json")
    if state["status"] == "accepted_merged":
        receipt = load_json(QXM2 / "QXM2-MERGE-RECEIPT-v0.1.json")
        assert receipt["merge_authority"] == "AUTHORIZE_QXM2_MERGE"
        assert receipt["candidate_pack_is_canon"] is False
```

Run the QXM2 test suite and confirm RED before creating the receipt.

- [ ] **Step 7: Write the merge receipt and advance state**

Receipt must include PR number, semantic pre-merge head, pre-merge exact CI run, merge method, merge commit, Human Acceptance token, explicit merge authority, candidate counts, preserved negative authorities, and next gate `QXM_F_G1_SELECTIVE_ADMISSION`.

- [ ] **Step 8: Extend QXM2 validator and run GREEN**

```bash
python scripts/validate_qxm2_evidence_hardening.py
python -m unittest tests.test_qxm2_evidence_hardening -v
```

- [ ] **Step 9: Open closure PR, obtain exact-head repository-gates, then merge closure under the same QXM2 merge authorization**

Use expected-head protection on the closure PR. The closure PR may not introduce Registry, benchmark, capability-promotion, runtime, or trading authority.

- [ ] **Step 10: Verify main**

Fresh-read `main`; require `QXM2.status == "accepted_merged"`, the merge receipt exists, and all higher authorities remain false.

---

### Task 2: Bootstrap the QXM-F program validator and state on the post-G0 baseline

**Files:**
- Carry forward unchanged from design branch: `docs/superpowers/specs/2026-08-21-qxm-f-financial-mechanics-capability-closure-design.md`
- Carry forward unchanged from design branch: `docs/superpowers/plans/2026-08-21-qxm-f-financial-mechanics-capability-closure.md`
- Create: `docs/architecture/qxm-f/QXM-F-STATE.json`
- Create: `scripts/validate_qxm_f_closure.py`
- Create: `tests/test_qxm_f_closure.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: QXM2 `accepted_merged` and `QXM2-MERGE-RECEIPT-v0.1.json` from main.
- Produces: one fail-closed QXM-F state machine, persisted QXM-F spec/plan, and reusable gate validators.

- [ ] **Step 1: Create implementation branch `qxm-f/financial-mechanics-capability-closure-v0.1` from the freshly verified post-G0 main**

Copy the approved QXM-F spec and this plan byte-for-byte from `qxm-f/financial-mechanics-capability-closure-design-v0.1` into the implementation branch. Their content hashes must be recorded in `QXM-F-STATE.json` so execution cannot silently drift from the approved design/plan.

- [ ] **Step 2: Write RED tests for the legal state machine and authority separation**

```python
LEGAL_STATES = {
    "G0_QXM2_ACCEPTED_MERGED",
    "G1_SELECTIVE_ADMISSION_READY_FOR_HUMAN_REVIEW",
    "G1_ADMITTED_MERGED",
    "G2_PREREGISTRATION_READY_FOR_HUMAN_REVIEW",
    "G2_PREREGISTERED_MERGED",
    "G3_PROVIDER_PROTOCOL_READY_FOR_HUMAN_REVIEW",
    "G3_REALITY_PROOF_EXECUTION_AUTHORIZED",
    "G3_REALITY_PROOF_READY_FOR_HUMAN_REVIEW",
    "G3_RESULTS_MERGED",
    "G4_SETTLEMENT_READY_FOR_HUMAN_REVIEW",
    "G4_SETTLED_MERGED",
    "G5_CLOSURE_READY_FOR_HUMAN_REVIEW",
    "QXM_PROJECT_CLOSED",
}

def test_qxm_f_rejects_trading_authority():
    with self.assertRaises(AssertionError):
        assert_no_authority_escalation({"trading_action_authorized": True})
```

- [ ] **Step 3: Run RED**

```bash
python -m unittest tests.test_qxm_f_closure -v
```

Expected: import failure because the QXM-F validator does not yet exist.

- [ ] **Step 4: Implement validator primitives**

Implement `load_json`, `require_fields`, `assert_state`, `assert_no_authority_escalation`, `assert_receipt_precedes_projection`, `assert_registry_counts_consistent`, and `validate_qxm_f(root)`.

- [ ] **Step 5: Create initial QXM-F state**

```json
{
  "schema_version": "0.1.0",
  "stage": "QXM_F_FINANCIAL_MECHANICS_CAPABILITY_CLOSURE",
  "status": "G0_QXM2_ACCEPTED_MERGED",
  "upstream_qxm2_status": "accepted_merged",
  "identity_settlement": "not_started",
  "reality_settlement": "not_started",
  "learning_settlement": "not_started",
  "registry_admission_authority": "none",
  "hypothesis_preregistration_authority": "none",
  "benchmark_execution_authority": "none",
  "capability_promotion_authority": "none",
  "production_runtime_authority": "none",
  "trading_authority": "none",
  "next_gate": "QXM_F_G1_SELECTIVE_ADMISSION"
}
```

Add `approved_spec_sha256` and `approved_plan_sha256` using the actual byte hashes produced in Step 1.

- [ ] **Step 6: Add QXM-F validator to `repository-gates` after QXM2 validator**

```yaml
- run: python scripts/validate_qxm_f_closure.py
```

- [ ] **Step 7: Run GREEN and commit**

```bash
python scripts/validate_qxm_f_closure.py
python -m unittest discover -s tests -p 'test_*.py' -v
git add docs/superpowers/specs docs/superpowers/plans docs/architecture/qxm-f scripts/validate_qxm_f_closure.py tests/test_qxm_f_closure.py .github/workflows/ci.yml
git commit -m "test(qxm-f): bootstrap closure state and governance validator"
```

---

### Task 3: G1 — Build the Selective Admission Ledger without touching formal Registry packs

**Files:**
- Create: `docs/architecture/qxm-f/g1/QXM-F-G1-ADMISSION-LEDGER-v0.1.json`
- Create: `docs/architecture/qxm-f/g1/QXM-F-G1-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `scripts/validate_qxm_f_closure.py`
- Modify: `tests/test_qxm_f_closure.py`
- Modify: `docs/architecture/qxm-f/QXM-F-STATE.json`

**Interfaces:**
- Consumes: exactly 12 QXM2 Shadow TheoryObjects, 12 Shadow HypothesisObjects, 6 Benchmark Seeds and the per-candidate QXM2 recommendations.
- Produces: one complete admission candidate ledger; no formal Registry mutation.

- [ ] **Step 1: Write RED coverage tests**

Require exactly 30 source objects in the ledger: 12 theories + 12 hypotheses + 6 benchmark seeds. Each theory/hypothesis disposition enum is `ADMIT | ADMIT_WITH_BOUNDARY | KEEP_SHADOW | REJECT`; each seed disposition enum is `FORMALIZE | DEFER | REJECT`. Before Human Review, `human_disposition` must be `null` and `recommended_disposition` must be explicit.

- [ ] **Step 2: Generate ledger rows from QXM2 object IDs without renaming semantic IDs**

Each row must carry `source_shadow_id`, canonical object ID, candidate ID/profile, QXM2 recommendation, evidence boundary, recommended disposition, human disposition, rationale, and downstream authority requested.

- [ ] **Step 3: Enforce the Tier-3 boundary**

Any row linked to `QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE` must prohibit predictive/timing admission unless a later G2/G3 predictive path is explicitly selected and preregistered.

- [ ] **Step 4: Create Human Review Card**

The card must require a disposition for every row and explicitly ask whether any recommended admission overstates evidence authority.

Human Gate token:

```text
ACCEPT_QXM_F_G1_SELECTIVE_ADMISSION
```

- [ ] **Step 5: Run GREEN, obtain exact-head CI, set state to `G1_SELECTIVE_ADMISSION_READY_FOR_HUMAN_REVIEW`, and stop**

Do not write `registry/theories`, `registry/hypotheses`, or `registry/benchmarks` before the Human token.

---

### Task 4: G1 — Apply accepted dispositions to the formal Theory/Hypothesis Registry

**Files:**
- Create after Human Acceptance: `docs/architecture/qxm-f/g1/QXM-F-G1-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json`
- Create: `registry/theories/qxm-f-financial-mechanics-v0.1.json`
- Create: `registry/hypotheses/qxm-f-financial-mechanics-v0.1.json`
- Modify: `registry/theories/_index.json`
- Modify: `registry/hypotheses/_index.json`
- Modify: `registry/registry-index.json`
- Create: `docs/architecture/qxm-f/g1/QXM-F-G1-ADMISSION-RECEIPT-v0.1.json`
- Modify: QXM-F validator/tests/state.

**Interfaces:**
- Consumes: Human-accepted G1 ledger.
- Produces: formal TheoryObjects and `proposed` HypothesisObjects only for accepted rows; seeds remain non-formal until G2.

- [ ] **Step 1: Verify literal Human token and exact reviewed head**

If `ACCEPT_QXM_F_G1_SELECTIVE_ADMISSION` is absent, stop with no Registry writes.

- [ ] **Step 2: Write RED tests for exact Registry delta**

```python
def test_g1_registry_delta_equals_accepted_ledger():
    ledger = load_json(G1_LEDGER)
    expected_theory_ids = {
        r["object_id"] for r in ledger["theories"]
        if r["human_disposition"] in {"ADMIT", "ADMIT_WITH_BOUNDARY"}
    }
    expected_hyp_ids = {
        r["object_id"] for r in ledger["hypotheses"]
        if r["human_disposition"] in {"ADMIT", "ADMIT_WITH_BOUNDARY"}
    }
    assert ids_from_pack(THEORY_PACK) == expected_theory_ids
    assert ids_from_pack(HYP_PACK) == expected_hyp_ids
```

- [ ] **Step 3: Materialize accepted objects using existing schemas**

Copy the QXM2 inner `theory_object` / `hypothesis_object` payloads without semantic mutation. G1 formal hypotheses remain `status="proposed"`.

- [ ] **Step 4: Update subindexes and global Registry count deterministically**

Compute each new `entry_count` from pack contents, then require the global total to equal the sum of all nine registry subindex counts.

- [ ] **Step 5: Run R1 validator, QXM-F validator and full tests**

```bash
python scripts/validate_r1_registry.py
python scripts/validate_qxm_f_closure.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 6: Set state to Human-accepted ready-for-merge and wait for separate merge authority**

Required token:

```text
AUTHORIZE_QXM_F_G1_MERGE
```

- [ ] **Step 7: After authorization, squash merge exact head and close G1 with receipt**

Post-merge state: `G1_ADMITTED_MERGED`; next gate `QXM_F_G2_PREREGISTRATION`.

---

### Task 5: G2 — Compile preregistration and formal Benchmark candidates before results are visible

**Files:**
- Create: `docs/architecture/qxm-f/g2/QXM-F-G2-PREREGISTRATION-PACK-v0.1.json`
- Create: `docs/architecture/qxm-f/g2/QXM-F-G2-BENCHMARK-CANDIDATES-v0.1.json`
- Create: `docs/architecture/qxm-f/g2/QXM-F-G2-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: validator/tests/state.

**Interfaces:**
- Consumes: G1 admitted `proposed` hypotheses and seed dispositions marked `FORMALIZE`.
- Produces: frozen candidate experiment contracts plus SHA-256 hashes; still no benchmark execution.

- [ ] **Step 1: Create branch `qxm-f/g2-preregistration-benchmark-v0.1` from the verified G1 post-merge main**

Do not continue using the G1 branch after G1 is merged.

- [ ] **Step 2: Write RED tests that require immutable experiment fields**

Each selected hypothesis/benchmark pair must freeze target, horizon, universe, conditioning state, baseline, split method, PIT policy, lookahead prohibition, regime holdout, metric set, acceptance threshold, complexity penalty, multiple-testing policy, calibration requirement, missing-data policy and revision rule.

- [ ] **Step 3: Define exact benchmark IDs**

Use R1 ID rules:

```text
BENCH-P-FUNDAMENTAL-DRIVER-INCREMENTAL-V1
BENCH-P-CASH-CONVERSION-INTEGRITY-V1
BENCH-P-CREDIT-BALANCE-TRANSMISSION-V1
BENCH-V-DISCOUNT-RATE-EXPECTATION-DECOMPOSITION-V1
BENCH-S-STRESS-EXIT-LIQUIDITY-V1
BENCH-CROSS-RETURN-SOURCE-ATTRIBUTION-V1
```

Only IDs whose seed disposition is `FORMALIZE` may enter the candidate pack.

- [ ] **Step 4: Freeze the modality for Return Source Attribution**

Its `split_method` must use held-out ResearchReceipt/episode cases; its acceptance threshold must evaluate reconstruction error and thesis-fidelity discrimination versus naive P&L-sign/baseline attribution. Do not use forecast accuracy as the primary metric.

- [ ] **Step 5: Hash every preregistration record**

Use canonical JSON serialization with `sort_keys=True`, UTF-8 and compact separators, then SHA-256. Store `contract_hash` in the preregistration pack.

- [ ] **Step 6: Create Human Review Card and obtain exact-head CI**

Human Gate token:

```text
ACCEPT_QXM_F_G2_PREREGISTRATION_BENCHMARK_FORMALIZATION
```

Stop before mutating formal hypothesis status or `registry/benchmarks`.

---

### Task 6: G2 — Preregister hypotheses and create formal BenchmarkObjects

**Files:**
- Create after Human Acceptance: `docs/architecture/qxm-f/g2/QXM-F-G2-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json`
- Modify: `registry/hypotheses/qxm-f-financial-mechanics-v0.1.json`
- Create: `registry/benchmarks/qxm-f-financial-mechanics-v0.1.json`
- Modify Registry indexes/global index.
- Create: `docs/architecture/qxm-f/g2/QXM-F-G2-PREREGISTRATION-RECEIPT-v0.1.json`
- Modify validator/tests/state.

**Interfaces:**
- Consumes: Human-accepted G2 pack and hashes.
- Produces: selected formal hypotheses with `status="preregistered"` and formal BenchmarkObjects; execution authority remains false.

- [ ] **Step 1: Write RED tests that reject unaccepted status changes and benchmark drift**

Require every changed hypothesis ID to be Human-accepted, and require its non-status semantic fields to hash identically to the G1 version. Require each BenchmarkObject to hash to the accepted G2 candidate contract.

- [ ] **Step 2: Change only selected hypotheses from `proposed` to `preregistered`**

No statement, null, target, horizon, universe, conditioning state, direction or falsification text may change in the same commit.

- [ ] **Step 3: Materialize BenchmarkObjects and validate against `benchmark-object.schema.json`**

Every object must have `lookahead_prohibited=true` and at least one simple baseline.

- [ ] **Step 4: Assert execution remains unauthorized**

The G2 receipt must contain:

```json
{
  "benchmark_execution_authorized": false,
  "benchmark_pass_claim_authorized": false,
  "capability_promotion_authorized": false
}
```

- [ ] **Step 5: Run Registry/QXM-F/full tests, exact-head CI, then stop for merge authority**

Required merge token:

```text
AUTHORIZE_QXM_F_G2_MERGE
```

- [ ] **Step 6: After authorization, merge and close G2**

Post-merge state: `G2_PREREGISTERED_MERGED`; next gate `QXM_F_G3_PROVIDER_AND_REALITY_PROOF`.

---

### Task 7: G3A — Compile provider-neutral fields, implementation contracts, Wind mapping candidates, and the execution packet

**Files:**
- Create: `docs/architecture/qxm-f/g3/QXM-F-G3-CANONICAL-FIELD-GAPS-v0.1.json`
- Create: `docs/architecture/qxm-f/g3/QXM-F-G3-WIND-PROVIDER-ADAPTER-CANDIDATE-v0.1.json`
- Create: `docs/architecture/qxm-f/g3/QXM-F-G3-IMPLEMENTATION-CONTRACTS-v0.1.json`
- Create: `docs/architecture/qxm-f/g3/QXM-F-G3-WIND-EXECUTION-TASK-SPEC-v0.1.md`
- Create: `docs/architecture/qxm-f/g3/QXM-F-G3-HUMAN-REVIEW-CARD-v0.1.md`
- Create deterministic reference implementation modules under `src/yuanli_research/financial_mechanics/` only for G2-preregistered tests.
- Create unit tests under `tests/financial_mechanics/`.
- Modify QXM-F validator/tests/state.

**Interfaces:**
- Consumes: G2 formal hypotheses/benchmarks and current canonical data-field registry.
- Produces: provider-neutral implementation contracts and a schema-compatible Wind ProviderAdapter candidate; no licensed data and no benchmark execution yet.

- [ ] **Step 1: Create branch `qxm-f/g3-provider-reality-proof-v0.1` from the verified G2 post-merge main**

G3A and G3B share this single G3 branch/PR because G3B is execution of the protocol reviewed in G3A; no G3 merge occurs between protocol review and authorized execution.

- [ ] **Step 2: Inventory every required observable against `registry/data-fields`**

Classify each as `existing_field`, `new_provider_neutral_field_required`, or `provider_only_not_canonical`. New economic semantics require a new `FIELD-*`; Wind codes never appear in `FIELD-*` identities.

- [ ] **Step 3: Write RED implementation tests per Tier-1 capability**

Minimum modules:

```text
fundamental_driver.py
three_statement_integrity.py
return_source_attribution.py
```

Each exposes a deterministic function returning structured ResearchState-compatible diagnostics and abstains/fails closed on missing PIT lineage.

- [ ] **Step 4: Create FactorObject or AlgorithmObject candidates required by `ResearchCapability` schema**

Do not create a ResearchCapability entry that lacks both factor and algorithm linkage; the schema explicitly requires at least one. Predictive mechanics may use FactorObject/AlgorithmObject; attribution may use an AlgorithmObject with `causal_claim_status="not_applicable"` or `descriptive` as justified by the contract.

- [ ] **Step 5: Build Wind ProviderAdapter candidate**

Use `PROVIDER-WIND-FINANCIAL-MECHANICS-V1` if it still validates against the current provider schema at execution time. Every mapping must specify canonical `field_id`, provider field, transformation, PIT compatibility and revision handling; `canonical_semantics_may_not_be_redefined=true`.

- [ ] **Step 6: Write the external Wind execution task spec**

The task spec must list benchmark IDs, preregistration hashes, required universes/splits, field mappings, publication-lag rules, permitted derived transforms, simple baselines, expected receipt schema, and the prohibition on uploading raw licensed data to GitHub.

- [ ] **Step 7: Create Human Review Card and obtain exact-head CI**

Human Gate token:

```text
ACCEPT_QXM_F_G3_PROVIDER_MAPPING_AND_EXECUTION_PROTOCOL
```

Stop before any licensed data execution.

---

### Task 8: G3B — Authorize and execute PIT/held-out reality proof, then ingest receipts only

**Files:**
- After protocol acceptance, create formal `registry/providers/qxm-f-wind-financial-mechanics-v0.1.json` and any accepted `registry/data-fields/qxm-f-financial-mechanics-v0.1.json`, `registry/factors/qxm-f-financial-mechanics-v0.1.json`, `registry/algorithms/qxm-f-financial-mechanics-v0.1.json`.
- Create result receipts under `research/financial-mechanics/reality-proof/`.
- Create: `docs/architecture/qxm-f/g3/QXM-F-G3-REALITY-PROOF-RESULTS-v0.1.json`
- Create: `docs/architecture/qxm-f/g3/QXM-F-G3-HUMAN-REVIEW-CARD-RESULTS-v0.1.md`
- Modify Registry indexes, validator/tests/state.

**Interfaces:**
- Consumes: frozen G2 benchmark hashes, accepted G3 protocol, authorized provider access outside GitHub.
- Produces: immutable execution receipts with metrics and data lineage; no self-promotion.

- [ ] **Step 1: Require explicit execution authority**

Literal token:

```text
AUTHORIZE_QXM_F_G3_REALITY_PROOF_EXECUTION
```

Without it, no Wind/provider data request may run.

- [ ] **Step 2: Execute Tier-1 four-part proof**

For CAP-P-003 and CAP-P-004: PIT replay, true OOS/held-out prediction-or-explanation test, regime holdout, failure replay.

For CAP-CROSS-001: PIT position/receipt reconstruction, held-out episode reconstruction and thesis-fidelity discrimination, regime/asset-form holdout, hindsight/failure replay.

- [ ] **Step 3: Execute Tier-2 only when data contract is genuinely satisfiable**

Credit and Stress Liquidity may return `DEFER_DATA_INSUFFICIENT` when vintage-consistent borrower/funding/stress data is inadequate. `DEFER_DATA_INSUFFICIENT` cannot be counted as support.

- [ ] **Step 4: Store receipt-only results**

Each receipt must include benchmark ID, preregistration hash, implementation revision, provider adapter revision, data-vintage/hash metadata, universe size, time span, split/regime labels, baseline metrics, candidate metrics, failure metrics, missingness, exclusions, and `raw_licensed_data_committed=false`.

- [ ] **Step 5: Validate result integrity**

A result is stale if its preregistration hash, code revision, provider adapter revision, or BenchmarkObject revision differs from the frozen execution contract.

- [ ] **Step 6: Human Results Review**

Token:

```text
ACCEPT_QXM_F_G3_REALITY_PROOF_RESULTS
```

Human Review judges data lineage, leakage, metric interpretation, boundary/failure evidence, and whether results are admissible for settlement. It does not promote capabilities.

- [ ] **Step 7: After Human Acceptance and exact-head CI, wait for merge authority**

```text
AUTHORIZE_QXM_F_G3_MERGE
```

After merge: state `G3_RESULTS_MERGED`; next gate `QXM_F_G4_CAPABILITY_SETTLEMENT`.

---

### Task 9: G4 — Compute settlement candidates and Known Failure Envelopes without self-promotion

**Files:**
- Create: `docs/architecture/qxm-f/g4/QXM-F-G4-CAPABILITY-SETTLEMENT-CANDIDATES-v0.1.json`
- Create: `docs/architecture/qxm-f/g4/QXM-F-G4-KNOWN-FAILURE-ENVELOPES-v0.1.json`
- Create: `docs/architecture/qxm-f/g4/QXM-F-G4-HUMAN-REVIEW-CARD-v0.1.md`
- Modify validator/tests/state.

**Interfaces:**
- Consumes: six candidate dispositions, G2 preregistration/benchmark receipts, G3 results/defer records.
- Produces: exactly one proposed terminal research disposition for each of six QXM candidates.

- [ ] **Step 1: Create branch `qxm-f/g4-capability-settlement-v0.1` from the verified G3 post-merge main**

- [ ] **Step 2: Write RED test requiring 6/6 settlement coverage**

Legal values:

```python
SETTLEMENTS = {
    "PROMOTE",
    "PROMOTE_WITH_BOUNDARY",
    "INTERPRETATION_ONLY",
    "REJECT_OR_REDESIGN",
}
```

Every candidate must have one proposed settlement, evidence pointers, benchmark outcome, boundary, and runtime-authority proposal.

- [ ] **Step 3: Derive candidate settlement from frozen rules, never from narrative preference**

A predictive promotion requires meeting the exact G2 acceptance threshold against simple baselines. An attribution/interpretation promotion requires the corresponding reconstruction/discrimination threshold. Failed, deferred, or stale benchmarks cannot be overridden by prose rationale.

- [ ] **Step 4: Build Known Failure Envelope for every proposed promoted/bounded capability**

Require unsupported asset forms, sectors/regimes, data-quality failures, false positives, false negatives, causal-language limits, provider limits and abstention conditions.

- [ ] **Step 5: Enforce Discount-Rate boundary**

Without a valid predictive benchmark PASS, Candidate 04 settlement cannot be `PROMOTE` with timing authority; it may remain `INTERPRETATION_ONLY` or be redesigned.

- [ ] **Step 6: Create Human Review Card and stop at exact-head CI**

Token:

```text
ACCEPT_QXM_F_G4_CAPABILITY_SETTLEMENT
```

No Capability Registry mutation occurs before this token.

---

### Task 10: G4 — Apply settlement, lifecycle transitions, and build `FM-GOLD-01` only when earned

**Files:**
- Create after Human Acceptance: `docs/architecture/qxm-f/g4/QXM-F-G4-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json`
- Create/update: `registry/capabilities/qxm-f-financial-mechanics-v0.1.json`
- Create accepted Factor/Algorithm/Skill packs when required by promoted capability contracts.
- Update Registry indexes/global index.
- Create: `research/financial-mechanics/FM-GOLD-01/README.md` only if Tier-1 settlement meets the Gold Pack rule.
- Create: `research/financial-mechanics/FM-GOLD-01/manifest.json` only if Gold Pack exists.
- Create: `docs/architecture/qxm-f/g4/QXM-F-G4-SETTLEMENT-RECEIPT-v0.1.json`
- Modify validator/tests/state.

**Interfaces:**
- Consumes: Human-accepted settlements.
- Produces: lifecycle-legal ResearchCapability entries/revisions and optional de-personalized Gold Pack.

- [ ] **Step 1: Write RED lifecycle tests**

Reject any capability maturity jump that lacks the R1-required receipts. For example, `specified -> benchmark_passed` is illegal unless implementation, replication and benchmark receipts exist or an explicit migration receipt proves those intermediate states.

- [ ] **Step 2: Create or revise formal capability objects only to the highest earned maturity**

`PROMOTE` is a QXM-F settlement label, not permission to write `maturity_state="canon"`. Use the highest state actually supported by R1 evidence; entering `canon` still requires the separate R1 Human Gate semantics.

- [ ] **Step 3: Preserve profile semantics for CAP-R-01 and CAP-V-01**

Do not overwrite mother capability meaning to force a QXM profile into the current schema. If the current schema lacks a profile representation, keep the profile settlement in the QXM-F ledger and do not mutate the mother object under the same ID.

- [ ] **Step 4: Build `FM-GOLD-01` only if all three Tier-1 core capabilities have accepted usable settlement**

If any Tier-1 object is `REJECT_OR_REDESIGN`, record `gold_pack_created=false` with exact reason in the settlement receipt instead of creating a cosmetic Gold Pack.

- [ ] **Step 5: Run R1/QXM-F/full tests and exact-head CI**

```bash
python scripts/validate_r1_registry.py
python scripts/validate_qxm_f_closure.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 6: Wait for separate merge authority**

```text
AUTHORIZE_QXM_F_G4_MERGE
```

After merge: state `G4_SETTLED_MERGED`; next gate `QXM_F_G5_ERC_CANONIZATION`.

---

### Task 11: G5 — Compile the External Research Compiler and QXM Gold Case

**Files:**
- Create: `docs/research-compiler/EXTERNAL-RESEARCH-COMPILER-CANON-v0.1.md`
- Create: `docs/research-compiler/SOURCE-AUTHORITY-CONTRACT-v0.1.json`
- Create: `docs/research-compiler/EVIDENCE-RELATION-CONTRACT-v0.1.json`
- Create: `docs/research-compiler/ADMISSION-GATE-v0.1.md`
- Create: `docs/research-compiler/SETTLEMENT-GATE-v0.1.md`
- Create: `docs/research-compiler/ERC-GOLD-CASE-001-QXM.md`
- Create: `docs/architecture/qxm-f/g5/QXM-F-G5-CLOSURE-CANDIDATE-v0.1.json`
- Create: `docs/architecture/qxm-f/g5/QXM-F-G5-HUMAN-REVIEW-CARD-v0.1.md`
- Modify validator/tests/state.

**Interfaces:**
- Consumes: complete QXM0/QXM1/QXM2/QXM-F provenance, all dispositions and settlements.
- Produces: reusable External Research Compiler protocol and archival Gold Case; QXM is not declared closed until Human Gate and merge.

- [ ] **Step 1: Create branch `qxm-f/g5-erc-canonization-closure-v0.1` from the verified G4 post-merge main**

- [ ] **Step 2: Write RED closure tests for the 13-stage compiler sequence**

Require exactly:

```text
R0 Source Authority Classification
R1 Mechanism Extraction
R2 Capability Candidate Contract
R3 Primary Theory Ancestry
R4 Evidence Graph
R5 Atomic Claim Compilation
R6 Shadow Theory / Hypothesis
R7 Human Epistemic Review
R8 Selective Registry Admission
R9 Hypothesis Preregistration
R10 Implementation / Provider Mapping
R11 PIT/Held-Out Benchmark + Failure Replay
R12 Settlement
R13 Promote / Bound / Interpret / Reject
```

- [ ] **Step 3: Encode the de-personalization law**

The ERC contract must preserve source/person provenance but prohibit practitioner authority from automatically creating Theory, Hypothesis, Capability or runtime authority.

- [ ] **Step 4: Build `ERC-GOLD-CASE-001-QXM.md` as an auditable case, not a biography**

It must map QXM0 -> QXM1 -> QXM2 -> QXM-F, show accepted/rejected/deferred objects, reality proofs, failures, settlement decisions, and the compiler rules learned from the project.

- [ ] **Step 5: Evaluate the full Project Closure Contract**

Closure candidate must prove: QXM2 accepted_merged; six candidate terminal dispositions; all 12 theory shadows disposed; all 12 hypothesis shadows disposed; all six seeds formalized/deferred/rejected; Tier-1 four-part reality proof; simple baselines; Tier-1 settlement receipts; failure envelopes for promoted/bounded objects; no orphan Registry objects; ERC frozen; trading authority still false.

- [ ] **Step 6: Create Human Review Card and exact-head CI**

Human Gate token:

```text
ACCEPT_QXM_F_G5_ERC_CANONIZATION_QXM_CLOSURE
```

Stop before declaring `QXM_PROJECT_CLOSED`.

---

### Task 12: G5 — Final closure receipt, merge, and archive state

**Files:**
- Create after Human Acceptance: `docs/architecture/qxm-f/g5/QXM-F-G5-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json`
- Create: `docs/architecture/qxm-f/QXM-F-CLOSURE-RECEIPT-v0.1.json`
- Modify: `docs/architecture/qxm-f/QXM-F-STATE.json`
- Modify validator/tests.

**Interfaces:**
- Consumes: Human-accepted G5 closure candidate and exact-head CI.
- Produces: terminal QXM project state and immutable closure ledger.

- [ ] **Step 1: Write RED terminal-state test**

```python
def test_qxm_project_closed_requires_all_three_settlements():
    state = load_json(QXM_F_STATE)
    if state["status"] == "QXM_PROJECT_CLOSED":
        assert state["identity_settlement"] == "complete"
        assert state["reality_settlement"] == "complete"
        assert state["learning_settlement"] == "complete"
        assert state["trading_authority"] == "none"
```

- [ ] **Step 2: Create Human Acceptance Receipt and final Closure Receipt**

Closure Receipt must include every gate receipt, exact QXM2 merge commit, Registry object deltas, preregistration hashes, benchmark/result receipts, six terminal dispositions, Gold Pack creation decision, ERC revision, final exact-head CI and explicit `trading_authority=false`.

- [ ] **Step 3: Advance state only after receipt exists**

```json
{
  "status": "QXM_PROJECT_CLOSED",
  "identity_settlement": "complete",
  "reality_settlement": "complete",
  "learning_settlement": "complete",
  "active_research_campaign": false,
  "erc_gold_case": "ERC-GOLD-CASE-001",
  "trading_authority": "none",
  "next_gate": "CAPABILITY_REVISION_OR_FUTURE_SETTLEMENT_ONLY"
}
```

- [ ] **Step 4: Run final full validation**

```bash
python scripts/validate_r1_registry.py
python scripts/validate_qxm2_evidence_hardening.py
python scripts/validate_qxm_f_closure.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 5: Obtain exact-head repository-gates and stop for merge authority**

Required token:

```text
AUTHORIZE_QXM_F_G5_MERGE
```

- [ ] **Step 6: Squash merge with expected-head protection, then verify main**

Main must show `QXM_PROJECT_CLOSED`, ERC Gold Case present, no orphan QXM object, and no trading authority. The closure does not create or imply any future portfolio/trading permission.

---

## Required Human / Authority Tokens in Order

```text
1. AUTHORIZE_QXM2_MERGE
2. ACCEPT_QXM_F_G1_SELECTIVE_ADMISSION
3. AUTHORIZE_QXM_F_G1_MERGE
4. ACCEPT_QXM_F_G2_PREREGISTRATION_BENCHMARK_FORMALIZATION
5. AUTHORIZE_QXM_F_G2_MERGE
6. ACCEPT_QXM_F_G3_PROVIDER_MAPPING_AND_EXECUTION_PROTOCOL
7. AUTHORIZE_QXM_F_G3_REALITY_PROOF_EXECUTION
8. ACCEPT_QXM_F_G3_REALITY_PROOF_RESULTS
9. AUTHORIZE_QXM_F_G3_MERGE
10. ACCEPT_QXM_F_G4_CAPABILITY_SETTLEMENT
11. AUTHORIZE_QXM_F_G4_MERGE
12. ACCEPT_QXM_F_G5_ERC_CANONIZATION_QXM_CLOSURE
13. AUTHORIZE_QXM_F_G5_MERGE
```

A token authorizes only its named action. No token may be inferred from a previous token or from approval of this plan.

## Final Verification Checklist

Before claiming QXM-F complete, verify all of the following from fresh repository/runtime evidence:

- QXM2 state is `accepted_merged` on main.
- Every QXM2 Shadow TheoryObject has a terminal G1 disposition.
- Every QXM2 Shadow HypothesisObject has a terminal G1/G2 disposition.
- Every Benchmark Seed has `FORMALIZE`, `DEFER`, or `REJECT` disposition.
- Every formally executed benchmark points to its preregistration hash and exact provider/implementation revisions.
- All Tier-1 capabilities have PIT, held-out, regime and failure proof receipts.
- Every executed complex method was compared with the declared simple baseline.
- Every promoted/bounded capability has a Known Failure Envelope.
- Six QXM candidates have exactly one accepted G4 terminal settlement each.
- Registry indexes exactly equal pack object counts and contain no orphan QXM references.
- `FM-GOLD-01` exists only if its creation rule was earned; otherwise the settlement receipt records why it was not created.
- ERC v0.1 is frozen and QXM is `ERC-GOLD-CASE-001`.
- `QXM-F-CLOSURE-RECEIPT-v0.1.json` exists before State is projected to `QXM_PROJECT_CLOSED`.
- QXM project closure leaves target price, recommendation, position sizing, broker action and live execution authority unavailable.
