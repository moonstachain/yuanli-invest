# YMQ-OS0-G0｜Macro Quant Constitution × Object Model × Physical Plane Freeze — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Date:** 2026-09-13  
**Repository:** `moonstachain/yuanli-invest`  
**Current design branch:** `ymq-os0-g0-ymq3-r0-written-spec`  
**Design authority:** `docs/superpowers/specs/2026-09-13-ymq-os0-g0-macro-quant-constitution-design.md`  
**Execution mode:** TDD + fail-closed + exact-head GitHub Actions + separate Human acceptance/merge gates

## Goal

Compile the accepted `YMQ-OS0-G0` design into a narrow, machine-checkable constitutional layer for the macro-quant research subsystem: four physical planes, nine canonical research objects, strict Point-in-Time semantics, five stable `MQE1–MQE5` engine roles, provider-neutral compute boundaries, and explicit separation from Capital/Execution authority.

This battle is deliberately **law-only**. It does not apply a Supabase migration, create an HF Dataset/Model/Space, run YMQ3-R0, build Market Clock, or mutate external runtime state. Those are later battles. Existing YMQ4 Evidence/PIT/Runtime work is referenced as inherited Reality evidence, not rewritten.

## Architecture

G0 compiles the following accepted research loop into GitHub contracts:

`External Reality → Evidence Snapshot → PIT Observation → PIT Feature → PIT State → Transmission → Capability Run → Research Settlement → LearningDelta`

The implementation creates:

- one machine contract;
- nine JSON Schemas;
- three human-readable architecture freezes plus one Human Review Card;
- one fail-closed validator;
- one focused TDD test module;
- one protected-CI hook;
- one Machine Qualification Receipt after fresh exact-head GREEN.

No external data-plane mutation is required to machine-qualify G0.

## Tech Stack

- Python `3.12`
- JSON Schema Draft `2020-12`
- `jsonschema==4.25.1`
- Python stdlib `unittest`, `json`, `datetime`, `hashlib`, `pathlib`
- GitHub Actions existing `repository-gates` jobs: `contracts`, `governance`
- Repository-local readback of existing YIOS0/YMQ4 authority evidence

## Global Constraints

