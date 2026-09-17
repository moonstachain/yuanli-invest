# YMQ-GOLD2 Learning Live Design

**Program:** YMQ-GOLD2
**Battle:** G7 — Data Live → Learning Live
**Status:** USER_AUTHORIZED_IMPLEMENTATION

## Mother question
Can each successful Gold Live Shadow observation become a point-in-time, auditable learning candidate without inventing predictions, accepting learning, or granting investment authority?

## Architecture
`LIVE_SHADOW_RECEIPT(t-1) → LIVE_SHADOW_RECEIPT(t) → GoldStateDelta → DailySettlement → LearningCandidate`

The existing Wind acquisition runner remains the only provider-facing process. Learning Live is a deterministic post-processor over normalized receipts and never reads credentials or raw provider bodies.

## Daily identity
A new learning day requires a successful `LIVE_SHADOW_RECEIPT` whose `as_of` is later than the previous successful daily receipt. Repeated receipts on the same `as_of` are duplicates for daily learning and must not create a second settlement.

## GoldStateDelta
Track only normalized, provider-independent changes:
- gold price percent change;
- real-yield change in basis points;
- DXY percent change;
- evidence-date advance/regression;
- Property Drift / Expectation×Reality / Valuation / Research / Lifecycle state transitions;
- unknowns resolved and unknowns newly introduced.

Attention heuristics are research-only: gold >= 1.0% absolute daily move, real yield >= 10 bps absolute move, DXY >= 0.5% absolute daily move. They are not buy/sell or sizing thresholds.

## Settlement law
- PIT integrity must pass: provider evidence may not be future-dated; known-as-of may stay unchanged but may not regress versus the previous successful daily state.
- A state transition is recorded, not judged as correct merely because price moved.
- Directional claim scoring is `NOT_SCORABLE` unless a preregistered directional claim existed in the prior receipt.
- Regime detection lag and decision regret remain `PENDING`/`NOT_APPLICABLE` until the necessary preregistered objects exist.

## Learning candidate
Output `LEARNING_CANDIDATE_ONLY`, containing source receipt hashes, delta, settlement, unresolved unknown rate, material attention signals, and explicit authority. `accepted_learning=false`; no AST/CAN promotion.

## Runtime storage
Private runtime only under `$YMQ_GOLD2_SHADOW_DIR/learning/`; no Git persistence of daily runtime receipts and no local absolute paths in repository artifacts.

## Authority
Research processing and scheduler inheritance are allowed. Capital, sizing, execution, broker, VeighNa, accepted learning, asset promotion, and Canon promotion remain denied.
