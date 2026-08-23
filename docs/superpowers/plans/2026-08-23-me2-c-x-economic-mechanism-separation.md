# ME2 | C–X Economic Mechanism Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the accepted ME2 design into machine-checkable C/X successor contracts that separate underlying economic right-tail mechanisms from portfolio payoff convexity, preserve historical X/Convexity/CAP-XS ledger identities, and fail closed on semantic leakage without granting alpha, portfolio, trading, or ME3–ME5 authority.

**Architecture:** Keep the accepted ME1 `ResearchTarget -> EngineThesis -> PositionPassport -> BookState@PIT` object graph unchanged. Add five focused sidecar/compatibility schemas, ME2-only fixtures, and one fail-closed relational validator. ME2 is additive successor architecture: accepted `EngineThesis`, `PositionPassport`, historical `ConvexityProfile`, `CAP-XS-01`, Extreme Engine, and the old R2.3-B2 plan remain immutable.

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
- Do not modify `docs/superpowers/plans/2026-08-21-r2-3b2-p0-reference-implementation.md`; supersede only its future CAP-XS execution path through ME2 successor metadata.
- A qualified/active `ENG-C` Thesis requires exactly one authoritative-current `CompoundingMechanismAttachment`.
- A qualified/active `ENG-X` Thesis requires exactly one authoritative-current `ConvexityMechanismAttachment`.
- An authoritative-current XMA requires at least one referenced `TailActivationSnapshot`, with exactly one referenced TAS marked `authoritative_current=true`.
- An eligible/active X `PositionPassport` requires exactly one authoritative-current `PayoffGeometryContext`.
- C/R Passports may carry PGCs; a valid C thesis requires `geometry_dependency != dominant`.
- A valid X thesis requires `nonlinear_payoff_geometry` in `EngineThesis.research_contract.source_of_return`, `expected_pnl_driver = nonlinear_payoff_geometry`, and `geometry_dependency = dominant`.
- Numeric tail probability is forbidden without `probability_definition`, `horizon`, `base_rate_ref`, and `calibration_ref`.
- Legacy projection is permanently one-way, non-authoritative, write-back-prohibited, and engine-inference-prohibited.
- Static linear exposure cannot qualify as X from upside narrative, historical multibagger status, positive skew, TAM, moat, network effect, real optionality, or legacy Xs/convexity labels alone.
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

No other semantic implementation file is required for the ME2 candidate.

---

### Task 1: Freeze candidate authority, successor lineage, and Human gates

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
        for key in ("alpha_runtime", "portfolio", "position_sizing", "trading", "live_execution", "ME3", "ME4", "ME5"):
            self.assertFalse(state["implementation_authorities"][key])

    def test_successor_map_supersedes_cap_xs_future_execution_without_rewriting_history(self):
        successor = json.loads((ME2 / "ME2-SEMANTIC-SUCCESSOR-MAP-v0.1.json").read_text(encoding="utf-8"))
        xs = successor["historical_identities"]["CAP-XS-01"]
        self.assertTrue(xs["historical_contract_authority"])
        self.assertFalse(xs["redefined_in_place"])
        self.assertFalse(xs["future_reference_implementation_authority"])
        self.assertEqual(xs["successor_policy"], "typed_route_split_by_causal_mechanism")
        old_plan = successor["superseded_future_paths"]["R2_3B2_CAP_XS_01"]
        self.assertEqual(old_plan["status"], "superseded_before_execution_by_ME2")
        self.assertTrue(old_plan["do_not_execute"])

    def test_review_contract_has_exactly_18_dimensions(self):
        text = (ME2 / "ME2-HUMAN-REVIEW-CARD-v0.1.md").read_text(encoding="utf-8")
        for index in range(1, 19):
            self.assertIn(f"D{index} |", text)
        self.assertNotIn("D19 |", text)
        self.assertIn("Acceptance does not imply merge.", text)
```

- [ ] **Step 2: Run tests and verify failure**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2GovernanceTests -v
```

Expected: FAIL because `docs/architecture/me2/` is absent.

- [ ] **Step 3: Create `ME2-STATE.json`**

```json
{
  "schema_version":"0.1.0",
  "stage":"ME2_C_X_ECONOMIC_MECHANISM_SEPARATION",
  "status":"candidate_started",
  "design_acceptance":"ACCEPT_ME2_WRITTEN_SPEC",
  "program_order":["ME2","ME3","ME4","ME5"],
  "implementation_authorities":{
    "semantic_successor_contracts":true,
    "candidate_schema_validation":true,
    "alpha_runtime":false,
    "historical_performance_claim":false,
    "capability_promotion":false,
    "new_engine_creation":false,
    "portfolio":false,
    "position_sizing":false,
    "trading":false,
    "live_execution":false,
    "constitution_mutation":false,
    "runtime_cutover":false,
    "ME3":false,
    "ME4":false,
    "ME5":false
  },
  "human_review_dimensions":18,
  "next_gate":"ME2_MACHINE_QUALIFICATION"
}
```

- [ ] **Step 4: Create `ME2-SEMANTIC-SUCCESSOR-MAP-v0.1.json` with literal historical locks**

Use these immutable artifacts and SHAs:

```json
{
  "stage":"ME2_C_X_ECONOMIC_MECHANISM_SEPARATION",
  "policy":"semantic_successors_never_mutate_historical_receipts_or_contracts",
  "historical_artifacts":{
    "convexity_profile_v1":{"path":"packages/contracts/schemas/convexity-profile.schema.json","blob_sha":"6c150e03ae3163517153bdd9683cbd083a675198","redefined_in_place":false,"future_write_authority":false},
    "cap_xs_01":{"path":"docs/architecture/r2_3b1/CAP-XS-01-SPEC-v0.1.json","blob_sha":"862ff407d39171283884d920e25641ffdddabb0b","redefined_in_place":false},
    "extreme_engine_v0_1":{"path":"docs/methodology/extreme-engine-v0.1.md","blob_sha":"f9dd55a855b4f64f1f606487e24a0536af80b61e","redefined_in_place":false},
    "r2_3b2_plan":{"path":"docs/superpowers/plans/2026-08-21-r2-3b2-p0-reference-implementation.md","blob_sha":"408a9e76a102f87eaab19c14cf6303105588e54f","redefined_in_place":false},
    "engine_thesis_v1":{"path":"packages/contracts/schemas/vnext/engine-thesis.schema.json","blob_sha":"06102eeffce467c8d6707a4fcadcc4f652811d79","redefined_in_place":false},
    "position_passport_v1":{"path":"packages/contracts/schemas/vnext/position-passport.schema.json","blob_sha":"22e73c090b84ff88d809d70d638a2d9f6ce31697","redefined_in_place":false}
  },
  "historical_identities":{
    "CAP-XS-01":{"historical_contract_authority":true,"historical_meaning":"Structural Asymmetry Source Mapper","redefined_in_place":false,"future_reference_implementation_authority":false,"future_canonical_output_authority":false,"successor_policy":"typed_route_split_by_causal_mechanism"},
    "StructuralRightTailProfile":{"historical_status":"candidate_only_never_canonical_schema","successor_status":"superseded_before_canonical_schema_creation","schema_creation_prohibited_under_ME2":true},
    "TailActivationSnapshot":{"historical_status":"candidate_object","successor_status":"explicit_ME2_successor_contract_candidate"},
    "PayoffConvexityContext":{"historical_status":"candidate_object","successor_identity":"PayoffGeometryContext"}
  },
  "superseded_future_paths":{
    "R2_3B2_CAP_XS_01":{"path":"docs/superpowers/plans/2026-08-21-r2-3b2-p0-reference-implementation.md","status":"superseded_before_execution_by_ME2","do_not_execute":true,"replacement":"ME2_typed_successor_contracts_plus_future_capability_specific_governance"}
  },
  "next_me_stage_authorized":false
}
```

