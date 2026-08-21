# ME1 | State Object Model Reframe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the accepted ME1 design into a machine-checkable multi-thesis state-model candidate centered on `ResearchTarget v2 -> EngineThesis -> PositionPassport -> BookState@PIT`, while preserving ResearchTarget v1 and ResearchStateVector as immutable historical/compatibility identities.

**Architecture:** ME1 introduces six focused vnext schemas plus a fail-closed relational validator and candidate lifecycle artifacts under `docs/architecture/me1/`. Historical `research-target.schema.json` v1 and `research-state-vector.schema.json` are never redefined in place. Local JSON Schema validation handles single-object shape; `scripts/validate_me1_state_object_model.py` handles cross-object identity, cardinality, lifecycle, PIT, compatibility, and authority invariants.

**Tech Stack:** JSON Schema Draft 2020-12, Python 3.12, `jsonschema`, stdlib `json/pathlib/datetime`, `unittest`, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-22-me1-state-object-model-reframe-design.md`

## Global Constraints

- Preserve `ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE` as upstream authority.
- Preserve historical `packages/contracts/schemas/vnext/research-target.schema.json` with `$id = urn:yuanli-invest:schema:vnext-research-target:1.0.0` and existing meaning.
- Preserve historical `packages/contracts/schemas/vnext/research-state-vector.schema.json` identity and meaning.
- Add `ResearchTarget v2.0.0` as explicit semantic successor; never mutate v1 in place.
- `ResearchTarget != EngineThesis != PositionPassport != BookState`.
- `ResearchTarget v2 : EngineThesis = 1 : 0..N`.
- `EngineThesis : PositionPassport = 1 : 0..N`.
- A PositionPassport may occupy at most one primary Book per `portfolio_namespace + as_of`.
- C/R/X are Genesis Engines; engine namespace remains open-world but resolution is fail-closed.
- `primary_engine` is immutable inside one qualified Thesis identity.
- `Revision != Thesis Migration`.
- `Settlement evaluates history; it never rewrites history.`
- `Book membership belongs to PositionPassport, never directly to ticker or ResearchTarget.`
- `BOOK-CASH` is a liquidity-reserve role and must never create `ENG-CASH`.
- Legacy RSV preserves historical authority but has zero future canonical write authority.
- Legacy compatibility is one-way/read-only and cannot automatically create EngineThesis.
- PIT evidence distinguishes `recorded_at`, `known_as_of`, `knowledge_cutoff`, and replay cutoff.
- ME1 grants no portfolio weights, sizing, buy/sell/hold, trading, execution, Registry promotion, Constitution mutation, or ME2–ME5 authority.
- Final Human Review requires 13/13 PASS.
- Do not merge the ME1 PR without a later explicit merge authorization token.

---

## File Structure

### Candidate authority and governance
- Create: `docs/architecture/me1/ME1-STATE-OBJECT-MODEL-AUTHORITY-v0.1.md`
- Create: `docs/architecture/me1/ME1-SEMANTIC-SUCCESSOR-MAP-v0.1.json`
- Create: `docs/architecture/me1/ME1-STATE.json`
- Create: `docs/architecture/me1/ME1-HUMAN-REVIEW-CARD-v0.1.md`

### New schemas
- Create: `packages/contracts/schemas/vnext/research-target-v2.schema.json`
- Create: `packages/contracts/schemas/vnext/engine-thesis.schema.json`
- Create: `packages/contracts/schemas/vnext/position-passport.schema.json`
- Create: `packages/contracts/schemas/vnext/book-state.schema.json`
- Create: `packages/contracts/schemas/vnext/legacy-rsv-projection.schema.json`
- Create: `packages/contracts/schemas/vnext/legacy-rsv-read-model.schema.json`

### Candidate fixtures / shadow bundle
- Create: `docs/architecture/me1/fixtures/research-targets-v2.json`
- Create: `docs/architecture/me1/fixtures/engine-theses.json`
- Create: `docs/architecture/me1/fixtures/position-passports.json`
- Create: `docs/architecture/me1/fixtures/book-states.json`
- Create: `docs/architecture/me1/fixtures/legacy-rsv-projections.json`

### Validation
- Create: `scripts/validate_me1_state_object_model.py`
- Create: `tests/test_me1_state_object_model.py`
- Modify: `.github/workflows/ci.yml`

---

### Task 1: Freeze ME1 candidate authority and historical semantic successors

**Files:**
- Create: `docs/architecture/me1/ME1-STATE-OBJECT-MODEL-AUTHORITY-v0.1.md`
- Create: `docs/architecture/me1/ME1-SEMANTIC-SUCCESSOR-MAP-v0.1.json`
- Create: `docs/architecture/me1/ME1-STATE.json`
- Create: `docs/architecture/me1/ME1-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Consumes: accepted ME1 Design Spec and ME0 authority contract.
- Produces: machine-readable lifecycle/state, explicit v1->v2 successor mapping, 13-dimension Human Review gate.

