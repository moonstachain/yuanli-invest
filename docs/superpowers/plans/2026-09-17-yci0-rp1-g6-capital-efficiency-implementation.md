# YCI0-RP1-G6 Capital Efficiency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the accepted G6 Marginal Capital Productivity Stack into a PIT-safe, entity-safe, direction-aware RESEARCH-only Reality dimension and attempt a raw-backed 6/6 AI-Infra Reality compile without weakening the accepted definition.

**Architecture:** Add a versioned G6 machine contract beside RP0 rather than mutating accepted RP0 semantics in place. Extend compilation through a dedicated capital-efficiency compiler that preserves raw metrics, applies metric directionality only for efficiency-state orientation, aggregates component → entity → cohort → dimension, and fails closed. Reconstruct representative cohort observations only from archived first-party filings; production admission happens only after raw archive + SHA readback + PIT receipts pass.

**Tech Stack:** Python 3.11/3.12 stdlib runtime, unittest, JSON machine contracts, SEC EDGAR first-party filings/XBRL facts, GitHub Actions, Supabase private S3 + runtime tables, Notion Human Workbench projection.

**Spec:** `docs/superpowers/specs/2026-09-17-yci0-rp1-g6-capital-efficiency-definition-freeze-design.md`

## Global Constraints

- Authority remains exactly `RESEARCH_ONLY`; no Narrative, Shadow, Capital, sizing, broker, or Execution authority.
- Mandatory first-proof components are exactly `INCREMENTAL_ROIC`, `CASH_CONVERSION`, `CAPITAL_INTENSITY`.
- Frozen cohorts are exactly `HYPERSCALER`, `COMPUTE`, `NETWORKING`, `POWER_ELECTRICAL`.
- Initial representatives are exactly `MSFT`, `NVDA`, `ANET`, `ETN` unless a representative fails source/accounting validity; failure leaves that cohort and G6 `UNKNOWN` rather than substituting a convenient company.
- `Incremental ROIC_t = (TTM NOPAT_t - TTM NOPAT_{t-4}) / (Operating Invested Capital_t - Operating Invested Capital_{t-4})`.
- `Cash Conversion = TTM Operating Cash Flow / TTM NOPAT`.
- `Capital Intensity = TTM Capex / TTM Revenue`.
- Directionality closed set is exactly `HIGHER_IS_MORE_EFFICIENT` and `LOWER_IS_MORE_EFFICIENT`.
- Raw Level / Delta / Delta2 are preserved; only oriented values are used for G6 efficiency-state classification.
- Four consecutive derived quarterly observations require at least eight consecutive raw filing quarters for Incremental ROIC.
- Every PASS observation must retain `source → raw snapshot → normalized components → calculation receipt → known_as_of → content hash → evidence receipt`.
- Missing mandatory component, unstable denominator, accounting-regime break, missing PIT semantics, missing raw/hash lineage, insufficient history, semantic ambiguity, entity collision, or unregistered directionality => `UNKNOWN`.
- No 0–100 score and no market-cap/revenue/subjective weighting.
- Even `FULL_REALITY_STATE_6_OF_6` must leave Notion at `02 EVIDENCE / HOLD` until a separate Human Gate.

---

### Task 1: Freeze the G6 Machine Contract and Validator

**Files:**
- Create: `config/yci0_rp1/capital_efficiency_contract.v0.1.json`
- Create: `runtime/yci0_rp1/__init__.py`
- Create: `runtime/yci0_rp1/capital_efficiency_contract.py`
- Create: `tests/test_yci0_rp1_capital_efficiency_contract.py`

**Interfaces:**
- Consumes: accepted G6 design spec and existing `RealityEvidence` authority/PIT vocabulary.
- Produces: `load_capital_efficiency_contract(path) -> CapitalEfficiencyContract`; `metric_spec(metric_id) -> CapitalEfficiencyMetricSpec`; immutable cohort/entity/component/directionality registry used by Tasks 2–5.

- [ ] **Step 1: Write RED contract tests**

```python
class CapitalEfficiencyContractTests(unittest.TestCase):
    def test_contract_has_exact_mandatory_components_and_cohorts(self):
        c = load_capital_efficiency_contract(CONTRACT)
        self.assertEqual(c.mandatory_components, ("INCREMENTAL_ROIC", "CASH_CONVERSION", "CAPITAL_INTENSITY"))
        self.assertEqual(c.required_cohorts, ("HYPERSCALER", "COMPUTE", "NETWORKING", "POWER_ELECTRICAL"))

    def test_metric_ids_encode_cohort_entity_component_and_direction(self):
        c = load_capital_efficiency_contract(CONTRACT)
        spec = c.metric_spec("AIINFRA.CAPITAL_EFFICIENCY.HYPERSCALER.MSFT.INCREMENTAL_ROIC")
        self.assertEqual(spec.entity_id, "MSFT")
        self.assertEqual(spec.cohort, "HYPERSCALER")
        self.assertEqual(spec.directionality, "HIGHER_IS_MORE_EFFICIENT")
        burden = c.metric_spec("AIINFRA.CAPITAL_EFFICIENCY.POWER_ELECTRICAL.ETN.CAPITAL_INTENSITY")
        self.assertEqual(burden.directionality, "LOWER_IS_MORE_EFFICIENT")
```

