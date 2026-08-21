# R2.3-B2 P0 Reference Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement deterministic, provider-independent reference runtimes and point-in-time replay/benchmark harnesses for CAP-R-01, CAP-V-01, and CAP-XS-01, then run a five-asset Shadow and benchmark/ablation without granting promotion, portfolio, or execution authority.

**Architecture:** Add a stdlib-only `research_runtime` Python package with shared typed envelopes/states, three capability modules, replay fixtures, and a benchmark/ablation harness. Each capability consumes normalized economic inputs rather than vendor fields, emits typed `ResearchState` plus `ResearchReceipt`, and fails closed on missing/stale/underidentified inputs. Historical/Shadow fixtures are immutable JSON with explicit `as_of`, `evidence_cutoff`, publication-lag metadata, and outcome fields physically separated from T0 inputs.

**Tech Stack:** Python 3.12 stdlib, `unittest`, existing `jsonschema==4.25.1` dev dependency, GitHub Actions `repository-gates`.

**Spec:** `docs/architecture/r2_3b1/R2-3B1-P0-CAPABILITY-CONTRACT-SPECIFICATION-v0.1.md`

## Global Constraints

- `Claim Authority <= Evidence Authority`.
- `P = P.capital + P.asset`; R remains a typed decomposition of `P.capital`, not a fourth human world.
- `Asset form is not pricing model`; routing uses A0 + A1.
- `X := (Xs, Xa, Xp)` remains indivisible; CAP-XS-01 implements Xs only.
- Canonical output is typed `ResearchState`; scalar Force/PNX/macro master scores are prohibited.
- Provider/vendor fields are adapters, never Capability identity.
- PIT semantics, publication lag, revisions, and evidence cutoff are mandatory.
- Target price, canonical upside %, recommended portfolio weight, position size, buy/sell/hold, and live execution are prohibited.
- `Research PASS != Capital PASS`.
- B2 is reference/shadow implementation only. Capability promotion, Evidence/Outcome admission, A9 switch, Wind/Codex production runtime, and trading authority remain unauthorized.
- Do not start B2 implementation until PR #25 / R2.3-B1 is merged to `main`.

---

### Task 1: Shared Runtime Types and Fail-Closed Contract

**Files:**
- Create: `research_runtime/__init__.py`
- Create: `research_runtime/types.py`
- Create: `research_runtime/validation.py`
- Create: `tests/test_research_runtime_contract.py`

**Interfaces:**
- Consumes: B0/B1 contract semantics.
- Produces: `InvocationEnvelope`, `ResearchState`, `ResearchReceipt`, `CapabilityError`, `validate_invocation()`, `fail_closed_state()`.

- [ ] **Step 1: Write failing tests for typed envelope/state/receipt and prohibited output guard**

```python
from research_runtime.types import InvocationEnvelope, ResearchState, ResearchReceipt
from research_runtime.validation import validate_invocation, assert_no_prohibited_outputs


def test_invocation_requires_pit_fields():
    env = InvocationEnvelope(
        canon_revision="test",
        canon_hash="abc",
        capability_id="CAP-R-01",
        capability_contract_version="0.1.0",
        research_target="UST30Y",
        A0_asset_form="sovereign_rates",
        A1_pricing_archetype="duration",
        as_of="2025-01-31",
        evidence_cutoff="2025-01-31T23:59:59Z",
        provider_runtime="fixture",
    )
    assert validate_invocation(env) is None


def test_prohibited_output_guard_rejects_target_price():
    try:
        assert_no_prohibited_outputs({"target_price": 100})
    except ValueError as exc:
        assert "target_price" in str(exc)
    else:
        raise AssertionError("expected prohibited-output failure")
```

- [ ] **Step 2: Run tests to verify failure**

Run: `python -m unittest tests.test_research_runtime_contract -v`
Expected: FAIL because `research_runtime` does not exist.

- [ ] **Step 3: Implement minimal immutable dataclasses and validation**

`InvocationEnvelope` fields must exactly match B0. `ResearchState` must contain `state_type`, `dimensions`, `uncertainty_semantics`, `evidence_refs`, `as_of`, `degrade_state`, `downstream_dependencies`. `ResearchReceipt` binds the envelope, algorithm family, evidence refs, output state version, identification status, and degrade state. `assert_no_prohibited_outputs()` rejects the B0 prohibited output names.

- [ ] **Step 4: Run tests**

Run: `python -m unittest tests.test_research_runtime_contract -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add research_runtime tests/test_research_runtime_contract.py
git commit -m "feat(runtime): add typed research state and receipt contract"
```

---

### Task 2: B2-R — CAP-R-01 Reference Implementation + Replay

