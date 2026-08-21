# QXM2｜Primary Theory & Empirical Evidence Hardening
## Evidence-First Shadow Admission Design v0.1

Status: `design_approved_pending_spec_review`

Base: `main@43911282d5ff80a2795d1b02afcf7ef40bc513a3`

Upstream: `QXM1_FINANCIAL_MECHANICS_CAPABILITY_CANDIDATE_PACK = accepted_merged`

Accepted design decisions:

- `ACCEPT_QXM2_EVIDENCE_AUTHORITY_ARCHITECTURE`
- `ACCEPT_QXM2_SIX_CAPABILITY_EVIDENCE_COMPILATION_DESIGN`
- `ACCEPT_QXM2_SHADOW_ADMISSION_OBJECT_AND_GATE_DESIGN`
- `ACCEPT_QXM2_IMPLEMENTATION_BOUNDARY_AND_EXIT_GATE`

---

## 1. Purpose

QXM1 compiled six Financial Mechanics candidates into the frozen 11-block `ResearchCapability` contract. QXM2 does not implement or promote those capabilities. Its purpose is to construct the minimum sufficient, machine-readable evidence graph required for later scientific review and admission decisions.

The governing transformation is:

```text
Practitioner Seed
  -> Primary / Seminal Theory
  -> Mechanism Claim
  -> Independent Empirical Evidence
  -> Boundary / Competing Evidence
  -> Atomic Claim
  -> Falsifiable Shadow Hypothesis
  -> Benchmark Seed
  -> Human Epistemic Review
```

QXM2 follows **Evidence-First Shadow Admission**. Shadow objects may be schema-compatible with formal Registry objects, but they have no Registry authority.

Core laws:

1. `Claim Authority <= Evidence Authority`.
2. Shadow != Registry.
3. Primary Source Verified != Theory Admitted.
4. Theory Supported != Hypothesis Supported.
5. Hypothesis Supported != Capability Qualified.
6. Benchmark Specified != Benchmark Passed.
7. Mechanism support != forecasting support.

---

## 2. Scope

QXM2 hardens exactly the six accepted QXM1 objects and may not rename, replace, merge, split or add a seventh object.

### 2.1 New capability candidates

- `CAP-P-003-FUNDAMENTAL-DRIVER-DECOMPOSITION`
- `CAP-P-004-THREE-STATEMENT-INTEGRITY-CASH-CONVERSION`
- `CAP-S-004-STRESS-EXIT-LIQUIDITY`
- `CAP-CROSS-001-RETURN-SOURCE-ATTRIBUTION`

### 2.2 Existing capability profile candidates

- `CAP-R-01::QXM1-PROFILE-R-CREDIT-BALANCE-SHEET-TRANSMISSION`
- `CAP-V-01::QXM1-PROFILE-V-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE`

QXM2 does not mutate the mother semantics of `CAP-R-01` or `CAP-V-01`.

---

## 3. Evidence Authority Architecture

QXM2 organizes evidence into four layers.

### A. Theory Lineage

Primary papers, seminal papers, books where appropriate, and normative accounting authority where applicable. These sources establish theoretical mechanisms or reporting rules; they do not by themselves prove operational usefulness.

### B. Empirical Anchor

Independent evidence that tests a mechanism, association, decomposition or predictive relation. Empirical support must not be silently upgraded to causality when identification does not warrant it.

### C. Replication / Robustness

Direct replication, extensions, cross-market evidence, contradictory evidence, known failure regimes, external-validity limits and unresolved replication gaps.

### D. Operational Proof

Future Yuanli PIT/OOS replay and benchmark evidence. QXM2 only prepares Benchmark Seeds; it does not execute formal benchmarks or claim PASS.

The scientific chain is therefore:

```text
Theory lineage
  -> mechanism
  -> empirical evidence
  -> competing explanations
  -> falsifiable hypothesis
  -> operational benchmark seed
```

---

## 4. Six-Capability Evidence Compilation

### 4.1 Fundamental Driver Decomposition

Primary lineage candidates include Lev & Thiagarajan, Abarbanell & Bushee, and Nissim & Penman.

