# YF3N0-C Prospective Prediction & Reality Settlement Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the accepted YF3N0-C prospective-prediction protocol as a deterministic, fail-closed, candidate-only contract system that preregisters Three-Non mechanism claims before outcomes are known, atomically seals evidence/prediction/resolution rules, supports Full-vs-ablation-vs-baseline comparison, performs blind resolution and lawful settlement, and evaluates Canon-promotion gates without enrolling real cases or granting final Canon authority.

**Architecture:** Reuse the repository's existing ME1 style: JSON Schema 2020-12 contracts, Point-in-Time timestamps, deterministic Python validation, synthetic Gold/hard-negative fixtures, `unittest`, and a fail-closed repository validator wired into `repository-gates`. YF3N0-C remains stacked on the accepted YF3N0-B branch; all runtime objects are candidate research objects with zero portfolio/trading/psychometric authority. The implementation separates six lawful objects (`ProspectiveCase → EvidenceSeal → PredictionContract + ResolutionContract atomic bundle → SettlementRecord → QualificationState`) and never allows future evidence to mutate preregistered claims.

**Tech Stack:** Python 3.12 standard library (`dataclasses` not required; use dictionaries to match repository patterns), `hashlib.sha256`, `json`, `datetime`, `pathlib`, `jsonschema==4.25.1` Draft 2020-12 + `FormatChecker`, `unittest`, JSON/Markdown fixtures, GitHub Actions existing `repository-gates` workflow.

**Spec:** `docs/superpowers/specs/2026-08-24-yf3n0-c-prospective-prediction-reality-settlement-design.md`

## Global Constraints

- Parent authority is YF3N0-B only; this implementation must not mutate SOUL, ME0, ME1, or any accepted ontology outside the dedicated YF3N0-C namespace.
- YF3N0-C is prospective qualification, not scientific proof and not a universal success predictor.
- Lawful analysis unit remains `Actor × ProblemDomain × Context × PointInTime`.
- Human Grammar remains `非理性痴迷 × 非对称优势 × 非线性回报`; machine ontology remains `PIP ∧ EAA ∧ NLP`.
- Primary hypotheses remain exactly `H1_DURATION`, `H2_EDGE`, `H3_LEVERAGE`, `H4_CONJUNCTIVE`, `H5_WEAKEST_LINK`.
- Genesis cohort architecture remains exactly 12 slots = 3 domains (`entrepreneurship`, `investment_capital`, `ai_native_os`) × 4 structural types (`full_candidate`, `ablation_candidate`, `uncertain_candidate`, `exogenous_control`).
- Implementation creates **slot definitions and synthetic fixtures only**. `real_case_enrollment_authorized` must remain `false` until a later explicit Human Gate.
- Every enrolled case must eventually have exactly four Primary Predictions (`P1_PIP_PERSISTENCE`, `P2_EAA_PERSISTENCE_OR_DECAY`, `P3_NLP_ACTIVATION_OR_FAILURE`, `P4_INTEGRATED_FORCE_POTENTIAL`) and at most two Secondary Predictions.
- Primary prediction count is not configurable in v0.1.
- Full model, three single-primitive ablations (`ABLATE_PIP`, `ABLATE_EAA`, `ABLATE_NLP`), and `BASELINE` must forecast the **same frozen outcome definition** for any comparable probabilistic event.
- Probability forecasts are lawful only for binary events whose resolution rule can return `YES`, `NO`, or `INDETERMINATE`.
- `INDETERMINATE` is a lawful unresolved state and must never be converted to support, failure, 0, 1, or a Brier score.
- Mechanism claims use causal settlement states `SUPPORTED`, `PARTIALLY_SUPPORTED`, `FALSIFIED`, `INDETERMINATE`; they are not forced into pseudo-probabilities.
- Evidence Seal must precede the atomic preregistration bundle; PredictionContract and ResolutionContract share one immutable preregistration seal timestamp and evidence digest.
- Prediction/Resolution rules cannot cite evidence with `known_as_of` later than the frozen evidence cutoff.
- Settlement is append-only relative to preregistration: settlement can reference a sealed contract but cannot mutate it.
- Required settlement horizons are exactly `T90`, `T180`, `T365`; `T730` is optional only if declared before the preregistration seal.
- Blind resolution payload must omit model probabilities, model identity preference, Brier values, and analyst narrative about whether a forecast was optimistic or pessimistic.
- Brier score for a resolved binary event is `(probability - outcome)^2`; no Brier score is computed for `INDETERMINATE`.
- Three-Non remains conjunctive, not compensatory: a falsified primitive cannot be offset by high support for the other two when constructing `ForcePotential` qualification.
- Final YF3N0-C qualification outcome is one of `CANON_PROMOTION_READY`, `PARTIAL_CANON_REFRAME_REQUIRED`, `FIRST_PRINCIPLES_CANON_REJECTED`, `INSUFFICIENT_EVIDENCE`.
- No single global “Three-Non accuracy score” may be emitted. Final outputs are evidence matrices, calibration summaries, gate statuses, falsification counts, and narrative-safe qualification states.
- `ClaimAuthority <= EvidenceAuthority` remains mandatory.
- `Reality outranks Three-Non`; `Survival outranks Nonlinearity` remain inherited constitutional constraints.
- No security recommendation, portfolio sizing, manager approval, trade execution, performance guarantee, psychometric diagnosis, or capital movement authority may appear in schemas, fixtures, reports, or scripts.
- PR #59/#60 merge and YF3N0 final Canon promotion remain outside this implementation plan.

---

## File Structure

Create or modify the following focused files:

```text
packages/contracts/schemas/yf3n0/
  prospective-case.schema.json
  evidence-seal.schema.json
  prediction-contract.schema.json
  resolution-contract.schema.json
  preregistration-bundle.schema.json
  settlement-record.schema.json
  qualification-state.schema.json

docs/architecture/yf3n0/
  YF3N0-C-PROTOCOL-v0.1.json
  YF3N0-C-GENESIS-COHORT-SLOTS-v0.1.json
  YF3N0-C-STATE.json
  YF3N0-C-HUMAN-REVIEW-CARD-v0.1.md
  fixtures/
    synthetic-full-case.json
    synthetic-evidence-seal.json
    synthetic-preregistration-bundle.json
    synthetic-settlements.json
    synthetic-qualification-state.json
    hard-negatives.json

docs/human-projection/
  YF3N0-C-PROSPECTIVE-PREDICTION-PROTOCOL-v0.1.md

scripts/
  yf3n0_prospective.py
  validate_yf3n0_c_prospective.py

tests/
  test_yf3n0_c_prospective.py

.github/workflows/ci.yml
```

No production API, database, scheduler, automation, external case crawler, or user-facing enrollment UI is added in v0.1.

---

### Task 1: Freeze YF3N0-C Machine Contracts and Protocol Registry

