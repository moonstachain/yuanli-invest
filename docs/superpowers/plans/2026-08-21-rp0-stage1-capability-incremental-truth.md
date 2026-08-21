# RP0 Stage-1 Capability Incremental Truth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the RP0 Stage-1 reality-settlement layer that evaluates whether a ResearchCapability earns independent incremental research value beyond preregistered baselines, without creating a second Replay/Benchmark engine or granting Registry, Canon, production-runtime, portfolio, or trading authority.

**Architecture:** RP0 is an additive layer above the R2.3-B2 runtime. B2 remains the owner of typed `ResearchState` / `ResearchReceipt`, PIT replay, Shadow, Benchmark and Ablation primitives. RP0 adds immutable `RealityTrial` contracts, baseline doctrine, evaluation and complexity accounting, negative-reality learning receipts, five-case manifests, and the `RP0-G1` settlement gate. RP0 must fail closed if B2 primitives are unavailable or incompatible.

**Tech Stack:** Python 3.12 stdlib, `unittest`, existing `jsonschema==4.25.1` dev dependency, GitHub Actions `repository-gates`.

**Spec:** `docs/superpowers/specs/2026-08-21-rp0-stage1-capability-incremental-truth-design.md`

## Global Constraints

- `Research PASS != Capital PASS`.
- `Claim Authority <= Evidence Authority` remains binding.
- RP0 must reuse B2 PIT replay, typed state/receipt, benchmark, and ablation primitives; no second replay or benchmark engine.
- Every trial freezes `Capability × RealityCase × T0 × FrozenEvidence × BaselineSet × SettlementRule`.
- T0 semantics are immutable after preregistration; settlement may append but must never rewrite T0 inputs, baseline definitions, falsifiers, capability version, or evaluation contract.
- Every evaluated Capability must face B0 naive, B1 practitioner, and where applicable B2 component/cheap-proxy baselines.
- Beating B0 alone is insufficient if the best valid preregistered B1 is not beaten.
- No scalar `RP0 score`, `Capability score`, `Force score`, or `PNX score`.
- Allowed Stage-1 dispositions are exactly `PROMOTE_FOR_STAGE2`, `KEEP_SHADOW`, `SIMPLIFY`, `MERGE_INTO_COMPOSITE`, `REJECT_NO_INCREMENT`, `INSUFFICIENT_EVIDENCE`.
- `PROMOTE_FOR_STAGE2` authorizes only RP0 Stage-2 testing; Registry, Canon, capability-lifecycle, production-runtime, portfolio and trading authorities remain false.
- Negative Reality Registry is an RP0 learning ledger only and must not write to canonical `registry/**`.
- `S` remains primarily a Stage-2 survival/decision constraint; `Xa` and `Xp` are out of Stage-1 v0.1 scope unless separately authorized.
- Provider-native fields remain outside Capability identity and RP0 trial semantics.
- Target price, buy/sell/hold, recommended/target weight, position size, broker action and live execution outputs are prohibited.
- Stage-1 implementation must not begin reality execution until required B2 runtime interfaces have landed on the implementation base and passed their own governed qualification.

---

### Task 1: B2 Dependency Qualification Gate

**Files:**
- Create: `research_runtime/reality_proof/__init__.py`
- Create: `research_runtime/reality_proof/compat.py`
- Create: `tests/test_rp0_stage1_b2_compat.py`

**Interfaces:**
- Consumes: B2 `research_runtime.types`, replay, benchmark and ablation modules after they are implemented.
- Produces: `B2CompatibilityReport`, `assert_b2_stage1_compatible()`.

- [ ] **Step 1: Write the failing compatibility test**

```python
from research_runtime.reality_proof.compat import assert_b2_stage1_compatible


def test_rp0_requires_b2_runtime_contracts():
    report = assert_b2_stage1_compatible()
    assert report.typed_state_available is True
    assert report.typed_receipt_available is True
    assert report.replay_available is True
    assert report.benchmark_available is True
    assert report.ablation_available is True
```

- [ ] **Step 2: Run the test and observe RED**

