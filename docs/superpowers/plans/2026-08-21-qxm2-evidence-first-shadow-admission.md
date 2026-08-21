# QXM2 Evidence-First Shadow Admission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the QXM2 minimum sufficient Evidence Graph for the six accepted QXM1 Financial Mechanics candidates, producing schema-compatible Shadow TheoryObjects, proposed Shadow HypothesisObjects, and Benchmark Seeds without formal Registry admission, benchmark execution, capability promotion, or trading authority.

**Architecture:** QXM2 is an Evidence Staging Plane under `docs/architecture/qxm2/`. It reads the accepted QXM1 candidate identities as upstream authority, compiles primary-source and empirical evidence into atomic claim/mechanism relations, wraps formal-schema-compatible Theory/Hypothesis payloads in shadow envelopes, and prepares non-executable Benchmark Seeds. A deterministic validator checks structure, coverage, schema compatibility, PIT/falsification discipline, state transitions, and negative governance rules; Human Review remains the authority for scientific interpretation.

**Tech Stack:** Python 3.12, JSON, Markdown, `jsonschema==4.25.1`, `unittest`, GitHub Actions `repository-gates`, Git/GitHub PR governance.

**Spec:** `docs/superpowers/specs/2026-08-21-qxm2-evidence-first-shadow-admission-design.md`

## Global Constraints

- `Claim Authority <= Evidence Authority`.
- Shadow != Registry.
- Primary Source Verified != Theory Admitted.
- Theory Supported != Hypothesis Supported.
- Hypothesis Supported != Capability Qualified.
- Benchmark Specified != Benchmark Passed.
- Mechanism support != forecasting support.
- Harden exactly the six accepted QXM1 objects; do not rename, split, merge, replace, or add a seventh candidate.
- `CAP-R-01` remains inside `P.capital`; QXM2 may add only the accepted credit-transmission profile semantics.
- `CAP-V-01` remains Price-Implied Expectations; `Asset form is not pricing model` remains binding.
- All Shadow HypothesisObjects remain `status = proposed` in QXM2.
- QXM2 creates Benchmark Seeds only; formal `BenchmarkObject` creation and benchmark execution are not authorized.
- Do not modify `registry/theories/`, `registry/hypotheses/`, `registry/benchmarks/`, `registry/capabilities/`, or `canon/` during the QXM2 implementation PR.
- Qin Xiaoming material remains `practitioner_teaching_source` / internal synthesis authority only; it cannot self-promote to TheoryObject authority or independent empirical evidence.
- Do not store copyrighted full papers or long extracts. Store bibliographic identity, stable locators, concise mechanism paraphrases, claim boundaries, and source-role metadata.
- No target price, buy/sell/hold instruction, recommended weight, position size, broker action, or live execution.
- Human Acceptance token is `ACCEPT_QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING`.
- Merge authorization is separate and must use `AUTHORIZE_QXM2_MERGE` or an unambiguous equivalent instruction.

---

## File map

**Create during implementation**

- `docs/architecture/qxm2/QXM2-PRIMARY-THEORY-EVIDENCE-HARDENING-v0.1.md` — human-readable research synthesis and authority boundaries.
- `docs/architecture/qxm2/QXM2-PRIMARY-SOURCE-MATRIX-v0.1.json` — verified source identities, authority classes, candidate mappings, and source verification metadata.
- `docs/architecture/qxm2/QXM2-EMPIRICAL-EVIDENCE-MATRIX-v0.1.json` — EvidenceRelation objects linking sources to atomic claims.
- `docs/architecture/qxm2/QXM2-CLAIM-MECHANISM-CROSSWALK-v0.1.json` — canonical QXM2 claim/mechanism/observable/hypothesis/benchmark graph.
- `docs/architecture/qxm2/QXM2-SHADOW-THEORY-OBJECTS-v0.1.json` — TheoryObject-compatible payloads inside `shadow_only` envelopes.
- `docs/architecture/qxm2/QXM2-SHADOW-HYPOTHESIS-OBJECTS-v0.1.json` — HypothesisObject-compatible payloads inside `shadow_only` envelopes; all `proposed`.
- `docs/architecture/qxm2/QXM2-BENCHMARK-SEEDS-v0.1.json` — non-executable benchmark seeds.
- `docs/architecture/qxm2/QXM2-STATE.json` — governed stage projection.
- `docs/architecture/qxm2/QXM2-HUMAN-REVIEW-CARD-v0.1.md` — Human Epistemic Review card.
- `scripts/validate_qxm2_evidence_hardening.py` — deterministic structure/governance validator.
- `tests/test_qxm2_evidence_hardening.py` — focused unit tests and negative regression tests.