**Files:**
- Create: `packages/contracts/schemas/yf3n0/prospective-case.schema.json`
- Create: `packages/contracts/schemas/yf3n0/evidence-seal.schema.json`
- Create: `packages/contracts/schemas/yf3n0/prediction-contract.schema.json`
- Create: `packages/contracts/schemas/yf3n0/resolution-contract.schema.json`
- Create: `packages/contracts/schemas/yf3n0/preregistration-bundle.schema.json`
- Create: `packages/contracts/schemas/yf3n0/settlement-record.schema.json`
- Create: `packages/contracts/schemas/yf3n0/qualification-state.schema.json`
- Create: `docs/architecture/yf3n0/YF3N0-C-PROTOCOL-v0.1.json`
- Create: `tests/test_yf3n0_c_prospective.py`

**Interfaces:**
- Consumes: accepted YF3N0-C Written Spec and inherited YF3N0-B primitive IDs `PIP`, `EAA`, `NLP`.
- Produces: seven Draft 2020-12 schemas and one protocol registry containing the immutable v0.1 hypotheses, prediction IDs, model variants, settlement states, horizons, promotion gates, and zero-authority contract.

- [ ] **Step 1: Write failing schema and protocol-identity tests**

Create `tests/test_yf3n0_c_prospective.py` with repository helpers and these first tests:

```python
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "packages" / "contracts" / "schemas" / "yf3n0"
ARCH = ROOT / "docs" / "architecture" / "yf3n0"
PROTOCOL = ARCH / "YF3N0-C-PROTOCOL-v0.1.json"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class YF3N0CContractTests(unittest.TestCase):
    def test_all_local_schemas_are_valid_draft_202012(self):
        names = {
            "prospective-case.schema.json",
            "evidence-seal.schema.json",
            "prediction-contract.schema.json",
            "resolution-contract.schema.json",
            "preregistration-bundle.schema.json",
            "settlement-record.schema.json",
            "qualification-state.schema.json",
        }
        self.assertEqual({p.name for p in SCHEMA_DIR.glob("*.json")}, names)
        for path in SCHEMA_DIR.glob("*.json"):
            Draft202012Validator.check_schema(load_json(path))

    def test_protocol_freezes_exact_hypotheses_predictions_and_horizons(self):
        protocol = load_json(PROTOCOL)
        self.assertEqual(protocol["hypotheses"], [
            "H1_DURATION",
            "H2_EDGE",
            "H3_LEVERAGE",
            "H4_CONJUNCTIVE",
            "H5_WEAKEST_LINK",
        ])
        self.assertEqual(protocol["primary_prediction_ids"], [
            "P1_PIP_PERSISTENCE",
            "P2_EAA_PERSISTENCE_OR_DECAY",
            "P3_NLP_ACTIVATION_OR_FAILURE",
            "P4_INTEGRATED_FORCE_POTENTIAL",
        ])
        self.assertEqual(protocol["required_horizons"], ["T90", "T180", "T365"])
        self.assertEqual(protocol["model_variants"], [
            "FULL", "ABLATE_PIP", "ABLATE_EAA", "ABLATE_NLP", "BASELINE"
        ])

    def test_protocol_has_zero_external_authority(self):
        authority = load_json(PROTOCOL)["authority"]
        self.assertTrue(authority)
        self.assertTrue(all(value is False for value in authority.values()))
```

- [ ] **Step 2: Run Task 1 tests and verify RED**

Run:

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CContractTests -v
```

Expected: FAIL because the YF3N0-C schemas and protocol registry do not exist.

- [ ] **Step 3: Create schema identities and stable object boundaries**

Use `$schema: "https://json-schema.org/draft/2020-12/schema"`, `additionalProperties: false` on every stable object, and these schema IDs:

```text
urn:yuanli-invest:schema:yf3n0-prospective-case:1.0.0
urn:yuanli-invest:schema:yf3n0-evidence-seal:1.0.0
urn:yuanli-invest:schema:yf3n0-prediction-contract:1.0.0
urn:yuanli-invest:schema:yf3n0-resolution-contract:1.0.0
urn:yuanli-invest:schema:yf3n0-preregistration-bundle:1.0.0
urn:yuanli-invest:schema:yf3n0-settlement-record:1.0.0
urn:yuanli-invest:schema:yf3n0-qualification-state:1.0.0
```

`prospective-case.schema.json` must require:

```text
case_id
schema_version
slot_id
actor_label
problem_domain
context
reference_group
structural_type
recorded_at
known_as_of
authority
```

`evidence-seal.schema.json` must require:

```text
evidence_seal_id
case_id
schema_version
sealed_at
knowledge_cutoff
evidence_manifest
unknowns
excluded_future_information
evidence_digest_sha256
authority
```

`prediction-contract.schema.json` must require exactly four primary prediction records and allow zero-to-two secondary prediction records. Each primary record requires:

```text
prediction_id
hypothesis_id
role
outcome_definition_id
forecast_channel
full_forecast
ablation_forecasts
baseline_forecast
falsifiers
source_evidence_refs
```

For `forecast_channel == "binary"`, every model forecast has `probability` in `[0, 1]`. For `forecast_channel == "causal"`, use `expected_state` drawn from the causal settlement vocabulary; do not add a probability field.

`resolution-contract.schema.json` must require one resolution rule per frozen outcome definition, with:

```text
outcome_definition_id
event_definition
resolution_source_rule
resolution_cutoff_rule
allowed_binary_states
allowed_causal_states
indeterminate_rule
```

`preregistration-bundle.schema.json` must contain exactly one `prediction_contract`, one `resolution_contract`, one shared `sealed_at`, one `evidence_digest_sha256`, and one `bundle_digest_sha256`.

`settlement-record.schema.json` must never include a field capable of replacing or editing a prediction probability, outcome definition, or resolution rule.

`qualification-state.schema.json` must expose gate-by-gate state and final qualification outcome but must not expose a single aggregate accuracy score.

- [ ] **Step 4: Create `YF3N0-C-PROTOCOL-v0.1.json`**

Freeze this top-level content shape:

```json
{
  "protocol_id": "YF3N0-C-v0.1",
  "schema_version": "1.0.0",
  "hypotheses": ["H1_DURATION", "H2_EDGE", "H3_LEVERAGE", "H4_CONJUNCTIVE", "H5_WEAKEST_LINK"],
  "primary_prediction_ids": ["P1_PIP_PERSISTENCE", "P2_EAA_PERSISTENCE_OR_DECAY", "P3_NLP_ACTIVATION_OR_FAILURE", "P4_INTEGRATED_FORCE_POTENTIAL"],
  "max_secondary_predictions_per_case": 2,
  "model_variants": ["FULL", "ABLATE_PIP", "ABLATE_EAA", "ABLATE_NLP", "BASELINE"],
  "required_horizons": ["T90", "T180", "T365"],
  "optional_horizons": ["T730"],
  "binary_resolution_states": ["YES", "NO", "INDETERMINATE"],
  "causal_settlement_states": ["SUPPORTED", "PARTIALLY_SUPPORTED", "FALSIFIED", "INDETERMINATE"],
  "qualification_outcomes": ["CANON_PROMOTION_READY", "PARTIAL_CANON_REFRAME_REQUIRED", "FIRST_PRINCIPLES_CANON_REJECTED", "INSUFFICIENT_EVIDENCE"],
  "promotion_gates": ["C_G1_PROTOCOL_INTEGRITY", "C_G2_NO_RESOLUTION_DRIFT", "C_G3_PRIMITIVE_DISCRIMINATION", "C_G4_ABLATION_VALUE", "C_G5_CROSS_DOMAIN_ROBUSTNESS", "C_G6_NO_CONSTITUTIONAL_BREACH"],
  "authority": {
    "real_case_enrollment_authority": false,
    "prediction_clock_start_authority": false,
    "canon_promotion_authority": false,
    "psychometric_authority": false,
    "security_recommendation_authority": false,
    "portfolio_sizing_authority": false,
    "trade_execution_authority": false,
    "manager_approval_authority": false
  }
}
```

- [ ] **Step 5: Run Task 1 tests and verify GREEN**

Run:

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CContractTests -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 1**

```bash
git add packages/contracts/schemas/yf3n0 docs/architecture/yf3n0/YF3N0-C-PROTOCOL-v0.1.json tests/test_yf3n0_c_prospective.py
git commit -m "YF3N0-C: add prospective protocol contracts"
```

---

### Task 2: Implement Canonical Hashing, Evidence Seal, and Atomic Preregistration

**Files:**
- Create: `scripts/yf3n0_prospective.py`
- Modify: `tests/test_yf3n0_c_prospective.py`

**Interfaces:**
- Consumes: schema-shaped Python dictionaries from Task 1.
- Produces:
  - `canonical_json_bytes(value: dict) -> bytes`
  - `sha256_json(value: dict) -> str`
  - `verify_digest(value: dict, expected_digest: str) -> bool`
  - `validate_evidence_seal(case: dict, seal: dict) -> None`
  - `validate_atomic_preregistration(evidence_seal: dict, bundle: dict) -> None`

- [ ] **Step 1: Write failing seal-integrity tests**

Append:

```python
from copy import deepcopy
from scripts import yf3n0_prospective as yf3


