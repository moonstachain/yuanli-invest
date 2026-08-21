# RIOS-0.1-C Capability Registry Materialization & Governance Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Materialize the ten RIOS Genesis concepts as a governed convergence/orchestration layer over the existing R1/R2 ResearchCapability system, prove exact coverage and authority boundaries in CI, and stop at Human Review before any formal Registry mutation.

**Architecture:** RIOS-0.1-C does not create a second Registry or replace existing ResearchCapability identities. It creates an architecture-level convergence matrix and Genesis orchestration manifest under `docs/architecture/rios/0.1-c/`, validates them against the existing R1/R2 capability graph, and permits later Registry apply only for Human-accepted genuine semantic gaps whose dependencies satisfy the existing schema.

**Tech Stack:** Python 3.12, stdlib `json` / `pathlib` / `subprocess`, `jsonschema==4.25.1`, `unittest`, GitHub Actions `repository-gates`.

**Spec:** `docs/superpowers/specs/2026-08-21-rios-0-1-c-capability-registry-materialization-governance-gate-design.md`

## Global Constraints

- Do not create a parallel `/capabilities/registry.yaml`, alternate Capability schema, or tenth Registry namespace.
- Preserve the existing `ResearchCapability` schema and ID pattern `^CAP-(P|N|XS|XA|XP|V|S|E|CROSS)-[0-9]{3}-[A-Z0-9-]+$`.
- Preserve lifecycle `concept → specified → implemented → replicated → benchmark_passed → shadow_qualified → canon → deprecated`.
- Pre-Human phase must not modify `registry/**`, `canon/**`, provider/runtime/live-execution code, or existing R1/R2 capability identities.
- Provider Independence remains mandatory; Wind/provider-specific field semantics must not enter capability identity.
- Scalar PNX/Force scores are prohibited.
- Target price, buy/sell signal, recommended weight, target weight, position size, broker action, and live execution are prohibited.
- CI validates structure/governance only; it does not establish investment validity, evidence truth, benchmark success, or trading authority.
- Human Acceptance does not imply merge or Registry mutation.
- Current repository baseline observed at design time: `main@bd8931e1bf21dceb5e34a68ec41aa199b83e9410`, Registry total `99`, Capability Registry active count `12`, Canon count `0`, Provider count `0`.
- Before execution, re-read `main` and perform base-drift audit; never overwrite concurrent changes.

---

## File Map

**Create in pre-Human implementation:**
- `docs/architecture/rios/0.1-c/RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json` — exactly ten Genesis rows and classification decisions.
- `docs/architecture/rios/0.1-c/RIOS-0.1-C-GENESIS-PACK-v0.1.json` — orchestration manifest, Agent routing hints, Replay prerequisites, explicit non-authorities.
- `docs/architecture/rios/0.1-c/RIOS-0.1-C-STATE.json` — governed state projection.
- `docs/architecture/rios/0.1-c/RIOS-0.1-C-HUMAN-REVIEW-CARD-v0.1.md` — epistemic/architecture review surface.
- `scripts/validate_rios_0_1_c_capability_registry.py` — fail-closed structural/governance validator.
- `tests/test_rios_0_1_c_capability_registry.py` — TDD and negative-authority tests.

**Modify in pre-Human implementation:**
- `.github/workflows/ci.yml` — add RIOS-0.1-C validator immediately before full unit tests.

**Conditional post-Human files only if separately authorized:**
- `docs/architecture/rios/0.1-c/RIOS-0.1-C-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json`
- optional candidate pack under `registry/capabilities/` only when Human disposition is `new_candidate_ready_for_registry_apply` and every referenced dependency already exists.
- `registry/capabilities/_index.json` and `registry/registry-index.json` only in the separately governed apply phase.

---

### Task 1: Isolated implementation branch, base-drift audit, and RED validator skeleton

