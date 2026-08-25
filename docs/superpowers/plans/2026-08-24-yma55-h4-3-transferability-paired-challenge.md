# YMA55-H4.3 Transferability & Prior-Violation Paired Challenge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a six-pair PIT-isolated H3 challenge that measures structural transferability gating and prior-violation detection separately from return forecasting.

**Architecture:** Reuse the accepted H3 `TransferabilityAssessment` and `PriorViolationRecord` primitives, add a deterministic non-scalar transferability resolver plus an experiment-only transported-diagnostic contract, and keep target structural evidence physically separate from forward target observations. Compare three same-pair variants: unconditional transport, transferability gate only, and full H3.

**Tech Stack:** Python 3.12 stdlib, `unittest`, JSON fixtures, existing `research_runtime.yma55`, GitHub Actions `repository-gates`.

**Spec:** `docs/architecture/yma55/YMA55-H4.3-TRANSFERABILITY-PRIOR-VIOLATION-PAIRED-CHALLENGE-v0.1.md`

## Global Constraints

- No new third-party runtime dependency.
- No scalar transferability score.
- `WEAK_TRANSFERABILITY`, `NON_TRANSFERABLE`, and `UNRESOLVED` cannot receive active prior authority.
- Transferability is frozen before any forward target observation is visible.
- Source hypothesis remains immutable; target diagnostics are separate transported contracts.
- No Historical Gold admission, Canon/Engine Registry mutation, Portfolio authority, sizing, signals, trading, live execution, or merge authority.
- Results are challenge-set counts only; no population probability or out-of-sample forecast claim.

---

### Task 1: Freeze H4.3 contract tests (RED)

**Files:**
- Create: `tests/test_yma55_h4_3_transfer_challenge.py`
- Existing contract source: `research_runtime/yma55/validation.py`

**Interfaces:**
- Consumes: `TransferabilityDimension`, `TransferabilityAssessment`, `evaluate_prior_violation`.
- Produces expectations for `resolve_transferability_state()`, `validate_transported_diagnostic()`, `run_transfer_variant()`, `run_h43_matrix()`.

- [ ] **Step 1: Write failing resolver tests**

```python
from research_runtime.yma55.transfer_challenge import resolve_transferability_state


def test_blocking_mismatch_forces_non_transferable():
    dims = [
        {"name": "policy_toolkit", "state": "MISMATCHED", "blocking_if_mismatched": True, "mechanism_relevance": "critical"},
        {"name": "monetary_regime", "state": "MATCHED", "blocking_if_mismatched": False, "mechanism_relevance": "critical"},
        {"name": "fiscal_capacity", "state": "MATCHED", "blocking_if_mismatched": False, "mechanism_relevance": "secondary"},
        {"name": "market_structure", "state": "PARTIAL", "blocking_if_mismatched": False, "mechanism_relevance": "material"},
        {"name": "global_order", "state": "PARTIAL", "blocking_if_mismatched": False, "mechanism_relevance": "secondary"},
    ]
    assert resolve_transferability_state(dims) == "NON_TRANSFERABLE"
```

- [ ] **Step 2: Add WEAK fail-closed test**

```python
def test_weak_transferability_cannot_receive_active_authority():
    result = run_transfer_variant(weak_packet(), observations={}, variant="T1_TRANSFERABILITY_GATE_ONLY")
    assert result["authority_settlement"] == "ACTIVE_PRIOR_BLOCKED"
    assert result["weak_prior_active_authority_leak"] is False
```

- [ ] **Step 3: Add firewall and mutation-negative tests**

Require rejection when a structural packet contains `forward_observation_stream`, `settlement`, role-bearing pair IDs, or a transported diagnostic with `frozen_at > observation_window_start`.

- [ ] **Step 4: Run RED**

Run: `python -m unittest tests.test_yma55_h4_3_transfer_challenge -v`  
Expected: FAIL with `ModuleNotFoundError: research_runtime.yma55.transfer_challenge`.

- [ ] **Step 5: Commit RED checkpoint**

```bash
git add tests/test_yma55_h4_3_transfer_challenge.py
git commit -m "test(yma55): freeze H4.3 paired challenge contract"
```

---

### Task 2: Implement transferability resolver and active-authority gate (GREEN)

**Files:**
- Create: `research_runtime/yma55/transfer_challenge.py`
- Modify: `research_runtime/yma55/prior_violation.py`
- Modify if exports are needed: `research_runtime/yma55/__init__.py`

**Interfaces:**
- Produces: `resolve_transferability_state(dimensions: Sequence[Mapping[str, Any]]) -> str`.
- Produces: `active_prior_allowed(overall_transferability: str) -> bool`.

- [ ] **Step 1: Implement deterministic resolver**

