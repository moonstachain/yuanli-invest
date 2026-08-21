# RIOS-0.1-C｜Capability Registry Materialization & Governance Gate — Design v0.1

Status: `candidate_ready_for_written_spec_review`

Base: `main@bd8931e1bf21dceb5e34a68ec41aa199b83e9410`

## 0. Decision summary

RIOS-0.1-C SHALL NOT create a second capability registry or a parallel capability schema.

The repository already contains the canonical R1 object model and nine Registry namespaces, including `registry/capabilities/`, together with the production-candidate `ResearchCapability` JSON Schema and R2 specified capabilities. Therefore RIOS-0.1-C is a **convergence and materialization layer** that projects the RIOS Genesis Capability Pack onto the existing R1/R2 object system.

Core law:

> RIOS is a runtime/research operating-system projection over the existing ResearchCapability Canon architecture; it is not a competing authority system.

This design preserves:

- existing `ResearchCapability` schema and ID rules;
- existing nine Registry namespaces;
- maturity lifecycle `concept → specified → implemented → replicated → benchmark_passed → shadow_qualified → canon → deprecated`;
- Provider Independence;
- scalar PNX/Force-score prohibition;
- target-price / buy-sell / recommended-weight / position-size / live-execution prohibitions;
- Human Gate for promotion.

## 1. Why this design is necessary

The previously proposed RIOS Genesis Pack contains ten human-facing capability ideas:

1. AI Infrastructure Regime Transition
2. Energy Bottleneck Capture
3. Narrative Diffusion Engine
4. Narrative Bubble Detection
5. Platform Winner Capture
6. Convexity Expression Engine
7. Evidence Authority Engine
8. Narrative Price Gap
9. Portfolio Survival Engine
10. Market Clock Regime Transition

Current repository reality already includes specified mother capabilities such as:

- `CAP-P-001-TECHNOLOGY-COST-CURVE`
- `CAP-P-002-ADOPTION-ACCELERATION`
- `CAP-N-001-NARRATIVE-VELOCITY`
- `CAP-N-002-NARRATIVE-SATURATION`
- `CAP-XS-001-MARKET-SHARE-ACCELERATION`
- `CAP-XS-002-BOTTLENECK-SCARCITY`
- `CAP-XA-001-CONDITIONAL-TAIL-ACTIVATION`
- `CAP-XA-002-EXTREME-REGIME-SHIFT`
- `CAP-XP-001-PAYOFF-CONVEXITY-GEOMETRY`
- `CAP-V-001-REVERSE-DCF-EXPECTATIONS`
- `CAP-S-001-RUIN-AND-EXPECTED-SHORTFALL`
- `CAP-S-002-ROBUST-FRACTIONAL-KELLY`

RIOS-0.1-C must therefore distinguish between:

- **Mother Capability** — canonical reusable ResearchCapability identity;
- **Profile** — domain/theme/asset-form specialization of an existing capability;
- **Composite / Orchestration Pack** — ordered set of capabilities used together for a research question;
- **New Capability Candidate** — created only when no existing mother capability can faithfully express the function.

## 2. Alternatives considered

### Approach A — Parallel RIOS registry

Create `/capabilities/`, `registry.yaml`, and a separate RIOS schema.

Rejected because it creates duplicate authority, ID drift, lifecycle drift, and conflicting validation.

### Approach B — Rename existing R1/R2 capabilities to match the ten Genesis labels

Rejected because it mutates already-governed capability identities and confuses human-facing RIOS vocabulary with canonical machine identity.

### Approach C — Convergence-first projection over R1/R2 — SELECTED

Keep canonical capability identities stable. Materialize the Genesis Pack as a governed RIOS projection that maps each human-facing Genesis concept to one of:

- existing mother capability;
- theme/profile binding;
- composite orchestration;
- explicitly justified new capability candidate.

This is the lowest-authority, highest-reuse design.

## 3. Genesis convergence map

### 3.1 Reuse / orchestration, not new mother capabilities

`Narrative Diffusion Engine`
→ reuse `CAP-N-001-NARRATIVE-VELOCITY` + `CAP-N-002-NARRATIVE-SATURATION` as a composite narrative-dynamics pack.

`Narrative Bubble Detection`
→ composite of `CAP-N-002-NARRATIVE-SATURATION`, `CAP-V-001-REVERSE-DCF-EXPECTATIONS`, `CAP-XA-002-EXTREME-REGIME-SHIFT`; no independent mother capability in RIOS-0.1-C.