Roles:

- Fundamental-signal literature: whether disaggregated operating / financial signals contain information beyond headline earnings.
- Future-outcome literature: whether such signals are associated with later earnings or operating outcomes.
- Hierarchical ratio / decomposition literature: architecture for decomposing higher-level outcomes into lower-level economic drivers.

QXM2 must preserve the distinction between arithmetic decomposition and causal identification.

Primary operational hypothesis family:

> Under stable definitions and explicit treatment of M&A / segment breaks, PIT primitive-driver decomposition provides stable OOS incremental information about future revenue, margin, FCF or declared operating KPIs relative to simpler revenue-growth / margin / consensus baselines.

A valid falsifier is failure to add stable OOS information after complexity penalties and regime holdouts.

### 4.2 Three-Statement Integrity & Cash Conversion

Primary lineage candidates include Dechow, Sloan, Dechow-Dichev, Richardson et al., plus IAS 7 as normative accounting authority rather than a predictive TheoryObject.

Required boundary:

> Cash flow is not automatically economically superior to accrual earnings. Accruals can improve matching and timing, while accrual components also differ in persistence and reliability.

QXM2 must explicitly preserve competing explanations such as normal growth investment, seasonality, accounting-policy changes and working-capital cycles.

No object may produce or imply a fraud score. Statement divergence remains diagnostic, not proof of manipulation, fraud or insolvency.

### 4.3 Credit & Balance-Sheet Transmission Profile

Primary lineage candidates include Bernanke-Gertler and Kiyotaki-Moore, with long-horizon empirical anchors such as Schularick-Taylor and Jorda-Schularick-Taylor.

The machine mechanism must be sectoral and balance-sheet based:

```text
Borrower sector
  -> leverage / net worth
  -> collateral
  -> lending standard / funding cost
  -> credit creation
  -> spending / investment
  -> cash flow
  -> asset-price / financial-condition feedback
```

Aggregate credit correlation alone is insufficient for causal-transmission claims. When sector, collateral or balance-sheet mechanism evidence is absent, the output must degrade to association-only semantics.

### 4.4 Opportunity-Cost / Discount-Rate Bridge Profile

Primary lineage candidates include Sharpe, Campbell-Shiller and Cochrane. OOS skepticism such as Welch-Goyal is part of the evidence graph, not an inconvenient footnote.

The profile is an expectations-decomposition capability, not a market-timing oracle.

It must keep separate:

- cash-flow expectations,
- discount-rate / required-return expectations,
- term / liquidity / scarcity premia where applicable,
- unresolved identification ambiguity.

DCF may be used for compatible asset forms; it may not be forced onto all assets. Price-implied expectations remain distinct from target prices.

### 4.5 Stress Exit Liquidity

Primary lineage candidates include Kyle, Amihud, Pastor-Stambaugh and Brunnermeier-Pedersen.

Liquidity must be decomposed at least into:

- transaction liquidity,
- market liquidity,
- liquidity risk,
- funding liquidity.

High ADV or a narrow normal-state spread is not sufficient evidence of good stress exit.

Primary operational comparison:

> Does a multi-dimensional stress-liquidity state improve explanation of realized liquidation horizon, slippage, gap loss or funding breach during stress windows relative to simple ADV / spread baselines?

### 4.6 Return Source Attribution

Primary lineage candidates include Brinson-Hood-Beebower, Campbell return-news decomposition and Fama-French style common-risk-factor decomposition.

The capability must route by asset form rather than use one universal attribution algorithm.

Examples:

```text
Portfolio -> policy / timing / selection
Equity -> cash-flow news / discount-rate news / factor exposure / residual
Bond -> carry / curve / spread / default / liquidity
FX -> spot / carry / rate differential
Option -> underlying / volatility / time / convexity / path
```

Two distinct tests are required:

1. Accounting Identity Test: attribution buckets plus residual reconstruct realized return.
2. Thesis Fidelity Test: attribution is compared with the immutable original `ResearchReceipt` without hindsight rewriting.

