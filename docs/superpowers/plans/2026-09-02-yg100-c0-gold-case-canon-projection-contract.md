# YG100-C0 | Gold Case Canon & Projection Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a machine-checkable, fail-closed C0 candidate contract that defines GoldCase identity, authority, point-in-time, settlement, projection, mutation, and stale/conflict rules without creating a second knowledge canon or writing the twelve GoldCase contents.

**Architecture:** C0 lives entirely as an architecture candidate under `docs/architecture/yg100/c0/` until a later explicit human gate promotes any schema into `packages/contracts/schemas/` or any object into a canonical replay surface. A JSON Schema defines one `GoldCase` object shape; a registry freezes the twelve Genesis IDs and their lifecycle/protection flags; a projection policy defines what Notion may display or propose but never authoritatively mutate; a single fail-closed Python validator plus `unittest` cover schema, registry, PIT, OPEN-state, protected-field, projection-hash, and no-authority invariants. CI runs the validator and tests, but C0 grants no knowledge promotion, live Notion mutation, query-runtime admission, decision, or capital authority.

**Tech Stack:** JSON Schema Draft 2020-12, Python 3.12, `jsonschema`, stdlib `json/pathlib/datetime/hashlib`, `unittest`, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-02-yg100-brain1-gold-knowledge-organ-design.md`

## Global Constraints

- `Canon first, Projection second`.
- `Human Projection != Machine Authority`.
- `Asset != Engine`.
- `Target != Thesis != Position != Book`.
- `Research pass != Capital pass`.
- `ClaimAuthority <= EvidenceAuthority`.
- `Open Case != Settled Case`.
- `Notion edit != Canon mutation`.
- `yuanli-invest` owns the Gold domain contract and candidate case-object specification; it must not create a second OB LLM Wiki knowledge canon.
- Notion is only `Human Projection + Navigation + Learning Experience`.
- Hero infographic is a generated projection artifact and is never evidence.
- C0 freezes authority and contracts only; it does **not** write the full twelve GoldCase contents.
- `YG100-C12` must remain `OPEN` until a later separately authorized Reality Settlement.
- `YG100-C06`, `YG100-C08`, and `YG100-C11` must retain Hard Negative protection metadata.
- Unknown or conflicting authority fails closed.
- No direct Notion-to-canon mutation path may exist.
- No automatic trading, portfolio sizing, buy/sell recommendation, Canon promotion, OS-MAX action, or cross-domain methodology promotion.
- C0 completion authorizes only a later K1 implementation plan; it does not automatically start K1.
- Do not merge the YG100 PR without a later explicit merge authorization token.

---

## File Structure

### Candidate authority and lifecycle
- Create: `docs/architecture/yg100/c0/YG100-C0-AUTHORITY-v0.1.md`
- Create: `docs/architecture/yg100/c0/YG100-C0-STATE.json`
- Create: `docs/architecture/yg100/c0/YG100-C0-HUMAN-REVIEW-CARD-v0.1.md`

### Candidate machine contracts
- Create: `docs/architecture/yg100/c0/contracts/gold-case.schema.json`
- Create: `docs/architecture/yg100/c0/gold-case-registry.v0.1.json`
- Create: `docs/architecture/yg100/c0/notion-projection-policy.v0.1.json`
- Create: `docs/architecture/yg100/c0/fixtures/gold-case-minimal-valid.json`
- Create: `docs/architecture/yg100/c0/fixtures/gold-case-invalid-open-settlement.json`
- Create: `docs/architecture/yg100/c0/fixtures/notion-mutation-safe.json`
- Create: `docs/architecture/yg100/c0/fixtures/notion-mutation-protected.json`

### Validation
- Create: `scripts/validate_yg100_c0.py`
- Create: `tests/test_yg100_c0.py`
- Modify: `.github/workflows/ci.yml`

---

### Task 1: Freeze C0 authority, lifecycle, and review gate

**Files:**
- Create: `docs/architecture/yg100/c0/YG100-C0-AUTHORITY-v0.1.md`
- Create: `docs/architecture/yg100/c0/YG100-C0-STATE.json`
- Create: `docs/architecture/yg100/c0/YG100-C0-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Consumes: accepted YG100-BRAIN1 design and existing YIP0 / ME0 / ME1 authority boundaries.
- Produces: one explicit C0 candidate-state object and a human-readable authority contract used by all later C0 tasks.