**Modify during implementation**

- `.github/workflows/ci.yml` — add `python scripts/validate_qxm2_evidence_hardening.py` after the QXM1 validator and before full unit tests.

**Conditional post-acceptance files**

- `docs/architecture/qxm2/QXM2-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json` — only after the Human Acceptance token is received.
- `docs/architecture/qxm2/QXM2-MERGE-RECEIPT-v0.1.json` — only after separate merge authorization and actual merge.

---

### Task 1: Isolate execution and establish validator primitives with TDD

**Files:**
- Create: `scripts/validate_qxm2_evidence_hardening.py`
- Create: `tests/test_qxm2_evidence_hardening.py`
- Create: `docs/architecture/qxm2/QXM2-STATE.json`

**Interfaces:**
- Consumes: `docs/architecture/qxm1/QXM1-STATE.json`, `docs/architecture/qxm1/QXM1-CANDIDATE-CONTRACTS-v0.1.json`, `packages/contracts/schemas/theory-object.schema.json`, `packages/contracts/schemas/hypothesis-object.schema.json`.
- Produces: reusable validator functions `require_fields()`, `assert_expected_candidate_ids()`, `assert_evidence_role()`, `assert_replication_status()`, `assert_shadow_hypothesis_state()`, `assert_benchmark_seed_authority()`, `assert_no_authority_regression()`.

- [ ] **Step 1: Create an isolated implementation worktree and branch**

Use `superpowers:using-git-worktrees` at execution time. Create the implementation branch from design commit `71a2fc3f84f202825815f7cb6dfb1f6abf17c175`:

```bash
git worktree add ../yuanli-invest-qxm2 -b qxm2/evidence-first-shadow-admission-v0.1 71a2fc3f84f202825815f7cb6dfb1f6abf17c175
cd ../yuanli-invest-qxm2
```

Verify:

```bash
git rev-parse HEAD
python -m pip install -r requirements-dev.txt
python scripts/validate_qxm1_candidate_pack.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: HEAD equals the design commit; QXM1 validator and existing tests pass before QXM2 changes.

- [ ] **Step 2: Write failing tests for validator primitives**

Create `tests/test_qxm2_evidence_hardening.py` with focused tests such as:

```python
import unittest

from scripts.validate_qxm2_evidence_hardening import (
    assert_benchmark_seed_authority,
    assert_evidence_role,
    assert_expected_candidate_ids,
    assert_replication_status,
    assert_shadow_hypothesis_state,
)

EXPECTED = [
    "QXM1-CAND-01-FUNDAMENTAL-DRIVER-DECOMPOSITION",
    "QXM1-CAND-02-THREE-STATEMENT-INTEGRITY",
    "QXM1-CAND-03-CREDIT-BALANCE-SHEET-TRANSMISSION",
    "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE",
    "QXM1-CAND-05-STRESS-EXIT-LIQUIDITY",
    "QXM1-CAND-06-RETURN-SOURCE-ATTRIBUTION",
]

class QXM2PrimitiveTests(unittest.TestCase):
    def test_candidate_identity_is_exact(self):
        assert_expected_candidate_ids(EXPECTED)
        with self.assertRaises(AssertionError):
            assert_expected_candidate_ids(EXPECTED + ["QXM2-CAND-07"])

    def test_evidence_roles_are_closed_enum(self):
        for role in ("supports", "contradicts", "boundary", "competing_mechanism"):
            assert_evidence_role(role)
        with self.assertRaises(AssertionError):
            assert_evidence_role("proves")

    def test_replication_gap_is_explicitly_legal(self):
        assert_replication_status("not_found")
        with self.assertRaises(AssertionError):
            assert_replication_status("")

    def test_shadow_hypothesis_cannot_preregister(self):
        assert_shadow_hypothesis_state("proposed")
        with self.assertRaises(AssertionError):
            assert_shadow_hypothesis_state("preregistered")

    def test_benchmark_seed_has_no_execution_authority(self):
        seed = {
            "formal_benchmark_status": "not_created",
            "benchmark_execution_authorized": False,
            "benchmark_pass_claim_authorized": False,
        }
        assert_benchmark_seed_authority(seed)
```

- [ ] **Step 3: Run the focused test and verify RED**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
```

Expected: import failure because `scripts/validate_qxm2_evidence_hardening.py` does not yet exist.

- [ ] **Step 4: Implement the minimum validator primitives**

