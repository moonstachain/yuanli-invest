# YIOS0｜Yuanli Investment OS Canonical Definition — Design

Date: 2026-09-09  
Status: `DESIGN_CANDIDATE / WRITTEN_SPEC_REVIEW_REQUIRED`  
Scope: `YIOS0 only`  
Architecture approval: `ACCEPT_YIOS0_CANONICAL_DEFINITION_ARCHITECTURE`  
Design base: protected `main` at `e2f06e039dccca45d178ab017654005cdb135666`

## 0. Purpose

YIOS0 creates the first stable, system-level definition of Yuanli Investment OS.

It does **not** create a new investment theory, research model, capital mandate, execution runtime, or trading authority. It composes already accepted laws and current program states into one versioned architecture definition that humans and machines can reliably resolve.

The canonical system statement is:

> **Yuanli Investment OS is a governed intelligence-to-capital machine: it lets Reality enter the system, requires intelligence to accept experimental defeat conditions, separates research authority from capital and execution authority, reconciles execution back to external Reality, and converts outcomes into learning.**

Mother loop:

`Reality → Knowledge → Trial → Settlement → Capital → Execution → Reality → Learning`

YIOS0 must make the answer to **“What is the current Yuanli Investment OS definition?”** resolvable without reconstructing it from chat history or scattered program documents.

YIOS0 is a composition Canon and discovery layer. It does not replace the detailed authority of subordinate Canons such as YIP0, ME0 / ME1, YEX0, or accepted YVN1 stages.

---

## 1. Authority position

YIOS0 is a **system architecture authority and stable discovery layer**. It is not philosophy authority, scientific settlement authority, capital authority, or execution authority.

```text
YIP0
Investment Philosophy Authority
        │ constrains
        ▼
YIOS0
System Architecture / Current Definition Authority
        │ describes + routes, but does not promote child authority
        ├─────────────── Knowledge Spine ───────────────┐
        │                                               │
        │     ME0 / ME1 → YRP1 → Capabilities          │
        │                         → Research Settlement  │
        │                                               │
        └─────────────── Action Spine ──────────────────┤
                                                      │
                              YEX0 → YVN1 → Execution  │
                                                      ▼
                                                   Reality
```

### 1.1 Binding authority rules

1. `YIP0` remains philosophy authority.
2. `ME0 / ME1` retain research ontology authority already earned on `main`.
3. `YRP1`, once separately accepted, governs future research procedure. YIOS0 cannot pre-authorize it.
4. `YEX0` remains the Capital × Execution constitutional boundary.
5. `YVN1` remains execution-plane program authority only to the exact accepted stage.
6. YIOS0 may report a component state; it cannot upgrade that state.
7. `ClaimAuthority <= EvidenceAuthority` remains binding.
8. `ResearchPass != CapitalPass` remains binding.
9. `ResearchAuthority != CapitalAuthority != ExecutionAuthority` remains binding.
10. No YIOS0 merge may authorize broker paper, live execution, real capital movement, or any currently unauthorized downstream stage.

### 1.2 Four mother laws frozen in YIOS0 v1.0

- `Reality > Belief`
- `Every Intelligence Claim Must Carry a Pre-Registered Defeat Condition` / `凡智必可败`
- `ResearchPass != CapitalPass`
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`

YIOS0 does not claim these laws all originated in YIOS0; it composes them into the system-level canonical definition.

---

## 2. One system definition, one Current pointer, one Status projection, one Human projection

YIOS0 v1.0 freezes this topology:

```text
GitHub YIOS0 System Definition
  │
  ├── Immutable Architecture Version
  │
  ├── Stable Current Pointer
  │
  ├── Dynamic Non-Authoritative Status Projection
  │
  └── Machine Contract
          │
          ▼
     Projection Contract
          │
          ▼
