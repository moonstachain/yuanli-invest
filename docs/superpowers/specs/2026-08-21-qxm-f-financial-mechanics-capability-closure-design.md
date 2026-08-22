# QXM-F｜Financial Mechanics Capability Closure — Design v0.1

Status: architectural design candidate
Date: 2026-08-21
Repository: `moonstachain/yuanli-invest`
Program role: close the Qin Xiaoming Financial Mechanics research line by settling every QXM1/QXM2 candidate through governed admission, preregistration, reality proof, capability settlement, and compiler canonization.

## 0. Executive decision

QXM-F is not "QXM3 with a larger name" and is not authorization to promote all six QXM candidates. It is the terminal program that converts the QXM research line from a practitioner-seeded knowledge project into a closed, auditable research-capability lineage.

The program is complete only when three settlements are simultaneously true:

1. **Identity Settlement** — every QXM2 Shadow TheoryObject, Shadow HypothesisObject, and Benchmark Seed has an explicit disposition and no orphan authority object remains.
2. **Reality Settlement** — the designated priority capabilities have undergone frozen point-in-time, held-out, regime, and failure-replay tests against simpler baselines, using a test modality appropriate to the capability's semantics rather than forcing every capability into a forecasting task.
3. **Learning Settlement** — results, including failures, have been compiled into Promote / Promote-with-Boundary / Interpretation-Only / Reject-or-Redesign decisions and into a reusable External Research Compiler protocol.

Mnemonic:

> **Closure = Identity Settlement × Reality Settlement × Learning Settlement**

This is a governance conjunction, not a scalar score.

---

## 1. Upstream state and hard precondition

QXM-F begins from QXM2, but does not silently absorb QXM2 merge authority.

At design-freeze time:

- QXM1 is `accepted_merged` on `main`.
- QXM2 PR #38 is Human Accepted and exact-head qualified, with governed status `human_accepted_ready_for_merge` on its implementation branch.
- QXM2 has zero Registry admissions, zero hypothesis preregistrations, zero formal BenchmarkObjects, zero benchmark executions, zero capability promotions, and zero trading authority.

### Hard authority rule

`START_QXM_F` or a request to execute QXM-F **does not imply** `AUTHORIZE_QXM2_MERGE`.

G0 may execute only after the explicit token:

`AUTHORIZE_QXM2_MERGE`

Until that token exists, QXM-F may create only its architecture/specification/planning artifacts. It may not merge PR #38 and may not perform any downstream admission, preregistration, benchmark execution, promotion, runtime activation, portfolio action, or trading action.

---

## 2. Program architecture — one closure program, six gates

QXM-F is decomposed into six sequential gates. No later gate may infer authority from an earlier gate.

```text
QXM2 Human Accepted
        |
        v
G0 | QXM2 Merge Closure
        |
        v
G1 | Selective Registry Admission
        |
        v
G2 | Hypothesis Preregistration + Benchmark Formalization
        |
        v
G3 | Provider Mapping + PIT/Held-Out Reality Proof
        |
        v
G4 | Capability Settlement + Financial Mechanics Gold Pack
        |
        v
G5 | External Research Compiler Canonization + QXM Archive Closure
        |
        v
QXM_PROJECT_CLOSED
```

Each gate is an independent governed deliverable with its own machine qualification and Human Gate where epistemic judgment is required.

---

## 3. G0｜QXM2 Merge Closure

### Purpose

Close the already Human-Accepted QXM2 Evidence-First Shadow Admission stage without expanding its authority.

### Required precondition

Explicit user token: `AUTHORIZE_QXM2_MERGE`.

### Required sequence

1. Re-fetch PR #38 immediately before merge.
2. Verify exact head SHA has not changed.
3. Verify required checks on that exact head are successful.
4. Verify changed-path audit still contains no forbidden formal-authority paths.
5. Squash merge with expected-head protection.
6. Create a dedicated post-merge closure branch.
7. Create `QXM2-MERGE-RECEIPT-v0.1.json`.
8. Advance `QXM2-STATE.json` to `accepted_merged`.
9. Extend the QXM2 validator so the merged state and merge receipt are fail-closed.
10. Run exact-head closure CI and merge the closure PR only under the already-authorized QXM2 merge authority, following the QXM1/QXM2 closure precedent.

### Preserved boundaries

G0 does **not** authorize:

- Registry admission;
- hypothesis preregistration;
- formal BenchmarkObject creation;
- benchmark execution;
- capability implementation or promotion;
- production runtime;
- target price, recommended weight, position size, or trading.

### Exit state

`QXM2.status = accepted_merged`

Next gate: `QXM_F_G1_SELECTIVE_ADMISSION`

---

## 4. G1｜Selective Registry Admission

### Purpose

Convert the QXM2 Shadow Pack into explicit identity decisions. Human Acceptance of QXM2 is not blanket admission.

### Four legal dispositions

Every Shadow TheoryObject and Shadow HypothesisObject must receive exactly one disposition:

- `ADMIT`
- `ADMIT_WITH_BOUNDARY`
- `KEEP_SHADOW`
- `REJECT`

Every Benchmark Seed must receive exactly one disposition:

- `FORMALIZE`
- `DEFER`
- `REJECT`

No object may remain undecided at QXM-F closure.

### QXM2 recommendation discipline

QXM2 recommendations are inputs, not commands:

- Fundamental Driver Decomposition — `advance_with_boundary`
- Three-Statement Integrity & Cash Conversion — `advance_with_boundary`
- Credit & Balance-Sheet Transmission — `advance_with_boundary`
- Opportunity-Cost / Discount-Rate Bridge — `interpretation_only`
- Stress Exit Liquidity — `advance_with_boundary`
- Return Source Attribution — `advance_with_boundary`

The Discount-Rate Bridge must not be silently upgraded from `interpretation_only` to predictive/timing authority.

### Priority structure: 3 + 2 + 1

#### Tier 1 — mandatory full Reality Proof

1. `CAP-P-003-FUNDAMENTAL-DRIVER-DECOMPOSITION`
2. `CAP-P-004-THREE-STATEMENT-INTEGRITY-CASH-CONVERSION`
3. `CAP-CROSS-001-RETURN-SOURCE-ATTRIBUTION`

Rationale: these form the core Financial Mechanics learning loop:

> pre-investment business decomposition → in-period accounting/cash integrity → post-outcome thesis attribution

#### Tier 2 — formal experiment candidates, promotion not required

4. `CAP-R-01::QXM1-PROFILE-R-CREDIT-BALANCE-SHEET-TRANSMISSION`
5. `CAP-S-004-STRESS-EXIT-LIQUIDITY`

#### Tier 3 — identity-limited

6. `CAP-V-01::QXM1-PROFILE-V-OPPORTUNITY-COST-DISCOUNT-RATE-BRIDGE`

Default admissible identity: expectations/discount-rate interpretation only. Predictive authority requires later preregistered OOS evidence.

### G1 machine/human split

Machine validation may check schema compatibility, referential integrity, completeness of dispositions, absence of orphan objects, and absence of unauthorized authority escalation.

Human Review must decide theory fit, mechanism fidelity, causal-vs-associational language, external validity, and whether an object deserves formal Registry identity.

### G1 exit

A frozen Admission Ledger with complete dispositions and no orphan Shadow object.

No hypothesis becomes `preregistered` in G1.

---

## 5. G2｜Hypothesis Preregistration + Benchmark Formalization

### Purpose

Freeze the experiment before access to result-conditioned tuning.

### Core law

> **Preregister before data-conditioned model selection.**

A formal Reality Proof may start only after the corresponding hypothesis and BenchmarkObject are frozen.

### Required formal HypothesisObject fields

Each hypothesis selected for Reality Proof must freeze at least:

- hypothesis identity;
- statement;
- null hypothesis;
- target variable;
- horizon;
- eligible universe;
- conditioning state;
- expected direction where applicable;
- point-in-time requirement;
- falsification rule;
- status = `preregistered` only after explicit Human Gate.

### Required BenchmarkObject fields

Each formal benchmark must freeze at least:

- benchmark identity;
- linked hypothesis;
- candidate model/capability;
- simpler baselines;
- point-in-time policy;
- lookahead prohibition;
- train/validation/OOS split or held-out case split appropriate to the capability;
- regime holdout;
- primary metrics;
- failure metrics;
- acceptance threshold;
- complexity penalty;
- multiple-testing policy;
- missing-data policy;
- revision policy;
- data/provider versioning policy.

### Simple-baseline constitution

Every complex capability must beat a simpler alternative under the same PIT/held-out rules when incremental performance is part of its claimed authority.

Minimum baseline map:

| Capability | Required simple baseline family |
|---|---|
| Fundamental Driver Decomposition | revenue growth / margin / consensus-EPS style baseline |
| Three-Statement Integrity | net-income growth / CFO growth / leverage-only baseline |
| Credit Transmission | aggregate-credit-growth baseline |
| Discount-Rate Bridge | historical-mean / constant-discount-rate interpretation baseline |
| Stress Exit Liquidity | ADV + spread baseline |
| Return Source Attribution | naive P&L / benchmark-return decomposition baseline |

Law:

> **No stable incremental information over a simpler baseline → no predictive Capability promotion.**

For non-predictive learning/interpretation capabilities, settlement must instead demonstrate stable reconstruction, discrimination, or thesis-fidelity value over the simpler baseline defined in the BenchmarkObject.

### Anti-p-hacking / anti-hindsight rule

Once a preregistration hash is frozen, changes to target, horizon, universe, metric, threshold, split, or baseline require a new revision identity. Results from the old contract cannot be relabeled under the revised contract.

---

## 6. G3｜Provider Mapping + PIT/Held-Out Reality Proof

### Purpose

Move from literature-backed capability candidates to reality-tested research capability evidence.

### Provider law

Capability identity remains provider-independent.

Provider-specific mappings are profiles/adapters, not capability identities.

Example:

```text
FundamentalDriverState
   ├── WindProviderProfile
   ├── OtherVendorProviderProfile
   └── ManualEvidenceProfile
```

No Wind field code may become part of the canonical capability identity.

### Minimum Reality Proof stack

For each Tier-1 capability, all four categories are mandatory, but the held-out modality must match the capability's actual semantics:

1. **PIT Replay** — prove that every observable was available at the decision timestamp under the frozen data policy.
2. **Held-Out Test** — predictive capabilities use OOS forecasting/evaluation; attribution or interpretation capabilities use held-out episodes/cases and reconstruction, discrimination, or thesis-fidelity tests rather than pretending to forecast.
3. **Regime Holdout** — evaluate under materially different regimes/markets/accounting states where applicable.
4. **Failure Replay** — deliberately test cases where the model is expected to mislead or become inapplicable.

Tier-2 capabilities may be settled as `DEFER` if required data or stress samples are not sufficiently reliable; defer is a legitimate result and cannot be converted into implicit support.

### Failure-envelope requirement

Any capability considered for promotion must carry a machine-readable Known Failure Envelope describing at least:

- unsupported asset forms;
- unsupported sectors/regimes;
- data-quality failure modes;
- common false positives;
- common false negatives;
- causal-language limits;
- provider-specific limitations;
- conditions requiring abstention.

### Result integrity

Positive P&L does not prove the original thesis. Negative P&L does not automatically falsify every underlying mechanism. Return Source Attribution must preserve the immutable original ResearchReceipt and explicitly separate outcome accounting from causal explanation.

---

## 7. G4｜Capability Settlement + Financial Mechanics Gold Pack

### Purpose

Give every QXM capability candidate a terminal research disposition.

### Legal settlement outcomes

- `PROMOTE`
- `PROMOTE_WITH_BOUNDARY`
- `INTERPRETATION_ONLY`
- `REJECT_OR_REDESIGN`

These are not ranking labels. Each has distinct runtime authority.

### Promotion discipline

A capability cannot be promoted merely because:

- its primary theory is canonical;
- one paper supports its mechanism;
- it fits the QXM2 Evidence Graph;
- an in-sample backtest is significant;
- a retrospective case study looks persuasive;
- it explains realized P&L after the fact.

Promotion requires the frozen G2/G3 evidence contract to meet its predefined settlement rule.

### Healthy failure budget

QXM-F does not target 6/6 promotion. A healthy outcome may contain:

- 2–4 Promote / Promote-with-Boundary;
- 1–2 Interpretation / Keep-limited outcomes;
- 0–2 Reject-or-Redesign outcomes.

Six universal promotions should trigger a gate-quality review rather than celebration.

### Financial Mechanics Gold Pack

If the Tier-1 loop earns sufficient settlement authority, create:

`FM-GOLD-01｜Classical Financial Mechanics Gold Pack`

The Gold Pack is de-personalized. Qin Xiaoming remains in provenance, but runtime identity is capability-based, not person-based.

Expected core:

1. Fundamental Driver Decomposition
2. Three-Statement Integrity & Cash Conversion
3. Return Source Attribution

The pack must include:

- admitted theory ancestry;
- admitted/preregistered hypothesis identities;
- benchmark receipts;
- PIT/held-out replay receipts;
- known failure envelopes;
- capability revision history;
- settlement status;
- explicit runtime authority boundary.

Gold Pack existence does not imply trading authority.

---

## 8. G5｜External Research Compiler Canonization + QXM Archive Closure

### Purpose

Convert the QXM-specific workflow into a reusable platform capability.

### Canonical object

Create an External Research Compiler (ERC) protocol that can ingest practitioner systems, books, courses, paper families, investor frameworks, and institutional methodologies without granting them automatic theory/capability authority.

### Canonical compiler sequence

```text
R0  Source Authority Classification
R1  Mechanism Extraction
R2  Capability Candidate Contract
R3  Primary Theory Ancestry
R4  Evidence Graph
R5  Atomic Claim Compilation
R6  Shadow Theory / Hypothesis
R7  Human Epistemic Review
R8  Selective Registry Admission
R9  Hypothesis Preregistration
R10 Implementation / Provider Mapping
R11 PIT/Held-Out Benchmark + Failure Replay
R12 Settlement
R13 Promote / Bound / Interpret / Reject
```

QXM becomes:

`ERC-GOLD-CASE-001`

### De-personalization law

> **Person is provenance; capability is the durable runtime asset.**

The compiler must preserve practitioner provenance while preventing person-authority from becoming capability-authority.

### QXM archival state

After G5:

- QXM0/QXM1/QXM2/QXM-F remain as auditable provenance and governance history;
- the active runtime objects are the resulting formal ResearchCapabilities and Financial Mechanics pack;
- QXM is no longer an open research campaign;
- future changes occur through Capability Revision / Benchmark / Failure / FutureSettlement workflows, not by reopening the personality-centered project.

---

## 9. Project Closure Contract

QXM-F may declare `QXM_PROJECT_CLOSED` only when every condition below is satisfied.

| Closure condition | Required state |
|---|---|
| QXM2 | `accepted_merged` |
| Six QXM candidates | 6/6 have explicit terminal disposition |
| Shadow TheoryObjects | every object = Admit / Admit-with-Boundary / Keep-Shadow / Reject |
| Shadow HypothesisObjects | every object = Preregister / Keep / Reject disposition |
| Benchmark Seeds | every seed = Formalize / Defer / Reject disposition |
| Tier-1 Reality Proof | PIT + held-out + regime holdout + failure replay completed |
| Simple baseline | present for every executed benchmark |
| Settlement receipt | exists for every Tier-1 capability |
| Known Failure Envelope | exists for every promoted/bounded capability |
| Registry integrity | no orphan QXM object |
| Runtime | only settled/promoted identities may be runtime-callable |
| Trading authority | remains independent and false unless separately governed elsewhere |
| ERC | External Research Compiler Canon frozen |
| QXM archive | Gold Case + final closure receipt written |

### Terminal law

> **All objects having a disposition is more important than all objects succeeding.**

---

## 10. Governance and authority matrix

QXM-F keeps the following authorities independent:

1. Human epistemic acceptance;
2. merge authorization;
3. Registry admission;
4. hypothesis preregistration;
5. formal benchmark creation;
6. benchmark execution;
7. capability promotion;
8. production runtime activation;
9. portfolio/trading authority.

No one authority implies another.

Particularly:

- `AUTHORIZE_QXM2_MERGE` only closes QXM2;
- G1 Human Admission Review may authorize specific Registry admissions but not preregistration or execution;
- G2 may preregister hypotheses and create BenchmarkObjects but not claim benchmark PASS;
- G3 may execute approved benchmarks but not self-promote capabilities;
- G4 Human Settlement decides promotion status;
- G5 canonizes the compiler but cannot create trading authority.

---

## 11. Receipt and state architecture

The program follows the existing repository rule:

> **Receipt = Ledger; State = Projection.**

Each gate must have an immutable receipt for accepted/authorized decisions and a state projection for current workflow status.

Recommended QXM-F paths:

```text
docs/architecture/qxm-f/
├── QXM-F-PROGRAM-STATE.json
├── G1-ADMISSION-LEDGER-v0.1.json
├── G1-HUMAN-REVIEW-CARD-v0.1.md
├── G2-PREREGISTRATION-LEDGER-v0.1.json
├── G2-BENCHMARK-FORMALIZATION-LEDGER-v0.1.json
├── G3-REALITY-PROOF-LEDGER-v0.1.json
├── G4-CAPABILITY-SETTLEMENT-LEDGER-v0.1.json
├── G4-HUMAN-SETTLEMENT-CARD-v0.1.md
├── G5-ERC-CANONIZATION-RECEIPT-v0.1.json
└── QXM-F-CLOSURE-RECEIPT-v0.1.json
```

