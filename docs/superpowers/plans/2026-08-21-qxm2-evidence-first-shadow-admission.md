# QXM2 Evidence-First Shadow Admission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the minimum sufficient, machine-readable Evidence Graph for the six accepted QXM1 Financial Mechanics candidates, producing schema-compatible Shadow TheoryObjects, `proposed` Shadow HypothesisObjects, and non-executable Benchmark Seeds without formal Registry admission, benchmark execution, capability promotion, or trading authority.

**Architecture:** QXM2 is an Evidence Staging Plane under `docs/architecture/qxm2/`. It treats QXM1 candidate identities as immutable upstream authority, compiles verified primary sources and empirical relations into atomic claims and mechanisms, then turns those claims into schema-compatible shadow objects and falsifiable benchmark seeds. Deterministic CI validates structure, coverage, PIT/falsification discipline, state transitions, and negative authority constraints; Human Review alone judges epistemic fit and admission recommendation.

**Tech Stack:** Python 3.12, JSON, Markdown, `jsonschema==4.25.1`, `unittest`, GitHub Actions `repository-gates`, Git/GitHub PR governance.

**Spec:** `docs/superpowers/specs/2026-08-21-qxm2-evidence-first-shadow-admission-design.md`

**Written spec approval:** `ACCEPT_QXM2_WRITTEN_DESIGN_SPEC`

## Global Constraints

- `Claim Authority <= Evidence Authority`.
- Shadow != Registry.
- Primary Source Verified != Theory Admitted.
- Theory Supported != Hypothesis Supported.
- Hypothesis Supported != Capability Qualified.
- Benchmark Specified != Benchmark Passed.
- Mechanism support != forecasting support.
- Harden exactly the six accepted QXM1 objects; do not rename, split, merge, replace, or add a seventh candidate.
- `CAP-R-01` remains inside `P.capital`; QXM2 may only harden the accepted credit-transmission profile.
- `CAP-V-01` remains Price-Implied Expectations; `Asset form is not pricing model` remains binding.
- All QXM2 Shadow HypothesisObjects remain `status = proposed`.
- QXM2 creates Benchmark Seeds only; no formal `BenchmarkObject` is created in this stage.
- Do not modify `registry/theories/`, `registry/hypotheses/`, `registry/benchmarks/`, `registry/capabilities/`, or `canon/` in the QXM2 implementation PR.
- Qin Xiaoming material remains practitioner teaching/internal synthesis authority only and cannot self-promote into TheoryObject authority or independent empirical evidence.
- Do not store full copyrighted papers or long excerpts; store bibliographic identity, stable source locators, concise paraphrases, claim boundaries, and evidence-role metadata.
- No target price, buy/sell/hold instruction, recommended weight, position size, broker action, or live execution.
- Human Acceptance token: `ACCEPT_QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING`.
- Merge requires a separate `AUTHORIZE_QXM2_MERGE` authority.

---

## File Map

**Create during implementation**

- `docs/architecture/qxm2/QXM2-PRIMARY-THEORY-EVIDENCE-HARDENING-v0.1.md`
- `docs/architecture/qxm2/QXM2-PRIMARY-SOURCE-MATRIX-v0.1.json`
- `docs/architecture/qxm2/QXM2-EMPIRICAL-EVIDENCE-MATRIX-v0.1.json`
- `docs/architecture/qxm2/QXM2-CLAIM-MECHANISM-CROSSWALK-v0.1.json`
- `docs/architecture/qxm2/QXM2-SHADOW-THEORY-OBJECTS-v0.1.json`
- `docs/architecture/qxm2/QXM2-SHADOW-HYPOTHESIS-OBJECTS-v0.1.json`
- `docs/architecture/qxm2/QXM2-BENCHMARK-SEEDS-v0.1.json`
- `docs/architecture/qxm2/QXM2-HUMAN-REVIEW-CARD-v0.1.md`
- `docs/architecture/qxm2/QXM2-STATE.json`
- `scripts/validate_qxm2_evidence_hardening.py`
- `tests/test_qxm2_evidence_hardening.py`