class YF3N0CSealTests(unittest.TestCase):
    def test_canonical_hash_is_key_order_independent(self):
        left = {"b": 2, "a": {"y": 2, "x": 1}}
        right = {"a": {"x": 1, "y": 2}, "b": 2}
        self.assertEqual(yf3.sha256_json(left), yf3.sha256_json(right))

    def test_mutating_sealed_payload_breaks_digest(self):
        payload = {"case_id": "SYN-001", "claims": ["a"]}
        digest = yf3.sha256_json(payload)
        mutated = deepcopy(payload)
        mutated["claims"].append("b")
        self.assertFalse(yf3.verify_digest(mutated, digest))

    def test_preregistration_must_share_evidence_digest_and_timestamp(self):
        evidence = make_synthetic_evidence_seal()
        bundle = make_synthetic_preregistration_bundle(evidence)
        yf3.validate_atomic_preregistration(evidence, bundle)
        broken = deepcopy(bundle)
        broken["resolution_contract"]["sealed_at"] = "2026-08-25T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "atomic preregistration timestamp mismatch"):
            yf3.validate_atomic_preregistration(evidence, broken)
```

Add local test factories with deterministic synthetic values; do not load future real-case content.

- [ ] **Step 2: Run seal tests and verify RED**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CSealTests -v
```

Expected: FAIL because `scripts/yf3n0_prospective.py` does not exist.

- [ ] **Step 3: Implement deterministic canonical JSON hashing**

Create `scripts/yf3n0_prospective.py` beginning with:

```python
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone


def canonical_json_bytes(value: dict) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_json(value: dict) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def verify_digest(value: dict, expected_digest: str) -> bool:
    return sha256_json(value) == expected_digest


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)
```

- [ ] **Step 4: Implement Evidence Seal and atomic preregistration invariants**

`validate_evidence_seal(case, seal)` must enforce:

```python
require(seal["case_id"] == case["case_id"], "evidence seal case mismatch")
require(parse_dt(case["known_as_of"]) <= parse_dt(seal["knowledge_cutoff"]), "case knowledge exceeds cutoff")
require(parse_dt(seal["knowledge_cutoff"]) <= parse_dt(seal["sealed_at"]), "knowledge cutoff exceeds seal time")
```

Every evidence-manifest item with a `known_as_of` must satisfy `known_as_of <= knowledge_cutoff`.

`validate_atomic_preregistration(evidence_seal, bundle)` must enforce:

```python
prediction = bundle["prediction_contract"]
resolution = bundle["resolution_contract"]
require(bundle["evidence_digest_sha256"] == evidence_seal["evidence_digest_sha256"], "preregistration evidence digest mismatch")
require(prediction["evidence_digest_sha256"] == bundle["evidence_digest_sha256"], "prediction evidence digest mismatch")
require(resolution["evidence_digest_sha256"] == bundle["evidence_digest_sha256"], "resolution evidence digest mismatch")
require(prediction["sealed_at"] == resolution["sealed_at"] == bundle["sealed_at"], "atomic preregistration timestamp mismatch")
```

Also verify the bundle digest over a digestable copy that omits only `bundle_digest_sha256` itself.

- [ ] **Step 5: Run seal tests and verify GREEN**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CSealTests -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add scripts/yf3n0_prospective.py tests/test_yf3n0_c_prospective.py
git commit -m "YF3N0-C: enforce atomic preregistration seals"
```

---

### Task 3: Freeze the 12-Slot Genesis Cohort and Fail-Closed Eligibility Rules

**Files:**
- Create: `docs/architecture/yf3n0/YF3N0-C-GENESIS-COHORT-SLOTS-v0.1.json`
- Modify: `scripts/yf3n0_prospective.py`
- Modify: `tests/test_yf3n0_c_prospective.py`

**Interfaces:**
- Produces:
  - `validate_genesis_slots(slots: dict) -> None`
  - `validate_case_eligibility(case: dict, slot: dict, evidence_seal: dict, protocol_state: dict) -> None`

- [ ] **Step 1: Write failing cohort-structure tests**

```python
class YF3N0CCohortTests(unittest.TestCase):
    def test_genesis_cohort_is_exactly_three_by_four(self):
        slots = load_json(ARCH / "YF3N0-C-GENESIS-COHORT-SLOTS-v0.1.json")
        yf3.validate_genesis_slots(slots)
        self.assertEqual(len(slots["slots"]), 12)
        self.assertEqual({s["domain"] for s in slots["slots"]}, {
            "entrepreneurship", "investment_capital", "ai_native_os"
        })
        self.assertEqual({s["structural_type"] for s in slots["slots"]}, {
            "full_candidate", "ablation_candidate", "uncertain_candidate", "exogenous_control"
        })

    def test_v01_slots_do_not_enroll_real_actors(self):
        slots = load_json(ARCH / "YF3N0-C-GENESIS-COHORT-SLOTS-v0.1.json")
        self.assertTrue(all(slot["actor_ref"] is None for slot in slots["slots"]))
        self.assertTrue(all(slot["enrollment_status"] == "UNFILLED" for slot in slots["slots"]))
