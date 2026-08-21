# ME0 Multi-Engine Investment Ontology & Authority Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the approved ME0 successor design into a governed, machine-checkable candidate authority freeze that separates research primitives, return engines, engine theses and capital-expression objects without mutating historical Canon or acquiring trading authority.

**Architecture:** ME0 is implemented as a candidate architecture pack under `docs/architecture/me0/`, containing a prose authority freeze, a machine-readable authority contract, an explicit semantic-successor map, candidate state and Human Review card. A dedicated fail-closed validator proves namespace separation, open-world engine semantics, historical-Canon immutability, Evidence/Survival supremacy and no-trading authority; CI runs the validator before repository-wide tests. ME0 does not yet rewrite `docs/os-vnext/CONSTITUTION.md`, migrate schemas, change Registry entries, or implement C/R/X runtime objects; those are successor stages after Human Acceptance.

**Tech Stack:** Markdown, JSON, Python 3.12, standard library `json`/`pathlib`, unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-21-me0-multi-engine-investment-ontology-authority-freeze-design.md`

## Global Constraints

- Preserve YIP0 philosophical laws: `REALITY_OVER_BELIEF`, `REFLEXIVITY`, `TAIL_ASYMMETRY`, `SURVIVAL_FIRST`.
- Preserve all historical YIP0, R2.3-A, R2.3-B0, R2.3-B1, QXM1 and QXM2 receipts as immutable ledger facts.
- Freeze `ENG-C | Compounding`, `ENG-R | Reflexive Repricing`, `ENG-X | Convexity` as the Genesis Engine Set.
- Freeze `engine_registry_closed_world = false`; ME0 must not claim C/R/X are a proven exhaustive ontology.
- Preserve `CAP-R-01` historical meaning as `Regime Causal Decomposition`; `ENG-R` must never redefine that identifier.
- Preserve `Claim Authority <= Evidence Authority` as a horizontal Evidence authority invariant.
- Preserve Survival as a cross-engine constraint; research pass must not imply capital pass.
- Treat P/N/E/V/S as research primitives, services or constraints, not automatic return-engine identities.
- Freeze `Cash` as `BOOK-CASH | Liquidity Reserve`, not as a fourth return engine.
- Freeze `No Silent Thesis Migration`; engine changes require a future governed `AssetGraduationEvent` or equivalent Human-Gated successor mechanism.
- No scalar PNX / Force / engine master score.
- No target price, recommended portfolio weight, automatic position size, buy/sell/hold instruction or live execution authority.
- ME0 implementation must not modify `docs/os-vnext/CONSTITUTION.md`, existing accepted Capability specs, existing schemas, formal Registry contents or historical receipts.
- Human Acceptance token: `ACCEPT_ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE`.
- Future merge authorization is separate from Human Acceptance and must not be inferred by the validator or state.

---

## File Structure

### Candidate authority pack

- `docs/architecture/me0/ME0-MULTI-ENGINE-ONTOLOGY-AUTHORITY-FREEZE-v0.1.md` — human-readable authority freeze and first-principles ontology.
- `docs/architecture/me0/ME0-AUTHORITY-CONTRACT-v0.1.json` — machine-readable engine identities, authority layers, invariants and prohibited interpretations.
- `docs/architecture/me0/ME0-SEMANTIC-SUCCESSOR-MAP-v0.1.json` — explicit mapping from current accepted semantics to successor roles without historical mutation.
- `docs/architecture/me0/ME0-STATE.json` — candidate lifecycle and Human Gate state.
- `docs/architecture/me0/ME0-HUMAN-REVIEW-CARD-v0.1.md` — formal review dimensions and acceptance token.

### Validation

- `scripts/validate_me0_multi_engine_ontology.py` — fail-closed semantic/governance validator.
- `tests/test_me0_multi_engine_ontology.py` — focused unit tests, including negative mutation tests.
- `.github/workflows/ci.yml` — invokes the ME0 validator in `contracts`.

No production schema, runtime, Registry, portfolio or Constitution file is created or modified in ME0.

---

### Task 1: Candidate Authority Freeze and Machine Contract

**Files:**
- Create: `docs/architecture/me0/ME0-MULTI-ENGINE-ONTOLOGY-AUTHORITY-FREEZE-v0.1.md`
- Create: `docs/architecture/me0/ME0-AUTHORITY-CONTRACT-v0.1.json`

**Interfaces:**
- Consumes: YIP0 philosophical authority and accepted historical OS semantics as read-only upstream context.
- Produces: stable engine IDs `ENG-C`, `ENG-R`, `ENG-X`; authority-layer IDs; candidate invariants consumed by the successor map and validator.

- [ ] **Step 1: Write the human-readable authority freeze**

The document must contain these exact sections and meanings:

```text
0 Status and authority
1 Mother objective
2 Ontology distinctions
3 Authority layers
4 Genesis Engine Set
5 Shared research primitives/services
6 Cash / liquidity reserve role
7 No Silent Thesis Migration
8 Human compression boundary
9 Historical-Canon preservation
10 Explicit non-goals
11 Success criteria
```

Required mother objective:

```text
Lifetime Right-Tail Capture under Survival Constraints
```

Required ontology inequality:

```text
asset_form != pricing_archetype != return_engine != engine_thesis != position_expression
```

Required authority layers:

```text
L0 Philosophy Authority
L1 Research Primitive / Service Authority
L2 Return Engine Authority
L3 Thesis Authority
L4 Capital Expression Authority
L5 Runtime / Settlement Authority
```

Required Engine definitions:

```text
ENG-C | Compounding
ENG-R | Reflexive Repricing
ENG-X | Convexity
```

The prose must state that these are the `Genesis Engine Set`, that the engine registry is open-world, and that future evidence-backed engines may be added only through a separately governed successor process.

- [ ] **Step 2: Write the machine-readable authority contract**

Use this exact top-level shape:

```json
{
  "schema_version": "0.1.0",
  "stage": "ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE",
  "status": "candidate_successor_ontology_authority",
  "mother_objective": "Lifetime Right-Tail Capture under Survival Constraints",
  "ontology_distinctions": {},
  "authority_layers": [],
  "genesis_engine_set": [],
  "research_primitives_services": {},
  "book_roles": {},
  "migration_invariants": [],
  "historical_canon_policy": {},
  "human_projection_policy": {},
  "governance": {},
  "prohibited_interpretations": []
}
```

`ontology_distinctions` must encode:

```json
{
  "asset_form_not_pricing_archetype": true,
  "pricing_archetype_not_return_engine": true,
  "return_engine_not_engine_thesis": true,
  "engine_thesis_not_position_expression": true,
  "target_identity_does_not_determine_thesis_identity": true,
  "book_membership_is_thesis_position_specific": true
}
```

Each element of `genesis_engine_set` must contain exactly these keys:

```json
{
  "engine_id": "ENG-C",
  "name": "Compounding",
  "stable_question": "...",
  "primary_source_of_return": [],
  "price_semantics": "...",
  "not_this_engine": []
}
```

The three exact IDs must be unique. Add:

```json
"engine_registry_closed_world": false
```

inside `governance`.

`research_primitives_services` must encode:

```json
{
  "P": "reality_structural_state_family",
  "N": "belief_expectation_state_family",
  "E": "horizontal_evidence_authority_plane",
  "V": "routed_price_interpretation_service_family",
  "S": "horizontal_survival_constraint"
}
```

`book_roles` must include:

```json
{
  "BOOK-CASH": {
    "name": "Liquidity Reserve",
    "is_return_engine": false,
    "roles": ["survival_buffer", "future_optionality", "funding_resilience", "forced_selling_avoidance"]
  }
}
```

`migration_invariants` must include exact string tokens:

```text
NO_SILENT_THESIS_MIGRATION
HISTORICAL_IDENTITIES_IMMUTABLE
ENGINE_CHANGE_REQUIRES_GOVERNED_EVENT
RESEARCH_PASS_DOES_NOT_IMPLY_CAPITAL_PASS
CLAIM_AUTHORITY_LE_EVIDENCE_AUTHORITY
```

- [ ] **Step 3: Encode explicit authority prohibitions**

`governance` must contain:

```json
{
  "engine_registry_closed_world": false,
  "historical_canon_mutation_authority": false,
  "registry_admission_authority": false,
  "capability_promotion_authority": false,
  "position_sizing_authority": false,
  "portfolio_weight_authority": false,
  "buy_sell_hold_authority": false,
  "live_execution_authority": false
}
```

`prohibited_interpretations` must explicitly prohibit:

- `C_R_X_are_proven_exhaustive_universal_ontology`;
- `CAP_R_01_means_ENG_R`;
- `cash_is_fourth_return_engine`;
- `human_PNX_projection_is_machine_return_engine_ontology`;
- `research_target_has_only_one_valid_thesis`;
- `engine_change_can_be_implicit`;
- `research_pass_implies_capital_pass`.

- [ ] **Step 4: Commit Task 1**

```bash
git add docs/architecture/me0/ME0-MULTI-ENGINE-ONTOLOGY-AUTHORITY-FREEZE-v0.1.md docs/architecture/me0/ME0-AUTHORITY-CONTRACT-v0.1.json
git commit -m "feat: add ME0 multi-engine authority contract"
```

---

### Task 2: Semantic Successor Map

**Files:**
- Create: `docs/architecture/me0/ME0-SEMANTIC-SUCCESSOR-MAP-v0.1.json`

**Interfaces:**
- Consumes: `ME0-AUTHORITY-CONTRACT-v0.1.json` plus current accepted semantic IDs.
- Produces: non-destructive routing metadata used by future ME1/ME2 migrations and by the ME0 validator.

- [ ] **Step 1: Write successor-map top-level shape**

```json
{
  "schema_version": "0.1.0",
  "stage": "ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE",
  "policy": "semantic_successors_never_mutate_historical_receipts",
  "historical_identities": [],
  "successor_roles": [],
  "future_object_identities": [],
  "deferred_migrations": []
}
```

- [ ] **Step 2: Encode historical identity preservation**

`historical_identities` must include at minimum:

```json
[
  {
    "id": "CAP-R-01",
    "historical_meaning": "Regime Causal Decomposition",
    "historical_semantic_parent": "P.capital",
    "redefined_in_place": false,
    "future_successor_hint": "CAP-REG-01"
  },
  {
    "id": "CAP-XS-01",
    "historical_meaning": "Structural Asymmetry Source Mapper",
    "redefined_in_place": false,
    "future_action": "typed_successor_split_under_ME2"
  },
  {
    "id": "CAP-V-01",
    "historical_meaning": "Price-Implied Expectations",
    "redefined_in_place": false,
    "future_action": "routed_price_interpretation_successor"
  }
]
```

- [ ] **Step 3: Encode successor authority roles**

`successor_roles` must include exact role IDs:

```text
ENG-C
ENG-R
ENG-X
A2_RETURN_ENGINE_ROUTE
BOOK-C
BOOK-R
BOOK-X
BOOK-CASH
```

For `ENG-R`, require:

```json
{
  "role_id": "ENG-R",
  "meaning": "Reflexive Repricing",
  "namespace": "return_engine",
  "must_not_alias": ["CAP-R-01"]
}
```

- [ ] **Step 4: Freeze future object identities without implementing schemas**

`future_object_identities` must contain:

```text
EngineThesis
PositionPassport
AssetGraduationEvent
BookState
MetaAllocationResearchState
```

Each entry must set:

```json
{
  "implementation_authority_in_ME0": false,
  "schema_creation_deferred_to": "ME1_or_later"
}
```

- [ ] **Step 5: Encode deferred migrations**

At minimum:

```text
ME1_STATE_OBJECT_MODEL_REFRAME
ME2_C_X_SEMANTIC_SEPARATION
ME3_REFLEXIVE_ENGINE_MARKET_CLOCK_CONTRACT
ME4_GRADUATION_META_ALLOCATOR
ME5_THREE_ENGINE_GOLD_REPLAY_ABLATION
```

No deferred migration may be marked `authorized` by ME0.

- [ ] **Step 6: Commit Task 2**

```bash
git add docs/architecture/me0/ME0-SEMANTIC-SUCCESSOR-MAP-v0.1.json
git commit -m "docs: freeze ME0 semantic successor map"
```

---

### Task 3: Candidate State and Human Review Gate

**Files:**
- Create: `docs/architecture/me0/ME0-STATE.json`
- Create: `docs/architecture/me0/ME0-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Consumes: Task 1 contract and Task 2 successor map.
- Produces: lifecycle state and formal Human Review criteria consumed by the validator.