**Files:**
- Create: `tests/test_rios_0_1_c_capability_registry.py`
- Create later in task: `scripts/validate_rios_0_1_c_capability_registry.py`
- Create later in task: `docs/architecture/rios/0.1-c/RIOS-0.1-C-STATE.json`

**Interfaces:**
- Produces validator primitives: `assert_exact_genesis_ids(rows)`, `assert_classification(row)`, `assert_non_authority(obj)`, `assert_pre_human_scope(paths)`, `validate_rios_0_1_c(root)`.
- `validate_rios_0_1_c(root: Path) -> dict` returns at least `genesis_count`, `new_candidate_count`, `registry_mutations`, `next_gate`.

- [ ] **Step 1: Create isolated execution branch/worktree from fresh main**

Use `superpowers:using-git-worktrees` when local worktrees are available. Otherwise create a dedicated GitHub branch from the fresh main SHA. Before branching, compare current main with design base `bd8931e1bf21dceb5e34a68ec41aa199b83e9410`; if newer commits touch `registry/**`, `.github/workflows/ci.yml`, R1/R2 capability schemas, or `docs/architecture/rios/`, audit and preserve them.

- [ ] **Step 2: Run baseline gates**

```bash
python scripts/validate_r1_registry.py
python scripts/validate_r2_gold_pack.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS before RIOS changes.

- [ ] **Step 3: Write the first failing tests**

```python
import unittest
from pathlib import Path

from scripts.validate_rios_0_1_c_capability_registry import (
    assert_exact_genesis_ids,
    assert_pre_human_scope,
    validate_rios_0_1_c,
)

ROOT = Path(__file__).resolve().parents[1]

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

class RIOS01CPrimitiveTests(unittest.TestCase):
    def test_exact_genesis_identity(self):
        assert_exact_genesis_ids(EXPECTED_GENESIS_IDS)
        with self.assertRaises(AssertionError):
            assert_exact_genesis_ids(EXPECTED_GENESIS_IDS + ["RIOS-GEN-11-SILENT"])

    def test_pre_human_registry_paths_fail_closed(self):
        assert_pre_human_scope(["docs/architecture/rios/0.1-c/example.json"])
        with self.assertRaises(AssertionError):
            assert_pre_human_scope(["registry/capabilities/new.json"])

    def test_full_pack_is_required(self):
        validate_rios_0_1_c(ROOT)
