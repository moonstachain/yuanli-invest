# YIM0｜Yuanli Investment Methodology Map & Projection Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-new-authority Human Methodology Map, add a non-destructive OS vNext bridge, and make `CANON-STATUS` deterministically project the accepted YIP0 → ME0 → ME1 architecture plus parallel capability-program state without rewriting historical identities or authorizing ME2–ME5.

**Architecture:** YIM0 has three production surfaces and one governance/test surface. The Human Projection explains accepted authority but creates none; the OS README bridges Human Grammar to the ME0/ME1 successor architecture without rewriting upstream semantics; `build_canon_status.py` becomes the single deterministic producer of an authority-aware multi-program status projection; a fail-closed YIM0 validator and unit tests enforce the 12 Genesis negatives and prepare a 10/10 Human Review gate.

**Tech Stack:** Markdown, JSON, Python 3.12, `unittest`, GitHub Actions `repository-gates`, existing repository state/receipt files.

**Spec:** `docs/superpowers/specs/2026-08-22-yim0-yuanli-investment-methodology-map-projection-convergence-design.md`

## Global Constraints

- YIM0 is **Human Navigation Projection + Deterministic Canon Status Convergence**, not a new Canon layer.
- Do not modify repository root `README.md`.
- Do not modify `docs/os-vnext/CONSTITUTION.md`.
- Do not modify accepted YIP0 / ME0 / ME1 receipts or historical identity meanings.
- Do not modify production research schemas.
- Preserve `one_core_three_worlds_three_gates_one_loop` and `势 · 信 · 极｜真 · 价 · 生` as Human Grammar.
- Preserve ME0 Genesis Engine semantics: `ENG-C`, `ENG-R`, `ENG-X`; do not claim exhaustiveness.
- Preserve `Human Grammar != Return Engine Ontology`.
- Preserve `Asset != Engine`.
- Preserve `Target != Thesis != Position != Book`.
- Preserve `NO_SILENT_THESIS_MIGRATION`.
- Preserve `Research pass != Capital pass`.
- Preserve `ClaimAuthority <= EvidenceAuthority`.
- Preserve historical `ResearchStateVector`; it is not the sole future canonical state.
- Preserve `semantic_successors_not_in_place_redefinition`.
- ME2–ME5 may be visible as roadmap only and must remain `authorized=false`.
- Do not authorize M3 cutover, Registry admission, portfolio sizing, trading, live execution, A9 switching, or RSI promotion.
- `CANON-STATUS.json` must be regenerated from `scripts/build_canon_status.py`; direct output-only edits are invalid.
- YIP0 lifecycle status must be sourced from `docs/architecture/yip0/YIP0-STATE.json`.
- ME0 lifecycle status must be sourced from `docs/architecture/me0/ME0-STATE.json`.
- ME1 lifecycle status must be sourced from `docs/architecture/me1/ME1-STATE.json`.
- The current Research Capability / QXM program projection must use the current authoritative QXM state chain; on the current base this is QXM2 with next gate `QXM3_THEORY_HYPOTHESIS_REGISTRY_ADMISSION_BENCHMARK_PREREGISTRATION`, not the stale R2.3B0 `QXM1` gate.
- Existing `center_object` / `canonical_state` compatibility fields, if retained, must be explicitly non-normative `legacy_compatibility_only`; `system_identity` / `state_architecture` are the normative semantics.
- Human Review requires `10/10 PASS`.
- Human Acceptance does not imply merge.
- No merge token is defined by this plan; merge authorization remains a later separate owner decision after Human Acceptance.

---

## File Structure

### New files

- `docs/human-projection/YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md` — human-readable Mother Map and deep-link navigation projection.
- `scripts/validate_yim0_methodology_projection.py` — fail-closed YIM0 validator.
- `tests/test_yim0_methodology_projection.py` — positive and negative tests for YIM0 semantics.
- `docs/architecture/yim0/YIM0-STATE.json` — implementation-stage governance projection for YIM0 only.
- `docs/architecture/yim0/YIM0-HUMAN-REVIEW-CARD-v0.1.md` — 10-dimension Human Review card.

### Modified files