Positive P&L does not prove the thesis, and negative P&L does not automatically falsify every original claim.

---

## 5. QXM2 Evidence Staging Plane

QXM2 introduces no tenth Registry. All staging objects live under `docs/architecture/qxm2/`.

Planned artifacts:

```text
docs/architecture/qxm2/
├── QXM2-PRIMARY-THEORY-EVIDENCE-HARDENING-v0.1.md
├── QXM2-PRIMARY-SOURCE-MATRIX-v0.1.json
├── QXM2-EMPIRICAL-EVIDENCE-MATRIX-v0.1.json
├── QXM2-CLAIM-MECHANISM-CROSSWALK-v0.1.json
├── QXM2-SHADOW-THEORY-OBJECTS-v0.1.json
├── QXM2-SHADOW-HYPOTHESIS-OBJECTS-v0.1.json
├── QXM2-BENCHMARK-SEEDS-v0.1.json
├── QXM2-HUMAN-REVIEW-CARD-v0.1.md
└── QXM2-STATE.json
```

Implementation support files:

```text
scripts/validate_qxm2_evidence_hardening.py
tests/test_qxm2_evidence_hardening.py
.github/workflows/ci.yml
```

The implementation PR must not modify:

```text
registry/theories/
registry/hypotheses/
registry/benchmarks/
registry/capabilities/
canon/
```

---

## 6. Shadow TheoryObject Contract

A Shadow TheoryObject reuses the formal `TheoryObject` payload without changing the R1 schema.

It is wrapped in a staging envelope, conceptually:

```json
{
  "shadow_object_id": "...",
  "admission_state": "shadow_only",
  "candidate_targets": ["..."],
  "theory_object": {
    "theory_id": "THEORY-...",
    "title": "...",
    "authors": ["..."],
    "year": 2000,
    "source_locator": "...",
    "source_class": "original_paper",
    "mechanisms": ["..."],
    "pnxs_mapping": ["P"],
    "claim_boundary": "...",
    "evidence_status": "primary_source_verified"
  },
  "verification": {
    "primary_source_opened": true,
    "bibliographic_identity_verified": true,
    "mechanism_extracted_from_primary_source": true,
    "claim_boundary_verified": true
  },
  "admission_authority": "none"
}
```

`primary_source_verified` describes source verification. It must never imply formal theory admission.

Shadow admission readiness is a separate staging concept:

- `source_verified`
- `mechanism_ready`
- `admission_candidate`

These are not added to the formal `TheoryObject` schema.

---

## 7. EvidenceRelation Contract

The primary unit of the empirical matrix is a relation between a source and an atomic claim, not a paper count.

Required conceptual fields:

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

`role` must be one of:

- `supports`
- `contradicts`
- `boundary`
- `competing_mechanism`

Replication status must be explicit, including honest gap states such as `not_found`.

Evidence quality is not calculated by paper counting or scalar score.

---

## 8. Claim–Mechanism Crosswalk

Each capability is decomposed into approximately 3-6 atomic claims. Each claim must link:

```text
Capability
  -> Atomic Claim
  -> Mechanism
  -> Evidence Relations
  -> Observable
  -> Shadow Hypothesis
  -> Benchmark Seed
```

The crosswalk is the central QXM2 research asset because it prevents an AI runtime from free-form inference from a capability name or bibliography.

Every material claim must expose evidence for support, boundary, contradiction or competing explanation where available.

---

## 9. Shadow HypothesisObject Contract

Shadow hypotheses must be compatible with the formal `HypothesisObject` schema and must remain:

```text
status = proposed
```

QXM2 does not authorize `preregistered`, `tested`, `supported` or any later state.

Every shadow hypothesis requires:

- statement,
- null hypothesis,
- target variable,
- horizon,
- eligible universe,
- conditioning state,
- expected direction,
- falsification rule,
- `point_in_time_requirement = true`.

A literature statement becomes useful to Yuanli only when it is transformed into a PIT-testable, falsifiable research hypothesis.

---

## 10. Benchmark Seed Contract