- [ ] **Step 1: Create a fail-closed successor-map fixture first**

Write `ME1-SEMANTIC-SUCCESSOR-MAP-v0.1.json` with this minimum shape:

```json
{
  "stage": "ME1_STATE_OBJECT_MODEL_REFRAME",
  "historical_identities": [
    {
      "schema_id": "urn:yuanli-invest:schema:vnext-research-target:1.0.0",
      "path": "packages/contracts/schemas/vnext/research-target.schema.json",
      "redefined_in_place": false,
      "future_write_authority": false,
      "successor_schema_id": "urn:yuanli-invest:schema:vnext-research-target:2.0.0"
    },
    {
      "schema_id": "urn:yuanli-invest:schema:vnext-research-state-vector:1.0.0",
      "path": "packages/contracts/schemas/vnext/research-state-vector.schema.json",
      "redefined_in_place": false,
      "future_write_authority": false,
      "compatibility_role": "legacy_authoritative_history_non_authoritative_future"
    }
  ],
  "new_object_authority": {
    "research_target_v2": "target_identity_only",
    "engine_thesis": "thesis_authority_only",
    "position_passport": "capital_expression_contract_only",
    "book_state": "point_in_time_membership_only"
  },
  "next_me_stage_authorized": false
}
```

- [ ] **Step 2: Create ME1 lifecycle state**

Start `ME1-STATE.json` as:

```json
{
  "schema_version": "0.1.0",
  "stage": "ME1_STATE_OBJECT_MODEL_REFRAME",
  "status": "candidate_started",
  "design_acceptance": "ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME_DESIGN",
  "research_target_v2_successor_approved": true,
  "implementation_authorities": {
    "portfolio": false,
    "position_sizing": false,
    "trading": false,
    "live_execution": false,
    "registry_promotion": false,
    "constitution_mutation": false,
    "ME2": false,
    "ME3": false,
    "ME4": false,
    "ME5": false
  },
  "next_gate": "ME1_MACHINE_QUALIFICATION"
}
```

- [ ] **Step 3: Write authority note and 13-dimension review card**

The review card MUST contain D1–D13 exactly as defined by the spec and the acceptance token placeholder only for a future Human decision:

`ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME`

It must state: `Acceptance does not imply merge.`

- [ ] **Step 4: Review Task 1 for scope**

Verify no production schema or CI file changed in Task 1.

- [ ] **Step 5: Commit**

```bash
git add docs/architecture/me1
git commit -m "ME1: freeze state-object authority and semantic successors"
```

---

### Task 2: Add ResearchTarget v2 without mutating ResearchTarget v1

**Files:**
- Create: `packages/contracts/schemas/vnext/research-target-v2.schema.json`
- Test: `tests/test_me1_state_object_model.py`

**Interfaces:**
- Consumes: existing ResearchTarget v1 schema and Task 1 successor map.
- Produces: `ResearchTarget v2.0.0` local schema contract.

- [ ] **Step 1: Write failing tests for historical non-regression and v2 identity**

Add:

```python
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "packages/contracts/schemas/vnext/research-target.schema.json"
V2 = ROOT / "packages/contracts/schemas/vnext/research-target-v2.schema.json"

class ME1ResearchTargetTests(unittest.TestCase):
    def test_research_target_v1_identity_is_preserved(self):
        v1 = json.loads(V1.read_text())
        self.assertEqual(v1["$id"], "urn:yuanli-invest:schema:vnext-research-target:1.0.0")
        self.assertEqual(v1["required"], ["target_type", "target_id", "display_name"])

    def test_research_target_v2_exists_as_semantic_successor(self):
        v2 = json.loads(V2.read_text())
        self.assertEqual(v2["$id"], "urn:yuanli-invest:schema:vnext-research-target:2.0.0")
        self.assertIn("canonical_name", v2["properties"])
        self.assertIn("asset_form", v2["properties"])
```

