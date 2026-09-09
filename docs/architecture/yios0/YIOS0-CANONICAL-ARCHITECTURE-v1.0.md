# YIOS0｜Yuanli Investment OS Canonical Architecture v1.0

**Architecture version:** `1.0.0`  
**System ID:** `YIOS0`  
**Authority role:** System Architecture / Current Definition Authority  
**Objective:** `Lifetime Right-Tail Capture under Survival Constraints`

> **Yuanli Investment OS is a governed intelligence-to-capital machine: it lets Reality enter the system, requires intelligence to accept experimental defeat conditions, separates research authority from capital and execution authority, reconciles execution back to external Reality, and converts outcomes into learning.**

YIOS0 is a composition/discovery Canon. **YIP0 remains philosophy authority**; ME0/ME1, YEX0 and the exact accepted YVN1 stage retain their own detailed domain authority. YIOS0 can describe and route those authorities, but cannot promote them.

## 1｜Mother loop

`Reality → Knowledge → Trial → Settlement → Capital → Execution → Reality → Learning`

Reality is the final external judge. Learning may revise future state, but must not rewrite past evidence or settlement.

## 2｜Four mother laws

1. `Reality > Belief`
2. `Every Intelligence Claim Must Carry a Pre-Registered Defeat Condition` / `凡智必可败`
3. `ResearchPass != CapitalPass`
4. `ResearchAuthority != CapitalAuthority != ExecutionAuthority`

Additional binding laws remain:

- `ClaimAuthority <= EvidenceAuthority`
- `UNKNOWN = DENY`
- `Receipt = Ledger; Status = Projection`
- `ResearchCredential != CapitalCredential != ExecutionCredential != BrokerCredential`

## 3｜Authority topology

```text
YIP0 — Philosophy Authority
  │ constrains
  ▼
YIOS0 — System Architecture / Current Definition Authority
  ├── Knowledge Spine → ME0 / ME1 → capabilities → trials → research settlement
  └── Action Spine    → YEX0 → exact accepted YVN1 stage → execution boundary
                                                     │
                                                     ▼
                                                  Reality
```

YIOS0 does not create scientific settlement, Capital Authority, Execution Authority, broker authority or trading authority.

## 4｜Knowledge Spine

`External Reality → Evidence → PIT → State → Research Capability → Trial → Research Settlement → Learning`

Gold is the Genesis Reality Proof for material portions of this spine. This does not imply universal cross-domain proof.

## 5｜Action Spine

`Research Settlement → Capital Admission → PositionPassport → ExecutionIntent → ActionContract → Execution Runtime → Broker Reality → Reconciliation → Execution Settlement`

YEX0 and YVN1-A0 are accepted constitutional stages. `YVN1-A1`, VeighNa adapter invocation, Broker Paper and Live Execution remain separately gated.

## 6｜Three buses

### Reality Bus
`External World → Reality Gateway → Evidence / PIT → Research State Kernel`

### Intelligence Bus
`State → Capability → Claim → Trial → Settlement → Learning`

### Action Bus
`Research Settlement → Capital Admission → ActionContract → Execution → Market`

Invariant: `REALITY_BUS != ACTION_BUS`. A read-side Reality credential cannot silently become a write-side execution credential.

## 7｜Human explanatory architecture: L0–L12

| Layer | Name | Core contents |
|---|---|---|
| L0 | Philosophy & Authority Constitution | YIP0, accepted research laws, survival constraints |
| L1 | Canon & Control Plane | GitHub, Constitution, Schema, Validator, CI, Version |
| L2 | Reality Gateway | Macro, Filings, IR, Market, Narrative, Alternative Data |
| L3 | Evidence & PIT Plane | Release, Vintage, KnownAsOf, Revision, Provenance |
| L4 | Research State Kernel | Asset, State, Thesis, Evidence, Unknown, Falsifier |
| L5 | Research State Compiler | AssetState@PIT, ThesisState, DriverState, Context Compiler |
| L6 | Research Capability Plane | YMQ4, Market Clock, Narrative, C/R/X, Valuation, Tail |
| L7 | Research Trial Runtime | YRP1, Baseline, PreRegistration, KillGate, Replay, Benchmark |
| L8 | Research Settlement & Learning | Physical / Scientific / Authority Settlement, LearningDelta |
| L9 | Capital & Action Authority | CapitalAdmission, PositionPassport, ExecutionIntent, ActionContract, Authorization Firewall |
| L10 | Execution Runtime | Yuanli Execution Runtime, Provider Adapter, VeighNa, Broker |
| L11 | Execution Settlement & Learning | Reconciliation, Execution Quality, Golden Failure |
| L12 | Human / AI Experience Plane | ChatGPT, Web Cockpit, Notion Human Atlas |