QXM2 creates Benchmark Seeds, not formal `BenchmarkObject` entries.

Minimum fields:

```text
benchmark_seed_id
candidate_id
hypothesis_id
target
horizon
candidate_model
simpler_baselines
pit_requirement
oos_requirement
regime_holdout
primary_metrics
failure_metrics
known_leakage_risks
multiple_testing_risk
formal_benchmark_status = not_created
benchmark_execution_authorized = false
benchmark_pass_claim_authorized = false
```

A Benchmark Seed must be compiled into a formal `BenchmarkObject` in a later authorized stage before execution.

---

## 11. Minimum Sufficient Evidence Graph

QXM2 is deliberately not an academic encyclopedia.

Per candidate, minimum coverage is:

- primary / seminal theory anchors: at least 2;
- independent empirical relation: at least 1;
- boundary / contradiction / competing relation: at least 1;
- atomic claims: approximately 3-6;
- shadow hypotheses: at least 2;
- benchmark seeds: at least 1;
- explicit falsifier: one per hypothesis;
- replication status: mandatory, including explicit gap states.

These quotas are completeness tests only. They are not evidence-quality scores.

---

## 12. State Machine

QXM2 uses the following governed states:

```text
shadow_compilation_started
  -> source_verification_complete
  -> mechanism_compilation_complete
  -> shadow_admission_ready_for_human_review
  -> human_accepted_ready_for_merge
  -> accepted_merged
```

Meanings:

### `source_verification_complete`

Bibliographic identity and primary-source provenance are verified. No epistemic acceptance is implied.

### `mechanism_compilation_complete`

Source-to-claim-to-mechanism relations, boundaries and competing evidence are compiled. Predictive validity is not implied.

### `shadow_admission_ready_for_human_review`

The chain from mechanism to observable to falsifiable hypothesis to benchmark seed is structurally complete.

### `human_accepted_ready_for_merge`

Human Epistemic Review is accepted and post-acceptance exact-head CI has passed. Merge still requires separate authority.

### `accepted_merged`

The QXM2 shadow pack is merged and a merge receipt has been recorded. Formal Registry admission is still not implied.

---

## 13. Machine Validation

`validate_qxm2_evidence_hardening.py` validates structure and governance, not scientific truth.

Required validation groups:

### A. Coverage

- exactly six QXM1 candidates;
- identities must match accepted QXM1 definitions;
- no seventh candidate;
- no mutation of CAP-R-01 or CAP-V-01 mother semantics.

### B. Evidence Completeness

Per candidate enforce minimum theory / empirical / boundary / hypothesis / benchmark-seed coverage.

### C. Schema Compatibility

- each embedded shadow TheoryObject independently validates against the existing TheoryObject schema;
- each embedded shadow HypothesisObject independently validates against the existing HypothesisObject schema;
- all shadow hypotheses must have `status = proposed`.

### D. Evidence Relation Integrity

Each relation declares role, identification strength, domain, time scope, replication status, external validity and operationalization fields.

### E. Benchmark Seed Integrity

Every seed includes simpler baselines, PIT, OOS, regime holdout, leakage risk, multiple-testing risk and explicit non-authorization of execution / PASS claims.

### F. Governance Negative Tests

CI must fail on any silent assertion of:

- Registry admission;
- capability promotion;
- benchmark PASS;
- shadow qualification;
- target price;
- buy / sell;
- recommended weight;
- position size;
- live execution.

It must also fail if code maps `primary_source_verified` directly to `theory_admitted`, or maps `paper supports mechanism` directly to `hypothesis supported`.

Machine validation must not claim that a paper has been interpreted correctly. That remains Human Review authority.

---

## 14. Human Epistemic Review

Human Review evaluates questions machine validation cannot decide:

1. Is the cited work genuinely an ancestor of the candidate mechanism rather than merely adjacent literature?
2. Is mechanism extraction faithful to the original work?
3. Are correlation, predictability and causality correctly separated?
4. Is the claim boundary strong enough?
5. Has material contradictory / competing evidence been represented fairly?
6. Are external-validity limits explicit?
7. Can the proposed hypothesis actually be tested with PIT data?
8. Which shadow objects should advance to later formal admission review?

