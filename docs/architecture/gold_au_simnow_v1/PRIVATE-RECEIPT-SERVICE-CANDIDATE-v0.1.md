# GOLD2 私有收讫与一次性认领服务候选 v0.1

2026-09-26 状态更新：数据库迁移和 Edge Function 已实际部署，但服务保持 `SERVICE_DISABLED`，订单认领硬关闭，未配置业务 HMAC 密钥或开通 `PaperGrant`。部署、权限与回滚测试证据见 [实际部署记录](../../operations/GOLD2-PRIVATE-RECEIPT-DEPLOYMENT-20260926.md)。以下是原候选设计；任何返回值都不是订单或成交回执。

原冻结状态（部署前）：`SOURCE_CANDIDATE_DISABLED_NOT_DEPLOYED`。当时尚未应用 migration、部署 Edge Function、配置密钥或接入优宽、SimNow。

## 边界与复用

仓内 [YMQ4-DP1-A 研究证据管道](../ymq4/YMQ4-DP1-A-REALITY-PROOF-v0.1.md)曾证明远端 Supabase 私有存储、RPC 与读回可用，但其 `evidence.source_snapshots` 允许更新取得时间，不可作为交易事件账。本候选另建 `gold2_paper` 私有 schema；原研究表、密钥和业务规则不迁移。已有本地 `LocalSignalRegistry`、`PaperLedger` 和 `DurableOutbox` 继续分别负责本地登记、事件投影、CommandRobot 网络尝试；它们本身不能证明远端收讫、跨主机订单认领或 SimNow 成交。

代码：

- `supabase/migrations/20260925072235_gold2_paper_private_receipts.sql`：四张私有表，RLS 开启且无匿名/普通用户策略，服务角色独占六个 RPC；信号在数据库服务器的 08:30 分钟内收讫；事件账逐流行锁、全前缀逐项比对、仅追加；订单 `command_id` 主键永久单次认领。
- `supabase/functions/gold2-paper-control/{index.ts,service.mjs,core.mjs}`：默认无开关/密钥时返回 `SERVICE_DISABLED`；请求须经 30 秒内的 HMAC-SHA256 验签，信号端和运行端各有单独密钥与操作范围。它用服务端 Supabase secret key 调用 RPC，写后再读回；超时、解析失败或读回不符返回 `UNKNOWN_NO_RETRY`。**本版 Edge 入口硬编码 `claimEnabled: false`**，即使配置服务开关也不接受订单认领。
- `supabase/config.toml`：只针对该函数关闭平台 JWT 前置检查。**函数内 HMAC 是必需的独立认证层**；没有开启开关和全部服务器配置时没有可用入口。

与现有接口的预期接线如下。这里的“可衔接”指数据形状，**不是已有可调用的生产回调**；迁移和 Edge 均未部署，所以目前真实可用的远端回调数量为零。

| 现有调用口 | 本候选可提供的远端事实 | 仍需实现的适配 |
| --- | --- | --- |
| `LocalSignalRegistry.gateway_adapter(anchor_verifier)` | `anchor_signal` 写入后由 `read_signal` 返回独立收讫时间、原记录/根哈希及稳定 proof | 本地 HMAC 客户端、同分钟调用/再次读回、超时只读查询；其余登记流程仍在本地。 |
| `YouQuantBridge.ledger_anchor(events, root_hash)` | `append_ledger` 的 `source=external_append_only_ledger`、`accepted=true` 和精确 `root_hash`，且 Edge 已重新读回远端账头 | 用**安全注入的账号/机器人身份**封装云端 HMAC 客户端；不可从订单字符串自报身份。 |
| `YouQuantBridge.atomic_claim(command_id, contract_hash, account_id, now)` | SQL 和隔离测试具备永久唯一认领的候选形状；**Edge 入口目前固定关闭 `claim_order`，真实回调不可用** | 先设计账户级待决互斥与释放协议；云端回调须固定已核实的 `robot_id`，UNKNOWN 时只调用 `read_claim`，绝不自动再次下单。 |

本服务**不产生** `account_attestation`、`current_margin`、`current_round_trip_fee_upper`、`strategy_equity_mark`、`daily_close_history`、`terminal_truth` 或 `reconciliation_probe`；这些必须由实际优宽/CTP/独立对账来源实现。它也不会构造或注入 `GOLD2_SIMNOW_RUNTIME`，不会打开 `PaperGrant`。账户准备仍要在官方渠道取得 SimNow 正常环境账号、在优宽接入 CTP 并对 `GetPlatformList/GetRobotDetail`、交易账号/订单/持仓进行真实只读核验；HMAC 密钥只在可验证的非源码秘密注入路径就绪后才能分发。

HMAC 签名正文为 UTF-8 文本：`GOLD2-PAPER-V1\nPOST\n<实际 URL pathname>\n<x-gold2-timestamp>\n<SHA256(原始请求体) 小写 hex>`。请求头 `x-gold2-role` 为 `signal` 或 `runtime`，`x-gold2-signature` 为 `sha256=<HMAC hex>`，时间戳必须带时区且距离函数时钟不超过 30 秒。JSON 请求仅接受明确操作及固定字段；`signal` 仅可 `anchor_signal/read_signal`，`runtime` 的协议候选有 `append_ledger/read_ledger/claim_order/read_claim`，其中 `claim_order` 在入口额外硬阻断。事件哈希和登记哈希按仓内 Python 的 UTF-8、排序键、无空格 JSON 口径重算；为避免 JavaScript/Python 浮点重序列化差异，服务拒绝非整数 JSON 数值。现有合成的开仓→四方结算→保护平仓 **11 个事件**跨 Python/Node 哈希回放通过，且未含浮点；真实回调尚不存在，无法保证其产生相同类型。若实际事件触发浮点限制，应停机并版本化修订，不能跳过哈希校验。