Implement exact closed enums:

```python
EXPECTED_CANDIDATES = [
    "QXM1-CAND-01-FUNDAMENTAL-DRIVER-DECOMPOSITION",
    "QXM1-CAND-02-THREE-STATEMENT-INTEGRITY",
    "QXM1-CAND-03-CREDIT-BALANCE-SHEET-TRANSMISSION",
    "QXM1-CAND-04-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE",
    "QXM1-CAND-05-STRESS-EXIT-LIQUIDITY",
    "QXM1-CAND-06-RETURN-SOURCE-ATTRIBUTION",
]
EVIDENCE_ROLES = {"supports", "contradicts", "boundary", "competing_mechanism"}
REPLICATION_STATES = {
    "direct_replication_supported",
    "extension_supported",
    "mixed",
    "failed",
    "not_found",
    "not_applicable",
}

def assert_expected_candidate_ids(ids):
    assert ids == EXPECTED_CANDIDATES, ids

def assert_evidence_role(role):
    assert role in EVIDENCE_ROLES, role

def assert_replication_status(status):
    assert status in REPLICATION_STATES, status

def assert_shadow_hypothesis_state(status):
    assert status == "proposed", status

def assert_benchmark_seed_authority(seed):
    assert seed["formal_benchmark_status"] == "not_created"
    assert seed["benchmark_execution_authorized"] is False
    assert seed["benchmark_pass_claim_authorized"] is False
```

- [ ] **Step 5: Create initial QXM2 state projection**

`QXM2-STATE.json` begins with:

```json
{
  "schema_version": "0.1.0",
  "stage": "QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING",
  "status": "shadow_compilation_started",
  "upstream_dependency": {
    "stage": "QXM1_FINANCIAL_MECHANICS_CAPABILITY_CANDIDATE_PACK",
    "required_status": "accepted_merged",
    "merge_commit": "81bf6d83da7463e31c58e2d35bcabc291b580546",
    "merge_receipt": "docs/architecture/qxm1/QXM1-MERGE-RECEIPT-v0.1.json",
    "resolved": true
  },
  "candidate_count": 6,
  "admission_authority": "none",
  "benchmark_execution_authority": "none",
  "capability_promotion_authority": "none",
  "human_gate": {
    "token": "ACCEPT_QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING",
    "decision": "pending"
  },
  "next_gate": "QXM2_SOURCE_VERIFICATION"
}
```

- [ ] **Step 6: Run focused tests GREEN and commit**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
git add scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py docs/architecture/qxm2/QXM2-STATE.json
git commit -m "test(qxm2): establish evidence hardening validator primitives"
```

---

### Task 2: Compile Reality Mechanics primary sources and evidence relations

**Files:**
- Create: `docs/architecture/qxm2/QXM2-PRIMARY-SOURCE-MATRIX-v0.1.json`
- Create: `docs/architecture/qxm2/QXM2-EMPIRICAL-EVIDENCE-MATRIX-v0.1.json`
- Create: `docs/architecture/qxm2/QXM2-PRIMARY-THEORY-EVIDENCE-HARDENING-v0.1.md`
- Modify: `tests/test_qxm2_evidence_hardening.py`
- Modify: `scripts/validate_qxm2_evidence_hardening.py`

**Interfaces:**
- Produces source IDs and evidence-relation IDs used by the later Claim Crosswalk and Shadow Theory pack.
- Primary research batch covers `QXM1-CAND-01` and `QXM1-CAND-02` only; later tasks append the remaining four candidates.

- [ ] **Step 1: Verify primary-source identities for Fundamental Driver Decomposition**

Research and open the primary/publisher record for these exact targets before writing them to JSON:

- Lev & Thiagarajan (1993), *Fundamental Information Analysis*.
- Abarbanell & Bushee (1997), *Fundamental Analysis, Future Earnings, and Stock Prices*.
- Nissim & Penman (2001), *Ratio Analysis and Equity Valuation: From Research to Practice*.

For each source record: verify title, authors, year, journal/publisher, stable locator, whether the primary source was opened, and a concise mechanism/claim boundary. Do not infer causal identification from predictive association.

- [ ] **Step 2: Verify primary and competing sources for Three-Statement Integrity**

Research and open primary/publisher records for:

- Dechow (1994), *Accounting Earnings and Cash Flows as Measures of Firm Performance: The Role of Accounting Accruals*.
- Sloan (1996), *Do Stock Prices Fully Reflect Information in Accruals and Cash Flows about Future Earnings?*
- Dechow & Dichev (2002), accrual-quality / working-capital estimation-error paper.
- Richardson, Sloan, Soliman & Tuna (2005), accrual reliability / earnings persistence paper.
- Fairfield, Whisenant & Yohn (2003), growth-based competing explanation for accrued earnings effects.
- IAS 7 from the official IFRS source as `normative_accounting_standard`, explicitly excluded from Shadow TheoryObject creation.

- [ ] **Step 3: Write failing coverage tests**

Add tests requiring at least two seminal anchors, one empirical relation, and one boundary/competing relation for each of the two candidates. The test should load the two JSON files and count relations by `candidate_id` and `role`.

- [ ] **Step 4: Run focused tests RED**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
```

