# Q0｜CI + Human Gate v1

Status: `architecture_freeze_candidate`

## 1. Principle

CI proves machine invariants. Human Gate decides authority changes. Passing CI never means research truth or Canon promotion.

## 2. Required CI Jobs

### `architecture-contracts`

- validate all Q0 JSON files;
- validate JSON Schema syntax;
- validate 30-asset universe uniqueness;
- require every seed asset `initial_force_state=unknown`;
- reject ranking / target price / position / trade action fields;
- verify Q0 base revision is recorded.

### `point-in-time`

- replay fixtures reject `published_at > as_of`;
- same-day ambiguous timestamp returns review state;
- historical estimate queries cannot backfill current consensus;
- input manifest hashes are reproducible.

### `agent-contracts`

- all seven agent names match schema;
- specialist outputs cannot contain approved/admitted governance state;
- CIO final output must include counterevidence, falsifiers and unknowns;
- output schema strictness tests;
- prohibited action guard tests.

### `tool-policy`

- R0/R1/W1/G1/X registry is complete;
- normal specialists cannot access G1 or X tools;
- write tools require approval;
- broker/execution tools absent.

### `replay-regression`

- run deterministic validators over A4/A5 fixtures;
- no change to historical T0 definitions;
- no post-T0 source leakage;
- no automatic Outcome acceptance.

### `repository-boundary`

- raw documents / Parquet / DuckDB files not added to Git;
- no absolute local paths or secrets;
- no RSI FROZEN file writes from this repository;
- no A9 operational-canon activation receipt unless separately authorized.

## 3. Human Gates

### HG-Q0 Architecture Acceptance

Scope: architecture only.

Can accept:

- repository responsibilities;
- data model;
- schema candidates;
- agent pattern;
- MCP/tool boundary;
- seed universe as research fixture;
- replay/eval design;
- roadmap.

Does NOT authorize:

- production ingestion;
- A9 canon switch;
- Evidence admission;
- RSI FROZEN change;
- automated trading.

### HG-E Evidence Admission

Independent Evidence Reviewer accepts/rejects claims and locators.

### HG-C Canon Promotion

Promotes reviewed candidate research object into Canon.

### HG-O Outcome Acceptance

Accepts future outcome/settlement object.

### HG-RSI Challenger Ratchet

Allows a challenger method/runtime delta to enter RSI governed experimentation/promotion path.

### HG-A9 Operational Activation

Separate PMO/Governance Registry gate; outside Q0.

## 4. Risk-based Tool Approval

| Risk | Examples | Default |
|---|---|---|
| R0 | read asset/market/evidence/features | automatic |
| R1 | broad Wind search / costly scans | policy-limited |
| W1 | persist capture / open candidate PR | approval required |
| G1 | admit/promote/accept/governance writes | human always |
| X | broker execution / secrets / live allocation | unavailable |

## 5. Review Receipts

Every Human Gate receipt records:

- decision ID;
- reviewer identity/role;
- exact commit/SHA under review;
- CI run IDs;
- accepted scope;
- explicitly excluded scope;
- decision: `accept | accept_with_changes | reject`;
- timestamp.

## 6. Fail-closed Conditions

Immediately block promotion if:

- point-in-time leakage detected;
- evidence locator missing for material claim;
- runtime strips provenance;
- any tool performs unauthorized write;
- seed universe interpreted as recommendation;
- scalar P/N/X score introduced;
- production/canon authority changes without separate gate;
- raw licensed Wind material is committed to Git in violation of license/storage policy.
