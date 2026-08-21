# ME0 | Yuanli Multi-Engine Investment Ontology & Authority Freeze — Design

## 0. Status

- Stage: `ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE`
- Design state: approved in conversation for architectural specification on 2026-08-21
- Repository role: successor ontology / authority-freeze candidate
- Base: `main@bd8931e1bf21dceb5e34a68ec41aa199b83e9410`
- Branch: `me0-multi-engine-ontology-freeze`
- Historical Canon mutation: prohibited in ME0 design phase
- Merge authority: not implied
- Runtime / trading authority: none

## 1. Why ME0 exists

The current repository has a strong research-governance substrate but still binds the top-level machine ontology too tightly to the accepted `P/N/X + E/V/S` research-state grammar.

That grammar has produced several durable assets:

- provider-independent `ResearchCapability` contracts;
- evidence authority and point-in-time semantics;
- falsifiers, failure receipts and future settlement;
- explicit separation between research authority and capital authority;
- no scalar PNX / Force score;
- cross-asset routing through `A0 asset_form` and `A1 pricing_archetype`;
- survival as an independent portfolio constraint.

ME0 does **not** reject those achievements. It addresses a different problem:

> **What is the correct machine ontology for representing why capital is expected to earn a return, when the same research target can simultaneously support multiple distinct return mechanisms?**

The current object graph tends to converge toward one target -> one canonical research-state vector. That is insufficient when the same target can carry a long-horizon compounding thesis, a tactical reflexive repricing thesis and a convex tail-expression thesis at the same time, each with different time horizons, falsifiers, price semantics and capital rules.

ME0 therefore freezes a successor distinction among:

1. **world / research state** — what is true, believed, priced and changing;
2. **return engine** — the mechanism expected to produce portfolio return;
3. **engine thesis** — one target interpreted through one primary return engine;
4. **capital expression** — how a thesis is expressed under portfolio and survival authority.

These are not synonyms and must not be collapsed.

---

## 2. First-principles derivation

### 2.1 Investments earn through mechanisms, not labels

An asset class, sector, theme, narrative label or valuation bucket does not itself explain a return.

The machine must be able to answer:

> **What causal or structural mechanism is expected to transfer future states into investor payoff?**

Therefore:

`asset_form != pricing_archetype != return_engine != position_expression`

### 2.2 The research target is not the thesis

A target such as NVIDIA, UST30Y, Copper, Gold or USDJPY is an object of reality. A thesis is a governed interpretation of that object.

One target may host multiple theses without contradiction if they have distinct return engines, horizons and falsifiers.

Invariant:

> **Target identity must not determine thesis identity.**

### 2.3 One ticker must not imply one engine

An equity can be held because of durable economic compounding, tactical repricing or optional convexity. A commodity can be held because of a reflexive scarcity repricing or expressed through a convex option. A sovereign bond may be a regime/repricing expression while its option may belong to a convexity thesis.

Invariant:

> **Book membership is thesis/position-specific, not ticker-specific.**

### 2.4 Human compression is not machine ontology

`势 · 信 · 极｜真 · 价 · 生` remains a powerful human cognitive compression. It helps a researcher ask whether reality is changing, what the market believes, where asymmetry exists, what evidence is valid, what price embeds and whether survival is protected.

But a human mnemonic must not force every machine object into one serialized dependency chain.

Invariant:

> **Human navigation may compress machine state; it may not erase independent return mechanisms.**

### 2.5 No closed ontology without proof of completeness

A strict claim that exactly three return engines exhaust all investing would be epistemically inconsistent with YIP0 fallibilism.

Carry/harvest, convergence/arbitrage, liquidity provision and other mechanisms may later deserve independent engine identities if replay and mechanism evidence justify them.

Therefore ME0 freezes:

> **C / R / X as the Genesis Engine Set, not a metaphysically complete closed set.**

Machine field:

`engine_registry_closed_world = false`

This preserves current strategic focus without laundering a current design choice into universal truth.

---

## 3. Relationship to YIP0 philosophy authority

YIP0 remains upstream philosophical authority.

ME0 does not repeal:

- `REALITY_OVER_BELIEF`;
- `REFLEXIVITY`;
- `TAIL_ASYMMETRY`;
- `SURVIVAL_FIRST`;
- fallibilism and falsification;
- reality as final settlement authority;
- the distinction between research truth and trading authority.

