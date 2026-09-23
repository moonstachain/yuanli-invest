# YMQ-OS0-G0｜Machine Qualification Receipt v0.1

**Stage:** `YMQ_OS0_G0_MACHINE_QUALIFIED`  
**Recorded at:** `2026-09-13`  
**Repository:** `moonstachain/yuanli-invest`  
**Candidate branch:** `ymq-os0-g0-ymq3-r0-implementation`  
**Candidate PR:** `#92`  
**Architecture version:** `0.1.0`  
**Authority:** `RESEARCH_CONSTITUTION_CANDIDATE_ONLY`

## 1｜Qualified implementation head

`f59d0555812a2a2419cf7764c35d7448851b0c0f`

This is the exact consolidated candidate head that passed a fresh pull-request-triggered `repository-gates` run after the G0 validator had been wired into the protected `contracts` job.

Protected `main` at qualification readback:

`8b30065d00f1c6aa321c9caf875b36b8a0b2d754`

PR #92 at qualification readback:

`DRAFT / OPEN / NOT MERGED`

## 2｜TDD evidence

### RED observed first

- RED head: `d501cb7f6a05c9d0a90ed830adf5eba62e1c170b`
- repository-gates run: `#760`
- run id: `34744803542`
- `governance`: success
- `contracts`: expected failure during full unittest discovery
- root cause: G0 tests existed before `scripts.validate_ymq_os0_g0` and the machine artifacts existed
- interpretation: the constitutional tests were physically RED before implementation

The RED test was merged into the isolated implementation branch before the implementation tasks.

### GREEN reached and then independently hardened

An initial full GREEN validator candidate was reached before review, but that result was not treated as final qualification. Independent review found two real issues:

1. provider replaceability was internally inconsistent for the Law plane;
2. PIT relational validation did not yet reject `release_time` / `vintage_time` later than `known_as_of`.

The implementation was hardened with additional temporal, lifecycle, provider-neutrality and authority-ceiling negative tests.

Review-hardened exact head:

`4c73d7576b648b4b6410e4ef3da481cb745ae097`

- repository-gates: `#771`
- run id: `34745359529`
- conclusion: `success`
- `contracts`: success
- `governance`: success
- full unittest discovery: success

### Protected CI integration qualification

The G0 validator was then inserted directly into the protected `contracts` job.

Task-6 exact head:

`bcfaa011ae46eb745988080305f27d129864aa93`

- repository-gates: `#772`
- run id: `34745425565`
- conclusion: `success`
- explicit `python scripts/validate_ymq_os0_g0.py`: success
- full unittest discovery: success
- `contracts`: success
- `governance`: success

After the internal Task-6 squash merge, the consolidated candidate head became `f59d0555812a2a2419cf7764c35d7448851b0c0f` and was freshly requalified on PR #92:

- repository-gates: `#773`
- run id: `34745523220`
- conclusion: `success`
- explicit G0 validator: success
- full unittest discovery: success
- `contracts`: success
- `governance`: success

The machine-qualification claim is bound to this latter consolidated candidate head/run, not to an earlier partial task head.

## 3｜Scope-qualified artifacts

The candidate contains exactly the G0 law/control implementation plus its accepted design/plan:

### Machine law

- `config/ymq_os0/ymq_os0_contract.v0.1.json`

### Nine canonical research-object schemas

- `packages/contracts/schemas/ymq/source_snapshot.schema.json`
- `packages/contracts/schemas/ymq/observation_pit.schema.json`
- `packages/contracts/schemas/ymq/feature_pit.schema.json`
- `packages/contracts/schemas/ymq/state_pit.schema.json`
- `packages/contracts/schemas/ymq/transmission_edge_pit.schema.json`
- `packages/contracts/schemas/ymq/research_claim.schema.json`
- `packages/contracts/schemas/ymq/capability_run.schema.json`
- `packages/contracts/schemas/ymq/research_settlement.schema.json`
- `packages/contracts/schemas/ymq/learning_delta.schema.json`

### Human architecture projections