**Modify during implementation**

- `.github/workflows/ci.yml`

**Create only after later explicit gates**

- `docs/architecture/qxm2/QXM2-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json` — after Human Acceptance.
- `docs/architecture/qxm2/QXM2-MERGE-RECEIPT-v0.1.json` — after separately authorized merge.

---

### Task 1: Create the isolated execution branch and TDD validator primitives

**Files:**
- Create: `scripts/validate_qxm2_evidence_hardening.py`
- Create: `tests/test_qxm2_evidence_hardening.py`
- Create: `docs/architecture/qxm2/QXM2-STATE.json`

**Interfaces:**
- Consumes: accepted QXM1 state/contracts and existing Theory/Hypothesis schemas.
- Produces: `require_fields()`, `assert_expected_candidate_ids()`, `assert_evidence_role()`, `assert_replication_status()`, `assert_shadow_hypothesis_state()`, `assert_benchmark_seed_authority()`, `assert_no_authority_regression()`.

- [ ] **Step 1: Use `superpowers:using-git-worktrees` and create the implementation worktree**

```bash
git worktree add ../yuanli-invest-qxm2 -b qxm2/evidence-first-shadow-admission-v0.1 71a2fc3f84f202825815f7cb6dfb1f6abf17c175
cd ../yuanli-invest-qxm2
```

- [ ] **Step 2: Verify the untouched baseline**

```bash
git rev-parse HEAD
python -m pip install -r requirements-dev.txt
python scripts/validate_qxm1_candidate_pack.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected HEAD: `71a2fc3f84f202825815f7cb6dfb1f6abf17c175`. Existing QXM1 validator and unit tests must pass before QXM2 changes.

- [ ] **Step 3: Write RED tests for closed enums and authority rules**

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

    def test_evidence_role_rejects_proof_language(self):
        for role in ("supports", "contradicts", "boundary", "competing_mechanism"):
            assert_evidence_role(role)
        with self.assertRaises(AssertionError):
            assert_evidence_role("proves")

    def test_replication_gap_must_be_explicit(self):
        assert_replication_status("not_found")
        with self.assertRaises(AssertionError):
            assert_replication_status("")

    def test_shadow_hypothesis_cannot_preregister(self):
        assert_shadow_hypothesis_state("proposed")
        with self.assertRaises(AssertionError):
            assert_shadow_hypothesis_state("preregistered")

    def test_benchmark_seed_has_no_execution_authority(self):
        assert_benchmark_seed_authority({
            "formal_benchmark_status": "not_created",
            "benchmark_execution_authorized": False,
            "benchmark_pass_claim_authorized": False,
        })
```

- [ ] **Step 4: Run RED**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
```

Expected: import failure because the QXM2 validator does not yet exist.

- [ ] **Step 5: Implement minimum primitives**

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

- [ ] **Step 6: Create initial state**

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

- [ ] **Step 7: Run GREEN and commit**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
git add scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py docs/architecture/qxm2/QXM2-STATE.json
git commit -m "test(qxm2): establish evidence hardening validator primitives"
```

---

### Task 2: Compile the Reality Mechanics evidence batch

**Files:**
- Create: `QXM2-PRIMARY-SOURCE-MATRIX-v0.1.json`
- Create: `QXM2-EMPIRICAL-EVIDENCE-MATRIX-v0.1.json`
- Create: `QXM2-PRIMARY-THEORY-EVIDENCE-HARDENING-v0.1.md`
- Modify: validator and tests.

**Interfaces:** Establish source/evidence IDs for QXM1 candidates 01 and 02; later tasks append candidates 03-06 without changing prior IDs.

- [ ] **Step 1: Verify Fundamental Driver primary sources from primary/publisher records**

Research and open these targets:

- Lev & Thiagarajan (1993), *Fundamental Information Analysis*.
- Abarbanell & Bushee (1997), *Fundamental Analysis, Future Earnings, and Stock Prices*.
- Nissim & Penman (2001), *Ratio Analysis and Equity Valuation: From Research to Practice*.

For every source, verify title, authors, year, journal/publisher, stable locator, mechanism claim, and claim boundary. Predictive association must not be relabeled causal identification.

- [ ] **Step 2: Verify Three-Statement primary, competing, and normative sources**

Research and open:

- Dechow (1994), *Accounting Earnings and Cash Flows as Measures of Firm Performance: The Role of Accounting Accruals*.
- Sloan (1996), *Do Stock Prices Fully Reflect Information in Accruals and Cash Flows about Future Earnings?*
- Dechow & Dichev (2002), accrual-quality / working-capital estimation-error paper.
- Richardson, Sloan, Soliman & Tuna (2005), accrual reliability / earnings persistence paper.
- Fairfield, Whisenant & Yohn (2003), growth-based competing explanation.
- IAS 7 from the official IFRS source, classified as `normative_accounting_standard` and explicitly excluded from Shadow TheoryObject creation.

- [ ] **Step 3: Write coverage tests RED**

Require per candidate: at least 2 theory/seminal anchors, 1 independent empirical relation, and 1 `boundary`, `contradicts`, or `competing_mechanism` relation.

- [ ] **Step 4: Create source records using verified locators**

For Dechow (1994), the source record can use the verified DOI locator `https://doi.org/10.1016/0165-4101(94)90016-7` after confirming it against the publisher record. Record `fulltext_stored=false`.

- [ ] **Step 5: Create EvidenceRelation records**

Each relation must include:

```text
relation_id
candidate_id
claim_id
mechanism_id
source_id
source_class
original_or_secondary
publication_year
role
identification_strength
direction
magnitude_relevance
sample_domain
geography
asset_class
period
frequency
replication_status
external_validity
known_failures
pit_usable
observable_mapping
benchmark_relevance
what_it_supports
what_it_does_not_support
```

- [ ] **Step 6: Run GREEN and commit**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
git add docs/architecture/qxm2 scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "research(qxm2): compile reality mechanics evidence"
```

---

### Task 3: Compile Credit Transmission and Discount-Rate evidence

**Files:** Modify the source matrix, evidence matrix, research note, validator, and tests.

- [ ] **Step 1: Verify Credit Transmission sources**

- Bernanke & Gertler (1989), borrower net worth / agency-cost transmission.
- Kiyotaki & Moore (1997), collateral-credit feedback / credit cycles.
- Schularick & Taylor (2012), long-run credit boom / crisis evidence.
- Jordà–Schularick–Taylor long-horizon leveraged-boom / recession-severity evidence; verify exact primary bibliographic identity before assigning its final source ID.

Keep mechanism theory distinct from historical empirical anchor. Aggregate credit association alone cannot receive causal-transmission authority.

- [ ] **Step 2: Verify Discount-Rate / Opportunity-Cost sources**

- Sharpe (1964), equilibrium risk pricing assumptions.
- Campbell & Shiller (1988), present-value cash-flow / discount-rate decomposition.
- Cochrane (2011), discount-rate variation.
- Welch & Goyal (2008), OOS predictor skepticism as boundary evidence.

The evidence graph must permit an `interpretation_only` recommendation when decomposition is useful but forecasting lacks OOS support.

- [ ] **Step 3: Extend tests, run RED, add records, run GREEN**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
```

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/qxm2 scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "research(qxm2): compile credit and discount-rate evidence"
```

---

### Task 4: Compile Stress Liquidity and Return Attribution evidence

**Files:** Modify the same matrix/note/validator/test set.

- [ ] **Step 1: Verify Stress Liquidity sources**

- Kyle (1985), market depth / price impact.
- Amihud (2002), illiquidity proxy and pricing relation.
- Pástor & Stambaugh (2003), systematic liquidity risk.
- Brunnermeier & Pedersen (2009), market-liquidity / funding-liquidity feedback.

Keep transaction liquidity, market liquidity, liquidity risk, and funding liquidity separate. ADV alone cannot imply stress-exit quality.

- [ ] **Step 2: Verify Return Attribution sources**

- Brinson, Hood & Beebower (1986), portfolio attribution.
- Campbell (1991), cash-flow-news / expected-return-news decomposition.
- Fama & French (1993), common risk factors.
- Ibbotson & Kaplan (2000), boundary on interpretation of asset-allocation explanatory percentages.

Keep accounting identity, factor exposure, and causal explanation distinct. Realized P&L cannot rewrite the original ResearchReceipt.

- [ ] **Step 3: Complete six-candidate source coverage and update state**

After all source identities and evidence relations satisfy the minimum source gate:

```json
"status": "source_verification_complete",
"next_gate": "QXM2_MECHANISM_COMPILATION"
```

- [ ] **Step 4: Verify and commit**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
python scripts/validate_qxm2_evidence_hardening.py
git add docs/architecture/qxm2 scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "research(qxm2): complete six-candidate source verification"
```