- `Reality > Belief`.
- Every intelligence claim carries a defeat condition.
- `ClaimAuthority <= EvidenceAuthority`.
- `ResearchPass != CapitalPass`.
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`.
- `UNKNOWN = DENY`.
- `Receipt = Ledger; Status = Projection`.
- Past evidence/settlement is immutable; LearningDelta is forward-only.
- Existing `YMQ4` program IDs are never renumbered into `MQE` IDs.
- `MQE1–MQE5` are capability-family roles, not claims that production runtimes already exist.
- HF/Supabase/Notion/ChatGPT are providers/surfaces, not Canon merely by identity.
- No portfolio sizing, position sizing, VeighNa, broker credential/connection, paper/live order, or real capital movement.
- No Supabase/HF runtime mutation in G0.
- No accepted YIOS0/YMQ4/YEX0/YVN1 receipt is rewritten by this battle.

---

## Task 1｜TDD RED: write the constitutional failure contract first

**Files:**
- Create: `tests/test_ymq_os0_g0.py`

**Interfaces:**
- Imports future module: `scripts.validate_ymq_os0_g0`.
- Reads future machine contract: `config/ymq_os0/ymq_os0_contract.v0.1.json`.
- Reads future schemas: `packages/contracts/schemas/ymq/*.schema.json`.
- Reads repository-local YIOS0/YMQ4 facts only; no network calls.

- [ ] **Step 1: Write failing tests before implementation artifacts exist.** Minimum assertions:
  - `program_id == "YMQ-OS0-G0"`;
  - parent authority is YIOS0 research side L2–L8;
  - physical planes are exactly `LAW_CONTROL`, `EVIDENCE_RUNTIME_TRUTH`, `EXPERIMENT_COMPUTE`, `EXPERIENCE_PROJECTION`;
  - exactly nine canonical object types exist;
  - engine roles are exactly `MQE1..MQE5` with accepted names;
  - replay eligibility is `known_as_of <= T0`;
  - `UNKNOWN = DENY`;
  - `PHYSICAL_PASS` may coexist with `SCIENTIFIC_NO_GO`;
  - `ResearchPass == CapitalPass` semantics are rejected;
  - existing YMQ4 IDs are preserved;
  - B3 scientific NO-GO / non-Canon state remains visible;
  - no Capital/Execution/broker/live authority is introduced.

Representative beginning:

```python
from pathlib import Path
import json
import unittest

from scripts import validate_ymq_os0_g0 as ymq

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/ymq_os0/ymq_os0_contract.v0.1.json"
SCHEMAS = ROOT / "packages/contracts/schemas/ymq"

class YMQOS0G0Tests(unittest.TestCase):
    def test_engine_roles_are_exact(self):
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(
            [row["id"] for row in cfg["engines"]],
            ["MQE1", "MQE2", "MQE3", "MQE4", "MQE5"],
        )
```

- [ ] **Step 2: Run targeted test immediately.**

```bash
python -m unittest tests.test_ymq_os0_g0 -v
```

Expected RED: `ModuleNotFoundError` / missing contract artifacts.

- [ ] **Step 3: Commit RED test alone.** Preserve exact RED head and later Actions run as qualification evidence.

---

## Task 2｜Materialize the single machine contract

**Files:**
- Create: `config/ymq_os0/ymq_os0_contract.v0.1.json`

**Interfaces:**
- This is the machine-readable composition contract for G0.
- It does not self-authorize Canon, runtime, Capital, or Execution.

- [ ] **Step 1: Encode identity and parent authority.** Required blocks:
  - `identity`
  - `parent_authority`
  - `laws`
  - `research_loop`
  - `physical_planes`
  - `canonical_objects`
  - `pit_time_semantics`
  - `engines`
  - `capability_execution_contract`
  - `settlement_semantics`
  - `provider_policy`
  - `ymq4_lineage`
  - `authority`
  - `non_authorizations`
  - `versioning`

- [ ] **Step 2: Freeze the exact engine map:**

```json
[
  {"id":"MQE1","name":"Macro Reality Engine"},
  {"id":"MQE2","name":"Industrial Reality Engine"},
  {"id":"MQE3","name":"Narrative × Herding Engine"},
  {"id":"MQE4","name":"Dynamic Transmission Engine"},
  {"id":"MQE5","name":"Price × Payoff Engine"}
]
```

- [ ] **Step 3: Freeze provider/authority separation.** GitHub = Law/Control; Evidence/Runtime Truth = Postgres/Supabase + Object Storage/NAS role; HF Jobs/container = replaceable Experiment Compute; Web/HF Space/ChatGPT/Notion = Experience/Projection only.

- [ ] **Step 4: Freeze YMQ4 lineage without aliasing.** Record DP1-A/DP1-B/B2 as inherited physical evidence and B3 as scientific NO-GO / non-Canon according to repository-local evidence. Explicitly state `YMQ4 != MQE4_CANON`.

- [ ] **Step 5: Freeze non-authorizations as machine booleans/arrays, not prose only.** Capital, sizing, broker, execution, HF write, external runtime mutation all remain false/not-authorized.

- [ ] **Step 6: Re-run targeted tests.** Contract identity tests should turn GREEN while schema-dependent tests remain RED.

---

## Task 3｜TDD the nine canonical object schemas in the accepted namespace

**Files:**
- Create: `packages/contracts/schemas/ymq/source_snapshot.schema.json`
- Create: `packages/contracts/schemas/ymq/observation_pit.schema.json`
- Create: `packages/contracts/schemas/ymq/feature_pit.schema.json`
- Create: `packages/contracts/schemas/ymq/state_pit.schema.json`
- Create: `packages/contracts/schemas/ymq/transmission_edge_pit.schema.json`
- Create: `packages/contracts/schemas/ymq/research_claim.schema.json`
- Create: `packages/contracts/schemas/ymq/capability_run.schema.json`
- Create: `packages/contracts/schemas/ymq/research_settlement.schema.json`
- Create: `packages/contracts/schemas/ymq/learning_delta.schema.json`
- Extend: `tests/test_ymq_os0_g0.py`

**Interfaces:**
- Schemas are YMQ-specific constitutional objects.
- They may reference existing generic vNext semantics conceptually, but G0 does not overwrite existing vNext files.

- [ ] **Step 1: Add schema-validation tests using `Draft202012Validator.check_schema`.** Require exactly nine files and unique `$id` values.

- [ ] **Step 2: Implement `SourceSnapshot`.** Require source authority tier/class, canonical locator, retrieved timestamp, 64-char SHA-256, storage locator, license class, runner Git SHA. Snapshot mutation is forbidden semantically; replacement creates a new identity/hash.

- [ ] **Step 3: Implement `ObservationPIT`.** Require observation/release/vintage/known-as-of clocks, value/unit, source snapshot ref, measurement regime and PIT status.

- [ ] **Step 4: Implement `FeaturePIT`.** Require feature-definition version, `as_of`, input observation refs, transform Git SHA, value, lookback and normalization rule.

- [ ] **Step 5: Implement `StatePIT` and `TransmissionEdgePIT`.** State requires uncertainty + explicit unknown fields; transmission requires as-of, method, effect/coefficient, uncertainty/evidence refs and stability window. No permanent-beta semantics.

- [ ] **Step 6: Implement `ResearchClaim`.** Require evidence refs, claim authority, falsifier and expiry/review rule. Validator will enforce `ClaimAuthority <= EvidenceAuthority` relationally.

- [ ] **Step 7: Implement `CapabilityRun`.** Require battle/capability/version, exact Git SHA, panel revisions, parameter contract, runner identity, start/end and artifact hashes.

- [ ] **Step 8: Implement `ResearchSettlement`.** Require independent `physical_status`, `scientific_status`, `authority_status`, plus baseline/hard-negative/ablation results, limitations and next authorized stage. No single global `PASS` field may substitute for these.

- [ ] **Step 9: Implement `LearningDelta`.** Require settlement ref, proposed forward change, affected capability/contract, evidence basis, Human-review requirement and state. Include an explicit `rewrite_past_authorized: false` / equivalent `const:false` field.

- [ ] **Step 10: Add positive and negative in-test fixtures.** Negative fixtures must include: future knowledge, claim authority > evidence authority, collapsed settlement state, LearningDelta past rewrite, execution-authority leakage.

- [ ] **Step 11: Run:**

```bash
python -m unittest tests.test_ymq_os0_g0 -v
```

---

## Task 4｜Write the exact human architecture artifacts from the accepted design

**Files:**
- Create: `docs/architecture/ymq_os0/YMQ-OS0-CONSTITUTION-v0.1.md`
- Create: `docs/architecture/ymq_os0/YMQ-OS0-OBJECT-MODEL-v0.1.md`
- Create: `docs/architecture/ymq_os0/YMQ-OS0-PHYSICAL-PLANE-FREEZE-v0.1.md`
- Create: `docs/architecture/ymq_os0/YMQ-OS0-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Human-readable projection of the accepted spec + implemented machine contract.
- Docs cannot grant more authority than config/schema.

- [ ] **Step 1: Constitution doc** freezes mission, inherited mother laws, research loop, namespace reconciliation and non-authorizations.

- [ ] **Step 2: Object Model doc** documents O1–O9 fields, relationships and invariants. Include an explicit lineage diagram:

```text
SourceSnapshot
  ↓
ObservationPIT
  ↓
FeaturePIT
  ↓
StatePIT ↔ TransmissionEdgePIT
  ↓
ResearchClaim
  ↓
CapabilityRun
  ↓
ResearchSettlement
  ↓
LearningDelta
```

- [ ] **Step 3: Physical Plane Freeze doc** states one primary authority role per plane, provider replaceability, and `Execution = outside YMQ-OS`.

- [ ] **Step 4: Human Review Card** enumerates exact G0 acceptance questions and explicitly states that G0 acceptance does not authorize Supabase migration, HF write, YMQ3 physical run, Capital, or Execution.

- [ ] **Step 5: Extend tests/validator expectations so human docs cannot drift from machine IDs/names.**

---

## Task 5｜Implement the fail-closed constitutional validator

**Files:**
- Create: `scripts/validate_ymq_os0_g0.py`
- Extend: `tests/test_ymq_os0_g0.py`

**Interfaces:**
- Repository-local only; no live GitHub/HF/Supabase/network calls in protected CI.

Required validator functions should remain small and independently testable, e.g.:

```python
load_json(path) -> dict
require(condition, message) -> None
validate_contract() -> None
validate_schemas() -> None
validate_pit_relations(bundle) -> None
validate_claim_authority(bundle) -> None
validate_settlement_separation(bundle) -> None
validate_learning_forward_only(bundle) -> None
validate_provider_authority() -> None
validate_ymq4_lineage() -> None
validate_non_authorizations() -> None
```

- [ ] **Step 1: Validate exact artifact set and JSON Schema syntax.**

- [ ] **Step 2: Validate PIT relational law with in-test fixture bundle.** For every Observation/Feature/State relationship, evidence `known_as_of` later than the consuming `as_of` must fail closed.

- [ ] **Step 3: Validate ClaimAuthority ceiling.** Define a frozen authority ordering in the contract and reject stronger claim authority than its weakest required evidence basis.

- [ ] **Step 4: Validate settlement separation.** Reject a settlement missing any of physical/scientific/authority axes or introducing one catch-all PASS as authority.

- [ ] **Step 5: Validate LearningDelta forward-only semantics.** Past evidence/settlement rewrite must be impossible in accepted fixtures.

- [ ] **Step 6: Validate provider non-authority.** Reject configs/docs that make HF/Supabase/Notion/ChatGPT authority merely by provider identity.

- [ ] **Step 7: Validate YMQ4 lineage.** Existing IDs must remain YMQ4; B3 NO-GO/non-Canon must not be upgraded or hidden.

- [ ] **Step 8: Validate no action-side leakage.** Fail if G0 config/schema grants portfolio weighting, sizing, order submission, broker or execution authority.

- [ ] **Step 9: Only after all checks print:**

```text
YMQ-OS0-G0 validator: PASS
```

- [ ] **Step 10: Run:**

```bash
python scripts/validate_ymq_os0_g0.py
python -m unittest tests.test_ymq_os0_g0 -v
```

---

## Task 6｜Wire G0 into protected repository-gates and reach exact-head GREEN

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Preserve existing protected job identities `contracts` and `governance`.
- G0 validator runs inside `contracts` before repository-wide unittest discovery.

- [ ] **Step 1: Add:**

```yaml
- run: python scripts/validate_ymq_os0_g0.py
```

in the existing `contracts` job after prerequisite constitutional validators and before full unittest discovery.

- [ ] **Step 2: Push candidate and wait for fresh PR Actions.** Required evidence:
  - G0 validator success;
  - `tests.test_ymq_os0_g0` success;
  - full unittest discovery success;
  - `contracts` success;
  - `governance` success.

- [ ] **Step 3: Perform a scope audit on the exact qualified head.** Reject if diff contains:
  - Supabase migration/application;
  - HF Dataset/Model/Space creation;
  - data ingestion/runtime write;
  - YMQ3 execution;
  - Market Clock implementation;
  - portfolio/position sizing;
  - VeighNa/broker/paper/live action;
  - secret/token literal;
  - edits that rewrite accepted YMQ4/YIOS0 receipts.

---

## Task 7｜Create the Machine Qualification Receipt and stop at Human Gate

**Files:**
- Create only after fresh exact-head GREEN: `docs/architecture/ymq_os0/YMQ-OS0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md`
- Update PR body only.

**Interfaces:**
- Receipt is evidence of repository-level machine qualification only.
- It does not imply Human Acceptance, merge, runtime deployment, R0 execution or Capital/Execution authority.

- [ ] **Step 1: Freshly read back the exact candidate head, PR status, protected `main`, and repository-local YMQ4 B3 state.** Do not copy stale design-time SHAs.

- [ ] **Step 2: Record TDD RED evidence:** exact RED head, failing test/CI cause.

- [ ] **Step 3: Record GREEN evidence:** exact qualified head, repository-gates run number/id, `contracts`, `governance`, validator and full tests.

- [ ] **Step 4: Record scope-qualified artifacts:** one contract, nine schemas, three architecture freezes, Human Review Card, validator, test, CI hook, plan.

- [ ] **Step 5: Freeze candidate state only if evidence supports it:**

```text
YMQ_OS0_G0_MACHINE_QUALIFIED / AWAITING_HUMAN_REVIEW
```

- [ ] **Step 6: Keep PR Draft/Open/Not Merged.** Required next Human token:

`ACCEPT_YMQ_OS0_G0_MACHINE_QUALIFICATION`

A later merge remains separately gated by:

`AUTHORIZE_YMQ_OS0_G0_MERGE`

Do not create an acceptance receipt or merge action without the explicit corresponding token.

---

## Dependency law for YMQ3-R0

`YMQ3-R0` may prepare code/preregistration against this accepted G0 design, but the canonical physical scientific run must bind to a stable accepted G0 object/time/plane contract. G0 does not itself authorize that physical run.

Clean sequence:

`G0 TDD → G0 machine qualification → Human acceptance → separately authorized merge/readback → R0 canonical physical Reality Audit`.

## Completion evidence

Do not collapse layers:

- **G0 files exist**: GitHub content readback only.
- **G0 machine-qualified**: fresh exact-head validator/tests + `contracts/governance` GREEN.
- **G0 Human-accepted**: explicit Human token/receipt.
- **G0 Canon on main**: separately authorized merge + protected-main readback.
- **External runtime changed**: not part of this G0 battle.

Nothing in this plan authorizes Capital or Execution.