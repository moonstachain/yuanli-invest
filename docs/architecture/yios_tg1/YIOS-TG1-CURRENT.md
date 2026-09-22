# YIOS-TG1｜CURRENT

**Program:** Yuanli Investment OS · Trade Guidance Product  
**Status:** `G0_AUTHORIZED_TO_EXECUTE / SHADOW_ONLY`  
**Known As Of:** 2026-09-22  
**Master Issue:** https://github.com/moonstachain/yuanli-invest/issues/107  
**Human Cockpit:** https://app.notion.com/p/3e38e1aaace4813eb8d2c4e4495a710e?pvs=204

## Purpose

把已有 Research Runtime 收束成可每日使用的 Trade Guidance Product：

```text
Reality
→ Evidence / PIT
→ Research State
→ Reality Audit
→ TradeDecisionCandidate
→ Capital Admission
→ Shadow PositionPassport
→ Shadow Settlement
→ LearningDelta
→ Next-Task Pre-Action Recall
→ Decision Delta
```

TG1 不授权 Broker / VeighNa / Live Execution / Real Capital。

## Product Language

前台 Action State：

`WAIT / PROBE / HOLD / REDUCE / HEDGE`

硬边界：

- `Research != Capital != Execution`
- `UNKNOWN = DENY`
- `WAIT / DENY` 是合法完成态
- Research pass 不自动产生 sizing 或 execution authority

## Current Reality

### Proven / Existing

- GOLD2 G6 Live Shadow 在 M4 每日 08:10 运行。
- 2026-09-22 已产生 successful `LIVE_SHADOW_RECEIPT`。
- G7 已产生 `LEARNING_CANDIDATE_ONLY`。
- Wind 当前 live spine：Gold Spot / DXY / US long real yield。
- `yuanli-invest-runtime` Supabase 已存在 Evidence / PIT / Runtime schema。
- `yuanli-life/yuanli-os` 已证明 Web / CLI / MCP → One Kernel 的 Private Preview。

### Product Gaps

- M4 G6/G7 → Supabase Reality Sink 尚未闭环。
- strict product PIT timestamps 尚未完整冻结。
- central-bank demand + stress proxy 尚未成为 P0 live evidence slots。
- `TradeDecisionCandidate` 尚未成为 runtime object。
- Invest Domain Gateway / Gold Product API 尚未形成。
- Gold Decision Cockpit 尚未连接真实 backend。
- Supabase `shadow_settlements` / `learning_deltas` 尚未形成真实产品闭环。

## Gates

| Gate | Battle | Current |
|---|---|---|
| G0 | Product Constitution × Architecture Freeze | AUTHORIZED / CANDIDATE FREEZE |
| G1 | Live Reality Plane × Supabase Sink × Freshness Contract | ACTIVE NEXT BATTLE |
| G2 | Invest Domain Gateway | NOT_STARTED |
| G3 | Gold Decision Cockpit | NOT_STARTED |
| G4 | Trade Decision Compiler | NOT_STARTED |
| G5 | Shadow Runtime | NOT_STARTED |
| G6 | Learning Recall | NOT_STARTED |
| G7 | Internal Alpha | NOT_STARTED |
| G8 | Seed Alpha | NOT_STARTED |

## Cross-Repo Work

- Program / domain law: https://github.com/moonstachain/yuanli-invest/issues/107
- G0 Draft PR: https://github.com/moonstachain/yuanli-invest/pull/108
- G1 runtime: https://github.com/moonstachain/yuanli-invest-runtime/issues/28
- G2/G3 product: https://github.com/yuanli-life/yuanli-os/issues/34
- Human Project Cockpit: https://app.notion.com/p/3e38e1aaace4813eb8d2c4e4495a710e?pvs=204

## Next Legal Action

`YIOS-TG1-G1｜Live Reality Plane × Supabase Sink × Freshness Contract`

Acceptance must prove one same-day Reality chain:

```text
Wind
→ GOLD2 G6 receipt
→ normalized PIT
→ idempotent Supabase write
→ GOLD Research State
→ Product readback
```

source / value / known_as_of / version / authority must reconcile.

## Retrieval Contract

New session / new AI should restore in this order:

1. This `YIOS-TG1-CURRENT.md`
2. Master Issue #107
3. Notion `YIOS-TG1｜Trade Guidance Product｜Project Cockpit`
4. Runtime issue #28 and Product issue #34
5. Only then query Supabase / M4 receipts for current Reality

**GitHub Truth First → Runtime Reality on demand → Notion Human Projection.**