- [ ] **Step 2: Run RED tests**

Run: `python -m unittest tests.test_yci0_rp1_capital_efficiency_contract -v`
Expected: FAIL because the contract loader/module does not exist.

- [ ] **Step 3: Implement minimal versioned contract and loader**

The JSON must register exactly 12 mandatory metric identities: 4 cohorts × 1 representative × 3 components. Each metric object contains `metric_id`, `cohort`, `entity_id`, `component`, `directionality`, `unit`, `authority`, `pit_policy`, `minimum_derived_observations`, and `minimum_raw_quarters`. The loader validates closed sets, identity consistency, `RESEARCH` authority, and duplicate IDs.

- [ ] **Step 4: Run focused and repository tests**

Run: `python -m unittest tests.test_yci0_rp1_capital_efficiency_contract -v`
Expected: PASS.
Run: `python -m unittest discover -s tests -p 'test_*.py' -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add config/yci0_rp1 runtime/yci0_rp1 tests/test_yci0_rp1_capital_efficiency_contract.py
git commit -m "feat(yci0-rp1): freeze G6 machine contract"
```

---

### Task 2: Implement Entity-Safe, Direction-Aware G6 Compilation

**Files:**
- Create: `runtime/yci0_rp1/capital_efficiency_compiler.py`
- Create: `tests/test_yci0_rp1_capital_efficiency_compiler.py`
- Modify: `runtime/yci0_rp0/state_compiler.py` only to delegate `capital_efficiency` rows to the G6 compiler; existing five dimensions retain current semantics.

**Interfaces:**
- Consumes: `RealityEvidence`, `CapitalEfficiencyContract`.
- Produces: `compile_capital_efficiency(evidence, as_of, contract) -> DimensionState`; raw per-series audit fields plus oriented component/entity/cohort state; no authority expansion.

- [ ] **Step 1: Write RED tests for identity, directionality, aggregation and fail-closed behavior**

```python
def test_same_component_different_entities_never_cross_mix(self):
    rows = entity_series("MSFT", "HYPERSCALER", "INCREMENTAL_ROIC", [0.20, 0.25, 0.35])
    rows += entity_series("NVDA", "COMPUTE", "INCREMENTAL_ROIC", [0.80, 0.70, 0.50])
    result = compile_capital_efficiency(rows, AS_OF, CONTRACT)
    self.assertNotEqual(result.entities["MSFT"].components["INCREMENTAL_ROIC"].state,
                        result.entities["NVDA"].components["INCREMENTAL_ROIC"].state)

def test_lower_is_more_efficient_preserves_raw_delta_but_orients_state(self):
    rows = full_entity_fixture("ETN", "POWER_ELECTRICAL", capital_intensity=[0.12, 0.10, 0.07])
    result = compile_capital_efficiency(rows, AS_OF, CONTRACT)
    c = result.entities["ETN"].components["CAPITAL_INTENSITY"]
    self.assertEqual(c.raw_delta, -0.03)
    self.assertEqual(c.state, RealityState.ACCELERATING)

def test_missing_mandatory_component_for_required_cohort_forces_dimension_unknown(self):
    rows = qualified_fixture_without("ANET", "CASH_CONVERSION")
    self.assertEqual(compile_capital_efficiency(rows, AS_OF, CONTRACT).state, RealityState.UNKNOWN)
```

- [ ] **Step 2: Run RED tests**

Run: `python -m unittest tests.test_yci0_rp1_capital_efficiency_compiler -v`
Expected: FAIL because the compiler does not exist.

- [ ] **Step 3: Implement the dedicated compiler**

Define immutable component/entity/cohort result dataclasses. Series identity is full `metric_id`; contract validation must additionally prove encoded entity/cohort/component match evidence `entity_id`. Compute raw Level/Delta/Delta2 with the existing three-point numerical rule; compute oriented values by sign-normalizing only the classification input; aggregate mandatory components → entity, qualified entity → required cohort, required cohorts → dimension. Any missing mandatory component or required cohort returns dimension `UNKNOWN / LOW`.

