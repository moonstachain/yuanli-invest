# YKS0-R0｜Five-Country 1990–2026 Research Estate × Evidence Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the accepted YKS0-R0 design into a durable five-country research estate that preserves source facts, Yuanli research inferences, PIT readiness, counterevidence, replay candidates, and desktop scientific status without claiming formal replay qualification or creating production runtime authority.

**Architecture:** GitHub `yuanli-invest` is the research/evidence estate for R0. The implementation creates a bounded `research/k-shaped-society/` tree, a fail-closed validator, deterministic discovery manifest, and five-country evidence/report artifacts. Soul ontology, Supabase/Object Storage, Hugging Face, Notion/Web, UIG/Brain Context Gateway, Capital, Broker, and Execution remain untouched. R0 records desktop research and PIT readiness only; G2/G3 retain authority for vintage-safe Reality reconstruction and blind replay.

**Tech Stack:** Markdown, JSON, Python 3.12 standard library, existing `jsonschema==4.25.1`, existing repository `repository-gates`, `leak_guard.py`, `build_manifest.py`, GitHub protected-main workflow.

**Spec:** `docs/superpowers/specs/2026-09-13-yks0-r0-five-country-research-estate-design.md`

## Global Constraints

- Human acceptance token is `ACCEPT_YKS0_R0_RESEARCH_ESTATE_WRITTEN_SPEC`.
- Accepted design branch is `yks0-r0-five-country-research-estate-design-20260913` from protected `main@8b30065d00f1c6aa321c9caf875b36b8a0b2d754`.
- `Reality > Belief`.
- `ClaimAuthority <= EvidenceAuthority`.
- `UNKNOWN = DENY`.
- `ResearchPass != CapitalPass`.
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`.
- Preserve exactly `US / DE / JP / KR / CN` and `K01..K09`.
- No scalar K score, weighted K composite, or hidden single-number K ranking.
- Keep `Source Fact`, `Research Inference`, and `Scientific Status` as separate fields/layers.
- Every decisive claim requires explicit source IDs and counterevidence/gaps where present.
- Every source/candidate case must declare one PIT status: `PIT_NATIVE / PIT_RECONSTRUCTABLE / CURRENT_ONLY / BACKTEST_OR_RESTATED / UNKNOWN`.
- Formal replay eligibility requires `PIT_NATIVE` or separately validated `PIT_RECONSTRUCTABLE`; R0 itself does not validate reconstructed historical vintages.
- R0 maximum scientific authority is `STRONG_PRIOR / FORMAL_PIT_VALIDATION_REQUIRED`; unconditional scientific `PASS` is forbidden.
- Asset mapping is limited to `KRegime -> Value Capture -> Earnings/Cash-flow Distribution -> Ownership -> Price/Valuation/Discount Rate/Liquidity -> Relative Return Candidate`.
- Forbidden outputs include target price, buy/sell, recommended weight, target weight, position size, broker action, paper order, live order, or automatic execution.
- Do not create or mutate production Supabase/Object Storage, Hugging Face, Notion/Web, UIG/Brain Context Gateway, Soul ontology, broker, capital, or execution assets.
- Do not create a tenth global Research Capability Registry or a second Evidence authority.
- Use existing `packages/contracts/schemas/evidence.schema.json` semantics as the compatibility floor; local R0 metadata may be richer but must not silently increase authority.
- Later physical retrieval does not grant information to earlier T0. `observed_at` must never be substituted for historical `known_as_of`.
- Revision/backtest data must never be laundered into PIT-native evidence.
- If true subagent dispatch is unavailable, record that as a Ruling and preserve task-scoped independent review; do not claim fresh-agent review occurred.

---

## File map

### Create

```text
research/k-shaped-society/README.md
research/k-shaped-society/reports/YKS0-R0-FIVE-COUNTRY-1990-2026-RESEARCH.md
research/k-shaped-society/reports/YKS0-R0-DIVERGENCE-ASSET-MAP.md
research/k-shaped-society/countries/US.md
research/k-shaped-society/countries/DE.md
research/k-shaped-society/countries/JP.md
research/k-shaped-society/countries/KR.md
research/k-shaped-society/countries/CN.md
research/k-shaped-society/evidence/source-registry.json
research/k-shaped-society/evidence/evidence-claims.json
research/k-shaped-society/evidence/source-authority-policy.md
research/k-shaped-society/dimensions/k-dimension-evidence-matrix.json
research/k-shaped-society/hypotheses/hypothesis-registry.json
research/k-shaped-society/replay/case-candidate-registry.json
research/k-shaped-society/replay/pit-readiness-matrix.json
research/k-shaped-society/settlements/YKS0-R0-DESKTOP-SETTLEMENT.md
research/k-shaped-society/manifests/research-estate-manifest.json
scripts/validate_yks0_r0_research_estate.py
tests/test_yks0_r0_research_estate.py
```

### Modify

```text
docs/superpowers/specs/2026-09-13-yks0-r0-five-country-research-estate-design.md
.github/workflows/ci.yml
```

### Must remain untouched

```text
ontology/**
supabase/**
notion/**
huggingface/**
UIG/BCG production registries or runtime config
canon/** except pre-existing files read for compatibility
broker/execution/capital runtime files
```

---

# Task 1: Bind Human Acceptance and freeze execution branch scope

**Files:**
- Modify: `docs/superpowers/specs/2026-09-13-yks0-r0-five-country-research-estate-design.md`
- Read: `.github/workflows/ci.yml`
- Read: `packages/contracts/schemas/evidence.schema.json`
- Read: `docs/architecture/yios_g1/YIOS-G1-G1-GOLD-EVIDENCE-PACK-T0-v1.md`

**Interfaces:**
- Consumes: Human token `ACCEPT_YKS0_R0_RESEARCH_ESTATE_WRITTEN_SPEC` and accepted design content.
- Produces: acceptance-bound spec metadata only; no research estate content yet.

- [ ] **Step 1: Fresh-read spec and capture current blob SHA**

Run:
```bash
git show HEAD:docs/superpowers/specs/2026-09-13-yks0-r0-five-country-research-estate-design.md > /tmp/yks0-r0-spec.md
git hash-object /tmp/yks0-r0-spec.md
```
Expected: current spec is the Human-reviewed candidate and no implementation files exist yet.

- [ ] **Step 2: Change only acceptance metadata**

Header must contain:
```markdown
**Status:** `WRITTEN_SPEC_HUMAN_ACCEPTED`
**Human decision:** `ACCEPT_YKS0_R0_RESEARCH_ESTATE_WRITTEN_SPEC`
**Implementation authority:** `NOT_AUTHORIZED`
**Merge authority:** `NOT_AUTHORIZED`
**Production runtime mutations:** `0`
```
Do not rewrite research semantics in this step.

- [ ] **Step 3: Prove metadata-only diff**

Run:
```bash
git diff -- docs/superpowers/specs/2026-09-13-yks0-r0-five-country-research-estate-design.md
```
Expected: only status/acceptance metadata changes.

- [ ] **Step 4: Commit acceptance binding**

```bash
git add docs/superpowers/specs/2026-09-13-yks0-r0-five-country-research-estate-design.md
git commit -m "docs: bind YKS0-R0 research-estate acceptance"
```

---

# Task 2: Write the fail-closed validator first (RED)

**Files:**
- Create: `tests/test_yks0_r0_research_estate.py`
- Create: `scripts/validate_yks0_r0_research_estate.py`

**Interfaces:**
- Consumes: accepted R0 file topology and invariants.
- Produces: `validate_estate(root: Path) -> dict[str, int | str]` and CLI exit 0/1.

- [ ] **Step 1: Write failing structural tests before estate files exist**

Create tests with exact constants:

```python
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_yks0_r0_research_estate.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("yks0_r0_validator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_expected_country_and_dimension_sets_are_closed():
    module = load_validator()
    assert module.COUNTRIES == {"US", "DE", "JP", "KR", "CN"}
    assert module.DIMENSIONS == {f"K{i:02d}" for i in range(1, 10)}
```

Also write a test asserting `validate_estate(ROOT)["status"] == "VALID"`; before estate files exist it must fail because required paths are absent.

- [ ] **Step 2: Run RED**

```bash
python -m unittest tests.test_yks0_r0_research_estate -v
```
Expected: failure caused by missing estate content, not import/syntax errors.

- [ ] **Step 3: Implement validator skeleton with explicit invariants**

Minimum constants/functions:

```python
COUNTRIES = {"US", "DE", "JP", "KR", "CN"}
DIMENSIONS = {f"K{i:02d}" for i in range(1, 10)}
PIT_STATES = {"PIT_NATIVE", "PIT_RECONSTRUCTABLE", "CURRENT_ONLY", "BACKTEST_OR_RESTATED", "UNKNOWN"}
CASE_STATES = {"CANDIDATE_DESKTOP", "PIT_AUDIT_REQUIRED", "PREREGISTRATION_READY", "REJECTED"}
FORBIDDEN_TERMS = {
    "recommended_weight", "target_weight", "position_size", "broker_action",
    "live_execution_authorized", "replay_pass", "scientific_pass"
}


def load_json(path: Path): ...
def validate_estate(root: Path) -> dict[str, int | str]: ...
def main() -> int: ...
```

Validator must fail closed for missing manifest paths, wrong country/dimension sets, scalar K-score keys, missing source IDs, missing PIT state, replay-qualified case status, forbidden investment/action keys, desktop settlement claiming unconditional PASS, or manifest authorization flags set true.

- [ ] **Step 4: Keep test RED for the right reason**

```bash
python -m unittest tests.test_yks0_r0_research_estate -v
```
Expected: validator loads and fails because estate files do not yet exist.

- [ ] **Step 5: Commit RED contract**

```bash
git add scripts/validate_yks0_r0_research_estate.py tests/test_yks0_r0_research_estate.py
git commit -m "test: freeze YKS0-R0 research estate invariants"
```

---

# Task 3: Build evidence authority policy and source registry

**Files:**
- Create: `research/k-shaped-society/evidence/source-authority-policy.md`
- Create: `research/k-shaped-society/evidence/source-registry.json`
- Create: `research/k-shaped-society/evidence/evidence-claims.json`

**Interfaces:**
- Produces source IDs consumed by country dossiers, dimensions, hypotheses, case candidates, and reports.

- [ ] **Step 1: Freeze local source record shape**

Every source record must contain:

```json
{
  "source_id": "SRC-YKS0-US-FED-DFA-001",
  "title": "...",
  "issuer": "...",
  "published_at": "YYYY-MM-DD|UNKNOWN",
  "local_grade": "A1",
  "coarse_grade": "A",
  "source_type": "official|academic|index_provider|industry_primary|secondary",
  "url": "https://...",
  "logical_locator": "section/table/page/series",
  "country_scope": ["US"],
  "k_dimensions": ["K06"],
  "hypothesis_ids": ["H3"],
  "stance": "support|counter|mixed|method",
  "pit_status": "CURRENT_ONLY",
  "known_as_of": null,
  "revision_notes": "...",
  "source_fact_summary": "..."
}
```

Rules: `coarse_grade` must be the non-upgrading projection from the accepted local grade; `source_fact_summary` must paraphrase only what the source supports; `known_as_of` is null when not established.

- [ ] **Step 2: Revalidate the initial anchor set from primary/academic/index-provider sources**

At minimum revalidate and register the 17 accepted anchors from the spec: OECD wage/productivity; Autor superstar firms; OECD revisions; FRED/ALFRED realtime method; Fed DFA; S&P concentration/equal weight; OECD Germany bargaining/productivity-wage; STOXX Germany; BOJ wage/productivity; BOJ small/large firms; JPX TOPIX Large70/TOPIX; OECD Korea chaebol/trickle-down; OECD Korea SME catch-up; STOXX Korea; China NBS household/GDP/productivity; China NBS industrial profits; World Bank China Gini.

For every numerical statement, store the exact source locator and distinguish current/retrospective evidence from historical PIT evidence.

- [ ] **Step 3: Write evidence claims as fact/inference pairs**

Each record must contain:

```json
{
  "claim_id": "YKS0-CLM-KR-D-C-001",
  "country": "KR",
  "k_dimensions": ["K02", "K03", "K04"],
  "divergence_targets": ["D-C"],
  "source_ids": ["SRC-YKS0-KR-OECD-001"],
  "counterevidence_ids": [],
  "source_fact": "...",
  "research_inference": "...",
  "scientific_status": "DESKTOP_PRIOR",
  "pit_qualified": false
}
```

No claim may set `pit_qualified=true` in R0 unless the source itself is `PIT_NATIVE` and the exact T0 fact is independently verifiable; otherwise fail closed.

- [ ] **Step 4: Add counterevidence before synthesis**

Register at least the accepted hard-negative anchors: Japan Large70 underperformance vs TOPIX; Germany sector/global exposure confounder; Korea SME productivity catch-up; Japan aggregate-stagnation control. Counterevidence is not optional metadata.

- [ ] **Step 5: Run validator**

```bash
python scripts/validate_yks0_r0_research_estate.py
```
Expected: still nonzero because remaining estate paths are absent, but evidence-specific validation must be clean.

- [ ] **Step 6: Commit evidence layer**

```bash
git add research/k-shaped-society/evidence scripts/validate_yks0_r0_research_estate.py tests/test_yks0_r0_research_estate.py
git commit -m "research: add YKS0-R0 evidence authority and source registry"
```

---

# Task 4: Build five country dossiers with symmetrical structure

**Files:**
- Create: `research/k-shaped-society/countries/US.md`
- Create: `research/k-shaped-society/countries/DE.md`
- Create: `research/k-shaped-society/countries/JP.md`
- Create: `research/k-shaped-society/countries/KR.md`
- Create: `research/k-shaped-society/countries/CN.md`

**Interfaces:**
- Consumes: source registry and evidence-claims registry.
- Produces: human-readable country synthesis with source IDs, counterevidence, PIT gaps, and divergence assessments.

- [ ] **Step 1: Use one mandatory dossier template for all five countries**

Each file must contain these headings exactly:

```markdown
# <COUNTRY>｜1990–2026 K-Shaped Research Dossier
## 1. Scope and data boundary
## 2. K01–K09 evidence map
## 3. D-A Index–Median Divergence
## 4. D-B GDP–Household Divergence
## 5. D-C Profit–Employment Divergence
## 6. Candidate regime episodes
## 7. Asset-transmission evidence
## 8. Counterevidence and hard negatives
## 9. PIT readiness by period
## 10. Comparability limits
## 11. Current scientific status
## 12. Source IDs
```

- [ ] **Step 2: Write US dossier**

Must cover frontier/superstar firms, profit/market concentration, wealth ownership, cap-weight/equal-weight evidence, household/labor counterpoints, and PIT reconstruction constraints for constituents/weights/accounting.

- [ ] **Step 3: Write DE dossier**

Must treat collective bargaining/predistribution as K09 slope compression evidence and separate German domestic K from DAX global/sector exposure. Germany large-index relative strength must remain a potential `HN7 SECTOR_ROTATION` confounder.

- [ ] **Step 4: Write JP dossier**

Must cover productivity-real-wage decoupling, large-vs-small firm profitability, employment/wage institutional features, 1990s aggregate-stagnation control, and TOPIX Large70 underperformance as D-A falsifier/counterevidence.

- [ ] **Step 5: Write KR dossier**

Must cover chaebol export/profit concentration, weak employment diffusion, SME employment/productivity structure, later SME catch-up as rediffusion evidence, and equity-index concentration without converting concentration into an absolute return rule.

- [ ] **Step 6: Write CN dossier**

Must distinguish official facts from Huachuang/Zhang Yu interpretation; cover industrial-profit dispersion, GDP/productivity vs median income/consumption, Gini counterevidence, new/old economy claims as research hypotheses unless independently reverified, and explicit current PIT gaps.

- [ ] **Step 7: Verify symmetrical disclosure**

Add a validator rule that every country file contains `Counterevidence`, `PIT readiness`, `Comparability limits`, and `Current scientific status` sections and references at least one registered source ID.

- [ ] **Step 8: Commit country dossiers**

```bash
git add research/k-shaped-society/countries scripts/validate_yks0_r0_research_estate.py tests/test_yks0_r0_research_estate.py
git commit -m "research: add five-country YKS0-R0 dossiers"
```

---

# Task 5: Build the 45-cell K matrix, hypotheses, PIT readiness, and 50 case candidates

**Files:**
- Create: `research/k-shaped-society/dimensions/k-dimension-evidence-matrix.json`
- Create: `research/k-shaped-society/hypotheses/hypothesis-registry.json`
- Create: `research/k-shaped-society/replay/pit-readiness-matrix.json`
- Create: `research/k-shaped-society/replay/case-candidate-registry.json`

**Interfaces:**
- Consumes: evidence registry + country dossiers.
- Produces: machine-readable 5×9 evidence matrix, H1–H8 registry, source/case PIT status, and exactly 50 candidate cases.

- [ ] **Step 1: Create exactly 45 country×dimension records**

Each matrix row must contain:

```json
{
  "country": "US",
  "dimension": "K02",
  "source_count": 0,
  "highest_evidence_grade": "UNKNOWN",
  "earliest_reliable_history": null,
  "latest_reliable_history": null,
  "pit_vintage_availability": "UNKNOWN",
  "comparability": "COUNTRY_NATIVE_ONLY",
  "direction_candidate": "UNKNOWN",
  "level_constructable": false,
  "delta_constructable": false,
  "delta2_constructable": false,
  "breadth_constructable": false,
  "dispersion_constructable": false,
  "support_source_ids": [],
  "counterevidence_source_ids": [],
  "unresolved_gaps": []
}
```

Populate only from registered evidence. Unknown is valid; invented completeness is not.

- [ ] **Step 2: Freeze H1–H8 machine registry**

Each hypothesis record must contain statement, null, expected direction, decisive dimensions, baselines, falsifier, desktop evidence state, contradictory source IDs, relevant countries, and `formal_replay_status="NOT_RUN"`.

H7/H8 must explicitly encode the R0 refinement: relative-return/breadth/concentration transmission is testable; absolute-index timing is not established.

- [ ] **Step 3: Build PIT-readiness matrix**

Track every registered source and every candidate case with the five-state PIT vocabulary. A source with no exact original vintage/availability proof must not be upgraded above `CURRENT_ONLY`, `BACKTEST_OR_RESTATED`, or `UNKNOWN` merely because its issuer is authoritative.

- [ ] **Step 4: Create exactly 50 candidate cases, 10 per country**

Use the G0 case IDs/windows/questions. Every case must include case ID, country, provisional T0, proposed visible cutoff, hidden horizon, divergence targets, dimensions, baselines, hard-negative class, PIT readiness, source IDs, leakage risks, and candidate status.

R0 may mark `PREREGISTRATION_READY` only when the case question/window/source plan is complete; it must never use `REPLAY_PASS`, `REPLAY_FAIL`, or `SETTLED`.

- [ ] **Step 5: Add negative tests**

Tests must mutate in-memory fixtures and prove validator rejection for: 44 or 46 matrix rows; sixth country; scalar `k_score`; `REPLAY_PASS`; missing PIT state; a source reference not in the registry; and `production_runtime_authorized=true`.

- [ ] **Step 6: Run focused tests**

```bash
python -m unittest tests.test_yks0_r0_research_estate -v
```
Expected: all implemented contract tests PASS once these files exist.

- [ ] **Step 7: Commit machine research objects**

```bash
git add research/k-shaped-society/dimensions research/k-shaped-society/hypotheses research/k-shaped-society/replay scripts/validate_yks0_r0_research_estate.py tests/test_yks0_r0_research_estate.py
git commit -m "research: compile YKS0-R0 matrix hypotheses and replay candidates"
```

---

# Task 6: Write the integrated research reports and desktop settlement

**Files:**
- Create: `research/k-shaped-society/reports/YKS0-R0-FIVE-COUNTRY-1990-2026-RESEARCH.md`
- Create: `research/k-shaped-society/reports/YKS0-R0-DIVERGENCE-ASSET-MAP.md`
- Create: `research/k-shaped-society/settlements/YKS0-R0-DESKTOP-SETTLEMENT.md`

**Interfaces:**
- Consumes: all evidence, countries, matrix, hypotheses, and case candidates.
- Produces: the durable human-readable full research corpus and bounded desktop settlement.

- [ ] **Step 1: Write full five-country report**

Required sections: Executive finding; Research question and non-claims; Five-country comparative map; Nine-dimensional K evidence; D-A; D-B; D-C; Country-by-country replay priors; Hard negatives and failed/simple explanations; PIT limitations and vintage gaps; What G2/G3 must prove; Source index.

The report may state `D-C > D-B > D-A` only as a desktop explanatory-prior ordering, not as a replay result.

- [ ] **Step 2: Write divergence-to-asset map**

For each divergence, show: K dimensions → economic mechanism → control point/value capture → ownership → earnings/cash-flow distribution → valuation/rates/liquidity gate → relative-return candidate → falsifier. Include examples and counterexamples from the five countries. Do not include allocation or trade instructions.

- [ ] **Step 3: Write desktop settlement with separate axes**

Required format:

```text
physical_evidence_state = <coverage statement>
scientific_state = STRONG_PRIOR / FORMAL_PIT_VALIDATION_REQUIRED
authority_state = RESEARCH_CANDIDATE_ONLY
runtime_state = NOT_STARTED
```

Then separately settle H1–H8. The document must explicitly say that no 50-case blind replay has yet occurred and that H7/H8 remain conditional.

- [ ] **Step 4: Add report-language guardrails to validator**

Reject exact or equivalent unconditional authority phrases such as `YKS0-R0 scientific PASS`, `formal replay passed`, `asset alpha proven`, `capital authorized`, or `execution authorized`.

- [ ] **Step 5: Commit reports and settlement**

```bash
git add research/k-shaped-society/reports research/k-shaped-society/settlements scripts/validate_yks0_r0_research_estate.py tests/test_yks0_r0_research_estate.py
git commit -m "research: publish YKS0-R0 five-country synthesis and desktop settlement"
```

---

# Task 7: Build one discovery root and integrate repository gates

**Files:**
- Create: `research/k-shaped-society/README.md`
- Create: `research/k-shaped-society/manifests/research-estate-manifest.json`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: one human discovery root, one machine discovery root, and CI enforcement.

- [ ] **Step 1: Write README as the human entry point**

README must show current status axes, explain Source Fact / Research Inference / Scientific Status, link every country/report/registry/matrix/replay/settlement artifact, and make the next boundary explicit: `G2 = vintage-safe Reality; G3 = blind replay`.

- [ ] **Step 2: Write deterministic research-estate manifest**

Use the exact minimum fields from the accepted spec, with authorization flags all false. Add only deterministic path/count/fingerprint metadata; no current timestamp is required.

- [ ] **Step 3: Add validator to contracts CI**

Insert in `.github/workflows/ci.yml` under `contracts` before the full unittest command:

```yaml
      - run: python scripts/validate_yks0_r0_research_estate.py
```

Do not add a new workflow unless existing `repository-gates` cannot express the check.

- [ ] **Step 4: Run complete local gate stack**

```bash
python scripts/validate_yks0_r0_research_estate.py
python scripts/validate_repository.py
python scripts/leak_guard.py
python scripts/check_governance.py
python scripts/verify_bootstrap_receipt.py
python scripts/build_manifest.py --check
python -m unittest discover -s tests -p 'test_*.py' -v
```
Expected: all PASS. `leak_guard.py` must remain green; do not add blocked binary research files such as PDF/XLSX/Parquet to the repository.

- [ ] **Step 5: Prove external production mutation count is zero**

Changed-file audit must show only the accepted spec metadata, this implementation plan, `research/k-shaped-society/**`, the R0 validator/test, and the one CI-line integration. No Soul/Supabase/HF/Notion/UIG/runtime/capital/execution path is permitted.

- [ ] **Step 6: Commit discovery and CI integration**

```bash
git add research/k-shaped-society/README.md research/k-shaped-society/manifests/research-estate-manifest.json .github/workflows/ci.yml
git commit -m "ci: gate YKS0-R0 research estate"
```

---

# Task 8: Independent review, exact-head PR qualification, and stop at merge gate

**Files:**
- No semantic changes after final review unless a defect is found.

**Interfaces:**
- Consumes: complete R0 candidate branch.
- Produces: review record, exact-head GitHub CI evidence, and a Human merge decision gate.

- [ ] **Step 1: Run task-scoped independent review**

Review separately for: source fidelity/citation laundering; PIT laundering; country-definition collapse; missing counterevidence; scalar-K resurrection; scientific-authority escalation; asset/action escalation; and manifest/path integrity. Any substantive finding returns to the owning task, then the full validator/gates rerun.

- [ ] **Step 2: Push candidate branch and open Draft PR**

PR title:
```text
YKS0-R0｜Five-Country 1990–2026 Research Estate × Evidence Pack
```
PR body must state: research-estate/evidence-hardening only; no formal PIT replay; no production external mutation; no capital/execution authority.

- [ ] **Step 3: Require exact-head `repository-gates`**

Required GitHub job identities:
```text
contracts = success
governance = success
```
Record exact head SHA and run ID in the PR conversation.

- [ ] **Step 4: Present R0 closure card**

Required axes:

```text
YKS0-R0 authority_state = HUMAN_ACCEPTED_SPEC / IMPLEMENTED_CANDIDATE
YKS0-R0 reality_state = DESKTOP_EVIDENCE_HARDENED
YKS0-R0 scientific_state = STRONG_PRIOR / FORMAL_PIT_VALIDATION_REQUIRED
YKS0-R0 runtime_state = NOT_STARTED
Production Supabase/HF/Notion/UIG mutations = 0
Capital/Execution = NOT_AUTHORIZED
```

- [ ] **Step 5: Stop for independent merge authorization**

Required token:
```text
AUTHORIZE_YKS0_R0_MERGE
```
Do not infer this from Written Spec acceptance or implementation authorization.

---

## Execution stop conditions

Stop immediately and surface a Human Gate if any of the following occurs:

- a source fact cannot be reproduced from the cited source;
- a material numerical claim has only a secondary or inaccessible source;
- historical `known_as_of` is guessed rather than established;
- a restated/backtested series is about to be labeled PIT-native;
- a country-native definition is about to be compared as a common level without crosswalk;
- any task proposes a scalar K score;
- any report turns K structure into a buy/sell/allocation instruction;
- any artifact claims replay/scientific PASS before G3;
- execution would mutate Soul ontology or production Supabase/HF/Notion/UIG/capital/execution assets;
- a required counterexample is being omitted because it weakens the thesis;
- protected main drift changes YIOS0/YKS0 authority semantics;
- exact-head repository gates are not green.

## Plan self-review

- Spec coverage: all accepted R0 sections map to Tasks 1–8.
- Scope: one bounded Research Estate; G1 Ontology and G2/G3 runtime/scientific work remain outside this plan.
- Placeholder scan: no implementation requirement depends on undefined `TBD/TODO` values; dynamic GitHub SHAs/run IDs are retrieved at execution time rather than hard-coded.
- Type consistency: country/dimension/PIT/case-status vocabularies match the accepted spec.
- Authority consistency: R0 never claims formal PIT replay, Capital Admission, or Execution Authority.

## Execution authorization

This plan exists because `ACCEPT_YKS0_R0_RESEARCH_ESTATE_WRITTEN_SPEC` authorized plan creation only. Implementation must not begin until the Human Principal chooses an execution mode and explicitly authorizes it.

Recommended token for Subagent-Driven execution:

```text
EXECUTE_YKS0_R0_RESEARCH_ESTATE_SUBAGENT_DRIVEN
```

Alternative Inline token:

```text
EXECUTE_YKS0_R0_RESEARCH_ESTATE_INLINE
```
