# YEX0 Capital × Execution Constitution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the approved YEX0 Capital × Execution Constitution into machine-checkable contracts that preserve Research/Capital/Execution authority separation and fail closed without creating any broker or live-execution runtime.

**Architecture:** Extend the existing vNext contract layer with five provider-neutral schemas plus a machine-readable YEX0 constitution. Add a fail-closed validator and positive/negative fixture bundle, then wire the validator into the existing `repository-gates` CI. Existing `PositionPassport` remains immutable in authority semantics and must continue to grant no execution authority.

**Tech Stack:** JSON Schema Draft 2020-12, Python stdlib + existing project dev dependencies, unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-09-yex0-capital-execution-constitution-design.md`

## Global Constraints

- No broker credentials, broker connection, VeighNa invocation, market-data subscription, live order, or real capital movement.
- Existing `PositionPassport` must retain all four authority flags as `const: false`.
- `Research Pass != Capital Pass != Execution Pass`.
- `UNKNOWN = DENY` at the firewall boundary.
- `Receipt = Ledger; Status = Projection`.
- `Research failure != Execution failure`.
- YEX0 may machine-qualify contracts only; merge and YVN1 remain separately authorized.

---

### Task 1: Contract tests first

**Files:**
- Create: `tests/test_yex0_capital_execution_constitution.py`

**Interfaces:**
- Consumes: existing `position-passport.schema.json`.
- Produces: executable RED contract for the new YEX0 validator and schema pack.

- [ ] **Step 1: Write failing tests** that import `scripts.validate_yex0_capital_execution_constitution` and assert:
  - five new schemas exist;
  - PositionPassport execution authority remains false;
  - CapitalAdmission cannot execute;
  - ExecutionIntent cannot self-authorize;
  - ActionContract supports only shadow/paper and live flags are false;
  - ExecutionEvent is append-only and hash-chained;
  - ExecutionSettlement requires four-way reconciliation and separates research outcome from execution quality;
  - positive fixture validates;
  - authority escalation / live / missing-reconciliation attacks are rejected.

- [ ] **Step 2: Open Draft PR and run repository CI**.

Expected: `contracts` RED because validator/module/contracts do not yet exist.

---

### Task 2: Machine-readable constitution and schemas

**Files:**
- Create: `config/yex0/yex0_constitution.v0.1.json`
- Create: `packages/contracts/schemas/vnext/capital-admission.schema.json`
- Create: `packages/contracts/schemas/vnext/execution-intent.schema.json`
- Create: `packages/contracts/schemas/vnext/action-contract.schema.json`
- Create: `packages/contracts/schemas/vnext/execution-event.schema.json`
- Create: `packages/contracts/schemas/vnext/execution-settlement.schema.json`

**Interfaces:**
- Produces: canonical machine contracts consumed by Task 3 validator.

- [ ] **Step 1:** Encode twelve YEX0 constitutional laws and explicit non-authorizations in `yex0_constitution.v0.1.json`.
- [ ] **Step 2:** Implement schemas with `additionalProperties:false`, explicit IDs, timestamps, identity references, and authority flags.
- [ ] **Step 3:** Keep executable modes to `shadow` and `broker_paper`; live and real-capital movement remain `const:false`.

---

### Task 3: Fixture bundle and fail-closed validator

**Files:**
- Create: `fixtures/yex0/yex0_positive_bundle.v0.1.json`
- Create: `scripts/validate_yex0_capital_execution_constitution.py`

**Interfaces:**
- Consumes: YEX0 constitution config, five schemas, existing PositionPassport.
- Produces: `validate_bundle(bundle)` plus independently testable validation functions.

- [ ] **Step 1:** Build one positive shadow-only bundle with CapitalAdmission → ExecutionIntent → ActionContract → ordered ExecutionEvents → reconciled ExecutionSettlement.
- [ ] **Step 2:** Implement shape/reference/authority/time/scope/ledger/reconciliation validation.
- [ ] **Step 3:** Fail closed on unknown/missing authority, live flags, expired scope, mismatched references, incomplete four-way reconciliation, and mutable-state-as-truth semantics.
- [ ] **Step 4:** Print `YEX0_CONSTITUTION_MACHINE_QUALIFIED` only after all checks pass.

---

### Task 4: Human-facing constitution and review card

**Files:**
- Create: `docs/architecture/yex0/YEX0-CAPITAL-EXECUTION-CONSTITUTION-v0.1.md`
- Create: `docs/architecture/yex0/YEX0-HUMAN-REVIEW-CARD-v0.1.md`

**Interfaces:**
- Consumes: approved spec and machine contracts.
- Produces: human-readable authority map and exact Human Gate checklist.

- [ ] **Step 1:** Freeze the three-authority separation and end-to-end object chain.
- [ ] **Step 2:** Freeze Action Gateway / Execution Runtime / provider-adapter boundaries.
- [ ] **Step 3:** Freeze Four-Way Reconciliation, Event Ledger, Golden Failure and security laws.
- [ ] **Step 4:** State explicit non-authorizations and next lawful battle `YVN1-A0`.

---

### Task 5: CI integration and GREEN verification

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: YEX0 validator and unittest suite.
- Produces: exact-head repository qualification evidence.

- [ ] **Step 1:** Add `python scripts/validate_yex0_capital_execution_constitution.py` after ME1 validation and before YIM0/project-wide unittest discovery.
- [ ] **Step 2:** Run PR CI.

Expected:
- YEX0 validator PASS;
- all YEX0 tests PASS;
- repository `contracts` PASS;
- repository `governance` PASS.

- [ ] **Step 3:** Verify PR diff contains no provider import, secret, broker endpoint, live-order code, or PositionPassport authority escalation.

---

### Task 6: Candidate settlement

**Files:**
- Create: `docs/architecture/yex0/YEX0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md`
- Modify: PR body only.

**Interfaces:**
- Consumes: exact-head CI evidence.
- Produces: candidate settlement without merge/execution authority.

- [ ] **Step 1:** Record exact head SHA and CI run outcome.
- [ ] **Step 2:** Freeze settlement as `YEX0_CONSTITUTION_MACHINE_QUALIFIED` only if all gates pass.
- [ ] **Step 3:** Keep PR Draft/Open/Not Merged; request separate Human Review for merge.
