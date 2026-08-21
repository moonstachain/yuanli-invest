# YIP0 Investment Philosophy Canon Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the approved Yuanli Investment Philosophy into a governed, machine-checkable candidate Canon layer without changing accepted P/N/X/E/V/S semantics or the active QXM2 program gate.

**Architecture:** Add YIP0 as an upstream philosophy authority candidate in `docs/architecture/yip0/`, backed by a stable 12-axiom JSON contract, stage state, Human Review card and fail-closed validator. The validator is added to the existing `repository-gates` contracts job and explicitly checks that YIP0 cannot mutate the accepted OS or acquire trading authority.

**Tech Stack:** Markdown, JSON, Python 3.12, GitHub Actions, unittest-compatible repository validation.

**Spec:** `docs/superpowers/specs/2026-08-21-yip0-investment-philosophy-canon-design.md`

## Global Constraints

- Preserve `one_core_three_worlds_three_gates_one_loop`.
- Preserve `P Reality / N Belief / X Asymmetry` and `P != N`.
- Preserve canonical `X := (Xs, Xa, Xp)` exactly.
- Preserve E as horizontal evidence control.
- Preserve V as Price-Implied Expectations; no target-price ontology.
- Preserve S as Portfolio Survival; no automatic recommended sizing.
- No scalar PNX / Force / philosophy score.
- No target price, recommended weight, position size, buy/sell or live execution.
- YIP0 must not overwrite the repository-wide active QXM2 gate.
- Human Acceptance token: `ACCEPT_YIP0_INVESTMENT_PHILOSOPHY_CANON`.
- Merge authorization token: `AUTHORIZE_YIP0_MERGE`.

---

### Task 1: Philosophy Canon artifacts

**Files:**
- Create: `docs/architecture/yip0/YIP0-INVESTMENT-PHILOSOPHY-CANON-v0.1.md`
- Create: `docs/architecture/yip0/YIP0-PHILOSOPHY-CONTRACT-v0.1.json`

**Interfaces:**
- Consumes: accepted OS semantics in `docs/os-vnext/CONSTITUTION.md`
- Produces: stable axiom IDs `YL-PH-01` through `YL-PH-12` and machine-readable mappings used by the validator

- [ ] **Step 1: Write Canon prose with exact 12 axiom IDs**

The prose must contain the approved identity `Fallibilist Reflexive Evolutionary Realism`, the Chinese identity `可错的反身演化实在论`, the six compression words `实在 · 可错 · 反身 · 演化 · 凸性 · 生存`, the four mother laws, the 12 axioms, intellectual-lineage boundary, OS mapping, forbidden interpretations and governance boundary.

- [ ] **Step 2: Write JSON contract**

Required top-level shape:

```json
{
  "schema_version": "0.1.0",
  "stage": "YIP0_INVESTMENT_PHILOSOPHY_CANON",
  "status": "candidate_philosophy_authority",
  "identity": {},
  "mother_proposition": "...",
  "compression": [],
  "mother_laws": [],
  "axioms": [],
  "os_mapping": {},
  "lineage_boundary": {},
  "forbidden_interpretations": [],
  "governance": {}
}
```

The `axioms` array must contain exactly 12 unique IDs from `YL-PH-01` to `YL-PH-12`.

- [ ] **Step 3: Self-check semantic non-regression**

Verify contract strings preserve:

```text
one_core_three_worlds_three_gates_one_loop
X := (Xs, Xa, Xp)
Claim Authority <= Evidence Authority
Price-Implied Expectations
Portfolio Survival
```

- [ ] **Step 4: Commit Task 1**

Commit message:

```text
feat: add YIP0 philosophy canon contract
```

---

### Task 2: Stage state and Human Review gate

