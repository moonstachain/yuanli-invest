# YMQ-OS0-G0｜Macro Quant Constitution × Object Model × Physical Plane Freeze — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Date:** 2026-09-13  
**Repository:** `moonstachain/yuanli-invest`  
**Current design branch:** `ymq-os0-g0-ymq3-r0-written-spec`  
**Design authority:** `docs/superpowers/specs/2026-09-13-ymq-os0-g0-macro-quant-constitution-design.md`  
**Execution mode:** TDD + fail-closed + exact-head GitHub Actions + separate Human acceptance/merge gates

## Goal

Compile the accepted `YMQ-OS0-G0` design into machine-checkable law for the macro-quant research subsystem: four physical planes, nine canonical research objects, strict Point-in-Time time semantics, five stable `MQE1–MQE5` engine roles, provider-neutral compute boundaries, and explicit separation from Capital/Execution authority.

The implementation must extend the existing YMQ4 Evidence/PIT/Runtime lineage rather than fork it. Existing YMQ4 IDs and settlements remain historically intact, especially `YMQ4-B3 = REALITY PASS / SCIENTIFIC NO-GO / DRAFT / OPEN / NOT MERGED`.

## Architecture

The implementation creates a thin constitutional layer over existing YIOS0 and YMQ4 infrastructure:

`GitHub Law/Control → Evidence/PIT Truth → Provider-neutral Compute → Research Settlement → LearningDelta`

It does **not** create a new Investment OS, a trading engine, a portfolio allocator, a live macro predictor, or an execution path.

The machine contract and schemas live in GitHub. Existing `evidence.source_snapshots`, `pit.observations`, and `runtime.reality_gate_runs` remain the inherited physical truth foundation. New database structures add only the missing derived research objects. Hugging Face Jobs/container runners are replaceable compute providers and receive no authority.

## Tech Stack

- Python `3.12`
- JSON Schema Draft `2020-12`
- `jsonschema==4.25.1`
- `numpy==2.3.2` where deterministic numeric helpers are needed
- Python stdlib `unittest`, `hashlib`, `json`, `datetime`, `pathlib`
- PostgreSQL / Supabase migrations with RLS
- GitHub Actions existing `repository-gates` (`contracts`, `governance`)
- Existing YMQ4 Supabase Evidence/PIT/Runtime lineage

## Global Constraints

- `Reality > Belief`.
- Every intelligence claim has a preregistered defeat condition.
- `ClaimAuthority <= EvidenceAuthority`.
- `ResearchPass != CapitalPass`.
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`.
- `UNKNOWN = DENY`.
- `Receipt = Ledger; Status = Projection`.
- Past evidence/settlement is immutable; LearningDelta is forward-only.
- Existing `YMQ4` program IDs are never renumbered into `MQE` IDs.
- `MQE1–MQE5` are stable capability-family roles, not claims that production engines already exist.
- No portfolio sizing, position sizing, VeighNa, broker credential, broker connection, paper order, live order, or real capital movement.
- No HF Dataset/Model/Space write is assumed from the current chat OAuth; any writable HF identity requires a separate Reality Proof.
- No implementation task may rewrite accepted YIOS0/YMQ4/YEX0/YVN1 semantics.

---

## Task 1｜TDD RED: freeze the machine contract before implementation

**Files:**
- Create: `tests/test_ymq_os0_g0.py`

**Interfaces:**
- Imports future module: `scripts.validate_ymq_os0_g0`.
- Reads future config: `config/ymq_os0/ymq_os0_architecture.v0.1.json`.
- Reads existing YIOS0/YMQ4 authority evidence from repository-local files only.

- [ ] **Step 1: Write failing contract tests first.** Minimum assertions:
  - `program_id == YMQ-OS0-G0`;
  - parent system is `YIOS0` and scope is L2–L8 research-side only;
  - physical planes are exactly `LAW_CONTROL`, `EVIDENCE_RUNTIME_TRUTH`, `EXPERIMENT_COMPUTE`, `EXPERIENCE_PROJECTION`;
  - canonical object types are exactly the nine accepted objects;
  - engine roles are exactly `MQE1` through `MQE5` with accepted names;
  - replay rule is `known_as_of <= T0`;
  - `UNKNOWN = DENY`;
  - `PHYSICAL_PASS` and `SCIENTIFIC_NO_GO` are allowed to coexist;
  - existing YMQ4 IDs are preserved rather than remapped;
  - repository-local evidence still states B3 scientific NO-GO / no Canon authority;
  - no Capital/Execution/broker/live authority appears in the new config.

A representative test shape:

```python
from pathlib import Path
import json
import unittest

from scripts import validate_ymq_os0_g0 as ymq

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/ymq_os0/ymq_os0_architecture.v0.1.json"