新信号只有在数据库 `clock_timestamp()` 落在其决策日北京时间 **08:30:00–08:30:59** 且不早于本地登记时间时才可入账；数据库时间才是远端证据。`read_signal` 从该表重取完整登记对象，验证原文哈希后给出稳定的 `proof_sha256` 与新的 `verified_at`。超时后应**只读查询**原 `registry_id/record_id`，不可重新生成或回填登记时间。隔离的 SQL 认领逻辑第一次请求返回 `claimed=true`；同一 `command_id` 再次请求无论合同是否相同都不能授权第二次提交。这个逻辑目前不可由 Edge 客户调用。未来打开之前，超时后只能 `read_claim`，订单状态仍须向 SimNow/OMS 单独核对，不能因为认领存在就推断已下单。

事件追加请求提供完整前缀和根哈希。Edge 逐事件重算 SHA-256，数据库在同账户/机器人行锁下将既有每项与新请求逐项比对，只追加后缀并返回数据库时间。既有前缀改变、旧根重放或缩短都会拒绝；写后另查账头。如果写入已发生但读回超时，返回 `UNKNOWN_NO_RETRY`，运行端必须停新单、核对远端根与交易端状态。代码里不做自动重发。

## 密钥与启动条件

本候选没有生成或保存任何密钥。将来若经审查部署，Edge 端需要服务器私密配置 `GOLD2_PAPER_ENABLED=true`、`GOLD2_SIGNAL_HMAC_KEY`、`GOLD2_RUNTIME_HMAC_KEY`、`GOLD2_DB_SECRET_KEY`（现代 `sb_secret_`）、`GOLD2_SUPABASE_PROJECT_REF`，以及平台提供的 `SUPABASE_URL`。两个 HMAC 密钥必须不同且至少 32 字节；数据库 secret **只在 Edge 端**，不得出现在优宽编辑器、浏览器、Git、对话或前端。优宽/本地客户各自只能持有其操作范围对应的 HMAC 密钥，并需有可信的秘密注入方式；该方式在优宽云托管上尚未验证，不能通过把密钥硬编码进单文件策略来绕过。正式配置前服务默认关闭。

当前 SQL 中 `public` RPC 只授权 `service_role`；`gold2_paper` 表位于非公开 schema、RLS 开启且无 `anon`/`authenticated` 授权或策略。Edge 使用 server-only secret 调用 RPC，不把该 key 发给 HMAC 客户。数据库触发器阻止应用角色更新/删除信号、事件和认领行。项目所有者或数据库管理员仍能修改数据库：这是**应用级逻辑不可改写**，不是物理 WORM 或独立第三方时间戳；正式采用前还要审查管理员权限、备份、不可篡改导出/外部见证及事故恢复方案。

## 可复核的本地验证

```bash
node --test tests/test_gold2_paper_control.mjs
npm install --prefix /tmp/gold2-paper-pglite --no-save @electric-sql/pglite@0.5.8
GOLD2_PGLITE_MODULE=/tmp/gold2-paper-pglite/node_modules/@electric-sql/pglite/dist/index.js node tests/gold2_paper_sql_probe.mjs
```

2026-09-25 本地结果：Node 协议 8/8；隔离内存 PostgreSQL migration 与一组事务探针通过，覆盖重复认领、不同合同冲突、账本前缀分叉、过期信号拒绝、匿名角色拒绝与历史行更新拒绝。此验证没有连接现有 Supabase 项目；尚未运行 Supabase 数据库 Advisor、Edge 宿主、平台密钥注入、生产并发/故障注入或远程 08:30 截止实测。

## 未解决的交易准入条件

1. **硬阻断：**SQL 只按 `command_id` 永久去重，尚未提供同一账户下两个不同有效命令的并发串行化；直接加永久账户唯一键还会阻断已持仓的保护平仓。现有运行时没有账户级待决认领、经真实终态/四方对账后释放的远程回调。为避免错误启用，Edge 入口将 `claimEnabled` 固定为 `false`；本版**不得**用环境变量、复制代码或改数据库绕开。须另行版本化实现账户级互斥和保护性退出协议，并通过并发与断线演练，才可审议启用订单认领。
2. `YouQuantBridge` 的真实宿主 bootstrap、独立账户身份与终态读回、费用/保证金、权益、日线、四方对账回调仍未实现。本服务不能提供或伪造这些 Broker/OMS 事实。
3. US 区远端延迟、冷启动、网络断连和时钟偏差可能使 08:30 登记过期；结果必须记 `SKIPPED/UNKNOWN`，不得补录。服务的 2.1 MB 请求上限与全前缀设计须在 30 日事件规模下验证，超限时停机并另定版本。
4. 应以专用 Supabase 项目或至少专门受控的密钥/权限边界复核研究与交易隔离。已有研究项目真实状态、迁移冲突、Edge 配置、RLS/数据库 Advisor 均需部署前独立核对。

官方依据：[Edge Function 认证](https://supabase.com/docs/guides/functions/auth)、[请求头与 `verify_jwt`](https://supabase.com/docs/guides/functions/auth-headers)、[Edge secrets](https://supabase.com/docs/guides/functions/secrets)、[数据库函数权限](https://supabase.com/docs/guides/database/functions)、[RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)。已核对 [Supabase changelog](https://supabase.com/changelog.md)：2026 年 Data API 自动暴露变更不应成为开放这些私有表的理由；本候选只通过授权 RPC 访问。