- [ ] **Step 4: Integrate with RP0 state compiler without changing five existing dimensions**

When `compile_reality_state()` reaches `capital_efficiency`, call the G6 compiler if a valid G6 contract is available; otherwise retain `UNKNOWN`. Do not apply G6 directionality to financing/capex/compute/networking/power dimensions.

- [ ] **Step 5: Run focused regression suite**

Run: `python -m unittest tests.test_yci0_rp1_capital_efficiency_compiler tests.test_yci0_rp0_state_compiler -v`
Expected: PASS.
Run: `python -m unittest discover -s tests -p 'test_*.py' -v`
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add runtime/yci0_rp0/state_compiler.py runtime/yci0_rp1/capital_efficiency_compiler.py tests/test_yci0_rp1_capital_efficiency_compiler.py
git commit -m "feat(yci0-rp1): compile entity-safe capital efficiency"
```

---

### Task 3: Build Deterministic PIT Filing Reconstruction

**Files:**
- Create: `runtime/yci0_rp1/capital_efficiency_reconstruction.py`
- Create: `config/yci0_rp1/capital_efficiency_entities.v0.1.json`
- Create: `tests/fixtures/yci0_rp1_g6/` with small synthetic SEC-fact fixtures only; no copied production filings.
- Create: `tests/test_yci0_rp1_capital_efficiency_reconstruction.py`

**Interfaces:**
- Consumes: normalized quarterly filing facts with `entity_id`, fiscal period, filing/release timestamp, source locator/hash, GAAP concept, value/unit.
- Produces: `reconstruct_entity_observations(facts, entity_spec) -> list[DerivedCapitalEfficiencyObservation]` with numerator/denominator lineage and explicit invalidation reasons.

- [ ] **Step 1: Write RED reconstruction tests**

Cover exactly: TTM NOPAT tax-rate 0–50% guard; operating invested-capital formula; positive/economically-meaningful YoY denominator; eight-quarter minimum for four derived observations; CFO/NOPAT near-zero guard; capex/revenue TTM; fiscal-calendar/accounting-regime break; calculation receipt containing every source fact/hash.

- [ ] **Step 2: Run RED tests**

Run: `python -m unittest tests.test_yci0_rp1_capital_efficiency_reconstruction -v`
Expected: FAIL because reconstruction types/functions do not exist.

- [ ] **Step 3: Implement deterministic reconstruction**

Use only stdlib dataclasses/Decimal/date handling. Tax-rate, denominator and near-zero thresholds live in the entity contract, not hidden constants. The output includes `status=PASS|UNKNOWN`, `reason`, raw formula inputs, derived raw value, `known_as_of=max(required source known_as_of)`, and a deterministic SHA-256 calculation receipt.

- [ ] **Step 4: Run focused + full tests**

Run: `python -m unittest tests.test_yci0_rp1_capital_efficiency_reconstruction -v`
Expected: PASS.
Run: `python -m unittest discover -s tests -p 'test_*.py' -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add runtime/yci0_rp1/capital_efficiency_reconstruction.py config/yci0_rp1/capital_efficiency_entities.v0.1.json tests/fixtures/yci0_rp1_g6 tests/test_yci0_rp1_capital_efficiency_reconstruction.py
git commit -m "feat(yci0-rp1): reconstruct G6 PIT economics"
```

---

### Task 4: Archive and Validate First-Party Evidence for Four Cohorts

**Files:**
- Create: `scripts/yci0_rp1_capital_efficiency_archive.py`
- Create: `.github/workflows/yci0-rp1-capital-efficiency-evidence.yml`
- Create: `tests/test_yci0_rp1_capital_efficiency_archive.py`
- Create after successful source proof: `docs/architecture/yci0_rp1/receipts/YCI0-RP1-G6-CAPITAL-EFFICIENCY-EVIDENCE.md`

**Interfaces:**
- Consumes: exact source locators and GAAP concept mappings frozen in `capital_efficiency_entities.v0.1.json`.
- Produces: private-S3 raw archives with SHA readback, non-secret archive receipt JSON, normalized filing facts, derived observation receipts. No database mutation in the archive script.

- [ ] **Step 1: RED-test archive manifest and authority leakage**

```python
def test_archive_manifest_requires_all_four_frozen_entities(self):
    self.assertEqual(set(manifest_entities()), {"MSFT", "NVDA", "ANET", "ETN"})

def test_archive_receipt_grants_zero_downstream_authority(self):
    receipt = synthetic_receipt()
    self.assertFalse(any(receipt["authority"].values()))