- `YMQ-OS0-CONSTITUTION-v0.1.md`
- `YMQ-OS0-OBJECT-MODEL-v0.1.md`
- `YMQ-OS0-PHYSICAL-PLANE-FREEZE-v0.1.md`
- `YMQ-OS0-HUMAN-REVIEW-CARD-v0.1.md`

### Verification / CI

- `scripts/validate_ymq_os0_g0.py`
- `tests/test_ymq_os0_g0.py`
- `.github/workflows/ci.yml` G0 validator hook
- accepted Written Spec and implementation plan

## 4｜Scope audit

Fresh PR #92 changed-file readback contained only:

- accepted specs/plans;
- G0 config;
- G0 schemas;
- G0 Human architecture docs;
- G0 validator/tests;
- one `repository-gates` CI hook.

It contained **no**:

- Supabase migration/application;
- Evidence/Runtime database mutation;
- HF Dataset/Model/Space write;
- data-ingestion runtime;
- YMQ3 physical execution;
- Market Clock implementation;
- portfolio/position sizing;
- VeighNa or broker adapter;
- paper/live order path;
- secret/token literal;
- real-capital action.

## 5｜Constitutional verification

Machine qualification preserves:

- `Reality > Belief`;
- preregistered defeat conditions;
- `ClaimAuthority <= EvidenceAuthority`;
- `ResearchPass != CapitalPass`;
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`;
- `UNKNOWN = DENY`;
- `Receipt = Ledger; Status = Projection`;
- past Evidence/Settlement immutability;
- forward-only LearningDelta.

The validator additionally proves at repository level that:

- the four physical planes are exact and provider-neutral;
- all nine canonical object schemas parse and validate;
- `known_as_of <= T0` semantics fail closed on future knowledge;
- release/vintage cannot occur after the claimed `known_as_of`;
- ClaimAuthority cannot exceed EvidenceAuthority;
- one catch-all ResearchSettlement `PASS` is rejected;
- `PHYSICAL_PASS / SCIENTIFIC_NO_GO` remains valid;
- LearningDelta cannot rewrite past evidence or settlement;
- provider identity grants no Canon authority;
- action-side authority is absent from the YMQ schema pack.

## 6｜YMQ4 lineage preserved

Repository-local readback continues to preserve:

- YMQ4 historical IDs;
- `YMQ4 != MQE4 Canon`;
- YMQ4-B3 scientific settlement: `SCIENTIFIC_NO_GO`;
- economic observation: `DYNAMIC_BETA_DOES_NOT_BEAT_B2`;
- PR #72 remains non-Canon / not a basis for automatic promotion.

G0 does not rewrite, rescue or hide that result.

## 7｜Non-authorizations preserved

This machine qualification creates **no** authority for:

- protected-main merge;
- Supabase/runtime mutation;
- HF repository write;
- YMQ3-R0 canonical physical scientific run;
- Capital Admission;
- portfolio weighting or position sizing;
- VeighNa invocation;
- broker credentials/connection;
- broker paper order submission;
- live order submission;
- real capital movement;
- automatic research-to-capital or research-to-execution promotion.

## 8｜Current gate state

Evidence supports:

`YMQ_OS0_G0_MACHINE_QUALIFIED / AWAITING_HUMAN_REVIEW`

Machine qualification does **not** imply Human Acceptance.

Required next independent Human token:

# `ACCEPT_YMQ_OS0_G0_MACHINE_QUALIFICATION`

Only after that token is explicitly received may a Human Acceptance Receipt be created.

Human Acceptance would still **not** imply protected-main merge. Merge remains separately gated by:

# `AUTHORIZE_YMQ_OS0_G0_MERGE`

No acceptance or merge token may be inferred from the earlier Written Spec acceptance, CI success, this receipt, or the user's general instruction to execute autonomously.

## 9｜Post-receipt verification requirement

This receipt is itself a new candidate artifact. Therefore its commit/head must receive a fresh exact-head `repository-gates` run before it is presented as the final Human Review candidate.

Until that fresh post-receipt run is successful, the receipt is only a recorded qualification claim about the pre-receipt head.
