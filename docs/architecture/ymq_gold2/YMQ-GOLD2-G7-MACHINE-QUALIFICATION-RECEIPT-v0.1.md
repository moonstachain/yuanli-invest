# YMQ-GOLD2-G7 Machine Qualification Receipt v0.1

**Program:** YMQ-GOLD2
**Battle:** G7 — Data Live → Learning Live
**Qualification state:** `MACHINE_QUALIFIED_AWAITING_HUMAN_GATE`
**Implementation code head:** `04dd687d3543ad68041c0ea15bf08472f6a41585`

## Qualified chain

`LIVE_SHADOW_RECEIPT(t-1) → LIVE_SHADOW_RECEIPT(t) → GoldStateDelta → DailySettlement → LEARNING_CANDIDATE_ONLY`

The G7 post-processor is provider-neutral and reads normalized G6 receipts only. It has no provider credential access and does not call Wind or any external provider.

## TDD evidence

RED was observed twice and corrected for test validity:
1. the first run failed because the test imported `pytest`, which the repository CI does not install; this was rejected as an invalid RED;
2. after conversion to repository-standard `unittest`, CI failed specifically because `scripts.ymq_gold2_learning_live` did not exist;
3. after core implementation, repository gates and the GOLD2 workflow passed;
4. integration tests were then added and correctly failed because `emit_learning_live` did not exist;
5. the gated integration hook was implemented and exact-head CI passed.

## Private Reality Replay

A read-only replay was run against two existing private runtime receipts:
- prior successful preflight: `as_of=2026-09-16`, evidence through `2026-09-15`;
- current production scheduler receipt: `as_of=2026-09-17`, evidence through `2026-09-16`.

Derived delta:
- Gold price: `+0.7460167825%`;
- US long real yield: `+1.0 bp`;
- DXY: `+0.6983594875%`;
- research-only attention: `usd_pct` only;
- Property Drift: `DRIFT_CANDIDATE → DRIFT_CANDIDATE`;
- Expectation × Reality: `INDETERMINATE → INDETERMINATE`;
- Valuation: `UNIDENTIFIABLE → UNIDENTIFIABLE`;
- Research State: `WATCH → WATCH`;
- unknowns resolved: none;
- unknowns added: none.

The failed 2026-09-16 production receipt was explicitly rejected as a prior learning state because it had `PROVIDER_FAIL_CLOSED` and no provider observations. This validates the rule that only successful earlier daily receipts may become prior state.

## Settlement interpretation

No preregistered directional claim exists in the prior receipt, therefore the directional score is `NOT_SCORABLE`. Price movement is not accepted as proof of thesis correctness. Regime detection lag remains `PENDING`; decision regret remains `NOT_APPLICABLE` without a decision object.

## Authority firewall

The default contract keeps `production_scheduler_integration_authorized=false`. The integration code exists but remains inert in production until a separate Human Gate flips that field.

Always denied:
- accepted learning;
- asset promotion;
- Canon promotion;
- capital;
- sizing;
- execution;
- broker action;
- VeighNa.

## Operational note

The formal production runtime has no successful 2026-09-16 daily receipt; its first successful production day is 2026-09-17. Therefore, if G7 is activated immediately, production Learning Live should correctly emit `LEARNING_WARMUP_PENDING` until a later successful `as_of` exists. The private preflight receipt was used for qualification only and is not silently copied into production lineage.
