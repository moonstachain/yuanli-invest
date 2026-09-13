# YKS0-G0｜K-Shaped Society Program Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close `YKS0-G0` as a design-only, Human-Accepted program freeze, then sequence `G1–G6` as separately governed child battles without prematurely creating production Supabase, Hugging Face, Notion, UIG runtime, capital, or execution authority.

**Architecture:** `YKS0` is a YIOS0 Knowledge-Spine research capability candidate. `G0` is intentionally limited to the accepted Written Spec plus this implementation/sequencing plan. Each downstream gate (`G1–G6`) is an independent architectural sub-project that must repeat `Written Spec → Human Acceptance → Implementation Plan → Explicit Execution Authorization → Machine Qualification → Human Merge Gate → Post-merge Reality Readback` before the next gate may consume it.

**Tech Stack:** GitHub protected-main governance, Markdown design/plan artifacts, GitHub Actions `repository-gates`, existing YIOS0 authority model; future child gates may use LinkML/Soul Ontology, UIG, Supabase/Postgres, Hugging Face, Notion/Web, but G0 does not invoke them.

**Spec:** `docs/superpowers/specs/2026-09-13-yks0-g0-k-shaped-society-design.md`

## Global Constraints

- `Reality > Belief`
- `Every Intelligence Claim Must Carry a Pre-Registered Defeat Condition`
- `ResearchPass != CapitalPass`
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`
- `ClaimAuthority <= EvidenceAuthority`
- `UNKNOWN = DENY`
- `Receipt = Ledger; Status = Projection`
- Historical evidence and settlement may not be rewritten by later learning.
- No single synthetic `K Score` is admitted.
- GDP-per-capita thresholds may not be promoted into deterministic K laws.
- `r > g` may not be promoted into a timing formula.
- G0 performs no production Supabase writes.
- G0 performs no Hugging Face dataset/job mutation.
- G0 performs no Notion page/database mutation.
- G0 performs no production UIG graph/runtime mutation.
- G0 creates no Capital, portfolio-sizing, broker, paper-order, live-order, or execution authority.
- Notion/Web/ChatGPT/Hugging Face remain projection/experiment surfaces, not Canon or truth authority.
- The accepted G0 spec explicitly states: `G0 itself writes only this design spec and later, after approval, the implementation plan.` Therefore no machine ontology, metric registry, replay dataset, runtime table, or human cockpit may be created inside G0.

---

## 1｜Scope decomposition: six child projects, not one mega-implementation

The accepted spec spans independent subsystems. They MUST remain separate child specs/plans because a reviewer must be able to reject one without implicitly accepting the others.

| Child gate | Purpose | Primary estate | Minimum deliverable before child close | Must NOT be smuggled in |
|---|---|---|---|---|
| `YKS0-G1` | Ontology × Object Model × Metric Registry | `yuanli-strategy-soul` + `yuanli-invest` | LinkML semantic objects, compiled non-authoritative artifacts, metric registry, validators/tests | Supabase data ingestion, HF runs, Notion pages |
| `YKS0-G2` | Reality Gateway × Five-Country PIT Dataset | Supabase/Postgres + object storage + GitHub manifests | vintage-safe observations, exact release calendars, PIT bundles, source manifest | model scoring, scientific PASS, asset recommendation |
| `YKS0-G3` | 50-Case Pre-Registered Blind Replay | HF Blind Lab / replaceable compute + frozen GitHub trial law | blind outputs, baselines, hard negatives, near twins, reveal receipts, scientific settlement | G4 asset alpha claim, capital use |
| `YKS0-G4` | K Regime × Asset Transmission Benchmark | `yuanli-invest` research runtime + quantitative evidence | incremental-value benchmark vs aggregate/market/inequality baselines | automatic allocation, PositionPassport |
| `YKS0-G5` | UIG × Brain Context Gateway Shadow | Soul/UIG + BCG shadow | zero-human-routing, minimal/authority-correct `K-ContextBundle` | production graph authority, write-back |
| `YKS0-G6` | Notion × Web Human Atlas | Experience/Projection Plane | five progressive-disclosure surfaces with parity/readback | Notion-as-Canon, truth mutation |

No child gate is authorized by `ACCEPT_YKS0_G0_WRITTEN_SPEC`. The acceptance only permits this G0 plan and later G0 closure.

---

## 2｜Frozen G0 Reality at plan time

- Repository: `moonstachain/yuanli-invest`
- Branch: `yks0-g0-k-shaped-society-design-20260913`
- Base protected-main SHA at branch creation: `ee497283d0b402e16f43e91abc759355ebe35e5e`
- Accepted design commit: `5094a6cb88cd6d98afaa63045e800fb2ffd34a9d`
- Accepted spec blob SHA: `58a851f0840e23a6d099299c83ca94183ed7551b`
- Draft PR: `#85`
- Human token received: `ACCEPT_YKS0_G0_WRITTEN_SPEC`
- Production mutation count from G0 at plan time: `0`