Expected: failure because source/evidence JSON files are absent or incomplete.

- [ ] **Step 5: Create source and EvidenceRelation records**

Every source record must contain at least:

```json
{
  "source_id": "QXM2-SRC-DECHOW-1994",
  "candidate_ids": ["QXM1-CAND-02-THREE-STATEMENT-INTEGRITY"],
  "title": "Accounting Earnings and Cash Flows as Measures of Firm Performance: The Role of Accounting Accruals",
  "authors": ["Patricia M. Dechow"],
  "year": 1994,
  "source_locator": "verified stable DOI or publisher locator",
  "authority_class": "primary_empirical_research",
  "source_class": "original_paper",
  "primary_source_opened": true,
  "bibliographic_identity_verified": true,
  "mechanism_extraction_status": "verified",
  "claim_boundary_status": "verified",
  "fulltext_stored": false
}
```

Every EvidenceRelation uses the Section 3 closed roles and contains `identification_strength`, sample/time domain, `replication_status`, external-validity boundary, PIT usability, observable mapping, and explicit `what_it_supports` / `what_it_does_not_support`.

- [ ] **Step 6: Run focused tests GREEN and commit**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
git add docs/architecture/qxm2 scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "research(qxm2): compile reality mechanics evidence batch"
```

---

### Task 3: Compile Credit Transmission and Discount-Rate evidence batch

**Files:**
- Modify: `QXM2-PRIMARY-SOURCE-MATRIX-v0.1.json`
- Modify: `QXM2-EMPIRICAL-EVIDENCE-MATRIX-v0.1.json`
- Modify: `QXM2-PRIMARY-THEORY-EVIDENCE-HARDENING-v0.1.md`
- Modify: tests and validator.

**Interfaces:** Adds coverage for QXM1 candidates 03 and 04 without changing mother capability identities.

- [ ] **Step 1: Verify credit-transmission source set**

Primary/seminal targets:

- Bernanke & Gertler (1989), agency costs / net worth / business fluctuations.
- Kiyotaki & Moore (1997), collateral-credit feedback / credit cycles.
- Schularick & Taylor (2012), long-run credit booms and financial crises.
- Jordà–Schularick–Taylor long-horizon leveraged-boom / recession-severity evidence; verify the exact primary bibliographic identity before assigning its final `source_id`.

The evidence graph must distinguish `mechanism_theory` from `historical_empirical_anchor`. Aggregate credit correlation cannot receive a causal role unless sector/balance-sheet mechanism evidence is separately linked.

- [ ] **Step 2: Verify opportunity-cost / discount-rate source set**

Targets:

- Sharpe (1964), capital asset prices / risk pricing assumptions.
- Campbell & Shiller (1988), present-value decomposition of dividend-price ratios.
- Cochrane (2011), discount-rate variation as central asset-pricing state.
- Welch & Goyal (2008), OOS equity-premium prediction skepticism as a boundary/competing empirical relation.

The graph must state explicitly that expectation decomposition may be useful even when forecasting does not beat simple OOS baselines.

- [ ] **Step 3: Extend coverage tests, run RED, populate data, run GREEN**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
```