Run: `python -m unittest tests.test_rp0_stage1_b2_compat -v`

Expected: FAIL until B2 has implemented the required modules. If B2 is still only at architecture/bootstrap state, STOP implementation here; do not add substitute RP0 replay or benchmark code.

- [ ] **Step 3: Implement minimal compatibility inspection**

`compat.py` must import the governed B2 interfaces and return an immutable dataclass with five booleans plus exact module/version identifiers. Missing interfaces raise `RuntimeError("B2_STAGE1_DEPENDENCY_NOT_READY")`.

- [ ] **Step 4: Re-run the compatibility test**

Run: `python -m unittest tests.test_rp0_stage1_b2_compat -v`

Expected: PASS only on a base containing qualified B2 runtime primitives.

- [ ] **Step 5: Commit**

```bash
git add research_runtime/reality_proof tests/test_rp0_stage1_b2_compat.py
git commit -m "feat(rp0): add fail-closed B2 compatibility gate"
```

---

### Task 2: RealityTrial Immutable Contract

**Files:**
- Create: `research_runtime/reality_proof/trial.py`
- Create: `tests/test_rp0_reality_trial.py`

**Interfaces:**
- Consumes: B2 `ResearchState` / `ResearchReceipt` identity semantics.
- Produces: `RealityTrial`, `TrialSettlement`, `freeze_trial()`, `append_settlement()`.

- [ ] **Step 1: Write failing tests for exact trial fields and T0 immutability**

```python
from dataclasses import replace
from research_runtime.reality_proof.trial import RealityTrial, freeze_trial


def test_reality_trial_requires_frozen_t0_contract(sample_trial):
    frozen = freeze_trial(sample_trial)
    assert frozen.trial_id
    assert frozen.reality_case_id
    assert frozen.capability_id
    assert frozen.capability_version
    assert frozen.t0
    assert frozen.evidence_cutoff
    assert frozen.input_snapshot_hash
    assert frozen.baseline_spec_ids
    assert frozen.research_state_spec
    assert frozen.falsifier
    assert frozen.settlement_rule
    assert frozen.evaluation_contract


def test_t0_semantics_cannot_be_rewritten(sample_trial):
    frozen = freeze_trial(sample_trial)
    mutated = replace(frozen, falsifier="post-hoc rewrite")
    try:
        freeze_trial(mutated, prior=frozen)
    except ValueError as exc:
        assert "IMMUTABLE_T0" in str(exc)
    else:
        raise AssertionError("expected immutable T0 failure")
```

- [ ] **Step 2: Run tests to verify RED**

Run: `python -m unittest tests.test_rp0_reality_trial -v`

Expected: FAIL because the contract is absent.

- [ ] **Step 3: Implement immutable dataclasses and deterministic trial hash**

The trial hash must be derived from the 12 frozen Stage-1 fields using canonical JSON ordering. `TrialSettlement` is stored separately and may append settlement evidence and outcome metadata without modifying the frozen hash.

- [ ] **Step 4: Add leakage test**

Add a test proving any settlement/outcome field included in the frozen T0 payload raises `ValueError("SETTLEMENT_LEAKAGE")`.

- [ ] **Step 5: Run tests**

Run: `python -m unittest tests.test_rp0_reality_trial -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add research_runtime/reality_proof/trial.py tests/test_rp0_reality_trial.py
git commit -m "feat(rp0): add immutable RealityTrial contract"
```

---

### Task 3: Three-Layer Baseline Doctrine

**Files:**
- Create: `research_runtime/reality_proof/baselines.py`
- Create: `fixtures/rp0/baselines/stage1_baselines_v0.1.json`
- Create: `tests/test_rp0_baselines.py`

**Interfaces:**
- Consumes: normalized PIT inputs already supported by B2.
- Produces: `BaselineSpec`, `BaselineResult`, `run_naive_baseline()`, `run_practitioner_baseline()`, `run_component_proxy()`.

- [ ] **Step 1: Write failing baseline-classification tests**