- [ ] **Step 1: Create the lifecycle state first**

Write `YG100-C0-STATE.json` exactly with this authority shape:

```json
{
  "schema_version": "0.1.0",
  "stage": "YG100_C0_GOLD_CASE_CANON_PROJECTION_CONTRACT",
  "status": "candidate_started",
  "design_acceptance": "ACCEPT_YG100_BRAIN1_GOLD_KNOWLEDGE_ORGAN_DESIGN",
  "truth_store_semantics": "single_upstream_gold_domain_contract_no_secondary_notion_truth_store",
  "implementation_authorities": {
    "gold_case_content_bootstrap": false,
    "knowledge_canon_promotion": false,
    "notion_live_mutation": false,
    "query_runtime_admission": false,
    "decision": false,
    "osmax_action": false,
    "portfolio_sizing": false,
    "trading": false,
    "reality_settlement": false,
    "cross_domain_methodology_promotion": false
  },
  "next_gate": "YG100_C0_MACHINE_QUALIFICATION"
}
```

- [ ] **Step 2: Write the authority note**

`YG100-C0-AUTHORITY-v0.1.md` must explicitly state:

```text
yuanli-invest C0 candidate = Gold domain contract / case identity / projection rules only
OB LLM Wiki / Yuanli Brain = federated knowledge canon / evidence graph / authority-aware recall
Notion = human projection / navigation / learning surface only
OS-MAX = later decision/action/outcome authority only when separately authorized
```

It must include these fail-closed rules verbatim:

```text
Notion edit != Canon mutation
Hero infographic != Evidence
OPEN != SETTLED
Projection visibility != Knowledge maturity
Research pass != Capital pass
```

- [ ] **Step 3: Create the human review card**

Create a seven-dimension C0 review card:

```text
D1 Authority separation
D2 Stable object identity
D3 PIT / hindsight protection
D4 OPEN / settlement protection
D5 Notion mutation boundary
D6 Projection traceability
D7 No action / capital authority leakage
```

The review card must use `PASS | FAIL | NOT_RUN` and include only this future acceptance token:

`ACCEPT_YG100_C0_GOLD_CASE_CANON_PROJECTION_CONTRACT`

It must state: `Acceptance does not imply merge, K1 bootstrap, Notion mutation, query admission, or capital action.`

- [ ] **Step 4: Verify Task 1 contains no GoldCase body content**

Run:

```bash
grep -R "outcome_summary\|entrepreneur_lesson\|evidence_refs" docs/architecture/yg100/c0/YG100-C0-*.md docs/architecture/yg100/c0/YG100-C0-STATE.json
```

Expected: no case-specific content; only generic contract terminology is permitted.

- [ ] **Step 5: Commit**

```bash
git add docs/architecture/yg100/c0/YG100-C0-AUTHORITY-v0.1.md \
        docs/architecture/yg100/c0/YG100-C0-STATE.json \
        docs/architecture/yg100/c0/YG100-C0-HUMAN-REVIEW-CARD-v0.1.md
git commit -m "YG100-C0: freeze authority and lifecycle"
```

---

### Task 2: Add the candidate GoldCase JSON Schema

**Files:**
- Create: `docs/architecture/yg100/c0/contracts/gold-case.schema.json`
- Create: `docs/architecture/yg100/c0/fixtures/gold-case-minimal-valid.json`
- Create: `docs/architecture/yg100/c0/fixtures/gold-case-invalid-open-settlement.json`
- Create: `tests/test_yg100_c0.py`

**Interfaces:**
- Consumes: Task 1 authority contract.
- Produces: Draft 2020-12 `GoldCase v0.1.0` candidate shape and positive/negative fixtures.

- [ ] **Step 1: Write failing tests for schema identity and required fields**

Create `tests/test_yg100_c0.py` with:

```python
from pathlib import Path
import json
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
C0 = ROOT / "docs" / "architecture" / "yg100" / "c0"
SCHEMA_PATH = C0 / "contracts" / "gold-case.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class YG100C0SchemaTests(unittest.TestCase):
    def test_gold_case_schema_identity_and_required_fields(self):
        schema = load(SCHEMA_PATH)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["$id"], "urn:yuanli-invest:schema:yg100-gold-case:0.1.0")
        required = set(schema["required"])
        for name in {
            "case_id", "title", "period_start", "period_end", "world_regime",
            "case_type", "lifecycle_state", "reality_state", "belief_state",
            "price_state", "convexity_state", "primary_engine", "book_roles",
            "action_state", "primary_drivers", "cross_asset_signals",
            "known_as_of", "replay_cutoff", "evidence_refs", "counter_evidence",
            "falsifiers", "hard_negative", "settlement_status", "authority_state",
            "projection_hash"
        }:
            self.assertIn(name, required)

    def test_schema_itself_is_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(load(SCHEMA_PATH))
```

- [ ] **Step 2: Run the tests and confirm the schema tests fail**

Run:

```bash
python -m unittest tests.test_yg100_c0.YG100C0SchemaTests -v
```

Expected: FAIL because `gold-case.schema.json` does not yet exist.

- [ ] **Step 3: Implement the candidate schema**

The schema must set `additionalProperties: false` and include these exact controlled enums:

```json
{
  "primary_engine": ["ENG-C", "ENG-R", "ENG-X"],
  "action_state": ["守", "攻", "持", "收", "等", "N/A"],
  "settlement_status": ["OPEN", "CLOSED_SUPPORTED", "CLOSED_PARTIAL", "CLOSED_FALSIFIED", "INDETERMINATE"],
  "authority_state": ["candidate", "reviewed", "admitted", "canonical_projection_only"]
}
```

`book_roles` must accept zero or more unique values from:

```json
["BOOK-S", "BOOK-C", "BOOK-R", "BOOK-X"]
```

`known_as_of` and `replay_cutoff` must be ISO date-time strings; `period_start` and `period_end` must be ISO dates.

`evidence_refs`, `counter_evidence`, and `falsifiers` must be arrays. Evidence entries must require at least:

```json
{
  "locator": "<stable locator>",
  "content_hash": "sha256:<64 lowercase hex>",
  "known_as_of": "<date-time>",
  "authority": "primary|admitted|derived"
}
```

`projection_hash` must either be `null` or match `^sha256:[0-9a-f]{64}$`.

- [ ] **Step 4: Create one minimal valid fixture and one invalid OPEN-settlement fixture**

`gold-case-minimal-valid.json` must use `YG100-C12`, `settlement_status = OPEN`, `authority_state = candidate`, `primary_engine = ENG-R`, and no outcome claim.

`gold-case-invalid-open-settlement.json` must intentionally combine:

```json
{
  "case_id": "YG100-C12",
  "settlement_status": "OPEN",
  "outcome_summary": "已证明储备体系重估完成"
}
```

so relational validation can later reject it even though its basic JSON shape may be valid.

- [ ] **Step 5: Add positive schema-instance validation test**

Append:

```python
    def test_minimal_fixture_validates(self):
        schema = load(SCHEMA_PATH)
        instance = load(C0 / "fixtures" / "gold-case-minimal-valid.json")
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = list(validator.iter_errors(instance))
        self.assertEqual(errors, [])
```

- [ ] **Step 6: Run tests**

```bash
python -m unittest tests.test_yg100_c0.YG100C0SchemaTests -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add docs/architecture/yg100/c0/contracts/gold-case.schema.json \
        docs/architecture/yg100/c0/fixtures/gold-case-minimal-valid.json \
        docs/architecture/yg100/c0/fixtures/gold-case-invalid-open-settlement.json \
        tests/test_yg100_c0.py
git commit -m "YG100-C0: add candidate GoldCase schema"
```

---

### Task 3: Freeze the twelve Genesis IDs in a registry without writing case bodies

**Files:**
- Create: `docs/architecture/yg100/c0/gold-case-registry.v0.1.json`
- Modify: `tests/test_yg100_c0.py`

**Interfaces:**
- Consumes: Task 2 schema identity.
- Produces: stable ID registry for K1; no evidence, mechanism, outcome, or investment conclusion is admitted by this registry.