These layers are explanatory architecture. They do not claim thirteen separately deployed microservices exist today.

## 8｜Eight stable machine-service boundaries

1. **Reality Gateway** — acquire and timestamp external Reality.
2. **Research State Kernel** — store structured evidence/state and provenance.
3. **State Compiler** — compile task-scoped point-in-time state objects.
4. **Research Capability Runtime** — execute provider/model-specific research capabilities.
5. **YRP1 Trial & Settlement** — preregistration, benchmark, kill gate, settlement and learning admission once separately accepted.
6. **Projection Gateway** — expose low-authority projections to Notion, Web and ChatGPT.
7. **Capital Action Gateway** — resolve whether settled research may consume Capital Authority.
8. **Execution Runtime** — convert a valid ActionContract into governed execution events and reconciliation.

Provider/capability examples are subordinate to these boundaries: YMQ4/Market Clock/Narrative/C-R-X are research capabilities; VeighNa is an execution provider/runtime adapter, **not investment or research authority**; Notion is Human Projection; ChatGPT is an interface; Web is a cockpit.

## 9｜Deployment-domain reference architecture

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

This is a reference topology, not a mandate to deploy every component or select a cloud vendor.

## 10｜Status ontology

System status is always three-axis:

- `authority_state`
- `reality_state`
- `runtime_state`

A single global `PASS` is forbidden because it collapses different forms of truth and authority. The dynamic snapshot lives in `YIOS0-STATUS-MATRIX.md` and is a Projection, not the underlying fact authority.

Architecture version and runtime maturity are independent. A status-only change does not automatically bump architecture v1.0.

## 11｜Experience Plane and projection law

Canonical direction:

`GitHub Canon → Projection Contract → Notion Human Projection`

Notion may receive a human-readable, progressively disclosed projection. It has no Canon write authority and no PIT/Evidence truth authority.

Allowed reverse path:

`Notion Comment / Review Request → GitHub Issue / Battle / PR → Human Review → Merge → New Canon Revision → Notion Reprojection`

Forbidden:

`Notion Edit → Direct Canon Mutation`

## 12｜Current non-authorizations

The following are explicitly **NOT_AUTHORIZED** by YIOS0 v1.0:

- `YVN1-A1` runtime;
- VeighNa installation or invocation through the YVN1 path;
- broker credentials or broker connection;
- **Broker Paper** orders;
- **Live Execution**;
- real capital movement;
- portfolio/position sizing authority;
- automatic research-to-execution.

No YIOS0 acceptance or merge changes these boundaries.

## 13｜Version law

- **Major:** incompatible mother-loop, authority-topology, Research/Capital/Execution separation, state-ontology, stable service-boundary or projection-contract change.
- **Minor:** backward-compatible architecture addition.
- **Patch:** documentation/clarification without architecture semantic change.
- Runtime/status updates alone do not bump architecture version.

After v1.0 is Human Accepted and merged, incompatible changes create a new architecture version rather than silently rewriting v1.0 semantics.

## 14｜Stable discovery

Humans resolve `docs/architecture/yios0/YIOS0-CURRENT.md` first. Machines resolve `config/yios0/yios0_current.json` first.

A pointer does not self-authorize. “Current Canon” only becomes real when the architecture is present on protected `main`, the valid Human Acceptance Receipt is present, and post-merge Reality readback confirms it.

## 15｜Canonical closure principle

> **ONE SYSTEM DEFINITION, ONE CURRENT POINTER, ONE REALITY STATUS PROJECTION, ONE HUMAN PROJECTION.**

> **Reality enters first. Intelligence may lose. Capital requires a higher authority. Execution must reconcile back to Reality. Learning may revise the future, but it must not rewrite the past.**