- [ ] **Step 2: Run the tests and verify the v2 test fails**

Run:

```bash
python -m unittest tests.test_me1_state_object_model.ME1ResearchTargetTests -v
```

Expected: v1 preservation PASS, v2 test FAIL because file does not yet exist.

- [ ] **Step 3: Implement ResearchTarget v2 schema**

Use Draft 2020-12 and `$id = urn:yuanli-invest:schema:vnext-research-target:2.0.0`. Require:

```json
[
  "target_id", "schema_version", "target_type", "canonical_name",
  "asset_form", "active_status", "created_at", "authority"
]
```

Set authority constants:

```json
"authority": {
  "type": "object",
  "additionalProperties": false,
  "required": ["thesis_authority", "capital_authority", "trading_authority"],
  "properties": {
    "thesis_authority": {"const": false},
    "capital_authority": {"const": false},
    "trading_authority": {"const": false}
  }
}
```

Do not use a closed enum for `target_type`; use a non-empty string plus optional typed-extension metadata.

- [ ] **Step 4: Run tests**

Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add packages/contracts/schemas/vnext/research-target-v2.schema.json tests/test_me1_state_object_model.py
git commit -m "ME1: add ResearchTarget v2 semantic successor"
```

---

### Task 3: Add EngineThesis and PositionPassport schemas

**Files:**
- Create: `packages/contracts/schemas/vnext/engine-thesis.schema.json`
- Create: `packages/contracts/schemas/vnext/position-passport.schema.json`
- Modify: `tests/test_me1_state_object_model.py`
- Create: `docs/architecture/me1/fixtures/engine-theses.json`
- Create: `docs/architecture/me1/fixtures/position-passports.json`

**Interfaces:**
- Consumes: ResearchTarget v2 identity and Genesis engine names from ME0.
- Produces: local schemas and valid positive fixtures for later relational validation.

- [ ] **Step 1: Add failing schema-shape tests**

Test that EngineThesis requires one `identity_core.primary_engine`, and PositionPassport authority is false:

```python
def test_engine_thesis_schema_has_immutable_identity_core(self):
    schema = json.loads((ROOT / "packages/contracts/schemas/vnext/engine-thesis.schema.json").read_text())
    required = schema["properties"]["identity_core"]["required"]
    self.assertIn("primary_engine", required)
    self.assertIn("opened_at", required)


def test_position_passport_cannot_grant_trade_execution(self):
    schema = json.loads((ROOT / "packages/contracts/schemas/vnext/position-passport.schema.json").read_text())
    authority = schema["properties"]["authority"]["properties"]
    self.assertEqual(authority["trade_execution_authority"]["const"], False)
```

- [ ] **Step 2: Run and observe FAIL because schemas are absent**

```bash
python -m unittest tests.test_me1_state_object_model -v
```

- [ ] **Step 3: Implement `engine-thesis.schema.json`**

Require at least:

```json
[
  "engine_thesis_id", "schema_version", "target_id", "identity_core",
  "research_contract", "evidence", "falsification", "lifecycle", "authority"
]
```

Use lifecycle status enum limited to the accepted ME1 lifecycle:

```json
["draft", "researching", "qualified", "active", "challenged", "invalidated", "closed", "settled"]
```

Do NOT hard-code `primary_engine` to C/R/X in JSON Schema; relational validation handles governed engine resolution.

- [ ] **Step 4: Implement `position-passport.schema.json`**

Require redundant `target_id` and `primary_engine`, plus:

```json
"silent_migration_prohibited": {"const": true},
"governed_event_required": {"const": true}
```

and authority constants false.

- [ ] **Step 5: Create one positive Thesis + Passport fixture**

Use an NVDA example with `ENG-C`; do not add target price, weight, or trade action.

- [ ] **Step 6: Run tests**

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add packages/contracts/schemas/vnext/engine-thesis.schema.json packages/contracts/schemas/vnext/position-passport.schema.json docs/architecture/me1/fixtures tests/test_me1_state_object_model.py
git commit -m "ME1: add EngineThesis and PositionPassport contracts"
```

---

### Task 4: Add BookState and legacy compatibility schemas

**Files:**
- Create: `packages/contracts/schemas/vnext/book-state.schema.json`
- Create: `packages/contracts/schemas/vnext/legacy-rsv-projection.schema.json`
- Create: `packages/contracts/schemas/vnext/legacy-rsv-read-model.schema.json`
- Create: `docs/architecture/me1/fixtures/book-states.json`
- Create: `docs/architecture/me1/fixtures/legacy-rsv-projections.json`
- Create: `docs/architecture/me1/fixtures/research-targets-v2.json`
- Modify: `tests/test_me1_state_object_model.py`