- [ ] **Step 1: Create candidate state**

Use this exact minimum structure:

```json
{
  "stage": "ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE",
  "status": "candidate_started",
  "repository_base_sha": "bd8931e1bf21dceb5e34a68ec41aa199b83e9410",
  "design_approval": {
    "token": "APPROVE_ME0_DESIGN_FOR_IMPLEMENTATION",
    "decision": "accepted"
  },
  "human_gate": {
    "token": "ACCEPT_ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE",
    "decision": "pending",
    "acceptance_does_not_imply_merge": true
  },
  "implementation_authorities": {
    "constitution_mutation": false,
    "schema_migration": false,
    "registry_admission": false,
    "runtime": false,
    "portfolio": false,
    "live_execution": false
  },
  "next_gate": "ME0_MACHINE_QUALIFICATION"
}
```

- [ ] **Step 2: Create the Human Review card**

The card must define PASS/FAIL dimensions `D1` through `D16`:

```text
D1  first-principles coherence
D2  YIP0 philosophical compatibility
D3  target / thesis separation
D4  asset-form / pricing-archetype / engine separation
D5  C engine boundary
D6  R engine boundary
D7  X engine boundary
D8  open-world engine-registry boundary
D9  CAP-R-01 / ENG-R namespace non-collision
D10 Xs successor-split boundary
D11 P/N/E/V/S shared-service boundary
D12 Cash is book role, not engine
D13 No Silent Thesis Migration
D14 historical receipt immutability
D15 Evidence and Survival supremacy
D16 no trading / sizing / Registry authority regression
```

