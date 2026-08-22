# YIM0｜Yuanli Investment Methodology Map & Projection Convergence — Design Spec

**Status:** design_candidate_for_human_review  
**Date:** 2026-08-22  
**Repository:** `moonstachain/yuanli-invest`  
**Base:** `main@877c3bbc59fb6fc01b586b554930bdaca5db4c59`

## 0. Purpose

YIM0 is a **Human Navigation Projection + Deterministic Canon Status Convergence** effort.

It does **not** create new ontology, schema, registry, portfolio, trading, execution, Constitution, or ME2–ME5 authority. Its job is to converge the already-accepted architecture into one readable top-level map and to eliminate projection drift in `CANON-STATUS` by fixing the generator rather than hand-editing output.

The three approved changes are:

1. create `docs/human-projection/YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md`;
2. add a successor-architecture bridge to `docs/os-vnext/README.md` without changing the Constitution or root README;
3. update `scripts/build_canon_status.py` and generated `docs/architecture/CANON-STATUS.json` so YIP0/ME0/ME1 and their authority boundaries are projected correctly.

## 1. Authority architecture

### 1.1 Authority lineage

```text
YIP0
Philosophy Authority
        ↓
OS vNext
Human Research Grammar
        ↓
ME0
Return Engine Ontology
        ↓
ME1
State Object Model
        ↓
ME2–ME5
Roadmap only; not authorized by YIM0
```

YIM0 is not a new authority layer. It is a human-readable projection over accepted artifacts.

### 1.2 Core invariants

The human-facing map must preserve these distinctions:

- `Human Grammar != Return Engine Ontology`
- `Asset != Engine`
- `Target != Thesis != Position != Book`
- `Research pass != Capital pass`
- `ClaimAuthority <= EvidenceAuthority`
- `Roadmap visibility != Stage authorization`
- `Projection explains authority; it never creates authority`

### 1.3 Historical identity law

YIM0 follows the accepted policy:

`semantic_successors_not_in_place_redefinition`

Therefore historical `ResearchStateVector` identity is preserved. ME1 is represented as a successor state architecture, not as a retroactive deletion or in-place reinterpretation of RSV.

## 2. Human Projection information architecture

### 2.1 Canonical document

Create:

`docs/human-projection/YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md`

The document begins with an Authority Notice:

> This document is a human navigation projection. It does not create ontology, schema, registry, portfolio, trading, execution, or program-stage authority. Where this explanation conflicts with accepted YIP0 / OS Constitution / ME0 / ME1 artifacts, the authoritative artifacts prevail.

### 2.2 Mother Map

The top of the document presents this chain:

```text
YIP0 Philosophy
实在 · 可错 · 反身 · 演化 · 凸性 · 生存
        ↓
OS Human Grammar
势 · 信 · 极｜真 · 价 · 生
        ↓
ME0 Return Engines
ENG-C / ENG-R / ENG-X
        ↓
ME1 State Objects
ResearchTarget → EngineThesis → PositionPassport → BookState@PIT
        ↓
Learning Loop
Replay → Benchmark → Settlement → Revision
        ↓
Ultimate Objective
Survive → Capture → Compound
```

The three prominent anti-misread guards are:

- `Human Grammar != Machine Ontology`
- `Asset != Engine`
- `Target != Thesis != Position != Book`

### 2.3 Document sections

The document structure is frozen as:

- `00｜这张地图是什么`
- `01｜哲学本源：我们如何认识投资世界`
- `02｜人类语法：势·信·极｜真·价·生`
- `03｜收益机制：C / R / X`
- `04｜机器对象：Target → Thesis → Passport → Book`
- `05｜研究学习环：PIT / Evidence / Falsifier / Settlement`
- `06｜五资产案例：同一语法，不同物理`
- `07｜ME0–ME5 演进路线`
- `08｜Authority Map：什么能定义什么`
- `09｜十分钟使用方法`

The five explanatory targets are NVIDIA, Gold, UST30Y, Copper, and USDJPY. They are examples only and do not create current investment conclusions or alpha claims.

## 3. OS README successor bridge

### 3.1 Non-destructive rule

`docs/os-vnext/README.md` keeps its existing identity:

- `一核 · 三界 · 三门 · 一环`
- `势 · 信 · 极｜真 · 价 · 生`

YIM0 does not rewrite these into C/R/X.

### 3.2 New bridge section

Add a section titled `Successor Architecture Bridge` after the Human Interface section.

Its primary bridge is:

```text
Human Research Grammar
势 · 信 · 极｜真 · 价 · 生
        ↓
Shared Research Primitives / Services
P / N / E / V / S
        ↓
ME0 Return Engine Ontology
ENG-C / ENG-R / ENG-X
        ↓
ME1 State Object Model
ResearchTarget → EngineThesis → PositionPassport → BookState@PIT
```

The bridge explicitly states:

1. Human Grammar is not a Return Engine ontology.
2. P/N/E/V/S are reusable shared research services and are not owned by one engine.
3. Asset identity does not determine permanent engine identity; engine identity belongs to `EngineThesis`.
4. ME1 is a successor state model while historical RSV remains preserved history.

## 4. CANON-STATUS projection convergence

### 4.1 Root cause

Current `scripts/build_canon_status.py` hard-codes:

- `center_object = ResearchCapability`
- `canonical_state = ResearchStateVector`

and only reads the R0–R2.3B0 family. It does not read accepted YIP0 / ME0 / ME1 state files. This is the identified projection-drift source.

### 4.2 Generator-first correction

The implementation must modify `scripts/build_canon_status.py` first and regenerate `docs/architecture/CANON-STATUS.json`. Direct output-only edits are invalid.

The generator must read at least:

- `docs/architecture/yip0/YIP0-STATE.json`
- `docs/architecture/me0/ME0-STATE.json`
- `docs/architecture/me1/ME1-STATE.json`

and project their factual states without hard-coding acceptance/completion outcomes.

The OS vNext human-grammar identity may remain a stable semantic constant derived from its accepted Constitution/README; it must not be represented as a fabricated lifecycle receipt.

### 4.3 Layered system identity and compatibility transition

The authoritative projection moves from a single-center abstraction to layered system identity:

```json
{
  "system_identity": {
    "mission_center": "ResearchCapability",
    "return_reasoning_center": "EngineThesis",
    "capital_expression_center": "PositionPassport"
  },
  "state_architecture": {
    "historical_canonical_state": "ResearchStateVector",
    "successor_state_model": [
      "ResearchTarget",
      "EngineThesis",
      "PositionPassport",
      "BookState"
    ],
    "legacy_future_write_authority": false
  }
}
```

Repository search found no active code consumer of top-level `center_object` / `canonical_state` beyond the builder and projection itself. Even so, YIM0 will not require an abrupt compatibility break. If those legacy top-level fields are retained during the transition, they must be explicitly marked `legacy_compatibility_only` and must not be documented or validated as the unique current architecture.

The new `system_identity` and `state_architecture` semantics are normative. The implementation plan must choose one deterministic compatibility representation and test it; it may not leave two equally authoritative interpretations.

### 4.4 Architecture lineage

Add a deterministic `architecture_lineage` projection that exposes:

- YIP0: factual status sourced from `YIP0-STATE.json`;
- OS vNext: active human research grammar, represented as semantic authority rather than a fabricated stage receipt;
- ME0: factual completed state sourced from `ME0-STATE.json`;
- ME1: factual completed state sourced from `ME1-STATE.json`;
- ME2–ME5: visible roadmap entries with `authorized=false`.

`ME2–ME5` visibility cannot modify any state file or authorize work.

### 4.5 Multi-program projection

A single global `next_gate` is insufficient once capability and multi-engine programs coexist.

The projection must distinguish:

- `latest_completed_architecture_stage`
- `roadmap_next_unapproved_stage`
- `next_stage_authorized`
- `parallel_programs`

The research-capability/QXM track remains visible under `parallel_programs`; YIM0 must not erase or silently supersede it.

Normative example:

```json
{
  "latest_completed_architecture_stage": "ME1_COMPLETE",
  "roadmap_next_unapproved_stage": "ME2",
  "next_stage_authorized": false,
  "parallel_programs": {
    "research_capability_program": {
      "last_authoritative_stage": "R2_3B0"
    },
    "multi_engine_program": {
      "last_completed_stage": "ME1",
      "next_stage": "ME2",
      "authorized": false
    }
  }
}
```

The exact current QXM gate must continue to come from its existing authoritative state source rather than being re-authored by YIM0.

## 5. Success criteria

YIM0 passes only if all five results hold:

1. Human Projection exists and coherently maps YIP0 → OS → ME0 → ME1 → roadmap.
2. OS README gains a bridge without rewriting the upstream grammar or Constitution.
3. CANON-STATUS is generator-derived and accurately projects YIP0/ME0/ME1 plus historical/successor state semantics.
4. CI detects future projection drift.
5. YIM0 grants zero ontology/schema/portfolio/trading/execution/ME2–ME5 authority.

