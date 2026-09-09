# YEX0 Machine Qualification Receipt v0.1

## Settlement

`YEX0_CONSTITUTION_MACHINE_QUALIFIED`

This receipt qualifies the provider-neutral Capital × Execution Constitution and contracts only. It grants no merge, broker, portfolio-sizing, paper-trading, live-trading, or real-capital-movement authority.

## Semantic qualification head

- Branch: `yex0-capital-execution-constitution`
- Semantic qualification commit: `29aa3cda47ab03d8db7e878eddb76fbfd9036caa`
- Repository-gates run: `34307533570`
- `contracts`: **SUCCESS**
- `governance`: **SUCCESS**
- YEX0 validator: **SUCCESS**
- Repository unittest discovery: **SUCCESS**

The YEX0 validator emitted:

`YEX0_CONSTITUTION_MACHINE_QUALIFIED`

## TDD evidence

### RED

Initial PR run `34306994968`:

- governance: PASS;
- contracts: FAIL at unittest discovery because the YEX0 validator/module and contracts intentionally did not yet exist.

### Implementation / diagnostic checkpoint

Run `34307345179`:

- standalone YEX0 validator: PASS;
- governance: PASS;
- one YEX0 schema-introspection unit test failed because the test incorrectly read `reconciliation.required` from `reconciliation.properties`.

Root cause was in the test assertion path, not the production schema. The production schema already placed `required` correctly at the reconciliation-object level.

### GREEN

The test-only assertion was repaired without changing production contracts. Exact semantic head `29aa3cda47ab03d8db7e878eddb76fbfd9036caa` then passed repository-gates run `34307533570` with both required jobs green.

## Machine-qualified contract surface

YEX0 freezes these five new provider-neutral contracts:

1. `CapitalAdmission`
2. `ExecutionIntent`
3. `ActionContract`
4. `ExecutionEvent`
5. `ExecutionSettlement`

It also preserves the existing ME1 `PositionPassport` authority boundary.

## Frozen authority state

- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`
- PositionPassport portfolio-weight authority: `false`
- PositionPassport position-sizing authority: `false`
- PositionPassport trade-execution authority: `false`
- PositionPassport live-execution authority: `false`
- CapitalAdmission order-submission authority: `false`
- ActionContract live-execution authority: `false`
- ActionContract real-capital-movement authority: `false`
- ExecutionSettlement grants-new-capital-authority: `false`
- ExecutionSettlement grants-new-execution-authority: `false`

## Frozen execution laws

- `Research Pass != Capital Pass != Execution Pass`
- `Intent != Authorization`
- `UNKNOWN = DENY`
- `Receipt = Ledger; Status = Projection`
- Four-way reconciliation is the production invariant.
- `ResearchFailure != ExecutionFailure`
- execution-provider adapters remain replaceable and non-sovereign.
- material execution failures become Golden Failure regression evidence.

## Diff / security review

The semantic qualification diff contains only:

- architecture/design/plan/review documents;
- YEX0 config and JSON Schemas;
- synthetic fixture;
- validator and tests;
- one CI validator hook.

No provider adapter, VeighNa import, broker endpoint, credential, market-data connection, order-submission runtime, or PositionPassport authority escalation is introduced.

## Explicit non-authorizations

YEX0 does **not** authorize:

- broker/exchange credential creation;
- VeighNa installation or invocation;
- market-data subscription;
- paper-broker order submission;
- live-order submission;
- portfolio weighting;
- position sizing;
- real capital movement;
- YVN1/YVN2/YVN3 execution;
- Canon promotion;
- merge.

## Current gate

`MACHINE_QUALIFIED / AWAITING_HUMAN_REVIEW`

Candidate Human Review token:

`ACCEPT_YEX0_CAPITAL_EXECUTION_CONSTITUTION`

Only after a separate Human Review and separately authorized merge may the next battle be opened:

`YVN1-A0｜Shadow Execution Constitution & Deployment Freeze`
