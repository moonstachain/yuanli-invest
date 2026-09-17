# YMQ-GOLD2 Learning Live Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing 30-day Gold Live Shadow so every new successful daily state produces a fail-closed GoldStateDelta, DailySettlement, and non-authoritative LearningCandidate.

**Architecture:** Add a provider-neutral learning module that reads only normalized live-shadow receipts. Hook it into the successful live-shadow path after receipt persistence; provider acquisition remains unchanged and learning failure cannot fabricate or upgrade a research state.

**Tech Stack:** Python 3.11, JSON contracts, pytest/unittest, existing launchd runtime.

**Spec:** `docs/superpowers/specs/2026-09-17-ymq-gold2-learning-live-design.md`

## Global Constraints
- no provider credential access in learning code;
- no raw provider body persistence;
- no future evidence or known-as-of regression;
- same-day duplicate receipts do not create a new daily settlement;
- no directional scoring without a preregistered claim;
- capital/sizing/execution/broker/VeighNa/accepted-learning/Canon all remain false.

### Task 1 — Freeze Learning Live contract
Create `config/ymq_gold2/gold2_learning_live.v0.1.json` and tests proving the authority ceiling, thresholds, storage policy, and scoring law.

### Task 2 — Implement GoldStateDelta
Create `scripts/ymq_gold2_learning_live.py` with receipt identity, prior-day selection, PIT validation, normalized delta math, state transitions, and unknown resolution.

### Task 3 — Implement DailySettlement and LearningCandidate
Add deterministic settlement and learning-candidate construction, including `NOT_SCORABLE` when no prior directional claim exists and `accepted_learning=false`.

### Task 4 — Integrate daily chain
Modify `scripts/ymq_gold2_live_shadow.py` so a successful receipt triggers Learning Live after persistence. Provider failure remains provider fail-closed; learning failure is explicit and never changes the provider receipt.

### Task 5 — Reality replay and verification
Run Learning Live against the existing 2026-09-16 → 2026-09-17 private Gold receipts in an isolated preflight output root, verify actual delta/settlement, then run focused tests, full repository tests, `git diff --check`, leak guard, and secret scan. Create Draft PR and stop at Human Gate before merge/production activation.