If protected `main` changes before G0 merge, executor MUST record the new main SHA and inspect whether the drift changes YIOS0 authority semantics. Do not silently copy the design-time base assumption.

---

# Task 1: Bind Human Written-Spec Acceptance without expanding G0 scope

**Files:**
- Modify: `docs/superpowers/specs/2026-09-13-yks0-g0-k-shaped-society-design.md`
- No new acceptance-receipt file is created because the accepted spec explicitly limits G0 repository artifacts to the spec and the plan.

**Interfaces:**
- Consumes: Human decision token `ACCEPT_YKS0_G0_WRITTEN_SPEC`; accepted spec blob `58a851f0840e23a6d099299c83ca94183ed7551b`.
- Produces: the same spec document with status metadata changed from candidate review state to Human-Accepted design state; no implementation authority.

- [ ] **Step 1: Fresh-read the accepted spec at the accepted blob**

Run:
```bash
git show 5094a6cb88cd6d98afaa63045e800fb2ffd34a9d:docs/superpowers/specs/2026-09-13-yks0-g0-k-shaped-society-design.md > /tmp/yks0-g0-accepted-spec.md
sha256sum /tmp/yks0-g0-accepted-spec.md
```
Expected: file exists and is byte-identical to the reviewed spec content; any mismatch blocks status mutation.

- [ ] **Step 2: Update only the acceptance metadata**

Change the header to:
```markdown
**Status:** `WRITTEN_SPEC_HUMAN_ACCEPTED`  
**Human decision:** `ACCEPT_YKS0_G0_WRITTEN_SPEC`  
**Accepted design commit:** `5094a6cb88cd6d98afaa63045e800fb2ffd34a9d`  
**Accepted spec blob:** `58a851f0840e23a6d099299c83ca94183ed7551b`  
**Implementation authority:** `NOT_AUTHORIZED`  
**Merge authority:** `NOT_AUTHORIZED`
```
Do not edit the nine dimensions, objects, hypotheses, 50 replay cases, thresholds, source hierarchy, physical deployment map, or deferred gate boundaries in this step.

- [ ] **Step 3: Verify semantic freeze**

