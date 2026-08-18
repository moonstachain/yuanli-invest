# Q0｜Force Agent Contracts v1

Status: `architecture_freeze_candidate`

## 1. Orchestration Pattern

Default pattern: **Manager + Specialists as Tools**.

`ForceCIOAgent` is the only agent allowed to assemble a complete Force candidate. Specialists return narrow structured artifacts and cannot directly promote Canon.

```text
ForceCIOAgent
  ├─ ParadigmAgent
  ├─ NarrativeAgent
  ├─ ConvexityAgent
  ├─ FundamentalAgent
  ├─ RedTeamAgent
  └─ EvidenceJudgeAgent
```

Handoffs are reserved for long-running investigation branches; ordinary production flow uses specialists-as-tools so the CIO keeps one auditable task state.

## 2. Shared Contract

Every agent run MUST receive:

- `subject_id`
- `as_of`
- `input_manifest_hash`
- allowed tool list
- point-in-time policy
- prohibited action policy
- required output schema

Every output MUST include:

- claims and counterclaims;
- evidence IDs, not uncited prose;
- explicit unknowns;
- at least one falsifier per material claim;
- `lookahead_check`;
- no trade/position/target-price/recommendation payload;
- `run_id`, `trace_id`, `runtime_profile`.

If required evidence is missing, return `partial` or `blocked`, not invented facts.

## 3. ForceCIOAgent

### Mission

Turn an asset or narrative research question into a reviewable Force candidate package.

### Allowed

- call six specialists;
- request additional read-only evidence/features;
- reconcile contradictory specialist outputs;
- form `ForceRadarSnapshotCandidate`;
- set `research_priority`.

### Forbidden

- admitting Evidence;
- approving Canon;
- accepting Outcome;
- changing RSI rules;
- live trading/action;
- scalar P×N×X score.

### Required final output

- P/N/X states;
- Fundamental/Survival gates;
- classification candidate;
- evidence/counterevidence;
- disagreements;
- unknowns;
- falsifiers;
- next evidence requests;
- Human Gate requirement.

## 4. ParadigmAgent

### Mission

Evaluate structural paradigm migration, not stock popularity.

### Six surfaces

`technology_breakthrough, cost_curve, infrastructure, capital_formation, institutional_adaptation, productivity_diffusion`

### Required behavior

- separate paradigm truth from asset value capture;
- assign one stage: `emergence|installation|frenzy|turning_point|deployment|maturity|unknown`;
- identify evidence gaps and alternative paradigms;
- never use later success as proof of earlier paradigm strength.

## 5. NarrativeAgent

### Mission

Track how a narrative diffuses across cohorts and whether it is accelerating, crowded or reversing.

### Cohorts

`researchers, developers, founders, enterprises, investors, media, government, consumers`

### Required behavior

- distinguish raw event from narrative propagation;
- evaluate cross-cohort transitions;
- return `discover|accelerate|consensus|decay|residual|unknown`;
- explicitly surface reverse narratives and crowding;
- reject any post-`as_of` source.

## 6. ConvexityAgent

### Mission

Assess asymmetric value capture and ruin risk.

### Right tail

`winner_take_most, network_effects, scale_economics, bottleneck_control, platform_optionality, market_expansion, value_capture`

### Left tail

`balance_sheet_fragility, refinancing_dependency, dilution_risk, concentration_risk, regulatory_ruin, technical_obsolescence, valuation_cashflow_mismatch`

### Required behavior

- never infer company value capture merely from industry growth;
- combine deterministic risk features with evidence;
- keep EVT/VaR/ES as left-tail subcomponents only;
- return `convexity_state` and `left_tail_state`.

## 7. FundamentalAgent

### Mission

Attempt to falsify the narrative using economic reality.

### Core checks

- revenue and growth quality;
- gross/operating margin;
- FCF and cash conversion;
- customer adoption/orders/backlog where valid;
- CAPEX and working capital;
- estimate revisions and dispersion;
- valuation-to-cashflow mismatch.

### Output

`fundamental_gate = passed|partial|failed|unknown`

No direct Force classification.

## 8. RedTeamAgent

### Mission

Attack the entire candidate as if known historical outcomes were hidden.

### Mandatory attacks

- hindsight leakage;
- confirmation bias;
- source dependence / circular citation;
- survivorship and winner bias;
- narrative crowding;
- technical substitution;
- policy/regulatory break;
- capital-cycle overbuild;
- valuation/cash-flow mismatch;
- missing counterevidence.

### Required output

- strongest 3 reasons the candidate could be wrong;
- evidence for each attack;
- which P/N/X state should be downgraded if attack succeeds;
- unresolved questions;
- whether classification should remain `unknown`.

## 9. EvidenceJudgeAgent

### Mission

Judge source/claim eligibility. It does not decide investment merit.

### Decisions

`accept_support | accept_counterevidence | reject_insufficient | reject_post_t0 | reject_wrong_locator | needs_timestamp_review`

### Checks

- source authenticity and type;
- published time vs T0/as_of;
- locator reproducibility;
- claim does not exceed source;
- supporting vs counterevidence direction;
- duplicated or circular sources;
- accepted machine evidence still requires independent human admission where governance demands it.

## 10. Runtime Profile

Do not hard-code model names in Canon. Runtime config MUST expose:

```yaml
reasoning_model: ${MODEL_REASONER}
fast_model: ${MODEL_FAST}
batch_model: ${MODEL_BATCH}
max_turns: 24
tracing: true
point_in_time_guard: true
prohibited_action_guard: true
```

Suggested mapping by task class:

- CIO / Red Team / difficult adjudication -> `reasoning_model`;
- normal specialist synthesis -> `reasoning_model` or `fast_model` based on eval;
- tagging/entity/claim extraction -> `fast_model`;
- overnight universe scan -> `batch_model`.

Model promotion requires replay/eval evidence, not intuition.

## 11. Guardrails / HITL

Input guardrails:

- valid asset/as_of;
- no request for live execution;
- valid T0 for replay.

Tool guardrails:

- reject data after `as_of` in replay mode;
- prohibit tool calls outside allow-list;
- writes require explicit approval policy.

Output guardrails:

- strict schema;
- no scalar Force score;
- no buy/sell/position/target price;
- all material claims cite evidence;
- unknown preserved where evidence incomplete.

Always-human actions:

- Evidence admission;
- Canon promotion;
- Outcome acceptance;
- A9 operational-canon switch;
- RSI FROZEN change;
- any future broker/execution integration.
