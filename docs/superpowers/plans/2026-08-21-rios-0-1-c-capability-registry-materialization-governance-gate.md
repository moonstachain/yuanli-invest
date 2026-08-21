# RIOS-0.1-C Capability Registry Materialization & Governance Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Materialize the ten RIOS Genesis concepts as a governed convergence/orchestration layer over the existing R1/R2 ResearchCapability system, prove exact coverage and authority boundaries in CI, and stop at Human Review before any formal Registry mutation.

**Architecture:** RIOS-0.1-C does not create a second Registry or rename existing ResearchCapability identities. It creates a ten-row convergence matrix plus a Genesis orchestration manifest under `docs/architecture/rios/0.1-c/`, validates both against the existing Registry graph, and permits later Registry apply only for Human-accepted genuine semantic gaps whose dependencies satisfy the unchanged R1 schema.

**Tech Stack:** Python 3.12, stdlib `json` / `pathlib` / `subprocess`, `jsonschema==4.25.1`, `unittest`, GitHub Actions `repository-gates`.

**Spec:** `docs/superpowers/specs/2026-08-21-rios-0-1-c-capability-registry-materialization-governance-gate-design.md`

## Global Constraints

- No parallel `/capabilities/registry.yaml`, alternate Capability schema, or tenth Registry namespace.
- Preserve current `ResearchCapability` ID pattern `^CAP-(P|N|XS|XA|XP|V|S|E|CROSS)-[0-9]{3}-[A-Z0-9-]+$`.
- Preserve maturity lifecycle `concept → specified → implemented → replicated → benchmark_passed → shadow_qualified → canon → deprecated`.
- Pre-Human phase must not modify `registry/**`, `canon/**`, provider/runtime/live-execution code, or existing R1/R2 capability identities.
- Provider Independence remains mandatory; provider-native fields do not enter capability semantics.
- Scalar PNX/Force scores and target-price / buy-sell / recommended-weight / position-size / broker / live-execution outputs are prohibited.
- CI establishes structural/governance validity only, never evidence truth, investment validity, Benchmark PASS, Runtime authority, or Trading authority.
- Human Acceptance does not imply merge or Registry apply.
- Design-time baseline was `main@bd8931e1bf21dceb5e34a68ec41aa199b83e9410`, Registry total 99, active Capability count 12, Canon 0, Provider 0. Execution must re-read fresh main and audit base drift.
- Physical capability pack presence is not equivalent to active Registry admission. Duplicate-ID scans inspect all physical packs; active counts come from governed indexes.

## File Map

**Pre-Human create:**
- `docs/architecture/rios/0.1-c/RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json`
- `docs/architecture/rios/0.1-c/RIOS-0.1-C-GENESIS-PACK-v0.1.json`
- `docs/architecture/rios/0.1-c/RIOS-0.1-C-STATE.json`
- `docs/architecture/rios/0.1-c/RIOS-0.1-C-HUMAN-REVIEW-CARD-v0.1.md`
- `scripts/validate_rios_0_1_c_capability_registry.py`
- `tests/test_rios_0_1_c_capability_registry.py`

**Pre-Human modify:**
- `.github/workflows/ci.yml`

**Conditional post-Human only:**
- `docs/architecture/rios/0.1-c/RIOS-0.1-C-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json`
- optional `registry/capabilities/rios-0-1-c-new-candidates-v0.1.json`
- optional Registry indexes, only after separate Registry-apply authority.

---

### Task 1: Isolated execution branch, base-drift audit, and validator primitives

**Files:** Create `tests/test_rios_0_1_c_capability_registry.py`, `scripts/validate_rios_0_1_c_capability_registry.py`, `docs/architecture/rios/0.1-c/RIOS-0.1-C-STATE.json`.

- [ ] Re-read fresh `main`; compare it with design base. If concurrent commits touch Registry, CI, R1/R2 schemas, or RIOS paths, preserve and reconcile them before any implementation.
- [ ] Use `superpowers:using-git-worktrees` when a local repo is available; otherwise create a dedicated GitHub implementation branch from fresh main. Never implement on `main`.
- [ ] Run baseline:

```bash
python scripts/validate_r1_registry.py
python scripts/validate_r2_gold_pack.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] Write RED tests first. Freeze exact Genesis IDs:

```python
EXPECTED_GENESIS_IDS = [
    "RIOS-GEN-01-AI-INFRASTRUCTURE-REGIME-TRANSITION",
    "RIOS-GEN-02-ENERGY-BOTTLENECK-CAPTURE",
    "RIOS-GEN-03-NARRATIVE-DIFFUSION-ENGINE",
    "RIOS-GEN-04-NARRATIVE-BUBBLE-DETECTION",
    "RIOS-GEN-05-PLATFORM-WINNER-CAPTURE",
    "RIOS-GEN-06-CONVEXITY-EXPRESSION-ENGINE",
    "RIOS-GEN-07-EVIDENCE-AUTHORITY-ENGINE",
    "RIOS-GEN-08-NARRATIVE-PRICE-GAP",
    "RIOS-GEN-09-PORTFOLIO-SURVIVAL-ENGINE",
    "RIOS-GEN-10-MARKET-CLOCK-REGIME-TRANSITION",
]
```

Tests must fail on an eleventh concept and on pre-Human paths such as `registry/capabilities/new.json`.
- [ ] Confirm targeted RED with `python -m unittest tests.test_rios_0_1_c_capability_registry -v`.
- [ ] Implement primitives `assert_exact_genesis_ids`, `assert_classification`, `assert_non_authority`, `assert_pre_human_scope`, `validate_rios_0_1_c`.
- [ ] Create initial State with `status=convergence_compilation_started`, `next_gate=RIOS_0_1_C_CONVERGENCE_COMPILATION`, and Registry/Benchmark/Runtime/Trading authorities all `none`.
- [ ] Re-run targeted tests; primitives GREEN while full-pack test remains RED because Matrix/Pack are missing.
- [ ] Commit: `test(rios): bootstrap 0.1-c convergence gate`.

---

### Task 2: Compile exact ten-row Capability Convergence Matrix

**Files:** Create Matrix; modify tests and validator.

Each row requires:
`genesis_id`, `human_name`, `classification`, `canonical_capability_ids`, `candidate_capability_id`, `rationale`, `semantic_overlap_notes`, `authority_boundary`, `registry_mutation_required`, `benchmark_execution_authorized`, `runtime_authorized`, `trading_authorized`.

Allowed classification: `reuse | composite | profile | new_candidate | reject`.

- [ ] Add RED tests for exactly ten rows, unique identities, exact coverage, and all execution authorities false.
- [ ] Freeze starting classifications:

```text
GEN-01 profile
GEN-02 profile
GEN-03 composite
GEN-04 composite
GEN-05 composite
GEN-06 composite
GEN-07 new_candidate
GEN-08 composite
GEN-09 composite
GEN-10 new_candidate
```

Market Clock may be downgraded by Human Review to `composite` if irreducible CROSS semantics are not demonstrated.
- [ ] Confirm RED because Matrix is absent.
- [ ] Build Matrix using fresh governed capability identities. Minimum intent:
  - GEN-01: P001/P002 + XS001/XS002 + N001/N002 + governed V identity.
  - GEN-02: P001/P002 + XS002.
  - GEN-03: N001 + N002.
  - GEN-04: N002 + governed V identity + XA002.
  - GEN-05: XS001 + XS002.
  - GEN-06: XA001 + XA002 + XP001.
  - GEN-07: proposed `CAP-E-001-EVIDENCE-AUTHORITY-VALIDATION`.
  - GEN-08: governed Price-Implied Expectations identity; target price prohibited.
  - GEN-09: governed S identities present on fresh main.
  - GEN-10: preferred `CAP-CROSS-002-MARKET-CLOCK-REGIME-TRANSITION` only if duplicate scan proves unused.
- [ ] Implement `load_available_capability_ids(root)`: scan all physical `registry/capabilities/*.json` except `_index.json` for referential/duplicate checks, but derive active authority from governed indexes.
- [ ] Every canonical dependency must resolve; stale aliases fail closed.
- [ ] GREEN targeted tests and commit `feat(rios): compile genesis capability convergence matrix`.

---

### Task 3: Genesis Orchestration Pack and Agent routing

**Files:** Create Genesis Pack; modify tests and validator.

Pack contract:
- `pack_id=RIOS-GENESIS-PACK-001`
- `status=candidate_orchestration_pack`
- routing labels only: `P_AGENT`, `N_AGENT`, `X_AGENT`, `E_AGENT`, `V_AGENT`, `S_AGENT`, `CHIEF_RESEARCH_COUNCIL`.

- [ ] RED tests require ten concepts, dependencies equal Matrix, Replay prerequisites, and all non-authorities false.
- [ ] Add negative tests for `target_price`, `buy_signal`, `sell_signal`, `recommended_weight`, `target_weight`, `position_size`, `broker_action`, `live_execution`, `pnx_score`, `force_score`.
- [ ] Confirm RED because Pack is absent.
- [ ] Create Pack. Agent routing references Genesis IDs and canonical dependencies; it does not copy canonical theory/mechanism semantics into Agent definitions.
- [ ] Replay prerequisites remain research-only: `historical_case_required`, `pit_evidence_required`, `falsifier_required`, `benchmark_spec_required_before_execution`; no Replay PASS claim.
- [ ] Implement provider-leak guard rejecting semantic keys such as `wind_field`, `wind_code`, `bloomberg_field` or other provider-native identifiers. Explanatory prose may state providers are deferred adapters, but providers do not define canonical inputs.
- [ ] GREEN tests and commit `feat(rios): add genesis orchestration pack`.

---

### Task 4: E / Market Clock semantic-gap hardening without Registry admission

**Files:** Modify Matrix, tests, validator.

- [ ] RED tests require every `new_candidate` row to provide `semantic_gap_statement`, `why_existing_mothers_are_insufficient`, `required_dependency_types`, and `candidate_readiness`.
- [ ] Candidate readiness is one of `identity_candidate_only | schema_dependencies_complete_candidate | not_justified`.
- [ ] Duplicate-scan all physical capability packs. `CAP-E-001-EVIDENCE-AUTHORITY-VALIDATION` and preferred CROSS identity must be unused; otherwise select the next unused legal ID before proceeding.
- [ ] Registry readiness must verify existing governed dependencies: at least one Theory, one Hypothesis, one Factor or Algorithm, one Benchmark, one CanonicalDataField, valid output contract, provider independence, and both prohibition flags.
- [ ] Do not weaken `research-capability.schema.json` and do not create stub dependencies to manufacture readiness.
- [ ] Expected legitimate result: identity may be accepted while Registry apply remains deferred.
- [ ] GREEN tests and commit `feat(rios): harden genesis capability gap analysis`.

---

### Task 5: Full validator, scope guard, and machine-ready State

**Files:** Modify validator, tests, State.

- [ ] Add RED full-pack test requiring `genesis_count=10`, `registry_mutations=0`, `next_gate=RIOS_0_1_C_HUMAN_REVIEW`.
- [ ] Implement PR changed-path detection using `git diff --name-only origin/$GITHUB_BASE_REF...HEAD`.
- [ ] Pre-Human prohibit `registry/`, `canon/`, `runtime/`, and any modification of `packages/contracts/schemas/research-capability.schema.json`.
- [ ] Full validator checks exact coverage, classification legality, referential integrity, duplicate candidate IDs, candidate-gap rationale, non-authorities, provider neutrality, no scalar scores, State consistency, and zero pre-Human Registry mutation.
- [ ] Advance State only after full local GREEN:

```json
{
  "status": "candidate_ready_for_human_review",
  "next_gate": "RIOS_0_1_C_HUMAN_REVIEW",
  "registry_mutation_authority": "none",
  "benchmark_execution_authority": "none",
  "runtime_authority": "none",
  "trading_authority": "none"
}
```

- [ ] Run:

```bash
python scripts/validate_rios_0_1_c_capability_registry.py
python scripts/validate_r1_registry.py
python scripts/validate_r2_gold_pack.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] Commit `feat(rios): close 0.1-c machine governance gate`.

---

### Task 6: CI integration and Draft PR qualification

**Files:** Modify `.github/workflows/ci.yml` and tests.

- [ ] RED test asserts exact command `python scripts/validate_rios_0_1_c_capability_registry.py` occurs once in CI.
- [ ] Confirm RED.
- [ ] Add RIOS validator after current architecture/governance validators and before full unit tests. Preserve every concurrent main gate; never replace the workflow wholesale from the old design snapshot.
- [ ] Run targeted and full unit tests; commit `ci(rios): add capability convergence gate`.
- [ ] Open Draft PR titled `RIOS-0.1-C: converge Genesis Pack onto ResearchCapability Registry`.
- [ ] PR metadata states Registry mutations 0, Canon promotions 0, Benchmark executions 0, Runtime authority 0, Trading authority 0, Human gate pending.
- [ ] Obtain exact-head protected `contracts=success` and `governance=success`. Record CI facts in PR metadata without recursively changing State to record the same head.

---

### Task 7: Human Review Card and Human Gate

**Files:** Create Human Review Card; modify validator/tests; State only if needed before final head.

Allowed dispositions:
`reuse_confirmed | composite_confirmed | profile_confirmed | new_candidate_identity_accepted_registry_deferred | new_candidate_ready_for_registry_apply | revise | reject`.

- [ ] Human Review Card has one section per Genesis concept with classification, dependencies, overlap, mother-vs-profile/composite rationale, Replay prerequisites, authority boundary, and recommended disposition.
- [ ] E and Market Clock receive explicit semantic-necessity review. Market Clock defaults to deferred identity or composite unless irreducible CROSS semantics are demonstrated.
- [ ] Validator requires all ten concepts and reserved token `ACCEPT_RIOS_0_1_C_CAPABILITY_CONVERGENCE_AND_GOVERNANCE`.
- [ ] Run full local qualification and push final review head.
- [ ] Obtain fresh exact-head `contracts` + `governance` PASS.
- [ ] STOP and request exactly `ACCEPT_RIOS_0_1_C_CAPABILITY_CONVERGENCE_AND_GOVERNANCE`.
- [ ] Do not create Acceptance Receipt or modify Registry before that token.

---

### Task 8: Conditional Human Acceptance and post-acceptance qualification

**Condition:** Execute only after the exact Human token from Task 7.

**Files:** Create Human Acceptance Receipt; modify validator/tests/State.

- [ ] Create Receipt while State remains Human-review-ready. The executor must copy the exact 40-character Human-reviewed PR head SHA and exact reviewed CI run number/run ID verbatim from GitHub metadata at execution time. Those runtime facts are not pre-filled in this plan.
- [ ] Receipt fixes decision token and records reviewed CI as `conclusion=success`, `contracts=success`, `governance=success`; it also records `registry_apply_authorized=false`, `merge_authorized=false`, `benchmark_execution_authorized=false`, `runtime_authorized=false`, `trading_authorized=false`.
- [ ] TDD receipt validator rejects wrong token, wrong reviewed SHA/run binding, or any higher authority set true.
- [ ] Obtain post-acceptance exact-head CI.
- [ ] Only after PASS advance State to `status=human_accepted_ready_for_apply_plan`, `next_gate=RIOS_0_1_C_APPLY_AUTHORITY`, `registry_mutation_authority=not_implied_by_acceptance`.
- [ ] Obtain another exact-head qualification and STOP.
- [ ] If zero new identities are Registry-ready, request only convergence-artifact merge authority. If any are `new_candidate_ready_for_registry_apply`, show the exact dependency-complete list and request a separate Registry-apply authority. Never infer apply authority from Human Acceptance.

---

### Task 9: Conditional governed Registry apply

**Condition:** Execute only after separate explicit Registry-apply authority. This task is skipped if all new identities remain deferred.

**Files:** Optional new candidate pack, capability index, global Registry index, apply receipt, apply-specific validator/tests.

- [ ] RED tests freeze exactly the separately authorized candidate IDs and require dependency closure.
- [ ] Confirm RED because authorized candidate pack is absent.
- [ ] Materialize only dependency-complete authorized `ResearchCapability` objects. Validate each with unchanged `research-capability.schema.json`.
- [ ] Every Theory/Hypothesis/Factor-or-Algorithm/Benchmark/DataField reference must already resolve. No stub dependencies may be invented to make schema validation pass.
- [ ] Read fresh Registry counts and increment arithmetically by actual admitted capabilities only. Keep `canon_entry_count=0`; RIOS-0.1-C has no Canon promotion authority.
- [ ] Run R1, R2, RIOS validators and all unit tests.
- [ ] Obtain exact-head protected CI and create an immutable Registry Apply Receipt.
- [ ] Stop for separate merge authority. Registry apply never authorizes Benchmark execution, Runtime, portfolio actions, or Trading.

## Final Verification

Before declaring RIOS-0.1-C complete, on the final candidate head run:

```bash
python scripts/validate_r1_registry.py
python scripts/validate_r2_gold_pack.py
python scripts/validate_rios_0_1_c_capability_registry.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Then require GitHub exact-head:

```text
contracts = success
governance = success
```

Audit changed paths against fresh main. Before Human Acceptance, Registry changes must be zero. After a separately authorized apply, Registry changes must be limited exactly to the authorized capability pack/index changes; `canon/**`, provider/runtime/live-execution paths remain unchanged.

RIOS-0.1-C is complete when all ten Genesis concepts have explicit Human dispositions, convergence/orchestration artifacts are accepted and merged, and every possible Registry mutation is either separately applied with dependency closure or explicitly deferred. `RIOS-0.2｜Capability Replay Engine Bootstrap` does not start automatically.