```

- [ ] **Step 4: Run the targeted test and confirm RED**

```bash
python -m unittest tests.test_rios_0_1_c_capability_registry -v
```

Expected: FAIL because validator/module and artifacts do not yet exist.

- [ ] **Step 5: Add minimal validator primitives and initial State**

Initial state must be:

```json
{
  "stage": "RIOS_0_1_C_CAPABILITY_REGISTRY_MATERIALIZATION_GOVERNANCE_GATE",
  "status": "convergence_compilation_started",
  "design_spec_accepted": true,
  "genesis_concept_count": 10,
  "registry_mutation_authority": "none",
  "benchmark_execution_authority": "none",
  "runtime_authority": "none",
  "trading_authority": "none",
  "next_gate": "RIOS_0_1_C_CONVERGENCE_COMPILATION"
}
```

Implement primitives with fail-closed assertions; `validate_rios_0_1_c` may still fail because matrix/pack are missing.

- [ ] **Step 6: Run targeted tests**

Expected: primitive tests PASS; full-pack test remains RED for missing convergence artifacts.

- [ ] **Step 7: Commit**

```bash
git add tests/test_rios_0_1_c_capability_registry.py scripts/validate_rios_0_1_c_capability_registry.py docs/architecture/rios/0.1-c/RIOS-0.1-C-STATE.json
git commit -m "test(rios): bootstrap 0.1-c convergence gate"
```

---

### Task 2: Compile exact ten-row Capability Convergence Matrix

**Files:**
- Create: `docs/architecture/rios/0.1-c/RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json`
- Modify: `tests/test_rios_0_1_c_capability_registry.py`
- Modify: `scripts/validate_rios_0_1_c_capability_registry.py`

**Interfaces:**
- Matrix row fields: `genesis_id`, `human_name`, `classification`, `canonical_capability_ids`, `candidate_capability_id`, `rationale`, `semantic_overlap_notes`, `authority_boundary`, `registry_mutation_required`, `benchmark_execution_authorized`, `runtime_authorized`, `trading_authorized`.
- Allowed classification: `reuse | composite | profile | new_candidate | reject`.

- [ ] **Step 1: Add failing matrix tests**

Tests must require exactly ten rows, exact ordering/identity set, no duplicates, and require all `benchmark_execution_authorized`, `runtime_authorized`, and `trading_authorized` values to be `false`.

Also freeze these minimum mappings:

```python
EXPECTED_CLASS = {
    "RIOS-GEN-01-AI-INFRASTRUCTURE-REGIME-TRANSITION": "profile",
    "RIOS-GEN-02-ENERGY-BOTTLENECK-CAPTURE": "profile",
    "RIOS-GEN-03-NARRATIVE-DIFFUSION-ENGINE": "composite",
    "RIOS-GEN-04-NARRATIVE-BUBBLE-DETECTION": "composite",
    "RIOS-GEN-05-PLATFORM-WINNER-CAPTURE": "composite",
    "RIOS-GEN-06-CONVEXITY-EXPRESSION-ENGINE": "composite",
    "RIOS-GEN-07-EVIDENCE-AUTHORITY-ENGINE": "new_candidate",
    "RIOS-GEN-08-NARRATIVE-PRICE-GAP": "composite",
    "RIOS-GEN-09-PORTFOLIO-SURVIVAL-ENGINE": "composite",
    "RIOS-GEN-10-MARKET-CLOCK-REGIME-TRANSITION": "new_candidate"
}
```

Market Clock remains a candidate identity subject to Human Review; its row must explicitly state that Human Review may downgrade it to `composite` if semantic-gap evidence is insufficient.

- [ ] **Step 2: Run and verify RED**

Expected: FAIL because matrix file is missing.

- [ ] **Step 3: Create the matrix**

Minimum canonical dependencies:

```text
GEN-01 profile: CAP-P-001, CAP-P-002, CAP-XS-001, CAP-XS-002, CAP-N-001, CAP-N-002, CAP-V-002 if present in current branch; otherwise active V mother capability only.
GEN-02 profile: CAP-P-001, CAP-P-002, CAP-XS-002.
GEN-03 composite: CAP-N-001, CAP-N-002.
GEN-04 composite: CAP-N-002 + active V Price-Implied Expectations capability + CAP-XA-002.
GEN-05 composite: CAP-XS-001, CAP-XS-002.
GEN-06 composite: CAP-XA-001, CAP-XA-002, CAP-XP-001.
GEN-07 new_candidate: candidate ID CAP-E-001-EVIDENCE-AUTHORITY-VALIDATION.
GEN-08 composite: active V Price-Implied Expectations capability; target price prohibited.
GEN-09 composite: CAP-S-001, CAP-S-002 and/or governed S successor identities present on fresh main.
GEN-10 new_candidate: candidate ID must be determined after duplicate scan of all capability pack files; preferred identity CAP-CROSS-002-MARKET-CLOCK-REGIME-TRANSITION only if unused.
```

Do not hard-code stale aliases when fresh main contains a governed successor identity; validator should load actual available capability IDs from all capability pack files and fail on unresolved references.

- [ ] **Step 4: Implement referential checks**

Add `load_available_capability_ids(root)` and require every `canonical_capability_ids` entry to resolve to an existing capability object. Scan all `registry/capabilities/*.json` except `_index.json` so inactive/successor packs are visible for duplicate-ID detection, but do not treat mere physical presence as active Registry admission.

- [ ] **Step 5: Run targeted tests**

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/architecture/rios/0.1-c/RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json tests/test_rios_0_1_c_capability_registry.py scripts/validate_rios_0_1_c_capability_registry.py
git commit -m "feat(rios): compile genesis capability convergence matrix"
```

---

### Task 3: Compile Genesis Orchestration Pack and Agent routing hints

**Files:**
- Create: `docs/architecture/rios/0.1-c/RIOS-0.1-C-GENESIS-PACK-v0.1.json`
- Modify: `tests/test_rios_0_1_c_capability_registry.py`
- Modify: `scripts/validate_rios_0_1_c_capability_registry.py`

**Interfaces:**
- Pack ID: `RIOS-GENESIS-PACK-001`.
- Status: `candidate_orchestration_pack`.
- Agent names are routing labels only: `P_AGENT`, `N_AGENT`, `X_AGENT`, `E_AGENT`, `V_AGENT`, `S_AGENT`, `CHIEF_RESEARCH_COUNCIL`.

- [ ] **Step 1: Add failing pack tests**

Require ten concepts, canonical dependencies matching the matrix, explicit `replay_prerequisites`, and top-level non-authorities:

```json
{
  "registry_admission_authorized": false,
  "benchmark_execution_authorized": false,
  "capability_promotion_authorized": false,
  "runtime_authorized": false,
  "trading_authorized": false
}
```

- [ ] **Step 2: Add prohibited-key negative tests**

For each of `target_price`, `buy_signal`, `sell_signal`, `recommended_weight`, `target_weight`, `position_size`, `broker_action`, `live_execution`, `pnx_score`, `force_score`, mutate a valid pack copy and assert `assert_non_authority()` fails.

- [ ] **Step 3: Run and confirm RED**

Expected: missing pack / authority test failure.

- [ ] **Step 4: Create the Genesis Pack**

Agent routing must reference Genesis concept IDs and canonical capability dependencies; it must not duplicate theory/mechanism semantics inside Agent definitions.

Replay prerequisites should be research-only, e.g. `historical_case_required`, `pit_evidence_required`, `falsifier_required`, `benchmark_spec_required_before_execution`; do not claim Replay PASS.

- [ ] **Step 5: Add provider-leak guard**

Implement `assert_no_provider_semantics(obj)` to reject semantic keys/values that embed provider field namespaces such as `wind_field`, `wind_code`, `bloomberg_field`, or other provider-native identifiers in the Genesis Pack or convergence matrix. Provider names may appear only in explanatory non-semantic prose stating they are deferred adapters; they must not define canonical inputs.

- [ ] **Step 6: Run targeted tests and commit**

```bash
python -m unittest tests.test_rios_0_1_c_capability_registry -v
git add docs/architecture/rios/0.1-c/RIOS-0.1-C-GENESIS-PACK-v0.1.json tests/test_rios_0_1_c_capability_registry.py scripts/validate_rios_0_1_c_capability_registry.py
git commit -m "feat(rios): add genesis orchestration pack"
```

---

### Task 4: Candidate-gap validation for E and Market Clock without Registry admission

**Files:**
- Modify: `docs/architecture/rios/0.1-c/RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json`
- Modify: `tests/test_rios_0_1_c_capability_registry.py`
- Modify: `scripts/validate_rios_0_1_c_capability_registry.py`

**Interfaces:**
- Candidate identity proposal is metadata only; no `ResearchCapability` Registry object is created in this task.
- Candidate readiness enum in matrix rationale metadata: `identity_candidate_only | schema_dependencies_complete_candidate | not_justified`.

- [ ] **Step 1: Add failing tests for semantic-gap rationale**

Require every `new_candidate` row to contain non-empty:

```text
semantic_gap_statement
why_existing_mothers_are_insufficient
required_dependency_types
candidate_readiness
```

- [ ] **Step 2: Add duplicate-ID scan tests**

Collect all physical capability IDs across `registry/capabilities/*.json` and assert proposed IDs are absent. If `CAP-CROSS-002-MARKET-CLOCK-REGIME-TRANSITION` is already occupied on fresh main, select the next unused three-digit CROSS number and update both matrix and tests before continuing.

- [ ] **Step 3: Add schema-dependency test logic**

For a proposed `ResearchCapability`, Registry readiness requires all of:

```text
>=1 TheoryObject
>=1 HypothesisObject
>=1 FactorObject OR >=1 AlgorithmObject
>=1 BenchmarkObject
>=1 CanonicalDataField
valid output_contract
provider_independent=true
scalar_pnx_score_prohibited=true
investment_action_fields_prohibited=true
```

The pre-Human artifacts may conclude `identity_candidate_only` when these dependencies do not yet exist. Do not weaken `research-capability.schema.json`.

- [ ] **Step 4: Run tests and update matrix rationale**

Expected: E and Market Clock are likely identity candidates with Registry apply deferred unless existing governed dependencies already satisfy the schema at execution time.

- [ ] **Step 5: Commit**

```bash
git add docs/architecture/rios/0.1-c/RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json tests/test_rios_0_1_c_capability_registry.py scripts/validate_rios_0_1_c_capability_registry.py
git commit -m "feat(rios): harden genesis capability gap analysis"
```

---

### Task 5: Full validator, branch-scope guard, and State transition

**Files:**
- Modify: `scripts/validate_rios_0_1_c_capability_registry.py`
- Modify: `tests/test_rios_0_1_c_capability_registry.py`
- Modify: `docs/architecture/rios/0.1-c/RIOS-0.1-C-STATE.json`

**Interfaces:**
- `validate_rios_0_1_c(root)` validates Matrix + Pack + fresh existing Registry references + state + pre-Human changed paths.

- [ ] **Step 1: Add full-pack failing tests**

```python
class RIOS01CFullPackTests(unittest.TestCase):
    def test_full_pack_validates(self):
        result = validate_rios_0_1_c(ROOT)
        self.assertEqual(result["genesis_count"], 10)
        self.assertEqual(result["registry_mutations"], 0)
        self.assertEqual(result["next_gate"], "RIOS_0_1_C_HUMAN_REVIEW")
```

- [ ] **Step 2: Implement Git PR scope detection**

Use the QXM2 pattern:

```python
base_ref = os.environ.get("GITHUB_BASE_REF")
subprocess.run(
    ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"],
    ...
)
```

Pre-Human prohibited prefixes:

```python
(
    "registry/",
    "canon/",
    "runtime/",
)
```

Also reject modifications to `packages/contracts/schemas/research-capability.schema.json` in this stage.

- [ ] **Step 3: Implement full validation**

Validate exact ten Genesis identities, classifications, referential integrity, candidate duplicate scan, non-authorities, provider neutrality, no scalar scores, no Registry mutation, and State consistency.

- [ ] **Step 4: Advance State**

After local full validator and unit tests pass, set:

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

- [ ] **Step 5: Run local gates**

```bash
python scripts/validate_rios_0_1_c_capability_registry.py
python scripts/validate_r1_registry.py
python scripts/validate_r2_gold_pack.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_rios_0_1_c_capability_registry.py tests/test_rios_0_1_c_capability_registry.py docs/architecture/rios/0.1-c/RIOS-0.1-C-STATE.json
git commit -m "feat(rios): close 0.1-c machine governance gate"
```

---

### Task 6: CI integration and Draft PR machine qualification

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- CI step: `python scripts/validate_rios_0_1_c_capability_registry.py`.

- [ ] **Step 1: Add a test that CI references the validator**

In `tests/test_rios_0_1_c_capability_registry.py`, read `.github/workflows/ci.yml` and assert the exact command exists once.

- [ ] **Step 2: Run test and confirm RED**

Expected: FAIL because CI does not yet contain the RIOS gate.

- [ ] **Step 3: Add CI step**

Insert after the latest architecture/governance validators and before:

```yaml
- run: python -m unittest discover -s tests -p 'test_*.py' -v
```

Add:

```yaml
- run: python scripts/validate_rios_0_1_c_capability_registry.py
```

Preserve all concurrent gates on fresh main; never replace the workflow wholesale with the design-branch snapshot.

- [ ] **Step 4: Run local tests and commit**

```bash
python -m unittest tests.test_rios_0_1_c_capability_registry -v
python -m unittest discover -s tests -p 'test_*.py' -v
git add .github/workflows/ci.yml tests/test_rios_0_1_c_capability_registry.py
git commit -m "ci(rios): add capability convergence gate"
```

- [ ] **Step 5: Open Draft PR**

Title:

`RIOS-0.1-C: converge Genesis Pack onto ResearchCapability Registry`

PR body must state:

```text
Registry mutations: 0
Canon promotions: 0
Benchmark executions: 0
Runtime authority: 0
Trading authority: 0
Human gate: pending
```

- [ ] **Step 6: Obtain exact-head repository-gates**

Require both protected jobs `contracts=success` and `governance=success`. Record run number/id and exact head in PR metadata, not by recursively editing State after every CI run.

---

### Task 7: Human Review Card and Human Gate

**Files:**
- Create: `docs/architecture/rios/0.1-c/RIOS-0.1-C-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `docs/architecture/rios/0.1-c/RIOS-0.1-C-STATE.json` only if needed before the final exact-head run.

**Interfaces:**
- Allowed dispositions: `reuse_confirmed`, `composite_confirmed`, `profile_confirmed`, `new_candidate_identity_accepted_registry_deferred`, `new_candidate_ready_for_registry_apply`, `revise`, `reject`.

- [ ] **Step 1: Write Human Review Card**

For each of the ten Genesis concepts include:

```text
Genesis ID
Current classification
Canonical dependencies
Semantic overlap
Why this is/is not a new mother capability
Replay prerequisites
Authority boundary
Recommended Human disposition
```

E and Market Clock must receive explicit scrutiny for semantic necessity. Market Clock should default to `new_candidate_identity_accepted_registry_deferred` or downgrade to `composite_confirmed` unless a genuine irreducible CROSS semantic is demonstrated.

- [ ] **Step 2: Add validator checks for the Review Card**

Require all ten rows appear, all allowed dispositions are legal, and the reserved token appears exactly:

`ACCEPT_RIOS_0_1_C_CAPABILITY_CONVERGENCE_AND_GOVERNANCE`

- [ ] **Step 3: Run full local qualification and push final review head**

- [ ] **Step 4: Obtain fresh exact-head `contracts` + `governance` PASS**

- [ ] **Step 5: STOP at Human Gate**

Request exactly:

`ACCEPT_RIOS_0_1_C_CAPABILITY_CONVERGENCE_AND_GOVERNANCE`

Do not create Acceptance Receipt or modify Registry before the user supplies the token.

---

### Task 8: Conditional Human Acceptance Receipt and post-acceptance qualification

**Condition:** Execute only after the exact Human token above.

**Files:**
- Create: `docs/architecture/rios/0.1-c/RIOS-0.1-C-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json`
- Modify: `scripts/validate_rios_0_1_c_capability_registry.py`
- Modify: `tests/test_rios_0_1_c_capability_registry.py`
- Modify: `docs/architecture/rios/0.1-c/RIOS-0.1-C-STATE.json`

**Interfaces:**
- Receipt binds the reviewed exact head and reviewed CI.
- Acceptance does not imply merge or Registry apply.

- [ ] **Step 1: Create Acceptance Receipt while State remains Human-review-ready**

Receipt must include:

```json
{
  "decision": "ACCEPT_RIOS_0_1_C_CAPABILITY_CONVERGENCE_AND_GOVERNANCE",
  "reviewed_head_sha": "<copy the exact reviewed SHA from GitHub metadata at execution time>",
  "reviewed_ci": {
    "conclusion": "success",
    "contracts": "success",
    "governance": "success"
  },
  "registry_apply_authorized": false,
  "merge_authorized": false,
  "benchmark_execution_authorized": false,
  "runtime_authorized": false,
  "trading_authorized": false
}
```

The executor must substitute the actual GitHub SHA/run facts; do not pre-fill them in source before the reviewed run exists.

- [ ] **Step 2: Add TDD receipt validation**

Require exact token, exact reviewed SHA/run binding, and all higher authorities false.

- [ ] **Step 3: Obtain post-acceptance exact-head CI**

- [ ] **Step 4: Advance State only after PASS**

Set:

```json
{
  "status": "human_accepted_ready_for_apply_plan",
  "next_gate": "RIOS_0_1_C_APPLY_AUTHORITY",
  "registry_mutation_authority": "not_implied_by_acceptance"
}
```

- [ ] **Step 5: Run another exact-head qualification and STOP**

If Human Review accepted zero Registry-ready new identities, request only merge authority for the convergence artifacts. If one or more identities are `new_candidate_ready_for_registry_apply`, present the exact dependency-complete candidate list and request a separate Registry-apply authority. Never infer it from Human Acceptance.

---

### Task 9: Conditional governed Registry apply for dependency-complete new candidates

**Condition:** Execute only with a separate explicit apply authority defined after Task 8 review. This task may legitimately be skipped if all new identities are deferred.

**Files:**
- Create only if authorized: `registry/capabilities/rios-0-1-c-new-candidates-v0.1.json`
- Modify only if authorized: `registry/capabilities/_index.json`
- Modify only if authorized: `registry/registry-index.json`
- Create: `docs/architecture/rios/0.1-c/RIOS-0.1-C-REGISTRY-APPLY-RECEIPT-v0.1.json`
- Add apply-specific validator/tests.

**Interfaces:**
- Every object must validate against `packages/contracts/schemas/research-capability.schema.json`.
- Every referenced Theory/Hypothesis/Factor-or-Algorithm/Benchmark/DataField must already resolve in the corresponding Registry.

- [ ] **Step 1: Write RED tests for exact authorized IDs and dependency closure**

- [ ] **Step 2: Confirm RED because candidate pack is absent**

- [ ] **Step 3: Materialize only authorized dependency-complete candidates**

Do not create stub Theory/Hypothesis/Benchmark/Field objects merely to make the Capability schema pass. If dependencies are incomplete, keep the candidate deferred and do not mutate Registry.

- [ ] **Step 4: Update Registry indexes arithmetically**

Read fresh counts at execution time. Increment only by the actual number of admitted ResearchCapability objects; preserve `canon_entry_count=0` unless a separate Canon gate exists (RIOS-0.1-C does not create one).

- [ ] **Step 5: Run all Registry + RIOS validators**

```bash
python scripts/validate_r1_registry.py
python scripts/validate_r2_gold_pack.py
python scripts/validate_rios_0_1_c_capability_registry.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 6: Exact-head CI, Receipt, separate merge authority**

Registry apply still does not authorize benchmark execution, runtime, portfolio actions, or trading.

---

## Final Verification Before Declaring RIOS-0.1-C Complete

Run on the final candidate head:

```bash
python scripts/validate_r1_registry.py
python scripts/validate_r2_gold_pack.py
python scripts/validate_rios_0_1_c_capability_registry.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Then verify via GitHub exact-head Actions:

```text
contracts = success
governance = success
```

Audit changed paths against fresh main. Before Human Acceptance, changed Registry paths must equal zero. After a separately authorized apply, Registry changes must be limited exactly to the approved capability pack and indexes; `canon/**`, provider/runtime/live-execution paths remain unchanged.

The stage is complete when the ten Genesis concepts have explicit Human dispositions, the convergence/orchestration artifacts are accepted and merged, and any Registry mutation has either been separately applied with dependency closure or explicitly deferred. `RIOS-0.2｜Capability Replay Engine Bootstrap` does not start automatically.
