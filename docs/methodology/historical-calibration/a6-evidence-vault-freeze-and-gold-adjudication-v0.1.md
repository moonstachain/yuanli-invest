---
title: Force Triangle Evidence Vault Freeze & Gold Adjudication
version: 0.1.0
status: started_waiting_external_vault_capture_and_reviewer
portfolio: A9
accepted_a5_commit: f37f1127d49981d6ece81b6000d494d87a1214f1
---

# A6｜Evidence Vault Freeze & Gold Adjudication v0.1

## 0. Human Gate 已通过

A5 Human Review 决策：`ACCEPT_CANDIDATE_RECONSTRUCTION`。

A5 只被接受为 point-in-time Candidate Reconstruction；不代表历史 Gold Outcome 已成立，也不代表 P/N/X 已升级为 approved Canon。

A6 的任务是把 A5 的“来源集合冻结”推进为真正可审计的 Evidence：

`Candidate source → immutable capture → SHA-256 → locator → SourceRecord → Evidence → independent adjudication → Canon P/N/X snapshot candidate`

## 1. A6 唯一目标

把 PC-1995、Mobile-2008、AI-2023 三个案例中的 T0 合格来源变成**可重放、可验哈希、可定位原文、可被独立 Reviewer 逐条接受或拒绝**的历史证据包。

A6 不负责：

- 接受任何 Outcome；
- 根据后续收益修改 P/N/X；
- 修改 RSI FROZEN；
- 切换 A9 operational canon；
- 产生交易、仓位、目标价或收益承诺。

## 2. Evidence Vault 真冻结标准

一个来源只有同时满足以下条件，才能从 `eligible_pending_vault_capture` 进入 `captured_pending_adjudication`：

1. 原始网页/PDF/文件已保存到本机或 NAS Evidence Vault；
2. 生成稳定 SHA-256；
3. 保存 capture timestamp；
4. 保存原始 URL / publisher / published_at；
5. 保存 locator（页码、段落、表格、section 或可复现文本锚点）；
6. 保存 T0 eligibility；
7. 同日来源必须完成精确时间戳裁决，不能自动升级；
8. GitHub 只保存 locator/hash/metadata，不保存受限原文附件。

## 3. A6 两个独立门

### Gate A｜Capture Integrity

验证的是“材料是不是同一份材料”：

- snapshot 可读取；
- SHA-256 可复算；
- URL 与 published_at 可追溯；
- locator 能定位到支持/反驳的原文；
- 无 post-T0 信息泄漏。

### Gate B｜Evidence Adjudication

验证的是“材料有没有资格支持这个 claim”。Reviewer 对每条 claim 只能给：

- `accept_support`
- `accept_counterevidence`
- `reject_insufficient`
- `reject_post_t0`
- `reject_wrong_locator`
- `needs_timestamp_review`

Capture 成功不等于 Evidence 被接受。

## 4. 第一批 Vault Capture 顺序

优先级按“原始来源 > 二手来源；跨 P/N/X 覆盖 > 单点叙事；T0 明确 > 同日时间不明”排序。

### P0｜Primary / T0 明确

- `FTSRC-MOB-001` Apple — iPhone 2.0 Software Beta
- `FTSRC-MOB-002` Apple — iPhone SDK Downloads Top 100,000
- `FTSRC-MOB-003` SEC — Apple 2008 Q2 Form 10-Q
- `FTSRC-MOB-004` Apple — iPhone 3G announcement
- `FTSRC-AI-001` OpenAI — Introducing ChatGPT
- `FTSRC-AI-002` SEC — NVIDIA 2022 Q3 Form 10-Q
- `FTSRC-AI-003` Microsoft — OpenAI partnership extension

### P1｜Secondary / T0 明确

- `FTSRC-PC-001` Washington Post — Netscape IPO pre-analysis

### P2｜Same-day timestamp adjudication

- `FTSRC-PC-002` Time — Netscape with a Bullet
- `FTSRC-MOB-005` Apple — iPhone 3G on Sale Tomorrow

### 永久排除于 T0 Evidence

- `FTSRC-AI-004`：2023-02-02 的 ChatGPT 100m 用户报道，晚于 AI T0 `2023-02-01`；
- 所有 2026 derived research：仅 discovery，不得成为历史 T0 Evidence。

## 5. Reviewer 独立性

Evidence Reviewer 必须与 A5 candidate reconstruction 的作者角色分离。Reviewer 的任务不是“证明黄金三角正确”，而是主动寻找：

- hindsight leakage；
- claim 超出原文；
- publisher/source independence 假象；
- same-day 时间不确定；
- P/N/X 偷换；
- 只收赢家证据、不收反证。

在 Reviewer 未具名前，A6 状态必须保持 fail-closed。

## 6. 三个案例的 Gold 晋级门

每个案例必须独立满足：

1. 至少一组 P 证据 accepted；
2. 至少一组 N 证据 accepted；
3. 至少一组 X/right-tail 证据 accepted；
4. 至少一组 X/left-tail 或 counterevidence accepted；
5. Fundamental Gate 有 accepted evidence；
6. Survival Gate 有 accepted evidence；
7. 所有用到的 source 都通过 T0 eligibility；
8. `lookahead_check = passed`；
9. Reviewer 明确签署 adjudication receipt；
10. Outcome 仍保持 locked，直到独立后续阶段。

若任何一项不足，允许维持 `unknown` / `partial`，不得为了凑齐 Gold 强行补分。

## 7. A6 退出条件

A6 只有在以下全部完成后才能结束：

- P0/P1/P2 capture queue 全部进入终态；
- 每个 captured source 有 SHA-256 + locator；
- same-day 来源有明确裁决；
- 独立 Evidence Reviewer 已具名并完成逐条 adjudication；
- 三个案例生成可复算 SourceRecord/Evidence 集；
- P/N/X snapshot candidate 只消费 accepted Evidence；
- CI 可验证引用、hash receipt 与 no-lookahead；
- Human Review 接受 A6 Gold Adjudication 结果。

在此之前，A6 只是 `started_waiting_external_vault_capture_and_reviewer`。