Before data changes: expect missing-coverage failures for candidates 03/04. After adding verified source and evidence relations: all four covered candidates pass.

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/qxm2 scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "research(qxm2): compile pricing and credit transmission evidence"
```

---

### Task 4: Compile Stress Liquidity and Return Attribution evidence batch

**Files:** Same matrix/narrative/test/validator files as Tasks 2-3.

**Interfaces:** Completes source verification for candidates 05 and 06; after GREEN, all six candidates satisfy source/empirical/boundary minimums.

- [ ] **Step 1: Verify stress-liquidity source set**

Targets:

- Kyle (1985), market depth / price impact.
- Amihud (2002), illiquidity proxy and asset-pricing relation.
- Pástor & Stambaugh (2003), systematic liquidity risk.
- Brunnermeier & Pedersen (2009), market-liquidity / funding-liquidity feedback.

Classify transaction liquidity, market liquidity, liquidity risk, and funding liquidity separately. `ADV` must never be treated as sufficient stress-exit evidence.

- [ ] **Step 2: Verify return-attribution source set**

Targets:

- Brinson, Hood & Beebower (1986), portfolio performance attribution.
- Campbell (1991), cash-flow-news / expected-return-news decomposition.
- Fama & French (1993), common risk-factor decomposition.
- Ibbotson & Kaplan (2000), boundary around the interpretation of asset-allocation explanatory percentages.

The graph must distinguish accounting identity, factor exposure, and causal interpretation; later P&L cannot rewrite the immutable original ResearchReceipt.

- [ ] **Step 3: Extend tests and complete source-verification state**

After all six candidates satisfy source quotas, update `QXM2-STATE.json`:

```json
"status": "source_verification_complete",
"next_gate": "QXM2_MECHANISM_COMPILATION"
```

Run:

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
python scripts/validate_qxm2_evidence_hardening.py
```

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/qxm2 scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "research(qxm2): complete six-candidate source verification"
```

---

### Task 5: Build the canonical Claim–Mechanism Crosswalk

**Files:**
- Create: `QXM2-CLAIM-MECHANISM-CROSSWALK-v0.1.json`
- Modify: tests and validator.

**Interfaces:** Each atomic claim references existing `source_id` / `relation_id`; later Shadow Hypothesis and Benchmark Seed IDs point back to these claims.

- [ ] **Step 1: Freeze claim ID families**

Use these exact prefixes and 3-6 atomic claims per candidate:

- `CLAIM-P003-*` — driver decomposition, incremental information, definition stability, arithmetic-vs-causal boundary.
- `CLAIM-P004-*` — accrual matching, cash/accrual persistence, accrual reliability, growth competing explanation, diagnostic-not-fraud boundary.
- `CLAIM-R01QXM1-*` — borrower net worth, collateral feedback, sectoral credit transmission, aggregate-correlation boundary.
- `CLAIM-V01QXM1-*` — cash-flow/discount-rate decomposition, asset-routed opportunity cost, identification ambiguity, OOS forecasting boundary.
- `CLAIM-S004-*` — price impact, liquidity-risk commonality, funding-liquidity spiral, ADV insufficiency.
- `CLAIM-CROSS001-*` — return identity reconstruction, asset-form routing, factor/news attribution, thesis-fidelity boundary.

Each claim must contain `claim_id`, `candidate_id`, `statement`, `mechanism_ids`, `support_relation_ids`, `boundary_relation_ids`, `observable_set`, `falsifier`, `shadow_hypothesis_ids`, and `benchmark_seed_ids`.

- [ ] **Step 2: Write RED referential-integrity tests**

Tests must fail if any claim points to an unknown source/evidence relation, lacks a falsifier, or lacks both support and boundary/competing evidence.

- [ ] **Step 3: Populate crosswalk and run GREEN**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
```

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/qxm2/QXM2-CLAIM-MECHANISM-CROSSWALK-v0.1.json scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "feat(qxm2): compile atomic claim mechanism crosswalk"
```

---

### Task 6: Compile Shadow TheoryObjects and proposed Shadow HypothesisObjects

**Files:**
- Create: `QXM2-SHADOW-THEORY-OBJECTS-v0.1.json`
- Create: `QXM2-SHADOW-HYPOTHESIS-OBJECTS-v0.1.json`
- Modify: tests and validator.

**Interfaces:** Embedded `theory_object` payloads validate against `theory-object.schema.json`; embedded `hypothesis_object` payloads validate against `hypothesis-object.schema.json`.

- [ ] **Step 1: Write schema-compatibility tests RED**

Use `jsonschema.Draft202012Validator` to validate every embedded payload against the existing schemas. Add negative tests proving `status=preregistered` fails QXM2 even though the formal schema would allow it.

- [ ] **Step 2: Build Shadow TheoryObject envelopes**

Required envelope fields:

```json
{
  "shadow_object_id": "QXM2-SHADOW-THEORY-001",
  "admission_state": "shadow_only",
  "admission_readiness": "source_verified",
  "candidate_targets": ["QXM1-CAND-01-FUNDAMENTAL-DRIVER-DECOMPOSITION"],
  "theory_object": {},
  "verification": {
    "primary_source_opened": true,
    "bibliographic_identity_verified": true,
    "mechanism_extracted_from_primary_source": true,
    "claim_boundary_verified": true
  },
  "admission_authority": "none"
}
```

IAS 7 remains in the source/evidence matrices as normative accounting authority and must not be serialized as a TheoryObject.

- [ ] **Step 3: Build at least two proposed Shadow Hypotheses per candidate**

Use these exact ID seeds:

- `HYP-P-201-DRIVER-INCREMENTAL-OOS`
- `HYP-P-202-DRIVER-REGIME-STABILITY`
- `HYP-P-203-CASH-CONVERSION-PERSISTENCE`
- `HYP-P-204-ACCRUAL-RELIABILITY`
- `HYP-P-205-CREDIT-SECTORAL-TRANSMISSION`
- `HYP-P-206-COLLATERAL-FEEDBACK`
- `HYP-V-201-EXPECTATION-DECOMPOSITION`
- `HYP-V-202-OOS-DISCOUNT-RATE`
- `HYP-S-201-STRESS-LIQUIDITY-INCREMENTAL`
- `HYP-S-202-FUNDING-LIQUIDITY-SPIRAL`
- `HYP-CROSS-201-RETURN-IDENTITY-RECONSTRUCTION`
- `HYP-CROSS-202-THESIS-FIDELITY`

Every payload must include a real null hypothesis, target variable, horizon, eligible universe, conditioning state, expected direction, falsification rule, `point_in_time_requirement=true`, and `status="proposed"`.

- [ ] **Step 4: Run schema tests GREEN**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
python scripts/validate_qxm2_evidence_hardening.py
```