- [ ] **Step 5: Create `ME2-HARD-NEGATIVE-MATRIX-v0.1.json`**

```json
{
  "hard_negatives":[
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
  "hard_positives":[
    {"id":"HP-01","proposition":"NVDA_common_stock_C_plus_CMA","expected":"PASS"},
    {"id":"HP-02","proposition":"NVDA_LEAPS_C_plus_CMA_plus_PGC_material","expected":"PASS"},
    {"id":"HP-03","proposition":"long_call_X_plus_XMA_plus_TAS_plus_PGC_dominant","expected":"PASS"},
    {"id":"HP-04","proposition":"legacy_convexity_profile_read_only_projection","expected":"PASS"},
    {"id":"HP-05","proposition":"same_target_has_independent_C_and_X_theses","expected":"PASS"}
  ]
}
```

- [ ] **Step 6: Create authority note and Human Review card**

The authority note must contain the eight ME2 invariants, Stable Core + Sidecar architecture, five candidate contracts, CAP-XS/Convexity historical preservation, no runtime/portfolio authority, and strict ME2→ME3 serial gate.

The review card starts `Status: candidate_not_yet_human_reviewed`, contains future token `ACCEPT_ME2_C_X_ECONOMIC_MECHANISM_SEPARATION`, states `Acceptance does not imply merge.`, and contains exactly:

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