class YMQOS0ContractTests(unittest.TestCase):
    def test_exact_engine_roles(self):
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(
            [e["id"] for e in cfg["engines"]],
            ["MQE1", "MQE2", "MQE3", "MQE4", "MQE5"],
        )

    def test_no_execution_authority(self):
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertFalse(cfg["authority"]["capital_authorized"])
        self.assertFalse(cfg["authority"]["execution_authorized"])
        self.assertFalse(cfg["authority"]["broker_authorized"])
```

- [ ] **Step 2: Run the targeted test before creating implementation artifacts.**

```bash
python -m unittest tests.test_ymq_os0_g0 -v
```

Expected RED: import/module/config failure because the implementation does not exist yet.

- [ ] **Step 3: Commit the RED test alone.** Record the exact RED head and CI run later in the qualification receipt.

---

## Task 2｜Materialize the YMQ-OS0 machine architecture contract

**Files:**
- Create: `config/ymq_os0/ymq_os0_architecture.v0.1.json`
- Create: `config/ymq_os0/ymq_os0_current.json`
- Create: `docs/architecture/ymq_os0/YMQ-OS0-G0-CANDIDATE-v0.1.md`

**Interfaces:**
- Consumes the accepted Written Spec only.
- `ymq_os0_current.json` is a stable discovery pointer; it cannot self-authorize.

- [ ] **Step 1: Encode identity and inherited authority.** Required top-level blocks:
  `identity`, `parent_authority`, `laws`, `research_loop`, `planes`, `objects`, `pit_time_semantics`, `engines`, `capability_run_contract`, `settlement_semantics`, `provider_policy`, `ymq4_lineage`, `authority`, `non_authorizations`, `versioning`.

- [ ] **Step 2: Freeze exact plane ownership.** Encode GitHub as Law/Control authority; Supabase/Postgres + object storage/NAS as Evidence/Runtime Truth; HF Jobs/container as replaceable compute; Web/HF Space/ChatGPT/Notion as projection only.

- [ ] **Step 3: Freeze YMQ4 lineage without aliasing it to MQE4 Canon.** Machine contract must state that DP1-A/DP1-B/B2 are inherited physical evidence and B3 remains scientific NO-GO / non-Canon unless separately admitted.

- [ ] **Step 4: Make the current pointer lifecycle-neutral.** It resolves paths/version only; current authority requires protected-main presence + a valid Human Acceptance Receipt + post-merge readback, following YIOS0 precedent.

- [ ] **Step 5: Run targeted tests.** They should still fail on missing schemas/validator details, but architecture identity tests should turn GREEN.

---

## Task 3｜TDD the nine canonical research-object schemas

**Files:**
- Create: `packages/contracts/schemas/vnext/ymq-source-snapshot.schema.json`
- Create: `packages/contracts/schemas/vnext/ymq-observation-pit.schema.json`
- Create: `packages/contracts/schemas/vnext/ymq-feature-pit.schema.json`
- Create: `packages/contracts/schemas/vnext/ymq-state-pit.schema.json`
- Create: `packages/contracts/schemas/vnext/ymq-transmission-edge-pit.schema.json`
- Create: `packages/contracts/schemas/vnext/ymq-research-claim.schema.json`
- Create: `packages/contracts/schemas/vnext/ymq-capability-run.schema.json`
- Create: `packages/contracts/schemas/vnext/ymq-research-settlement.schema.json`
- Create: `packages/contracts/schemas/vnext/ymq-learning-delta.schema.json`
- Create: `tests/test_ymq_os0_schemas.py`

**Interfaces:**
- Schemas are candidate semantic contracts in the existing `vnext` contract layer.
- They do not supersede generic `canonical-observation`, `evidence-claim`, `capability-invocation/result`, or `capability-revision`; the YMQ schemas specialize the accepted macro-quant semantics and cross-object invariants.

- [ ] **Step 1: Write schema-shape tests first.** Use `Draft202012Validator.check_schema` and positive/negative fixtures built inside the test.

- [ ] **Step 2: Enforce object invariants in schema where expressible.** Examples:
  - `SourceSnapshot.content_sha256` is 64 lowercase hex;
  - `ObservationPIT.known_as_of`, release/vintage/observation clocks are explicit;
  - `FeaturePIT` requires input observation refs + transform SHA;
  - `StatePIT` requires uncertainty + `unknown_fields`;
  - `TransmissionEdgePIT` requires `as_of` and stability window;
  - `ResearchClaim` requires at least one falsifier/revision rule;
  - `CapabilityRun` requires exact git SHA, capability version, parameter contract, runner identity and artifact hashes;
  - `ResearchSettlement` requires separate physical/scientific/authority statuses;
  - `LearningDelta` requires Human review for any law/capability change and explicitly forbids past rewrite.

- [ ] **Step 3: Keep authority fields fail-closed.** No object schema contains portfolio-weight, order-submission, broker or live-execution authority.

- [ ] **Step 4: Run:**

```bash
python -m unittest tests.test_ymq_os0_schemas -v
```

Expected GREEN only when all nine schemas validate and negative fixtures are rejected.

- [ ] **Step 5: Commit schemas + schema tests together.**

---

## Task 4｜Implement and test the reusable PIT law

**Files:**
- Create: `scripts/ymq_os0_pit.py`
- Create: `tests/test_ymq_os0_pit.py`

**Interfaces:**

```python
parse_utc(value: str) -> datetime
is_known_at(known_as_of: str, t0: str) -> bool
assert_pit_eligible(rows: list[dict], t0: str, field: str = "known_as_of") -> None
canonical_json_hash(payload: object) -> str
```

- [ ] **Step 1: Write failing tests.** Cover equality-at-T0 allowed, one-microsecond future denied, missing/UNKNOWN availability denied, naive timestamps rejected, deterministic canonical JSON hash, and reordered dictionary keys producing the same hash.

Example:

```python
def test_future_knowledge_fails_closed(self):
    rows = [{"known_as_of": "2020-03-12T00:00:00Z"}]
    with self.assertRaises(ValueError):
        pit.assert_pit_eligible(rows, "2020-03-11T23:59:59Z")