ME0 does change the proposed **downstream semantic mapping** of those philosophical laws.

YIP0 was accepted under the then-current OS semantics and explicitly preserved `P/N/X + E/V/S`. ME0 must therefore be handled as an explicit successor architecture, never as a silent reinterpretation of YIP0 history.

Authority rule:

```text
YIP0 philosophical laws
        ↓ remain upstream
ME0 successor investment ontology candidate
        ↓ if Human Accepted + separately merged
Research primitives / services + engine contracts
        ↓
EngineThesis / Position / Book / Meta-allocation objects
        ↓
Runtime / Replay / Benchmark / Settlement
```

Historical YIP0 documents and receipts remain immutable ledger facts.

If ME0 is eventually accepted, future YIP0 documentation may gain an explicit compatibility note stating that old OS-node mappings are historical projections of the philosophical laws, while the philosophical laws themselves remain authoritative.

---

## 4. Alternatives considered

### Approach A — Overlay C/R/X on top of the existing P/N/X ontology

Keep `P/N/X + E/V/S` as the machine ontology and add C/R/X only as strategy labels.

**Advantages**

- lowest migration cost;
- minimal disruption to accepted contracts;
- easy backward compatibility.

**Failure mode**

- duplicates semantics;
- leaves the one-target / one-state-vector bias intact;
- C and X continue to compete for `Xs` meaning;
- `R` remains ambiguous between Regime and Repricing;
- engine-specific falsifiers, horizons and books remain secondary labels rather than first-class authority.

**ME0 judgment:** reject as long-term ontology.

### Approach B — Hard replace P/N/X immediately with C/R/X

Rewrite the Constitution and schemas in place.

**Advantages**

- conceptually simple final picture;
- no compatibility layer.

**Failure mode**

- destroys ledger clarity;
- silently changes Human-Accepted meanings;
- conflates research-state primitives with return mechanisms;
- creates a high-risk migration with no replay proof.

**ME0 judgment:** reject.

### Approach C — Authority stratification with semantic successors

Preserve historical Canon; separate philosophical laws, research primitives/services, return engines, thesis objects and capital-expression objects. Freeze C/R/X as Genesis Engines while keeping the engine registry extensible.

**Advantages**

- preserves ledger integrity;
- fixes the ontology error rather than adding labels;
- supports multiple simultaneous theses per target;
- allows engine-specific replay and benchmark law;
- creates a clean path from current contracts to future successors.

**Cost**

- requires explicit successor maps and compatibility projections;
- ME1+ object-model work is non-trivial.

**ME0 recommendation:** adopt Approach C.

---

## 5. Canonical authority layers proposed by ME0

### Layer 0 — Philosophy Authority

Owned by YIP0.

Answers:

> What must any valid Yuanli investment system believe about reality, knowledge, reflexivity, tails and survival?

This layer is not replaced.

### Layer 1 — Research Primitive / Service Authority

Represents states needed by one or more engines.

Examples:

- Reality / structural transition (`P` lineage);
- Belief / expectation regime (`N` lineage);
- Macro regime decomposition;
- evidence authority (`E`);
- price interpretation / implied state (`V` lineage);
- survival constraints (`S`).

These objects are **inputs and constraints**, not themselves return engines.

### Layer 2 — Return Engine Authority

Represents the mechanism expected to produce investor payoff.

Genesis Engine Set:

- `ENG-C | Compounding`
- `ENG-R | Reflexive Repricing`
- `ENG-X | Convexity`

The registry remains open to future evidence-backed engines.

### Layer 3 — Thesis Authority

A typed `EngineThesis` binds one target to one primary return engine under a declared horizon, source of return, evidence graph, price framework and falsifiers.

### Layer 4 — Capital Expression Authority

`PositionPassport`, `BookState`, `AssetGraduationEvent` and `MetaAllocationResearchState` govern how a research thesis may be expressed or handed off.

Research OS may specify these objects and analyze them; actual weights, sizing and execution remain separately governed by Portfolio OS authority.

### Layer 5 — Runtime / Settlement Authority

Wind AI, Codex, `quant-workspace`, Evidence Vault and future Portfolio OS runtimes implement or test the accepted contracts under existing sovereignty rules.