## 6. Scope freeze

### In scope

- new human-projection methodology map;
- OS vNext README bridge;
- `build_canon_status.py` projection logic;
- regenerated `CANON-STATUS.json`;
- focused validator/tests/fixtures required to protect the convergence;
- `docs/architecture/yim0/` governance artifacts when implementation begins.

### Out of scope

- root `README.md`;
- `docs/os-vnext/CONSTITUTION.md`;
- YIP0 accepted authority artifacts;
- ME0 / ME1 receipts or historical identity meanings;
- production research schemas;
- Engine Registry admission;
- Portfolio sizing / allocation;
- trading / execution;
- ME2, ME3, ME4, ME5 implementation or authorization;
- M3 authority cutover;
- A9 operational-canon switching.

## 7. Failure modes

YIM0 must fail closed against at least these classes:

- Human Projection claims machine or capital authority.
- README rewrites human grammar as C/R/X.
- CANON-STATUS exposes ME2 as authorized.
- Single-center regression replaces RSV with one new universal center.
- Existing research-capability/QXM program disappears from projection.
- CANON-STATUS is hand-edited without generator convergence.
- YIP0/ME0/ME1 lifecycle outcomes are hard-coded rather than sourced from their state artifacts.

## 8. Genesis hard negatives

The implementation test pack must include at least these twelve negatives:

1. Human Projection missing Authority Notice → FAIL.
2. Human Projection claims ontology/portfolio/trading authority → FAIL.
3. README removes or redefines `势·信·极｜真·价·生` → FAIL.
4. README states Human Grammar equals Machine Engine ontology → FAIL.
5. CANON-STATUS omits YIP0, ME0, or ME1 → FAIL.
6. RSV remains the only future canonical state → FAIL.
7. ME2 appears as next stage without explicit `authorized=false` → FAIL.
8. QXM/R2.3 parallel program is erased → FAIL.
9. Generator hard-codes YIP0/ME0/ME1 lifecycle outcomes instead of reading state → FAIL.
10. Human Projection defines a new machine object or engine authority → FAIL.
11. YIM0 changes Constitution, production schema, or YIP0/ME0/ME1 accepted receipts → FAIL.
12. Repository root README is modified → FAIL.

## 9. Human Review Gate

Human Review requires `10/10 PASS` across:

1. YIP0 → OS → ME0 → ME1 forms one coherent mainline.
2. Human Grammar vs Machine Ontology boundary is explicit.
3. C/R/X remain an open-world Genesis Engine Set, not an exhaustive universal classification.
4. Target / Thesis / Passport / Book semantics remain correct.
5. No Silent Thesis Migration is preserved.
6. OS README change is a bridge, not an upstream rewrite.
7. Projection drift is fixed at generator level.
8. Parallel program visibility is preserved.
9. No Constitution/schema/portfolio/trading/ME2 authority is granted.
10. New-reader entry experience is materially clearer rather than more complex.

## 10. Implementation decomposition

After written-spec acceptance, the implementation plan should contain four main tasks:

1. **Human Projection** — create the methodology map.
2. **OS README Bridge** — add the non-destructive successor bridge.
3. **CANON-STATUS Generator Convergence** — update generator and regenerated output, including the explicit compatibility transition for legacy singular fields.
4. **Validator / Negatives / Human Gate** — add fail-closed tests, run CI, and prepare governance state.

Each task should be independently reviewable and use test-first development where executable behavior is involved.

## 11. YIM0 constitutional rules

1. **Projection explains authority; it never creates authority.**
2. **README bridges systems; it does not rewrite upstream constitutions.**
3. **Status must be generated from receipts/states, not hand-narrated.**
4. **Roadmap visibility never implies stage authorization.**

## 12. Approval chain

Approved design sections:

- `APPROVE_YIM0_SECTION1_AUTHORITY_ARCHITECTURE`
- `APPROVE_YIM0_SECTION2_METHODOLOGY_MAP_INFORMATION_ARCHITECTURE`
- `APPROVE_YIM0_SECTION3_README_CANON_STATUS_PROJECTION_DESIGN`
- `APPROVE_YIM0_SECTION4_TESTS_FAILURE_HUMAN_GATE_SCOPE_FREEZE`

This spec does not authorize implementation. Implementation planning may begin only after explicit written-spec Human Acceptance.