- [ ] **Step 5: Commit**

```bash
git add docs/architecture/qxm2/QXM2-SHADOW-* scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "feat(qxm2): compile shadow theory and hypothesis objects"
```

---

### Task 7: Compile six non-executable Benchmark Seeds

**Files:**
- Create: `QXM2-BENCHMARK-SEEDS-v0.1.json`
- Modify: tests, validator, state.

**Interfaces:** One minimum seed per candidate; each references at least one Shadow Hypothesis ID and one simpler baseline.

- [ ] **Step 1: Write Benchmark Seed negative tests RED**

Fail when a seed omits PIT/OOS/regime holdout, has no simpler baseline, sets formal benchmark state to anything except `not_created`, or enables execution/PASS authority.

- [ ] **Step 2: Create these six seed identities**

- `QXM2-BSEED-P003-DRIVER-OOS`
- `QXM2-BSEED-P004-CASH-CONVERSION`
- `QXM2-BSEED-R01-CREDIT-TRANSMISSION`
- `QXM2-BSEED-V01-EXPECTATION-DECOMPOSITION`
- `QXM2-BSEED-S004-STRESS-EXIT`
- `QXM2-BSEED-CROSS001-RETURN-ATTRIBUTION`

Each seed must contain target, horizon, candidate model, simpler baselines, PIT policy, OOS policy, regime holdout, primary metrics, failure metrics, leakage risks, multiple-testing risk, and the three explicit non-authority fields.

- [ ] **Step 3: Update state to mechanism compilation complete**

Only after the crosswalk, Shadow objects, and all six seeds validate:

```json
"status": "mechanism_compilation_complete",
"next_gate": "QXM2_MACHINE_QUALIFICATION"
```

- [ ] **Step 4: Run focused and full local verification**

