# YIOS-TG1｜CURRENT

**Program:** Yuanli Investment OS · Trade Guidance Product  
**Status:** `G1_CORE_REALITY_SINK_PROOF_PASS / SHADOW_ONLY / MACHINE_SECRET_PROJECTION_PENDING`  
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

前台 Action State：`WAIT / PROBE / HOLD / REDUCE / HEDGE`

硬边界：

- `Research != Capital != Execution`
- `UNKNOWN = DENY`
- `WAIT / DENY` 是合法完成态
- Research pass 不自动产生 sizing 或 execution authority

## Current Reality

### Proven

- GOLD2 G6 Live Shadow 在 M4 每日 08:10 运行。
- 2026-09-22 G6 = `LIVE_SHADOW_RECEIPT`；G7 = `LEARNING_CANDIDATE_ONLY`。
- Real 2026-09-22 receipt 已完成：M4 → Supabase ingest → 3 PIT observations → Data Health → GOLD Research State → Product State readback。
- Idempotency PASS：重复写同一 receipt 不产生第二组事实。
- Failure path PASS：真实 `PROVIDER_FAIL_CLOSED` → `DEGRADED`、0 observation、0 new state。
- Authority firewall PASS：`capital_authorized=true` 被数据库拒绝。
- RPC ACL：anon/authenticated 无读写权；service_role only。
- Runtime PR #29 CI = PASS。

### Open Gaps

- unattended M4 scheduler 尚未绑定 machine-safe Supabase secret projection；不能长期依赖个人解锁的 1Password session。
- exact `released_at / available_at / vintage_id` 尚无 provider authority，继续保持 NULL；当前 temporal grade = `DATE_LEVEL_ONLY__RELEASE_TIME_UNKNOWN`。
- central-bank demand + stress proxy 尚未成为 P0 live evidence slots。
- `TradeDecisionCandidate` 尚未成为 runtime object。
- Invest Domain Gateway / Gold Decision Cockpit 尚未形成。
- Shadow Settlement → LearningDelta → Pre-Action Recall 尚未形成产品闭环。

## Gates

| Gate | Battle | Current |
|---|---|---|
| G0 | Product Constitution × Architecture Freeze | DRAFT PR #108 |
| G1 | Live Reality Plane × Supabase Sink × Freshness Contract | CORE PROOF PASS / AUTO-SINK PENDING MACHINE SECRET |
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
- G1 Runtime issue: https://github.com/moonstachain/yuanli-invest-runtime/issues/28
- G1 Runtime Draft PR: https://github.com/moonstachain/yuanli-invest-runtime/pull/29
- G2/G3 product: https://github.com/yuanli-life/yuanli-os/issues/34
- Human Project Cockpit: https://app.notion.com/p/3e38e1aaace4813eb8d2c4e4495a710e?pvs=204

## Next Legal Action

`YIOS-TG1-G1R｜Unattended Auto-Sink × Machine Secret Projection × Second-Day Delta`

目标：

1. 为 M4 launchd 提供 scoped machine/runtime secret projection，而不是个人 1Password unlock dependency；
2. G6/G7 每日成功或 fail-closed 后自动调用 Reality Sink；
3. 用下一独立日 receipt 验证自动写入、freshness、delta 与失败降级；
4. 未完成前不得声称 G1 fully automated production runtime。

## Retrieval Contract

1. 本 `YIOS-TG1-CURRENT.md`
2. Master Issue #107
3. Notion Project Cockpit
4. Runtime #28 / PR #29 / Product #34
5. 需要实时状态时再查 Supabase / M4 receipts

**GitHub Truth First → Runtime Reality on demand → Notion Human Projection.**