The card must end with:

```text
Human Acceptance Token:
ACCEPT_ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE

Acceptance does not imply merge.
```

- [ ] **Step 3: Commit Task 3**

```bash
git add docs/architecture/me0/ME0-STATE.json docs/architecture/me0/ME0-HUMAN-REVIEW-CARD-v0.1.md
git commit -m "docs: add ME0 state and human review gate"
```

---

### Task 4: Fail-Closed ME0 Validator with Negative Tests

**Files:**
- Create: `scripts/validate_me0_multi_engine_ontology.py`
- Create: `tests/test_me0_multi_engine_ontology.py`

**Interfaces:**
- Consumes: all ME0 candidate artifacts and read-only historical Canon files.
- Produces: exit 0 only if ME0 candidate semantics and governance invariants hold; importable validation functions for focused mutation tests.

- [ ] **Step 1: Write failing repository-pass test before validator exists**

Create:

```python
import unittest

from scripts import validate_me0_multi_engine_ontology as me0


class ME0OntologyTests(unittest.TestCase):
    def test_repository_me0_candidate_passes(self):
        me0.main()


if __name__ == "__main__":
    unittest.main()
```

Run:

```bash
python -m unittest tests.test_me0_multi_engine_ontology.ME0OntologyTests.test_repository_me0_candidate_passes -v
```