- [ ] **Step 7: Run Task 1 tests**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2GovernanceTests -v
```

Expected: PASS.

- [ ] **Step 8: Commit**

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
- Consumes: accepted EngineThesis v1 identity and Genesis engine IDs.
- Produces: local `CMA-*` and `XMA-*` schemas.

- [ ] **Step 1: Write failing schema tests**

```python
class ME2AttachmentSchemaTests(unittest.TestCase):
    def test_cma_is_eng_c_sidecar(self):
        schema = json.loads((ROOT / "packages/contracts/schemas/vnext/compounding-mechanism-attachment.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "urn:yuanli-invest:schema:vnext-compounding-mechanism-attachment:1.0.0")
        self.assertEqual(schema["properties"]["primary_engine"], {"const":"ENG-C"})
        self.assertEqual(schema["properties"]["primary_return_source"], {"const":"economic_compounding"})
        self.assertNotIn("economic_asymmetry_score", schema["properties"])
        self.assertNotIn("convexity_state", schema["properties"])

    def test_xma_is_eng_x_payoff_sidecar(self):
        schema = json.loads((ROOT / "packages/contracts/schemas/vnext/convexity-mechanism-attachment.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "urn:yuanli-invest:schema:vnext-convexity-mechanism-attachment:1.0.0")
        self.assertEqual(schema["properties"]["primary_engine"], {"const":"ENG-X"})
        self.assertEqual(schema["properties"]["primary_return_source"], {"const":"nonlinear_payoff_geometry"})
        for name in ("network_effects","market_expansion","winner_take_most","value_capture"):
            self.assertNotIn(name, schema["properties"])
```

- [ ] **Step 2: Run and verify missing-schema failure**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2AttachmentSchemaTests -v
```

Expected: FAIL.

- [ ] **Step 3: Implement CMA schema**

Use Draft 2020-12, `type=object`, `additionalProperties=false`, `$id=urn:yuanli-invest:schema:vnext-compounding-mechanism-attachment:1.0.0`, and require:

```json
["attachment_id","schema_version","engine_thesis_id","target_id","primary_engine","primary_return_source","economic_mechanism_refs","economic_optionality_refs","return_bridge","price_semantics_refs","dominance_test","evidence","falsification","lifecycle","authority"]
```

Exact identity/constants:

```json
"attachment_id":{"type":"string","pattern":"^CMA-[A-Z0-9-]+$"},
"schema_version":{"const":"1.0.0"},
"primary_engine":{"const":"ENG-C"},
"primary_return_source":{"const":"economic_compounding"}
```

`economic_mechanism_refs` is a non-empty array of unique objects requiring `role` and `ref`; role enum is `value_pool|value_creation|value_capture|owner_economics|reinvestment|durability|other_governed_mechanism`. `economic_optionality_refs` is a unique string array. `return_bridge` requires `value_creation_or_control_ref`, `value_capture_ref`, `owner_economics_ref`, `reinvestment_ref`. `price_semantics_refs` is a unique string array.

`dominance_test` requires:

```json
{
  "linear_counterfactual":{"enum":["survives","materially_degraded","fails","unknown"]},
  "geometry_dependency":{"enum":["auxiliary","material","dominant"]},
  "tail_state_dependency":{"enum":["low","material","dominant","unknown"]},
  "expected_pnl_driver":{"const":"economic_compounding"},
  "rationale":{"type":"string","minLength":1}
}
```

`evidence` requires string arrays `supporting_refs`, `counter_refs`, plus date-times `known_as_of`, `knowledge_cutoff`. `falsification` requires non-empty `falsifier_refs`. `lifecycle` requires `status`, `as_of`, `valid_from`, `valid_to`, `authoritative_current`; status enum is `draft|researching|qualified|active|challenged|invalidated|closed`. `valid_to` is date-time or null. `authority` requires hard-false keys `capital_authority`, `portfolio_weight_authority`, `position_sizing_authority`, `trading_authority`, `live_execution_authority`, `alpha_runtime_authority`, `capability_promotion_authority`, `new_engine_creation_authority`.

- [ ] **Step 4: Implement XMA schema**

Use `$id=urn:yuanli-invest:schema:vnext-convexity-mechanism-attachment:1.0.0`, `additionalProperties=false`, and require:

```json
["attachment_id","schema_version","engine_thesis_id","target_id","primary_engine","primary_return_source","tail_activation_refs","convexity_price_refs","underlying_state_refs","state_to_payoff_hypothesis","dominance_test","evidence","falsification","lifecycle","authority"]
```

Exact constants:

```json
"attachment_id":{"type":"string","pattern":"^XMA-[A-Z0-9-]+$"},
"schema_version":{"const":"1.0.0"},
"primary_engine":{"const":"ENG-X"},
"primary_return_source":{"const":"nonlinear_payoff_geometry"}
```

`tail_activation_refs` is a non-empty unique array matching `^TAS-[A-Z0-9-]+$`. `convexity_price_refs` is a non-empty unique string array. `underlying_state_refs` is a unique string array and is context-only. `state_to_payoff_hypothesis` is non-empty. Dominance uses the same enums as CMA with `expected_pnl_driver` constant `nonlinear_payoff_geometry`. Evidence/falsification/lifecycle/authority use the same shapes and hard-false authority keys as CMA.

- [ ] **Step 5: Run tests**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2AttachmentSchemaTests -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

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
- Consumes: XMA tail references and accepted PositionPassport identity.
- Produces: PIT `TAS-*` and Position-level `PGC-*` contracts.

- [ ] **Step 1: Write failing schema tests**

```python
class ME2PayoffSchemaTests(unittest.TestCase):
    def test_tas_has_calibrated_probability_guard(self):
        schema = json.loads((ROOT / "packages/contracts/schemas/vnext/tail-activation-snapshot.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "urn:yuanli-invest:schema:vnext-tail-activation-snapshot:1.0.0")
        self.assertIn("estimated_probability", schema["properties"])
        self.assertIn("allOf", schema)

    def test_pgc_belongs_to_position(self):
        schema = json.loads((ROOT / "packages/contracts/schemas/vnext/payoff-geometry-context.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "urn:yuanli-invest:schema:vnext-payoff-geometry-context:1.0.0")
        for field in ("position_passport_id","engine_thesis_id","instrument_ref","geometry_dependency"):
            self.assertIn(field, schema["required"])
        self.assertNotIn("research_target_convexity", schema["properties"])
```

- [ ] **Step 2: Run and verify failure**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2PayoffSchemaTests -v
```

Expected: FAIL.

- [ ] **Step 3: Implement TAS schema**

Use `$id=urn:yuanli-invest:schema:vnext-tail-activation-snapshot:1.0.0`, `additionalProperties=false`, and require:

```json
["tail_activation_snapshot_id","schema_version","target_id","as_of","known_as_of","knowledge_cutoff","horizon","tail_side","activation_state","state_refs","evidence_refs","counter_evidence_refs","probability_semantics","staleness","authoritative_current","authority"]
```

Exact enums:

```json
"tail_side":{"enum":["upside","downside","two_sided"]},
"activation_state":{"enum":["inactive","watch","activating","active","unknown"]},
"probability_semantics":{"enum":["uncalibrated_state","calibrated_probability"]},
"staleness":{"enum":["fresh","stale","unknown"]}
```

`estimated_probability` is optional number `[0,1]`. Add:

```json
"allOf":[{
  "if":{"required":["estimated_probability"]},
  "then":{
    "required":["probability_definition","base_rate_ref","calibration_ref"],
    "properties":{"probability_semantics":{"const":"calibrated_probability"}}
  }
}]
```

`probability_definition`, `base_rate_ref`, `calibration_ref` are non-empty strings. `horizon` is required independently. Authority keys `capital_authority`, `position_sizing_authority`, `trading_authority`, `live_execution_authority`, `alpha_runtime_authority` are all false.

- [ ] **Step 4: Implement PGC schema**

Use `$id=urn:yuanli-invest:schema:vnext-payoff-geometry-context:1.0.0`, `additionalProperties=false`, and require:

```json
["payoff_geometry_context_id","schema_version","position_passport_id","engine_thesis_id","instrument_ref","as_of","valid_from","valid_to","geometry_family","direction_semantics","downside_geometry","upside_geometry","expiry_semantics","path_dependency","leverage_semantics","premium_ref","implied_volatility_ref","skew_ref","term_structure_ref","carry_decay_ref","breakeven_ref","liquidity_ref","friction_refs","geometry_dependency","authoritative_current","authority"]
```

Exact enums:

```json
"geometry_family":{"enum":["linear","leveraged_linear","convex","concave","capped","binary","path_dependent","mixed","unknown"]},
"geometry_dependency":{"enum":["auxiliary","material","dominant"]}
```

All price/liquidity `*_ref` properties accept non-empty string or null. `friction_refs` is an array. `valid_to` is date-time or null. `authoritative_current` is boolean. Authority keys are hard false.

- [ ] **Step 5: Run tests**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2PayoffSchemaTests -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

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
- Produces: HP-01 common-stock C path, HP-02 C LEAPS/material-geometry path, HP-03 X long-call/dominant-geometry path, HP-04 legacy projection, HP-05 same-target C+X cardinality.

- [ ] **Step 1: Write failing fixture tests**

```python
class ME2FixtureTests(unittest.TestCase):
    def test_legacy_projection_is_one_way(self):
        schema = json.loads((ROOT / "packages/contracts/schemas/vnext/legacy-convexity-projection.schema.json").read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(props["projection_only"], {"const":True})
        self.assertEqual(props["machine_authority"], {"const":False})
        self.assertEqual(props["write_back_prohibited"], {"const":True})
        self.assertEqual(props["engine_inference_prohibited"], {"const":True})

    def test_me2_adds_x_thesis_and_c_leaps_passport_without_mutating_me1(self):
        theses = json.loads((ME2 / "fixtures/me2-engine-theses.json").read_text(encoding="utf-8"))
        passports = json.loads((ME2 / "fixtures/me2-position-passports.json").read_text(encoding="utf-8"))
        self.assertEqual([t["engine_thesis_id"] for t in theses], ["ET-NVDA-X-001"])
        self.assertEqual({p["position_passport_id"] for p in passports}, {"PP-NVDA-C-LEAPS-001","PP-NVDA-X-001"})
```

- [ ] **Step 2: Run and verify failure**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2FixtureTests -v
```

Expected: FAIL.

- [ ] **Step 3: Implement LegacyConvexityProjection schema**

Use `$id=urn:yuanli-invest:schema:vnext-legacy-convexity-projection:1.0.0`, `additionalProperties=false`, required fields:

```json
["legacy_convexity_projection_id","schema_version","source_schema_id","source_ref","target_ref","legacy_underlying_structure","legacy_issuer_durability","legacy_labels","projection_only","machine_authority","write_back_prohibited","engine_inference_prohibited"]
```

Set:

```json
"source_schema_id":{"const":"urn:yuanli-invest:schema:convexity-profile:1.0.0"},
"projection_only":{"const":true},
"machine_authority":{"const":false},
"write_back_prohibited":{"const":true},
"engine_inference_prohibited":{"const":true}
```

The three legacy payload fields are objects with `additionalProperties=true`; they preserve historical information only.

- [ ] **Step 4: Create `me2-engine-theses.json`**

Use exactly one new EngineThesis object conforming to the unchanged ME1 schema:

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

- [ ] **Step 5: Create `me2-position-passports.json`**

```json
[
  {
    "position_passport_id":"PP-NVDA-C-LEAPS-001","schema_version":"1.0.0","engine_thesis_id":"ET-NVDA-C-001","target_id":"RT2-NVDA","primary_engine":"ENG-C",
    "expression":{"expression_type":"long_call_shadow","instrument_ref":"NVDA-LEAPS-CALL-SHADOW","direction_semantics":"long_call_used_for_capital_efficiency_not_engine_identity"},
    "conditions":{"entry":"C thesis qualified and expression admissible","add":"economic compounding thesis strengthens","hold":"C causal mechanism remains valid","trim":"valuation or risk conditions weaken","exit":"C thesis falsifier triggers"},
    "risk_contract":{"risk_budget_class":"research_shadow_only","max_loss_semantics":"premium_loss_semantics_only_not_live_budget","path_risk_notes":"Geometry is material but not the primary expected P&L source."},
    "falsifier_refs":["F-NVDA-C-1"],"settlement_basis":"linked C EngineThesis settlement",
    "migration_policy":{"silent_migration_prohibited":true,"graduation_allowed":true,"governed_event_required":true},
    "lifecycle":{"status":"eligible","created_at":"2026-08-23T17:01:00+08:00","as_of":"2026-08-23T16:59:00+08:00","valid_from":"2026-08-23T16:59:00+08:00","valid_to":null,"closed_at":null},
    "authority":{"portfolio_weight_authority":false,"position_sizing_authority":false,"trade_execution_authority":false,"live_execution_authority":false}
  },
  {
    "position_passport_id":"PP-NVDA-X-001","schema_version":"1.0.0","engine_thesis_id":"ET-NVDA-X-001","target_id":"RT2-NVDA","primary_engine":"ENG-X",
    "expression":{"expression_type":"long_call_shadow","instrument_ref":"NVDA-X-CALL-SHADOW","direction_semantics":"long_upside_tail_expression"},
    "conditions":{"entry":"X thesis qualified with current tail activation and paid convexity context","add":"tail activation strengthens while convexity price remains admissible","hold":"tail activation and payoff geometry remain valid","trim":"convexity price or tail state deteriorates","exit":"tail activation fails or X falsifier triggers"},
    "risk_contract":{"risk_budget_class":"research_shadow_only","max_loss_semantics":"premium_loss_semantics_only_not_live_budget","path_risk_notes":"No sizing or execution authority."},
    "falsifier_refs":["ME2-F-X-1"],"settlement_basis":"linked X EngineThesis settlement",
    "migration_policy":{"silent_migration_prohibited":true,"graduation_allowed":true,"governed_event_required":true},
    "lifecycle":{"status":"eligible","created_at":"2026-08-23T17:02:00+08:00","as_of":"2026-08-23T16:59:00+08:00","valid_from":"2026-08-23T16:59:00+08:00","valid_to":null,"closed_at":null},
    "authority":{"portfolio_weight_authority":false,"position_sizing_authority":false,"trade_execution_authority":false,"live_execution_authority":false}
  }
]
```

- [ ] **Step 6: Create complete CMA fixture**

```json
[
  {
    "attachment_id":"CMA-NVDA-C-001","schema_version":"1.0.0","engine_thesis_id":"ET-NVDA-C-001","target_id":"RT2-NVDA","primary_engine":"ENG-C","primary_return_source":"economic_compounding",
    "economic_mechanism_refs":[{"role":"value_creation","ref":"ME2-MECH-NVDA-VALUE-POOL"},{"role":"value_capture","ref":"ME2-MECH-NVDA-VALUE-CAPTURE"},{"role":"owner_economics","ref":"ME2-MECH-NVDA-OWNER-ECONOMICS"},{"role":"reinvestment","ref":"ME2-MECH-NVDA-REINVESTMENT"}],
    "economic_optionality_refs":["ME2-MECH-NVDA-ADJACENT-MARKET-OPTIONALITY"],
    "return_bridge":{"value_creation_or_control_ref":"ME2-MECH-NVDA-VALUE-POOL","value_capture_ref":"ME2-MECH-NVDA-VALUE-CAPTURE","owner_economics_ref":"ME2-MECH-NVDA-OWNER-ECONOMICS","reinvestment_ref":"ME2-MECH-NVDA-REINVESTMENT"},
    "price_semantics_refs":["ME2-PRICE-NVDA-C"],
    "dominance_test":{"linear_counterfactual":"survives","geometry_dependency":"auxiliary","tail_state_dependency":"low","expected_pnl_driver":"economic_compounding","rationale":"The thesis remains economic-compounding-led under linear common-equity exposure."},
    "evidence":{"supporting_refs":["SHADOW-E-NVDA-C-1"],"counter_refs":[],"known_as_of":"2026-08-21T23:59:00+08:00","knowledge_cutoff":"2026-08-21T23:59:00+08:00"},
    "falsification":{"falsifier_refs":["F-NVDA-C-1"]},
    "lifecycle":{"status":"active","as_of":"2026-08-21T23:59:00+08:00","valid_from":"2026-08-21T23:59:00+08:00","valid_to":null,"authoritative_current":true},
    "authority":{"capital_authority":false,"portfolio_weight_authority":false,"position_sizing_authority":false,"trading_authority":false,"live_execution_authority":false,"alpha_runtime_authority":false,"capability_promotion_authority":false,"new_engine_creation_authority":false}
  }
]
```

- [ ] **Step 7: Create complete XMA fixture**

```json
[
  {
    "attachment_id":"XMA-NVDA-X-001","schema_version":"1.0.0","engine_thesis_id":"ET-NVDA-X-001","target_id":"RT2-NVDA","primary_engine":"ENG-X","primary_return_source":"nonlinear_payoff_geometry",
    "tail_activation_refs":["TAS-NVDA-X-001"],"convexity_price_refs":["ME2-PRICE-NVDA-X-IV","ME2-PRICE-NVDA-X-SKEW"],"underlying_state_refs":["ME2-UNDERLYING-NVDA-AI-STATE"],
    "state_to_payoff_hypothesis":"An activated upside tail combined with paid call geometry produces the dominant expected P&L mapping.",
    "dominance_test":{"linear_counterfactual":"fails","geometry_dependency":"dominant","tail_state_dependency":"dominant","expected_pnl_driver":"nonlinear_payoff_geometry","rationale":"The thesis loses its defining payoff objective if replaced by linear exposure."},
    "evidence":{"supporting_refs":["ME2-E-X-1"],"counter_refs":[],"known_as_of":"2026-08-23T16:59:00+08:00","knowledge_cutoff":"2026-08-23T16:59:00+08:00"},
    "falsification":{"falsifier_refs":["ME2-F-X-1"]},
    "lifecycle":{"status":"active","as_of":"2026-08-23T16:59:00+08:00","valid_from":"2026-08-23T16:59:00+08:00","valid_to":null,"authoritative_current":true},
    "authority":{"capital_authority":false,"portfolio_weight_authority":false,"position_sizing_authority":false,"trading_authority":false,"live_execution_authority":false,"alpha_runtime_authority":false,"capability_promotion_authority":false,"new_engine_creation_authority":false}
  }
]
```

- [ ] **Step 8: Create complete TAS fixture**

```json
[
  {
    "tail_activation_snapshot_id":"TAS-NVDA-X-001","schema_version":"1.0.0","target_id":"RT2-NVDA","as_of":"2026-08-23T16:59:00+08:00","known_as_of":"2026-08-23T16:58:00+08:00","knowledge_cutoff":"2026-08-23T16:59:00+08:00","horizon":"18_month_upside_tail","tail_side":"upside","activation_state":"activating",
    "state_refs":["ME2-TAIL-STATE-NVDA-1"],"evidence_refs":["ME2-E-X-1"],"counter_evidence_refs":[],"probability_semantics":"uncalibrated_state","staleness":"fresh","authoritative_current":true,
    "authority":{"capital_authority":false,"position_sizing_authority":false,"trading_authority":false,"live_execution_authority":false,"alpha_runtime_authority":false}
  }
]
```

Do not add `estimated_probability` to the positive TAS fixture.

- [ ] **Step 9: Create complete PGC fixtures**

```json
[
  {
    "payoff_geometry_context_id":"PGC-NVDA-C-LEAPS-001","schema_version":"1.0.0","position_passport_id":"PP-NVDA-C-LEAPS-001","engine_thesis_id":"ET-NVDA-C-001","instrument_ref":"NVDA-LEAPS-CALL-SHADOW","as_of":"2026-08-23T16:59:00+08:00","valid_from":"2026-08-23T16:59:00+08:00","valid_to":null,"geometry_family":"convex","direction_semantics":"long_call","downside_geometry":"premium_bounded_shadow_semantics","upside_geometry":"nonlinear_upside_shadow_semantics","expiry_semantics":"long_dated_shadow_expiry","path_dependency":"option_mark_to_market_and_expiry_path","leverage_semantics":"embedded_option_delta_not_live_leverage","premium_ref":null,"implied_volatility_ref":null,"skew_ref":null,"term_structure_ref":null,"carry_decay_ref":null,"breakeven_ref":null,"liquidity_ref":null,"friction_refs":[],"geometry_dependency":"material","authoritative_current":true,
    "authority":{"capital_authority":false,"position_sizing_authority":false,"trading_authority":false,"live_execution_authority":false,"alpha_runtime_authority":false}
  },
  {
    "payoff_geometry_context_id":"PGC-NVDA-X-001","schema_version":"1.0.0","position_passport_id":"PP-NVDA-X-001","engine_thesis_id":"ET-NVDA-X-001","instrument_ref":"NVDA-X-CALL-SHADOW","as_of":"2026-08-23T16:59:00+08:00","valid_from":"2026-08-23T16:59:00+08:00","valid_to":null,"geometry_family":"convex","direction_semantics":"long_upside_call","downside_geometry":"premium_bounded_shadow_semantics","upside_geometry":"dominant_nonlinear_tail_capture_semantics","expiry_semantics":"18_month_shadow_expiry","path_dependency":"tail_activation_must_arrive_within_expiry_horizon","leverage_semantics":"embedded_option_delta_not_live_leverage","premium_ref":"ME2-PRICE-NVDA-X-PREMIUM","implied_volatility_ref":"ME2-PRICE-NVDA-X-IV","skew_ref":"ME2-PRICE-NVDA-X-SKEW","term_structure_ref":"ME2-PRICE-NVDA-X-TERM","carry_decay_ref":"ME2-PRICE-NVDA-X-THETA","breakeven_ref":"ME2-PRICE-NVDA-X-BREAKEVEN","liquidity_ref":"ME2-LIQ-NVDA-X","friction_refs":["ME2-FRICTION-NVDA-X-SPREAD"],"geometry_dependency":"dominant","authoritative_current":true,
    "authority":{"capital_authority":false,"position_sizing_authority":false,"trading_authority":false,"live_execution_authority":false,"alpha_runtime_authority":false}
  }
]
```

- [ ] **Step 10: Create legacy projection fixture**

```json
[
  {
    "legacy_convexity_projection_id":"LCP-NVDA-001","schema_version":"1.0.0","source_schema_id":"urn:yuanli-invest:schema:convexity-profile:1.0.0","source_ref":"LEGACY-CONVEXITY-NVDA-001","target_ref":"RT2-NVDA",
    "legacy_underlying_structure":{"network_effects":"strong","scale_economics":"strong","value_capture":"strong"},
    "legacy_issuer_durability":{"balance_sheet_fragility":"low","refinancing_dependency":"low"},
    "legacy_labels":{"convexity_state":"convex","left_tail_state":"survivable"},
    "projection_only":true,"machine_authority":false,"write_back_prohibited":true,"engine_inference_prohibited":true
  }
]
```

- [ ] **Step 11: Run fixture tests**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2FixtureTests -v
```

Expected: PASS.

- [ ] **Step 12: Commit**

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
- Consumes: ME1 target/thesis/passport fixtures, ME2 schemas/fixtures/successor map/matrix.
- Produces: `load_fixture_bundle()`, `validate_bundle(bundle)`, deterministic `ME2ValidationError.code`, CLI PASS/FAIL, V0–V10.

- [ ] **Step 1: Write failing validator smoke tests**

```python
class ME2ValidatorSmokeTests(unittest.TestCase):
    def test_reference_bundle_validates(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle, validate_bundle
        validate_bundle(load_fixture_bundle())

    def test_validation_error_exposes_code(self):
        from scripts.validate_me2_c_x_separation import ME2ValidationError
        error = ME2ValidationError("ME2_E_TEST", "test")
        self.assertEqual(error.code, "ME2_E_TEST")
```

- [ ] **Step 2: Run and verify import failure**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2ValidatorSmokeTests -v
```

Expected: FAIL.

- [ ] **Step 3: Create validator scaffold**

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


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
```

- [ ] **Step 4: Implement V0 historical/successor non-regression**

`validate_historical_non_regression()` reads `historical_artifacts` from the successor map and requires each current blob SHA to match. Failure code: `ME2_E_HISTORICAL_DRIFT`.

`validate_successor_policy(bundle)` requires:

```python
xs = bundle["successor_map"]["historical_identities"]["CAP-XS-01"]
require(xs["historical_contract_authority"] is True, "ME2_E_CAP_XS_SUCCESSOR_AUTHORITY", "CAP-XS historical authority must remain")
require(xs["redefined_in_place"] is False, "ME2_E_CAP_XS_SUCCESSOR_AUTHORITY", "CAP-XS cannot be redefined")
require(xs["future_reference_implementation_authority"] is False, "ME2_E_CAP_XS_SUCCESSOR_AUTHORITY", "old universal CAP-XS runtime is superseded")
require(xs["future_canonical_output_authority"] is False, "ME2_E_CAP_XS_SUCCESSOR_AUTHORITY", "old CAP-XS cannot own new canonical output")
require(bundle["successor_map"]["next_me_stage_authorized"] is False, "ME2_E_NEXT_STAGE_AUTHORITY", "ME2 cannot authorize ME3")
```

- [ ] **Step 5: Implement local schema validation and bundle loader**

Use schema map:

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

`load_fixture_bundle()` combines ME1 targets, ME1 theses + ME2 theses, ME1 passports + ME2 passports, all ME2 fixture lists, successor map, matrix, and an empty `thesis_histories` dict. `validate_schema_shapes()` first calls `Draft202012Validator.check_schema()` on all five new schemas, then validates every instance with `FormatChecker`; first validation failure raises `ME2_E_SCHEMA`.

- [ ] **Step 6: Implement V1–V3 identity/reference/cardinality**

Create `validate_identity_integrity`, `validate_reference_integrity`, `validate_attachment_cardinality` with these exact rules:

```text
all CMA/XMA/TAS/PGC/LCP IDs unique
attachment target and thesis references resolve
CMA thesis primary_engine == ENG-C -> otherwise ME2_E_C_ENGINE_MISMATCH
XMA thesis primary_engine == ENG-X -> otherwise ME2_E_X_ENGINE_MISMATCH
PGC Passport and Thesis resolve
PGC engine_thesis_id == Passport.engine_thesis_id -> ME2_E_PGC_THESIS_MISMATCH
PGC instrument_ref == Passport.expression.instrument_ref -> ME2_E_PGC_INSTRUMENT_MISMATCH
qualified/active C Thesis has exactly one current CMA -> ME2_E_C_ATTACHMENT_REQUIRED
qualified/active X Thesis has exactly one current XMA -> ME2_E_X_ATTACHMENT_REQUIRED
current XMA references >=1 TAS and exactly one referenced TAS is current -> ME2_E_X_TAIL_REQUIRED
eligible/active X Passport has exactly one current PGC -> ME2_E_X_PGC_REQUIRED
```

- [ ] **Step 7: Implement V4–V5 source-of-return and dominance firewall**

Use:

```python
PROHIBITED_X_SOURCE_TOKENS = {
    "large_tam", "network_effect", "network_effects", "winner_take_most",
    "historical_20x", "positive_skew", "market_expansion", "platform_optionality",
    "value_capture", "reinvestment_runway", "legacy_convexity_state", "legacy_xs",
    "real_optionality", "option_instrument"
}


def validate_c_x_mechanism_separation(bundle: dict) -> None:
    for thesis in bundle["theses"]:
        if thesis["identity_core"]["primary_engine"] != "ENG-X":
            continue
        sources = set(thesis["research_contract"]["source_of_return"])
        require("nonlinear_payoff_geometry" in sources, "ME2_E_X_SOURCE_OF_RETURN", "ENG-X requires nonlinear_payoff_geometry as a source of return")
        prohibited_only = bool(sources) and sources.issubset(PROHIBITED_X_SOURCE_TOKENS)
        require(not prohibited_only, "ME2_E_X_SOURCE_OF_RETURN", "underlying/instrument label cannot define ENG-X")


def validate_dominance(bundle: dict) -> None:
    for cma in bundle["cma"]:
        d = cma["dominance_test"]
        require(d["expected_pnl_driver"] == "economic_compounding", "ME2_E_C_PNL_DRIVER", "CMA P&L driver mismatch")
        require(d["geometry_dependency"] != "dominant", "ME2_E_C_GEOMETRY_DOMINANT", "C cannot be geometry-dominant")
    for xma in bundle["xma"]:
        d = xma["dominance_test"]
        require(d["expected_pnl_driver"] == "nonlinear_payoff_geometry", "ME2_E_X_PNL_DRIVER", "XMA P&L driver mismatch")
        require(d["geometry_dependency"] == "dominant", "ME2_E_X_GEOMETRY_NOT_DOMINANT", "X requires dominant geometry")
```

- [ ] **Step 8: Implement V6 Tail Activation PIT/calibration**

`validate_tail_activation(bundle)` requires `known_as_of <= knowledge_cutoff <= as_of`; violation -> `ME2_E_TAS_FUTURE_KNOWLEDGE`. If `estimated_probability` exists, require `probability_semantics=calibrated_probability` and non-empty `probability_definition`, `base_rate_ref`, `calibration_ref`, `horizon`; otherwise `ME2_E_TAS_UNCALIBRATED_PROBABILITY`.

- [ ] **Step 9: Implement V7 Position/Geometry firewall**

`validate_payoff_geometry(bundle)` requires PGC/Passport thesis and instrument equality. For X Passports, current PGC must have `geometry_dependency=dominant` and `geometry_family` not in `{linear, leveraged_linear}`; static linear X fails with `ME2_E_X_STATIC_LINEAR_GEOMETRY`. This does not ban common stock from all X expressions: a genuinely contingent/dynamic stock strategy must represent its Position geometry as `path_dependent` or `mixed`, not `linear`.

- [ ] **Step 10: Implement V8 legacy one-way compatibility**

```python
def validate_legacy_compatibility(bundle: dict) -> None:
    for projection in bundle["legacy"]:
        require(projection["projection_only"] is True, "ME2_E_LEGACY_AUTHORITY_LEAK", "legacy projection must be projection-only")
        require(projection["machine_authority"] is False, "ME2_E_LEGACY_AUTHORITY_LEAK", "legacy projection cannot have machine authority")
        require(projection["write_back_prohibited"] is True, "ME2_E_LEGACY_AUTHORITY_LEAK", "legacy write-back must be prohibited")
        require(projection["engine_inference_prohibited"] is True, "ME2_E_LEGACY_AUTHORITY_LEAK", "legacy engine inference must be prohibited")
```

- [ ] **Step 11: Implement V9 authority and no-silent-migration firewalls**

`validate_authority(bundle)` recursively checks every ME2 successor `authority` object and requires every value false; failure -> `ME2_E_AUTHORITY_LEAK`. It also requires state authorities `alpha_runtime`, `historical_performance_claim`, `capability_promotion`, `new_engine_creation`, `portfolio`, `position_sizing`, `trading`, `live_execution`, `constitution_mutation`, `runtime_cutover`, `ME3`, `ME4`, `ME5` false.

`validate_no_silent_migration(bundle)` iterates each `thesis_histories` list ordered by revision and requires immutable `target_id`, `identity_core.primary_engine`, `identity_core.thesis_origin`, `identity_core.opened_at`; any mutation -> `ME2_E_SILENT_ENGINE_MIGRATION`.

- [ ] **Step 12: Implement V10 matrix integrity and orchestrator**

`validate_matrix_integrity(bundle)` requires exactly HN-01..HN-16 and HP-01..HP-05 with expected FAIL/PASS values.

```python
def validate_bundle(bundle: dict) -> None:
    validate_historical_non_regression()
    validate_successor_policy(bundle)
    validate_schema_shapes(bundle)
    validate_identity_integrity(bundle)
    validate_reference_integrity(bundle)
    validate_attachment_cardinality(bundle)
    validate_c_x_mechanism_separation(bundle)
    validate_dominance(bundle)
    validate_tail_activation(bundle)
    validate_payoff_geometry(bundle)
    validate_legacy_compatibility(bundle)
    validate_no_silent_migration(bundle)
    validate_authority(bundle)
    validate_matrix_integrity(bundle)


def main() -> int:
    validate_bundle(load_fixture_bundle())
    print("ME2 C-X Economic Mechanism Separation validation: PASS")
    return 0
```

CLI catches exceptions, prints `validation_error: ...`, and exits `1`.

- [ ] **Step 13: Run smoke tests and validator**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2ValidatorSmokeTests -v
python scripts/validate_me2_c_x_separation.py
```

Expected: PASS and `ME2 C-X Economic Mechanism Separation validation: PASS`.

- [ ] **Step 14: Commit**

```bash
git add scripts/validate_me2_c_x_separation.py tests/test_me2_c_x_separation.py
git commit -m "ME2: add fail-closed C-X relational validator"
```

---

### Task 6: Encode HN-01..HN-16 and HP-01..HP-05 as executable tests

**Files:**
- Modify: `tests/test_me2_c_x_separation.py`

**Interfaces:**
- Consumes: `load_fixture_bundle`, `validate_bundle`, `ME2ValidationError`.
- Produces: executable negative/positive proof matrix.

- [ ] **Step 1: Add helpers**

```python
import copy


def assert_me2_error(testcase, bundle, expected_code):
    from scripts.validate_me2_c_x_separation import ME2ValidationError, validate_bundle
    with testcase.assertRaises(ME2ValidationError) as ctx:
        validate_bundle(bundle)
    testcase.assertEqual(ctx.exception.code, expected_code)


def set_x_sources(bundle, sources):
    thesis = next(t for t in bundle["theses"] if t["engine_thesis_id"] == "ET-NVDA-X-001")
    thesis["research_contract"]["source_of_return"] = list(sources)
    return bundle
```

- [ ] **Step 2: Add HN-01, HN-02, HN-03, HN-05, HN-06, HN-12 source-of-return tests**

```python
class ME2HardNegativeSourceTests(unittest.TestCase):
    def _assert_bad_source(self, token):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle
        bundle = set_x_sources(copy.deepcopy(load_fixture_bundle()), [token])
        assert_me2_error(self, bundle, "ME2_E_X_SOURCE_OF_RETURN")

    def test_hn01_large_tam_does_not_create_x(self): self._assert_bad_source("large_tam")
    def test_hn02_network_effect_does_not_create_x(self): self._assert_bad_source("network_effect")
    def test_hn03_historical_20x_does_not_create_x(self): self._assert_bad_source("historical_20x")
    def test_hn05_legacy_xs_does_not_create_x(self): self._assert_bad_source("legacy_xs")
    def test_hn06_option_instrument_does_not_create_x(self): self._assert_bad_source("option_instrument")
    def test_hn12_real_optionality_does_not_create_x(self): self._assert_bad_source("real_optionality")
```

- [ ] **Step 3: Add HN-04 and HN-14 legacy tests**

HN-04: clone valid bundle, replace the X thesis source-of-return with `legacy_convexity_state`, assert `ME2_E_X_SOURCE_OF_RETURN`.

HN-14: clone valid bundle, set first legacy projection `write_back_prohibited=false`; because the schema uses `const:true`, assert `ME2_E_SCHEMA`.

Use explicit methods `test_hn04_legacy_convexity_label_does_not_create_x` and `test_hn14_legacy_projection_cannot_write_back`.

- [ ] **Step 4: Add HN-07..HN-11 structural/dominance tests**

```python
class ME2HardNegativeMechanismTests(unittest.TestCase):
    def test_hn07_x_without_tail_activation_fails(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle
        bundle = copy.deepcopy(load_fixture_bundle())
        bundle["xma"][0]["tail_activation_refs"] = []
        assert_me2_error(self, bundle, "ME2_E_SCHEMA")

    def test_hn08_x_without_current_pgc_fails(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle
        bundle = copy.deepcopy(load_fixture_bundle())
        bundle["pgc"] = [p for p in bundle["pgc"] if p["position_passport_id"] != "PP-NVDA-X-001"]
        assert_me2_error(self, bundle, "ME2_E_X_PGC_REQUIRED")

    def test_hn09_probability_without_calibration_fails(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle
        bundle = copy.deepcopy(load_fixture_bundle())
        bundle["tas"][0]["estimated_probability"] = 0.72
        assert_me2_error(self, bundle, "ME2_E_SCHEMA")

    def test_hn10_c_cannot_be_geometry_dominant(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle
        bundle = copy.deepcopy(load_fixture_bundle())
        bundle["cma"][0]["dominance_test"]["geometry_dependency"] = "dominant"
        assert_me2_error(self, bundle, "ME2_E_C_GEOMETRY_DOMINANT")

    def test_hn11_x_must_be_geometry_dominant(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle
        bundle = copy.deepcopy(load_fixture_bundle())
        bundle["xma"][0]["dominance_test"]["geometry_dependency"] = "material"
        assert_me2_error(self, bundle, "ME2_E_X_GEOMETRY_NOT_DOMINANT")
```

- [ ] **Step 5: Add HN-13, HN-15, HN-16 governance tests**

```python
class ME2HardNegativeGovernanceTests(unittest.TestCase):
    def test_hn13_cap_xs_old_runtime_cannot_regain_future_authority(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle
        bundle = copy.deepcopy(load_fixture_bundle())
        bundle["successor_map"]["historical_identities"]["CAP-XS-01"]["future_reference_implementation_authority"] = True
        assert_me2_error(self, bundle, "ME2_E_CAP_XS_SUCCESSOR_AUTHORITY")

    def test_hn15_same_thesis_cannot_mutate_primary_engine(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle
        bundle = copy.deepcopy(load_fixture_bundle())
        base = next(t for t in bundle["theses"] if t["engine_thesis_id"] == "ET-NVDA-C-001")
        mutated = copy.deepcopy(base)
        mutated["lifecycle"]["revision"] = 2
        mutated["identity_core"]["primary_engine"] = "ENG-X"
        bundle["thesis_histories"] = {"ET-NVDA-C-001":[base, mutated]}
        assert_me2_error(self, bundle, "ME2_E_SILENT_ENGINE_MIGRATION")

    def test_hn16_me2_contract_cannot_grant_trading_authority(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle
        bundle = copy.deepcopy(load_fixture_bundle())
        bundle["cma"][0]["authority"]["trading_authority"] = True
        assert_me2_error(self, bundle, "ME2_E_SCHEMA")
```

- [ ] **Step 6: Add one extra static-linear semantic guard**

This test supports D13 even though it is not a separate HN matrix ID:

```python
def test_x_static_linear_geometry_fails_closed(self):
    from scripts.validate_me2_c_x_separation import load_fixture_bundle
    bundle = copy.deepcopy(load_fixture_bundle())
    pgc = next(p for p in bundle["pgc"] if p["position_passport_id"] == "PP-NVDA-X-001")
    pgc["geometry_family"] = "linear"
    assert_me2_error(self, bundle, "ME2_E_X_STATIC_LINEAR_GEOMETRY")
```

Place it inside `ME2HardNegativeMechanismTests`.

- [ ] **Step 7: Add HP-01..HP-05 positive tests**

```python
class ME2HardPositiveTests(unittest.TestCase):
    def test_hp01_common_stock_c_plus_cma_passes(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle, validate_bundle
        bundle = load_fixture_bundle()
        self.assertTrue(any(p["position_passport_id"] == "PP-NVDA-C-001" for p in bundle["passports"]))
        validate_bundle(bundle)

    def test_hp02_c_leaps_with_material_geometry_passes(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle, validate_bundle
        bundle = load_fixture_bundle()
        pgc = next(p for p in bundle["pgc"] if p["position_passport_id"] == "PP-NVDA-C-LEAPS-001")
        self.assertEqual(pgc["geometry_dependency"], "material")
        validate_bundle(bundle)

    def test_hp03_x_call_with_tail_and_dominant_geometry_passes(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle, validate_bundle
        bundle = load_fixture_bundle()
        self.assertEqual(bundle["xma"][0]["dominance_test"]["geometry_dependency"], "dominant")
        self.assertTrue(bundle["xma"][0]["tail_activation_refs"])
        validate_bundle(bundle)

    def test_hp04_legacy_projection_read_only_passes(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle, validate_bundle
        bundle = load_fixture_bundle()
        projection = bundle["legacy"][0]
        self.assertTrue(projection["projection_only"])
        self.assertFalse(projection["machine_authority"])
        validate_bundle(bundle)

    def test_hp05_same_target_supports_independent_c_and_x_theses(self):
        from scripts.validate_me2_c_x_separation import load_fixture_bundle, validate_bundle
        bundle = load_fixture_bundle()
        selected = {t["engine_thesis_id"]:t for t in bundle["theses"] if t["engine_thesis_id"] in {"ET-NVDA-C-001","ET-NVDA-X-001"}}
        self.assertEqual({t["target_id"] for t in selected.values()}, {"RT2-NVDA"})
        self.assertEqual({t["identity_core"]["primary_engine"] for t in selected.values()}, {"ENG-C","ENG-X"})
        validate_bundle(bundle)
```

- [ ] **Step 8: Run complete ME2 unit file**

```bash
python -m unittest tests.test_me2_c_x_separation -v
```

Expected: PASS and output includes tests named for HN-01..HN-16 and HP-01..HP-05.

- [ ] **Step 9: Commit**

```bash
git add scripts/validate_me2_c_x_separation.py tests/test_me2_c_x_separation.py
git commit -m "ME2: enforce hard-negative and hard-positive matrix"
```

---

### Task 7: Integrate ME2 into repository-gates and qualify the candidate

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/architecture/me2/ME2-STATE.json`
- Modify: `docs/architecture/me2/ME2-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `tests/test_me2_c_x_separation.py`
- Modify only the repository's existing generated manifest if `scripts/build_manifest.py --check` requires regeneration.

**Interfaces:**
- Consumes: passing local ME2 validator/test suite.
- Produces: repository-level ME2 gate and `machine_qualified_ready_for_human_review` state; no Human acceptance.

- [ ] **Step 1: Write failing CI-order test**

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

- [ ] **Step 2: Run and verify failure**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2CIGateTests -v
```

Expected: FAIL because CI does not call ME2.

- [ ] **Step 3: Add exactly one ME2 command**

Immediately after:

```yaml
- run: python scripts/validate_me1_state_object_model.py
```

insert:

```yaml
- run: python scripts/validate_me2_c_x_separation.py
```

Leave all other workflow steps unchanged.

- [ ] **Step 4: Run local repository gates**

```bash
python scripts/validate_me2_c_x_separation.py
python -m unittest tests.test_me2_c_x_separation -v
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/validate_repository.py
python scripts/check_governance.py
python scripts/build_manifest.py --check
```

Expected: all exit 0. If manifest check reports drift caused by new files, run the repository's existing `python scripts/build_manifest.py`, then rerun `--check`; stage only the existing generated manifest file reported by that script. Never hand-edit manifest hashes and never create a second manifest.

- [ ] **Step 5: Transition state only after full local green**

Change:

```json
"status":"machine_qualified_ready_for_human_review",
"next_gate":"ME2_HUMAN_REVIEW"
```

No acceptance or merge field becomes true. Change Human Review card header to `Status: machine_qualified_ready_for_human_review`; D1–D18 remain pending Human decisions.

- [ ] **Step 6: Run CI-order test and full local gates again**

```bash
python -m unittest tests.test_me2_c_x_separation.ME2CIGateTests -v
python scripts/validate_me2_c_x_separation.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/check_governance.py
python scripts/build_manifest.py --check
```

Expected: PASS.

- [ ] **Step 7: Commit**

Stage `.github/workflows/ci.yml`, `docs/architecture/me2`, `tests/test_me2_c_x_separation.py`, and only the existing manifest file if it changed:

```bash
git commit -m "ME2: wire C-X separation into repository gates"
```

---

### Task 8: Verify exact candidate head and stop at ME2 Human Review

**Files:**
- No semantic implementation files change in this task.

**Interfaces:**
- Consumes: committed ME2 candidate.
- Produces: exact-head verification evidence and Human Review handoff; no acceptance receipt, merge, or ME3 work.

- [ ] **Step 1: Verify branch diff scope**

```bash
git diff --name-status main...HEAD
```

Allowed additions/modifications are the accepted ME2 design/plan, `docs/architecture/me2/**`, the five new vnext schemas, `scripts/validate_me2_c_x_separation.py`, `tests/test_me2_c_x_separation.py`, `.github/workflows/ci.yml`, and the repository's pre-existing generated manifest only if regeneration was required. Historical CAP-XS, Extreme Engine, ConvexityProfile, EngineThesis, PositionPassport, and old R2.3-B2 plan must not be modified.

- [ ] **Step 2: Re-run exact-head qualification**

```bash
python scripts/validate_me2_c_x_separation.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/validate_repository.py
python scripts/check_governance.py
python scripts/build_manifest.py --check
```

Expected: all PASS.

- [ ] **Step 3: Observe GitHub Actions for the exact candidate head**

The existing `repository-gates` workflow must report both `contracts` and `governance` SUCCESS for the exact candidate head. Record exact head SHA and workflow run ID in the conversational handoff. Do not write a Human Acceptance receipt in this task.

- [ ] **Step 4: Present Human Review without pre-answering it**

Surface D1–D18, exact candidate head, local qualification summary, and GitHub Actions status. The only next Human decision token is:

```text
ACCEPT_ME2_C_X_ECONOMIC_MECHANISM_SEPARATION
```

- [ ] **Step 5: Stop**

Do not create an acceptance receipt, do not merge, do not set `ME2_COMPLETE`, do not authorize ME3, and do not begin ME3.

---

## Plan Self-Check Matrix

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
| Old R2.3-B2 CAP-XS path superseded | Tasks 1, 5 |
| Historical blob non-regression | Tasks 1, 5, 8 |
| Dominance test | Tasks 2, 4–6 |
| Instrument != Engine | Tasks 4–6 |
| No Silent Thesis Migration | Tasks 5–6 |
| PIT/calibration discipline | Tasks 3, 5, 6 |
| 16 hard negatives | Tasks 1, 6 |
| 5 hard positives | Tasks 1, 4, 6 |
| Authority firewall | Tasks 1–7 |
| CI integration | Task 7 |
| 18/18 Human Review gate | Tasks 1, 7, 8 |
| No ME3/ME4/ME5 implementation | Global Constraints, Tasks 1, 7, 8 |
| No alpha/portfolio/trading implementation | Global Constraints, Tasks 1–7 |