- `docs/os-vnext/README.md` — add only `Successor Architecture Bridge` after Human Interface.
- `scripts/build_canon_status.py` — read YIP0/ME0/ME1/current QXM state and produce authority-aware multi-program projection.
- `docs/architecture/CANON-STATUS.json` — generated output only.
- `.github/workflows/ci.yml` — add YIM0 validator in `contracts` job.

### Explicit non-targets

No changes to:

```text
README.md
docs/os-vnext/CONSTITUTION.md
docs/architecture/yip0/* accepted authority/receipt files
docs/architecture/me0/* accepted authority/receipt files
docs/architecture/me1/* accepted authority/receipt files
packages/contracts/schemas/**
canon/**
registry/**
portfolio/**
```

---

### Task 1: Human Projection — Yuanli Investment Methodology Map

**Files:**
- Create: `docs/human-projection/YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md`
- Test: `tests/test_yim0_methodology_projection.py`

**Interfaces:**
- Consumes: `docs/architecture/yip0/YIP0-STATE.json`, `docs/architecture/yip0/YIP0-PHILOSOPHY-CONTRACT-v0.1.json`, `docs/os-vnext/README.md`, `docs/architecture/me0/ME0-AUTHORITY-CONTRACT-v0.1.json`, `docs/architecture/me1/ME1-STATE.json`.
- Produces: one human-facing non-authoritative document containing the approved Mother Map, nine content sections plus `00`, five explanatory cases, three anti-misread guards, and explicit Authority Notice.

- [ ] **Step 1: Write the failing Human Projection contract tests**

Create `tests/test_yim0_methodology_projection.py` with an initial test class that requires the new document to exist and to contain the exact guard strings.

```python
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs/human-projection/YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md"


class YIM0HumanProjectionTests(unittest.TestCase):
    def text(self):
        return MAP.read_text(encoding="utf-8")

    def test_map_exists_with_authority_notice_and_guards(self):
        text = self.text()
        self.assertIn("human navigation projection", text.lower())
        self.assertIn("Human Grammar != Machine Ontology", text)
        self.assertIn("Asset != Engine", text)
        self.assertIn("Target != Thesis != Position != Book", text)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python -m unittest tests.test_yim0_methodology_projection.YIM0HumanProjectionTests -v
```

Expected: FAIL because `YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md` does not exist.

- [ ] **Step 3: Create the Methodology Map with the approved information architecture**

The document must begin with this authority notice in substance and without ambiguity:

```text
This document is a human navigation projection. It does not create ontology, schema, registry, portfolio, trading, execution, or program-stage authority. Where this explanation conflicts with accepted YIP0 / OS Constitution / ME0 / ME1 artifacts, the authoritative artifacts prevail.
```

It must include the Mother Map:

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

The document headings must be exactly represented in this order:

```text
00｜这张地图是什么
01｜哲学本源：我们如何认识投资世界
02｜人类语法：势·信·极｜真·价·生
03｜收益机制：C / R / X
04｜机器对象：Target → Thesis → Passport → Book
05｜研究学习环：PIT / Evidence / Falsifier / Settlement
06｜五资产案例：同一语法，不同物理
07｜ME0–ME5 演进路线
08｜Authority Map：什么能定义什么
09｜十分钟使用方法
```

The five case sections must mention `NVIDIA`, `Gold`, `UST30Y`, `Copper`, `USDJPY` and state that they are explanatory examples only, not current investment conclusions or alpha claims.

The ME0–ME5 roadmap must say ME0 and ME1 are completed accepted architecture while ME2–ME5 are visible roadmap only and `not authorized`.

Do not introduce any new Engine, machine object, score, target price, allocation recommendation or trading instruction.

- [ ] **Step 4: Expand the focused tests to cover the document contract**

Add tests that assert:

```python
self.assertIn("ENG-C", text)
self.assertIn("ENG-R", text)
self.assertIn("ENG-X", text)
self.assertIn("ResearchTarget", text)
self.assertIn("EngineThesis", text)
self.assertIn("PositionPassport", text)
self.assertIn("BookState@PIT", text)
self.assertIn("No Silent Thesis Migration", text)
self.assertIn("ME2", text)
self.assertIn("not authorized", text.lower())
```