```python
from research_runtime.reality_proof.baselines import validate_baseline_set


def test_every_trial_has_b0_and_b1():
    result = validate_baseline_set(["B0-PERSISTENCE", "B1-GOLD-REAL-YIELD-USD"])
    assert result.has_b0 is True
    assert result.has_b1 is True


def test_b2_is_required_when_component_proxy_is_applicable():
    try:
        validate_baseline_set(
            ["B0-PERSISTENCE", "B1-NARRATIVE-PRACTITIONER"],
            component_proxy_applicable=True,
        )
    except ValueError as exc:
        assert "B2_COMPONENT_PROXY_REQUIRED" in str(exc)
    else:
        raise AssertionError("expected missing B2 failure")
```

- [ ] **Step 2: Run tests to verify RED**

Run: `python -m unittest tests.test_rp0_baselines -v`

- [ ] **Step 3: Implement provider-independent baseline specs**

Freeze baseline IDs for the five Reality Cases. Baselines must consume canonical normalized inputs only. B1 definitions must be simple enough to represent competent practitioner logic and must not call the ResearchCapability being tested.

- [ ] **Step 4: Add anti-strawman rule**

`select_best_valid_baseline(results)` must select the strongest valid preregistered baseline; evaluation may not choose B0 if B1 is valid and available.

- [ ] **Step 5: Run tests**

Run: `python -m unittest tests.test_rp0_baselines -v`

- [ ] **Step 6: Commit**

```bash
git add research_runtime/reality_proof/baselines.py fixtures/rp0/baselines tests/test_rp0_baselines.py
git commit -m "feat(rp0): add three-layer baseline doctrine"
```

---

### Task 4: M1–M5 Evaluation and Complexity Accounting

**Files:**
- Create: `research_runtime/reality_proof/evaluation.py`
- Create: `research_runtime/reality_proof/complexity.py`
- Create: `tests/test_rp0_evaluation.py`

**Interfaces:**
- Consumes: trial state, settlement, baseline results and B2 benchmark outputs.
- Produces: `ResearchRealityProfile`, `ComplexityProfile`, `evaluate_trial()`.

- [ ] **Step 1: Write failing tests for non-scalar evaluation**

```python
from research_runtime.reality_proof.evaluation import evaluate_trial


def test_reality_profile_is_vector_not_score(sample_evaluation_input):
    result = evaluate_trial(sample_evaluation_input)
    assert result.state_accuracy is not None
    assert result.uncertainty_calibration is not None
    assert result.incremental_information in {
        "positive_increment", "neutral_increment", "negative_increment", "insufficient_evidence"
    }
    assert result.decision_relevance is not None
    assert result.complexity_profile is not None
    assert not hasattr(result, "score")
```

- [ ] **Step 2: Add failing anti-naive-only test**

```python
def test_beating_b0_but_losing_to_b1_is_not_positive_increment(sample_evaluation_input):
    sample_evaluation_input.capability_metric = 0.60
    sample_evaluation_input.b0_metric = 0.50
    sample_evaluation_input.b1_metric = 0.65
    result = evaluate_trial(sample_evaluation_input)
    assert result.incremental_information != "positive_increment"
```

- [ ] **Step 3: Run tests and observe RED**

Run: `python -m unittest tests.test_rp0_evaluation -v`

- [ ] **Step 4: Implement M1–M5 structured outputs**

`ComplexityProfile` must contain `data_dependency_cost`, `provider_dependency_cost`, `runtime_cost`, `human_review_cost`, `interpretability_cost`, `failure_surface`, `maintenance_cost` as typed ordinal/structured fields. Do not sum them into a scalar.

- [ ] **Step 5: Add prohibited-output guards**

Fail if evaluation output contains `target_price`, `buy_signal`, `sell_signal`, `recommended_weight`, `target_weight`, `position_size`, `broker_action`, `live_execution`, `rp0_score`, `capability_score`, `force_score`, or `pnx_score`.

- [ ] **Step 6: Run tests**

Run: `python -m unittest tests.test_rp0_evaluation -v`

