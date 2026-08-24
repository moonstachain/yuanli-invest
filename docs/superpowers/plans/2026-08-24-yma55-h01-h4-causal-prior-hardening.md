# YMA55 H0.1 → H4 Causal Prior Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the YIM0 lifetime-scope validator so later legitimate programs cannot poison YIM0 CI, then implement the first YMA55-H4 reference runtime and a controlled Duration × Credit × Scarcity Gold/Hard-Negative replay pack that exercises the accepted H1/H2/H3 contracts without creating capital authority.

**Architecture:** H0.1 freezes YIM0 scope against its own accepted semantic merge rather than current repository HEAD while continuing to validate current YIM0 authority/state artifacts. H4 adds a stdlib-only `research_runtime.yma55` package with explicit five-layer objects, competing-mechanism sets, transferability assessment, prior-violation evaluation, immutable replay fixtures, and deterministic validators. Historical fixtures remain research candidates: T0 inputs and settlement are physically separated; evidence status is explicit; no historical analogy can directly create a trade action.

**Tech Stack:** Python 3.12 stdlib, `unittest`, existing GitHub Actions `repository-gates`, immutable JSON fixtures.

**Spec:** `docs/architecture/yma55/YMA55-H1-FIVE-LAYER-DECISION-KERNEL-FREEZE-v0.1.md`, `YMA55-H2-COMPETING-MECHANISM-NULL-HYPOTHESIS-CONTRACT-v0.1.md`, `YMA55-H3-TRANSFERABILITY-PRIOR-VIOLATION-ENGINE-v0.1.md`.

## Global Constraints

- Human kernel is exactly `WORLD → CONSTRAINT → TRANSMISSION → MECHANISM → SETTLEMENT`.
- `HumanKernel != MachineOntology`.
- `HistoricalEpoch != MacroRealityState`.
- `MacroReturnMechanism != ReturnEngine`; YMA55 MRM families do not mutate ME0 ENG-C/R/X authority.
- Every material H4 replay carries exactly one primary, one to three genuine alternatives, and exactly one null.
- H2 discrimination expectations are frozen at T0; settlement cannot rewrite them.
- `HistoricalValidity != CurrentTransferability`.
- `Surprise != PriorViolation`.
- `PriorViolation` updates research state only; it cannot emit buy/sell/hold, target weight, position size, or execution actions.
- `ClaimAuthority <= EvidenceAuthority` and `FalsifierBeforeConviction = true`.
- `RealitySettlement = final epistemic authority`.
- H4 remains reference/shadow research. No Canon promotion, Engine Registry mutation, Portfolio authority, sizing, trading, live execution, Constitution mutation, or merge authority is implied.

---

### Task 1: YMA55-H0.1 — YIM0 Validator Lifetime Scope Repair

**Files:**
- Modify: `tests/test_yim0_methodology_projection.py`
- Modify: `scripts/validate_yim0_methodology_projection.py`
- Create: `docs/architecture/yma55/YMA55-H0.1-YIM0-VALIDATOR-LIFETIME-SCOPE-REPAIR-v0.1.md`

**Interfaces:**
- Consumes: current `YIM0-STATE.json` including `semantic_merge_commit`.
- Produces: `scope_end_ref_for_state(state: dict) -> str` and `changed_paths_from_git(end_ref: str) -> list[str]`.

- [ ] **Step 1: Write failing regression tests**

Add tests that require merged YIM0 state to freeze scope at its recorded semantic merge commit and candidate state to use `HEAD`:

```python
def test_scope_end_ref_freezes_merged_yim0_at_semantic_merge():
    state = load(ROOT / "docs/architecture/yim0/YIM0-STATE.json")
    self.assertEqual(yim0.scope_end_ref_for_state(state), state["semantic_merge_commit"])


def test_scope_end_ref_uses_head_before_semantic_merge():
    self.assertEqual(yim0.scope_end_ref_for_state({"status": "candidate"}), "HEAD")
```

Also patch `subprocess.run` and assert `changed_paths_from_git("abc123")` invokes `git diff --name-only BASE_SHA...abc123`, not `BASE_SHA...HEAD`.

- [ ] **Step 2: Verify RED in CI**

Run: `python -m unittest tests.test_yim0_methodology_projection.YIM0ValidatorTests -v`
Expected: FAIL because `scope_end_ref_for_state` does not exist and `changed_paths_from_git` has no `end_ref` parameter.

- [ ] **Step 3: Implement the minimal lifetime-scope fix**

```python
def scope_end_ref_for_state(state: dict) -> str:
    semantic_merge_commit = state.get("semantic_merge_commit")
    return semantic_merge_commit if semantic_merge_commit else "HEAD"


def changed_paths_from_git(end_ref: str = "HEAD") -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{BASE_SHA}...{end_ref}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
```

In `main()`, replace `validate_scope_paths(changed_paths_from_git())` with:

```python
scope_end_ref = scope_end_ref_for_state(yim0_state)
validate_scope_paths(changed_paths_from_git(scope_end_ref))
```