Expected: FAIL because the validator module does not exist yet.

- [ ] **Step 2: Implement JSON loading and contract validation helpers**

The validator module must expose:

```python
def load_json(path: Path) -> dict: ...
def validate_contract(contract: dict) -> None: ...
def validate_successor_map(successor_map: dict) -> None: ...
def validate_state(state: dict) -> None: ...
def validate_review_card(text: str) -> None: ...
def validate_historical_non_regression() -> None: ...
def main() -> int: ...
```

Use constants:

```python
EXPECTED_ENGINES = {
    "ENG-C": "Compounding",
    "ENG-R": "Reflexive Repricing",
    "ENG-X": "Convexity",
}
EXPECTED_FUTURE_OBJECTS = {
    "EngineThesis",
    "PositionPassport",
    "AssetGraduationEvent",
    "BookState",
    "MetaAllocationResearchState",
}
EXPECTED_MIGRATION_INVARIANTS = {
    "NO_SILENT_THESIS_MIGRATION",
    "HISTORICAL_IDENTITIES_IMMUTABLE",
    "ENGINE_CHANGE_REQUIRES_GOVERNED_EVENT",
    "RESEARCH_PASS_DOES_NOT_IMPLY_CAPITAL_PASS",
    "CLAIM_AUTHORITY_LE_EVIDENCE_AUTHORITY",
}
```

- [ ] **Step 3: Implement positive invariants**

`validate_contract()` must fail unless:

- stage is exactly `ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE`;
- mother objective is exact;
- engine IDs are exactly `ENG-C`, `ENG-R`, `ENG-X` with unique IDs;
- `engine_registry_closed_world` is `false`;
- ontology distinction booleans are all `true`;
- E equals `horizontal_evidence_authority_plane`;
- S equals `horizontal_survival_constraint`;
- `BOOK-CASH.is_return_engine` is `false`;
- all required migration invariants exist;
- all authority booleans for mutation / promotion / sizing / trading / execution are `false`;
- all prohibited interpretation tokens exist.