---

## 6. Genesis Engine definitions

### 6.1 `ENG-C | Compounding`

**Stable question**

> Is the primary source of expected return durable economic value creation and reinvestment that compounds through time, purchased at an admissible price?

**Primary source of return**

- growth in owner-relevant economic value / cash flow;
- durable value capture;
- high-return reinvestment;
- balance-sheet resilience that permits duration;
- time itself as an ally when the thesis is correct.

**What C is not**

- generic “good company” classification;
- any equity position by default;
- short-term multiple expansion as the primary thesis;
- narrative strength;
- structural right-tail language without an economic compounding mechanism.

**Canonical research families likely to serve C**

- value pool and market structure;
- value control / moat / bargaining power;
- ROIC / cash conversion / balance sheet;
- reinvestment runway;
- economic durability;
- long-horizon valuation / expected IRR.

**Price semantics**

Price is an admission and expected-return boundary. Re-rating may affect realized return, but C cannot rely on re-rating as its primary source-of-return claim.

### 6.2 `ENG-R | Reflexive Repricing`

**Stable question**

> Is the primary source of expected return a finite-horizon repricing process in which belief, capital flow, price, positioning and later reality reinforce or break one another?

**Primary source of return**

- change in market-implied expectations / discounting;
- capital-flow and positioning feedback;
- narrative diffusion translated into economic expectations;
- reality/earnings realization that validates or breaks the loop;
- leadership, breadth and price confirmation that reveal whether repricing is propagating.

**What R is not**

- all market price movement;
- generic momentum without a declared mechanism;
- macro regime classification itself;
- a synonym for narrative;
- a substitute for evidence about actual reality.

**Canonical research families likely to serve R**

- liquidity / risk-appetite state;
- earnings or reality realization (`ERN` family);
- narrative / expectation diffusion;
- market-clock microstates;
- mainline / leadership / breadth;
- price confirmation and loop breakers.

**Price semantics**

Price is both sensor and participant. It can confirm propagation, alter financing/collateral/attention and feed back into the system. R does not treat “cheap” or “expensive” as a sufficient timing rule.

### 6.3 `ENG-X | Convexity`

**Stable question**

> Is the primary source of expected portfolio payoff a deliberately asymmetric or nonlinear payoff structure in which conditional tail activation and expression geometry dominate the outcome?

**Primary source of return**

- conditional tail activation;
- optionality / nonlinear payout;
- explicit payoff asymmetry;
- volatility, skew, path and timing structure;
- bounded or deliberately engineered left-tail relative to right-tail opportunity where the instrument permits.

**What X is not**

- every high-growth company;
- every monopoly / network effect;
- an asset being “capable of going up a lot”;
- C-style durable value capture renamed as convexity;
- uncalibrated probability-of-being-right.

**Canonical components**

- `Xa | Tail Activation`;
- `Xp | Payoff Geometry`;
- volatility / skew / premium / breakeven / theta / path / liquidity where applicable.

**Price semantics**

Price is the price of convexity: premium, implied distribution, skew, carry/decay and the cost of obtaining the desired payoff geometry.

---

## 7. Cash is not a fourth return engine

ME0 rejects `Cash` as an engine identity.

Cash / liquidity reserve is a **capital state and book role** whose value includes:

- survival buffer;
- option value for future opportunities;
- funding / liquidity resilience;
- ability to avoid forced selling.

Canonical future identity:

`BOOK-CASH | Liquidity Reserve`

This prevents a portfolio container from being confused with a source-of-return mechanism.

---

## 8. Research primitives after ME0

ME0 does not delete P/N/E/V/S semantics. It changes their proposed authority position.

### `P | Reality`

Retained as a research primitive / state family.

Used by C, R and X where relevant.

`P.capital` and `P.asset` remain useful decompositions. Their states do not constitute a return engine by themselves.

### `N | Belief / Expectation`

Retained as a research primitive.

Especially important to R, but may also matter to C valuation and X crowding/tail activation.

`N` must remain distinct from reality.

### `E | Evidence`

Promoted conceptually from a “gate” metaphor to a horizontal **authority plane**.

Invariant remains:

> `Claim Authority <= Evidence Authority`

Every engine thesis, graduation event, book state and meta-allocation research state must remain evidence-addressable.