Run:
```bash
git diff -- docs/superpowers/specs/2026-09-13-yks0-g0-k-shaped-society-design.md
```
Expected: diff is limited to status/acceptance metadata. If any research semantics changed, revert and stop.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-09-13-yks0-g0-k-shaped-society-design.md
git commit -m "docs: bind YKS0-G0 written-spec acceptance"
```

---

# Task 2: Verify the G0 two-artifact boundary and repository gates

**Files:**
- Read: `docs/superpowers/specs/2026-09-13-yks0-g0-k-shaped-society-design.md`
- Read: `docs/superpowers/plans/2026-09-13-yks0-g0-program-sequencing.md`
- Read: `.github/workflows/ci.yml`
- No production/runtime file may be created or modified.

**Interfaces:**
- Consumes: G0 spec + plan.
- Produces: verified evidence that G0 contains only design/planning changes and that existing repository gates still pass.

- [ ] **Step 1: Prove changed-file scope against main**

Run:
```bash
git fetch origin main
git diff --name-only origin/main...HEAD
```
Expected G0 paths only:
```text
docs/superpowers/specs/2026-09-13-yks0-g0-k-shaped-society-design.md
docs/superpowers/plans/2026-09-13-yks0-g0-program-sequencing.md
```
Any path under `ontology/`, `research/`, `config/`, `scripts/`, `tests/`, `supabase/`, workflow runtime code, or connector/projection assets is a G0 scope violation.

- [ ] **Step 2: Run repository-local deterministic checks**

Run:
```bash
python scripts/build_manifest.py --check
python scripts/leak_guard.py
python scripts/check_governance.py
python scripts/verify_bootstrap_receipt.py
python -m unittest discover -s tests -p 'test_*.py' -v
```
Expected: all existing checks PASS. G0 adds no new runtime validator because it implements no machine contract.

- [ ] **Step 3: Verify forbidden production strings are not introduced as active authority**

Run:
```bash
git diff origin/main...HEAD -- . | grep -E '^\+.*(LIVE_EXECUTION_AUTHORIZED|BROKER_PAPER_AUTHORIZED|CAPITAL_PASS|NOTION_CANON_WRITE|HF_TRUTH_AUTHORITY|SUPABASE_PRODUCTION_WRITE)' && exit 1 || true
```
Expected: command exits 0 because no such new active-authority claim exists.

- [ ] **Step 4: Commit only if verification generated no repository mutation**

No commit is expected from this task. If a tool produced generated repository files, delete them before proceeding.

---

# Task 3: Exact-head PR qualification for design-only G0

**Files:**
- No file changes required.

**Interfaces:**
- Consumes: branch head after Tasks 1–2 and PR `#85`.
- Produces: exact-head GitHub Actions evidence for the design-only PR.

- [ ] **Step 1: Push the accepted-spec metadata commit**

```bash
git push origin yks0-g0-k-shaped-society-design-20260913
```

- [ ] **Step 2: Wait for `repository-gates` on exact head**

Require both existing job identities:
```text
contracts = success
governance = success
```
Do not invent a YKS0-specific PASS; G0 has no machine implementation yet.

- [ ] **Step 3: Record exact-head evidence in the PR conversation, not a third repo file**

PR comment must include:
```text
YKS0-G0 WRITTEN SPEC: HUMAN ACCEPTED
Decision: ACCEPT_YKS0_G0_WRITTEN_SPEC
Scope: design spec + implementation/sequencing plan only
Exact head: <actual exact head SHA from this run>
repository-gates: contracts SUCCESS / governance SUCCESS
Production mutations: 0
G1 implementation: NOT AUTHORIZED
Merge: NOT AUTHORIZED
```
The executor substitutes the actual SHA and workflow run URL from GitHub Reality; this is an operational evidence value, not a design constant.

---

# Task 4: G0 merge gate — stop for independent Human authorization

**Files:**
- No file changes before authorization.

**Interfaces:**
- Consumes: Human-Accepted spec, plan, exact-head `contracts/governance` success, G0 scope audit.
- Produces: either a blocked state or authorization to merge design-only PR #85.

- [ ] **Step 1: Present the G0 closure card**

The card must explicitly state:
```text
Authority state: WRITTEN_SPEC_HUMAN_ACCEPTED
Reality state: SPEC_AND_PLAN_PHYSICALLY_PRESENT_ON_CANDIDATE_BRANCH
Runtime state: NOT_STARTED
Supabase: NOT_MUTATED
Hugging Face: NOT_MUTATED
Notion: NOT_MUTATED
UIG production runtime: NOT_MUTATED
Capital/Execution: NOT_AUTHORIZED
```

- [ ] **Step 2: Require independent merge token**

Required token:
```text
AUTHORIZE_YKS0_G0_MERGE
```
`ACCEPT_YKS0_G0_WRITTEN_SPEC` MUST NOT be interpreted as merge authorization.