Formal Registry objects continue to live only in existing Registry namespaces. QXM-F ledgers reference them; they do not create a parallel Registry.

---

## 12. CI and machine-validation architecture

QXM-F should use gate-specific validators rather than one monolithic validator.

Recommended validators:

- `validate_qxm_f_g1_admission.py`
- `validate_qxm_f_g2_preregistration.py`
- `validate_qxm_f_g3_reality_proof.py`
- `validate_qxm_f_g4_settlement.py`
- `validate_qxm_f_g5_closure.py`

Machine gates verify structure, referential integrity, frozen identities, no lookahead flags, benchmark contract completeness, authority boundaries, orphan-free settlement, and receipt/state consistency.

Machine gates do not judge scientific truth, theoretical merit, economic causality, or whether a result is economically meaningful beyond explicitly frozen quantitative rules.

Human gates retain epistemic and promotion authority.

---

## 13. Program execution strategy

QXM-F is too large to implement safely as one PR. It is one strategic program but multiple governed implementation campaigns.

### Campaign A — G0 closure

Uses the existing QXM2 PR/closure pattern. Blocked until `AUTHORIZE_QXM2_MERGE`.

### Campaign B — G1 selective admission

New branch/spec/plan after QXM2 is on `main`. Scope: admission ledger, exact Registry diffs, admission validator, Human Gate. No preregistration.

### Campaign C — G2 preregistration

Scope: selected HypothesisObject transitions and formal BenchmarkObjects. No benchmark execution.

### Campaign D — G3 reality proof

Scope: provider-independent implementation, provider adapters, PIT/held-out execution, failure replay, benchmark receipts. No self-promotion.

### Campaign E — G4 settlement

Scope: Human settlement, ResearchCapability promotion/revision/rejection, FM-GOLD-01 candidate, runtime authority boundaries.

### Campaign F — G5 compiler canonization

Scope: External Research Compiler Canon, ERC-GOLD-CASE-001, archive/closure receipt, final orphan audit.

Each campaign gets its own implementation plan and exact-head CI. Architectural changes inside G1–G5 that alter existing interfaces require their own child design review rather than being hidden inside the parent program.

---

## 14. Success criteria

QXM-F succeeds when:

- it closes the Qin Xiaoming line without turning practitioner authority into canonical theory authority;
- at least the Tier-1 Financial Mechanics loop receives complete reality settlement, whether the result is Promote or Reject;
- complex mechanics are tested against simpler baselines under PIT/held-out rules;
- failures become explicit known-failure knowledge rather than being discarded;
- every QXM object has a final disposition;
- durable runtime assets are de-personalized ResearchCapabilities;
- the method for learning from external knowledge becomes a reusable ERC Canon;
- no QXM-F action creates implicit portfolio or trading authority.

Strategic terminal statement:

> **QXM-F is complete not when Qin Xiaoming is fully imported, but when Yuanli Investment Research has demonstrated that it can scientifically learn from, test, bound, reject, and operationalize external knowledge — and preserve that learning as governed ResearchCapability.**

---

## 15. Explicit non-goals

QXM-F does not:

- maximize the number of admitted theories;
- maximize the number of promoted capabilities;
- use paper counts as evidence scores;
- treat statistical significance as economic usefulness;
- infer causality from attribution identity or correlation;
- make Wind the canonical capability ontology;
- reopen `X := (Xs, Xa, Xp)` into a scalar score;
- create target prices, buy/sell instructions, recommended weights, or live trading;
- make QXM a permanent person-centered runtime namespace.

---

## 16. Immediate next gate after design approval

After this written design is reviewed and accepted, create a program implementation plan using Superpowers `writing-plans`.

The implementation plan must begin with a governance preflight and must encode:

- G0 is blocked until the exact `AUTHORIZE_QXM2_MERGE` token;
- no G1 work may mutate formal Registry until QXM2 `accepted_merged` exists on `main`;
- G1–G5 are separate campaign checkpoints with independent Human/CI gates;
- the program may prepare non-authoritative planning artifacts while a higher-authority gate is blocked, but may not bypass it.
