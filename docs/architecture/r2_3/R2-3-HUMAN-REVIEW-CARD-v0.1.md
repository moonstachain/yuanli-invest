# R2.3 Human Review Card v0.1

R2.3 只要求 Human Review 三个问题；其余确定性事项由 CI 验证。

## Q1 | Ledger -> Projection

是否接受：R2.2 merge receipt 成为不可变事实账本之一，而 README / `CANON-STATUS.json` / stage state 仅作为确定性投影，并由 CI 检查漂移？

## Q2 | V Capability successor

是否接受：
- 历史 `CAP-V-001-REVERSE-DCF-EXPECTATIONS` 永久保留；
- 当前 vNext 研究问题身份升级为 `CAP-V-002-PRICE-IMPLIED-EXPECTATIONS`；
- `ALG-V-REVERSEDCF-IMPLIED-EXPECTATIONS` 降为该 Capability 的一个 Algorithm；
- 不产生 target price 或交易法权？

## Q3 | S Capability successor

是否接受：
- 历史 `CAP-S-002-ROBUST-FRACTIONAL-KELLY` 永久保留；
- 当前 vNext 研究问题身份升级为 `CAP-S-003-GROWTH-OPTIMAL-RISK-BUDGET-UNDER-UNCERTAINTY`；
- `ALG-S-KELLY-ROBUST-FRACTIONAL` 降为该 Capability 的一个 Algorithm；
- Capability 输出仅为 growth/survival risk-budget research state，不产生推荐仓位、权重或 live sizing？

## Boundary

若三项全部接受，current vNext effective Gold 仍为 12，不扩第二批 Gold。R3A 仍需 R2.3 merge 后才可启动。

Proposed Human Gate token:

`ACCEPT_R2_3_RUNTIME_BLOCKER_CLOSURE`