Also test that forbidden authority phrases are not asserted positively. Use narrow checks against explicit authorization formulations rather than banning ordinary explanatory words.

- [ ] **Step 5: Run Task 1 tests**

Run:

```bash
python -m unittest tests.test_yim0_methodology_projection.YIM0HumanProjectionTests -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 1**

```bash
git add docs/human-projection/YUANLI-INVESTMENT-METHODOLOGY-MAP-v1.md tests/test_yim0_methodology_projection.py
git commit -m "docs: add Yuanli investment methodology map"
```

---

### Task 2: OS vNext Successor Architecture Bridge

**Files:**
- Modify: `docs/os-vnext/README.md`
- Modify: `tests/test_yim0_methodology_projection.py`

**Interfaces:**
- Consumes: existing `Human interface` block and accepted ME0/ME1 terminology.
- Produces: one non-destructive `Successor Architecture Bridge` inserted after Human Interface and before existing R2.3-A.1 content.

- [ ] **Step 1: Add a failing README bridge test before changing README**

Add:

```python
README = ROOT / "docs/os-vnext/README.md"

class YIM0ReadmeBridgeTests(unittest.TestCase):
    def text(self):
        return README.read_text(encoding="utf-8")

    def test_successor_bridge_exists_without_rewriting_human_grammar(self):
        text = self.text()
        self.assertIn("## Successor Architecture Bridge", text)
        self.assertIn("势 · 信 · 极｜真 · 价 · 生", text)
        self.assertIn("ENG-C / ENG-R / ENG-X", text)
        self.assertIn("ResearchTarget → EngineThesis → PositionPassport → BookState@PIT", text)
```

- [ ] **Step 2: Run focused test and verify RED**

Run:

```bash
python -m unittest tests.test_yim0_methodology_projection.YIM0ReadmeBridgeTests -v
```

Expected: FAIL because the bridge does not yet exist.

- [ ] **Step 3: Add the bridge only; preserve all upstream content**

Insert after `## Human interface` content:

```text
## Successor Architecture Bridge

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

Add prose that explicitly says:

1. Human Grammar is not Return Engine ontology.
2. P/N/E/V/S are shared reusable research primitives/services; no Engine owns them.
3. Asset identity does not determine permanent Engine identity; Engine identity belongs to `EngineThesis`.
4. ME1 is a successor state model; historical RSV is preserved history.
5. C/R/X is a Genesis Engine Set and remains open-world, not a proven exhaustive ontology.

Do not remove or rewrite the current Base OS identity, Human interface, R2.3-A.1 section, Cross-asset architecture test or Authority section.

- [ ] **Step 4: Add non-regression assertions**

Extend tests to ensure README still contains:

```text
one_core_three_worlds_three_gates_one_loop
X | 极 := (Xs, Xa, Xp)
顺大势 · 乘共识 · 押极值｜凭真据 · 买好价 · 永不死
R | Regime Causal Decomposition
Asset form is not pricing model.
```

- [ ] **Step 5: Run Task 2 tests**

Run:

```bash
python -m unittest tests.test_yim0_methodology_projection.YIM0ReadmeBridgeTests -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add docs/os-vnext/README.md tests/test_yim0_methodology_projection.py
git commit -m "docs: bridge OS grammar to ME0 ME1 architecture"
```

---

### Task 3: CANON-STATUS Generator Convergence

**Files:**
- Modify: `scripts/build_canon_status.py`
- Modify: `docs/architecture/CANON-STATUS.json` — generated only
- Modify: `tests/test_yim0_methodology_projection.py`
- Existing compatibility test to keep green: `tests/test_r2_2_refoundation.py`

**Interfaces:**
- Consumes factual state from `YIP0-STATE.json`, `ME0-STATE.json`, `ME1-STATE.json`, and current capability-program state (`QXM2-STATE.json` on the current base).
- Produces a deterministic projection with normative `system_identity`, `state_architecture`, `architecture_lineage`, `latest_completed_architecture_stage`, `roadmap_next_unapproved_stage`, `next_stage_authorized`, and `parallel_programs`.

- [ ] **Step 1: Add failing projection tests for the new normative fields**

Add tests similar to:

```python
import json

