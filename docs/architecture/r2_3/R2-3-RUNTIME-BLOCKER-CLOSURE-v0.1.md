# R2.3 | Runtime Blocker Closure v0.1

## Purpose

R2.3 is deliberately narrow. It closes only the three semantic blockers that would otherwise be compiled into R3A Runtime interfaces.

1. **Post-merge Status / Receipt closure** — prove `Ledger -> Projection` after R2.2 merge.
2. **V Capability successor** — stable research question `Price-Implied Expectations` outranks a single implementation such as Reverse DCF.
3. **S Capability successor** — stable research question `Growth-Optimal Risk Budget under Uncertainty` outranks a single Kelly implementation.

## Non-goals

R2.3 does **not**:
- redesign the other ten R2 Gold capabilities;
- add a second Gold pack;
- implement Wind ProviderAdapters;
- implement Codex skills or Reference Quant Runtime calculations;
- execute benchmarks, replay or future settlement;
- authorize portfolio weights, recommended sizing, buy/sell, target prices or live execution;
- switch the A9 operational canon;
- unfreeze RSI.

## Successor law

Historical IDs are immutable. R2.3 therefore does not rename or overwrite:
- `CAP-V-001-REVERSE-DCF-EXPECTATIONS`;
- `CAP-S-002-ROBUST-FRACTIONAL-KELLY`.

Instead it proposes explicit successors:
- `CAP-V-002-PRICE-IMPLIED-EXPECTATIONS`;
- `CAP-S-003-GROWTH-OPTIMAL-RISK-BUDGET-UNDER-UNCERTAINTY`.

The predecessor algorithms remain valid candidate implementations:
- `ALG-V-REVERSEDCF-IMPLIED-EXPECTATIONS` under the broader V capability;
- `ALG-S-KELLY-ROBUST-FRACTIONAL` under the broader S capability.

No benchmark result is implied. Both successors remain `specified`.

## Gold-set semantics

R2 historical Gold remains an immutable 12-object pack. If R2.3 is Human Accepted and merged, the **current vNext effective Gold set remains 12**, consisting of ten retained R2 identities plus these two explicit successors. The two predecessors remain historical objects and are not deleted.

## R3A boundary

R3A remains paused until R2.3 is merged. After merge, R3A may bind the V vertical slice to `CAP-V-002-PRICE-IMPLIED-EXPECTATIONS`. No other runtime authority is created by this stage.