`validate_successor_map()` must fail unless:

- `CAP-R-01` historical meaning remains `Regime Causal Decomposition`;
- `CAP-R-01.redefined_in_place` is `false`;
- `ENG-R.must_not_alias` contains `CAP-R-01`;
- `CAP-XS-01` is deferred to typed successor split;
- `CAP-V-01` is deferred to routed price interpretation successor;
- all five future object identities exist and have `implementation_authority_in_ME0 == false`;
- all five deferred migrations exist and none is authorized.

`validate_state()` must fail unless Human Gate is pending, design approval is accepted, and every implementation authority is `false`.

- [ ] **Step 4: Implement historical non-regression checks**

Read:

```text
docs/architecture/r2_3b1/CAP-R-01-SPEC-v0.1.json
docs/architecture/r2_3b1/CAP-XS-01-SPEC-v0.1.json
docs/architecture/r2_3b1/CAP-V-01-SPEC-v0.1.json
docs/architecture/yip0/YIP0-PHILOSOPHY-CONTRACT-v0.1.json
```

Assert at minimum:

```python
cap_r["identity"]["name"] == "Regime Causal Decomposition"
cap_r["identity"]["semantic_parent"] == "P.capital"
cap_xs["identity"]["name"] == "Structural Asymmetry Source Mapper"
cap_v["identity"]["name"] == "Price-Implied Expectations"
yip0["stage"] == "YIP0_INVESTMENT_PHILOSOPHY_CANON"
```

ME0 validator must not rewrite these files; it only proves they still retain their accepted identity.

- [ ] **Step 5: Add negative mutation tests**

Extend `tests/test_me0_multi_engine_ontology.py` with these tests using `copy.deepcopy`:

```python
def test_closed_world_engine_registry_is_rejected(self):
    contract = me0.load_json(me0.CONTRACT_PATH)
    contract["governance"]["engine_registry_closed_world"] = True
    with self.assertRaises(ValueError):
        me0.validate_contract(contract)


def test_cap_r_alias_to_eng_r_is_rejected(self):
    successor_map = me0.load_json(me0.SUCCESSOR_MAP_PATH)
    eng_r = next(x for x in successor_map["successor_roles"] if x["role_id"] == "ENG-R")
    eng_r["must_not_alias"] = []
    with self.assertRaises(ValueError):
        me0.validate_successor_map(successor_map)


def test_cash_as_engine_is_rejected(self):
    contract = me0.load_json(me0.CONTRACT_PATH)
    contract["book_roles"]["BOOK-CASH"]["is_return_engine"] = True
    with self.assertRaises(ValueError):
        me0.validate_contract(contract)


def test_silent_thesis_migration_is_rejected(self):
    contract = me0.load_json(me0.CONTRACT_PATH)
    contract["migration_invariants"].remove("NO_SILENT_THESIS_MIGRATION")
    with self.assertRaises(ValueError):
        me0.validate_contract(contract)


def test_trading_authority_is_rejected(self):
    contract = me0.load_json(me0.CONTRACT_PATH)
    contract["governance"]["buy_sell_hold_authority"] = True
    with self.assertRaises(ValueError):
        me0.validate_contract(contract)
```

- [ ] **Step 6: Run focused tests and validator**

```bash
python -m unittest tests.test_me0_multi_engine_ontology -v
python scripts/validate_me0_multi_engine_ontology.py
```

Expected: all tests PASS and validator exits 0 with a concise line such as:

```text
me0_engines=3 state=candidate_started status=valid
```

- [ ] **Step 7: Commit Task 4**

```bash
git add scripts/validate_me0_multi_engine_ontology.py tests/test_me0_multi_engine_ontology.py
git commit -m "test: validate ME0 multi-engine authority invariants"
```

---

### Task 5: CI Integration and Repository-Wide Non-Regression

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: `scripts/validate_me0_multi_engine_ontology.py`.
- Produces: ME0 candidate qualification inside the existing `contracts` repository gate.

- [ ] **Step 1: Add ME0 validator after YIP0 validation**

Insert exactly:

```yaml
      - run: python scripts/validate_me0_multi_engine_ontology.py
```

immediately after:

```yaml
      - run: python scripts/validate_yip0_philosophy.py
```