- [ ] **Step 3: Stop if token is absent**

Expected state:
```text
YKS0_G0_READY_FOR_MERGE_AUTHORIZATION
```
Do not merge and do not open G1 implementation work.

---

# Task 5: Merge G0 and perform protected-main Reality readback

**Prerequisite:** explicit `AUTHORIZE_YKS0_G0_MERGE` received after Task 4.

**Files:**
- No new files.

**Interfaces:**
- Consumes: authorized PR #85 exact head.
- Produces: protected-main presence of the two G0 artifacts and fresh post-merge Reality evidence.

- [ ] **Step 1: Re-read PR head and required checks immediately before merge**

Verify the reviewed exact head has not changed and both required checks remain success.

- [ ] **Step 2: Merge through repository rules**

Do not bypass protected-main checks. Use the repository's normal merge method.

- [ ] **Step 3: Fresh-read protected main**

Verify:
```text
docs/superpowers/specs/2026-09-13-yks0-g0-k-shaped-society-design.md
docs/superpowers/plans/2026-09-13-yks0-g0-program-sequencing.md
```
exist on protected `main` and contain the accepted boundaries.

- [ ] **Step 4: Verify post-merge repository-gates**

Require:
```text
contracts = success
governance = success
```
for the merged main revision.

- [ ] **Step 5: Close G0 in the PR discussion**

Use exactly separated status axes:
```text
YKS0-G0 authority_state = HUMAN_ACCEPTED_AND_MERGED
YKS0-G0 reality_state = SPEC_AND_PLAN_READBACK_PROVEN
YKS0-G0 runtime_state = NOT_STARTED
YKS0-G1 = NOT_AUTHORIZED
Production external mutations = 0
```
No single global `PASS` is allowed.

---

# Task 6: Open the next child only as a design battle

**Prerequisite:** G0 merged + post-merge readback + separate user instruction to continue.

**Files for the next design battle only:**
- Future create in `moonstachain/yuanli-invest`: `docs/superpowers/specs/2026-09-13-yks0-g1-ontology-object-model-metric-registry-design.md`
- Future coordinated design target in `moonstachain/yuanli-strategy-soul`: existing LinkML root plus proposed `ontology/domains/investment/k_distribution.yaml`

**Interfaces:**
- Consumes: merged G0 Constitution, object freeze, source hierarchy, metric families, G1 deferred scope.
- Produces: G1 Written Spec only. It does not itself create LinkML classes or compiled artifacts.

- [ ] **Step 1: Require G1 design authorization**

Required token:
```text
AUTHORIZE_YKS0_G1_DESIGN
```

- [ ] **Step 2: Start a fresh isolated branch/worktree from current protected main**

Recommended branch:
```text
yks0-g1-ontology-object-model-metric-registry
```
Use `superpowers:using-git-worktrees` when execution begins.

- [ ] **Step 3: Re-run architectural discovery before writing G1 spec**

Read the current Soul ontology root and its governance/compile/test workflow. Confirm no directory/path assumption from G0 would create a second semantic root.

- [ ] **Step 4: Write G1 spec and stop at Human Gate**

Required Human token after G1 spec review:
```text
ACCEPT_YKS0_G1_WRITTEN_SPEC
```
Only that acceptance permits creation of a separate G1 Implementation Plan.

---

## 3｜Child-gate execution contracts after G0

The following contracts are planning law, not current implementation authorization.

### `YKS0-G1｜Ontology × Object Model × Metric Registry`

**Entry:** merged G0 + `AUTHORIZE_YKS0_G1_DESIGN`.  
**Design must settle:** exact LinkML classes/slots; reuse of existing Soul identity/authority axes; metric-registry object ownership in `yuanli-invest`; deterministic JSON Schema/SHACL/OWL compilation; hard negatives against second semantic roots and scalar K scores.  
**Implementation outputs after separate acceptance:** LinkML semantic objects, metric registry, validators/tests, CI integration, machine qualification receipt.  
**Exit:** semantic replay PASS; zero silent semantic loss; compiled artifacts explicitly non-authoritative; independent merge authorization.  
**Forbidden:** Supabase ingestion, HF runs, Notion surfaces.