- [ ] **Step 1: Write failing registry tests**

Append:

```python
class YG100C0RegistryTests(unittest.TestCase):
    def test_genesis_registry_has_exactly_twelve_unique_ids(self):
        registry = load(C0 / "gold-case-registry.v0.1.json")
        ids = [item["case_id"] for item in registry["cases"]]
        self.assertEqual(ids, [f"YG100-C{i:02d}" for i in range(1, 13)])
        self.assertEqual(len(ids), len(set(ids)))

    def test_hard_negative_protection_is_frozen(self):
        registry = load(C0 / "gold-case-registry.v0.1.json")
        by_id = {item["case_id"]: item for item in registry["cases"]}
        self.assertTrue(by_id["YG100-C06"]["hard_negative_protected"])
        self.assertTrue(by_id["YG100-C08"]["hard_negative_protected"])
        self.assertTrue(by_id["YG100-C11"]["hard_negative_protected"])

    def test_c12_is_open_and_not_settleable_by_projection(self):
        registry = load(C0 / "gold-case-registry.v0.1.json")
        c12 = {item["case_id"]: item for item in registry["cases"]}["YG100-C12"]
        self.assertEqual(c12["settlement_status"], "OPEN")
        self.assertFalse(c12["projection_may_settle"])
```

- [ ] **Step 2: Run and confirm FAIL because registry is absent**

```bash
python -m unittest tests.test_yg100_c0.YG100C0RegistryTests -v
```

- [ ] **Step 3: Implement the registry**

Registry header:

```json
{
  "schema_version": "0.1.0",
  "registry_id": "YG100-GOLD-CASE-REGISTRY-v0.1",
  "status": "candidate_identity_registry",
  "case_count": 12,
  "content_authority": false,
  "notion_truth_store": false,
  "cases": []
}
```

Each case entry may contain **only**:

```text
case_id
title
period_label
case_type_hint
hard_negative_protected
settlement_status
projection_may_settle
k1_content_bootstrapped
```

All `k1_content_bootstrapped` values must be `false` in C0.

C12 must be `OPEN`; C01-C11 may use their historical closed-status hints only if the field is explicitly marked `registry_hint_only` at registry level. The registry must not claim evidence-backed settlement before K1.

- [ ] **Step 4: Add a test prohibiting accidental case-body fields**

Append:

```python
    def test_registry_is_identity_only(self):
        registry = load(C0 / "gold-case-registry.v0.1.json")
        prohibited = {"evidence_refs", "counter_evidence", "falsifiers", "outcome_summary", "entrepreneur_lesson"}
        for item in registry["cases"]:
            self.assertTrue(prohibited.isdisjoint(item.keys()))
            self.assertFalse(item["k1_content_bootstrapped"])
```

- [ ] **Step 5: Run registry tests**

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/architecture/yg100/c0/gold-case-registry.v0.1.json tests/test_yg100_c0.py
git commit -m "YG100-C0: freeze twelve GoldCase identities"
```

---

### Task 4: Define Notion projection and mutation semantics

**Files:**
- Create: `docs/architecture/yg100/c0/notion-projection-policy.v0.1.json`
- Create: `docs/architecture/yg100/c0/fixtures/notion-mutation-safe.json`
- Create: `docs/architecture/yg100/c0/fixtures/notion-mutation-protected.json`
- Modify: `tests/test_yg100_c0.py`

**Interfaces:**
- Consumes: GoldCase field names from Task 2 and stable IDs from Task 3.
- Produces: explicit field classes for read projection, proposal-safe edits, and protected authority edits.

- [ ] **Step 1: Write failing projection-policy tests**

Append:

```python
class YG100C0ProjectionPolicyTests(unittest.TestCase):
    def test_notion_is_projection_only(self):
        policy = load(C0 / "notion-projection-policy.v0.1.json")
        self.assertEqual(policy["surface_role"], "human_projection_navigation_learning")
        self.assertFalse(policy["canonical_write_authority"])
        self.assertFalse(policy["settlement_authority"])
        self.assertFalse(policy["evidence_authority"])

    def test_protected_fields_fail_closed(self):
        policy = load(C0 / "notion-projection-policy.v0.1.json")
        protected = set(policy["protected_fields"])
        for field in {"settlement_status", "authority_state", "evidence_refs", "falsifiers", "primary_engine", "book_roles"}:
            self.assertIn(field, protected)

    def test_projection_hash_is_source_derived(self):
        policy = load(C0 / "notion-projection-policy.v0.1.json")
        self.assertEqual(policy["projection_hash_algorithm"], "sha256")
        self.assertEqual(policy["projection_hash_input"], "canonicalized_projection_payload_excluding_projection_hash")