---

### Task 5: Build the Claim–Mechanism Crosswalk

**Files:**
- Create: `QXM2-CLAIM-MECHANISM-CROSSWALK-v0.1.json`
- Modify: validator and tests.

**Interfaces:** Each claim references existing relation IDs; later Shadow Hypothesis and Benchmark Seed IDs reference these claims.

- [ ] **Step 1: Freeze claim ID families**

- `CLAIM-P003-*`: decomposition, incremental information, definition stability, arithmetic-vs-causal boundary.
- `CLAIM-P004-*`: accrual matching, persistence, reliability, growth competing explanation, diagnostic-not-fraud boundary.
- `CLAIM-R01QXM1-*`: borrower net worth, collateral feedback, sectoral transmission, aggregate-association boundary.
- `CLAIM-V01QXM1-*`: cash-flow/discount-rate decomposition, asset-routed opportunity cost, identification ambiguity, OOS boundary.
- `CLAIM-S004-*`: price impact, liquidity-risk commonality, funding-liquidity spiral, ADV insufficiency.
- `CLAIM-CROSS001-*`: return identity, asset-form routing, factor/news attribution, thesis fidelity.

Each candidate must have 3-6 atomic claims.

- [ ] **Step 2: Write referential-integrity tests RED**

Fail if a claim references an unknown relation, lacks a falsifier, lacks observable mapping, or lacks both supporting and boundary/competing evidence.

- [ ] **Step 3: Populate crosswalk GREEN**

Every claim contains:

```text
claim_id
candidate_id
statement
mechanism_ids
support_relation_ids
boundary_relation_ids
observable_set
falsifier
shadow_hypothesis_ids
benchmark_seed_ids
```

- [ ] **Step 4: Commit**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
git add docs/architecture/qxm2/QXM2-CLAIM-MECHANISM-CROSSWALK-v0.1.json scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "feat(qxm2): compile claim mechanism crosswalk"
```

---

### Task 6: Compile Shadow TheoryObjects and proposed Shadow HypothesisObjects

**Files:**
- Create: `QXM2-SHADOW-THEORY-OBJECTS-v0.1.json`
- Create: `QXM2-SHADOW-HYPOTHESIS-OBJECTS-v0.1.json`
- Modify: validator and tests.

- [ ] **Step 1: Write schema-compatibility tests RED**

Use `jsonschema.Draft202012Validator` against the existing formal TheoryObject and HypothesisObject schemas. Add a QXM2-specific negative test proving `preregistered` is rejected even though the formal Hypothesis schema permits it.

- [ ] **Step 2: Build Shadow Theory envelopes**

Use this exact envelope contract:

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

IAS 7 remains a normative source/evidence object and is not serialized as a TheoryObject.

- [ ] **Step 3: Build at least two Shadow Hypotheses per candidate using these IDs**

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

Every embedded hypothesis includes statement, real null hypothesis, target variable, horizon, eligible universe, conditioning state, expected direction, falsification rule, `point_in_time_requirement=true`, and `status="proposed"`.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest tests.test_qxm2_evidence_hardening -v
python scripts/validate_qxm2_evidence_hardening.py
git add docs/architecture/qxm2/QXM2-SHADOW-* scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "feat(qxm2): compile shadow theory and hypothesis objects"
```