**Interfaces:**
- Consumes: Task 2/3 schemas.
- Produces: PIT Book snapshots and one-way legacy compatibility contracts.

- [ ] **Step 1: Write failing tests for BookState PIT and read-only compatibility**

```python
def test_book_state_requires_point_in_time(self):
    schema = json.loads((ROOT / "packages/contracts/schemas/vnext/book-state.schema.json").read_text())
    self.assertIn("as_of", schema["required"])
    snapshot = schema["properties"]["snapshot"]["properties"]
    self.assertEqual(snapshot["append_only"]["const"], True)
    self.assertEqual(snapshot["point_in_time"]["const"], True)


def test_legacy_read_model_is_non_authoritative(self):
    schema = json.loads((ROOT / "packages/contracts/schemas/vnext/legacy-rsv-read-model.schema.json").read_text())
    props = schema["properties"]
    self.assertEqual(props["projection_only"]["const"], True)
    self.assertEqual(props["machine_authority"]["const"], False)
    self.assertEqual(props["write_back_prohibited"]["const"], True)
```

- [ ] **Step 2: Run and verify FAIL**

- [ ] **Step 3: Implement BookState schema**

Require:

```json
[
  "book_state_id", "schema_version", "book_id", "portfolio_namespace",
  "as_of", "memberships", "snapshot", "authority"
]
```

`book_id` may initially enumerate `BOOK-C`, `BOOK-R`, `BOOK-X`, `BOOK-CASH`; this is a Book namespace, not the open-world Return Engine registry.

- [ ] **Step 4: Implement compatibility schemas**

`legacy-rsv-projection.schema.json` must require:

```json
"engine_assignment": {
  "type": "object",
  "required": ["status"],
  "properties": {
    "status": {
      "enum": ["unresolved", "candidate_C", "candidate_R", "candidate_X", "candidate_other", "human_review_required", "resolved"]
    }
  }
}
```

The default fixture must use `unresolved` and contain no EngineThesis creation authority.

- [ ] **Step 5: Add 3–5 shadow targets/projections**

Use at least NVDA, Gold, UST30Y, Copper, USDJPY as target identities where practical. These fixtures are structural shadows only; do not infer C/R/X Thesis from legacy state.