```

- [ ] **Step 2: Run cohort tests and verify RED**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CCohortTests -v
```

Expected: FAIL because the slot registry does not exist.

- [ ] **Step 3: Create exact 12-slot registry**

Use deterministic IDs:

```text
ENT-FULL-01, ENT-ABL-01, ENT-UNC-01, ENT-EXO-01
INV-FULL-01, INV-ABL-01, INV-UNC-01, INV-EXO-01
AIO-FULL-01, AIO-ABL-01, AIO-UNC-01, AIO-EXO-01
```

Every slot must include:

```json
{
  "slot_id": "ENT-FULL-01",
  "domain": "entrepreneurship",
  "structural_type": "full_candidate",
  "actor_ref": null,
  "enrollment_status": "UNFILLED",
  "real_case": false
}
```

- [ ] **Step 4: Implement eligibility checks without authorizing enrollment**

`validate_case_eligibility` must verify:

```text
case slot/domain/type matches slot
case has explicit reference_group
case known_as_of <= evidence knowledge_cutoff
at least one future 365-day mechanism is observable by the declared resolution rule
case has no private-secret requirement flag
evidence contains at least one non-self-report item
protocol_state.real_case_enrollment_authorized == true for any real_case == true
```

For v0.1, a real case presented against state `false` must raise:

```text
real case enrollment not authorized
```

- [ ] **Step 5: Add hard test that protocol implementation cannot accidentally start enrollment**

```python
with self.assertRaisesRegex(ValueError, "real case enrollment not authorized"):
    yf3.validate_case_eligibility(real_case, slot, seal, {"real_case_enrollment_authorized": False})
```

- [ ] **Step 6: Run cohort tests and verify GREEN**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CCohortTests -v
```

Expected: PASS.

- [ ] **Step 7: Commit Task 3**

```bash
git add docs/architecture/yf3n0/YF3N0-C-GENESIS-COHORT-SLOTS-v0.1.json scripts/yf3n0_prospective.py tests/test_yf3n0_c_prospective.py
git commit -m "YF3N0-C: freeze prospective genesis cohort slots"
```

---

### Task 4: Enforce Four Primary Predictions and Full/Ablation/Baseline Comparability

**Files:**
- Modify: `scripts/yf3n0_prospective.py`
- Modify: `tests/test_yf3n0_c_prospective.py`

**Interfaces:**
- Produces:
  - `validate_prediction_contract(contract: dict, protocol: dict) -> None`
  - `validate_model_comparability(prediction: dict) -> None`
  - `force_candidate_state(primitive_states: dict) -> str`

- [ ] **Step 1: Write failing prediction-shape and comparability tests**

```python
class YF3N0CPredictionTests(unittest.TestCase):
    def test_prediction_contract_has_exactly_four_primaries(self):
        contract = make_prediction_contract()
        yf3.validate_prediction_contract(contract, load_json(PROTOCOL))
        primaries = [p for p in contract["predictions"] if p["role"] == "PRIMARY"]
        self.assertEqual([p["prediction_id"] for p in primaries], [
            "P1_PIP_PERSISTENCE",
            "P2_EAA_PERSISTENCE_OR_DECAY",
            "P3_NLP_ACTIVATION_OR_FAILURE",
            "P4_INTEGRATED_FORCE_POTENTIAL",
        ])

    def test_more_than_two_secondary_predictions_is_rejected(self):
        contract = make_prediction_contract(secondary_count=3)
        with self.assertRaisesRegex(ValueError, "secondary prediction limit exceeded"):
            yf3.validate_prediction_contract(contract, load_json(PROTOCOL))

    def test_full_ablations_and_baseline_share_same_outcome_definition(self):
        prediction = make_binary_primary_prediction()
        yf3.validate_model_comparability(prediction)
        broken = deepcopy(prediction)
        broken["ablation_forecasts"]["ABLATE_EAA"]["outcome_definition_id"] = "DIFFERENT-OUTCOME"
        with self.assertRaisesRegex(ValueError, "model outcome definition mismatch"):
            yf3.validate_model_comparability(broken)
```

- [ ] **Step 2: Run prediction tests and verify RED**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CPredictionTests -v
```

Expected: FAIL because validation functions do not exist.

- [ ] **Step 3: Implement exact prediction-count and model-variant validation**

`validate_prediction_contract` must:

```python
primary = [p for p in contract["predictions"] if p["role"] == "PRIMARY"]
secondary = [p for p in contract["predictions"] if p["role"] == "SECONDARY"]
require([p["prediction_id"] for p in primary] == protocol["primary_prediction_ids"], "primary prediction contract mismatch")
require(len(secondary) <= protocol["max_secondary_predictions_per_case"], "secondary prediction limit exceeded")
```

For binary forecasts, require every model variant probability to satisfy `0.0 <= p <= 1.0`.

For causal forecasts, prohibit `probability` and require lawful `expected_state`.

- [ ] **Step 4: Implement model comparability invariant**

For each primary prediction, require `FULL`, each ablation, and `BASELINE` to cite the same `outcome_definition_id` and `resolution_rule_id`. Do not allow model-specific outcome wording.

- [ ] **Step 5: Implement H5 weakest-link/no-compensation helper**

```python
def force_candidate_state(primitive_states: dict) -> str:
    required = {"PIP", "EAA", "NLP"}
    require(set(primitive_states) == required, "primitive state set mismatch")
    if any(primitive_states[key] == "FALSIFIED" for key in required):
        return "NOT_FULL_FORCE_CANDIDATE"
    if all(primitive_states[key] == "SUPPORTED" for key in required):
        return "FULL_FORCE_CANDIDATE"
    if any(primitive_states[key] == "INDETERMINATE" for key in required):
        return "INDETERMINATE"
    return "PARTIAL_FORCE_CANDIDATE"
```

Add a test that `PIP=SUPPORTED`, `EAA=FALSIFIED`, `NLP=SUPPORTED` cannot return `FULL_FORCE_CANDIDATE`.

