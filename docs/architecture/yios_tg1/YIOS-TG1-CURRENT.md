# YIOS-TG1｜CURRENT

**Program:** Yuanli Investment OS · Trade Guidance Product  
**Status:** `G1_CORE_PASS / G1R_MACHINE_GATEWAY_ACTIVATED / G2A0_ENGINEERING_READY / SHADOW_ONLY / SECOND_DAY_DELTA_PENDING`  
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

- GOLD2 G6/G7 继续由 M4 每日 08:10 调度。
- 2026-09-22 G6 = `LIVE_SHADOW_RECEIPT`；G7 = `LEARNING_CANDIDATE_ONLY`。
- G1 Core Reality Sink 已实证：M4 persisted receipt → Supabase ingest → 3 PIT observations → Data Health → GOLD Research State → Product State readback。
- Provider failure 已实证：`PROVIDER_FAIL_CLOSED → DEGRADED / 0 observation / 0 new state`。
- Authority firewall 已实证：资本法权升级被 DB 拒绝。
- Machine auth 已收窄为单用途 scope：`YIOS_TG1_G1_GOLD2_INGEST_ONLY`；M4 不持有 Supabase service-role。
- 1Password dedicated machine vault 已建立；Machine Ingest Token Canon 已生成。
- macOS Keychain runtime projection 与 1Password Canon fingerprint 一致。
- Supabase Edge Gateway `yios-tg1-g1-ingest` 已部署；缺/错 token 均返回 401 `MACHINE_AUTH_DENIED`。
- 完整 `Keychain → wrapper → machine client → Edge → G1 RPC → Product State` activation smoke = `MACHINE_REALITY_SINK_PASS`。
- Machine launchd 已切换：`RunAtLoad=false`，仅下一自然 08:10 触发；plist 不含 secret。
- Activation smoke 暴露并修复 State identity 幂等缺陷；同一 ingest 的 canonical state 已收敛为唯一：
  `STATE-GOLD-LIVE-b7d615240fe1d80634b0`。
- Runtime PR #29 merged：`4d77257fb583dfe89a0a115d093ac81bc88fb5a2`。
- GOLD2 machine hook PR #109 merged：`e6e0c2475fe835c2c98edc509f32f615a464d67f`。
- Scheduled-only activation PR #110 merged：`caf5926042eb4c7489232205fbdf14a814984edd`。
- Executable-bit PR #111 merged：`705dbedf8866453f12d42dde58dbd95dbc032ee7`。
- State-idempotency PR #31 merged：`7a8d3fdad2fe669b3ad9c117d8a09e0dfe1678a7`。

### Open Gaps

- **Second-Day Delta Pending**：必须等待下一独立自然日 08:10 自动运行，不能用同日重跑冒充 forward evidence。
- exact `released_at / available_at / vintage_id` 尚无 provider authority，继续保持 NULL；当前 temporal grade = `DATE_LEVEL_ONLY__RELEASE_TIME_UNKNOWN`。
- central-bank demand + stress proxy 尚未成为 P0 live evidence slots。
- `TradeDecisionCandidate` 尚未成为 runtime object。
- G2A0 Invest Domain Gateway 工程候选已双 CI PASS，但尚未激活真实 Runtime RPC、生产 Secret 或部署；Gold Decision Cockpit 仍未形成。
- Shadow Settlement → LearningDelta → Pre-Action Recall 尚未形成产品闭环。

## Gates

| Gate | Battle | Current |
|---|---|---|
| G0 | Product Constitution × Architecture Freeze | HUMAN AUTHORIZED / READY TO MERGE |
| G1 | Live Reality Plane × Supabase Sink × Freshness Contract | CORE PROOF PASS |
| G1R | Machine Gateway × Auto-Sink | ACTIVATED / SAME-DAY SMOKE PASS / SECOND-DAY DELTA PENDING |
| G2 | Invest Domain Gateway | A0 ENGINEERING READY / ACTIVATION BLOCKED ON G1R FORWARD SETTLEMENT |
| G3 | Gold Decision Cockpit | NOT_STARTED |
| G4 | Trade Decision Compiler | NOT_STARTED |
| G5 | Shadow Runtime | NOT_STARTED |
| G6 | Learning Recall | NOT_STARTED |
| G7 | Internal Alpha | NOT_STARTED |
| G8 | Seed Alpha | NOT_STARTED |

## Cross-Repo Work

- Program / domain law: https://github.com/moonstachain/yuanli-invest/issues/107
- G0 Constitution/CURRENT: https://github.com/moonstachain/yuanli-invest/pull/108
- G1 Runtime issue: https://github.com/moonstachain/yuanli-invest-runtime/issues/28
- G1 Runtime merged PR: https://github.com/moonstachain/yuanli-invest-runtime/pull/29
- G1R machine runtime: https://github.com/moonstachain/yuanli-invest-runtime/issues/30
- G1R GOLD2 hook merged PR: https://github.com/moonstachain/yuanli-invest/pull/109
- Scheduled-only activation: https://github.com/moonstachain/yuanli-invest/pull/110
- Executable-bit closure: https://github.com/moonstachain/yuanli-invest/pull/111
- State-idempotency closure: https://github.com/moonstachain/yuanli-invest-runtime/pull/31
- G2/G3 product: https://github.com/yuanli-life/yuanli-os/issues/34
- G2A0 Runtime Snapshot Draft PR: https://github.com/moonstachain/yuanli-invest-runtime/pull/32
- G2A0 Runtime issue: https://github.com/moonstachain/yuanli-invest-runtime/issues/33
- G2A0 Yuanli OS Gateway Draft PR: https://github.com/yuanli-life/yuanli-os/pull/40
- G2A1 Activation issue: https://github.com/yuanli-life/yuanli-os/issues/41
- Human Project Cockpit: https://app.notion.com/p/3e38e1aaace4813eb8d2c4e4495a710e?pvs=204

## Next Legal Action

`YIOS-TG1-G1R｜Second Independent Natural-Day Auto-Sink × Delta Settlement`

Acceptance requires the **next natural 08:10 scheduler run**, not a same-day manual rerun:

1. launchd invokes the Keychain-native machine wrapper;
2. G6/G7 produces a new independent daily receipt;
3. machine client automatically reaches Edge Gateway;
4. Supabase writes exactly one new governed ingest set;
5. freshness / known_as_of / values / state transition are compared with 2026-09-22;
6. no duplicate sample, no authority escalation;
7. settle G1R and then activate the already-prepared G2A0 read path through `YIOS-TG1-G2A1`.

Parallel preflight already completed: G2A0 Runtime Snapshot PR #32 and Yuanli OS Gateway PR #40 are both engineering-ready with CI PASS. They remain Draft and unactivated until this forward event exists.

Until this independent forward event exists, G1R is `ACTIVATED` but not `FULLY_SETTLED` and G2 remains `PREPARED_NOT_ACTIVATED`.

## Retrieval Contract

1. 本 `YIOS-TG1-CURRENT.md`
2. Master Issue #107
3. Notion Project Cockpit
4. Runtime #28 / #30 and Product #34
5. 需要实时状态时再查 Supabase / M4 receipts

**GitHub Truth First → Runtime Reality on demand → Notion Human Projection.**
