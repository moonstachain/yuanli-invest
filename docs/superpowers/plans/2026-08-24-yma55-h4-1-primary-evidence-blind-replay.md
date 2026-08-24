# YMA55-H4.1 Primary Evidence Hydration & Blind Replay Qualification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hydrate the 12 H4 replay candidates with point-in-time evidence, construct outcome-blind replay packets, run a transparent deterministic mechanism resolver, and produce qualification proposals without granting Historical Gold or capital authority.

**Architecture:** Preserve H4 fixtures as immutable candidate definitions. Add a separate H4.1 evidence layer, opaque blind-manifest / sealed-mapping split, deterministic resolver and post-reveal qualification layer. Every stage is fail-closed on publication lag, evidence tier, fake independence, role leakage, settlement leakage and prohibited capital outputs.

**Tech Stack:** Python 3.12 stdlib, `unittest`, JSON fixtures, GitHub Actions `repository-gates`.

**Spec:** `docs/architecture/yma55/YMA55-H4.1-PRIMARY-EVIDENCE-HYDRATION-BLIND-REPLAY-QUALIFICATION-v0.1.md`

## Global Constraints

- Preserve H4's 12 source fixtures; hydration is a separate evidence layer.
- Resolver evidence is E0/E1/admissible E2 only; E3/E4 are excluded from blind input.
- `published_at > evidence_cutoff` or `public_at_t0=false` fails closed.
- Every fully hydrated case requires at least one E0 and one genuinely independent E1 source unless explicitly degraded.
- Blind packets expose no `case_type`, settlement, outcome, role-bearing path or role-bearing episode id.
- This session may claim at most `B_PIPELINE_BLIND`, never A-grade independent blind replication.
- Blind resolution must be frozen before sealed mapping / settlement reveal.
- Historical Gold admission count remains 0.
- No Canon, Engine Registry, Portfolio, sizing, buy/sell/hold, trading, execution or merge authority.
- `Research PASS != Capital PASS`.

---

### Task 1: Evidence Admission Contract

**Files:**
- Create: `research_runtime/yma55/evidence.py`
- Create: `tests/test_yma55_h4_1_evidence.py`

**Interfaces:**
- Consumes: H4 case `evidence_cutoff`; JSON source records.
- Produces: `validate_evidence_source(source, cutoff)`, `admit_evidence(sources, cutoff)`, `assess_hydration(sources)`.

- [ ] **Step 1: Write failing tests**

```python
from research_runtime.yma55.evidence import admit_evidence, assess_hydration


def test_post_cutoff_primary_is_rejected():
    source = {
        "source_id": "S1", "evidence_tier": "E0", "publisher": "Federal Reserve",
        "producer_class": "central_bank", "originating_source_id": "S1",
        "published_at": "1994-02-04T00:00:00Z", "public_at_t0": True,
        "claims": [], "signals": []
    }
    admitted, rejected = admit_evidence([source], "1994-01-01T23:59:59Z")
    assert admitted == []
    assert rejected[0]["reason"] == "POST_CUTOFF"


def test_fake_e1_independence_does_not_fully_hydrate():
    sources = [
        {"source_id":"E0","evidence_tier":"E0","producer_class":"central_bank","originating_source_id":"ORIGIN"},
        {"source_id":"E1","evidence_tier":"E1","producer_class":"news_republication","originating_source_id":"ORIGIN"},
    ]
    assert assess_hydration(sources)["status"] != "EVIDENCE_HYDRATED"
```

- [ ] **Step 2: Run RED verification**

Run: `python -m unittest tests.test_yma55_h4_1_evidence -v`
Expected: FAIL because `research_runtime.yma55.evidence` does not exist.

- [ ] **Step 3: Implement minimal fail-closed evidence admission**

Implement allowed tiers `E0..E4`, timestamp comparison, `public_at_t0`, E3/E4 resolver exclusion, producer/origin independence and hydration states.

- [ ] **Step 4: Run GREEN verification**

Run: `python -m unittest tests.test_yma55_h4_1_evidence -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add research_runtime/yma55/evidence.py tests/test_yma55_h4_1_evidence.py
git commit -m "feat(yma55): add PIT evidence admission contract"
```

---

### Task 2: Blind Packet Firewall

**Files:**
- Create: `research_runtime/yma55/blind.py`
- Create: `tests/test_yma55_h4_1_blind.py`

**Interfaces:**
- Consumes: H4 case T0 object, opaque case id, admitted evidence signals.
- Produces: `build_blind_packet(blind_case_id, case, evidence_packet)` and `validate_blind_packet(packet)`.