STATUS = ROOT / "docs/architecture/CANON-STATUS.json"

class YIM0CanonStatusTests(unittest.TestCase):
    def status(self):
        return json.loads(STATUS.read_text(encoding="utf-8"))

    def test_layered_system_identity_and_successor_state_model(self):
        s = self.status()
        self.assertEqual(s["system_identity"]["mission_center"], "ResearchCapability")
        self.assertEqual(s["system_identity"]["return_reasoning_center"], "EngineThesis")
        self.assertEqual(s["system_identity"]["capital_expression_center"], "PositionPassport")
        self.assertEqual(s["state_architecture"]["historical_canonical_state"], "ResearchStateVector")
        self.assertEqual(
            s["state_architecture"]["successor_state_model"],
            ["ResearchTarget", "EngineThesis", "PositionPassport", "BookState"],
        )
        self.assertFalse(s["state_architecture"]["legacy_future_write_authority"])

    def test_architecture_and_parallel_program_projection(self):
        s = self.status()
        self.assertEqual(s["latest_completed_architecture_stage"], "ME1_COMPLETE")
        self.assertEqual(s["roadmap_next_unapproved_stage"], "ME2")
        self.assertFalse(s["next_stage_authorized"])
        self.assertIn("research_capability_program", s["parallel_programs"])
        self.assertIn("multi_engine_program", s["parallel_programs"])