**Files:**
- Create: `research_runtime/capabilities/__init__.py`
- Create: `research_runtime/capabilities/regime.py`
- Create: `research_runtime/replay.py`
- Create: `fixtures/replay/cap_r_01/*.json`
- Create: `tests/test_cap_r_01_reference.py`

**Interfaces:**
- Consumes: `InvocationEnvelope`; normalized observations keyed by `growth`, `inflation`, `liquidity`, `risk_appetite`, `term_premium`, `funding_stress`, `policy_reaction_function`.
- Produces: `run_cap_r_01(envelope, observations) -> tuple[ResearchState, ResearchReceipt]`; `run_replay_case(path, runner)`.

- [ ] **Step 1: Write failing tests for all seven dimensions, liquidity/risk-appetite separation, and stale-input degradation**

```python
from research_runtime.capabilities.regime import run_cap_r_01


def test_regime_emits_seven_separate_dimensions(sample_r_envelope, sample_r_inputs):
    state, receipt = run_cap_r_01(sample_r_envelope, sample_r_inputs)
    assert list(state.dimensions) == [
        "growth", "inflation", "liquidity", "risk_appetite",
        "term_premium", "funding_stress", "policy_reaction_function",
    ]
    assert state.dimensions["liquidity"] != state.dimensions["risk_appetite"]
    assert receipt.algorithm_family == "transparent_rule_graph_v0"
```

- [ ] **Step 2: Verify tests fail**

Run: `python -m unittest tests.test_cap_r_01_reference -v`
Expected: FAIL because runner is absent.

- [ ] **Step 3: Implement transparent rule-graph reference algorithm**

Each dimension maps normalized PIT observations into ordinal `direction` (`down|flat|up|mixed`), `magnitude_band` (`low|medium|high|unknown`), and `persistence_band` (`transitory|persistent|uncertain`). The implementation must surface `competing_mechanisms` and never collapse dimensions into one score. Any missing required dimension produces `insufficient_evidence`; stale publication lag produces `stale`.

- [ ] **Step 4: Add PIT replay cases**

Fixtures must contain `t0_inputs`, `t0_evidence_refs`, `as_of`, `evidence_cutoff`, `publication_lag_policy`, and a physically separate `settlement` object. Include at least one success case and one failure/ambiguous case. No settlement field may be passed to the runner.

- [ ] **Step 5: Run R tests and replay leakage test**

Run: `python -m unittest tests.test_cap_r_01_reference -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add research_runtime/capabilities/regime.py research_runtime/replay.py fixtures/replay/cap_r_01 tests/test_cap_r_01_reference.py
git commit -m "feat(cap-r): add regime reference implementation and PIT replay"
```

---

### Task 3: B2-V — CAP-V-01 Cross-Asset Reference Implementation + Replay

**Files:**
- Create: `research_runtime/capabilities/price_implied.py`
- Create: `fixtures/replay/cap_v_01/*.json`
- Create: `tests/test_cap_v_01_reference.py`

**Interfaces:**
- Consumes: envelope + normalized price/model inputs.
- Produces: `run_cap_v_01(envelope, inputs) -> tuple[ResearchState, ResearchReceipt]`.

- [ ] **Step 1: Write failing router tests**

```python
from research_runtime.capabilities.price_implied import select_v_model_family


def test_v_router_is_asset_specific():
    assert select_v_model_family("equity", "growth") == "reverse_dcf"
    assert select_v_model_family("sovereign_rates", "duration") == "implied_policy_path"
    assert select_v_model_family("commodity", "scarcity") == "futures_curve_scarcity"
    assert select_v_model_family("FX", "duration") == "forward_rate_differential"
    assert select_v_model_family("monetary_asset", "scarcity") == "real_rate_monetary_risk"
```

- [ ] **Step 2: Verify failure**

Run: `python -m unittest tests.test_cap_v_01_reference -v`
Expected: FAIL because router is absent.

- [ ] **Step 3: Implement deterministic inverse-pricing adapters**

Implement minimal reference families for the five Shadow asset forms using simple, auditable transforms. When more than one parameter combination fits within tolerance, set `identification_status="underidentified"`, emit parameter ranges/scenario families, and degrade rather than producing fake point precision. Do not output target prices or upside percentages.

- [ ] **Step 4: Add replay cases covering identified and underidentified inverse problems**

At least one equity/rates case must deliberately admit multiple parameter solutions and verify range/scenario output.

- [ ] **Step 5: Run V tests**