```bash
python scripts/validate_qxm2_evidence_hardening.py
python -m unittest tests.test_qxm2_evidence_hardening -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 5: Commit**

```bash
git add docs/architecture/qxm2 scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "feat(qxm2): add falsifiable benchmark seeds"
```

---

### Task 8: Harden full validator, scope guard, and research narrative

**Files:**
- Modify: `scripts/validate_qxm2_evidence_hardening.py`
- Modify: `tests/test_qxm2_evidence_hardening.py`
- Modify: `QXM2-PRIMARY-THEORY-EVIDENCE-HARDENING-v0.1.md`

**Interfaces:** Full validator entrypoint `validate_qxm2(ROOT)` and command-line `main()`.

- [ ] **Step 1: Add full-file validation**

The validator must verify:

1. QXM1 upstream state is `accepted_merged` and merge commit equals `81bf6d83da7463e31c58e2d35bcabc291b580546`.
2. Exactly six candidate IDs match QXM1 order and identities.
3. Per candidate: ≥2 theory/seminal anchors, ≥1 independent empirical relation, ≥1 boundary/contradict/competing relation, 3-6 atomic claims, ≥2 proposed Shadow Hypotheses, ≥1 Benchmark Seed.
4. Every EvidenceRelation has closed role, explicit identification strength, domain/time/sample scope, replication status, external validity, PIT usability, observable mapping, and support/boundary text.
5. All embedded Theory/Hypothesis payloads validate against existing schemas.
6. No `THEORY-QIN*` object can appear.
7. No scalar evidence score or paper-count vote determines admission.
8. No silent `primary_source_verified -> theory_admitted` or `supports -> hypothesis_supported` transition.
9. State transitions use only the frozen QXM2 state machine.

- [ ] **Step 2: Add PR-time prohibited-path scope guard**

While QXM2 is not `accepted_merged`, compute the branch diff against the merge-base of `origin/main` and fail if any changed path starts with:

```python
PROHIBITED_PREFIXES = (
    "registry/theories/",
    "registry/hypotheses/",
    "registry/benchmarks/",
    "registry/capabilities/",
    "canon/",
)
```

Use `git merge-base origin/main HEAD` plus `git diff --name-only <base>...HEAD`. Because checkout uses `fetch-depth: 0`, this is available in CI. After QXM2 reaches `accepted_merged`, later stages may change Registry under their own authority; the QXM2 validator should then validate its merge receipt boundaries rather than permanently freeze Registry forever.

- [ ] **Step 3: Add authority-regression negative tests**

Explicitly test that these strings/states fail: target price, recommended weight, position size, buy/sell instruction, `benchmark_passed=true`, `registry_admission=true`, `capability_promotion=true`, `live_execution=true`, or Shadow Hypothesis state beyond `proposed`.

- [ ] **Step 4: Finalize human-readable research note**

The note must explain the six evidence graphs, source-authority distinctions, major competing evidence, replication gaps, and admission recommendations without claiming scientific truth from machine validation.

- [ ] **Step 5: Verify and commit**

```bash
python scripts/validate_qxm2_evidence_hardening.py
python -m unittest tests.test_qxm2_evidence_hardening -v
python -m unittest discover -s tests -p 'test_*.py' -v
git add docs/architecture/qxm2 scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "test(qxm2): harden evidence and authority gates"
```

---

### Task 9: Wire CI, open PR, machine-qualify, and prepare Human Review

**Files:**
- Modify: `.github/workflows/ci.yml`
- Create: `QXM2-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `QXM2-STATE.json`

**Interfaces:** CI produces the machine qualification used by Human Review; Human Review remains pending.

- [ ] **Step 1: Write the CI change**

Insert immediately after QXM1 validator:

```yaml
      - run: python scripts/validate_qxm1_candidate_pack.py
      - run: python scripts/validate_qxm2_evidence_hardening.py
      - run: python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 2: Run complete local gate**

```bash
python scripts/validate_repository.py
python scripts/validate_qxm1_candidate_pack.py
python scripts/validate_qxm2_evidence_hardening.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all commands exit 0.

- [ ] **Step 3: Commit and open PR**

```bash
git add .github/workflows/ci.yml
git commit -m "ci(qxm2): add evidence hardening gate"
```

Open PR title:

`QXM2: harden Financial Mechanics primary theory and empirical evidence`

PR body must say `Evidence-First Shadow Admission`, list the six candidates, state `Registry admissions = 0`, and explicitly state that benchmark execution / capability promotion / production runtime / trading are not authorized.

- [ ] **Step 4: Wait for exact-head `repository-gates` and record the first successful machine qualification**

Require `contracts=success` and `governance=success`, with QXM2 validator and full unit tests successful inside `contracts`.

- [ ] **Step 5: Advance state and create Human Review Card**

After the first successful qualification, update state to:

```json
"status": "shadow_admission_ready_for_human_review",
"machine_qualification": {
  "validated_head_sha": "<actual qualified SHA>",
  "workflow": "repository-gates",
  "run_number": "<actual run number>",
  "run_id": "<actual run id>",
  "conclusion": "success"
},
"next_gate": "QXM2_HUMAN_REVIEW"
```

The Human Review Card must evaluate at least: theory fit, mechanism fidelity, identification, contradictory/competing evidence, replication/external validity, operationalization/PIT testability, and per-candidate admission recommendation. Recommendations may differ (`advance`, `advance_with_boundary`, `interpretation_only`, `keep_shadow`, `reject_or_revise`) even if the overall evidence-hardening process is accepted.

- [ ] **Step 6: Push the Human Review head and require a new exact-head CI success**

Do not recursively rewrite the exact final CI run into the same commit. Record the final exact-head run in the PR body, as an external Git runtime fact.