**Files:**
- Create: `docs/architecture/yip0/YIP0-STATE.json`
- Create: `docs/architecture/yip0/YIP0-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Consumes: YIP0 contract from Task 1
- Produces: candidate-stage governance state and review criteria consumed by the validator

- [ ] **Step 1: Create candidate state**

State must use:

```json
{
  "stage": "YIP0_INVESTMENT_PHILOSOPHY_CANON",
  "status": "candidate_started",
  "repository_base_sha": "43911282d5ff80a2795d1b02afcf7ef40bc513a3",
  "human_gate": {
    "token": "ACCEPT_YIP0_INVESTMENT_PHILOSOPHY_CANON",
    "decision": "pending",
    "acceptance_does_not_imply_merge": true
  },
  "merge_authority": "AUTHORIZE_YIP0_MERGE",
  "global_gate_behavior": "parallel_candidate_does_not_override_repository_next_gate",
  "next_gate": "YIP0_MACHINE_QUALIFICATION"
}
```

- [ ] **Step 2: Create 12-dimension Human Review card**

The card must require PASS/FAIL for: philosophical coherence; accepted-OS compatibility; reality/belief separation; reflexivity; non-equilibrium; tail/convexity; price; survival; evidence/falsification; lineage authority; scalar-score prohibition; trading-authority prohibition.

- [ ] **Step 3: Commit Task 2**

Commit message:

```text
docs: add YIP0 state and human review gate
```

---

### Task 3: Fail-closed validator

**Files:**
- Create: `scripts/validate_yip0_philosophy.py`
- Create: `tests/test_yip0_philosophy.py`

**Interfaces:**
- Consumes: YIP0 Canon, contract, state, review card and current OS Constitution
- Produces: process exit 0 only when all YIP0 semantic and governance invariants pass

- [ ] **Step 1: Write failing unit test**

Test should import `scripts.validate_yip0_philosophy` and assert `main()` completes without raising on repository fixtures.

```python
import unittest
from scripts import validate_yip0_philosophy


class YIP0PhilosophyTests(unittest.TestCase):
    def test_repository_yip0_contract_passes(self):
        validate_yip0_philosophy.main()


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test before validator exists**

Run:

```bash
python -m unittest tests.test_yip0_philosophy -v
```

Expected: import failure because `validate_yip0_philosophy.py` does not exist.

- [ ] **Step 3: Implement validator**

Validator must assert:

```python
EXPECTED_AXIOMS = [f"YL-PH-{i:02d}" for i in range(1, 13)]
```

and must check:

- exact 12 unique axiom IDs;
- exactly four mother laws: `REALITY_OVER_BELIEF`, `REFLEXIVITY`, `TAIL_ASYMMETRY`, `SURVIVAL_FIRST`;
- `P != N` encoded in contract;
- `X := (Xs, Xa, Xp)` encoded in contract and existing Constitution;
- E horizontal law and `Claim Authority <= Evidence Authority`;
- V preserves `Price-Implied Expectations` and rejects target price;
- S preserves `Portfolio Survival` and rejects recommended position size;
- no numeric scalar master score patterns;
- no buy/sell or live-execution authorization;
- state Human Gate token and pending decision;
- state declares parallel candidate behavior;
- Human Review card contains D1 through D12.

- [ ] **Step 4: Run focused test and validator**

Run:

```bash
python -m unittest tests.test_yip0_philosophy -v
python scripts/validate_yip0_philosophy.py
```

Expected: PASS / exit 0.

- [ ] **Step 5: Commit Task 3**

Commit message:

```text
test: validate YIP0 philosophy invariants
```

---

### Task 4: CI integration

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: `scripts/validate_yip0_philosophy.py`
- Produces: YIP0 validation inside the `contracts` repository gate

- [ ] **Step 1: Add YIP0 validator after QXM1 validation**

Required workflow line:

```yaml
      - run: python scripts/validate_yip0_philosophy.py
```

- [ ] **Step 2: Run repository validation locally where available**

Run:

```bash
python scripts/validate_yip0_philosophy.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS.

- [ ] **Step 3: Commit Task 4**

Commit message:

```text
ci: add YIP0 philosophy gate
```

---

### Task 5: PR and exact-head qualification

**Files:**
- Modify after CI only if machine qualification needs to be recorded: `docs/architecture/yip0/YIP0-STATE.json`

**Interfaces:**
- Consumes: GitHub Actions `repository-gates`
- Produces: Draft PR at `candidate_ready_for_human_review` only after exact-head success

- [ ] **Step 1: Open Draft PR**

Title:

```text
YIP0: establish Yuanli Investment Philosophy Canon
```

PR body must state that YIP0 is philosophy authority only, does not change QXM2 gate priority, and does not authorize capability promotion or trading.

- [ ] **Step 2: Read exact-head workflow result**

Require both jobs:

```text
contracts = success
governance = success
```

and require YIP0 validator to have run in the contracts job.

- [ ] **Step 3: Advance state only after successful exact-head CI**

Update:

```json
"status": "candidate_ready_for_human_review",
"next_gate": "YIP0_HUMAN_REVIEW"
```

and record the exact head SHA, workflow run number/id and conclusions.

- [ ] **Step 4: Re-run exact-head CI after state recording**

The state-recording commit changes head SHA, so require a second green exact-head run.

- [ ] **Step 5: Stop at Human Gate**

Present only:

```text
ACCEPT_YIP0_INVESTMENT_PHILOSOPHY_CANON
```

as the next owner decision. Do not merge without later `AUTHORIZE_YIP0_MERGE`.