- [ ] **Step 7: Commit**

```bash
git add research_runtime/reality_proof/evaluation.py research_runtime/reality_proof/complexity.py tests/test_rp0_evaluation.py
git commit -m "feat(rp0): add incremental truth evaluation profile"
```

---

### Task 5: RP0 Ablation Adapter over B2

**Files:**
- Create: `research_runtime/reality_proof/ablation.py`
- Create: `tests/test_rp0_ablation.py`

**Interfaces:**
- Consumes: B2 benchmark/ablation primitives.
- Produces: `AblationEvidence`, `run_remove_ablation()`, `run_replace_ablation()`, `run_mechanism_break_ablation()`.

- [ ] **Step 1: Write failing adapter tests**

```python
from research_runtime.reality_proof.ablation import classify_ablation


def test_remove_ablation_challenges_independent_value_when_delta_is_neutral():
    result = classify_ablation(kind="remove", full_metric=0.70, ablated_metric=0.70, tolerance=0.01)
    assert result.independent_value_supported is False


def test_replace_ablation_recommends_simplify_when_proxy_is_equivalent():
    result = classify_ablation(kind="replace", full_metric=0.70, ablated_metric=0.695, tolerance=0.01)
    assert result.suggested_disposition == "SIMPLIFY"
```

- [ ] **Step 2: Run tests to verify RED**

Run: `python -m unittest tests.test_rp0_ablation -v`

- [ ] **Step 3: Implement RP0 interpretation only**

The adapter must call B2 execution primitives rather than duplicating replay/benchmark calculations. RP0 is responsible only for Stage-1 interpretation and doctrine.

- [ ] **Step 4: Add mechanism-break provenance test**

Require a distinct `mechanism_break_spec_id`; feature reordering or causal-chain breaking must be preregistered before settlement.

- [ ] **Step 5: Run tests and commit**

Run: `python -m unittest tests.test_rp0_ablation -v`

```bash
git add research_runtime/reality_proof/ablation.py tests/test_rp0_ablation.py
git commit -m "feat(rp0): interpret B2 ablations for Stage-1 truth"
```

---

### Task 6: Negative Reality Learning Ledger

**Files:**
- Create: `research_runtime/reality_proof/failures.py`
- Create: `artifacts/rp0/negative_reality/.gitkeep`
- Create: `tests/test_rp0_negative_reality.py`

**Interfaces:**
- Consumes: failed/degraded trial, replay, baseline, ablation and evaluation receipts.
- Produces: immutable `NegativeRealityReceipt`, `record_failure()`.

- [ ] **Step 1: Write failing taxonomy and namespace tests**

```python
from research_runtime.reality_proof.failures import record_failure


def test_failure_taxonomy_is_closed(sample_failure):
    sample_failure.failure_type = "no_incremental_value"
    receipt = record_failure(sample_failure)
    assert receipt.failure_type == "no_incremental_value"


def test_negative_reality_never_targets_canonical_registry(sample_failure):
    receipt = record_failure(sample_failure)
    assert not receipt.storage_path.startswith("registry/")
```

- [ ] **Step 2: Run tests to verify RED**

Run: `python -m unittest tests.test_rp0_negative_reality -v`

- [ ] **Step 3: Implement closed failure taxonomy**

Allowed values are exactly `theory_failure`, `measurement_failure`, `provider_failure`, `pit_failure`, `implementation_failure`, `generalization_failure`, `calibration_failure`, `complexity_failure`, `no_incremental_value`, `underpowered_evidence`.

- [ ] **Step 4: Make receipts append-only and hash-bound**

Each receipt must bind trial hash, relevant B2 receipt IDs, evaluation version and failure evidence refs.

- [ ] **Step 5: Run tests and commit**

Run: `python -m unittest tests.test_rp0_negative_reality -v`

```bash
git add research_runtime/reality_proof/failures.py artifacts/rp0/negative_reality tests/test_rp0_negative_reality.py
git commit -m "feat(rp0): add negative reality learning receipts"
```

---