- [ ] **Step 7: Stop at Human Gate**

Do not create an acceptance receipt and do not merge. Present the Human Review result and request only:

`ACCEPT_QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING`

---

### Task 10: Conditional Human Acceptance and post-acceptance qualification

**Precondition:** The user has explicitly issued `ACCEPT_QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING`.

**Files:**
- Create: `QXM2-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json`
- Modify: `QXM2-STATE.json`
- Modify: validator tests if needed to validate accepted states.

- [ ] **Step 1: Create the immutable Human Acceptance Receipt**

Record the reviewed exact-head SHA and Human Review CI run, per-candidate admission recommendations, and boundaries:

```json
"boundaries_preserved": {
  "merge_authorized": false,
  "registry_admission_authorized": false,
  "hypothesis_preregistration_authorized": false,
  "formal_benchmark_creation_authorized": false,
  "benchmark_execution_authorized": false,
  "capability_promotion_authorized": false,
  "trading_action_authorized": false,
  "live_execution": false
}
```

- [ ] **Step 2: Move state to `human_accepted_pending_post_acceptance_ci` as a transient validator-supported state**

Although the design diagram compresses acceptance to `human_accepted_ready_for_merge`, implementation should use a transient post-acceptance-CI state, matching QXM1 governance practice, so acceptance cannot silently imply CI closure.

- [ ] **Step 3: Run exact-head post-acceptance CI**

Require the same repository gates. On success, update state to `human_accepted_ready_for_merge`, record the successful post-acceptance qualification, and keep `merge_authority = not_implied_by_acceptance`.

- [ ] **Step 4: Run one more exact-head CI if the state update changes HEAD**

Only after that run is successful is the merge gate ready.

- [ ] **Step 5: Stop at merge authority**

Request `AUTHORIZE_QXM2_MERGE`. Do not merge without it.

---

### Task 11: Conditional authorized merge and post-merge closure

**Precondition:** The user explicitly authorizes `AUTHORIZE_QXM2_MERGE`.

**Files:**
- Create after merge on closure branch: `QXM2-MERGE-RECEIPT-v0.1.json`
- Modify: `QXM2-STATE.json`
- Modify: validator to recognize `accepted_merged` and validate merge receipt.

- [ ] **Step 1: Re-check exact pre-merge HEAD and CI**

Use verification-before-completion discipline. Merge only if the current exact head has successful required checks.

- [ ] **Step 2: Squash-merge the QXM2 implementation PR**

Record actual merge commit and merged timestamp.

- [ ] **Step 3: Create a post-merge closure branch from new `main`**

Add `QXM2-MERGE-RECEIPT-v0.1.json` recording Human Acceptance token, merge authorization, pre-merge exact head, pre-merge CI run, merge method, merge commit, accepted Shadow Pack identity, all preserved non-authorities, and next gate:

`QXM3_THEORY_HYPOTHESIS_REGISTRY_ADMISSION_BENCHMARK_PREREGISTRATION`

- [ ] **Step 4: Advance state to `accepted_merged` and validate closure**

The final state must still report:

```json
"registry_admission_authority": "none",
"hypothesis_preregistration_authority": "none",
"benchmark_execution_authority": "none",
"capability_promotion_authority": "none"
```

- [ ] **Step 5: Run closure exact-head CI and merge the closure PR only if green**

This closure is governance bookkeeping only and does not start QXM3.

---

## Final verification checklist

Before claiming QXM2 complete, run and read fresh outputs for:

```bash
python scripts/validate_qxm1_candidate_pack.py
python scripts/validate_qxm2_evidence_hardening.py
python -m unittest tests.test_qxm2_evidence_hardening -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

Then verify repository facts:

```bash
git diff --name-only <implementation-base>...HEAD
git status --short
git rev-parse HEAD
```

For the implementation PR, confirm no changed path begins with `registry/theories/`, `registry/hypotheses/`, `registry/benchmarks/`, `registry/capabilities/`, or `canon/`. Confirm the exact-head `repository-gates` run is successful before presenting Human Review, and again after Human Acceptance before requesting merge authority.

## Expected end state

A completed, merged QXM2 does **not** assert that all six capabilities are scientifically proven. It establishes a machine-readable, reviewable Evidence Graph with explicit support, contradiction, boundaries, replication status, proposed hypotheses, and non-executable benchmark seeds. QXM3 may then selectively admit only Human-approved Theory/Hypothesis objects and compile Benchmark Seeds into formal preregistered BenchmarkObjects under a separate authority gate.