### `YKS0-G2｜Reality Gateway × Five-Country PIT Dataset`

**Entry:** G1 merged/readback.  
**Design must settle:** exact series registry; source-class requirements; country-native vs cross-country comparable metrics; release calendars; `observation_period/release_date/known_as_of/revision_date`; immutable evidence-bundle manifest; object-storage/Supabase schema; no future-data leakage.  
**Implementation outputs after separate acceptance:** PIT-safe observation ledger for CN/US/DE/JP/KR; source locators; vintage bundles; coverage/UNKNOWN audit.  
**Exit:** reproducible frozen evidence bundle for all 50 cases, with exact T0 cutoffs ready for blind replay.  
**Forbidden:** scientific reveal, model leaderboard promotion, asset claim.

### `YKS0-G3｜50-Case Pre-Registered Blind Replay`

**Entry:** G2 frozen PIT bundles.  
**Design must settle:** runner contract; model/provider isolation; three baselines; eight hard-negative classes; ten near twins; exact scoring rubric; hidden reveal procedure; candidate thresholds; leakage detector; receipt schema.  
**Implementation outputs after separate acceptance:** blind run manifests, baseline outputs, reveal outputs, scorecards, calibration, failure taxonomy, scientific settlement.  
**Exit:** `PASS_CANDIDATE`, `FAIL`, or `INDETERMINATE`; never force PASS.  
**Forbidden:** G4 asset alpha promotion if structural intelligence fails.

### `YKS0-G4｜K Regime × Asset Transmission Benchmark`

**Entry:** G3 scientific settlement sufficient to justify transmission testing.  
**Design must settle:** selected asset species; conventional aggregate baselines; median-stock/median-firm targets; horizon definitions; PIT-safe prices/returns; incremental-value test; ablations; multiple-comparison discipline; asset falsifiers.  
**Implementation outputs after separate acceptance:** transmission benchmark, baseline comparison, hard negatives, result receipts.  
**Exit:** evidence on whether K regime adds incremental explanatory value.  
**Forbidden:** automatic allocation, sizing, PositionPassport, research-to-capital conversion.

### `YKS0-G5｜UIG × Brain Context Gateway Shadow`

**Entry:** settled YKS0 semantic objects + evidence/replay locators.  
**Design must settle:** mappings to existing UIG object IDs/locators/relations/authority; bounded relations `SUPPORTED_BY`, `CONTRADICTED_BY`, `DERIVED_FROM`, `COMPARES_WITH`, `TRANSMITS_TO`, `TESTED_BY`, `SETTLED_BY`, `SUPERSEDES`; minimal context-bundle schema; fail-closed unknown/stale handling.  
**Implementation outputs after separate acceptance:** read-only shadow resolver/context assembler and Golden Queries/Hard Negatives.  
**Exit:** zero-human-routing shadow can return latest, minimal, authority-correct `K-ContextBundle` without projection-as-truth leakage.  
**Forbidden:** graph inference promotion, write authority, private-body expansion without separate law.

### `YKS0-G6｜Notion × Web Human Atlas`

**Entry:** G5 context path proven and GitHub truth/replay path stable.  
**Design must settle:** Projection Contract; five surfaces (`K Society Cockpit`, `9D K Radar`, `Five-Country Historical Atlas`, `K → Asset Transmission Map`, `Reality / Falsifier Review`); stale/unknown/candidate visual language; parity fields; reverse-review path.  
**Implementation outputs after separate acceptance:** Notion/Web projections only.  
**Exit:** GitHub↔projection parity readback and separate Human UX acceptance.  
**Forbidden:** `Notion Edit → Direct Canon Mutation`.

---

## 4｜Standard Human-Gate pattern for every child

Each G1–G6 MUST use this sequence; no child inherits authority from the previous child's success:

```text
Explore current Reality
→ Written Spec
→ Human token ACCEPT_YKS0_G{n}_WRITTEN_SPEC
→ Implementation Plan
→ explicit execution choice/token
→ TDD / fail-closed implementation
→ exact-head CI / runtime qualification
→ Human Review
→ independent AUTHORIZE_YKS0_G{n}_MERGE
→ protected-main merge
→ post-merge Reality readback
→ only then may G{n+1} consume it
```

Recommended explicit execution tokens:

```text
EXECUTE_YKS0_G1_PLAN_SUBAGENT_DRIVEN
EXECUTE_YKS0_G2_PLAN_SUBAGENT_DRIVEN
EXECUTE_YKS0_G3_PLAN_SUBAGENT_DRIVEN
EXECUTE_YKS0_G4_PLAN_SUBAGENT_DRIVEN
EXECUTE_YKS0_G5_PLAN_SUBAGENT_DRIVEN
EXECUTE_YKS0_G6_PLAN_SUBAGENT_DRIVEN
```

Equivalent inline tokens may be used when the Principal explicitly chooses Inline Execution.

---

## 5｜Program stop conditions

Execution MUST stop and request Human review when any of these occurs:

1. a proposed K object would create a second semantic authority outside the admitted Soul LinkML root;
2. a scalar K score is introduced as Canon rather than a projection;
3. `known_as_of` or revision state cannot be reconstructed for a critical replay metric;
4. fewer than 5/9 dimensions are evidenced for a proposed KState promotion;
5. a critical dimension relies only on D-grade evidence;
6. cross-country metric comparability has neither common definition nor crosswalk nor explicit country-native treatment;
7. hidden future information enters a PIT bundle;
8. hard-negative labels or pass thresholds are modified after first reveal without versioned Human amendment;
9. HF/model output is treated as truth or settlement authority;
10. Notion/Web edits are used to mutate GitHub Canon directly;
11. research output is routed to Capital Action or Execution without independent YIOS0 capital/action law;
12. production external mutation is attempted before the corresponding child gate authorizes it.

---

## 6｜Plan self-review

### Spec coverage

- G0 design-only physical boundary: covered by Global Constraints and Tasks 1–5.
- 9D K Vector / object model / source hierarchy / six regimes / H1–H8 / 50 cases / baselines / hard negatives / near twins / thresholds: preserved as immutable G0 inputs and routed to G1–G4.
- Soul Ontology: isolated to G1.
- Supabase Reality Ledger: isolated to G2.
- HF Blind Lab: isolated to G3.
- Asset transmission: isolated to G4.
- UIG/BCG: isolated to G5.
- Notion/Web: isolated to G6.
- Capital/Execution: explicitly outside YKS0 program authority unless later independent YIOS0 law admits a settled result.

### Placeholder scan

This plan contains no `TBD`, `TODO`, or unbound implementation requirement. Values that must come from future Reality, such as exact future branch head SHA or workflow run URL, are explicitly designated as runtime evidence to be read rather than invented.

### Type/authority consistency

- `KDimension/KMetric/KObservation/KState/KRegime/KTransmission/KReplayCase/KSettlement` remain G0 semantic requirements; actual LinkML ownership starts only at G1.
- `KState@PIT` remains data/state output from G2, not a Notion construct.
- G3 may issue scientific settlement but no CapitalPass.
- G6 is projection only.
- `UNKNOWN = DENY` remains fail-closed throughout.

---

## 7｜Execution handoff

This plan is complete only for **G0 closure and child-gate sequencing**. It intentionally does not contain production implementation code for G1–G6 because the accepted G0 spec requires those to be separately designed and Human Accepted.

Recommended next execution path:

1. execute Tasks 1–4 to close the G0 candidate through exact-head verification and stop at `AUTHORIZE_YKS0_G0_MERGE`;
2. after independent merge authorization, execute Task 5 and fresh protected-main readback;
3. only then request `AUTHORIZE_YKS0_G1_DESIGN` and begin the G1 Written Spec battle.