`Platform Winner Capture`
→ reuse `CAP-XS-001-MARKET-SHARE-ACCELERATION` + `CAP-XS-002-BOTTLENECK-SCARCITY`; theme-specific profiles may be added later.

`Convexity Expression Engine`
→ orchestration of `CAP-XA-001`, `CAP-XA-002`, and `CAP-XP-001`; no scalar X score.

`Narrative Price Gap`
→ human-facing alias/orchestration over V-layer Price-Implied Expectations / Reverse-DCF capability. It must never create target price output.

`Portfolio Survival Engine`
→ orchestration over `CAP-S-001` and `CAP-S-002` plus future liquidity/stress capabilities when formally admitted.

### 3.2 Profiles, not new mother capabilities

`AI Infrastructure Regime Transition`
→ RIOS Profile / Composite binding over P + XS + N + V capabilities, not a standalone mother ResearchCapability in this stage.

`Energy Bottleneck Capture`
→ theme profile over `CAP-P-001/002` + `CAP-XS-002-BOTTLENECK-SCARCITY`, with canonical energy/power data fields deferred to provider/data-plane work.

Profiles must not redefine canonical semantics and must not embed Wind-specific fields.

### 3.3 Genuine candidate gaps

`Evidence Authority Engine`
→ candidate for a new `E`-domain ResearchCapability because current R2 Gold Pack has no E-domain capability. Candidate purpose: evaluate claim/evidence authority, contradiction coverage, provenance quality, and authority ceilings. It SHALL NOT claim truth or causal validity by itself.

`Market Clock Regime Transition`
→ candidate for a `CROSS` ResearchCapability only if the existing Market Clock architecture cannot be represented as a simple orchestration. Its state must remain `concept` or `specified` and it must not emit trade actions. L/E/N state output is research state only.

No new capability candidate is allowed merely because the RIOS human-facing label is attractive.

## 4. New artifact model

RIOS-0.1-C introduces an architecture-level projection under:

`docs/architecture/rios/0.1-c/`

Planned artifacts:

- `RIOS-0.1-C-CAPABILITY-CONVERGENCE-MATRIX-v0.1.json`
- `RIOS-0.1-C-GENESIS-PACK-v0.1.json`
- `RIOS-0.1-C-HUMAN-REVIEW-CARD-v0.1.md`
- `RIOS-0.1-C-STATE.json`

If and only if Human Review accepts genuine new candidate identities, a later apply phase may add a pack file under `registry/capabilities/` and update `_index.json` / `registry-index.json`.

RIOS-0.1-C pre-Human phase SHALL NOT mutate:

- `registry/capabilities/`
- any other Registry namespace;
- `canon/`;
- runtime/live execution code.

## 5. Convergence Matrix contract

Each of the ten Genesis concepts must have exactly one row with:

- `genesis_id`
- `human_name`
- `classification`: `reuse | composite | profile | new_candidate | reject`
- `canonical_capability_ids`
- `candidate_capability_id` nullable
- `rationale`
- `semantic_overlap_notes`
- `authority_boundary`
- `registry_mutation_required`
- `benchmark_execution_authorized=false`
- `runtime_authorized=false`
- `trading_authorized=false`

Machine gate must require exact coverage of all ten and prohibit an eleventh silent Genesis concept.

## 6. Genesis Pack contract

The Genesis Pack is NOT itself a Registry and NOT a list of canon capabilities.

It is an orchestration manifest containing:

- `pack_id = RIOS-GENESIS-PACK-001`
- `status = candidate_orchestration_pack`
- ten human-facing concepts;
- canonical capability dependencies;
- candidate gaps;
- Agent routing hints;
- Replay prerequisites;
- explicit non-authorities.

The pack SHALL NOT contain:

- target price;
- buy/sell signal;
- recommended/target weight;
- position size;
- broker action;
- live execution;
- scalar P/N/X/Force score;
- `canon` maturity claims.

## 7. Candidate identity rules

If E and Market Clock are proposed as new ResearchCapability candidates, IDs must follow current schema:

- proposed E identity: `CAP-E-001-EVIDENCE-AUTHORITY-VALIDATION`
- proposed CROSS identity: `CAP-CROSS-002-MARKET-CLOCK-REGIME-TRANSITION`

The final CROSS number must be checked against current Registry before apply; duplicate ID is fail-closed.

A new candidate object must satisfy the existing `ResearchCapability` schema, which means it cannot be materialized into Registry until its referenced Theory/Hypothesis plus at least one Factor or Algorithm, Benchmark, CanonicalDataField, and output contract exist. RIOS-0.1-C SHALL NOT weaken the schema to make insertion easier.

Therefore Human Review may legitimately decide:

- `candidate_identity_accepted_but_registry_deferred`

when dependencies are not yet complete.

## 8. Agent routing model

RIOS Agent Council uses routing metadata, not duplicated capability semantics.

- P Agent → P mother capabilities + P profiles
- N Agent → N mother capabilities
- X Agent → XS/XA/XP orchestration
- E Agent → existing evidence objects plus future E capability when admitted
- V Agent → V capability
- S Agent → S capabilities
- Chief/Committee → CROSS orchestration only

Routing is research-only. No agent receives portfolio execution authority in this stage.

## 9. Governance validator

Planned validator:

`scripts/validate_rios_0_1_c_capability_registry.py`

It must fail closed on:

1. missing or duplicate coverage of the ten Genesis concepts;
2. parallel registry/schema creation outside existing R1 topology;
3. mutation of existing R2 capability identities in pre-Human phase;
4. duplicate proposed capability IDs;
5. unsupported `canon`, `validated`, `benchmark_passed`, or runtime claims;
6. investment-action fields or scalar PNX/Force score;
7. Wind/provider-specific field semantics leaking into capability identity;
8. Genesis concept classified `new_candidate` without explicit semantic-gap rationale;
9. any claim that a profile/composite is itself a canon ResearchCapability;
10. Registry apply before Human Acceptance.

CI qualification is structural/governance validity, not evidence validity or investment validity.

## 10. Human Review Gate

Human Review evaluates each Genesis concept on:

- semantic necessity;
- overlap with existing capability graph;
- mother-vs-profile-vs-composite classification;
- reusability across assets/regimes;
- evidence/replay prerequisites;
- authority boundary;
- whether new candidate identity is justified.

Allowed Human dispositions per row:

- `reuse_confirmed`
- `composite_confirmed`
- `profile_confirmed`
- `new_candidate_identity_accepted_registry_deferred`
- `new_candidate_ready_for_registry_apply`
- `revise`
- `reject`

Reserved acceptance token:

`ACCEPT_RIOS_0_1_C_CAPABILITY_CONVERGENCE_AND_GOVERNANCE`

Acceptance does NOT imply merge or Registry mutation.

Reserved merge/apply authorities must remain separate and will be defined in the implementation plan.

## 11. State machine

RIOS-0.1-C states:

`design_accepted`
→ `convergence_compilation_started`
→ `candidate_ready_for_human_review`
→ after Human Acceptance and exact-head CI: `human_accepted_ready_for_apply_plan`
→ later governed Registry apply, if any
→ `accepted_merged`

No intermediate state may imply benchmark execution, capability implementation, Agent runtime, portfolio action, or trading.

## 12. Testing strategy

TDD implementation plan must include:

- RED: missing convergence matrix;
- GREEN: exact ten-row matrix;
- RED: duplicate/parallel capability identity;
- GREEN: reuse/composite/profile classification;
- negative tests for target price, buy/sell, weight, position size, live execution, scalar Force score;
- negative test for provider-specific field in capability semantic identity;
- negative test for pre-Human Registry diff;
- schema-compatibility test for any proposed new ResearchCapability object;
- exact-head `contracts` + `governance` CI.

## 13. Exit criteria

RIOS-0.1-C is ready for Human Review only when:

1. all 10 Genesis concepts are classified exactly once;
2. existing R1/R2 capability identities are reused where semantically sufficient;
3. every proposed new candidate has explicit gap rationale;
4. no production Registry mutation has occurred;
5. no Canon/runtime/trading authority has been created;
6. validator and tests pass on exact head;
7. Human Review Card is complete.

RIOS-0.1-C is successful even if the Human Review admits zero new mother capabilities. The strategic objective is **capability-system convergence**, not object-count growth.

## 14. Explicit non-goals

This stage does not:

- create 10 new ResearchCapability objects by default;
- create a second Registry;
- rename accepted R1/R2 capability IDs;
- create ProviderAdapters;
- execute Benchmarks or Replays;
- implement Agent Council runtime;
- change portfolio positions;
- issue investment recommendations;
- switch A9 operational canon.

## 15. Follow-on

After Written Spec Acceptance, create a detailed implementation plan. Expected next technical sequence:

1. Convergence Matrix + Genesis Pack + validator (pre-Human, zero Registry mutation)
2. Human Review
3. Optional governed apply for only accepted new identities whose dependencies satisfy the existing schema
4. `RIOS-0.2｜Capability Replay Engine Bootstrap`

The first Replay stage should test whether this convergence architecture actually improves transferability and avoids duplicate research identities before RIOS expands capability count.