```

- [ ] **Step 2: Implement minimal helpers using stdlib only.** Never infer an unavailable date from observation date.

- [ ] **Step 3: Run:**

```bash
python -m unittest tests.test_ymq_os0_pit -v
```

- [ ] **Step 4: Run the combined G0 unit subset:**

```bash
python -m unittest tests.test_ymq_os0_g0 tests.test_ymq_os0_schemas tests.test_ymq_os0_pit -v
```

---

## Task 5｜Extend the existing Supabase Evidence/PIT lineage without duplication

**Files:**
- Create: `supabase/migrations/20260913090000_ymq_os0_g0_object_model.sql`
- Create: `tests/test_ymq_os0_g0_sql_contract.py`

**Interfaces:**
- Reuse, do not recreate: `evidence.sources`, `evidence.source_snapshots`, `pit.observations`, `runtime.reality_gate_runs`.
- Add the missing derived/runtime object projections only.

**Target tables:**
- `pit.features`
- `runtime.research_states`
- `runtime.transmission_edges`
- `runtime.research_claims`
- `runtime.capability_runs`
- `runtime.research_settlements`
- `runtime.learning_deltas`

- [ ] **Step 1: Write SQL contract tests first.** Tests inspect migration text and require reuse of the existing tables rather than duplicate `source_snapshots`/`observations` definitions.

- [ ] **Step 2: Encode provenance/reference fields.** Every derived table needs explicit `as_of/known_as_of` semantics or a reference to the PIT objects from which those semantics are inherited.

- [ ] **Step 3: Encode three-axis settlement.** `runtime.research_settlements` must persist physical, scientific, and authority states independently, plus baseline/hard-negative/ablation payloads and known limitations.

- [ ] **Step 4: Enable RLS on every new table and create no `anon`/`authenticated` write policy.** Database mutation remains service-role/controlled-runtime only.

- [ ] **Step 5: Do not apply the migration to production as part of this file-writing task.** Physical application/readback is a separately authorized runtime action during execution; a generated migration in Git is not evidence that the database changed.

- [ ] **Step 6: Run:**

```bash
python -m unittest tests.test_ymq_os0_g0_sql_contract -v
```

---

## Task 6｜Build the fail-closed YMQ-OS0 validator and Human Review artifacts

**Files:**
- Create: `scripts/validate_ymq_os0_g0.py`
- Create: `docs/architecture/ymq_os0/YMQ-OS0-G0-HUMAN-REVIEW-CARD-v0.1.md`
- Extend: `tests/test_ymq_os0_g0.py`

**Interfaces:**
- Repository-local validation only; no live GitHub/HF/Supabase calls in protected CI.

Validator must enforce:

- [ ] exact four-plane contract;
- [ ] exact nine-object contract;
- [ ] exact `MQE1–MQE5` roles;
- [ ] replay law and UNKNOWN-deny semantics;
- [ ] YMQ4 historical IDs preserved;
- [ ] B3 scientific NO-GO remains visible from repository/local status evidence;
- [ ] no schema/config contains portfolio sizing, order submission, broker, live execution, or real-capital authority;
- [ ] HF is provider/non-authority, not truth/canon;
- [ ] settlement has physical/scientific/authority separation;
- [ ] LearningDelta cannot rewrite past evidence/settlement;
- [ ] `ymq_os0_current.json` cannot self-authorize;
- [ ] all required files exist and parse.

Expected terminal output only after all checks:

```text
YMQ-OS0-G0 validator: PASS
```

- [ ] **Run validator directly:**

```bash
python scripts/validate_ymq_os0_g0.py
```

- [ ] **Run all G0 tests:**

```bash
python -m unittest tests.test_ymq_os0_g0 tests.test_ymq_os0_schemas tests.test_ymq_os0_pit tests.test_ymq_os0_g0_sql_contract -v
```

---

## Task 7｜Wire G0 into protected repository-gates and prove TDD GREEN

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Preserve the job identities `contracts` and `governance`.
- Add G0 validation before repository-wide unittest discovery.

- [ ] **Step 1: Add:**

```yaml
- run: python scripts/validate_ymq_os0_g0.py
```

under the existing `contracts` job, after upstream constitutional validators and before full unittest discovery.

- [ ] **Step 2: Push the implementation candidate and wait for exact-head PR Actions.**

Required GREEN evidence:
- `python scripts/validate_ymq_os0_g0.py` PASS;
- targeted G0 tests PASS;
- full unittest discovery PASS;
- `contracts` job success;
- `governance` job success.

- [ ] **Step 3: Audit PR diff for scope leakage.** Search for:
  - broker endpoint/credentials;
  - VeighNa imports/invocation;
  - portfolio/position sizing;
  - paper/live order code;
  - HF token literals;
  - service-role/API key literals;
  - silent edits to accepted YMQ4/YIOS0 receipts.

Any finding is a fail-closed condition.

---

## Task 8｜Optional-but-required-for-physical-plane qualification: apply migration and read back Reality

This task is performed only when an authorized Supabase credential is available. Git commit alone is **not** physical proof.

**Files/outputs:**
- Apply: `supabase/migrations/20260913090000_ymq_os0_g0_object_model.sql`
- Create after successful readback: `docs/architecture/ymq_os0/YMQ-OS0-G0-RUNTIME-REALITY-RECEIPT-v0.1.md`

- [ ] **Step 1:** Apply the candidate migration through the already authorized Supabase control path; do not print secrets.
- [ ] **Step 2:** Independently read back table existence, RLS enabled state, zero public write policies, and coexistence with existing YMQ4 evidence/PIT tables.
- [ ] **Step 3:** Prove no existing DP1-A/DP1-B/B2 rows or schemas were destroyed or reinterpreted.
- [ ] **Step 4:** Record physical result as either `RUNTIME_SCHEMA_REALITY_PASS` or fail closed with the exact discrepancy.

This physical-plane proof is not required merely to machine-qualify Git contracts, but is required before claiming the new runtime object model actually exists outside GitHub.

---

## Task 9｜Create exact-head Machine Qualification Receipt and stop at Human Gate

**Files:**
- Create: `docs/architecture/ymq_os0/YMQ-OS0-G0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md`
- Update PR body only.

**Interfaces:**
- Receipt binds exact candidate SHA, TDD RED evidence, exact-head GREEN run, `contracts`/`governance`, validator, scope audit, and any optional Supabase runtime readback.

- [ ] **Step 1:** Re-read protected `main` and PR #72 at qualification time. Preserve B3 as scientific NO-GO / not merged unless external Reality has separately changed.
- [ ] **Step 2:** Record exact SHA and workflow run IDs; never copy stale design-time values.
- [ ] **Step 3:** Set candidate state:

```text
YMQ_OS0_G0_MACHINE_QUALIFIED / AWAITING_HUMAN_REVIEW
```

only if all repository gates are freshly GREEN.

- [ ] **Step 4:** Keep PR Draft/Open/Not Merged. Machine qualification creates no merge authority and no R0 physical-run authority.

Required next Human decision after a qualified candidate:

`ACCEPT_YMQ_OS0_G0_MACHINE_QUALIFICATION`

A later merge must remain separately gated by:

`AUTHORIZE_YMQ_OS0_G0_MERGE`

Do not create either Human acceptance receipt or merge action until the corresponding explicit token is received.

---

## Implementation sequence / dependency law

Execute Tasks `1 → 9` in order. `YMQ3-R0` may prepare its preregistration in parallel only if it references the accepted G0 design; it must not start a physical scientific run against unfrozen/moving object or PIT contracts.

The clean dependency is:

`YMQ-OS0-G0 machine contract → Human acceptance → merge/readback → YMQ3-R0 physical Reality Audit`.

## Completion evidence

Do not claim G0 complete merely because files exist. Completion requires fresh evidence appropriate to the claimed layer:

- **Git implementation complete:** exact-head validator/tests + `contracts/governance` GREEN.
- **Runtime schema physically present:** independent Supabase readback.
- **Canon authority:** Human acceptance + separately authorized merge + protected-main readback.

Nothing in this plan authorizes Capital or Execution.