- [ ] **Step 6: Run prediction tests and verify GREEN**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CPredictionTests -v
```

Expected: PASS.

- [ ] **Step 7: Commit Task 4**

```bash
git add scripts/yf3n0_prospective.py tests/test_yf3n0_c_prospective.py
git commit -m "YF3N0-C: enforce prediction and ablation comparability"
```

---

### Task 5: Implement Blind Resolution, Binary Scoring, and Causal Settlement

**Files:**
- Modify: `scripts/yf3n0_prospective.py`
- Modify: `tests/test_yf3n0_c_prospective.py`

**Interfaces:**
- Produces:
  - `build_blind_resolution_packet(bundle: dict, horizon: str, new_evidence_refs: list[dict]) -> dict`
  - `validate_binary_resolution(value: str) -> None`
  - `brier_score(probability: float, resolution: str) -> float | None`
  - `validate_causal_settlement(value: str) -> None`
  - `build_settlement_record(bundle: dict, resolution_output: dict, settled_at: str) -> dict`

- [ ] **Step 1: Write failing blind-resolution and scoring tests**

```python
class YF3N0CResolutionTests(unittest.TestCase):
    def test_blind_packet_omits_forecast_probabilities_and_model_variants(self):
        bundle = make_synthetic_preregistration_bundle(make_synthetic_evidence_seal())
        packet = yf3.build_blind_resolution_packet(bundle, "T180", [{"evidence_ref": "NEW-001"}])
        text = json.dumps(packet, sort_keys=True)
        self.assertNotIn("probability", text)
        self.assertNotIn("ABLATE_PIP", text)
        self.assertNotIn("BASELINE", text)
        self.assertNotIn("brier", text.lower())

    def test_brier_score_uses_only_yes_or_no(self):
        self.assertAlmostEqual(yf3.brier_score(0.8, "YES"), 0.04)
        self.assertAlmostEqual(yf3.brier_score(0.8, "NO"), 0.64)
        self.assertIsNone(yf3.brier_score(0.8, "INDETERMINATE"))

    def test_indeterminate_cannot_be_promoted_to_support(self):
        with self.assertRaisesRegex(ValueError, "invalid causal settlement state"):
            yf3.validate_causal_settlement("INDETERMINATE_AS_SUPPORT")
```

- [ ] **Step 2: Run resolution tests and verify RED**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CResolutionTests -v
```

Expected: FAIL because resolution helpers do not exist.

- [ ] **Step 3: Implement blind packet construction**

`build_blind_resolution_packet` must expose only:

```text
case_id
preregistration_bundle_id
horizon
outcome_definitions[]
resolution_rules[]
new_evidence_refs[]
```

It must not copy any model forecast object, probability, expected state, Brier score, analyst preference, or “was bullish/bearish” narrative.

- [ ] **Step 4: Implement lawful binary and causal state validation**

```python
BINARY_STATES = {"YES", "NO", "INDETERMINATE"}
CAUSAL_STATES = {"SUPPORTED", "PARTIALLY_SUPPORTED", "FALSIFIED", "INDETERMINATE"}


def brier_score(probability: float, resolution: str) -> float | None:
    validate_binary_resolution(resolution)
    if resolution == "INDETERMINATE":
        return None
    outcome = 1.0 if resolution == "YES" else 0.0
    return (probability - outcome) ** 2
```

- [ ] **Step 5: Implement append-only settlement record construction**

The returned settlement record may reference immutable preregistration IDs/digests and contain resolution outputs, Brier values, causal settlement states, and evidence refs. It must not contain replacement copies of editable prediction contracts.

Add a test asserting forbidden keys `replacement_prediction_contract`, `revised_probability`, `revised_resolution_rule` are absent.

- [ ] **Step 6: Run resolution tests and verify GREEN**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CResolutionTests -v
```

Expected: PASS.

- [ ] **Step 7: Commit Task 5**

```bash
git add scripts/yf3n0_prospective.py tests/test_yf3n0_c_prospective.py
git commit -m "YF3N0-C: add blind resolution and settlement scoring"
```

---

### Task 6: Enforce T90/T180/T365 Horizon Integrity and Optional Predeclared T730

**Files:**
- Modify: `scripts/yf3n0_prospective.py`
- Modify: `tests/test_yf3n0_c_prospective.py`

**Interfaces:**
- Produces:
  - `horizon_due_at(sealed_at: str, horizon: str) -> datetime`
  - `validate_settlement_timing(bundle: dict, horizon: str, settled_at: str) -> None`
  - `validate_optional_horizon(bundle: dict, horizon: str) -> None`

- [ ] **Step 1: Write failing timing tests**

```python
class YF3N0CHorizonTests(unittest.TestCase):
    def test_horizon_due_dates_are_fixed_day_offsets(self):
        sealed = "2026-08-24T00:00:00Z"
        self.assertEqual(yf3.horizon_due_at(sealed, "T90").isoformat(), "2026-11-22T00:00:00+00:00")
        self.assertEqual(yf3.horizon_due_at(sealed, "T180").isoformat(), "2027-02-20T00:00:00+00:00")
        self.assertEqual(yf3.horizon_due_at(sealed, "T365").isoformat(), "2027-08-24T00:00:00+00:00")

    def test_t730_is_rejected_when_not_predeclared(self):
        bundle = make_synthetic_preregistration_bundle(make_synthetic_evidence_seal(), optional_horizons=[])
        with self.assertRaisesRegex(ValueError, "T730 was not preregistered"):
            yf3.validate_optional_horizon(bundle, "T730")
```

- [ ] **Step 2: Run timing tests and verify RED**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CHorizonTests -v
```

Expected: FAIL because horizon helpers do not exist.

- [ ] **Step 3: Implement fixed horizon offsets**

Use:

```python
HORIZON_DAYS = {"T90": 90, "T180": 180, "T365": 365, "T730": 730}
```

Do not use locale month arithmetic; the contract names are fixed day offsets.

- [ ] **Step 4: Enforce no early settlement masquerading as final settlement**

`validate_settlement_timing` must reject a `T365` SettlementRecord whose `settled_at` is earlier than the T365 due timestamp. Early observations may be stored only under their actual declared horizon.

- [ ] **Step 5: Run timing tests and verify GREEN**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CHorizonTests -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 6**

```bash
git add scripts/yf3n0_prospective.py tests/test_yf3n0_c_prospective.py
git commit -m "YF3N0-C: enforce prospective settlement horizons"
```

---

### Task 7: Build Evidence Matrix and Six Canon-Promotion Gates Without a Global Score

**Files:**
- Modify: `scripts/yf3n0_prospective.py`
- Modify: `tests/test_yf3n0_c_prospective.py`

**Interfaces:**
- Produces:
  - `build_evidence_matrix(cases: list[dict], settlements: list[dict]) -> dict`
  - `evaluate_promotion_gates(matrix: dict, protocol_integrity: dict) -> dict`
  - `derive_qualification_outcome(gates: dict) -> str`

- [ ] **Step 1: Write failing qualification tests**

