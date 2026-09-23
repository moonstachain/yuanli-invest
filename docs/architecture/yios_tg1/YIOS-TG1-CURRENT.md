# YIOS-TG1｜CURRENT

**Program:** Yuanli Investment OS · Trade Guidance Product  
**Status:** `G1_CORE_PASS / G1R_FORWARD_G6_SINK_PASS / G7_NOT_PROVIDED / LAUNCHD_ORIGIN_UNVERIFIED / G2A0_ENGINEERING_READY / SHADOW_ONLY`  
**Known As Of:** 2026-09-23  
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

- GOLD2 G6/G7 由 M4 每日 08:10 调度。
- 2026-09-22 G6 = `LIVE_SHADOW_RECEIPT`；G7 = `LEARNING_CANDIDATE_ONLY`。
- 2026-09-23 Runtime 收到新的 G6 `LIVE_SHADOW_RECEIPT`：generated_at = `08:10:09 Asia/Taipei`，known_as_of 从 `2026-09-21` 前进到 `2026-09-22`。
- 2026-09-23 Supabase 只出现 `1 ingest / 3 PIT observations / 1 health / 1 research state`，无第二个独立样本；Health=`OK`，freshness=`1`。
- 2026-09-23 新 canonical state：`STATE-GOLD-LIVE-d5e865812ca47895ff8b`；Research State 仍为 `WATCH`。
- 2026-09-22 → 2026-09-23：Gold `4324.25 → 4329.55`（+0.1226%）；DXY `100.4242 → 100.5409`（+0.1162%）；US long real yield `3.00% → 3.02%`（+2 bp）。
- Authority 未升级：capital / sizing / execution / Broker / VeighNa / Canon promotion 均为 false。
- G1 Core Reality Sink 已实证：M4 persisted receipt → Supabase ingest → 3 PIT observations → Data Health → GOLD Research State → Product State readback。
- Provider failure 已实证：`PROVIDER_FAIL_CLOSED → DEGRADED / 0 observation / 0 new state`。
- Authority firewall 已实证：资本法权升级被 DB 拒绝。
- Machine auth 已收窄为单用途 scope：`YIOS_TG1_G1_GOLD2_INGEST_ONLY`；M4 不持有 Supabase service-role。
- 1Password dedicated machine vault 已建立；Machine Ingest Token Canon 已生成。
- macOS Keychain runtime projection 与 1Password Canon fingerprint 一致。
- Supabase Edge Gateway `yios-tg1-g1-ingest` 已部署；缺/错 token 均返回 401 `MACHINE_AUTH_DENIED`。
- 完整 `Keychain → wrapper → machine client → Edge → G1 RPC → Product State` activation smoke = `MACHINE_REALITY_SINK_PASS`。
- Machine launchd 已切换：`RunAtLoad=false`，08:10 调度；plist 不含 secret。
- Activation smoke 暴露并修复 State identity 幂等缺陷；2026-09-22 canonical state = `STATE-GOLD-LIVE-b7d615240fe1d80634b0`。
- Runtime PR #29 merged：`4d77257fb583dfe89a0a115d093ac81bc88fb5a2`。
- GOLD2 machine hook PR #109 merged：`e6e0c2475fe835c2c98edc509f32f615a464d67f`。
- Scheduled-only activation PR #110 merged：`caf5926042eb4c7489232205fbdf14a814984edd`。
- Executable-bit PR #111 merged：`705dbedf8866453f12d42dde58dbd95dbc032ee7`。
- State-idempotency PR #31 merged：`7a8d3fdad2fe669b3ad9c117d8a09e0dfe1678a7`。

### Open Gaps

- **G1R 尚未 Fully Settled**：2026-09-23 的 G6 forward Reality Sink 已通过，但对应 ingest 的 `learning = null`、Data Health `learning_status = NOT_PROVIDED`，且没有新的 runtime learning delta；G7 forward evidence 不成立。
- **Natural launchd origin 未独立验真**：Runtime 生成时间与 08:10 调度吻合，但本轮未能读取本机 launchd/stdout 证据，因此不能证明不存在 manual kickstart。
- 不能用 2026-09-23 同日手工 replay 冒充 forward evidence；必须等待未来独立自然日恢复 G7 + launchd-origin proof。
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
| G1R | Machine Gateway × Auto-Sink | FORWARD G6 SINK PASS / G7 NOT PROVIDED / LAUNCHD ORIGIN UNVERIFIED / NOT FULLY SETTLED |
| G2 | Invest Domain Gateway | A0 ENGINEERING READY / ACTIVATION BLOCKED ON G1R FULL SETTLEMENT |
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
- G1R 2026-09-23 evidence: https://github.com/moonstachain/yuanli-invest-runtime/blob/main/evidence/yios-tg1-g1r/g1r_forward_verification.2026-09-23.json
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

`YIOS-TG1-G1R｜Recover G7 Forward Evidence × Natural Launchd Origin Proof`

2026-09-23 已证明第二自然日 G6 Reality 本身前进并且幂等落库，但尚不足以 settlement G1R。

下一次合法验收必须来自**未来独立自然日**，不能用 2026-09-23 同日 replay 替代：

1. 读取 launchd/stdout 原始证据，证明 08:10 是自然 scheduler event、无 manual kickstart；
2. G6 生成新的独立 `LIVE_SHADOW_RECEIPT`；
3. G7 必须生成并随同 sink 携带新的 `LEARNING_CANDIDATE_ONLY`；
4. machine client 自动通过 scoped Edge Gateway；
5. Supabase 只写一个 governed ingest set；
6. 新 ingest 的 Data Health `learning_status` 不再是 `NOT_PROVIDED`；
7. freshness / known_as_of / values / state identity 对上一自然日形成可解释 delta；
8. 无 duplicate sample、无法权升级；
9. 全部满足后才 `G1R = FULLY_SETTLED`，随后进入已准备好的 `YIOS-TG1-G2A1`。

G2A0 Runtime Snapshot PR #32 与 Yuanli OS Gateway PR #40 继续保持 `ENGINEERING_READY / DRAFT / NOT_ACTIVATED`。

## Retrieval Contract

1. 本 `YIOS-TG1-CURRENT.md`
2. Master Issue #107
3. Notion Project Cockpit
4. Runtime #28 / #30 and Product #34
5. 需要实时状态时再查 Supabase / M4 receipts

**GitHub Truth First → Runtime Reality on demand → Notion Human Projection.**