### `V | Price interpretation`

Retained as a shared service family rather than one universal sequential gate.

Engine-routed semantics:

- C -> long-horizon valuation / implied operating assumptions / expected IRR;
- R -> price confirmation / market-implied expectation change / propagation sensor;
- X -> implied volatility, skew, premium, tail distribution and convexity cost.

Current `CAP-V-01` remains historical Canon. A future successor design may convert it into a routed price-interpretation service without mutating its historical receipt.

### `S | Survival`

Promoted conceptually to a horizontal constraint and later Portfolio OS authority surface.

Survival applies across all engines and books.

A research pass never implies a capital pass.

---

## 9. The `Xs` semantic split

The current `Xs | Structural Asymmetry Source` is too broad for the successor engine ontology because it combines structurally different mechanisms:

- equity value capture / moat / scale;
- commodity scarcity / elasticity;
- rates duration / convexity;
- credit default / recovery / refinancing;
- FX carry / policy divergence;
- monetary scarcity;
- derivative convexity;
- network reflexivity.

ME0 freezes the following migration principle:

> **Structure belongs to the mechanism it actually causes; “asymmetry” is not a universal parent merely because outcomes are uneven.**

Therefore:

- durable value capture, reinvestment and economic concentration -> C or shared asset-physics capabilities;
- regime, scarcity, policy divergence and flow structures -> shared primitives and/or R when they create repricing dynamics;
- tail activation and payoff geometry -> X;
- cross-asset structural physics may remain separate reusable capabilities when they serve more than one engine.

`CAP-XS-01` is not deleted in ME0. It becomes a historical umbrella requiring a future successor map under ME2.

---

## 10. The `R` naming conflict

Current Canon already uses:

`CAP-R-01 | Regime Causal Decomposition`

Its semantic parent is `P.capital`.

ME0 reserves:

`ENG-R | Reflexive Repricing`

These meanings must never share one machine identifier namespace.

Freeze rules:

1. Historical `CAP-R-01` remains immutable and valid as a ledgered capability identity.
2. `ENG-R` is a new **engine namespace**, not a redefinition of `CAP-R-01`.
3. A future semantic successor for macro regime decomposition should use an unambiguous identity such as `CAP-REG-01`.
4. Until that successor is Human Accepted, all current `CAP-R-01` references continue to mean Regime Causal Decomposition.
5. No adapter, validator or runtime may infer `CAP-R-01 == ENG-R`.

This is a P0 semantic safety requirement.

---

## 11. Router architecture

Current routing is retained:

- `A0 | asset_form`
- `A1 | pricing_archetype`

ME0 proposes a new orthogonal routing dimension:

- `A2 | return_engine_route`

Invariant:

> `A0 != A1 != A2`

`A2` is multi-valued at the target opportunity level because the same target may support multiple candidate engine theses.

At thesis creation, however, each `EngineThesis` must declare exactly one `primary_engine`.

Optional secondary mechanism references may exist for context, but no blended weighted engine score is authoritative.

Example:

```text
Target: NVIDIA
A0: equity
A1: growth + compounder
A2 opportunity routes: C, R, X

Thesis 1: primary_engine=C
Thesis 2: primary_engine=R
Thesis 3: primary_engine=X
```

---

## 12. Successor object identities frozen for ME1+

ME0 freezes identities and authority boundaries only. Schemas are implemented later.

### `EngineThesis`

Purpose:

Bind one research target to one primary return engine.

Minimum future semantics:

- `engine_thesis_id`;
- `subject_id`;
- `primary_engine`;
- `source_of_return`;
- `time_horizon`;
- thesis claim;
- state;
- evidence and counter-evidence;
- falsifiers and revision rules;
- engine-routed price framework;
- `as_of` / PIT semantics;
- graduation eligibility.

### `PositionPassport`

Purpose:

Create a governed handoff from one EngineThesis to a potential capital expression.

It must carry the thesis identity forward so a position cannot silently change its reason-for-existing.

Future invariant:

> **No Silent Thesis Migration.**

### `AssetGraduationEvent`

Purpose:

Represent a governed thesis transition, especially `R -> C`, as an auditable event rather than a field edit.

A graduation requires new evidence sufficient for the destination engine; prior P&L or narrative success is not sufficient.