- [ ] **Step 6: Run tests and schema checks**

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add packages/contracts/schemas/vnext/book-state.schema.json packages/contracts/schemas/vnext/legacy-rsv-*.schema.json docs/architecture/me1/fixtures tests/test_me1_state_object_model.py
git commit -m "ME1: add BookState and legacy compatibility contracts"
```

---

### Task 5: Build the fail-closed ME1 relational validator with Genesis negatives

**Files:**
- Create: `scripts/validate_me1_state_object_model.py`
- Modify: `tests/test_me1_state_object_model.py`

**Interfaces:**
- Consumes: all Task 1–4 schemas and fixtures.
- Produces: `main() -> int`, plus testable validation functions for V0–V7.

- [ ] **Step 1: Write failing relational tests before validator exists**

The test module must import:

```python
from scripts import validate_me1_state_object_model as me1
```

Add at least these named mutation tests:

```python
def test_engine_migration_same_thesis_id_is_rejected(self): ...
def test_passport_engine_mismatch_is_rejected(self): ...
def test_wrong_engine_book_membership_is_rejected(self): ...
def test_legacy_projection_cannot_create_thesis(self): ...
def test_legacy_read_model_write_back_is_rejected(self): ...
def test_settled_thesis_revision_is_rejected(self): ...
def test_invalidated_thesis_new_active_passport_is_rejected(self): ...
def test_double_primary_book_membership_is_rejected(self): ...
def test_book_state_without_as_of_is_rejected(self): ...
def test_future_knowledge_is_rejected(self): ...
def test_trading_authority_is_rejected(self): ...
def test_eng_cash_is_rejected(self): ...
def test_unknown_engine_without_authority_is_rejected(self): ...
def test_recorded_at_cannot_replace_known_as_of(self): ...
def test_research_target_v1_redefinition_is_rejected(self): ...
def test_v1_target_cannot_gain_thesis_authority(self): ...
```

- [ ] **Step 2: Run tests and verify RED**

```bash
python -m unittest tests.test_me1_state_object_model -v
```

Expected: import/module failure for missing validator.

- [ ] **Step 3: Implement validator skeleton**

Define these exact functions:

```python
def load_json(path: Path): ...
def validate_historical_non_regression() -> None: ...
def validate_local_schemas() -> None: ...
def validate_identity_integrity(bundle: dict) -> None: ...
def validate_reference_integrity(bundle: dict) -> None: ...
def validate_engine_consistency(bundle: dict) -> None: ...
def validate_lifecycle_consistency(bundle: dict) -> None: ...
def validate_no_silent_migration(bundle: dict) -> None: ...
def validate_pit_integrity(bundle: dict) -> None: ...
def validate_authority_integrity(bundle: dict) -> None: ...
def load_fixture_bundle() -> dict: ...
def main() -> int: ...
```

- [ ] **Step 4: Implement V0 historical non-regression**

Hard-code only historical identity assertions that are already accepted facts:

```python
v1 = load_json(VNEXT / "research-target.schema.json")
require(v1["$id"] == "urn:yuanli-invest:schema:vnext-research-target:1.0.0", "ResearchTarget v1 identity regressed")
require(v1["required"] == ["target_type", "target_id", "display_name"], "ResearchTarget v1 semantics regressed")
rsv = load_json(VNEXT / "research-state-vector.schema.json")
require(rsv["$id"] == "urn:yuanli-invest:schema:vnext-research-state-vector:1.0.0", "RSV identity regressed")
```

- [ ] **Step 5: Implement local JSON Schema validation**

Load the six ME1 schemas with `Draft202012Validator.check_schema()` and validate all positive fixtures with `FormatChecker()`.

- [ ] **Step 6: Implement relational V1–V7**

At minimum enforce:

```python
require(passport["target_id"] == thesis["target_id"], "Passport target mismatch")
require(passport["primary_engine"] == thesis["identity_core"]["primary_engine"], "Passport engine mismatch")
```

Book mapping:

```python
BOOK_ENGINE = {"BOOK-C": "ENG-C", "BOOK-R": "ENG-R", "BOOK-X": "ENG-X"}
```

`BOOK-CASH` must not map to an engine.

Known engines:

```python
GENESIS_ENGINES = {"ENG-C", "ENG-R", "ENG-X"}
```

Unknown engines require non-empty `engine_authority_ref`; absence is failure.

- [ ] **Step 7: Implement PIT validation**

Parse ISO timestamps and enforce:

```python
known_as_of <= knowledge_cutoff <= replay_cutoff
```

When `known_as_of` is missing but `recorded_at` is present, fail instead of substituting the latter.

- [ ] **Step 8: Make all 16 Genesis negative tests GREEN**

Run:

```bash
python -m unittest tests.test_me1_state_object_model -v
python scripts/validate_me1_state_object_model.py
```

Expected: all tests PASS; validator prints `state_model=valid` and exits 0.

- [ ] **Step 9: Commit**

```bash
git add scripts/validate_me1_state_object_model.py tests/test_me1_state_object_model.py
git commit -m "ME1: add fail-closed relational state-model validator"
```

---

### Task 6: Qualify the M2 shadow candidate without authority cutover

**Files:**
- Modify: `docs/architecture/me1/ME1-STATE.json`
- Modify: `docs/architecture/me1/ME1-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: candidate fixtures only if validation reveals structural defects.

**Interfaces:**
- Consumes: Task 5 validator and 3–5 shadow fixtures.
- Produces: M2 candidate-ready evidence; does not perform M3 cutover.

- [ ] **Step 1: Run ME1 validator against the shadow bundle**

```bash
python scripts/validate_me1_state_object_model.py
```

Expected: PASS with all legacy engine assignments still unresolved unless explicitly governed.

- [ ] **Step 2: Prove multi-thesis cardinality with one target fixture**

Add two distinct Thesis objects for the same ResearchTarget v2 only if both are explicit research fixtures, e.g. one `ENG-C` and one `ENG-R` Thesis for NVDA. They must have different `engine_thesis_id`, evidence/falsifiers, and no automatic origin from RSV.

- [ ] **Step 3: Prove Book membership belongs to Passport**

Create separate Passports and place them into `BOOK-C` / `BOOK-R` through BookState memberships. Do not attach the NVDA target directly to a Book.

- [ ] **Step 4: Record M2 candidate status**

Update state with:

```json
"migration": {
  "M1_schema_parallel": "passed",
  "M2_shadow_projection": "candidate_ready",
  "M3_authority_cutover": "not_authorized"
}
```

- [ ] **Step 5: Re-run validator and unittest suite**

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/architecture/me1
git commit -m "ME1: qualify multi-thesis shadow state model"
```

---

### Task 7: Integrate CI and stop at Human Review Gate

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/architecture/me1/ME1-STATE.json`
- Modify: `docs/architecture/me1/ME1-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Consumes: Task 1–6 implementation.
- Produces: exact-head machine qualification and `candidate_ready_for_human_review`; no acceptance receipt and no merge.

- [ ] **Step 1: Add ME1 validator to contracts job**

Insert immediately after ME0 validator:

```yaml
      - run: python scripts/validate_me0_multi_engine_ontology.py
      - run: python scripts/validate_me1_state_object_model.py
      - run: python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 2: Run local/branch verification**

```bash
python scripts/validate_me1_state_object_model.py
python scripts/validate_me0_multi_engine_ontology.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all PASS.

- [ ] **Step 3: Commit CI integration**

```bash
git add .github/workflows/ci.yml
git commit -m "ME1: gate state-object model in repository CI"
```

- [ ] **Step 4: Wait for exact-head GitHub Actions qualification**

Require both jobs on the exact PR head:
- `contracts = success`
- `governance = success`

Also confirm the ME1 validator step and full unittest step are success.

- [ ] **Step 5: Promote state only after exact-head qualification**

Set:

```json
"status": "candidate_ready_for_human_review",
"machine_qualification": {
  "validated_head_sha": "<exact validated SHA>",
  "contracts": "success",
  "governance": "success",
  "me1_validator": "success",
  "unit_tests": "success"
},
"next_gate": "HUMAN_REVIEW",
"next_me_stage_authorized": false
```

The literal SHA is filled from the completed exact-head run; this is runtime evidence, not a design placeholder.

- [ ] **Step 6: Run a second exact-head qualification for the state-only head**

Require `contracts + governance = success` again.

- [ ] **Step 7: Stop at Human Gate**

Do NOT create an acceptance receipt yet. Present the 13-dimension Human Review and request only:

`ACCEPT_ME1_STATE_OBJECT_MODEL_REFRAME`

Acceptance must remain separate from merge authorization.

- [ ] **Step 8: Final implementation commit if state projection changed**

```bash
git add docs/architecture/me1/ME1-STATE.json docs/architecture/me1/ME1-HUMAN-REVIEW-CARD-v0.1.md
git commit -m "ME1: project exact-head qualification for Human Review"
```

---

## Plan Self-Review

### Spec coverage

- ResearchTarget v1 preservation + v2 successor: Task 1–2.
- Target/Thesis/Passport/Book separation: Task 2–4.
- Multi-thesis cardinality: Task 3 + Task 6.
- Engine immutability / No Silent Thesis Migration: Task 5.
- Lifecycle / settlement terminal semantics: Task 3 + Task 5.
- PIT/vintage semantics: Task 3–5.
- BookState PIT and primary-book uniqueness: Task 4–5.
- Compatibility Projection and no write-back: Task 4–5.
- Legacy RSV cannot infer Thesis: Task 4–6.
- Open-world/fail-closed future engine resolution: Task 5.
- M1/M2 migration candidate, no M3 cutover: Task 6.
- 13/13 Human Review and exact-head CI: Task 1 + Task 7.
- No Portfolio/Trading/ME2–ME5 authority: Global Constraints + Task 5 + Task 7.

### Placeholder scan

PASS. The only runtime-dependent value is the exact validated GitHub SHA in Task 7; the plan explicitly requires it to be copied from the completed exact-head run rather than guessed.

### Type/name consistency

PASS. Canonical names used consistently across tasks:
- `ResearchTarget v2`
- `EngineThesis`
- `PositionPassport`
- `BookState`
- `LegacyRSVProjection`
- `LegacyRSVReadModel`
- `validate_me1_state_object_model.py`

## Execution Handoff

Plan complete. Implementation must use one of:

1. **Subagent-Driven Development** — fresh implementation/review context per task where real subagent tooling exists.
2. **Inline Execution** — use `superpowers:executing-plans`, preserving TDD, task review, independent commits, exact-head CI, and final whole-branch review.

In the current ChatGPT environment, do not pretend true subagent isolation if no subagent dispatch tool is available.