```

- [ ] **Step 2: Implement source acquisition with first-party priority**

For each entity, acquire at least eight consecutive filing quarters from SEC EDGAR company filings/XBRL facts or filed exhibits. Archive the raw bytes used for every required accounting fact to private S3 and SHA-readback. Do not mark PASS if a required GAAP concept cannot be mapped consistently through all required quarters; emit `UNKNOWN` with the exact semantic/accounting break.

- [ ] **Step 3: Validate all three mandatory metrics per representative**

Run locally against synthetic fixtures first. Then run the GitHub workflow with repository secrets. The workflow must fail closed unless each archived object readback hash matches and the non-secret receipt reports no authority leakage.

- [ ] **Step 4: Record the Reality receipt**

The receipt must name each entity/cohort, exact filing range, source regime, accounting mappings, invalidation events, archive paths/hashes, derived observations, and whether the entity is `QUALIFIED` or `UNKNOWN`. It must state explicitly that one-company-per-cohort is a coverage proof, not statistical representativeness.

- [ ] **Step 5: Commit**

```bash
git add scripts/yci0_rp1_capital_efficiency_archive.py .github/workflows/yci0-rp1-capital-efficiency-evidence.yml tests/test_yci0_rp1_capital_efficiency_archive.py docs/architecture/yci0_rp1/receipts/YCI0-RP1-G6-CAPITAL-EFFICIENCY-EVIDENCE.md
git commit -m "feat(yci0-rp1): archive G6 first-party evidence"
```

---

### Task 5: Production Admission, Physical Readback, and 6/6 Compile Attempt

**Files:**
- Create: `scripts/yci0_rp1_g6_admit.py`
- Create: `tests/test_yci0_rp1_g6_admit.py`
- Modify: `HANDOFF.md`
- Modify: `docs/architecture/yci0_rp1/YCI0-RP1-G0-G1-REALITY-STATUS.md`
- Update PR #102 body and existing Notion Human Workbench only after production readback.

**Interfaces:**
- Consumes: qualified Task-4 receipts plus existing 5/6 production Reality evidence.
- Produces: additive Supabase Source/Snapshot/Observation/Claim records, calculation receipts, G6 state, and either `FULL_REALITY_STATE_6_OF_6` or an explicit fail-closed `PARTIAL_REALITY_STATE_5_OF_6` with exact blocker. Notion remains `02 EVIDENCE / HOLD`.

- [ ] **Step 1: RED-test admission guardrails**

Tests require: all 12 mandatory metric identities PASS before G6 can be non-UNKNOWN; duplicate content hash is idempotent; no mutation when raw readback is absent; produced authority is only `RESEARCH`; a 6/6 card still returns transition suggestion `HOLD`.

- [ ] **Step 2: Implement additive admission script**

The script consumes a signed/non-secret machine receipt file produced by Task 4, validates hashes and contract identity, performs additive writes only, compiles Reality from physically read-back rows, and prints a deterministic state hash. No overwrite of prior 5/6 receipts.

- [ ] **Step 3: Run local full verification**

Run: `python -m unittest discover -s tests -p 'test_*.py' -v`
Expected: all tests PASS.
Run existing repository validation commands used by `repository-gates`.
Expected: PASS.

- [ ] **Step 4: Execute production admission and physical readback**

Only if all four cohorts are qualified: write G6 records, read back `Source → Snapshot → Observation → Claim Receipt`, compile 6/6, and store the new state card/runtime run. If any cohort is `UNKNOWN`, do not manufacture 6/6; preserve 5/6 and record the exact blocker.

- [ ] **Step 5: Synchronize Human surfaces without authority escalation**

Update PR #102, status doc, HANDOFF, and Notion. If 6/6 succeeds, Notion may say `FULL_REALITY_STATE_6_OF_6`, but `Journey Stage=02 EVIDENCE`, `Transition Suggestion=HOLD`, `Delta=UNKNOWN`, `Delta2=UNKNOWN`, Capital/Execution remain locked. If G6 fails closed, keep `PARTIAL_REALITY_STATE_5_OF_6` and state the blocker.

- [ ] **Step 6: Commit and push branch**

```bash
git add scripts/yci0_rp1_g6_admit.py tests/test_yci0_rp1_g6_admit.py HANDOFF.md docs/architecture/yci0_rp1/YCI0-RP1-G0-G1-REALITY-STATUS.md
git commit -m "feat(yci0-rp1): admit G6 reality with fail-closed readback"
git push origin yci0-rp1-live-evidence-20260917
```

- [ ] **Step 7: Verify PR and CI**

Require all PR workflows and `repository-gates` SUCCESS. PR #102 remains draft/open; do not merge. Record the final head SHA and exact G6/full-state status in HANDOFF.