Notion Human Projection
```

The invariants are:

`ONE_SYSTEM_DEFINITION_ENTRYPOINT = GitHub / YIOS0`  
`SUBORDINATE_CANONS_RETAIN_DOMAIN_AUTHORITY = true`  
`NOTION_IS_PROJECTION = true`  
`NOTION_CANON_WRITE_AUTHORITY = false`

Notion feedback may create a review request, issue, battle, or PR candidate, but must never directly mutate GitHub Canon authority.

---

## 3. GitHub artifact model

After Written Spec approval, implementation is expected to create the following artifacts.

```text
docs/architecture/yios0/
├── YIOS0-CANONICAL-ARCHITECTURE-v1.0.md
├── YIOS0-CURRENT.md
├── YIOS0-STATUS-MATRIX.md
├── YIOS0-CHANGELOG.md
├── YIOS0-HUMAN-REVIEW-CARD-v1.0.md
├── YIOS0-NOTION-PROJECTION-CONTRACT-v1.0.md
├── YIOS0-MACHINE-QUALIFICATION-RECEIPT-v1.0.md
└── YIOS0-HUMAN-ACCEPTANCE-RECEIPT-v1.0.json

config/yios0/
├── yios0_architecture.v1.json
└── yios0_current.json

scripts/
└── validate_yios0_canonical_definition.py

tests/
└── test_yios0_canonical_definition.py
```

Post-merge GitHub Reality evidence may be recorded in the merged PR conversation plus live protected-main readback. YIOS0 v1.0 does not require a second post-merge PR merely to store a merge SHA inside the repository.

### 3.1 `YIOS0-CANONICAL-ARCHITECTURE-v1.0.md`

Immutable human-readable architecture version.

It contains:

- strategic positioning;
- value proposition;
- mother loop;
- four mother laws;
- two spines;
- three buses;
- twelve-layer human architecture;
- eight-service machine architecture;
- authority boundaries;
- deployment-domain reference architecture;
- Experience Plane roles;
- current non-authorizations;
- versioning law.

After v1.0 is accepted and merged, incompatible architecture change must create a new version rather than silently rewrite v1.0 semantics.

### 3.2 `YIOS0-CURRENT.md`

Stable human discovery pointer.

It does not restate the full architecture. It resolves:

- current architecture version;
- canonical file path;
- machine contract path;
- current status projection path;
- effective date;
- superseded version, if any;
- authority note that runtime state is separate from architecture version.

Any human or AI asked to use “the latest Yuanli Investment OS” should resolve this file first.

### 3.3 `config/yios0/yios0_current.json`

Stable machine discovery pointer.

Required fields:

```json
{
  "system_id": "YIOS0",
  "current_architecture_version": "1.0.0",
  "canonical_architecture_path": "docs/architecture/yios0/YIOS0-CANONICAL-ARCHITECTURE-v1.0.md",
  "machine_contract_path": "config/yios0/yios0_architecture.v1.json",
  "status_projection_path": "docs/architecture/yios0/YIOS0-STATUS-MATRIX.md",
  "human_acceptance_receipt_path": "docs/architecture/yios0/YIOS0-HUMAN-ACCEPTANCE-RECEIPT-v1.0.json",
  "authority_policy": "current_only_when_present_on_protected_main_with_valid_human_acceptance",
  "runtime_status_is_separate": true
}
```

The pointer must not contain a lifecycle value that becomes false merely because the branch is merged. Authority is established from protected-main presence plus the accepted Human Receipt and post-merge readback, not from a self-declared `human_accepted_merged` string in the pointer.

### 3.4 `YIOS0-STATUS-MATRIX.md`

A **dynamic, non-authoritative projection** of current program reality.

It must explicitly state:

`STATUS_MATRIX_IS_PROJECTION = true`

and:

`FACTUAL_AUTHORITY = underlying receipts / main files / separately recorded external runtime readbacks`

Every row must contain or resolve:

- `status_known_as_of`;
- `authority_state`;
- `reality_state`;
- `runtime_state`;
- `evidence_ref`;
- `open_authority_gap`, if one exists.

This file may evolve without changing architecture version, because runtime maturity changes faster than architecture law.

It must never fabricate a completed stage from roadmap intent.

The validator checks structural and evidentiary consistency from repository-local facts. It does **not** make network calls to GitHub or Notion during CI. Live external facts are re-read during qualification / projection operations and captured with `known_as_of`.

Refresh triggers include:

- a child program changes accepted authority state;
- a Reality settlement materially changes scientific state;
- an unauthorized stage becomes separately authorized;
- an architecture-relevant child program is deprecated or superseded.

A stale Status Matrix does not change the architecture version, but Notion must not present stale status as current.

### 3.5 `YIOS0-CHANGELOG.md`

Records architecture revisions only.

Routine runtime state changes do not automatically create an architecture version.

Major version is required when one or more of the following change incompatibly:

- mother loop;
- authority topology;
- Research / Capital / Execution separation;
- state ontology boundary;
- canonical service boundary;
- incompatible projection contract.

Minor versions may add backward-compatible architecture detail without changing the mother laws.

### 3.6 Qualification and Human Acceptance receipts

`YIOS0-MACHINE-QUALIFICATION-RECEIPT-v1.0.md` binds:

- candidate head SHA;
- repository-gates run ID;
- validator result;
- contracts / governance result;
- scope audit;
- live status readback timestamp used to build the Status Matrix.

`YIOS0-HUMAN-ACCEPTANCE-RECEIPT-v1.0.json` binds:

- decision `ACCEPT_YIOS0_CANONICAL_DEFINITION`;
- reviewed machine-qualified head;
- reviewed CI run;
- explicit non-authorizations;
- separate next merge token `AUTHORIZE_YIOS0_MERGE`.

---

## 4. Human architecture: twelve layers

YIOS0 v1.0 freezes the explanatory architecture below.

```text
L12 Human / AI Experience Plane
    ChatGPT · Web Cockpit · Notion Human Atlas