No other YIM0 semantic rule changes.

- [ ] **Step 4: Run focused tests**

Run: `python -m unittest tests.test_yim0_methodology_projection -v`
Expected: PASS.

- [ ] **Step 5: Run the previously failing validator directly**

Run: `python scripts/validate_yim0_methodology_projection.py`
Expected: `YIM0 methodology projection validation: PASS` even when later YMA55 files exist.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_yim0_methodology_projection.py tests/test_yim0_methodology_projection.py docs/architecture/yma55/YMA55-H0.1-YIM0-VALIDATOR-LIFETIME-SCOPE-REPAIR-v0.1.md
git commit -m "fix(yim0): freeze validator scope at semantic merge"
```

---

### Task 2: H4 Reference Runtime Types and Fail-Closed Contract

**Files:**
- Create: `research_runtime/yma55/__init__.py`
- Create: `research_runtime/yma55/types.py`
- Create: `research_runtime/yma55/validation.py`
- Create: `tests/test_yma55_h4_contract.py`

**Interfaces:**
- Produces immutable dataclasses `WorldState`, `StructuralConstraint`, `TransmissionState`, `MechanismHypothesis`, `MechanismHypothesisSet`, `TransferabilityAssessment`, `PriorViolationRecord`, `RealitySettlement`.
- Produces validators `validate_hypothesis_set()`, `validate_transferability()`, `assert_no_capital_outputs()`.

- [ ] **Step 1: Write failing contract tests**

Required tests:

```python
def test_human_kernel_is_exactly_five_layers():
    assert HUMAN_KERNEL == ("WORLD", "CONSTRAINT", "TRANSMISSION", "MECHANISM", "SETTLEMENT")


def test_hypothesis_set_requires_primary_alternative_and_null():
    with pytest_or_unittest_value_error():
        validate_hypothesis_set(invalid_without_null)


def test_capital_outputs_are_prohibited():
    with pytest_or_unittest_value_error():
        assert_no_capital_outputs({"position_size": 0.10})
```

Use `unittest`; no pytest dependency is introduced.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_yma55_h4_contract -v`
Expected: FAIL because `research_runtime.yma55` does not exist.

- [ ] **Step 3: Implement minimal immutable types and validation**

Validation must enforce:

- exactly one primary;
- `1..3` alternatives;
- exactly one null;
- primary/alternatives each have causal chain, expected observables, falsifiers, breaker and evidence refs;
- normal causal-chain node count `<= 6` unless `complexity_exception` is explicit;
- transferability dimensions exactly cover monetary regime, fiscal capacity, market structure, global order, policy toolkit;
- blocking mismatch forces `NON_TRANSFERABLE`;
- prohibited capital fields are rejected.

- [ ] **Step 4: Run contract tests**

Run: `python -m unittest tests.test_yma55_h4_contract -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add research_runtime/yma55 tests/test_yma55_h4_contract.py
git commit -m "feat(yma55): add H4 causal-prior reference contracts"
```

---

### Task 3: Prior Violation Evaluator

**Files:**
- Create: `research_runtime/yma55/prior_violation.py`
- Create: `tests/test_yma55_prior_violation.py`

**Interfaces:**
- `evaluate_prior_violation(transferability, hypothesis_set, observations, as_of) -> PriorViolationRecord`.

- [ ] **Step 1: Write failing behavior tests**

Cover:

1. missing PIT-frozen observables → `NOT_EVALUABLE`;
2. unexpected timing compatible with mechanism → Surprise / no breaker;
3. opposite required sign → `SIGN_VIOLATION`;
4. wrong cross-asset order → `SEQUENCE_VIOLATION`;
5. required policy response outside feasible set → `POLICY_REACTION_VIOLATION`;
6. required confirmation sensor missing after declared window → `CROSS_ASSET_CONFIRMATION_VIOLATION`;
7. violation produces research response only and never a trade action.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_yma55_prior_violation -v`
Expected: FAIL because evaluator is absent.

- [ ] **Step 3: Implement deterministic qualitative evaluator**

No numeric Bayesian probability. Allowed effects are exactly H3: `NO_CHANGE`, `MODEST_DOWNGRADE`, `MAJOR_DOWNGRADE`, `PRIMARY_BREAK`, `SHIFT_TO_ALTERNATIVE_REVIEW`, `SHIFT_TO_NULL_REVIEW`.

- [ ] **Step 4: Run tests**

Run: `python -m unittest tests.test_yma55_prior_violation -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add research_runtime/yma55/prior_violation.py tests/test_yma55_prior_violation.py
git commit -m "feat(yma55): add qualitative prior-violation evaluator"
```

---

### Task 4: Controlled Genesis Replay Pack — Duration × Credit × Scarcity

**Files:**
- Create: `fixtures/replay/yma55_h4/duration/*.json`
- Create: `fixtures/replay/yma55_h4/credit/*.json`
- Create: `fixtures/replay/yma55_h4/scarcity/*.json`
- Create: `fixtures/replay/yma55_h4/manifest.json`
- Create: `research_runtime/yma55/replay.py`
- Create: `tests/test_yma55_h4_replay.py`

**Interfaces:**
- `load_replay_case(path) -> dict`
- `run_replay_case(case) -> dict`
- 12 cases exactly: 3 mechanism families × (`GOLD`, `NEAR_MISS`, `WRONG_MECHANISM`, `WRONG_STRIKE`).

- [ ] **Step 1: Write failing manifest and leakage tests**

```python
def test_manifest_has_exact_three_by_four_matrix():
    manifest = load_manifest()
    assert set(manifest["mechanisms"]) == {"MRM-D", "MRM-CR", "MRM-SC"}
    for mechanism in manifest["mechanisms"].values():
        assert set(mechanism["case_types"]) == {"GOLD", "NEAR_MISS", "WRONG_MECHANISM", "WRONG_STRIKE"}


def test_settlement_is_not_visible_to_t0_runner():
    case = load_case(...)
    result = run_replay_case(case)
    assert "settlement" not in result["runner_input"]
```

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_yma55_h4_replay -v`
Expected: FAIL because manifest/replay runtime is absent.

- [ ] **Step 3: Create 12 immutable candidate fixtures**

Each fixture must contain:

```json
{
  "episode_id": "...",
  "mechanism_family": "MRM-D|MRM-CR|MRM-SC",
  "case_type": "GOLD|NEAR_MISS|WRONG_MECHANISM|WRONG_STRIKE",
  "as_of": "YYYY-MM-DD",
  "evidence_cutoff": "...",
  "evidence_status": "hydrated|partial|needs_primary_hydration",
  "t0": {
    "world": {},
    "constraint": {},
    "transmission": {},
    "hypothesis_set": {},
    "transferability_template": {}
  },
  "settlement": {
    "outcome_class": "...",
    "mechanism_resolution": "...",
    "expression_resolution": "...",
    "notes": "..."
  }
}
```

Fixtures with insufficient source support must say `needs_primary_hydration`; they must not fabricate evidence references or claim Gold authority.

- [ ] **Step 4: Implement replay isolation**

`run_replay_case()` passes only `t0` plus PIT metadata into the evaluators. Settlement is loaded only after research-state output is frozen.

- [ ] **Step 5: Run replay tests**

Run: `python -m unittest tests.test_yma55_h4_replay -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add fixtures/replay/yma55_h4 research_runtime/yma55/replay.py tests/test_yma55_h4_replay.py
git commit -m "feat(yma55): add controlled three-mechanism replay pack"
```

---

### Task 5: H4 Validator, Benchmark Receipt, and Governance State

**Files:**
- Create: `scripts/validate_yma55_h4_reference.py`
- Create: `tests/test_yma55_h4_validator.py`
- Create: `docs/architecture/yma55/YMA55-H4-REFERENCE-IMPLEMENTATION-REPLAY-REPORT-v0.1.md`
- Create: `docs/architecture/yma55/YMA55-H4-STATE.json`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Validator checks all H1/H2/H3 invariants, exact 12-case matrix, PIT leakage guard, evidence-status honesty, no capital outputs, and replay resolution taxonomy.

- [ ] **Step 1: Write failing validator tests**

Hard negatives must include at least:

1. missing null → FAIL;
2. zero alternatives → FAIL;
3. settlement field in runner input → FAIL;
4. `NON_TRANSFERABLE` ignored → FAIL;
5. `PriorViolation → Sell` field → FAIL;
6. historical `needs_primary_hydration` fixture labeled Gold-qualified → FAIL;
7. wrong-mechanism lucky outcome scored epistemically correct → FAIL;
8. unresolved case forcibly resolved → FAIL.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_yma55_h4_validator -v`
Expected: FAIL because validator is absent.

- [ ] **Step 3: Implement validator and CI gate**

Add `python scripts/validate_yma55_h4_reference.py` after `validate_yim0_methodology_projection.py` and before full unittest discovery.

- [ ] **Step 4: Generate deterministic report/state**

State must remain `reference_candidate` until machine qualification and human review. `implementation_authorized=true` reflects this user authorization only; `merge_authorized=false`, `canon_promotion=false`, `portfolio=false`, `trading=false`.

- [ ] **Step 5: Run full verification**

Run in order:

```bash
python scripts/validate_yim0_methodology_projection.py
python scripts/validate_yma55_h4_reference.py
python -m unittest tests.test_yim0_methodology_projection -v
python -m unittest tests.test_yma55_h4_contract -v
python -m unittest tests.test_yma55_prior_violation -v
python -m unittest tests.test_yma55_h4_replay -v
python -m unittest tests.test_yma55_h4_validator -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all commands exit 0.

- [ ] **Step 6: Commit and stop at Draft PR / Human Review**

Do not merge. Update PR #57 to describe H0.1 repair + H4 reference implementation and report exact-head CI status. Any merge requires a separate explicit authorization.