- [ ] **Step 1: Write failing tests**

```python
from research_runtime.yma55.blind import build_blind_packet, validate_blind_packet


def test_blind_packet_removes_role_and_settlement(h4_case, evidence_packet):
    packet = build_blind_packet("H41-B01", h4_case, evidence_packet)
    text = repr(packet)
    assert "case_type" not in packet
    assert "settlement" not in packet
    assert h4_case["episode_id"] not in text
    assert "GOLD" not in text and "NEAR" not in text and "WRONG_STRIKE" not in text
    validate_blind_packet(packet)


def test_role_bearing_id_is_rejected():
    bad = {"blind_case_id": "H4-GOLD-1982", "t0": {}, "evidence": []}
    try:
        validate_blind_packet(bad)
    except ValueError as exc:
        assert "role" in str(exc).lower()
    else:
        raise AssertionError("expected role-leak rejection")
```

- [ ] **Step 2: Run RED verification**

Run: `python -m unittest tests.test_yma55_h4_1_blind -v`
Expected: FAIL because blind module is absent.

- [ ] **Step 3: Implement sanitizer and recursive prohibited-key scan**

Blind packet contains only opaque id, mechanism family, as-of/cutoff, frozen T0 world/constraint/transmission/hypothesis set/transferability template and admitted evidence signals. Strip original episode id and H4 case role.

- [ ] **Step 4: Run GREEN verification**

Run: `python -m unittest tests.test_yma55_h4_1_blind -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add research_runtime/yma55/blind.py tests/test_yma55_h4_1_blind.py
git commit -m "feat(yma55): add blind replay firewall"
```

---

### Task 3: Transparent Mechanism Resolver

**Files:**
- Modify: `research_runtime/yma55/blind.py`
- Modify: `tests/test_yma55_h4_1_blind.py`

**Interfaces:**
- Produces: `resolve_blind_packet(packet) -> dict` with hypothesis scores and one resolution state.

- [ ] **Step 1: Add failing tests for alternative win, breaker and unresolved**

```python
def test_breaker_prevents_primary_win(primary_breaker_packet):
    result = resolve_blind_packet(primary_breaker_packet)
    assert result["resolution"] != "PRIMARY_LEADS"


def test_insufficient_decisive_evidence_stays_unresolved(sparse_packet):
    result = resolve_blind_packet(sparse_packet)
    assert result["resolution"] == "INSUFFICIENT_EVIDENCE"
```

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_yma55_h4_1_blind -v`
Expected: FAIL on missing resolver behavior.

- [ ] **Step 3: Implement deterministic signal comparison**

For each hypothesis compare normalized evidence signals with `predicted_observables`, detect explicit contradiction/falsifier/breaker signals, compute coverage, and preserve unresolved under ties/low coverage. Do not compute alpha or price target.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest tests.test_yma55_h4_1_blind -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add research_runtime/yma55/blind.py tests/test_yma55_h4_1_blind.py
git commit -m "feat(yma55): add transparent blind mechanism resolver"
```

---

### Task 4: Evidence Source Registry & 12 Hydration Packets

**Files:**
- Create: `fixtures/replay/yma55_h4_1/sources.json`
- Create: `fixtures/replay/yma55_h4_1/hydration/*.json`
- Create: `fixtures/replay/yma55_h4_1/blind_manifest.json`
- Create: `fixtures/replay/yma55_h4_1/sealed_mapping.json`
- Create: `tests/test_yma55_h4_1_fixtures.py`

**Interfaces:**
- Consumes: official/contemporaneous research sources and H4 fixture cutoffs.
- Produces: 12 evidence packets with source refs and normalized observable signals.

- [ ] **Step 1: Write failing fixture-integrity tests**