L11 Execution Settlement & Learning
    Reconciliation · Execution Quality · Golden Failure

L10 Execution Runtime
    Yuanli Execution Runtime · Provider Adapter · VeighNa · Broker

L9  Capital & Action Authority
    CapitalAdmission · PositionPassport · ExecutionIntent
    ActionContract · Authorization Firewall

L8  Research Settlement & Learning
    Physical / Scientific / Authority Settlement · LearningDelta

L7  Research Trial Runtime
    YRP1 · Baseline · PreRegistration · KillGate · Replay · Benchmark

L6  Research Capability Plane
    YMQ4 · Market Clock · Narrative · C/R/X · Valuation · Tail

L5  Research State Compiler
    AssetState@PIT · ThesisState · DriverState · Context Compiler

L4  Research State Kernel
    Asset · State · Thesis · Evidence · Unknown · Falsifier

L3  Evidence & PIT Plane
    Release · Vintage · KnownAsOf · Revision · Provenance

L2  Reality Gateway
    Macro · Filings · IR · Market · Narrative · Alternative Data

L1  Canon & Control Plane
    GitHub · Constitution · Schema · Validator · CI · Version

L0  Philosophy & Authority Constitution
    YIP0 · accepted research laws · survival constraints
```

The layers are **human explanatory architecture**, not a claim that twelve independently deployed microservices exist today.

---

## 5. Two spines

### 5.1 Knowledge Spine

Question:

> What are we allowed to know, and why?

Flow:

`External Reality → Evidence → PIT → State → Research Capability → Trial → Research Settlement → Learning`

Gold is the current Genesis Reality Proof for major portions of this spine, but YIOS0 must not call the whole spine universally proven until cross-domain transfer is separately demonstrated.

### 5.2 Action Spine

Question:

> What allows knowledge to become capital action?

Flow:

`Research Settlement → Capital Admission → PositionPassport → ExecutionIntent → ActionContract → Execution Runtime → Broker Reality → Reconciliation → Execution Settlement`

YEX0 and YVN1-A0 are accepted constitutional stages. YVN1-A1 runtime, VeighNa adapter, broker paper, and live execution remain separately gated.

---

## 6. Three buses

### 6.1 Reality Bus

`External World → Reality Gateway → Evidence / PIT → Research State Kernel`

Direction: world → Yuanli.

### 6.2 Intelligence Bus

`State → Capability → Claim → Trial → Settlement → Learning`

Direction: governed reasoning inside Yuanli.

### 6.3 Action Bus

`Research Settlement → Capital Admission → ActionContract → Execution → Market`

Direction: Yuanli → world.

Invariant:

`REALITY_BUS != ACTION_BUS`

No read-side Reality credential may silently become write-side execution authority.

---

## 7. Eight core machine services

YIOS0 uses twelve layers for human explanation but only eight stable service boundaries for machine architecture.

1. **Reality Gateway** — acquires and timestamps external Reality.
2. **Research State Kernel** — stores structured evidence/state and provenance.
3. **State Compiler** — compiles task-scoped point-in-time state objects.
4. **Research Capability Runtime** — executes provider/model-specific research capabilities.
5. **YRP1 Trial & Settlement** — controls preregistration, benchmark, kill gate, settlement, and learning admission once separately accepted.
6. **Projection Gateway** — exposes low-authority human/AI projections to Notion, Web, and ChatGPT.
7. **Capital Action Gateway** — resolves whether a settled research claim may consume capital authority.
8. **Execution Runtime** — converts a valid ActionContract into governed execution events and reconciliation.

Capabilities and providers are subordinate to these boundaries:

- YMQ4 / Market Clock / Narrative / C-R-X = research capabilities;
- YAU1 = human asset-universe projection / ontology experience;
- VeighNa = execution provider/runtime adapter, not OS authority;
- Notion = Human Projection, not Truth;
- ChatGPT = Universal Research Interface, not persistent Canon;
- Web = dynamic research cockpit, not authoritative state source.

---

## 8. Runtime status model: architecture version must not be confused with reality status

YIOS0 v1.0 freezes a three-axis status model.

### 8.1 Authority state

Allowed values:

- `CANON_ACCEPTED_MERGED`
- `HUMAN_ACCEPTED_NOT_MERGED`
- `ARCHITECTURE_ACCEPTED`
- `DESIGN_CANDIDATE`
- `NONE`

### 8.2 Reality state

Allowed values:

- `REALITY_PROVEN`
- `PARTIAL_REALITY_PROOF`
- `SCIENTIFIC_NO_GO`
- `NOT_RUN`
- `NOT_APPLICABLE`

### 8.3 Runtime / deployment state

Allowed values:

- `MAIN_ACTIVE`
- `CANDIDATE_BRANCH`
- `DESIGN_ONLY`
- `NOT_IMPLEMENTED`
- `NOT_AUTHORIZED`

A single label such as “PASS” is insufficient for system-wide status.

### 8.4 Initial v1.0 status snapshot expected at implementation time

The implementation must re-read live repo state before materializing the matrix. At design time, the known baseline is:

| Component | Authority | Reality | Runtime / Deployment | Design-time note |
|---|---|---|---|---|
| YIP0 | CANON_ACCEPTED_MERGED | NOT_APPLICABLE | MAIN_ACTIVE | Philosophy Canon exists on main |
| ME0 / ME1 | CANON_ACCEPTED_MERGED | NOT_APPLICABLE | MAIN_ACTIVE | Ontology authority accepted |
| Gold DP1-A / DP1-B / B2 | CANON_ACCEPTED_MERGED | REALITY_PROVEN | MAIN_ACTIVE | Gold evidence / PIT / baseline path materially proven |
| YMQ4-B3 | NONE | SCIENTIFIC_NO_GO | CANDIDATE_BRANCH | Physical Reality run exists; PR #72 remains Draft / Open / Not Merged |
| YGR0 | DESIGN_CANDIDATE | NOT_RUN | DESIGN_ONLY | Design spec branch exists; no Canon settlement yet |
| YRP1 | ARCHITECTURE_ACCEPTED | NOT_RUN | NOT_IMPLEMENTED | Protocol architecture approved; runtime not built |
| State Compiler | NONE | NOT_RUN | NOT_IMPLEMENTED | Target architecture only |
| YAU1 Notion Portal | DESIGN_CANDIDATE | NOT_RUN | DESIGN_ONLY | Notion-native architecture discussed; no formal acceptance / build yet |
| YEX0 | CANON_ACCEPTED_MERGED | NOT_APPLICABLE | MAIN_ACTIVE | Capital × Execution Constitution accepted |
| YVN1-A0 | CANON_ACCEPTED_MERGED | NOT_APPLICABLE | MAIN_ACTIVE | Shadow Execution Constitution / Deployment Freeze accepted |
| YVN1-A1 | NONE | NOT_RUN | NOT_AUTHORIZED | Eligible for future design only |
| VeighNa Adapter | NONE | NOT_RUN | NOT_AUTHORIZED | Not installed / invoked by YVN1 path |
| Broker Paper | NONE | NOT_RUN | NOT_AUTHORIZED | No broker credential or paper authority |
| Live Execution | NONE | NOT_RUN | NOT_AUTHORIZED | Real capital movement intentionally absent |

The materialized matrix must include `known_as_of` and evidence references. If implementation-time reality differs from this design-time baseline, implementation must use current facts and explicitly record the delta rather than copy this table blindly.

---

## 9. Machine architecture contract

`config/yios0/yios0_architecture.v1.json` is the machine-readable system definition.

Required blocks:

```text
identity
versioning
strategic_positioning
mother_loop
mother_laws
authority_topology
knowledge_spine
action_spine
buses
human_layers
machine_services
experience_plane
deployment_domains
status_semantics
projection_contract
bootstrap_contract
non_authorizations
```

### 9.1 Strategic positioning

Required exact concepts:

- `Governed Intelligence-to-Capital Machine`
- objective: `Lifetime Right-Tail Capture under Survival Constraints`
- Reality is final external judge.

### 9.2 Deployment domains

Reference deployment topology:

```text
CONTROL DOMAIN
GitHub

