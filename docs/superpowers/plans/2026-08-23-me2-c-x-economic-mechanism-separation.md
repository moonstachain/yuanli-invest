# ME2 | C–X Economic Mechanism Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the accepted ME2 design into machine-checkable C/X successor contracts that separate underlying economic right-tail mechanisms from portfolio payoff convexity, preserve all historical X/Convexity/CAP-XS ledger identities, and fail closed on semantic leakage without granting alpha, portfolio, trading, or ME3–ME5 authority.

**Architecture:** Keep the accepted ME1 `ResearchTarget -> EngineThesis -> PositionPassport -> BookState@PIT` object graph unchanged. Add five focused engine/position sidecar schemas, ME2-only fixtures, a one-way legacy projection, and a fail-closed relational validator that enforces C/X dominance, PIT/calibration, legacy immutability, and authority boundaries. ME2 is additive successor architecture; it must not modify the accepted `EngineThesis`, `PositionPassport`, historical `ConvexityProfile`, `CAP-XS-01`, or old R2.3-B2 plan in place.

**Tech Stack:** JSON Schema Draft 2020-12, Python 3.12, `jsonschema`, stdlib `json/pathlib/datetime/hashlib/copy`, `unittest`, GitHub Actions `repository-gates`.

**Spec:** `docs/superpowers/specs/2026-08-23-me2-c-x-economic-mechanism-separation-design.md`

## Global Constraints

- Program order is strict: `ME2 -> ME3 -> ME4 -> ME5`; this plan grants no ME3–ME5 authority.
- `ECONOMIC_RIGHT_TAIL != CONVEX_PAYOFF`.
- `REAL_OPTIONALITY != FINANCIAL_OPTION_PAYOFF`.
- `UNDERLYING_OPTIONALITY_DOES_NOT_PROPAGATE_ENGINE_IDENTITY`.
- `INSTRUMENT_TYPE != RETURN_ENGINE`.
- `STRUCTURE_BELONGS_TO_ITS_CAUSAL_MECHANISM`.
- `POSITIVE_SKEW != ENG-X`.
- `CONVEX_PAYOFF != POSITIVE_EXPECTED_VALUE`.
- `HUMAN_X != MACHINE_ENG_X`.
- Preserve upstream `Target != Thesis != Position != Book`.
- Preserve `Research Pass != Capital Pass`, `No Silent Thesis Migration`, and `Claim Authority <= Evidence Authority`.
- Do not create a universal `EconomicAsymmetryProfile`.
- Do not create `StructuralRightTailProfile`; it is `superseded_before_canonical_schema_creation`.
- Do not modify `packages/contracts/schemas/vnext/engine-thesis.schema.json`.
- Do not modify `packages/contracts/schemas/vnext/position-passport.schema.json`.
- Do not modify `packages/contracts/schemas/convexity-profile.schema.json`.
- Do not modify `docs/architecture/r2_3b1/CAP-XS-01-SPEC-v0.1.json`.
- Do not modify `docs/methodology/extreme-engine-v0.1.md`.
- Do not modify the historical R2.3-B2 implementation plan; supersede its future CAP-XS execution path only through ME2 successor metadata.
- A qualified/active `ENG-C` Thesis requires exactly one current `CompoundingMechanismAttachment`.
- A qualified/active `ENG-X` Thesis requires exactly one current `ConvexityMechanismAttachment`.
- An X mechanism requires at least one referenced `TailActivationSnapshot`, with exactly one authoritative-current snapshot in the fixture context.
- An eligible/active X `PositionPassport` requires exactly one authoritative-current `PayoffGeometryContext`.
- C/R Passports may carry PGCs, but a valid C thesis must have `geometry_dependency != dominant`.
- A valid X thesis must have `expected_pnl_driver = nonlinear_payoff_geometry` and `geometry_dependency = dominant`.
- Numeric tail probability is forbidden without `probability_definition`, `horizon`, `base_rate_ref`, and `calibration_ref`.
- Legacy projection must always be one-way, non-authoritative, write-back-prohibited, and engine-inference-prohibited.
- Static linear exposure cannot qualify as X from upside narrative, historical multibagger status, positive skew, TAM, moat, network effect, or legacy Xs/convexity labels alone.
- ME2 grants no alpha runtime, historical performance claim, portfolio weight, position size, buy/sell/hold, trade execution, live execution, new-engine creation, capability promotion, A9 switch, Constitution mutation, or runtime cutover authority.
- Final Human Review requires 18/18 PASS.
- Human acceptance does not imply merge; merge requires a later explicit `AUTHORIZE_ME2_MERGE`.

---

## File Structure

### Candidate authority / governance
- Create: `docs/architecture/me2/ME2-C-X-ECONOMIC-MECHANISM-SEPARATION-AUTHORITY-v0.1.md`
- Create: `docs/architecture/me2/ME2-SEMANTIC-SUCCESSOR-MAP-v0.1.json`
- Create: `docs/architecture/me2/ME2-HARD-NEGATIVE-MATRIX-v0.1.json`
- Create: `docs/architecture/me2/ME2-STATE.json`
- Create: `docs/architecture/me2/ME2-HUMAN-REVIEW-CARD-v0.1.md`

### New schemas
- Create: `packages/contracts/schemas/vnext/compounding-mechanism-attachment.schema.json`
- Create: `packages/contracts/schemas/vnext/convexity-mechanism-attachment.schema.json`
- Create: `packages/contracts/schemas/vnext/tail-activation-snapshot.schema.json`
- Create: `packages/contracts/schemas/vnext/payoff-geometry-context.schema.json`
- Create: `packages/contracts/schemas/vnext/legacy-convexity-projection.schema.json`

### ME2-only fixtures
- Create: `docs/architecture/me2/fixtures/me2-engine-theses.json`
- Create: `docs/architecture/me2/fixtures/me2-position-passports.json`
- Create: `docs/architecture/me2/fixtures/compounding-mechanism-attachments.json`
- Create: `docs/architecture/me2/fixtures/convexity-mechanism-attachments.json`
- Create: `docs/architecture/me2/fixtures/tail-activation-snapshots.json`
- Create: `docs/architecture/me2/fixtures/payoff-geometry-contexts.json`
- Create: `docs/architecture/me2/fixtures/legacy-convexity-projections.json`

### Validation / CI
- Create: `scripts/validate_me2_c_x_separation.py`
- Create: `tests/test_me2_c_x_separation.py`
- Modify: `.github/workflows/ci.yml`

No other file is required for the ME2 candidate implementation.

---

### Task 1: Freeze ME2 candidate authority, successor lineage, and review gates

**Files:**
- Create: `tests/test_me2_c_x_separation.py`
- Create: `docs/architecture/me2/ME2-C-X-ECONOMIC-MECHANISM-SEPARATION-AUTHORITY-v0.1.md`
- Create: `docs/architecture/me2/ME2-SEMANTIC-SUCCESSOR-MAP-v0.1.json`
- Create: `docs/architecture/me2/ME2-HARD-NEGATIVE-MATRIX-v0.1.json`
- Create: `docs/architecture/me2/ME2-STATE.json`
- Create: `docs/architecture/me2/ME2-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Consumes: accepted ME2 design, ME0 successor law, ME1 object/compatibility law.
- Produces: deterministic ME2 stage identity, historical lineage locks, 16 hard-negative IDs, 5 hard-positive IDs, 18-dimension Human Review contract.

- [ ] **Step 1: Write failing governance-file tests**

Create `tests/test_me2_c_x_separation.py` with:

```python
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ME2 = ROOT / "docs" / "architecture" / "me2"