---

### Task 7: Compile the six Benchmark Seeds and close mechanism compilation

**Files:**
- Create: `QXM2-BENCHMARK-SEEDS-v0.1.json`
- Modify: validator, tests, state.

- [ ] **Step 1: Write RED authority tests**

Fail if a seed lacks PIT/OOS/regime holdout or a simpler baseline; fail if `formal_benchmark_status` differs from `not_created`; fail if execution or PASS authority is true.

- [ ] **Step 2: Create six seed IDs**

- `QXM2-BSEED-P003-DRIVER-OOS`
- `QXM2-BSEED-P004-CASH-CONVERSION`
- `QXM2-BSEED-R01-CREDIT-TRANSMISSION`
- `QXM2-BSEED-V01-EXPECTATION-DECOMPOSITION`
- `QXM2-BSEED-S004-STRESS-EXIT`
- `QXM2-BSEED-CROSS001-RETURN-ATTRIBUTION`

Every seed contains target, horizon, candidate model, simpler baselines, PIT policy, OOS policy, regime holdout, primary metrics, failure metrics, leakage risks, multiple-testing risk, plus:

```json
{
  "formal_benchmark_status": "not_created",
  "benchmark_execution_authorized": false,
  "benchmark_pass_claim_authorized": false
}
```

- [ ] **Step 3: Advance state only after the full mechanism chain validates**

```json
"status": "mechanism_compilation_complete",
"next_gate": "QXM2_MACHINE_QUALIFICATION"
```

- [ ] **Step 4: Verify and commit**

```bash
python scripts/validate_qxm2_evidence_hardening.py
python -m unittest tests.test_qxm2_evidence_hardening -v
python -m unittest discover -s tests -p 'test_*.py' -v
git add docs/architecture/qxm2 scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "feat(qxm2): add falsifiable benchmark seeds"
```

---

### Task 8: Harden full validator, branch-scope guard, and narrative

**Files:** Modify validator, tests, and `QXM2-PRIMARY-THEORY-EVIDENCE-HARDENING-v0.1.md`.

- [ ] **Step 1: Implement `validate_qxm2(root)`**

It must verify:

1. QXM1 upstream is `accepted_merged` with merge commit `81bf6d83da7463e31c58e2d35bcabc291b580546`.
2. Exactly six candidate IDs match QXM1 identities.
3. Per candidate: at least 2 theory/seminal anchors, 1 independent empirical relation, 1 boundary/contradict/competing relation, 3-6 atomic claims, 2 proposed Shadow Hypotheses, and 1 Benchmark Seed.
4. All EvidenceRelation fields and closed enums are complete.
5. All embedded Theory/Hypothesis payloads validate against existing schemas.
6. `THEORY-QIN*` cannot appear.
7. No paper-count score or scalar evidence score decides admission.
8. No `primary_source_verified -> theory_admitted` or `supports -> hypothesis_supported` automatic mapping exists.
9. State uses only the approved QXM2 state machine.

- [ ] **Step 2: Add PR-time prohibited-path guard**

Use:

```bash
BASE_SHA=$(git merge-base origin/main HEAD)
git diff --name-only "$BASE_SHA"...HEAD
```

Fail while QXM2 is not `accepted_merged` if any changed path begins with:

```python
PROHIBITED_PREFIXES = (
    "registry/theories/",
    "registry/hypotheses/",
    "registry/benchmarks/",
    "registry/capabilities/",
    "canon/",
)
```

Once QXM2 itself is `accepted_merged`, later authorized stages may change Registry; at that point QXM2 validates its immutable merge receipt instead of globally freezing Registry forever.

- [ ] **Step 3: Add negative authority regression tests**

Reject target prices, recommended weights, position sizes, buy/sell instructions, `benchmark_passed=true`, `registry_admission=true`, `capability_promotion=true`, `live_execution=true`, and Shadow Hypothesis states beyond `proposed`.

- [ ] **Step 4: Finalize the research note**

For each candidate, summarize theory ancestry, empirical support, contradictory/competing evidence, replication status, external-validity limits, operational hypothesis, benchmark seed, and recommended Human Review question. The note must not claim scientific truth from CI success.

- [ ] **Step 5: Verify and commit**

```bash
python scripts/validate_qxm2_evidence_hardening.py
python -m unittest tests.test_qxm2_evidence_hardening -v
python -m unittest discover -s tests -p 'test_*.py' -v
git add docs/architecture/qxm2 scripts/validate_qxm2_evidence_hardening.py tests/test_qxm2_evidence_hardening.py
git commit -m "test(qxm2): harden evidence and authority gates"
```

---

### Task 9: Wire CI, machine-qualify, and prepare Human Epistemic Review

**Files:**
- Modify: `.github/workflows/ci.yml`
- Create: `QXM2-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `QXM2-STATE.json`

- [ ] **Step 1: Add QXM2 validator to `repository-gates`**

```yaml
      - run: python scripts/validate_qxm1_candidate_pack.py
      - run: python scripts/validate_qxm2_evidence_hardening.py
      - run: python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 2: Run the complete local gate**