```python
class YF3N0CQualificationTests(unittest.TestCase):
    def test_evidence_matrix_has_no_global_accuracy_score(self):
        matrix = yf3.build_evidence_matrix(make_case_list(), make_settlement_list())
        serialized = json.dumps(matrix, sort_keys=True).lower()
        self.assertNotIn("global_accuracy", serialized)
        self.assertNotIn("overall_score", serialized)
        self.assertNotIn("three_non_accuracy", serialized)

    def test_unresolved_required_evidence_yields_insufficient_evidence(self):
        gates = {
            "C_G1_PROTOCOL_INTEGRITY": "PASS",
            "C_G2_NO_RESOLUTION_DRIFT": "PASS",
            "C_G3_PRIMITIVE_DISCRIMINATION": "INDETERMINATE",
            "C_G4_ABLATION_VALUE": "INDETERMINATE",
            "C_G5_CROSS_DOMAIN_ROBUSTNESS": "INDETERMINATE",
            "C_G6_NO_CONSTITUTIONAL_BREACH": "PASS"
        }
        self.assertEqual(yf3.derive_qualification_outcome(gates), "INSUFFICIENT_EVIDENCE")

    def test_constitutional_breach_blocks_canon_promotion(self):
        gates = make_all_pass_gates()
        gates["C_G6_NO_CONSTITUTIONAL_BREACH"] = "FAIL"
        self.assertNotEqual(yf3.derive_qualification_outcome(gates), "CANON_PROMOTION_READY")
```

- [ ] **Step 2: Run qualification tests and verify RED**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CQualificationTests -v
```

Expected: FAIL because qualification functions do not exist.

- [ ] **Step 3: Implement evidence matrix**

The matrix must preserve case/domain/model/horizon detail and include at minimum:

```text
primitive_settlements.PIP
primitive_settlements.EAA
primitive_settlements.NLP
integrated_force_state
binary_forecast_scores_by_model
indeterminate_counts
falsification_counts
ablation_comparisons
baseline_comparisons
domain_coverage
protocol_integrity_findings
constitutional_breaches
```

It may compute mean Brier values **per model over resolved comparable binary events**, but must not collapse all evidence into one global theory score.

- [ ] **Step 4: Implement six gate evaluators**

Gate semantics:

```text
C_G1_PROTOCOL_INTEGRITY:
  PASS only if every primary prediction and resolution rule was sealed before outcome evidence and every digest verifies.

C_G2_NO_RESOLUTION_DRIFT:
  PASS only if every settlement uses the frozen resolution rule/digest and no post-seal rule mutation exists.

C_G3_PRIMITIVE_DISCRIMINATION:
  PASS only if PIP/EAA/NLP each have enough resolved evidence to demonstrate non-trivial discrimination; a primitive with only uniformly supportive or entirely indeterminate cases cannot earn PASS.

C_G4_ABLATION_VALUE:
  PASS only if FULL is not systematically dominated by any single ablation across comparable resolved events; FAIL if one ablation consistently outperforms FULL and qualitative settlements show the removed primitive adds no mechanism information.

C_G5_CROSS_DOMAIN_ROBUSTNESS:
  PASS only if entrepreneurship plus at least one of investment_capital or ai_native_os show supported mechanism evidence under the same ontology.

C_G6_NO_CONSTITUTIONAL_BREACH:
  PASS only if no observed implementation/analysis breach redefines Three-Non as universal success, bypasses evidence authority, converts indeterminate to support, or leaks capital/psychometric authority.
```

Where the evidence is not yet sufficient to decide a gate, return `INDETERMINATE`, not `PASS`.

- [ ] **Step 5: Implement final outcome derivation**

Rules:

```text
all six PASS -> CANON_PROMOTION_READY
any G1/G2/G6 FAIL -> FIRST_PRINCIPLES_CANON_REJECTED
G4 FAIL with otherwise usable evidence -> PARTIAL_CANON_REFRAME_REQUIRED
any unresolved required gate and no decisive rejection -> INSUFFICIENT_EVIDENCE
other primitive/domain structural failures -> PARTIAL_CANON_REFRAME_REQUIRED
```

Add tests for all four outcomes.

- [ ] **Step 6: Run qualification tests and verify GREEN**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CQualificationTests -v
```

Expected: PASS.

- [ ] **Step 7: Commit Task 7**

```bash
git add scripts/yf3n0_prospective.py tests/test_yf3n0_c_prospective.py
git commit -m "YF3N0-C: add qualification matrix and canon gates"
```

---

### Task 8: Add Synthetic Gold Fixtures and Hard-Negative Protocol Attacks

**Files:**
- Create: `docs/architecture/yf3n0/fixtures/synthetic-full-case.json`
- Create: `docs/architecture/yf3n0/fixtures/synthetic-evidence-seal.json`
- Create: `docs/architecture/yf3n0/fixtures/synthetic-preregistration-bundle.json`
- Create: `docs/architecture/yf3n0/fixtures/synthetic-settlements.json`
- Create: `docs/architecture/yf3n0/fixtures/synthetic-qualification-state.json`
- Create: `docs/architecture/yf3n0/fixtures/hard-negatives.json`
- Modify: `tests/test_yf3n0_c_prospective.py`

**Interfaces:**
- Consumes: schemas + pure validation helpers from Tasks 1–7.
- Produces: one completely synthetic happy path and a named hard-negative pack used by the repository validator.

- [ ] **Step 1: Write failing fixture-validation tests**

```python
FIXTURES = ARCH / "fixtures"


class YF3N0CFixtureTests(unittest.TestCase):
    def test_synthetic_gold_chain_validates_end_to_end(self):
        case = load_json(FIXTURES / "synthetic-full-case.json")
        seal = load_json(FIXTURES / "synthetic-evidence-seal.json")
        bundle = load_json(FIXTURES / "synthetic-preregistration-bundle.json")
        yf3.validate_evidence_seal(case, seal)
        yf3.validate_atomic_preregistration(seal, bundle)
        yf3.validate_prediction_contract(bundle["prediction_contract"], load_json(PROTOCOL))

    def test_hard_negative_pack_contains_required_attacks(self):
        attacks = {item["attack_id"] for item in load_json(FIXTURES / "hard-negatives.json")}
        self.assertEqual(attacks, {
            "HN01_POST_CUTOFF_EVIDENCE",
            "HN02_PREDICTION_MUTATION_AFTER_SEAL",
            "HN03_RESOLUTION_DRIFT_AFTER_SEAL",
            "HN04_TOO_MANY_SECONDARY_PREDICTIONS",
            "HN05_ABLATION_OUTCOME_MISMATCH",
            "HN06_INDETERMINATE_AS_SUPPORT",
            "HN07_EARLY_T365_SETTLEMENT",
            "HN08_UNDECLARED_T730_EXTENSION",
            "HN09_REAL_CASE_ENROLLMENT_WITHOUT_GATE",
            "HN10_GLOBAL_ACCURACY_SCORE",
            "HN11_CAPITAL_AUTHORITY_LEAKAGE",
            "HN12_H5_COMPENSATION_VIOLATION"
        })
```

