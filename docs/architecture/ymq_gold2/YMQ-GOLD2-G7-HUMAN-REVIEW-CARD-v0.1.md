# YMQ-GOLD2-G7 Human Review Card v0.1

**Program:** YMQ-GOLD2
**Battle:** G7 — Data Live → Learning Live
**Current state:** `MACHINE_QUALIFIED_AWAITING_HUMAN_GATE`

## Review questions

1. Accept the provider-neutral daily chain `Live Receipt → State Delta → Settlement → Learning Candidate`?
2. Accept the rule that only successful earlier `as_of` receipts can become prior state, while provider failures and same-day duplicates are excluded?
3. Accept the frozen research-only attention thresholds: Gold 1.0% absolute daily move, real yield 10 bps, DXY 0.5%?
4. Accept `NOT_SCORABLE` whenever the prior state contains no preregistered directional claim?
5. Accept that price movement cannot prove Property Drift, Expectation × Reality, Valuation, or thesis correctness by itself?
6. Accept `LEARNING_CANDIDATE_ONLY` as non-authoritative output with `accepted_learning=false`?
7. Accept that the 2026-09-16 successful preflight may qualify the mechanism but must not be silently copied into production lineage?
8. Accept that current production lineage therefore begins with a warm-up on 2026-09-17 and needs the next later successful daily state before producing its first production Learning Candidate?
9. Preserve zero authority for capital, sizing, execution, broker, VeighNa, asset promotion, and Canon promotion?
10. Keep production scheduler integration disabled until a separate explicit authorization?

## Human Gate choices

- `ACCEPT_G7_RESEARCH_LEARNING_IMPLEMENTATION` — permits merge of the research implementation while keeping production G7 integration disabled.
- `AUTHORIZE_G7_PRODUCTION_INTEGRATION` — separate authorization to flip only `production_scheduler_integration_authorized` and deploy the gated post-processor into the existing G6 scheduler.
- `REVISE_G7` — keep Draft PR open and revise the contract or learning semantics.

No choice authorizes capital movement, portfolio sizing, order generation, broker access, VeighNa, accepted learning, asset promotion, or Canon promotion.