and before unittest discovery.

- [ ] **Step 2: Run focused and repository-wide tests**

```bash
python scripts/validate_me0_multi_engine_ontology.py
python scripts/validate_yip0_philosophy.py
python scripts/validate_r2_3b1_p0_specs.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS. Any regression in YIP0 or R2.3-B1 blocks ME0.

- [ ] **Step 3: Run repository validator set used by CI where local dependencies permit**

```bash
python scripts/validate_repository.py
python scripts/build_canon_status.py --check
python scripts/check_governance.py
```

Expected: PASS. ME0 must not require a Canon projection update because it is still a parallel candidate authority pack.

- [ ] **Step 4: Commit Task 5**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add ME0 ontology authority gate"
```

---

### Task 6: Machine Qualification, Candidate State Promotion, and Human Review Stop

**Files:**
- Modify after exact-head CI success: `docs/architecture/me0/ME0-STATE.json`
- Modify only if needed for reviewer clarity: PR #47 body

**Interfaces:**
- Consumes: exact-head GitHub Actions `repository-gates` result.
- Produces: `candidate_ready_for_human_review` state and a hard stop before Human Acceptance.

- [ ] **Step 1: Push implementation commits and capture exact head SHA**

Record the branch exact head before interpreting CI.

- [ ] **Step 2: Verify exact-head repository-gates**

Use GitHub commit status / workflow run tools. Both `contracts` and `governance` must be green for the exact head. A green run on an older SHA does not qualify the candidate.

- [ ] **Step 3: Promote state only after exact-head green**

Change only these lifecycle fields:

```json
{
  "status": "candidate_ready_for_human_review",
  "machine_qualification": {
    "decision": "passed",
    "exact_head_sha": "<exact actual head sha>",
    "contracts_gate": "passed",
    "governance_gate": "passed"
  },
  "next_gate": "HUMAN_REVIEW"
}
```

The actual SHA must be copied from GitHub; never pre-fill or guess it.

- [ ] **Step 4: Re-run exact-head CI after the state-only commit**

Because the state update creates a new head, machine qualification must be re-established on the new exact head. If the first state update references the immediately previous qualified head, record it as `qualification_basis_sha`; the final Human Review candidate head itself must also be green.

- [ ] **Step 5: Confirm the Human Review card and PR remain pending**

The following must still be true:

```text
human_gate.decision = pending
PR draft = true
merged = false
```

Do not create Human Acceptance receipt. Do not merge. Do not modify Constitution, schemas, Registry or runtime.

- [ ] **Step 6: Stop and request Human Review**

Present the user with the 16 review dimensions and the exact acceptance token:

```text
ACCEPT_ME0_MULTI_ENGINE_INVESTMENT_ONTOLOGY_AUTHORITY_FREEZE
```

No implementation task after this step is authorized by this plan.

---

## Self-Review Checklist

### Spec coverage

- First-principles distinction among target, state, engine, thesis and capital expression: Task 1.
- C/R/X open-world Genesis Engine Set: Task 1 + Task 4.
- P/N/E/V/S re-positioning as shared primitives/services/constraints: Task 1.
- Cash as Book role, not engine: Task 1 + negative test.
- `CAP-R-01` versus `ENG-R` namespace conflict: Task 2 + negative test.
- `Xs` future split: Task 2.
- Routed V successor role: Task 2.
- Future object identities without premature schema implementation: Task 2.
- No Silent Thesis Migration: Task 1 + negative test.
- Historical ledger preservation: Task 2 + Task 4.
- Evidence / Survival supremacy: Task 1 + Task 4.
- Human Gate / no-trading boundary: Task 3 + Task 4.
- Exact-head CI qualification: Task 5 + Task 6.

### Explicitly deferred beyond ME0

The following are intentionally **not** implemented by this plan:

- `EngineThesis` JSON Schema;
- `PositionPassport` JSON Schema;
- `AssetGraduationEvent` runtime/state machine;
- `BookState` or portfolio schemas;
- `MetaAllocationResearchState` implementation;
- `A2 Return Engine Route` implementation;
- `CAP-REG-01` creation;
- `CAP-XS-01` split implementation;
- `CAP-V-01` routed successor implementation;
- C/R/X production runtimes;
- Market Clock L/ERN/N four-phase/eight-state contract;
- any portfolio weights, sizing or execution.

These belong to ME1–ME5 and require their own accepted designs.