### Task 7: Five-Case Stage-1 Manifest and 15–25 Trial Preregistration

**Files:**
- Create: `fixtures/rp0/reality_cases/five_case_reality_set_v0.1.json`
- Create: `fixtures/rp0/trials/stage1_trial_manifest_v0.1.json`
- Create: `tests/test_rp0_five_case_manifest.py`

**Interfaces:**
- Consumes: Stage-1 contract and currently executable Capability inventory after B2 qualification.
- Produces: exact five-case manifest and 15–25 preregistered `RealityTrial` definitions.

- [ ] **Step 1: Write failing exact-case test**

```python
REQUIRED_CASES = {
    "RP0-RC-01-NVIDIA",
    "RP0-RC-02-UST30Y",
    "RP0-RC-03-COPPER",
    "RP0-RC-04-GOLD",
    "RP0-RC-05-USDJPY",
}


def test_stage1_has_exact_five_cases(load_rp0_case_manifest):
    manifest = load_rp0_case_manifest()
    assert set(manifest["cases"]) == REQUIRED_CASES
```

- [ ] **Step 2: Add trial-count and preregistration test**

Require 15–25 trials; every trial must have a frozen capability version, T0/evidence cutoff, B0+B1 baseline set, falsifier and settlement rule. B2 component proxy is required where applicable.

- [ ] **Step 3: Run tests to verify RED**

Run: `python -m unittest tests.test_rp0_five_case_manifest -v`

- [ ] **Step 4: Populate manifests only from executable/qualified capabilities**

Do not invent implementations for P, N or E if they are not yet executable. Such planned trials must either be omitted from v0.1 execution or explicitly carry `execution_state="blocked_dependency"`; they must not be silently substituted with proxy capabilities.

- [ ] **Step 5: Run tests and commit**

Run: `python -m unittest tests.test_rp0_five_case_manifest -v`

```bash
git add fixtures/rp0/reality_cases fixtures/rp0/trials tests/test_rp0_five_case_manifest.py
git commit -m "feat(rp0): preregister five-case Stage-1 trial set"
```

---

### Task 8: RP0-G1 Capability Reality Settlement

**Files:**
- Create: `research_runtime/reality_proof/gate.py`
- Create: `artifacts/rp0/stage1/.gitkeep`
- Create: `tests/test_rp0_g1_gate.py`

**Interfaces:**
- Consumes: trial results, baseline results, ablation evidence, negative-reality receipts, complexity profile and evidence-authority record.
- Produces: `CapabilityRealityProfile`, one exact Stage-1 disposition, explicit authority flags.

- [ ] **Step 1: Write failing disposition test**

```python
from research_runtime.reality_proof.gate import settle_capability


def test_g1_emits_exactly_one_governed_disposition(sample_capability_evidence):
    result = settle_capability(sample_capability_evidence)
    assert result.disposition in {
        "PROMOTE_FOR_STAGE2",
        "KEEP_SHADOW",
        "SIMPLIFY",
        "MERGE_INTO_COMPOSITE",
        "REJECT_NO_INCREMENT",
        "INSUFFICIENT_EVIDENCE",
    }
```

- [ ] **Step 2: Write failing authority-separation test**

```python
def test_stage2_promotion_does_not_escalate_other_authorities(sample_positive_evidence):
    result = settle_capability(sample_positive_evidence)
    if result.disposition == "PROMOTE_FOR_STAGE2":
        assert result.stage2_test_authorized is True
    assert result.registry_promotion_authorized is False
    assert result.canon_promotion_authorized is False
    assert result.production_runtime_authorized is False
    assert result.portfolio_action_authorized is False
    assert result.trading_authorized is False
```

- [ ] **Step 3: Run tests to verify RED**

Run: `python -m unittest tests.test_rp0_g1_gate -v`

- [ ] **Step 4: Implement fail-closed settlement rules**

At minimum: B1 loss blocks `PROMOTE_FOR_STAGE2`; equivalent cheap proxy prefers `SIMPLIFY`; neutral remove-ablation challenges independent Mother value; insufficient evidence must remain `INSUFFICIENT_EVIDENCE`; unresolved cross-asset generalization cannot be upgraded by narrative rationale.