class ME2GovernanceTests(unittest.TestCase):
    def test_state_is_candidate_only_and_does_not_authorize_me3(self):
        state = json.loads((ME2 / "ME2-STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(state["stage"], "ME2_C_X_ECONOMIC_MECHANISM_SEPARATION")
        self.assertEqual(state["status"], "candidate_started")
        self.assertEqual(state["design_acceptance"], "ACCEPT_ME2_WRITTEN_SPEC")
        self.assertFalse(state["implementation_authorities"]["alpha_runtime"])
        self.assertFalse(state["implementation_authorities"]["portfolio"])
        self.assertFalse(state["implementation_authorities"]["trading"])
        self.assertFalse(state["implementation_authorities"]["ME3"])
        self.assertFalse(state["implementation_authorities"]["ME4"])
        self.assertFalse(state["implementation_authorities"]["ME5"])

    def test_successor_map_supersedes_old_cap_xs_future_execution_without_rewriting_history(self):
        successor = json.loads((ME2 / "ME2-SEMANTIC-SUCCESSOR-MAP-v0.1.json").read_text(encoding="utf-8"))
        xs = successor["historical_identities"]["CAP-XS-01"]
        self.assertTrue(xs["historical_contract_authority"])
        self.assertFalse(xs["redefined_in_place"])
        self.assertFalse(xs["future_reference_implementation_authority"])
        self.assertEqual(xs["successor_policy"], "typed_route_split_by_causal_mechanism")
        old_plan = successor["superseded_future_paths"]["R2_3B2_CAP_XS_01"]
        self.assertEqual(old_plan["status"], "superseded_before_execution_by_ME2")
        self.assertTrue(old_plan["do_not_execute"])

    def test_review_contract_is_exactly_18_dimensions(self):
        text = (ME2 / "ME2-HUMAN-REVIEW-CARD-v0.1.md").read_text(encoding="utf-8")
        for index in range(1, 19):
            self.assertIn(f"D{index} |", text)
        self.assertIn("Acceptance does not imply merge.", text)
```

- [ ] **Step 2: Run the governance tests and verify failure**

Run:

```bash
python -m unittest tests.test_me2_c_x_separation.ME2GovernanceTests -v
```

Expected: FAIL because `docs/architecture/me2/` does not yet exist.

- [ ] **Step 3: Create `ME2-STATE.json` with exact candidate authority**

Use:

```json
{
  "schema_version": "0.1.0",
  "stage": "ME2_C_X_ECONOMIC_MECHANISM_SEPARATION",
  "status": "candidate_started",
  "design_acceptance": "ACCEPT_ME2_WRITTEN_SPEC",
  "program_order": ["ME2", "ME3", "ME4", "ME5"],
  "implementation_authorities": {
    "semantic_successor_contracts": true,
    "candidate_schema_validation": true,
    "alpha_runtime": false,
    "historical_performance_claim": false,
    "capability_promotion": false,
    "new_engine_creation": false,
    "portfolio": false,
    "position_sizing": false,
    "trading": false,
    "live_execution": false,
    "constitution_mutation": false,
    "runtime_cutover": false,
    "ME3": false,
    "ME4": false,
    "ME5": false
  },
  "human_review_dimensions": 18,
  "next_gate": "ME2_MACHINE_QUALIFICATION"
}
```

- [ ] **Step 4: Create the semantic successor map with literal historical locks**

`ME2-SEMANTIC-SUCCESSOR-MAP-v0.1.json` must include these exact historical records:

```json
{
  "stage": "ME2_C_X_ECONOMIC_MECHANISM_SEPARATION",
  "policy": "semantic_successors_never_mutate_historical_receipts_or_contracts",
  "historical_artifacts": {
    "convexity_profile_v1": {
      "path": "packages/contracts/schemas/convexity-profile.schema.json",
      "blob_sha": "6c150e03ae3163517153bdd9683cbd083a675198",
      "future_write_authority": false,
      "redefined_in_place": false
    },
    "cap_xs_01": {
      "path": "docs/architecture/r2_3b1/CAP-XS-01-SPEC-v0.1.json",
      "blob_sha": "862ff407d39171283884d920e25641ffdddabb0b",
      "redefined_in_place": false
    },
    "extreme_engine_v0_1": {
      "path": "docs/methodology/extreme-engine-v0.1.md",
      "blob_sha": "f9dd55a855b4f64f1f606487e24a0536af80b61e",
      "redefined_in_place": false
    },
    "r2_3b2_plan": {
      "path": "docs/superpowers/plans/2026-08-21-r2-3b2-p0-reference-implementation.md",
      "blob_sha": "408a9e76a102f87eaab19c14cf6303105588e54f",
      "redefined_in_place": false
    },
    "engine_thesis_v1": {
      "path": "packages/contracts/schemas/vnext/engine-thesis.schema.json",
      "blob_sha": "06102eeffce467c8d6707a4fcadcc4f652811d79",
      "redefined_in_place": false
    },
    "position_passport_v1": {
      "path": "packages/contracts/schemas/vnext/position-passport.schema.json",
      "blob_sha": "22e73c090b84ff88d809d70d638a2d9f6ce31697",
      "redefined_in_place": false
    }
  },
  "historical_identities": {
    "CAP-XS-01": {
      "historical_contract_authority": true,
      "historical_meaning": "Structural Asymmetry Source Mapper",
      "redefined_in_place": false,
      "future_reference_implementation_authority": false,
      "future_canonical_output_authority": false,
      "successor_policy": "typed_route_split_by_causal_mechanism"
    },
    "StructuralRightTailProfile": {
      "historical_status": "candidate_only_never_canonical_schema",
      "successor_status": "superseded_before_canonical_schema_creation",
      "schema_creation_prohibited_under_ME2": true
    },
    "TailActivationSnapshot": {
      "historical_status": "candidate_object",
      "successor_status": "explicit_ME2_successor_contract_candidate"
    },
    "PayoffConvexityContext": {
      "historical_status": "candidate_object",
      "successor_identity": "PayoffGeometryContext"
    }
  },
  "superseded_future_paths": {
    "R2_3B2_CAP_XS_01": {
      "path": "docs/superpowers/plans/2026-08-21-r2-3b2-p0-reference-implementation.md",
      "status": "superseded_before_execution_by_ME2",
      "do_not_execute": true,
      "replacement": "ME2_typed_successor_contracts_plus_future_capability_specific_governance"
    }
  },
  "next_me_stage_authorized": false
}
```

- [ ] **Step 5: Create the 16-negative / 5-positive matrix**

`ME2-HARD-NEGATIVE-MATRIX-v0.1.json` must contain exact IDs `HN-01` through `HN-16` and `HP-01` through `HP-05`, with these propositions/results:

```json
{
  "hard_negatives": [
    {"id":"HN-01","proposition":"large_TAM_implies_ENG_X","expected":"FAIL"},
    {"id":"HN-02","proposition":"network_effect_implies_ENG_X","expected":"FAIL"},
    {"id":"HN-03","proposition":"historical_20x_implies_ENG_X","expected":"FAIL"},
    {"id":"HN-04","proposition":"legacy_convexity_state_convex_implies_ENG_X","expected":"FAIL"},
    {"id":"HN-05","proposition":"legacy_Xs_strong_implies_ENG_X","expected":"FAIL"},
    {"id":"HN-06","proposition":"option_instrument_implies_ENG_X","expected":"FAIL"},
    {"id":"HN-07","proposition":"ENG_X_without_tail_activation","expected":"FAIL"},
    {"id":"HN-08","proposition":"eligible_or_active_ENG_X_without_current_PGC","expected":"FAIL"},
    {"id":"HN-09","proposition":"Xa_probability_without_calibration","expected":"FAIL"},
    {"id":"HN-10","proposition":"ENG_C_with_dominant_geometry","expected":"FAIL"},
    {"id":"HN-11","proposition":"ENG_X_with_auxiliary_or_material_geometry","expected":"FAIL"},
    {"id":"HN-12","proposition":"real_optionality_implies_financial_convexity","expected":"FAIL"},
    {"id":"HN-13","proposition":"CAP_XS_legacy_output_auto_creates_new_mechanism_authority","expected":"FAIL"},
    {"id":"HN-14","proposition":"legacy_projection_writeback","expected":"FAIL"},
    {"id":"HN-15","proposition":"same_thesis_primary_engine_C_to_X_mutation","expected":"FAIL"},
    {"id":"HN-16","proposition":"ME2_contract_grants_capital_or_trading_authority","expected":"FAIL"}
  ],
  "hard_positives": [
    {"id":"HP-01","proposition":"NVDA_common_stock_C_plus_CMA","expected":"PASS"},
    {"id":"HP-02","proposition":"NVDA_LEAPS_C_plus_CMA_plus_PGC_material","expected":"PASS"},
    {"id":"HP-03","proposition":"long_call_X_plus_XMA_plus_TAS_plus_PGC_dominant","expected":"PASS"},
    {"id":"HP-04","proposition":"legacy_convexity_profile_read_only_projection","expected":"PASS"},
    {"id":"HP-05","proposition":"same_target_has_independent_C_and_X_theses","expected":"PASS"}
  ]
}
```

- [ ] **Step 6: Create authority note and 18-dimension Human Review card**

The authority note must restate the eight ME2 invariants, Stable Core + Sidecar architecture, five candidate contracts, no runtime/portfolio authority, and strict ME2→ME3 serial gate. The Human Review card must contain exactly:

```text
D1 | Economic Right Tail != Convex Payoff
D2 | Real Optionality != Financial Option Payoff
D3 | Human X != Machine ENG-X
D4 | Structure routed by causal mechanism
D5 | CAP-XS-01 historical identity preserved
D6 | CAP-XS future implementation path superseded
D7 | ConvexityProfile v1 immutable
D8 | CMA correctly governs ENG-C
D9 | XMA correctly governs ENG-X
D10 | Xa is PIT Tail Activation
D11 | Xp successor belongs to Position geometry
D12 | Instrument != Engine
D13 | Dominant geometry required for ENG-X
D14 | Legacy projection is one-way
D15 | No Silent Thesis Migration preserved
D16 | Hard Negative suite passes
D17 | No capability/engine/portfolio/runtime authority leakage
D18 | ME0/ME1 historical non-regression passes
```

The card must start as `Status: candidate_not_yet_human_reviewed`, name the future decision token `ACCEPT_ME2_C_X_ECONOMIC_MECHANISM_SEPARATION`, and state `Acceptance does not imply merge.`

- [ ] **Step 7: Run Task 1 tests**

Run:

```bash
python -m unittest tests.test_me2_c_x_separation.ME2GovernanceTests -v
```

Expected: PASS.

- [ ] **Step 8: Commit Task 1**

```bash
git add docs/architecture/me2 tests/test_me2_c_x_separation.py
git commit -m "ME2: freeze C-X successor authority and review gates"
```

---

### Task 2: Add Compounding and Convexity mechanism sidecar schemas

**Files:**
- Create: `packages/contracts/schemas/vnext/compounding-mechanism-attachment.schema.json`
- Create: `packages/contracts/schemas/vnext/convexity-mechanism-attachment.schema.json`
- Modify: `tests/test_me2_c_x_separation.py`

**Interfaces:**
- Consumes: accepted `EngineThesis v1` identity and Genesis engine IDs.
- Produces: `CompoundingMechanismAttachment (CMA-*)` and `ConvexityMechanismAttachment (XMA-*)` local JSON Schema contracts.

- [ ] **Step 1: Add failing schema identity and boundary tests**

Append:

```python
class ME2AttachmentSchemaTests(unittest.TestCase):
    def test_cma_is_eng_c_sidecar_not_right_tail_score(self):
        path = ROOT / "packages/contracts/schemas/vnext/compounding-mechanism-attachment.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "urn:yuanli-invest:schema:vnext-compounding-mechanism-attachment:1.0.0")
        props = schema["properties"]
        self.assertEqual(props["primary_engine"], {"const":"ENG-C"})
        self.assertEqual(props["primary_return_source"], {"const":"economic_compounding"})
        self.assertNotIn("economic_asymmetry_score", props)
        self.assertNotIn("convexity_state", props)

    def test_xma_is_payoff_engine_not_underlying_quality_profile(self):
        path = ROOT / "packages/contracts/schemas/vnext/convexity-mechanism-attachment.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "urn:yuanli-invest:schema:vnext-convexity-mechanism-attachment:1.0.0")
        props = schema["properties"]
        self.assertEqual(props["primary_engine"], {"const":"ENG-X"})
        self.assertEqual(props["primary_return_source"], {"const":"nonlinear_payoff_geometry"})
        for prohibited in ("network_effects", "market_expansion", "winner_take_most", "value_capture"):
            self.assertNotIn(prohibited, props)
```

- [ ] **Step 2: Run tests and observe missing-schema failure**

Run:

```bash
python -m unittest tests.test_me2_c_x_separation.ME2AttachmentSchemaTests -v
```

Expected: FAIL with missing files.

- [ ] **Step 3: Implement the CMA schema**

Use Draft 2020-12, `additionalProperties: false`, and this exact top-level contract:

```json
{
  "$id": "urn:yuanli-invest:schema:vnext-compounding-mechanism-attachment:1.0.0",
  "title": "CompoundingMechanismAttachment",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "attachment_id", "schema_version", "engine_thesis_id", "target_id",
    "primary_engine", "primary_return_source", "economic_mechanism_refs",
    "economic_optionality_refs", "return_bridge", "price_semantics_refs",
    "dominance_test", "evidence", "falsification", "lifecycle", "authority"
  ]
}
```

Exact semantic constants/enums:

```json
"attachment_id": {"type":"string","pattern":"^CMA-[A-Z0-9-]+$"},
"schema_version": {"const":"1.0.0"},
"primary_engine": {"const":"ENG-C"},
"primary_return_source": {"const":"economic_compounding"}
```

`economic_mechanism_refs` is a non-empty unique array of objects requiring `role` and `ref`; `role` is one of `value_pool`, `value_creation`, `value_capture`, `owner_economics`, `reinvestment`, `durability`, `other_governed_mechanism`. `economic_optionality_refs` is a unique array of non-empty strings and never grants X identity.

`return_bridge` must require all four refs:

```json
[
  "value_creation_or_control_ref",
  "value_capture_ref",
  "owner_economics_ref",
  "reinvestment_ref"
]
```

`dominance_test` must require:

```json
{
  "linear_counterfactual": {"enum":["survives","materially_degraded","fails","unknown"]},
  "geometry_dependency": {"enum":["auxiliary","material","dominant"]},
  "tail_state_dependency": {"enum":["low","material","dominant","unknown"]},
  "expected_pnl_driver": {"const":"economic_compounding"},
  "rationale": {"type":"string","minLength":1}
}
```

`evidence` requires `supporting_refs`, `counter_refs`, `known_as_of`, `knowledge_cutoff`; `falsification` requires a non-empty `falsifier_refs`; `lifecycle` requires `status`, `as_of`, `valid_from`, `valid_to`, `authoritative_current`, where status is `draft|researching|qualified|active|challenged|invalidated|closed`. `authority` contains only false constants for capital, portfolio weight, position sizing, trading, live execution, alpha runtime, capability promotion, and new-engine creation.

Do not enforce `geometry_dependency != dominant` in JSON Schema; that is a relational/business invariant checked by the ME2 validator so error codes stay deterministic.

- [ ] **Step 4: Implement the XMA schema**

Use the same envelope style with:

```json
{
  "$id": "urn:yuanli-invest:schema:vnext-convexity-mechanism-attachment:1.0.0",
  "title": "ConvexityMechanismAttachment",
  "required": [
    "attachment_id", "schema_version", "engine_thesis_id", "target_id",
    "primary_engine", "primary_return_source", "tail_activation_refs",
    "convexity_price_refs", "underlying_state_refs", "state_to_payoff_hypothesis",
    "dominance_test", "evidence", "falsification", "lifecycle", "authority"
  ]
}
```

Exact constants:

```json
"attachment_id": {"type":"string","pattern":"^XMA-[A-Z0-9-]+$"},
"schema_version": {"const":"1.0.0"},
"primary_engine": {"const":"ENG-X"},
"primary_return_source": {"const":"nonlinear_payoff_geometry"}
```

`tail_activation_refs` must be a non-empty unique array of `TAS-*` IDs. `convexity_price_refs` must be a non-empty unique array of non-empty strings. `underlying_state_refs` may be empty and is explicitly context-only. `state_to_payoff_hypothesis` is a non-empty string.

`dominance_test.expected_pnl_driver` is constant `nonlinear_payoff_geometry`; all other dominance fields use the same enums as CMA. Authority fields are the same hard-false constants.

- [ ] **Step 5: Run attachment tests**

Run:

```bash
python -m unittest tests.test_me2_c_x_separation.ME2AttachmentSchemaTests -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add packages/contracts/schemas/vnext/compounding-mechanism-attachment.schema.json packages/contracts/schemas/vnext/convexity-mechanism-attachment.schema.json tests/test_me2_c_x_separation.py
git commit -m "ME2: add C and X mechanism sidecar contracts"
```

---

### Task 3: Add Tail Activation and Payoff Geometry PIT schemas

**Files:**
- Create: `packages/contracts/schemas/vnext/tail-activation-snapshot.schema.json`
- Create: `packages/contracts/schemas/vnext/payoff-geometry-context.schema.json`
- Modify: `tests/test_me2_c_x_separation.py`

**Interfaces:**
- Consumes: XMA tail-reference semantics and accepted PositionPassport identity.
- Produces: PIT `TailActivationSnapshot (TAS-*)` and Position-level `PayoffGeometryContext (PGC-*)` contracts.

- [ ] **Step 1: Add failing TAS/PGC schema tests**

Append:

```python
class ME2PayoffSchemaTests(unittest.TestCase):
    def test_tail_activation_probability_requires_calibration_contract(self):
        schema = json.loads((ROOT / "packages/contracts/schemas/vnext/tail-activation-snapshot.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "urn:yuanli-invest:schema:vnext-tail-activation-snapshot:1.0.0")
        self.assertIn("estimated_probability", schema["properties"])
        self.assertIn("allOf", schema)

    def test_payoff_geometry_belongs_to_position(self):
        schema = json.loads((ROOT / "packages/contracts/schemas/vnext/payoff-geometry-context.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "urn:yuanli-invest:schema:vnext-payoff-geometry-context:1.0.0")
        self.assertIn("position_passport_id", schema["required"])
        self.assertIn("instrument_ref", schema["required"])
        self.assertIn("geometry_dependency", schema["required"])
        self.assertNotIn("research_target_convexity", schema["properties"])
```

- [ ] **Step 2: Run and verify failure because schemas are absent**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2PayoffSchemaTests -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `TailActivationSnapshot`**

Use:

```json
{
  "$id":"urn:yuanli-invest:schema:vnext-tail-activation-snapshot:1.0.0",
  "title":"TailActivationSnapshot",
  "type":"object",
  "additionalProperties":false,
  "required":[
    "tail_activation_snapshot_id","schema_version","target_id","as_of",
    "known_as_of","knowledge_cutoff","horizon","tail_side","activation_state",
    "state_refs","evidence_refs","counter_evidence_refs","probability_semantics",
    "staleness","authoritative_current","authority"
  ]
}
```

Exact enums:

```json
"tail_side": {"enum":["upside","downside","two_sided"]},
"activation_state": {"enum":["inactive","watch","activating","active","unknown"]},
"probability_semantics": {"enum":["uncalibrated_state","calibrated_probability"]},
"staleness": {"enum":["fresh","stale","unknown"]}
```

Optional `estimated_probability` is a number in `[0,1]`. Add Draft-2020-12 conditional validation:

```json
"allOf": [
  {
    "if": {"required":["estimated_probability"]},
    "then": {
      "required":["probability_definition","base_rate_ref","calibration_ref"],
      "properties": {"probability_semantics":{"const":"calibrated_probability"}}
    }
  }
]
```

`probability_definition`, `base_rate_ref`, `calibration_ref` are non-empty strings. `horizon` is already required. `authority` is all false for capital, trading, live execution, alpha runtime, and portfolio sizing.

- [ ] **Step 4: Implement `PayoffGeometryContext`**

Use:

```json
{
  "$id":"urn:yuanli-invest:schema:vnext-payoff-geometry-context:1.0.0",
  "title":"PayoffGeometryContext",
  "type":"object",
  "additionalProperties":false,
  "required":[
    "payoff_geometry_context_id","schema_version","position_passport_id",
    "engine_thesis_id","instrument_ref","as_of","valid_from","valid_to",
    "geometry_family","direction_semantics","downside_geometry","upside_geometry",
    "expiry_semantics","path_dependency","leverage_semantics","premium_ref",
    "implied_volatility_ref","skew_ref","term_structure_ref","carry_decay_ref",
    "breakeven_ref","liquidity_ref","friction_refs","geometry_dependency",
    "authoritative_current","authority"
  ]
}
```

Exact enums:

```json
"geometry_family": {"enum":["linear","leveraged_linear","convex","concave","capped","binary","path_dependent","mixed","unknown"]},
"geometry_dependency": {"enum":["auxiliary","material","dominant"]}
```

All `*_ref` price/liquidity fields may be string or null so linear/common-equity expressions do not need synthetic option metrics. `friction_refs` is an array. `valid_to` is string date-time or null. `authoritative_current` is boolean. Authority is hard-false.

- [ ] **Step 5: Run TAS/PGC tests**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2PayoffSchemaTests -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 3**

```bash
git add packages/contracts/schemas/vnext/tail-activation-snapshot.schema.json packages/contracts/schemas/vnext/payoff-geometry-context.schema.json tests/test_me2_c_x_separation.py
git commit -m "ME2: add tail activation and payoff geometry contracts"
```

---

### Task 4: Add one-way legacy projection and deterministic positive fixtures

**Files:**
- Create: `packages/contracts/schemas/vnext/legacy-convexity-projection.schema.json`
- Create: `docs/architecture/me2/fixtures/me2-engine-theses.json`
- Create: `docs/architecture/me2/fixtures/me2-position-passports.json`
- Create: `docs/architecture/me2/fixtures/compounding-mechanism-attachments.json`
- Create: `docs/architecture/me2/fixtures/convexity-mechanism-attachments.json`
- Create: `docs/architecture/me2/fixtures/tail-activation-snapshots.json`
- Create: `docs/architecture/me2/fixtures/payoff-geometry-contexts.json`
- Create: `docs/architecture/me2/fixtures/legacy-convexity-projections.json`
- Modify: `tests/test_me2_c_x_separation.py`

**Interfaces:**
- Consumes: ME1 target/thesis/passport fixtures plus Tasks 2–3 schemas.
- Produces: one valid C common-stock path, one C LEAPS/material-geometry path, one X long-call/dominant-geometry path, and one legacy read-only path.

- [ ] **Step 1: Add failing legacy-projection and fixture-presence tests**

Append:

```python
class ME2FixtureTests(unittest.TestCase):
    def test_legacy_projection_is_permanently_one_way(self):
        schema = json.loads((ROOT / "packages/contracts/schemas/vnext/legacy-convexity-projection.schema.json").read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(props["projection_only"], {"const": True})
        self.assertEqual(props["machine_authority"], {"const": False})
        self.assertEqual(props["write_back_prohibited"], {"const": True})
        self.assertEqual(props["engine_inference_prohibited"], {"const": True})

    def test_me2_fixture_contains_independent_x_thesis_and_c_leaps_passport(self):
        theses = json.loads((ME2 / "fixtures/me2-engine-theses.json").read_text(encoding="utf-8"))
        passports = json.loads((ME2 / "fixtures/me2-position-passports.json").read_text(encoding="utf-8"))
        self.assertEqual(theses[0]["engine_thesis_id"], "ET-NVDA-X-001")
        self.assertEqual(theses[0]["identity_core"]["primary_engine"], "ENG-X")
        ids = {p["position_passport_id"] for p in passports}
        self.assertEqual(ids, {"PP-NVDA-C-LEAPS-001", "PP-NVDA-X-001"})
```

- [ ] **Step 2: Run fixture tests and verify failure**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2FixtureTests -v
```

Expected: FAIL.

- [ ] **Step 3: Implement the legacy projection schema**

Use:

```json
{
  "$id":"urn:yuanli-invest:schema:vnext-legacy-convexity-projection:1.0.0",
  "title":"LegacyConvexityProjection",
  "type":"object",
  "additionalProperties":false,
  "required":[
    "legacy_convexity_projection_id","schema_version","source_schema_id","source_ref",
    "target_ref","legacy_underlying_structure","legacy_issuer_durability","legacy_labels",
    "projection_only","machine_authority","write_back_prohibited","engine_inference_prohibited"
  ],
  "properties": {
    "projection_only":{"const":true},
    "machine_authority":{"const":false},
    "write_back_prohibited":{"const":true},
    "engine_inference_prohibited":{"const":true}
  }
}
```

Set `source_schema_id` constant to `urn:yuanli-invest:schema:convexity-profile:1.0.0`. The three legacy payload fields are objects with free-form historical keys (`additionalProperties: true`) because this is a compatibility view, not new semantic authority.

- [ ] **Step 4: Create the ME2 X thesis fixture using the accepted EngineThesis schema unchanged**

`me2-engine-theses.json` contains exactly one new thesis:

```json
[
  {
    "engine_thesis_id":"ET-NVDA-X-001",
    "schema_version":"1.0.0",
    "target_id":"RT2-NVDA",
    "identity_core":{"primary_engine":"ENG-X","engine_authority_ref":null,"thesis_origin":"explicit_me2_convexity_shadow","opened_at":"2026-08-23T17:00:00+08:00"},
    "research_contract":{"source_of_return":["conditional_tail_activation","nonlinear_payoff_geometry"],"time_horizon":"18_month_tail_expression","thesis_statement":"A defined upside tail state may be expressed through paid nonlinear call geometry.","causal_mechanism":"tail state activation -> state contingent underlying move -> nonlinear option payoff net of convexity price","price_semantics":"premium_iv_skew_term_theta_and_breakeven"},
    "evidence":{"supporting_refs":["ME2-E-X-1"],"counter_refs":[],"capability_output_refs":[],"primitive_state_refs":["TAS-NVDA-X-001"],"recorded_at":"2026-08-23T17:00:00+08:00","known_as_of":"2026-08-23T16:59:00+08:00","knowledge_cutoff":"2026-08-23T16:59:00+08:00","replay_cutoff":"2026-08-23T16:59:00+08:00"},
    "falsification":{"falsifier_refs":["ME2-F-X-1"],"challenge_conditions":["tail activation fails or convexity becomes uneconomic"],"invalidation_reason":null,"triggered_falsifier_refs":[]},
    "lifecycle":{"status":"active","revision":1,"supersedes_revision":null,"revision_reason":"ME2 semantic fixture","as_of":"2026-08-23T16:59:00+08:00","valid_from":"2026-08-23T16:59:00+08:00","valid_to":null,"closed_at":null,"settlement_ref":null},
    "authority":{"capital_authority":false,"portfolio_weight_authority":false,"trading_authority":false,"live_execution_authority":false}
  }
]
```

- [ ] **Step 5: Create two ME2 Passport fixtures using PositionPassport v1 unchanged**

`PP-NVDA-C-LEAPS-001` references existing `ET-NVDA-C-001`, carries `primary_engine=ENG-C`, `expression_type=long_call_shadow`, `instrument_ref=NVDA-LEAPS-CALL-SHADOW`, and remains `eligible`. `PP-NVDA-X-001` references `ET-NVDA-X-001`, carries `primary_engine=ENG-X`, `expression_type=long_call_shadow`, `instrument_ref=NVDA-X-CALL-SHADOW`, and remains `eligible`. Both retain the accepted false authority object and `silent_migration_prohibited=true`, `governed_event_required=true`.

- [ ] **Step 6: Create one CMA and one XMA fixture**

CMA:

```json
{
  "attachment_id":"CMA-NVDA-C-001",
  "schema_version":"1.0.0",
  "engine_thesis_id":"ET-NVDA-C-001",
  "target_id":"RT2-NVDA",
  "primary_engine":"ENG-C",
  "primary_return_source":"economic_compounding",
  "economic_mechanism_refs":[
    {"role":"value_creation","ref":"ME2-MECH-NVDA-VALUE-POOL"},
    {"role":"value_capture","ref":"ME2-MECH-NVDA-VALUE-CAPTURE"},
    {"role":"owner_economics","ref":"ME2-MECH-NVDA-OWNER-ECONOMICS"},
    {"role":"reinvestment","ref":"ME2-MECH-NVDA-REINVESTMENT"}
  ],
  "economic_optionality_refs":["ME2-MECH-NVDA-ADJACENT-MARKET-OPTIONALITY"],
  "return_bridge":{"value_creation_or_control_ref":"ME2-MECH-NVDA-VALUE-POOL","value_capture_ref":"ME2-MECH-NVDA-VALUE-CAPTURE","owner_economics_ref":"ME2-MECH-NVDA-OWNER-ECONOMICS","reinvestment_ref":"ME2-MECH-NVDA-REINVESTMENT"},
  "price_semantics_refs":["ME2-PRICE-NVDA-C"],
  "dominance_test":{"linear_counterfactual":"survives","geometry_dependency":"auxiliary","tail_state_dependency":"low","expected_pnl_driver":"economic_compounding","rationale":"The thesis remains economic-compounding-led under linear common-equity exposure."}
}
```

Complete its evidence/falsification/lifecycle/authority fields according to Task 2 schema with `authoritative_current=true` and all authorities false.

XMA:

```json
{
  "attachment_id":"XMA-NVDA-X-001",
  "schema_version":"1.0.0",
  "engine_thesis_id":"ET-NVDA-X-001",
  "target_id":"RT2-NVDA",
  "primary_engine":"ENG-X",
  "primary_return_source":"nonlinear_payoff_geometry",
  "tail_activation_refs":["TAS-NVDA-X-001"],
  "convexity_price_refs":["ME2-PRICE-NVDA-X-IV","ME2-PRICE-NVDA-X-SKEW"],
  "underlying_state_refs":["ME2-UNDERLYING-NVDA-AI-STATE"],
  "state_to_payoff_hypothesis":"An activated upside tail combined with paid call geometry produces the dominant expected P&L mapping.",
  "dominance_test":{"linear_counterfactual":"fails","geometry_dependency":"dominant","tail_state_dependency":"dominant","expected_pnl_driver":"nonlinear_payoff_geometry","rationale":"The thesis loses its defining payoff objective if replaced by linear exposure."}
}
```

Complete evidence/falsification/lifecycle/authority fields likewise.

- [ ] **Step 7: Create TAS and PGC fixtures**

TAS uses `TAS-NVDA-X-001`, `activation_state=activating`, `tail_side=upside`, `probability_semantics=uncalibrated_state`, no numeric probability, and `authoritative_current=true`.

PGCs contain exactly two current contexts:

```json
[
  {
    "payoff_geometry_context_id":"PGC-NVDA-C-LEAPS-001",
    "schema_version":"1.0.0",
    "position_passport_id":"PP-NVDA-C-LEAPS-001",
    "engine_thesis_id":"ET-NVDA-C-001",
    "instrument_ref":"NVDA-LEAPS-CALL-SHADOW",
    "geometry_family":"convex",
    "geometry_dependency":"material",
    "authoritative_current":true
  },
  {
    "payoff_geometry_context_id":"PGC-NVDA-X-001",
    "schema_version":"1.0.0",
    "position_passport_id":"PP-NVDA-X-001",
    "engine_thesis_id":"ET-NVDA-X-001",
    "instrument_ref":"NVDA-X-CALL-SHADOW",
    "geometry_family":"convex",
    "geometry_dependency":"dominant",
    "authoritative_current":true
  }
]
```

Fill all remaining required PGC fields with explicit shadow semantics and null refs where a metric is intentionally unavailable; do not invent live market values.

- [ ] **Step 8: Create one legacy projection fixture**

Use source ref `LEGACY-CONVEXITY-NVDA-001`, target `RT2-NVDA`, map historical right-tail semantics under `legacy_underlying_structure`, issuer fragility under `legacy_issuer_durability`, old state labels under `legacy_labels`, and set all four projection constants exactly.

- [ ] **Step 9: Run fixture tests**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2FixtureTests -v
```

Expected: PASS.

- [ ] **Step 10: Commit Task 4**

```bash
git add packages/contracts/schemas/vnext/legacy-convexity-projection.schema.json docs/architecture/me2/fixtures tests/test_me2_c_x_separation.py
git commit -m "ME2: add one-way legacy projection and positive fixtures"
```

---

### Task 5: Implement fail-closed ME2 relational validator

**Files:**
- Create: `scripts/validate_me2_c_x_separation.py`
- Modify: `tests/test_me2_c_x_separation.py`

**Interfaces:**
- Consumes: ME1 target/thesis/passport fixtures, ME2 schemas/fixtures/successor map/hard-negative matrix.
- Produces: `validate_bundle(bundle: dict) -> None`, deterministic `ME2ValidationError.code`, CLI PASS/FAIL, and validation layers V0–V10.

- [ ] **Step 1: Add failing validator smoke tests**

Append:

```python
class ME2ValidatorSmokeTests(unittest.TestCase):
    def test_reference_bundle_validates(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle, validate_bundle
        validate_bundle(load_fixture_bundle())

    def test_validator_exposes_deterministic_error_codes(self):
        from scripts.validate_me2_c_x_separation import ME2ValidationError
        err = ME2ValidationError("ME2_E_TEST", "test")
        self.assertEqual(err.code, "ME2_E_TEST")
```

- [ ] **Step 2: Run and verify import failure**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2ValidatorSmokeTests -v
```

Expected: FAIL because validator module is absent.

- [ ] **Step 3: Implement validator scaffold and historical blob hashing**

Start with:

```python
#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "packages" / "contracts" / "schemas" / "vnext"
ME1 = ROOT / "docs" / "architecture" / "me1"
ME2 = ROOT / "docs" / "architecture" / "me2"
FIXTURES = ME2 / "fixtures"


class ME2ValidationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise ME2ValidationError(code, message)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def parse_dt(value: str):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
```

Implement `validate_historical_non_regression()` against the six literal blob SHAs in Task 1. Failure code: `ME2_E_HISTORICAL_DRIFT`.

- [ ] **Step 4: Implement schema shape validation and bundle loader**

Define schema map:

```python
SCHEMAS = {
    "cma": VNEXT / "compounding-mechanism-attachment.schema.json",
    "xma": VNEXT / "convexity-mechanism-attachment.schema.json",
    "tas": VNEXT / "tail-activation-snapshot.schema.json",
    "pgc": VNEXT / "payoff-geometry-context.schema.json",
    "legacy": VNEXT / "legacy-convexity-projection.schema.json",
    "engine_thesis": VNEXT / "engine-thesis.schema.json",
    "position_passport": VNEXT / "position-passport.schema.json"
}
```

`load_fixture_bundle()` must combine:
- ME1 `research-targets-v2.json`;
- ME1 `engine-theses.json` plus ME2 `me2-engine-theses.json`;
- ME1 `position-passports.json` plus ME2 `me2-position-passports.json`;
- all five ME2 contract fixture lists;
- successor map and hard-negative matrix.

`validate_schema_shapes(bundle)` must run `Draft202012Validator(..., format_checker=FormatChecker())` against every instance. On error, raise `ME2_E_SCHEMA` with label and first eight JSON Schema errors.

- [ ] **Step 5: Implement V1–V3 identity/reference/cardinality validation**

Create these functions and exact rules:

```python
validate_identity_integrity(bundle)
validate_reference_integrity(bundle)
validate_attachment_cardinality(bundle)
```

Rules:
- all CMA/XMA/TAS/PGC/LCP IDs unique;
- every attachment resolves a thesis and target;
- attachment target equals thesis target;
- CMA thesis engine must be `ENG-C` (`ME2_E_C_ENGINE_MISMATCH`);
- XMA thesis engine must be `ENG-X` (`ME2_E_X_ENGINE_MISMATCH`);
- every PGC resolves a PositionPassport and EngineThesis;
- PGC `instrument_ref` equals referenced Passport `expression.instrument_ref` (`ME2_E_PGC_INSTRUMENT_MISMATCH`);
- qualified/active C thesis has exactly one authoritative-current CMA (`ME2_E_C_ATTACHMENT_REQUIRED`);
- qualified/active X thesis has exactly one authoritative-current XMA (`ME2_E_X_ATTACHMENT_REQUIRED`);
- each authoritative-current XMA resolves at least one TAS and exactly one referenced TAS has `authoritative_current=true` (`ME2_E_X_TAIL_REQUIRED`);
- each eligible/active X Passport has exactly one current PGC (`ME2_E_X_PGC_REQUIRED`).

- [ ] **Step 6: Implement V4–V5 C/X separation and dominance law**

Create:

```python
PROHIBITED_X_IDENTITY_TOKENS = {
    "large_tam", "network_effect", "network_effects", "winner_take_most",
    "historical_20x", "positive_skew", "market_expansion", "platform_optionality",
    "value_capture", "reinvestment_runway", "legacy_convexity_state", "legacy_xs"
}


def validate_c_x_mechanism_separation(bundle): ...
def validate_dominance(bundle): ...
```

`validate_c_x_mechanism_separation` recursively scans XMA top-level field names and any `identity_claims` field present in negative test mutations; if an X identity is asserted solely by one of the prohibited tokens, raise `ME2_E_X_UNDERLYING_LEAKAGE`. It must also reject `automatic_engine_inference=true` anywhere in ME2 successor objects with `ME2_E_AUTO_ENGINE_INFERENCE`.

`validate_dominance` rules:
- CMA `expected_pnl_driver` must equal `economic_compounding`;
- CMA `geometry_dependency` may be `auxiliary|material`, never `dominant`; dominant -> `ME2_E_C_GEOMETRY_DOMINANT`;
- XMA `expected_pnl_driver` must equal `nonlinear_payoff_geometry`;
- XMA `geometry_dependency` must be `dominant`; otherwise `ME2_E_X_GEOMETRY_NOT_DOMINANT`;
- primary engine is read only from EngineThesis and cannot be inferred from instrument type.

- [ ] **Step 7: Implement V6 Tail Activation PIT/calibration law**

Create `validate_tail_activation(bundle)` with:
- `known_as_of <= knowledge_cutoff <= as_of` when all are timestamps; violation -> `ME2_E_TAS_FUTURE_KNOWLEDGE`;
- if `estimated_probability` exists, require `probability_semantics=calibrated_probability`, non-empty `probability_definition`, `base_rate_ref`, `calibration_ref`, and `horizon`; missing -> `ME2_E_TAS_UNCALIBRATED_PROBABILITY`;
- no numeric probability may be synthesized from `activation_state`.

- [ ] **Step 8: Implement V7 Position/Geometry law**

Create `validate_payoff_geometry(bundle)`:
- PGC must match Passport thesis ID and instrument ref;
- C LEAPS with `geometry_dependency=material` passes;
- option instrument does not change a C thesis into X;
- X Passport requires dominant geometry;
- if a mutated bundle sets `static_linear_exposure=true` plus `x_identity_basis` drawn only from large upside/positive skew/right-tail narrative, raise `ME2_E_STATIC_LINEAR_X_NARRATIVE_ONLY`.

- [ ] **Step 9: Implement V8 legacy one-way compatibility**

Create `validate_legacy_compatibility(bundle)` requiring on every LCP:

```python
projection["projection_only"] is True
projection["machine_authority"] is False
projection["write_back_prohibited"] is True
projection["engine_inference_prohibited"] is True
```

Any violation -> `ME2_E_LEGACY_AUTHORITY_LEAK`. Any field `derived_engine`, `auto_engine_thesis_creation_authorized`, or `write_back_requested` with truthy value -> same error.

- [ ] **Step 10: Implement V9 authority firewall**

Create `validate_authority(bundle)` that recursively finds every `authority` object on ME2 successor contracts and asserts every value is `False`; failure -> `ME2_E_AUTHORITY_LEAK`. Also require `ME2-STATE.json` authorities `alpha_runtime`, `historical_performance_claim`, `capability_promotion`, `new_engine_creation`, `portfolio`, `position_sizing`, `trading`, `live_execution`, `constitution_mutation`, `runtime_cutover`, `ME3`, `ME4`, and `ME5` are false.

- [ ] **Step 11: Implement V10 matrix integrity and top-level orchestration**

Create `validate_matrix_integrity(bundle)` requiring exactly 16 unique HN IDs and 5 unique HP IDs, all expected results correct.

Top-level:

```python
def validate_bundle(bundle: dict) -> None:
    validate_historical_non_regression()
    validate_schema_shapes(bundle)
    validate_identity_integrity(bundle)
    validate_reference_integrity(bundle)
    validate_attachment_cardinality(bundle)
    validate_c_x_mechanism_separation(bundle)
    validate_dominance(bundle)
    validate_tail_activation(bundle)
    validate_payoff_geometry(bundle)
    validate_legacy_compatibility(bundle)
    validate_authority(bundle)
    validate_matrix_integrity(bundle)


def main() -> int:
    validate_bundle(load_fixture_bundle())
    print("ME2 C-X Economic Mechanism Separation validation: PASS")
    return 0
```

CLI exception path prints the validation error and exits `1`.

- [ ] **Step 12: Run smoke tests and validator CLI**

Run:

```bash
python -m unittest tests.test_me2_c_x_separation.ME2ValidatorSmokeTests -v
python scripts/validate_me2_c_x_separation.py
```

Expected: PASS and `ME2 C-X Economic Mechanism Separation validation: PASS`.

- [ ] **Step 13: Commit Task 5**

```bash
git add scripts/validate_me2_c_x_separation.py tests/test_me2_c_x_separation.py
git commit -m "ME2: add fail-closed C-X relational validator"
```

---

### Task 6: Encode all hard negatives and hard positives as executable tests

**Files:**
- Modify: `tests/test_me2_c_x_separation.py`

**Interfaces:**
- Consumes: `load_fixture_bundle()`, `validate_bundle()`, `ME2ValidationError`.
- Produces: executable proof for HN-01..HN-16 and HP-01..HP-05.

- [ ] **Step 1: Add a mutation helper and error-code assertion helper**

```python
import copy


def assert_me2_error(testcase, bundle, expected_code):
    from scripts.validate_me2_c_x_separation import ME2ValidationError, validate_bundle
    with testcase.assertRaises(ME2ValidationError) as ctx:
        validate_bundle(bundle)
    testcase.assertEqual(ctx.exception.code, expected_code)
```

- [ ] **Step 2: Add HN-01..HN-06 underlying/instrument inference tests**

Use a fresh `copy.deepcopy(load_fixture_bundle())` per test. Mutate the XMA with `identity_claims=["large_tam"]`, `["network_effect"]`, `["historical_20x"]`, or a legacy projection with `derived_engine="ENG-X"`; mutate an X object with `identity_claims=["legacy_xs"]`; mutate the C LEAPS Passport with `automatic_engine_inference=true`. Assert respectively `ME2_E_X_UNDERLYING_LEAKAGE`, `ME2_E_LEGACY_AUTHORITY_LEAK`, or `ME2_E_AUTO_ENGINE_INFERENCE` as appropriate.

- [ ] **Step 3: Add HN-07..HN-11 contract/cardinality/dominance tests**

Mutations and expected codes:

```text
HN-07 remove XMA.tail_activation_refs -> ME2_E_SCHEMA or ME2_E_X_TAIL_REQUIRED
HN-08 remove X PGC from bundle -> ME2_E_X_PGC_REQUIRED
HN-09 add estimated_probability=0.72 while calibration fields are absent -> ME2_E_SCHEMA or ME2_E_TAS_UNCALIBRATED_PROBABILITY
HN-10 set CMA.dominance_test.geometry_dependency=dominant -> ME2_E_C_GEOMETRY_DOMINANT
HN-11 set XMA.dominance_test.geometry_dependency=material -> ME2_E_X_GEOMETRY_NOT_DOMINANT
```

Where JSON Schema catches a malformed object before relational validation, assert `ME2_E_SCHEMA`; otherwise assert the domain-specific code. Do not weaken schemas merely to force relational error codes.

- [ ] **Step 4: Add HN-12..HN-16 governance tests**

Mutations:
- HN-12 set XMA `identity_claims=["real_optionality"]` and add `real_optionality` to prohibited X identity tokens -> `ME2_E_X_UNDERLYING_LEAKAGE`;
- HN-13 set successor CAP-XS future authority true -> `ME2_E_AUTO_ENGINE_INFERENCE` or dedicated `ME2_E_CAP_XS_SUCCESSOR_AUTHORITY`; implement the dedicated code if testing successor policy directly;
- HN-14 set LCP `write_back_prohibited=false` -> `ME2_E_SCHEMA` or `ME2_E_LEGACY_AUTHORITY_LEAK`;
- HN-15 create a thesis history mutation with the same `engine_thesis_id=ET-NVDA-C-001` but `primary_engine=ENG-X`; add `validate_no_silent_migration()` to the validator if not already present and require `ME2_E_SILENT_ENGINE_MIGRATION`;
- HN-16 set any ME2 successor authority `trading=true` -> `ME2_E_SCHEMA` or `ME2_E_AUTHORITY_LEAK`.

For HN-15, `validate_no_silent_migration()` must compare `thesis_histories` entries exactly as ME1 does and prohibit changes to `target_id`, `primary_engine`, `thesis_origin`, or `opened_at` inside one thesis identity.

- [ ] **Step 5: Add HP-01..HP-05 passing tests**

Write five explicit tests:

```python
class ME2HardPositiveTests(unittest.TestCase):
    def test_hp01_common_stock_c_plus_cma_passes(self): ...
    def test_hp02_leaps_c_with_material_geometry_passes(self): ...
    def test_hp03_long_call_x_with_tail_and_dominant_geometry_passes(self): ...
    def test_hp04_legacy_projection_read_only_passes(self): ...
    def test_hp05_same_target_can_hold_independent_c_and_x_theses(self): ...
```

Each test calls `validate_bundle()` on a bundle retaining the relevant positive path. HP-05 asserts `ET-NVDA-C-001` and `ET-NVDA-X-001` share `RT2-NVDA` but retain distinct primary engines and IDs.

- [ ] **Step 6: Run the complete ME2 unit file**

```bash
python -m unittest tests.test_me2_c_x_separation -v
```

Expected: all tests PASS; the output must visibly contain all `test_hn01`..`test_hn16` and `test_hp01`..`test_hp05` methods.

- [ ] **Step 7: Commit Task 6**

```bash
git add scripts/validate_me2_c_x_separation.py tests/test_me2_c_x_separation.py
git commit -m "ME2: enforce hard-negative and hard-positive matrix"
```

---

### Task 7: Integrate ME2 into repository-gates without changing upstream semantics

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/architecture/me2/ME2-STATE.json`
- Modify: `docs/architecture/me2/ME2-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `tests/test_me2_c_x_separation.py`

**Interfaces:**
- Consumes: passing local validator/test suite.
- Produces: repository-level ME2 gate and a machine-qualified-but-not-human-accepted candidate state.

- [ ] **Step 1: Add a failing CI-order test**

Append:

```python
class ME2CIGateTests(unittest.TestCase):
    def test_ci_runs_me2_after_me1_and_before_yim0(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        me1 = ci.index("python scripts/validate_me1_state_object_model.py")
        me2 = ci.index("python scripts/validate_me2_c_x_separation.py")
        yim0 = ci.index("python scripts/validate_yim0_methodology_projection.py")
        self.assertLess(me1, me2)
        self.assertLess(me2, yim0)
```

- [ ] **Step 2: Run and verify failure because CI does not yet call ME2**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2CIGateTests -v
```

Expected: FAIL with substring not found.

- [ ] **Step 3: Add exactly one ME2 command to the existing contracts job**

In `.github/workflows/ci.yml`, immediately after:

```yaml
- run: python scripts/validate_me1_state_object_model.py
```

insert:

```yaml
- run: python scripts/validate_me2_c_x_separation.py
```

Leave all other workflow steps unchanged.

- [ ] **Step 4: Run ME2, full unittest, repository validator, and governance checks locally**

Run in this order:

```bash
python scripts/validate_me2_c_x_separation.py
python -m unittest tests.test_me2_c_x_separation -v
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/validate_repository.py
python scripts/check_governance.py
python scripts/build_manifest.py --check
```

Expected: every command exits 0. If `build_manifest.py --check` reports expected manifest drift caused by the new files, update the repository manifest using the repository's established `python scripts/build_manifest.py` command, then rerun `--check`; include the generated manifest change in this task only. Do not hand-edit manifest hashes.

- [ ] **Step 5: Transition candidate state only after local full green**

Change only these state values:

```json
"status": "machine_qualified_ready_for_human_review",
"next_gate": "ME2_HUMAN_REVIEW"
```

Do not set any acceptance or merge authority flag.

Update the review card header to `Status: machine_qualified_ready_for_human_review`, leave D1–D18 as unaccepted review dimensions, and add a qualification block listing the exact candidate commit SHA only after the commit exists. Because the commit SHA cannot be known before committing, first commit the candidate changes without the SHA annotation; the exact-head review annotation belongs to the subsequent Human Review/acceptance-record phase, not this implementation plan.

- [ ] **Step 6: Run CI-order test and full local gates again**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2CIGateTests -v
python scripts/validate_me2_c_x_separation.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/check_governance.py
python scripts/build_manifest.py --check
```

Expected: PASS.

- [ ] **Step 7: Commit Task 7**

```bash
git add .github/workflows/ci.yml docs/architecture/me2 tests/test_me2_c_x_separation.py MANIFEST.json
git commit -m "ME2: wire C-X separation into repository gates"
```

If the repository manifest path is not `MANIFEST.json`, stage only the actual generated manifest file reported by `scripts/build_manifest.py`; never create a second manifest.

---

### Task 8: Verify exact candidate head and stop at ME2 Human Review

**Files:**
- No semantic implementation files should change in this task.
- Read: branch diff, CI workflow run, ME2 state/review card.

**Interfaces:**
- Consumes: committed ME2 candidate.
- Produces: exact-head verification evidence and Human Review handoff; no acceptance receipt, merge, or ME3 work.

- [ ] **Step 1: Verify branch diff is scoped to the plan**

Run:

```bash
git diff --name-status main...HEAD
```

Expected files are only:

```text
docs/architecture/me2/**
packages/contracts/schemas/vnext/compounding-mechanism-attachment.schema.json
packages/contracts/schemas/vnext/convexity-mechanism-attachment.schema.json
packages/contracts/schemas/vnext/tail-activation-snapshot.schema.json
packages/contracts/schemas/vnext/payoff-geometry-context.schema.json
packages/contracts/schemas/vnext/legacy-convexity-projection.schema.json
scripts/validate_me2_c_x_separation.py
tests/test_me2_c_x_separation.py
.github/workflows/ci.yml
<existing generated manifest path, only if required>
```

The accepted ME2 design and implementation-plan files may also be present because they were committed earlier on the same branch. No historical CAP-XS/Extreme Engine/ConvexityProfile/EngineThesis/PositionPassport file may show as modified.

- [ ] **Step 2: Re-run local exact-head qualification**

```bash
python scripts/validate_me2_c_x_separation.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/validate_repository.py
python scripts/check_governance.py
python scripts/build_manifest.py --check
```

Expected: all PASS.

- [ ] **Step 3: Push/observe GitHub Actions using the normal branch/PR workflow**

The `repository-gates` workflow must report both `contracts` and `governance` SUCCESS for the exact candidate head. Record the run ID and exact head in the conversational handoff; do not write a Human Acceptance receipt yet.

- [ ] **Step 4: Present the 18/18 Human Review dimensions without pre-answering them**

Surface D1–D18 from `ME2-HUMAN-REVIEW-CARD-v0.1.md`, the exact head, local validation summary, and GitHub Actions run status. The only possible next Human decision token is:

```text
ACCEPT_ME2_C_X_ECONOMIC_MECHANISM_SEPARATION
```

- [ ] **Step 5: Stop**

Do not create an acceptance receipt, do not merge, do not set `ME2_COMPLETE`, do not update Canon to authorize ME3, and do not begin ME3. Those are separate post-Human-acceptance and merge-authorization phases.

---

## Plan Self-Check Matrix

This matrix is a planning aid, not a new authority layer.

| Spec requirement | Implemented by |
|---|---|
| Eight C/X semantic invariants | Tasks 1, 5, 6 |
| Stable core + sidecars | Tasks 2–5 |
| CMA | Tasks 2, 4, 5 |
| XMA | Tasks 2, 4, 5 |
| TailActivationSnapshot | Tasks 3–6 |
| PayoffGeometryContext belongs to Position | Tasks 3–6 |
| LegacyConvexityProjection one-way | Tasks 4–6 |
| CAP-XS historical preservation / future supersession | Tasks 1, 5, 6 |
| StructuralRightTailProfile never canonicalized | Tasks 1, 5 |
| Old R2.3-B2 CAP-XS execution path superseded | Tasks 1, 5 |
| Historical blob non-regression | Tasks 1, 5, 8 |
| Dominance test | Tasks 2, 4–6 |
| Instrument != Engine | Tasks 4–6 |
| No Silent Thesis Migration | Tasks 5–6 |
| PIT and calibration discipline | Tasks 3, 5, 6 |
| 16 hard negatives | Tasks 1, 6 |
| 5 hard positives | Tasks 1, 4, 6 |
| Authority firewall | Tasks 1–7 |
| CI integration | Task 7 |
| 18/18 Human Review gate | Tasks 1, 7, 8 |
| No ME3/ME4/ME5 implementation | Global Constraints, Tasks 1, 7, 8 |
| No alpha/portfolio/trading implementation | Global Constraints, Tasks 1, 2–7 |