RESEARCH DOMAIN
Supabase / Postgres + Object Storage + Quant / AI Compute

EXPERIENCE DOMAIN
Notion + Web + ChatGPT

EXECUTION DOMAIN
Capital Action Gateway + Yuanli Execution Runtime + provider adapter
```

These are architectural domains, not a mandate to deploy every component now or to any specific cloud vendor.

### 9.3 Credential separation

Machine contract must preserve:

`ResearchCredential != CapitalCredential != ExecutionCredential != BrokerCredential`

and:

`ResearchProductionHasBrokerWriteAuthority = false`

---

## 10. Notion Human Projection design

### 10.1 Current baseline

The current Notion `原力投研` Domain Registry page is:

`https://app.notion.com/p/3c18e1aaace48127ae39f7baa5335115`

At design time it has:

- `Projection State = candidate`
- `Source Authority = NONE`
- `Canon URI = empty`
- `Canon Revision = empty`
- `Visibility = PRIVATE`

YIOS0 must not silently treat this page as Canon.

### 10.2 Target IA

Do not replace the entire existing `原力投研` journey page with technical architecture.

Create a child Human Projection page under it:

# `原力投研 OS｜最新版定义`

The `原力投研` journey page remains guest-first. The YIOS0 projection is a deeper expert/system definition surface.