Run: `python -m unittest tests.test_cap_v_01_reference -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add research_runtime/capabilities/price_implied.py fixtures/replay/cap_v_01 tests/test_cap_v_01_reference.py
git commit -m "feat(cap-v): add cross-asset price-implied reference runtime"
```

---

### Task 4: B2-XS — CAP-XS-01 Routed Reference Implementation + Replay

**Files:**
- Create: `research_runtime/capabilities/asymmetry_source.py`
- Create: `fixtures/replay/cap_xs_01/*.json`
- Create: `tests/test_cap_xs_01_reference.py`

**Interfaces:**
- Consumes: envelope + normalized structural inputs.
- Produces: `run_cap_xs_01(envelope, inputs) -> tuple[ResearchState, ResearchReceipt]`.

- [ ] **Step 1: Write failing routing/boundary tests**

```python
from research_runtime.capabilities.asymmetry_source import select_xs_implementation


def test_xs_router_preserves_asset_physics():
    assert select_xs_implementation("equity") == "value_control_point"
    assert select_xs_implementation("commodity") == "scarcity_supply_elasticity"
    assert select_xs_implementation("sovereign_rates") == "duration_convexity_term_premium"
    assert select_xs_implementation("FX") == "policy_divergence_carry_flow"
    assert select_xs_implementation("monetary_asset") == "monetary_scarcity_reserve_demand"
```

- [ ] **Step 2: Verify failure**

Run: `python -m unittest tests.test_cap_xs_01_reference -v`
Expected: FAIL because implementation is absent.

- [ ] **Step 3: Implement routed structural mappers**

Each mapper emits `asymmetry_source`, `mechanism_chain`, `concentration_location`, `structural_conditions`, `durability_or_persistence`, `substitutability_or_elasticity`, and `invalidators`. It must not emit Xa activation probability, Xp instrument choice, V attractiveness, or S capital authorization.

- [ ] **Step 4: Add replay/failure cases**

Include a case where a structural bottleneck exists but does not become investable asymmetry; settlement must record this as a failure/limitation rather than retroactively changing Xs.

- [ ] **Step 5: Run XS tests**

Run: `python -m unittest tests.test_cap_xs_01_reference -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add research_runtime/capabilities/asymmetry_source.py fixtures/replay/cap_xs_01 tests/test_cap_xs_01_reference.py
git commit -m "feat(cap-xs): add routed asymmetry-source reference runtime"
```

---

### Task 5: Joint Five-Asset Shadow

**Files:**
- Create: `fixtures/shadow/five_asset_v0.1.json`
- Create: `research_runtime/shadow.py`
- Create: `tests/test_five_asset_shadow.py`
- Create: `docs/architecture/r2_3b2/R2-3B2-FIVE-ASSET-SHADOW-REPORT-v0.1.md`

**Interfaces:**
- Consumes: the three capability runners and immutable PIT fixture pack.
- Produces: one ResearchState/ResearchReceipt triplet per target and a machine-readable shadow result table.

- [ ] **Step 1: Write failing coverage test**

```python
REQUIRED = {
    "NVIDIA": ("equity", "growth"),
    "UST30Y": ("sovereign_rates", "duration"),
    "COPPER": ("commodity", "cyclical"),
    "GOLD": ("monetary_asset", "scarcity"),
    "USDJPY": ("FX", "duration"),
}


def test_shadow_has_exact_required_targets(load_shadow_fixture):
    fixture = load_shadow_fixture()
    assert set(fixture["targets"]) == set(REQUIRED)
    for target, route in REQUIRED.items():
        assert tuple(fixture["targets"][target]["route"]) == route
```

- [ ] **Step 2: Verify failure**

Run: `python -m unittest tests.test_five_asset_shadow -v`
Expected: FAIL because fixture/harness is absent.

- [ ] **Step 3: Build PIT fixture pack**

Every target must have normalized R/V/XS inputs, source/evidence IDs, `as_of`, `evidence_cutoff`, and separate settlement fields. Fixtures are research fixtures, not current market claims; every value must be tagged `synthetic`, `historical_public`, or `user_supplied` provenance.

- [ ] **Step 4: Implement joint Shadow runner**

The runner must execute R, V, XS independently, preserve degrade states, and never create a composite score or buy/sell output.

- [ ] **Step 5: Generate deterministic Markdown report from result JSON**

Report columns: target, A0/A1 route, R state summary, V identification status, Xs implementation/source, degrade states, evidence refs, settlement availability. No portfolio action column.

- [ ] **Step 6: Run Shadow tests**

Run: `python -m unittest tests.test_five_asset_shadow -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add fixtures/shadow research_runtime/shadow.py tests/test_five_asset_shadow.py docs/architecture/r2_3b2/R2-3B2-FIVE-ASSET-SHADOW-REPORT-v0.1.md
git commit -m "feat(shadow): add five-asset cross-asset P0 shadow"
```