- [ ] **Step 2: Run fixture tests and verify RED**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CFixtureTests -v
```

Expected: FAIL because fixtures do not exist.

- [ ] **Step 3: Create synthetic Gold Case and sealed chain**

Use a fictional actor label such as `SYNTHETIC-ACTOR-ALPHA`; do not use a real person, company, ticker, fund, or manager.

The synthetic case should be in slot `ENT-FULL-01`, with clearly artificial evidence refs (`SYN-EV-001`, etc.) and fixed timestamps. Build the Evidence Seal and Preregistration Bundle with digests generated by the same canonical hashing algorithm used by the runtime.

Primary predictions must include all four IDs and all five model variants on the same frozen outcome definitions.

- [ ] **Step 4: Create synthetic T90/T180/T365 settlements**

Use a mixture of `YES`, `NO`, and causal `PARTIALLY_SUPPORTED`/`SUPPORTED` results. Include at least one `INDETERMINATE` binary event so the fixture proves it yields no Brier score.

- [ ] **Step 5: Create 12 named hard-negative attacks**

Each attack object must contain:

```text
attack_id
description
mutated_object
expected_error_substring
```

The test runner should feed each mutated object through the appropriate validator and assert the named failure rather than merely checking `is_valid: false` metadata.

- [ ] **Step 6: Run fixture tests and verify GREEN**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CFixtureTests -v
```

Expected: PASS.

- [ ] **Step 7: Commit Task 8**

```bash
git add docs/architecture/yf3n0/fixtures tests/test_yf3n0_c_prospective.py
git commit -m "YF3N0-C: add synthetic gold and hard-negative fixtures"
```

---

### Task 9: Add Fail-Closed Repository Validator, State Gate, Human Projection, and CI

**Files:**
- Create: `scripts/validate_yf3n0_c_prospective.py`
- Create: `docs/architecture/yf3n0/YF3N0-C-STATE.json`
- Create: `docs/architecture/yf3n0/YF3N0-C-HUMAN-REVIEW-CARD-v0.1.md`
- Create: `docs/human-projection/YF3N0-C-PROSPECTIVE-PREDICTION-PROTOCOL-v0.1.md`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_yf3n0_c_prospective.py`

**Interfaces:**
- `python scripts/validate_yf3n0_c_prospective.py` exits `0` only when contracts, protocol, slots, fixtures, seals, hard negatives, state boundaries, and non-authority checks all pass.

- [ ] **Step 1: Write failing validator/state tests**

```python
class YF3N0CStateTests(unittest.TestCase):
    def test_state_remains_candidate_only_after_implementation(self):
        state = load_json(ARCH / "YF3N0-C-STATE.json")
        self.assertEqual(state["status"], "IMPLEMENTED_CANDIDATE_AWAITING_HUMAN_REVIEW")
        self.assertFalse(state["real_case_enrollment_authorized"])
        self.assertFalse(state["prediction_clock_start_authorized"])
        self.assertFalse(state["canon_promotion_authorized"])

    def test_human_projection_preserves_prediction_vs_postdiction_boundary(self):
        text = (ROOT / "docs" / "human-projection" / "YF3N0-C-PROSPECTIVE-PREDICTION-PROTOCOL-v0.1.md").read_text(encoding="utf-8")
        self.assertIn("预测不是事后解释", text)
        self.assertIn("INDETERMINATE", text)
        self.assertIn("三非不是万能成功预测器", text)
```

- [ ] **Step 2: Run state tests and verify RED**

```bash
python -m unittest tests.test_yf3n0_c_prospective.YF3N0CStateTests -v
```

Expected: FAIL because state and human projection files do not exist.

- [ ] **Step 3: Create candidate-only state**

`YF3N0-C-STATE.json` must contain:

```json
{
  "program": "YF3N0-C",
  "status": "IMPLEMENTED_CANDIDATE_AWAITING_HUMAN_REVIEW",
  "parent_written_spec_accepted": true,
  "protocol_implemented": true,
  "real_case_enrollment_authorized": false,
  "prediction_clock_start_authorized": false,
  "canon_promotion_authorized": false,
  "merge_authorized": false
}
```

- [ ] **Step 4: Create Human Review Card**

The review card must explicitly ask the human reviewer to check:

```text
1. Does the implementation preserve YF3N0-B scope?
2. Are Prediction and Resolution atomically sealed?
3. Can any post-cutoff evidence enter preregistration?
4. Are Full/Ablations/Baseline directly comparable?
5. Can INDETERMINATE accidentally count as support?
6. Can a falsified primitive be compensated by the other two?
7. Does any output imply security/portfolio/psychometric authority?
8. Is real-case enrollment still blocked?
9. Is the Genesis cohort still only 12 empty structural slots?
10. Does Canon promotion remain a future Human Gate?
```

- [ ] **Step 5: Create concise human projection**

Document the protocol as:

```text
过去：历史回放告诉我们“它能解释什么”
现在：前瞻预注册要求它“在不知道答案时先下注自己的解释”

Evidence Seal → Atomic Prediction+Resolution Seal → Future → Blind Resolution → Settlement → Ablation → Qualification
```

Use the exact public Three-Non terms, but clearly state that machine validation uses `PIP/EAA/NLP` and that no real-case experiment starts with this implementation.

- [ ] **Step 6: Implement `validate_yf3n0_c_prospective.py` in ME1 fail-closed style**

The validator must:

```text
check all seven JSON Schemas
validate protocol identity and zero authority
validate exact 12 cohort slots and zero real enrollment
validate synthetic Case/Seal/Preregistration/Settlement/Qualification fixtures
verify every stored SHA-256 digest
run all 12 hard-negative attacks and require the expected failure substring
assert state is candidate-only
scan YF3N0-C schemas/protocol/state/human projection for forbidden authority fields/phrases
print one compact success line and exit 0
print validation_error and exit 1 on any exception
```

Use the same `require(condition, message)` fail-closed pattern as `scripts/validate_me1_state_object_model.py`.

- [ ] **Step 7: Add validator to repository-gates CI**

In `.github/workflows/ci.yml`, add immediately after the ME1/YIM0 methodology validators and before unittest discovery:

```yaml
      - run: python scripts/validate_yf3n0_c_prospective.py
```

Do not remove or reorder existing gates except for placing this one in the contract-validation sequence.

- [ ] **Step 8: Run focused validator and all tests**

```bash
python scripts/validate_yf3n0_c_prospective.py
python -m unittest tests.test_yf3n0_c_prospective -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected:

```text
YF3N0-C ... prospective_protocol=valid real_case_enrollment_authorized=false canon_promotion_authorized=false
```

and all unit tests PASS.

- [ ] **Step 9: Run existing critical non-regression validators**