Tests require exactly 12 opaque cases, one-to-one sealed mapping, no role labels in blind manifest, source refs resolve, no admitted source after cutoff, no E3/E4 in resolver evidence, and H4 source fixtures remain `gold_qualified=false`.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_yma55_h4_1_fixtures -v`
Expected: FAIL because H4.1 fixture pack is absent.

- [ ] **Step 3: Build source registry**

Use official primary / contemporaneous sources where available; explicitly encode post-cutoff official records as rejected controls where useful. Store only paraphrased claims and normalized signals, not long copyrighted passages.

- [ ] **Step 4: Build 12 hydration packets and blind/sealed manifests**

Each hydration packet records admitted/rejected source ids, hydration status, decisive discriminators and `blindness_grade = B_PIPELINE_BLIND`.

- [ ] **Step 5: Verify GREEN**

Run: `python -m unittest tests.test_yma55_h4_1_fixtures -v`
Expected: PASS or explicit degraded-case expectations where independent T0 evidence is not available.

- [ ] **Step 6: Commit**

```bash
git add fixtures/replay/yma55_h4_1 tests/test_yma55_h4_1_fixtures.py
git commit -m "data(yma55): hydrate H4.1 PIT evidence pack"
```

---

### Task 5: Frozen Blind Results & Post-Reveal Qualification

**Files:**
- Create: `research_runtime/yma55/qualification.py`
- Create: `fixtures/replay/yma55_h4_1/blind_results.json`
- Create: `fixtures/replay/yma55_h4_1/qualification_results.json`
- Create: `tests/test_yma55_h4_1_qualification.py`

**Interfaces:**
- Consumes: frozen blind results + sealed mapping + H4 settlements.
- Produces: replay qualification proposals only.

- [ ] **Step 1: Write failing tests**

```python
from research_runtime.yma55.qualification import qualify_after_reveal


def test_qualification_never_grants_gold_or_capital(sample_blind_result, sample_reveal):
    result = qualify_after_reveal(sample_blind_result, sample_reveal)
    assert result["historical_gold_admitted"] is False
    assert result["capital_authority"] is False


def test_b_grade_cannot_claim_independent_blind(sample_blind_result, sample_reveal):
    sample_blind_result["blindness_grade"] = "B_PIPELINE_BLIND"
    result = qualify_after_reveal(sample_blind_result, sample_reveal)
    assert result["independent_blind_replication"] is False
```

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_yma55_h4_1_qualification -v`
Expected: FAIL because qualification module is absent.

- [ ] **Step 3: Implement reveal comparator**

Map resolver state and H4 settlement to proposal classes without changing original settlement or admitting Gold. Preserve ambiguity and insufficient evidence.

- [ ] **Step 4: Freeze blind results before reveal**

Generate `blind_results.json` from only `blind_manifest.json` + hydration packets; record content hashes. Only then generate post-reveal `qualification_results.json` using sealed mapping.

- [ ] **Step 5: Verify GREEN**

Run: `python -m unittest tests.test_yma55_h4_1_qualification -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add research_runtime/yma55/qualification.py fixtures/replay/yma55_h4_1/blind_results.json fixtures/replay/yma55_h4_1/qualification_results.json tests/test_yma55_h4_1_qualification.py
git commit -m "feat(yma55): freeze blind replay qualification results"
```

---

### Task 6: Dedicated Validator, CI Gate & Human Review

**Files:**
- Create: `scripts/validate_yma55_h4_1.py`
- Create: `tests/test_yma55_h4_1_validator.py`
- Modify: `.github/workflows/ci.yml`
- Create: `docs/architecture/yma55/YMA55-H4.1-BLIND-REPLAY-REPORT-v0.1.md`
- Create: `docs/architecture/yma55/YMA55-H4.1-STATE.json`
- Create: `docs/architecture/yma55/YMA55-H4.1-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Validator returns exit 0 only when all H4.1 authority, PIT, evidence, blindness and fixture invariants hold.

- [ ] **Step 1: Write validator negative tests first**

Negative fixtures must prove rejection of post-cutoff evidence, E4 resolver input, role leakage, settlement leakage, fake E1 independence, forced winner under insufficient evidence, Gold admission and capital output fields.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_yma55_h4_1_validator -v`
Expected: FAIL because validator is absent.

- [ ] **Step 3: Implement validator and add dedicated CI step**

Add `python scripts/validate_yma55_h4_1.py` after the H4 validator and before full unittest discovery.

- [ ] **Step 4: Run exact-head qualification**

Run through GitHub Actions and require:

- governance SUCCESS;
- contracts SUCCESS;
- H4 validator SUCCESS;
- H4.1 validator SUCCESS;
- full unittest discovery SUCCESS.

- [ ] **Step 5: Write report/state/review card from verified outputs**

State must distinguish evidence-hydrated count, partial/insufficient count, blind resolution distribution, B-grade limitation, qualification proposal counts and historical Gold admissions = 0.

- [ ] **Step 6: Final exact-head requalification**

After state/report/review artifacts are committed, require another exact-head `repository-gates` SUCCESS before claiming machine qualification.

- [ ] **Step 7: Stop at Human Review**

Do not merge. Do not admit Historical Gold. Present the H4.1 Human Review token only if the final review card threshold is machine-supported.