```bash
python scripts/validate_repository.py
python scripts/validate_qxm1_candidate_pack.py
python scripts/validate_qxm2_evidence_hardening.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

All commands must exit 0 before PR creation.

- [ ] **Step 3: Commit and open the implementation PR**

```bash
git add .github/workflows/ci.yml
git commit -m "ci(qxm2): add evidence hardening gate"
```

PR title: `QXM2: harden Financial Mechanics primary theory and empirical evidence`.

PR body must say `Evidence-First Shadow Admission`, list all six candidates, state `Registry admissions = 0`, and preserve every non-authority boundary.

- [ ] **Step 4: Obtain the first exact-head successful `repository-gates` run**

Use the GitHub workflow response to record its exact `head_sha`, numeric `run_number`, and numeric `run_id`. Do not write invented or estimated values.

- [ ] **Step 5: Advance state to Human Review readiness**

Set `status = shadow_admission_ready_for_human_review`, serialize the exact successful run facts under `machine_qualification`, and set `next_gate = QXM2_HUMAN_REVIEW`.

- [ ] **Step 6: Create the Human Review Card**

Review dimensions must include: theory fit, mechanism fidelity, identification strength, contradictory/competing evidence, replication/external validity, operationalization/PIT testability, and per-candidate admission recommendation. Permitted recommendations: `advance`, `advance_with_boundary`, `interpretation_only`, `keep_shadow`, `reject_or_revise`.

- [ ] **Step 7: Push the review head and require a new exact-head CI success**

Record that final exact-head run in the PR body as an external Git runtime fact. Do not recursively mutate the state file merely to record the same head's run.

- [ ] **Step 8: Stop at Human Gate**

Request only `ACCEPT_QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING`. Do not create an acceptance receipt or merge.

---

### Task 10: Conditional Human Acceptance and post-acceptance qualification

**Precondition:** User explicitly issues `ACCEPT_QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING`.

**Files:**
- Create: `QXM2-HUMAN-ACCEPTANCE-RECEIPT-v0.1.json`
- Modify after post-acceptance CI: `QXM2-STATE.json`
- Modify validator/tests only as needed to validate accepted states.

- [ ] **Step 1: Create the Human Acceptance Receipt without changing the governed status yet**

The receipt records the reviewed exact-head SHA, exact Human Review CI run, per-candidate admission recommendations, and these preserved boundaries:

```json
{
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

The state remains `shadow_admission_ready_for_human_review` until the acceptance-receipt head itself passes CI; this avoids inventing a transient state not present in the approved design.

- [ ] **Step 2: Run exact-head post-acceptance CI**

Require `contracts=success` and `governance=success`, with the QXM2 validator and full tests successful.

- [ ] **Step 3: Advance directly to `human_accepted_ready_for_merge`**

Only after Step 2 succeeds, update `QXM2-STATE.json` with the Human Gate decision, acceptance receipt path, exact post-acceptance qualification facts, `merge_authority = not_implied_by_acceptance`, and `next_gate = QXM2_MERGE`.

- [ ] **Step 4: Run a new exact-head CI on the state-update head**

The merge gate is ready only if this final head also passes.

- [ ] **Step 5: Stop at merge authority**

Request `AUTHORIZE_QXM2_MERGE`. Do not merge without it.

---

### Task 11: Conditional authorized merge and post-merge closure

**Precondition:** User explicitly issues `AUTHORIZE_QXM2_MERGE`.

**Files:**
- Create on a post-merge closure branch: `QXM2-MERGE-RECEIPT-v0.1.json`
- Modify: `QXM2-STATE.json`
- Modify validator to recognize `accepted_merged` and verify the receipt.

- [ ] **Step 1: Re-check the exact pre-merge head and required checks**

Use verification-before-completion discipline. Merge only if the current exact head has successful required checks.

- [ ] **Step 2: Squash-merge the QXM2 implementation PR**

Capture the actual merge commit and timestamp from GitHub.

- [ ] **Step 3: Create a closure branch from the new `main`**

The merge receipt records Human Acceptance, merge authorization, pre-merge head, pre-merge CI run, merge method, merge commit, accepted Shadow Pack identity, preserved boundaries, and next gate `QXM3_THEORY_HYPOTHESIS_REGISTRY_ADMISSION_BENCHMARK_PREREGISTRATION`.

- [ ] **Step 4: Advance state to `accepted_merged`**

Final authority fields remain:

```json
{
  "registry_admission_authority": "none",
  "hypothesis_preregistration_authority": "none",
  "benchmark_execution_authority": "none",
  "capability_promotion_authority": "none"
}
```

- [ ] **Step 5: Run closure exact-head CI and merge the closure PR only if green**

The closure PR is bookkeeping only and does not start QXM3.

---

## Final Verification Checklist

Before claiming QXM2 complete, run and read fresh outputs:

```bash
python scripts/validate_qxm1_candidate_pack.py
python scripts/validate_qxm2_evidence_hardening.py
python -m unittest tests.test_qxm2_evidence_hardening -v
python -m unittest discover -s tests -p 'test_*.py' -v
BASE_SHA=$(git merge-base origin/main HEAD)
git diff --name-only "$BASE_SHA"...HEAD
git status --short
git rev-parse HEAD
```

For the implementation PR, confirm no changed path begins with `registry/theories/`, `registry/hypotheses/`, `registry/benchmarks/`, `registry/capabilities/`, or `canon/`. Confirm exact-head `repository-gates` is successful before presenting Human Review, and again after Human Acceptance before requesting merge authority.

## Expected End State

A completed and merged QXM2 does **not** assert that all six capabilities are scientifically proven. It establishes a machine-readable, reviewable Evidence Graph with explicit support, contradiction, boundaries, replication status, proposed hypotheses, and non-executable Benchmark Seeds. QXM3 may then selectively admit only Human-approved Theory/Hypothesis objects and compile approved Benchmark Seeds into formal preregistration candidates under a separate authority gate.