### 10.3 Notion page structure

The projection page should use Progressive Disclosure:

1. **What Yuanli Investment OS is** — one sentence, human language.
2. **Current version card** — architecture version / Canon commit / Canon URI / status-known-as-of / last sync / projection state.
3. **Why it exists** — Lifetime Right-Tail Capture under Survival Constraints.
4. **Four mother laws**.
5. **Mother loop**.
6. **Two spines**.
7. **Three buses**.
8. **Twelve-layer architecture**.
9. **Eight machine services**.
10. **Current Reality Status** — separate architecture from actual completion.
11. **Deep links** — YIP0 / Gold / YRP1 / YEX0 / YVN1 / YAU1.
12. **Return path** — back to wealth / investment journey.

Internal project codes must be visually secondary to human-facing explanations.

### 10.4 Domain Registry projection fields

YIOS0 v1.0 must not alter the Domain Registry schema.

After GitHub YIOS0 is separately Human Accepted and merged, the existing `原力投研` Domain Registry row may be updated using existing fields only:

- `Canon URI` → stable GitHub `YIOS0-CURRENT.md` URL;
- `Canon Revision` → `YIOS0 v1.0 @ <merged-sha>`;
- `Source Authority` → `MULTI_CANON` for v1.0 because the current Registry does not contain an `INVEST_CANON` option;
- `Projection State` → `human_review` while Notion projection is under review;
- `Last Reviewed` → actual review date.

Introducing a new `INVEST_CANON` enum is explicitly outside YIOS0 v1.0 scope and requires a separate Portal governance change.

After independent Notion Projection Human Acceptance, `Projection State` may become `published` and the page may receive finite Notion verification. Default verification expiry for v1.0 is 90 days so stale projections become visible rather than silently remaining “current.”

### 10.5 Notion verification semantics

Notion verification means only:

> this Human Projection was reviewed against its GitHub Canon source as of a date.

It never means a research claim is scientifically validated.

`NotionVerification != ResearchSettlement`

### 10.6 Reverse feedback law

Allowed reverse path:

`Notion Comment / Review Request → GitHub Issue / Battle / PR → Human Review → Merge → New Canon Revision → Notion Reprojection`

Forbidden reverse path:

`Notion Edit → Direct Canon Mutation`