### `BookState`

Genesis books:

- `BOOK-C | Compounder Book`
- `BOOK-R | Reflexive Book`
- `BOOK-X | Convexity Book`
- `BOOK-CASH | Liquidity Reserve`

Book membership follows PositionPassport / thesis identity, not ticker identity.

### `MetaAllocationResearchState`

Purpose:

Compare opportunity quality, crowding, convexity cost, survival pressure and reserve option value across books.

ME0 explicitly prohibits turning this research state into recommended weights or live allocation without separate Portfolio OS authority.

---

## 13. No Silent Thesis Migration Constitution

This is a central ME0 invariant.

A position initiated under one engine must not be re-labeled after adverse price movement merely to avoid admitting thesis failure.

Prohibited examples:

- R trade fails -> silently becomes “long-term C investment”;
- X option loses -> justified with unrelated long-run P or moat evidence;
- C thesis suffers a short-term narrative break -> automatically treated as an R exit without C falsification;
- tactical position is averaged down because another engine has a positive story.

Allowed transition:

A new thesis is created or a governed `AssetGraduationEvent` is executed with destination-engine evidence, new falsifiers and explicit authority.

This invariant is epistemic hygiene and anti-loss-aversion governance, not merely portfolio bookkeeping.

---

## 14. Research dependency graph successor

The current serialized diagnostic sequence remains a historical and human-facing projection:

`P -> Xs -> N -> V -> Xa -> Xp -> S`, E horizontal.

ME0 successor machine orchestration is proposed as:

```text
ResearchTarget
      ↓
OpportunityMap
      ↓
A0 asset_form + A1 pricing_archetype + A2 engine routes
      ↓
Research primitives/services
(P reality, N belief, regime, E evidence, routed V price, S survival)
      ↓
┌──────────────────────────────────────────────┐
│ ENG-C          ENG-R             ENG-X       │
│ Compounding    Reflexive         Convexity   │
│                Repricing                     │
└──────────────────────────────────────────────┘
      ↓ one primary engine per thesis
EngineThesis[]
      ↓ governed handoff
PositionPassport[]
      ↓
BOOK-C / BOOK-R / BOOK-X / BOOK-CASH
      ↓
MetaAllocationResearchState
      ↓
Survival / Portfolio authority boundary
      ↓
Replay -> Benchmark -> Failure -> Settlement -> Revision
```

This graph is not a one-way law of market causality. Reflexive edges remain permitted when represented by evidence-backed mechanisms.

---

## 15. Force Triangle and human projection authority

The Golden Triangle / Force Triangle remains valuable as a human compression and teaching interface.

ME0 proposes that future successor governance classify `ForceTriangleSnapshot` as:

- `projection_only = true`;
- `machine_decision_authority = false`.

Its classifications may summarize research but must not determine engine routing, position authority, book membership or capital allocation by themselves.

ME0 does not delete the current schema or rewrite historical objects.

---

## 16. Capability authority after ME0

`ResearchCapability` remains the durable compounding unit of the repository.

ME0 does **not** replace capabilities with engines.

Distinction:

- **Capability** = reusable research competence;
- **Engine** = return-mechanism ontology;
- **EngineThesis** = one application of evidence/capabilities to one target under one engine;
- **PositionPassport** = governed capital-expression handoff.

One capability may serve several engines.

Examples:

- balance-sheet integrity may serve C durability and R earnings-realization analysis;
- macro regime decomposition may serve R and X activation contexts;
- Price-Implied Expectations may serve C, R and X through routed implementations;
- Evidence Authority Graph serves every engine.

Invariant:

> **Shared Capability does not imply Shared Thesis.**

---

## 17. Engine-specific benchmark law

ME0 freezes that C, R and X must not share one undifferentiated success metric.

### C benchmark family

Evaluate whether the research identified durable economic compounding rather than merely subsequent price appreciation.

Candidate dimensions for later benchmark design:

- value-capture persistence;
- ROIC / cash conversion quality;
- reinvestment durability;
- balance-sheet survival;
- long-horizon false-positive rate;
- incremental value over simple quality/value baselines.

### R benchmark family

Evaluate finite-horizon repricing-state discrimination and propagation.

Candidate dimensions:

- phase / microstate discrimination;
- mainline and leadership precision;
- breadth transition;
- false-theme / false-break rate;
- entry delay and upside capture only when a separately authorized benchmark permits return evaluation;
- loop-break detection.

### X benchmark family

Evaluate payoff geometry and tail-expression quality.

Candidate dimensions:

- false tail activation;
- premium / carry spent;
- realized payoff asymmetry;
- max-loss adherence;
- skew / volatility inference quality;
- path and liquidity failures.

### Meta benchmark family

Future ablations may compare:

- C only;
- R only;
- X only;
- C+R;
- C+X;
- R+X;
- Genesis multi-engine + liquidity reserve.

No benchmark result can grant trading authority by itself.

---

## 18. Historical compatibility and successor map

ME0 is a semantic-successor program, not an in-place rewrite.

Historical objects remain authoritative for the stage in which they were accepted.

Proposed future successor treatment:

| Historical object | ME0 successor treatment |
|---|---|
| `one_core_three_worlds_three_gates_one_loop` | preserve as historical Canon + human navigation projection; no longer sole machine investment ontology if ME0 later accepted |
| `P` | shared reality primitive/state family |
| `N` | shared belief/expectation primitive |
| `E` | horizontal evidence authority plane |
| `V` | routed price-interpretation service family |
| `S` | horizontal survival constraint / Portfolio OS boundary |
| `X := (Xs,Xa,Xp)` | historical structural-asymmetry tuple; `Xs` requires semantic split, `Xa/Xp` migrate naturally to ENG-X |
| `CAP-R-01` | immutable historical Regime capability; future successor uses unambiguous Regime ID |
| `CAP-V-01` | historical Canon retained; future routed service successor allowed |
| `CAP-XS-01` | historical umbrella retained; future typed successors by actual return mechanism |
| `ForceTriangleSnapshot` | future projection-only classification |
| `ResearchStateVector` | future decomposition into target/opportunity state + EngineThesis states |
| `A0/A1` | retain; add orthogonal `A2 return_engine_route` |

No historical receipt, acceptance token or merge fact is rewritten.

---

## 19. Forbidden interpretations

If ME0 is eventually accepted, the following interpretations remain prohibited:

1. `ENG-C`, `ENG-R`, `ENG-X` are scalar scores.
2. C/R/X probabilities can be averaged into one Force score.
3. Exactly one engine must exist per target.
4. C/R/X are proven exhaustive of all investing.
5. `CAP-R-01` means Reflexive Repricing.
6. Any positive P/N/V state automatically authorizes an R thesis.
7. Durable moat / value capture automatically constitutes X convexity.
8. A narrative break automatically invalidates a C thesis.
9. A C thesis automatically permits holding through every price path.
10. An R failure may be relabeled as C without a new governed thesis.
11. A research pass implies a portfolio/capital pass.
12. `MetaAllocationResearchState` implies recommended weights.
13. Book membership is permanently attached to a ticker.
14. Cash is a fourth return engine.
15. Human Force Triangle classification has machine allocation authority.
16. Engine identity replaces evidence, falsification or future settlement.

---

## 20. ME0 scope boundary

ME0 freezes ontology and authority only.

ME0 does **not** authorize:

- modification of `docs/os-vnext/CONSTITUTION.md` on main;
- modification of historical YIP0 Canon or receipts;
- deletion or reinterpretation in place of `CAP-R-01`, `CAP-V-01` or `CAP-XS-01`;
- implementation of `EngineThesis` schema;
- implementation of `PositionPassport` schema;
- implementation of `AssetGraduationEvent` schema;
- implementation of Book or MetaAllocator runtime;
- implementation of Market Clock / L-ERN-N algorithms;
- promotion of C/R/X capabilities;
- Evidence or Outcome admission;
- benchmark execution;
- Portfolio OS sizing / weighting;
- broker or live execution;
- A9 operational-canon switch;
- RSI promotion.

Those require later separately authorized stages.

---

## 21. Proposed program sequence after ME0

### `ME1 | State Object Model Reframe`

Implement the minimum machine contracts for:

`ResearchTarget -> OpportunityState -> EngineThesis -> PositionPassport -> BookState`

### `ME2 | C/X Semantic Separation`

Split historical `Xs` and `ConvexityProfile` semantics by actual return mechanism. Preserve all old receipts.