- [ ] **Step 5: Run tests and commit**

Run: `python -m unittest tests.test_rp0_g1_gate -v`

```bash
git add research_runtime/reality_proof/gate.py artifacts/rp0/stage1 tests/test_rp0_g1_gate.py
git commit -m "feat(rp0): add Incremental Truth settlement gate"
```

---

### Task 9: Full Stage-1 Validator, CI Gate, and Human Review Surface

**Files:**
- Create: `scripts/validate_rp0_stage1.py`
- Create: `tests/test_rp0_stage1_full_gate.py`
- Create: `docs/architecture/rp0/RP0-STAGE1-HUMAN-REVIEW-CARD-v0.1.md`
- Create: `docs/architecture/rp0/RP0-STAGE1-STATE.json`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: Tasks 1–8 artifacts.
- Produces: one fail-closed machine gate and a Human Review package; does not perform Human Acceptance.

- [ ] **Step 1: Write failing full-gate test**

```python
from scripts.validate_rp0_stage1 import validate_rp0_stage1


def test_stage1_gate_is_machine_ready(repo_root):
    result = validate_rp0_stage1(repo_root)
    assert result["reality_case_count"] == 5
    assert 15 <= result["trial_count"] <= 25
    assert result["registry_mutations"] == 0
    assert result["canon_mutations"] == 0
    assert result["trading_authority"] is False
    assert result["next_gate"] == "RP0_STAGE1_HUMAN_REVIEW"
```

- [ ] **Step 2: Add scope-guard test**

Fail if the Stage-1 implementation changes canonical `registry/**`, `canon/**`, production trading/runtime authority, or rewrites B2 execution ownership.

- [ ] **Step 3: Run tests to observe RED**

Run: `python -m unittest tests.test_rp0_stage1_full_gate -v`

- [ ] **Step 4: Implement validator and State projection**

State may advance only to `candidate_ready_for_human_review`; all Registry/Canon/production-runtime/portfolio/trading authority fields remain `none` or false.

- [ ] **Step 5: Wire validator into `repository-gates` exactly once**

Add `python scripts/validate_rp0_stage1.py` after existing architecture validators and before full unit-test discovery. Preserve all current gates.

- [ ] **Step 6: Create Human Review Card**

The card must list every capability with Stage-1 evidence, B0/B1/B2 results, ablation evidence, complexity profile, failures, generalization status and proposed disposition. It must explicitly separate `PROMOTE_FOR_STAGE2` from Registry/Canon/lifecycle promotion.

- [ ] **Step 7: Run full verification**

Run:

```bash
python scripts/validate_rp0_stage1.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add scripts/validate_rp0_stage1.py tests/test_rp0_stage1_full_gate.py docs/architecture/rp0 .github/workflows/ci.yml
git commit -m "feat(rp0): qualify Stage-1 Incremental Truth human gate"
```

---

## Execution Stop Conditions

Execution must stop immediately if any of the following is true:

1. B2 typed state/receipt, replay, benchmark or ablation interfaces are not yet implemented and qualified.
2. The implementation would require creating a second Replay/Benchmark engine.
3. Required P/N/E capabilities are not executable; their trials may remain dependency-blocked but must not be fabricated.
4. PIT evidence cannot be frozen without post-cutoff leakage.
5. Baseline definitions cannot be preregistered before settlement data are exposed.
6. A requested change would mutate canonical Registry/Canon or grant production-runtime/portfolio/trading authority without separate authorization.
7. Stage-1 result generation requires a scalar master score.

## Plan Completion Gate

Completion of Tasks 1–9 means only:

`RP0_STAGE1_CANDIDATE_READY_FOR_HUMAN_REVIEW`

It does **not** mean Stage-1 findings are Human Accepted, merged, Registry/Canon promoted, production-authorized, or eligible for portfolio/trading action.

Human acceptance and any later merge/apply authority must be separate governed actions.