```python
def resolve_transferability_state(dimensions):
    if any(d["state"] == "MISMATCHED" and d.get("blocking_if_mismatched") for d in dimensions):
        return "NON_TRANSFERABLE"
    if any(d["state"] == "UNKNOWN" and d.get("mechanism_relevance") in {"critical", "material"} for d in dimensions):
        return "UNRESOLVED"
    material = [d for d in dimensions if d.get("mechanism_relevance") in {"critical", "material"}]
    mismatches = sum(d["state"] == "MISMATCHED" for d in material)
    partials = sum(d["state"] == "PARTIAL" for d in material)
    if mismatches >= 2 or partials >= 3:
        return "WEAK_TRANSFERABILITY"
    if mismatches or partials:
        return "PARTIAL_TRANSFERABILITY"
    return "HIGH_TRANSFERABILITY"
```

- [ ] **Step 2: Freeze active-authority mapping**

```python
def active_prior_allowed(state: str) -> bool:
    return state in {"HIGH_TRANSFERABILITY", "PARTIAL_TRANSFERABILITY"}
```

- [ ] **Step 3: Harden prior-violation evaluator**

Change `evaluate_prior_violation()` so `WEAK_TRANSFERABILITY` returns `NOT_EVALUABLE` with research response `RETIRE_CURRENT_PRIOR_APPLICATION` or a stress-reference-only note; it must never evaluate as an active prior.

- [ ] **Step 4: Run Task 1 tests**

Run: `python -m unittest tests.test_yma55_h4_3_transfer_challenge tests.test_yma55_prior_violation -v`  
Expected: PASS for resolver/WEAK behaviors implemented so far.

- [ ] **Step 5: Commit**

```bash
git add research_runtime/yma55/transfer_challenge.py research_runtime/yma55/prior_violation.py research_runtime/yma55/__init__.py tests/test_yma55_h4_3_transfer_challenge.py
git commit -m "feat(yma55): add H3 transferability authority gate"
```

---

### Task 3: Implement transported diagnostic contract and evidence firewall

**Files:**
- Modify: `research_runtime/yma55/transfer_challenge.py`
- Modify: `tests/test_yma55_h4_3_transfer_challenge.py`

**Interfaces:**
- Produces: `validate_transported_diagnostic(packet: Mapping[str, Any]) -> None`.
- Produces: `build_hypothesis_set_from_transport(packet: Mapping[str, Any]) -> MechanismHypothesisSet`.

- [ ] **Step 1: Write RED tests for immutable source lineage**

```python
def test_transport_contract_is_separate_from_source_hypothesis():
    packet = valid_structural_packet()
    validate_transported_diagnostic(packet)
    assert packet["transported_diagnostic"]["transport_id"] != packet["transported_diagnostic"]["source_prior_ref"]
```

Also reject source-role-bearing IDs, missing `pit_frozen`, missing observation window, and forward evidence fields in structural packets.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_yma55_h4_3_transfer_challenge -v`  
Expected: FAIL on missing validation/build functions.

- [ ] **Step 3: Implement minimal validator/compiler**

The compiler creates a temporary PRIMARY diagnostic hypothesis using only the pre-frozen target-native diagnostic fields. It does not mutate or load the historical source hypothesis at evaluation time.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest tests.test_yma55_h4_3_transfer_challenge tests.test_yma55_prior_violation -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add research_runtime/yma55/transfer_challenge.py tests/test_yma55_h4_3_transfer_challenge.py
git commit -m "feat(yma55): freeze transported diagnostic firewall"
```

---

### Task 4: Build six opaque paired fixtures

**Files:**
- Create: `fixtures/replay/yma55_h4_3/blind_manifest.json`
- Create: `fixtures/replay/yma55_h4_3/structural/TP-01.json` through `TP-06.json`
- Create: `fixtures/replay/yma55_h4_3/observations/TP-01.json` through `TP-06.json`
- Create: `fixtures/replay/yma55_h4_3/sealed_mapping.json`
- Create: `fixtures/replay/yma55_h4_3/post_resolution_settlement.json`
- Modify: `tests/test_yma55_h4_3_transfer_challenge.py`

**Interfaces:**
- Structural packet contains opaque prior/target refs, five dimension states/evidence refs, and transported diagnostics only.
- Observation packet contains only opaque pair ID, target observation timestamps/signals, window state.
- Sealed mapping is the only artifact with actual source/target episode IDs and challenge roles.

- [ ] **Step 1: Add fixture-integrity RED tests**

Require exactly six unique pair IDs, one-to-one structural/observation files, five dimensions per structural packet, no `settlement`/actual episode ID in blind artifacts, and no forward signals in structural packets.

- [ ] **Step 2: Create pair fixtures from frozen H4.1 evidence**

Reuse target-world signals from the corresponding H4.1 blind/hydration packets; do not invent post-window target outcomes.

- [ ] **Step 3: Freeze pair-specific target diagnostics before observation files are consumed**

TP-01 must test compatible credit-backstop transfer; TP-02 and TP-04 must remain active but contain a target violation; TP-03 and TP-05 must contain blocking mismatches; TP-06 must resolve WEAK and remain stress-reference only.

- [ ] **Step 4: Run fixture tests**