```

- [ ] **Step 2: Run the new projection tests and verify RED**

Run:

```bash
python -m unittest tests.test_yim0_methodology_projection.YIM0CanonStatusTests -v
```

Expected: FAIL because current projection has only singular `center_object`, singular `canonical_state`, and stale QXM1 next gate.

- [ ] **Step 3: Update the generator inputs**

In `build()` load:

```python
yip0 = load(ARCH / "yip0" / "YIP0-STATE.json")
me0 = load(ARCH / "me0" / "ME0-STATE.json")
me1 = load(ARCH / "me1" / "ME1-STATE.json")
qxm2 = load(ARCH / "qxm2" / "QXM2-STATE.json")
```

Keep the existing R0–R2.3B0 reads because they remain historical projection inputs.

Do not infer YIP0/ME0/ME1 lifecycle values from prose. Read `status`, `next_gate`, merge facts and authorization booleans from their state files.

- [ ] **Step 4: Introduce normative layered projection fields**

Add deterministic output equivalent to:

```python
"system_identity": {
    "mission_center": "ResearchCapability",
    "return_reasoning_center": "EngineThesis",
    "capital_expression_center": "PositionPassport",
},
"state_architecture": {
    "historical_canonical_state": "ResearchStateVector",
    "successor_state_model": [
        "ResearchTarget",
        "EngineThesis",
        "PositionPassport",
        "BookState",
    ],
    "legacy_future_write_authority": False,
},
```

Choose the explicit compatibility representation:

```python
"legacy_compatibility": {
    "center_object": {
        "value": "ResearchCapability",
        "status": "legacy_compatibility_only",
    },
    "canonical_state": {
        "value": "ResearchStateVector",
        "status": "legacy_compatibility_only",
    },
},
```

Do **not** retain top-level singular `center_object` / `canonical_state` as equal normative peers. This plan resolves the ambiguity by moving legacy values under `legacy_compatibility`.

- [ ] **Step 5: Add architecture lineage from state facts**

Produce:

```python
"architecture_lineage": {
    "YIP0": {
        "status": yip0["status"],
        "next_gate": yip0["next_gate"],
        "authority": "philosophy_authority",
    },
    "OS_vNext": {
        "status": "active_semantic_authority",
        "authority": "human_research_grammar",
        "lifecycle_receipt_fabricated": False,
    },
    "ME0": {
        "status": me0["status"],
        "next_gate": me0["next_gate"],
        "authority": "return_engine_ontology",
    },
    "ME1": {
        "status": me1["status"],
        "next_gate": me1["next_gate"],
        "authority": "state_object_model",
    },
    "ME2": {"status": "roadmap_only", "authorized": False},
    "ME3": {"status": "roadmap_only", "authorized": False},
    "ME4": {"status": "roadmap_only", "authorized": False},
    "ME5": {"status": "roadmap_only", "authorized": False},
},
```

No ME2–ME5 lifecycle facts may be invented.

- [ ] **Step 6: Replace stale single-gate projection with multi-program projection**

Add:

```python
"latest_completed_architecture_stage": me1["next_gate"],
"roadmap_next_unapproved_stage": "ME2",
"next_stage_authorized": me1["next_me_stage_authorized"],
"parallel_programs": {
    "research_capability_program": {
        "last_authoritative_stage": qxm2["stage"],
        "status": qxm2["status"],
        "next_gate": qxm2["next_gate"],
        "qxm_f_next_gate": qxm2.get("qxm_f_next_gate"),
    },
    "multi_engine_program": {
        "last_completed_stage": "ME1",
        "completion_gate": me1["next_gate"],
        "next_stage": "ME2",
        "authorized": me1["next_me_stage_authorized"],
    },
},
```

Do not pretend there is one repository-wide `next_gate` once parallel programs exist. If backward compatibility requires retaining `pending_gate_chain` / `next_gate`, move them into `legacy_compatibility` or a clearly named compatibility block and source their value from current QXM2, never stale R2.3B0.

- [ ] **Step 7: Regenerate CANON-STATUS with the builder**

Run:

```bash
python scripts/build_canon_status.py
```

Then:

```bash
python scripts/build_canon_status.py --check
```

Expected:

```text
CANON-STATUS projection: PASS
```

- [ ] **Step 8: Run projection and historical compatibility tests**

Run:

```bash
python -m unittest tests.test_yim0_methodology_projection.YIM0CanonStatusTests -v
python -m unittest tests.test_r2_2_refoundation -v
```

Expected: PASS. The R2.2 test must continue to see `projection_semantics=deterministic_non_authoritative_projection` and historical R2.1 status.

- [ ] **Step 9: Add source-trace tests**

Tests must load YIP0/ME0/ME1/QXM2 states and compare generated values directly so future projection drift fails if a state changes without regenerated output.

For example:

```python
self.assertEqual(s["architecture_lineage"]["YIP0"]["status"], yip0["status"])
self.assertEqual(s["architecture_lineage"]["ME0"]["next_gate"], me0["next_gate"])
self.assertEqual(s["architecture_lineage"]["ME1"]["next_gate"], me1["next_gate"])
self.assertEqual(
    s["parallel_programs"]["research_capability_program"]["next_gate"],
    qxm2["next_gate"],
)
```

- [ ] **Step 10: Commit Task 3**

```bash
git add scripts/build_canon_status.py docs/architecture/CANON-STATUS.json tests/test_yim0_methodology_projection.py
git commit -m "feat: converge canon status on YIP0 ME0 ME1"
```

---

### Task 4: Fail-Closed Validator, Genesis Negatives, CI, and Human Gate

**Files:**
- Create: `scripts/validate_yim0_methodology_projection.py`
- Modify: `tests/test_yim0_methodology_projection.py`
- Create: `docs/architecture/yim0/YIM0-STATE.json`
- Create: `docs/architecture/yim0/YIM0-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: Methodology Map, OS README bridge, generated CANON-STATUS, accepted YIP0/ME0/ME1 state and ME0 authority contract, git diff against the YIM0 repository base.
- Produces: exit 0 only if all YIM0 authority, projection and scope invariants pass; candidate state may reach `candidate_ready_for_human_review` only after exact-head CI success.

- [ ] **Step 1: Write failing import/positive validator test**

Add:

```python
from scripts import validate_yim0_methodology_projection as yim0


class YIM0ValidatorTests(unittest.TestCase):
    def test_repository_yim0_projection_passes(self):
        yim0.main()
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python -m unittest tests.test_yim0_methodology_projection.YIM0ValidatorTests -v
```

Expected: import failure because validator does not exist.

- [ ] **Step 3: Implement focused validator helpers**

Use small functions with explicit purposes:

```python
validate_human_projection()
validate_readme_bridge()
validate_canon_status_projection()
validate_state_source_alignment()
validate_scope_guard()
validate_authority_boundaries()
```

The validator must fail closed through `require(condition, message)` style checks and return exit 0 only after every class passes.