---

### Task 6: Benchmark + Ablation

**Files:**
- Create: `research_runtime/benchmark.py`
- Create: `fixtures/benchmark/p0_baselines_v0.1.json`
- Create: `tests/test_p0_benchmark_ablation.py`
- Create: `docs/architecture/r2_3b2/R2-3B2-BENCHMARK-ABLATION-REPORT-v0.1.md`

**Interfaces:**
- Consumes: replay/shadow result objects.
- Produces: per-capability baseline comparison, ablation deltas, failure receipts, and qualification status (`informative|no_incremental_information|insufficient_evidence`).

- [ ] **Step 1: Write failing benchmark tests**

```python
from research_runtime.benchmark import compare_to_baseline, ablate


def test_complexity_is_demoted_without_incremental_information():
    result = compare_to_baseline(reference_metric=0.50, baseline_metric=0.51, tolerance=0.0)
    assert result["qualification"] == "no_incremental_information"


def test_ablation_reports_component_delta():
    result = ablate(full_metric=0.70, ablated_metric=0.61, component="term_premium")
    assert result["delta"] == 0.09
```

- [ ] **Step 2: Verify failure**

Run: `python -m unittest tests.test_p0_benchmark_ablation -v`
Expected: FAIL because benchmark module is absent.

- [ ] **Step 3: Implement baseline/ablation harness**

R baselines: single-rate level, simple growth/inflation quadrant, risk-asset momentum. V baselines: historical multiple/yield-spread percentile/simple forward carry. XS baselines: sector label/simple concentration/simple inventory-duration metric. Metrics must be capability-specific; no common scalar master score.

- [ ] **Step 4: Add failure receipts**

When reference complexity does not beat/add stable information versus baseline, persist a machine-readable failure receipt and mark the method for demotion; do not suppress the result.

- [ ] **Step 5: Run benchmark tests and full suite**

Run: `python -m unittest tests.test_p0_benchmark_ablation -v`
Expected: PASS.

Run: `python -m unittest discover -s tests -p 'test_*.py' -v`
Expected: PASS.

- [ ] **Step 6: Add B2 validator and CI gate**

Create `scripts/validate_r2_3b2_reference_implementation.py`; add it to `.github/workflows/ci.yml` after the B1 validator. Validator must verify five targets, three capability IDs, PIT separation, receipt production, prohibited-output absence, benchmark failure-receipt semantics, and no promotion/execution authority.

- [ ] **Step 7: Run repository gates**

Run locally where available: `python scripts/validate_r2_3b2_reference_implementation.py && python scripts/build_canon_status.py --check && python -m unittest discover -s tests -p 'test_*.py' -v`
Expected: PASS before pushing; GitHub exact-head `repository-gates` must also PASS.

- [ ] **Step 8: Commit**

```bash
git add research_runtime/benchmark.py fixtures/benchmark tests/test_p0_benchmark_ablation.py docs/architecture/r2_3b2 scripts/validate_r2_3b2_reference_implementation.py .github/workflows/ci.yml
git commit -m "feat(b2): close P0 benchmark and ablation harness"
```

---

### Task 7: B2 State, Human Review Candidate, and Governance Closure

**Files:**
- Create: `docs/architecture/r2_3b2/R2-3B2-STATE.json`
- Create: `docs/architecture/r2_3b2/R2-3B2-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `scripts/build_canon_status.py`
- Modify: `docs/architecture/CANON-STATUS.json`

**Interfaces:**
- Consumes: exact-head successful CI and B2 reports.
- Produces: deterministic candidate state only; no promotion.

- [ ] **Step 1: Record machine qualification only after exact-head CI is SUCCESS**

State must include exact SHA/run ID and per-gate conclusions.

- [ ] **Step 2: Create Human Review Card**

Review dimensions must include PIT leakage, causal overclaim, underidentification, cross-asset routing, X boundary integrity, benchmark incrementality, failure receipts, deterministic replay, and governance/no-execution boundaries.

- [ ] **Step 3: Rebuild deterministic Canon projection**

`CANON-STATUS` must show B2 as `candidate_ready_for_human_review`, with `promotion_authorized=false`, `production_runtime_authorized=false`, `portfolio_execution_authorized=false`.

- [ ] **Step 4: Re-run exact-head CI**

Expected: `repository-gates = SUCCESS` on the Human-Review exact head.

- [ ] **Step 5: Stop at Human Gate**

Do not merge or promote. Surface the exact Human Gate token generated by B2 state.