```bash
python scripts/validate_me1_state_object_model.py
python scripts/validate_yim0_methodology_projection.py
python scripts/check_governance.py
python scripts/leak_guard.py
```

Expected: all exit `0`.

- [ ] **Step 10: Commit Task 9**

```bash
git add scripts/validate_yf3n0_c_prospective.py docs/architecture/yf3n0/YF3N0-C-STATE.json docs/architecture/yf3n0/YF3N0-C-HUMAN-REVIEW-CARD-v0.1.md docs/human-projection/YF3N0-C-PROSPECTIVE-PREDICTION-PROTOCOL-v0.1.md .github/workflows/ci.yml tests/test_yf3n0_c_prospective.py
git commit -m "YF3N0-C: close prospective protocol candidate gates"
```

---

### Task 10: Final Candidate Settlement and Human Gate Preparation

**Files:**
- Modify only if validation finds a concrete defect in Task 1–9 artifacts.
- Do not create a merge receipt, real-case registry, clock-start receipt, or Canon acceptance artifact.

**Interfaces:**
- Produces: a verified candidate HEAD ready for Human Review, not a merged or operational protocol.

- [ ] **Step 1: Run the complete repository gate commands locally**

```bash
python scripts/validate_repository.py
python scripts/validate_me0_multi_engine_ontology.py
python scripts/validate_me1_state_object_model.py
python scripts/validate_yim0_methodology_projection.py
python scripts/validate_yf3n0_c_prospective.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/leak_guard.py
python scripts/check_governance.py
```

Expected: every command exits `0`.

- [ ] **Step 2: Verify implementation scope with repository search**

Run:

```bash
git grep -n "real_case_enrollment_authorized" -- packages docs scripts tests
git grep -n "canon_promotion_authorized" -- packages docs scripts tests
git grep -n -E "buy|sell|target price|portfolio weight|trade execution|manager approval" -- docs/architecture/yf3n0 packages/contracts/schemas/yf3n0 scripts/yf3n0_prospective.py scripts/validate_yf3n0_c_prospective.py
```

Expected:

- all operational authority flags remain `false`;
- any prohibited financial phrases appear only in explicit non-authority/forbidden-language tests or documentation, never as granted capabilities.

- [ ] **Step 3: Verify no real-case actor leaked into fixtures**

```bash
git grep -n -E "Amazon|NVIDIA|Tesla|Theranos|Webvan|Quibi|Aramco|BTC|NVDA|TSLA" -- docs/architecture/yf3n0/fixtures || true
```

Expected: no matches.

- [ ] **Step 4: Inspect git diff and commit history**

```bash
git status --short
git log --oneline --decorate -10
git diff yf3n0-b-scope-causal-ontology-freeze...HEAD --stat
git diff --check
```

Expected:

- clean worktree;
- no whitespace errors;
- only YF3N0-C implementation-plan-authorized paths plus the single CI line changed;
- no mutation to SOUL/ME0/ME1 accepted artifacts.

- [ ] **Step 5: Record implementation candidate state in PR #60 conversation**

Post a top-level PR comment containing exactly the machine-verifiable facts available at that time:

```text
YF3N0-C implementation candidate completed.

State: IMPLEMENTED_CANDIDATE_AWAITING_HUMAN_REVIEW
Real-case enrollment: NOT AUTHORIZED
Prediction clock start: NOT AUTHORIZED
Canon promotion: NOT AUTHORIZED
Merge: NOT AUTHORIZED

Verification:
- validate_yf3n0_c_prospective.py: PASS
- YF3N0-C unittest: PASS
- repository unittest discovery: PASS
- ME1/YIM0 non-regression: PASS
- governance/leak guard: PASS

Required next gate: Human Review of YF3N0-C candidate.
```

Do not post acceptance or merge tokens on behalf of the human.

---

## Implementation Completion Criteria

The plan is complete only when all of the following are true:

1. Seven YF3N0-C JSON Schemas validate under Draft 2020-12.
2. Protocol registry freezes exactly H1–H5, P1–P4, five model variants, required horizons, settlement vocabularies, and zero authority.
3. Genesis cohort contains exactly 12 empty slots; no real actor is enrolled.
4. Evidence payloads are canonically SHA-256 sealed.
5. PredictionContract and ResolutionContract are atomically preregistered against the same Evidence Seal and timestamp.
6. Any mutation after seal is detected by digest/invariant validation.
7. Four Primary Predictions and at most two Secondary Predictions are enforced.
8. Full/Ablation/Baseline forecasts use identical outcome and resolution definitions.
9. Blind resolution packets contain no probabilities/model hints.
10. `INDETERMINATE` never earns support or Brier score.
11. T90/T180/T365 timing is enforced; undeclared T730 is rejected.
12. H5 no-compensation logic prevents a falsified primitive from producing `FULL_FORCE_CANDIDATE`.
13. Evidence Matrix preserves model/domain/horizon detail and emits no global Three-Non accuracy score.
14. All six Canon Promotion Gates can return PASS/FAIL/INDETERMINATE and all four final qualification outcomes are reachable in tests.
15. Twelve named hard-negative protocol attacks fail closed for the expected reason.
16. Human Projection clearly distinguishes prospective prediction from postdiction and retains `Three-Non != Universal Success Theory`.
17. Candidate state keeps real enrollment, clock start, merge, and Canon promotion unauthorized.
18. Existing ME1/YIM0/governance/leak validators remain green.
19. PR #60 is ready for Human Review but remains unmerged and non-operational.

## Self-Review Notes

Plan coverage was checked against the accepted Written Spec with the following conclusions:

- **Scope coverage:** all six prospective objects, Triple Seal, H1–H5, 12-case structural cohort, Full/3 Ablations/Baseline, blind resolution, T90/T180/T365 plus predeclared T730, four-state settlement, six promotion gates, and four final outcomes have explicit implementation tasks.
- **Outcome-leakage control:** the plan uses `Nonlinear Leverage Potential`/mechanism claims rather than realized-return inputs and explicitly forbids post-cutoff evidence from preregistration.
- **Atomicity ambiguity:** resolved by implementing one `PreregistrationBundle` whose PredictionContract and ResolutionContract share `sealed_at`, Evidence Seal digest, and bundle digest.
- **Quantification boundary:** Brier scoring is limited to binary resolvable events; causal mechanism claims keep qualitative settlement states.
- **Real-world scope:** no real cases, external data hydration, scheduler, or settlement clock is authorized in this plan; v0.1 is a machine-contract candidate only.
- **Authority boundary:** all operational, psychometric, capital, and Canon authorities remain false and are tested.
- **Placeholder scan:** the plan contains no `TBD`, `TODO`, “implement later”, unspecified validation step, or undefined neighboring interface.
- **Type/name consistency:** function names used by later tasks are defined in earlier tasks; object and enum names match the Written Spec terminology.