- [ ] **Step 4: Implement the 12 Genesis negatives as independent unit tests**

The test suite must cover exactly these failure classes using temporary/copy data or helper-level inputs rather than mutating repository files in place:

1. Human Projection missing Authority Notice → reject.
2. Human Projection claims ontology/portfolio/trading authority → reject.
3. README removes or redefines `势·信·极｜真·价·生` → reject.
4. README states Human Grammar equals Machine Engine ontology → reject.
5. CANON-STATUS omits YIP0, ME0 or ME1 → reject.
6. RSV is represented as sole future canonical state → reject.
7. ME2 appears without `authorized=false` → reject.
8. Research Capability / QXM parallel program disappears → reject.
9. Generator/source alignment is broken for YIP0/ME0/ME1 lifecycle facts → reject.
10. Human Projection introduces a new machine object or new Engine authority → reject.
11. Scope guard detects Constitution, production schema, or accepted YIP0/ME0/ME1 receipt modification → reject.
12. Scope guard detects root `README.md` modification → reject.

For N11/N12, the implementation may inspect changed paths between the branch merge base and current head. The allowed production change set for YIM0 is:

```python
ALLOWED_PREFIXES = {
    "docs/human-projection/",
    "docs/os-vnext/README.md",
    "docs/architecture/CANON-STATUS.json",
    "docs/architecture/yim0/",
    "docs/superpowers/specs/2026-08-22-yim0-yuanli-investment-methodology-map-projection-convergence-design.md",
    "docs/superpowers/plans/2026-08-22-yim0-yuanli-investment-methodology-map-projection-convergence.md",
    "scripts/build_canon_status.py",
    "scripts/validate_yim0_methodology_projection.py",
    "tests/test_yim0_methodology_projection.py",
    ".github/workflows/ci.yml",
}
```

Do not treat unrelated pre-existing branch history as a YIM0 scope violation; compare against the YIM0 base `877c3bbc59fb6fc01b586b554930bdaca5db4c59` or the branch merge base with main.

- [ ] **Step 5: Create YIM0 candidate state**

Initial state shape:

```json
{
  "schema_version": "0.1.0",
  "stage": "YIM0_YUANLI_INVESTMENT_METHODOLOGY_MAP_PROJECTION_CONVERGENCE",
  "status": "candidate_implementation",
  "repository_base_sha": "877c3bbc59fb6fc01b586b554930bdaca5db4c59",
  "design_acceptance": "ACCEPT_YIM0_YUANLI_INVESTMENT_METHODOLOGY_MAP_PROJECTION_CONVERGENCE_DESIGN",
  "authority": {
    "human_projection_only": true,
    "ontology": false,
    "schema": false,
    "portfolio": false,
    "trading": false,
    "live_execution": false,
    "ME2": false,
    "ME3": false,
    "ME4": false,
    "ME5": false
  },
  "human_gate": {
    "token": "ACCEPT_YIM0_YUANLI_INVESTMENT_METHODOLOGY_MAP_PROJECTION_CONVERGENCE",
    "decision": "pending",
    "acceptance_does_not_imply_merge": true
  },
  "next_gate": "YIM0_MACHINE_QUALIFICATION"
}
```

YIM0 state is a governance record for this convergence effort only. It must not become a new ontology authority.

- [ ] **Step 6: Create the 10-dimension Human Review card**

`docs/architecture/yim0/YIM0-HUMAN-REVIEW-CARD-v0.1.md` must list D1–D10 exactly:

```text
D1 YIP0 → OS → ME0 → ME1 coherent mainline
D2 Human Grammar vs Machine Ontology boundary
D3 C/R/X open-world Genesis Engine Set
D4 Target / Thesis / Passport / Book correctness
D5 No Silent Thesis Migration
D6 README bridge not rewrite
D7 generator-level Projection Drift closure
D8 parallel-program visibility preserved
D9 zero Constitution/schema/portfolio/trading/ME2 authority
D10 new-reader entry experience materially clearer
```

Human Review threshold: `10/10 PASS`.

- [ ] **Step 7: Add the YIM0 validator to contracts CI**

In `.github/workflows/ci.yml`, after ME1 validator and before full unittest discovery, add:

```yaml
      - run: python scripts/validate_yim0_methodology_projection.py
```

Keep existing `python scripts/build_canon_status.py --check` earlier in the job.

- [ ] **Step 8: Run local/focused verification before PR qualification**

Run:

```bash
python scripts/build_canon_status.py --check
python scripts/validate_yim0_methodology_projection.py
python -m unittest tests.test_yim0_methodology_projection -v
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/check_governance.py
```

Expected: PASS.

- [ ] **Step 9: Commit Task 4 implementation**

```bash
git add scripts/validate_yim0_methodology_projection.py tests/test_yim0_methodology_projection.py docs/architecture/yim0/YIM0-STATE.json docs/architecture/yim0/YIM0-HUMAN-REVIEW-CARD-v0.1.md .github/workflows/ci.yml
git commit -m "test: gate YIM0 projection convergence"
```

- [ ] **Step 10: Open or update a Draft PR against main**

Title:

```text
YIM0: converge Yuanli investment methodology map and projections
```

PR body must state:

```text
Human Projection only; no new ontology authority.
README bridge only; no Constitution rewrite.
CANON-STATUS generated from accepted state artifacts.
ME2–ME5 visible but unauthorized.
No Portfolio / Trading / Registry / A9 switch authority.
Human Acceptance does not imply merge.
```

- [ ] **Step 11: Require exact-head repository-gates success**

Do not advance state based on a run for an older head. Require exact current head:

```text
contracts = success
governance = success
build_canon_status --check = success
validate_yim0_methodology_projection = success
full unittest discovery = success
```

- [ ] **Step 12: Advance YIM0 state only after exact-head success**

Update:

```json
"status": "candidate_ready_for_human_review",
"next_gate": "YIM0_HUMAN_REVIEW"
```

Record exact validated head SHA, workflow run number/id, `contracts`, `governance`, `yim0_validator`, and `unit_tests`.

- [ ] **Step 13: Re-run exact-head CI after the state-recording commit**

The state recording creates a new head. Require a second exact-head `contracts=success` and `governance=success` before presenting Human Review.

- [ ] **Step 14: Whole-branch scope review**

Compare against base `877c3bbc59fb6fc01b586b554930bdaca5db4c59` and verify that:

```text
root README unchanged
OS Constitution unchanged
YIP0 accepted artifacts unchanged
ME0 accepted artifacts unchanged
ME1 accepted artifacts unchanged
production schemas unchanged
registry/canon/portfolio unchanged
```

The only architecture-state addition is `docs/architecture/yim0/`.

- [ ] **Step 15: Stop at Human Gate**

Present the 10-dimension Human Review and request only:

```text
ACCEPT_YIM0_YUANLI_INVESTMENT_METHODOLOGY_MAP_PROJECTION_CONVERGENCE
```

Do not merge. Do not authorize ME2. Do not infer merge authorization from Human Acceptance.

---

## Plan Self-Review Checklist

Before execution, verify:

### Spec coverage

- Human Projection: Task 1.
- README bridge: Task 2.
- Generator convergence / compatibility transition / multi-program state: Task 3.
- 12 Genesis negatives: Task 4.
- CI drift protection: Tasks 3–4.
- 10/10 Human Review: Task 4.
- Zero-authority boundaries: Global Constraints + Task 4.
- Root README exclusion: Global Constraints + scope guard.
- YIP0/ME0/ME1 state-source requirement: Task 3.
- Current QXM gate freshness: Task 3 uses QXM2 state rather than stale R2.3B0.

### Type/name consistency

Normative projection keys are frozen in this plan as:

```text
system_identity
state_architecture
legacy_compatibility
architecture_lineage
latest_completed_architecture_stage
roadmap_next_unapproved_stage
next_stage_authorized
parallel_programs
```

Normative successor state list is exactly:

```text
ResearchTarget
EngineThesis
PositionPassport
BookState
```

### No placeholders

No `TBD`, `TODO`, future implementation gaps, or undefined function names are allowed in execution commits.

### Execution stop condition

Machine qualification + second exact-head qualification + whole-branch review lead only to Human Review. They do not authorize merge or ME2.