---

## 11. Projection sync contract

YIOS0 v1.0 freezes a one-way synchronization contract.

### 11.1 Canon-to-Projection fields

Every published Notion YIOS0 projection must expose:

- `Canon System ID = YIOS0`
- `Architecture Version`
- `Canon URI`
- `Canon Commit SHA`
- `Status Known As Of`
- `Last Synced At`
- `Projection State`
- `Projection Verification State`

### 11.2 Drift rule

If Notion claims a different architecture version or Canon commit from the merged `YIOS0-CURRENT`, the projection becomes stale / requires review; it must not continue to present itself as current.

If the architecture version is unchanged but the status projection is older than a known child-program settlement change, only the **status section** is stale; this does not retroactively invalidate the architecture version.

### 11.3 v1.0 sync mechanism

YIOS0 v1.0 uses **explicit controlled projection**, not background autonomous writeback.

Reason:

- architecture changes are rare;
- Human Projection quality matters more than high-frequency sync;
- avoiding early automation prevents silent cross-system authority drift.

Webhook / automated projection may be introduced later only after a separately accepted projection protocol.

---

## 12. Bootstrap contract

YIOS0 is intended to become the stable first architecture pointer for future AI sessions working on `yuanli-invest`.

Target bootstrap order:

```text
1. YIOS0-CURRENT
2. YIP0
3. YIOS0 machine contract
4. CANON-STATUS / underlying program state
5. task-specific constitution / receipt / runtime evidence
```

YIOS0 must not replace task-specific evidence loading.

The bootstrap invariant is:

`ArchitectureContext != TaskEvidence`

A model may know the OS architecture and still have insufficient authority to answer a current research or capital question.

---

## 13. Validation contract

`validate_yios0_canonical_definition.py` must fail closed on at least the following repository-local conditions:

1. missing immutable v1.0 Canon file;
2. `YIOS0-CURRENT` points to a nonexistent or mismatched version;
3. machine `current` pointer and human `CURRENT.md` disagree;
4. mother loop differs from eight frozen stages;
5. any of the four mother laws is absent;
6. Research / Capital / Execution authority separation is weakened;
7. Notion is described as Canon or Truth authority;
8. VeighNa is described as investment/research authority rather than provider/runtime role;
9. live execution, broker paper, or real capital is implicitly authorized;
10. status matrix uses a single ambiguous `PASS` instead of separate authority/reality/runtime semantics;
11. a `REALITY_PROVEN` row lacks `known_as_of` and a supporting evidence / receipt reference;
12. a `CANON_ACCEPTED_MERGED` row lacks repository-local accepted authority evidence;
13. the materialized B3 row omits `SCIENTIFIC_NO_GO`, omits the not-merged authority gap, or upgrades dynamic beta beyond the captured live readback;
14. YGR0, YRP1, State Compiler, YAU1, YVN1-A1, VeighNa, Broker Paper, or Live are silently promoted above their captured current state;
15. Notion projection contract allows direct Canon mutation;
16. architecture version is automatically bumped by a runtime-only status change;
17. `YIOS0` claims to supersede or rewrite YIP0 philosophical authority;
18. `YIOS0` mutates existing YIP0 / ME0 / ME1 / YEX0 / YVN1-A0 receipts or contracts.

Live GitHub / Notion facts such as PR state, protected-main head, and Notion projection metadata are checked during qualification and projection readback, not by network-dependent CI validation.

---

## 14. TDD and repository integration

After Written Spec approval, implementation must follow RED → GREEN.

Minimum test groups:

- current pointer integrity;
- architecture contract semantics;
- status three-axis semantics;
- authority non-escalation;
- projection one-way law;
- B3 negative evidence representation;
- downstream non-authorization;
- Notion baseline / target projection contract representation;
- no mutation of existing accepted child constitutions.

The YIOS0 validator must be wired into existing `repository-gates` under the protected main workflow.

No merge is allowed on test success alone.

---

## 15. Human Gate sequence

YIOS0 uses separate Human Gates.

### G0 — Architecture

`ACCEPT_YIOS0_CANONICAL_DEFINITION_ARCHITECTURE`

Status: **received**.

This authorizes this Written Design Spec only.

### G1 — Written Spec

Required next token:

`ACCEPT_YIOS0_WRITTEN_SPEC`