```

- [ ] **Step 2: Run and confirm FAIL because policy file is absent**

```bash
python -m unittest tests.test_yg100_c0.YG100C0ProjectionPolicyTests -v
```

- [ ] **Step 3: Implement projection policy**

The policy must define three field classes:

```json
{
  "display_only_fields": ["projection_note", "display_label", "hero_caption"],
  "proposal_safe_fields": ["projection_note", "display_label"],
  "protected_fields": [
    "case_id", "known_as_of", "replay_cutoff", "evidence_refs", "counter_evidence",
    "falsifiers", "primary_engine", "book_roles", "settlement_status", "authority_state"
  ]
}
```

It must define these transitions exactly:

```text
safe Notion edit -> detected -> re-fetch -> diff -> proposal -> upstream review
protected Notion edit -> detected -> re-fetch -> diff -> FAIL_CLOSED_HUMAN_GATE
no Notion edit -> direct canonical update
```

- [ ] **Step 4: Create safe and protected mutation fixtures**

`notion-mutation-safe.json`:

```json
{
  "case_id": "YG100-C12",
  "changed_fields": ["projection_note"],
  "expected_classification": "PROPOSAL_SAFE"
}
```

`notion-mutation-protected.json`:

```json
{
  "case_id": "YG100-C12",
  "changed_fields": ["settlement_status"],
  "expected_classification": "FAIL_CLOSED_HUMAN_GATE"
}
```

- [ ] **Step 5: Add explicit test that Hero cannot be evidence**

Append:

```python
    def test_hero_is_never_evidence(self):
        policy = load(C0 / "notion-projection-policy.v0.1.json")
        self.assertEqual(policy["hero_semantics"], "generated_projection_artifact")
        self.assertFalse(policy["hero_may_be_evidence"])
```

- [ ] **Step 6: Run tests**

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add docs/architecture/yg100/c0/notion-projection-policy.v0.1.json \
        docs/architecture/yg100/c0/fixtures/notion-mutation-safe.json \
        docs/architecture/yg100/c0/fixtures/notion-mutation-protected.json \
        tests/test_yg100_c0.py
git commit -m "YG100-C0: define Notion projection boundary"
```

---

### Task 5: Implement fail-closed relational validation

**Files:**
- Create: `scripts/validate_yg100_c0.py`
- Modify: `tests/test_yg100_c0.py`

**Interfaces:**
- Consumes: Tasks 1–4 files.
- Produces: one deterministic validator callable locally and from CI.

- [ ] **Step 1: Write a failing test that imports and runs the validator**

Append:

```python
class YG100C0ValidatorTests(unittest.TestCase):
    def test_validator_passes_candidate_bundle(self):
        from scripts.validate_yg100_c0 import validate_all
        validate_all()

    def test_open_case_cannot_claim_settled_outcome(self):
        from scripts.validate_yg100_c0 import validate_case_semantics
        case = load(C0 / "fixtures" / "gold-case-invalid-open-settlement.json")
        with self.assertRaisesRegex(ValueError, "OPEN case cannot contain settled outcome claim"):
            validate_case_semantics(case)
```

- [ ] **Step 2: Run and confirm FAIL because validator is absent**

```bash
python -m unittest tests.test_yg100_c0.YG100C0ValidatorTests -v
```

- [ ] **Step 3: Implement validator primitives**

`validate_yg100_c0.py` must provide exactly these public functions:

```python
load_json(path: Path) -> dict
require(condition: bool, message: str) -> None
parse_dt(value: str) -> datetime
validate_schema() -> None
validate_registry() -> None
validate_case_semantics(case: dict) -> None
classify_notion_mutation(mutation: dict) -> str
validate_projection_policy() -> None
validate_state_authority() -> None
validate_all() -> None
```

Use `Draft202012Validator` + `FormatChecker` for local shape validation.

- [ ] **Step 4: Enforce PIT invariants**

For any evidence-bearing Case candidate:

```python
known_as_of <= replay_cutoff
```

Every evidence ref must additionally satisfy:

```python
evidence_ref.known_as_of <= case.replay_cutoff
```

Never substitute file modification time, `recorded_at`, publication ingestion date, or current date for `known_as_of`.

- [ ] **Step 5: Enforce OPEN-state semantics**

`validate_case_semantics()` must raise when:

```text
settlement_status == OPEN
AND outcome_summary is non-empty and uses a settled/closed claim
```

For C0 fixtures use the deterministic rule: any non-empty `outcome_summary` on an OPEN case is prohibited. K1 may later introduce a separate `open_case_observation` field if needed; do not overload `outcome_summary`.

- [ ] **Step 6: Enforce registry and protection invariants**

Fail if:

```text
case_count != 12
IDs != YG100-C01..YG100-C12 exactly
any duplicate ID exists
C06/C08/C11 hard_negative_protected != true
C12 settlement_status != OPEN
C12 projection_may_settle != false
any k1_content_bootstrapped == true
```

- [ ] **Step 7: Enforce mutation classification**

`classify_notion_mutation()` returns only:

```text
NO_CHANGE
PROPOSAL_SAFE
FAIL_CLOSED_HUMAN_GATE
UNKNOWN_FIELD_FAIL_CLOSED
```

Any protected field yields `FAIL_CLOSED_HUMAN_GATE`; any unknown field yields `UNKNOWN_FIELD_FAIL_CLOSED`.

- [ ] **Step 8: Enforce no-authority leakage**

`validate_state_authority()` must verify every value under `implementation_authorities` is `false` and that `notion_live_mutation`, `knowledge_canon_promotion`, `decision`, `portfolio_sizing`, and `trading` cannot become true in C0.

- [ ] **Step 9: Run validator and tests**

```bash
python scripts/validate_yg100_c0.py
python -m unittest tests.test_yg100_c0 -v
```

Expected:

```text
YG100-C0 validation PASS
```

and all unit tests PASS.

- [ ] **Step 10: Commit**

```bash
git add scripts/validate_yg100_c0.py tests/test_yg100_c0.py
git commit -m "YG100-C0: add fail-closed contract validator"
```

---

### Task 6: Wire C0 validation into repository CI and generate the machine-qualification receipt

**Files:**
- Modify: `.github/workflows/ci.yml`
- Create: `docs/architecture/yg100/c0/YG100-C0-MACHINE-QUALIFICATION-v0.1.md`
- Modify: `docs/architecture/yg100/c0/YG100-C0-STATE.json`
- Modify: `docs/architecture/yg100/c0/YG100-C0-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Consumes: passing validator and unit tests from Task 5.
- Produces: CI gate plus a factual qualification receipt. It does not self-accept C0.

- [ ] **Step 1: Add the validator to the existing `contracts` CI job**

Insert immediately after `validate_me1_state_object_model.py`:

```yaml
      - run: python scripts/validate_yg100_c0.py
```

Do not create a separate workflow and do not remove any existing gate.

- [ ] **Step 2: Run the full relevant local gate set**

```bash
python scripts/validate_yg100_c0.py
python -m unittest tests.test_yg100_c0 -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all commands exit `0`.

- [ ] **Step 3: Create machine-qualification receipt**

`YG100-C0-MACHINE-QUALIFICATION-v0.1.md` must record only observed facts:

```text
schema draft validation: PASS
12 stable IDs: PASS
hard-negative protections: PASS
C12 OPEN protection: PASS
Notion protected-field fail-closed: PASS
Hero-not-evidence rule: PASS
PIT rule: PASS
no authority leakage: PASS
full unittest: PASS or exact observed failure
GitHub Actions: PASS / FAIL / NOT_RUN with run URL if available
```

