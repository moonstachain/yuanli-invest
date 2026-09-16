# YMQ-GOLD2 Gold Genesis Compiler — Implementation Plan

## Goal

Implement and machine-qualify the Gold Genesis macro-quant compiler through historical replay scaffolding, preserving all existing Gold/YMQ4/YIOS authority and stopping at Human Gate before live scheduler or capital authority.

## Execution order

### Task 1｜Constitution + machine contract
- Add `config/ymq_gold2/gold2_constitution.v0.1.json`.
- Encode upstream authority refs, B3 no-go preservation, unified state fields, allowed enums, hard negatives and zero-capital boundary.
- Add fail-closed validator.

### Task 2｜Unified State compiler
- Add `scripts/ymq_gold2_compiler.py`.
- Implement deterministic state validation and compilation helpers.
- Reject missing PIT timestamps, unknown authority, unsupported lifecycle labels and any execution authorization.

### Task 3｜Property Drift research layer
- Implement descriptive prior-only rolling sensitivity states.
- Preserve B2 fixed-beta opponent and B3 `DYNAMIC_BETA_DOES_NOT_BEAT_B2` as immutable benchmark history.
- Output research labels only; no alpha, price target or trade claim.

### Task 4｜Expectation × Reality + Valuation × Driver
- Implement categorical compilers.
- Require evidence authority and as-of timestamps.
- Fail closed to `INDETERMINATE` / `UNIDENTIFIABLE` when inputs are incomplete.

### Task 5｜Blind Replay harness
- Freeze eight historical regime windows.
- Build a replay packet contract: T0 state, frozen label, future settlement, learning delta.
- Add anti-leakage and hard-negative tests.

### Task 6｜Human triangulation contract
- Add RAY / Yiru / Machine independent slots.
- Machine may populate only its own slot.
- Empty human slots must remain `PENDING_HUMAN_EVIDENCE`.

### Task 7｜Live Shadow contract
- Add a 30-day live-shadow packet schema but do not activate scheduler.
- All capital/sizing/execution/broker booleans hard-false.
- Wind/provider identity remains replaceable and evidence-only.

### Task 8｜Verification and Human Gate
- Run focused unit tests.
- Run repository governance/contract checks through PR CI.
- Secret scan changed files.
- Create machine qualification receipt and Human Review Card.
- Open Draft PR.
- Stop before merge, Canon promotion, Human judgment fabrication or live scheduler activation.

## Required hard negatives

1. Post-T0 evidence enters a replay state → FAIL.
2. B3 scientific no-go is rewritten as success → FAIL.
3. Property drift is labeled dynamic-beta alpha → FAIL.
4. A missing human judgment is synthesized by machine → FAIL.
5. Research state grants sizing / capital / execution → FAIL.
6. Single-factor “inflation hedge” claim settles Gold state without broader evidence → FAIL.
7. Price appreciation alone proves thesis → FAIL.
8. Long-run regime thesis bypasses valuation/crowding → FAIL.

## Done definition

Branch may be marked `READY_FOR_HUMAN_REVIEW` only when:

- design + contract + code + tests exist;
- focused tests pass;
- PR CI governance/contracts pass;
- B2/B3/YIOS lineage is explicit and machine-checked;
- zero secret leakage;
- no scheduler, broker, capital or execution authority is enabled;
- unresolved human evidence remains visibly pending.