This authorizes creation of the implementation plan, not implementation by itself.

### G2 — GitHub Canon Human Acceptance

Expected token after machine qualification:

`ACCEPT_YIOS0_CANONICAL_DEFINITION`

This accepts the machine-qualified GitHub Canon candidate. It does not itself authorize merge.

### G3 — GitHub Merge

Expected token:

`AUTHORIZE_YIOS0_MERGE`

Only after this may the accepted YIOS0 Canon enter protected `main`, followed by post-merge Reality readback.

### G4 — Notion Projection Human Acceptance

After the merged GitHub Canon has been projected into Notion and parity is independently checked:

`ACCEPT_YIOS0_NOTION_PROJECTION`

Only after G4 may the Notion projection be marked `published` / verified.

No G0–G4 token grants YVN1-A1 runtime, VeighNa installation, broker paper, live execution, or real capital movement.

---

## 16. Implementation ordering

After Written Spec approval, the implementation plan must preserve this order:

```text
A. GitHub Canon candidate
   ↓
B. Machine Contract + Validator + Tests
   ↓
C. Dynamic Status Projection from current evidence
   ↓
D. Exact-head CI / Machine Qualification
   ↓
E. G2 Human Acceptance
   ↓
F. G3 Merge + Post-Merge Reality Readback
   ↓
G. Notion Projection built from merged YIOS0 Current
   ↓
H. Cross-System Parity Check
   ↓
I. G4 Notion Projection Human Acceptance
   ↓
J. Publish / Verify Human Projection
```

The Notion page must not become the “current definition” before the GitHub Canon is accepted and merged.

---

## 17. Explicit non-goals

YIOS0 v1.0 does **not**:

- modify YIP0 philosophy;
- rewrite ME0 / ME1 ontology;
- merge or scientifically promote YMQ4-B3;
- implement YGR0;
- implement YRP1;
- implement State Compiler;
- create YAU1 asset databases;
- start YVN1-A1 runtime;
- install or invoke VeighNa;
- create broker credentials;
- connect market-data or broker endpoints;
- authorize paper or live orders;
- move real capital;
- select a cloud vendor as constitutional dependency;
- introduce Kubernetes / Kafka / microservice mandates;
- turn Notion into PIT / Evidence truth;
- change the existing Notion Domain Registry schema.

---

## 18. Acceptance criteria for the Written Spec

This Written Spec is acceptable only if the human reviewer agrees that:

1. YIOS0 is an architecture/current-definition authority, not a new theory or runtime authority.
2. GitHub YIOS0 is the single system-definition entrypoint while subordinate Canons retain detailed domain authority.
3. Notion is Human Projection, not Canon.
4. architecture version and runtime status are separate.
5. human 12-layer architecture and machine 8-service architecture coexist without implying current deployment completeness.
6. two spines and three buses preserve Knowledge / Action separation.
7. status is represented as authority × reality × runtime, not one ambiguous PASS.
8. negative evidence such as B3 cannot disappear from current status.
9. YEX0 / YVN1-A0 authority cannot be expanded by YIOS0.
10. Notion projection is guest-aware, progressive, and version-bound to GitHub.
11. Domain Registry updates happen only after GitHub merge and use existing schema.
12. reverse feedback cannot directly mutate Canon.
13. implementation is split by Human Gates through GitHub Canon and Notion Projection.
14. bootstrap uses YIOS0 as architecture context but still requires task-specific evidence.
15. current-pointer semantics do not self-declare merge authority.
16. CI remains repository-local; live external facts are read during qualification / projection readback.
17. the design creates no broker, paper, live, or capital authorization.

---

## 19. Final design statement

YIOS0 v1.0 is the stable definition layer for Yuanli Investment OS.

Its purpose is not to declare the system complete. Its purpose is to make the difference between **what Yuanli Investment OS is**, **what parts have earned authority**, **what has been proven by Reality**, **what is only designed**, and **what remains unauthorized** impossible to confuse.

Canonical principle:

> **ONE SYSTEM DEFINITION, ONE CURRENT POINTER, ONE REALITY STATUS PROJECTION, ONE HUMAN PROJECTION.**

System principle:

> **Reality enters first. Intelligence may lose. Capital requires a higher authority. Execution must reconcile back to Reality. Learning may revise the future, but it must not rewrite the past.**