### `ME3 | Reflexive Repricing Engine & Market Clock Contract`

Compile liquidity / earnings-realization / narrative diffusion, microstates, phase compression, mainline, breadth, leadership and price confirmation into ENG-R contracts.

### `ME4 | Graduation & Meta Allocator Research Contract`

Implement governed thesis migration and book-level research allocation state without granting trading authority.

### `ME5 | Three-Engine Gold Replay & Ablation`

Run engine-specific Gold / hard-negative replay followed by unified shadow ablation. New ontology is promoted only if reality testing shows incremental research value and lower semantic error.

---

## 22. Human Review dimensions

Formal ME0 Human Review should PASS/FAIL at least these dimensions:

1. **First-principles coherence** — return mechanism separated from asset and label.
2. **YIP0 continuity** — philosophical mother laws remain intact.
3. **Ledger integrity** — no historical Human-Accepted object is silently redefined.
4. **Open-world engine rule** — C/R/X are Genesis Engines, not unproven universal completeness.
5. **C definition** — durable economic compounding is distinct from generic quality and rerating.
6. **R definition** — reflexive repricing is distinct from macro Regime and generic momentum.
7. **X definition** — payoff convexity is distinct from C-style moat/value capture.
8. **R namespace safety** — `CAP-R-01 != ENG-R` is explicit.
9. **P/N/E/V/S authority placement** — shared research primitives/services remain usable.
10. **No Silent Thesis Migration** — engine changes require governed events/new thesis authority.
11. **Multi-thesis support** — one target may host multiple engine theses.
12. **Book semantics** — books attach to thesis/position, not ticker.
13. **Cash semantics** — reserve role, not return engine.
14. **ResearchCapability continuity** — capabilities remain durable reusable research units.
15. **Benchmark separation** — C/R/X require different success criteria.
16. **No scalar regression** — no composite Force/engine score becomes ontology.
17. **No capital-authority regression** — no target price, weight, sizing or live action is authorized.
18. **Extensibility** — later engines can be admitted only through evidence/replay/governance.

---

## 23. Proposed acceptance and merge gates

Human acceptance token:

`ACCEPT_ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE`

Acceptance means:

- the ontology and authority boundaries in this design are approved as the ME0 successor candidate;
- implementation of the ME0 candidate pack may proceed under a dedicated contract/state/review/validator change set;
- acceptance does not imply merge.

Future merge authorization token:

`AUTHORIZE_ME0_MERGE`

Merge may occur only after:

- ME0 machine-readable authority contract exists;
- ME0 candidate state exists;
- formal Human Review Card exists;
- successor map is explicit;
- validator fails closed on forbidden reinterpretations;
- existing repository gates remain green;
- exact-head CI is green;
- no historical acceptance or receipt was mutated.

---

## 24. Design self-review

### Placeholder scan

No TBD/TODO placeholder is required for the design to be interpretable. Future capability IDs other than the necessary namespace examples are intentionally not frozen in ME0 because they belong to ME1-ME4.

### Internal consistency

- C/R/X are engines; P/N/E/V/S are primitives/services/constraints.
- `CAP-R-01` remains Regime and is never reused for Repricing.
- Cash is a book role, not an engine.
- multiple engine routes are allowed at opportunity level; exactly one primary engine is required per EngineThesis.
- historical Canon remains ledgered; successor semantics require explicit later acceptance.

### Scope check

ME0 is intentionally limited to ontology and authority freeze. Object schemas, migrations, validator implementation and Canon rewrites are downstream implementation work after Human Review of this design.

### Ambiguity check

The most dangerous ambiguity — whether C/R/X are universally exhaustive — is resolved by freezing an open engine registry with C/R/X as Genesis Engines.

---

## 25. Success criterion for the ME0 design gate

The ME0 design gate is complete when a human reviewer can answer all of the following without consulting unstated assumptions:

- what a return engine is;
- why a target may host multiple theses;
- why C, R and X are different;
- why Cash is not an engine;
- why P/N/E/V/S still matter;
- why `CAP-R-01` cannot be reused;
- how historical Canon remains auditable;
- why engine changes require governed thesis migration;
- what ME0 does not authorize;
- which later stages implement the object model and test it against reality.

If any of these remain ambiguous, ME0 must not proceed to implementation.