QXM2 may PASS as a process even when individual candidate admission recommendations differ.

Recommended per-candidate review outcomes may include:

- `advance`
- `advance_with_boundary`
- `interpretation_only`
- `keep_shadow`
- `revise`
- `reject`

No scalar scientific score is introduced.

---

## 15. Human Gate and Merge Governance

Reserved Human Acceptance token:

`ACCEPT_QXM2_PRIMARY_THEORY_EMPIRICAL_EVIDENCE_HARDENING`

Acceptance covers the Evidence Graph, Shadow TheoryObjects, Shadow Hypotheses, Benchmark Seeds and admission recommendations only.

Acceptance does not authorize:

- formal Registry admission;
- hypothesis preregistration;
- formal BenchmarkObject creation;
- benchmark execution or PASS;
- capability implementation or promotion;
- provider production runtime;
- portfolio or trading actions.

After Human Acceptance:

```text
Human Acceptance Receipt
  -> post-acceptance exact-head repository-gates
  -> human_accepted_ready_for_merge
  -> separate explicit merge authorization
```

Reserved merge token:

`AUTHORIZE_QXM2_MERGE`

A post-merge closure must create `QXM2-MERGE-RECEIPT-v0.1.json` and advance `QXM2-STATE.json` to `accepted_merged`.

Receipt is ledger; state is projection.

---

## 16. Exit Gate

QXM2 is eligible for Human Review only when all conditions are satisfied:

1. 6/6 candidates have a complete Evidence Graph;
2. each has at least 2 primary / seminal anchors;
3. each has at least 1 independent empirical relation;
4. each has at least 1 contradictory, boundary or competing relation;
5. every material atomic claim is connected to evidence relations;
6. each candidate has at least 2 Shadow Hypotheses, all `proposed`;
7. each candidate has at least 1 Benchmark Seed;
8. PIT, OOS, falsifier and replication fields are complete;
9. Shadow Theory / Hypothesis payloads are compatible with formal schemas;
10. formal Registry admission count remains zero;
11. exact-head `repository-gates` is green;
12. Human Epistemic Review is complete.

QXM2 PASS means the evidence-hardening process is complete and valid. It does not mean all six candidates have equal evidence strength or are ready for admission.

---

## 17. Next Stage Boundary

The recommended next stage after QXM2 is:

`QXM3 | Theory & Hypothesis Registry Admission + Benchmark Preregistration`

QXM3 will consider only QXM2 objects explicitly recommended to advance. It is the first stage allowed, under separate authority, to decide:

- which Shadow TheoryObjects enter `registry/theories`;
- which Shadow HypothesisObjects become formal `preregistered` hypotheses;
- which Benchmark Seeds are compiled into formal `BenchmarkObject` contracts.

Implementation, PIT/OOS replay and empirical qualification remain later work.

Longer sequence:

```text
QXM0 Reverse Engineering
  -> QXM1 Capability Candidate Contract
  -> QXM2 Evidence-First Shadow Admission
  -> QXM3 Registry Admission + Preregistration
  -> QXM4 Implementation + PIT/OOS Replay
  -> QXM5 Benchmark / Failure / Promotion Decision
```

---

## 18. Non-Goals

QXM2 does not authorize or perform:

- changes to formal theory, hypothesis, benchmark or capability registries;
- capability implementation;
- benchmark execution;
- shadow qualification;
- canon promotion;
- Wind / Codex production runtime;
- evidence or outcome admission into unrelated lanes;
- A9 switching;
- RSI promotion;
- target prices;
- recommended weights;
- position sizes;
- buy / sell recommendations;
- live execution.

---

## 19. Design Acceptance

This specification incorporates the four accepted architectural decisions:

- Evidence Authority Architecture;
- Six-Capability Evidence Compilation Design;
- Shadow Admission Object & Gate Design;
- Implementation Boundary & Exit Gate.

Implementation must not begin until this written specification receives explicit user review approval and a separate implementation plan is produced.