Run: `python -m unittest tests.test_yma55_h4_3_transfer_challenge -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fixtures/replay/yma55_h4_3 tests/test_yma55_h4_3_transfer_challenge.py
git commit -m "data(yma55): add H4.3 opaque paired challenge fixtures"
```

---

### Task 5: Implement T0/T1/T2 same-pair runner and settlement scoring

**Files:**
- Modify: `research_runtime/yma55/transfer_challenge.py`
- Modify: `tests/test_yma55_h4_3_transfer_challenge.py`

**Interfaces:**
- Produces: `TRANSFER_VARIANTS = ("T0_UNCONDITIONAL_TRANSPORT", "T1_TRANSFERABILITY_GATE_ONLY", "T2_H3_FULL")`.
- Produces: `run_transfer_variant(structural_packet, observations, variant) -> dict[str, Any]`.
- Produces: `run_h43_matrix(structural_packets, observations, settlements) -> dict[str, Any]`.

- [ ] **Step 1: Write RED tests for variant semantics**

T0 always applies an eligible source prior and can expose `unsafe_prior_application=true`; T1 blocks WEAK/NON/UNRESOLVED but never sees forward violations; T2 blocks structurally invalid priors and runs `evaluate_prior_violation()` only for HIGH/PARTIAL.

- [ ] **Step 2: Add non-scalar scoring tests**

Require direct counts for `unsafe_prior_applications`, `correct_structural_blocks`, `eligible_prior_violations_detected`, `eligible_prior_violations_missed`, `false_breakers`, `weak_prior_active_authority_leaks`, `source_prior_laundering_events`, and `capital_authority_events`. Forbid `win_rate`, `probability`, `position_size`, `trade_action`.

- [ ] **Step 3: Run RED**

Run: `python -m unittest tests.test_yma55_h4_3_transfer_challenge -v`  
Expected: FAIL on missing runner/matrix functions.

- [ ] **Step 4: Implement minimal runner and matrix**

Use structural packets first, freeze authority settlement, then consume observation packets only for T2 active priors. Compare to post-resolution settlement only after machine outputs are built.

- [ ] **Step 5: Run GREEN**

Run: `python -m unittest tests.test_yma55_h4_3_transfer_challenge tests.test_yma55_prior_violation -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add research_runtime/yma55/transfer_challenge.py tests/test_yma55_h4_3_transfer_challenge.py
git commit -m "feat(yma55): run H4.3 transferability ablation matrix"
```

---

### Task 6: Add dedicated H4.3 validator and CI gate

**Files:**
- Create: `scripts/validate_yma55_h4_3_transfer_challenge.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Validator reconstructs the full matrix from committed fixtures and fails closed on any authority leak, blindness leak, pair-count drift, or result/document drift.

- [ ] **Step 1: Create validator**

Validator must print each T0/T1/T2 count vector and explicit lines:

```text
historical_gold_admission=0
capital_authority=0
out_of_sample_claim=NOT_ESTABLISHED
exact_old_yma55_replication=NOT_CLAIMED
```

- [ ] **Step 2: Wire CI before full unittest discovery**

Add:

```yaml
- run: python scripts/validate_yma55_h4_3_transfer_challenge.py
```

immediately after H4.2 validator.

- [ ] **Step 3: Run/observe GitHub Actions**

Expected: governance PASS, contracts PASS, H4/H4.1/H4.2 PASS, H4.3 dedicated validator PASS, full unit suite PASS.

- [ ] **Step 4: Commit**

```bash
git add scripts/validate_yma55_h4_3_transfer_challenge.py .github/workflows/ci.yml
git commit -m "ci(yma55): gate H4.3 paired transfer challenge"
```

---

### Task 7: Freeze machine settlement, Human Review Card, and exact-head verification

**Files:**
- Create: `docs/architecture/yma55/YMA55-H4.3-STATE.json`
- Create: `docs/architecture/yma55/YMA55-H4.3-PAIRED-CHALLENGE-REPORT-v0.1.md`
- Create: `docs/architecture/yma55/YMA55-H4.3-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- State records machine outputs exactly; report may interpret only what the matrix supports; review card requires 24/24 PASS.

- [ ] **Step 1: Generate settlement from machine matrix, not prose-first reasoning**

Do not write any superiority claim until the dedicated validator has printed the committed matrix results.

- [ ] **Step 2: Write State and Report with explicit unresolved boundaries**

Preserve whether each measured contribution is supported, partially identified, not established, or unresolved.

- [ ] **Step 3: Write 24/24 Human Review Card**

Acceptance token:

`ACCEPT_YMA55_H4_3_TRANSFERABILITY_PRIOR_VIOLATION_PAIRED_CHALLENGE`

- [ ] **Step 4: Run final exact-head repository-gates**

No branch mutation after the final exact-head check. The qualifying run must reference the exact final PR head.

- [ ] **Step 5: Stop**

Final machine state may be `machine_qualified_paired_transfer_challenge_candidate`; PR remains Draft/unmerged and no successor is authorized.