It must not say `C0 accepted`, `Canon promoted`, `Notion operational`, `Gold Knowledge Organ operational`, or equivalent.

- [ ] **Step 4: Advance state only to machine-qualified candidate**

Update `YG100-C0-STATE.json`:

```json
"status": "machine_qualified_candidate",
"next_gate": "YG100_C0_HUMAN_REVIEW"
```

Keep every `implementation_authorities` value `false`.

- [ ] **Step 5: Fill the review card from observed results**

Set D1–D7 to `PASS`, `FAIL`, or `NOT_RUN` from actual evidence. Do not pre-fill the acceptance token as approved.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/ci.yml \
        docs/architecture/yg100/c0/YG100-C0-MACHINE-QUALIFICATION-v0.1.md \
        docs/architecture/yg100/c0/YG100-C0-STATE.json \
        docs/architecture/yg100/c0/YG100-C0-HUMAN-REVIEW-CARD-v0.1.md
git commit -m "YG100-C0: wire machine qualification gate"
```

---

### Task 7: Perform completion verification and stop at the C0 human gate

**Files:**
- No new production files.
- Read-only verification of all C0 outputs and the current PR diff.

**Interfaces:**
- Consumes: Tasks 1–6.
- Produces: a review-ready C0 candidate only.

- [ ] **Step 1: Run the exact C0 validator again from a clean working tree**

```bash
python scripts/validate_yg100_c0.py
```

Expected: `YG100-C0 validation PASS`.

- [ ] **Step 2: Run the exact C0 unit test module**

```bash
python -m unittest tests.test_yg100_c0 -v
```

Expected: all PASS.

- [ ] **Step 3: Run the full repository unit-test suite**

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all PASS. If any unrelated pre-existing test fails, record its exact name and output in the machine-qualification receipt; do not conceal or reinterpret it.

- [ ] **Step 4: Audit scope boundaries**

Verify all of the following are true:

```text
No file under canon/ was created or modified.
No file under replays/gold/ was created or modified.
No file under packages/contracts/schemas/ was created or modified.
No Notion write occurred.
No OB LLM Wiki write occurred.
No OS-MAX action occurred.
No query runtime admission occurred.
No capital instruction occurred.
```

- [ ] **Step 5: Review PR diff for C0-only scope**

Expected changed paths are limited to:

```text
docs/superpowers/specs/2026-09-02-yg100-brain1-gold-knowledge-organ-design.md
docs/superpowers/plans/2026-09-02-yg100-c0-gold-case-canon-projection-contract.md
docs/architecture/yg100/c0/**
scripts/validate_yg100_c0.py
tests/test_yg100_c0.py
.github/workflows/ci.yml
```

- [ ] **Step 6: Stop and request the C0 human gate**

Report the observed machine evidence and request exactly:

`ACCEPT_YG100_C0_GOLD_CASE_CANON_PROJECTION_CONTRACT`

Do **not** begin K1, modify live Notion, create GoldCase contents, or claim `GOLD KNOWLEDGE ORGAN OPERATIONAL` before this token is explicitly granted.

---

## Plan Self-Review

### Spec coverage

- C0 authority / projection rules: Tasks 1 and 4.
- GoldCase machine contract: Task 2.
- Twelve stable IDs without case content: Task 3.
- PIT / evidence / settlement boundary: Tasks 2 and 5.
- Notion mutation / stale-authority semantics: Tasks 4 and 5.
- Hero projection-not-evidence rule: Task 4.
- Hard Negative and C12 OPEN protection: Tasks 3 and 5.
- Fail-closed validation: Task 5.
- CI and observed receipt: Task 6.
- Human gate before K1: Task 7.

### Deliberately deferred to later child plans

- `YG100-K1`: twelve evidence-bearing GoldCase contents and settlement packets.
- `YG100-N1`: live Notion Hero / Gallery / Timeline / Hard Negative / Open Case projection.
- `YG100-Q1`: 40-case authority-aware Brain Recall benchmark.
- `YG100-P2`: Notion ↔ Brain Canary reconciliation proof.
- `YG100-R1`: real Reality Settlement after qualifying evidence exists.

These are separate subsystems and must receive their own implementation plans after the prior gate passes.
