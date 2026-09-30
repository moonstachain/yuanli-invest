# GOLD2 账户协调器 V2：已实现接口与验收边界

日期：2026-09-26。状态：源码、数据库迁移与离线验证完成；远端部署由主执行任务另行记录。本文件不证明真实 CTP 连接、工程成交或生产并发验收。账户绑定没有预置，交易准入默认关闭。

## 本轮解决的问题

V1 的 command_id 永久消费只能防止同一命令重复提交，无法拦住同账户两个不同命令。V2 将占位扩展为 `(environment, account_id)`：每个变更先锁账户行，核对单调 version，再读取已锚定账本与独立 reader 证据。同一账户只有一个 pending claim；不同账户有各自状态；command_id 仍跨账户永久唯一。

账户 phase 为 FLAT、CLAIMED、SUBMIT_ATTEMPTED、HELD、FROZEN。OPEN 成交且对账完成后清 pending，保留一手仓位及其 OPEN claim origin；CLOSE 必须绑定这个 origin 和同一个真实 AU 合约。FROZEN 不允许绕锁提交保护平仓；未决入场必须先有明确终态。这一限制须在正式运行时的风险说明中保留，不能宣称已经支持所有失联场景下的保护退出。

V1 Edge claim 永久拒绝；迁移还撤销 V1 SQL claim 的 service_role EXECUTE 和旧 order_claims INSERT。不存在 TTL、过期自动释放、重启自动重发或以空 GetOrders 推断无旧委托的路径。

## Wire contract

请求 HMAC envelope 沿用 `GOLD2-PAPER-V1`，签名涵盖 POST、路径、时间与原始 body SHA256；三个角色用三个不同密钥。`signal`、`runtime`、`broker_reader` 不共享权限。传输请求和 canonical JSON 只接受安全整数；金额用分。

runtime 六个操作共同字段为：

```text
op, environment="SIMNOW_FIRST_NORMAL", account_id, robot_id,
source_sha256 (已准入 runtime 源码 SHA256)
```

所有 mutation 再含 `expected_version`、`ledger_root_hash`、`ledger_sequence`。其余字段如下：

| op | 其余必填字段 | 对应账本末事件 kind |
|---|---|---|
| claim_order_v2 | command_id, contract_hash, action, instrument, position_origin_claim_id, broker_evidence_id | OrderClaimRequested |
| read_account_state_v2 | 无 | 无 |
| read_claim_v2 | command_id | 无 |
| record_submit_attempt_v2 | claim_id | OrderSubmitAttempted |
| record_terminal_v2 | claim_id, broker_evidence_id | OrderTerminalReconciled |
| freeze_account_v2 | claim_id（可 null）, reason_code | AccountFrozen |

`action` 只允许 OPEN_LONG/CLOSE_LONG，`instrument` 只允许具体 `auYYMM`。OPEN 的 origin 必须 null；CLOSE 的 origin 必须是当前已确认一手仓位的 OPEN claim。所有 mutation 的账本末事件必须是最新已锚定 head，且其 command、kind、data 引用、sequence、root 一致；旧 root、过旧/未来事件均不能变更账户状态。

账本末事件 data 至少包含：

```text
claim: source_sha256, contract_hash, action, instrument,
       position_origin_claim_id, broker_evidence_id
submit: source_sha256, claim_id
terminal: source_sha256, claim_id, broker_evidence_id
freeze: source_sha256, claim_id, reason_code
```

正常账户返回共同字段：

```text
source="external_account_coordinator_v2", status, claimed,
environment, account_id, robot_id, source_sha256, version, phase,
pending_claim_id, claim_id, command_id, position_quantity,
position_origin_claim_id, ledger_root_hash, ledger_sequence,
freeze_reason, updated_at
```

首次 read 的 version/sequence 为 0，root 为裸 64 个 `0`，FLAT、qty=0、origin/pending/claim/command=null。它是只读初始投影，不创建 claim 或许可。其他非空 hash 均是 `sha256:`＋64 位小写十六进制。

只有一次 fresh `CLAIMED` 可返回 `claimed:true`；它必须同时独立读回相同账户状态。已消费命令返回 ALREADY_CLAIMED，任何 read 都返回 `claimed:false`。read_claim 额外含 contract_hash/action/instrument/claimed_at，以便恢复时核对永久 claim。

success statuses：ACCOUNT_READ、CLAIM_READ、CLAIMED、SUBMIT_RECORDED、TERMINAL_RECORDED、FROZEN。409 明确拒绝 statuses：ALREADY_CLAIMED、CONFLICT、LEGACY_COMMAND_CONSUMED、VERSION_CONFLICT、ACCOUNT_BUSY、ACCOUNT_FROZEN、OPEN_POSITION_DENIED、CLOSE_ORIGIN_DENIED、CLOSE_INSTRUMENT_DENIED、SUBMIT_STATE_DENIED、TERMINAL_STATE_DENIED、FREEZE_CLAIM_DENIED、CLAIM_NOT_FOUND。SQL/RPC/读回不明统一 `503 UNKNOWN_NO_RETRY`；不能把它当作可再次提交。

## 独立 broker reader 证据

runtime 不得提交任意 MATCHED 字典以解除占位。独立配置的 broker_reader 使用另一密钥和 reader 源码身份，提交以下 exact envelope：

```text
op="ingest_broker_evidence_v2", environment, account_id, robot_id,
source_sha256 (reader 源码), evidence_id, kind="PRE_CLAIM"|"TERMINAL",
observed_at, raw_sha256, facts_sha256, facts
```

facts exact keys：command_id、claim_id、instrument、action、order_id、order_status、filled_quantity、position_quantity、pending_order_count、reconciliation、raw_account_sha256、raw_orders_sha256、raw_trades_sha256、raw_positions_sha256。

reconciliation 只有 broker/execution/ledger/expected 四方，各方只有 cash_cents、available_cents、frozen_margin_cents、position_quantity、filled_quantity。三项金额分别最大差不超过一分；仓位、成交量精确相同，并与 facts 顶层一致。qty 只能 0/1，pending_order_count 必须 0。

PRE_CLAIM 必须 claim/order=null、status=NONE、filled=0，仓位与当前服务器状态相同。TERMINAL 必须有明确 claim 与 order 身份，FILLED=1 手，REJECTED/CANCELED=0 手；证据时间不得早于持久化 submit-attempt。拒单/撤单保持原仓位与 origin，成交量不足、未知或错误前后仓位不能释放。

所有证据不可变，时间必须在服务器之前且不超过 30 秒。Edge 对 facts 和四个原文 hash 汇总做 canonical SHA256；内部 RPC 同时核对 canonical 材料 JSON、SHA256 和存储事实一致。ingest 成功后再次独立 readback。

原文 hash 的语义为真实 native CTP 返回完整 decoded JSON 的 canonical hash，并非 transport wire 字节。order_id 必须来自已审核 reader 的真实平台订单与 CTP OrderSysID/OrderRef/trading-day 映射。服务无法自己联系 CTP：独立 HMAC 只证明“绑定 reader 上报了这些事实”，不能替代真实适配器、账户身份及订单映射验收。

reader 写回执为 `source=bound_broker_reader_evidence_v2,status=EVIDENCE_RECORDED,evidence_id,facts_sha256,raw_sha256,received_at`。写结果未知后只能 `read_broker_evidence_v2`：请求共同 reader 字段加 evidence_id，返回 EVIDENCE_READ、完整不可变证据及 verified_at；无记录返回 404 EVIDENCE_NOT_FOUND。历史读允许超过 30 秒，但不会刷新 observed_at 或授予交易/释放权限。

## 部署约束

新私有表：runtime_bindings、account_execution_state、command_claims_v2、broker_evidence_v2、claim_events_v2。全部 RLS，无 anon/authenticated table/RPC 权限。函数均 SECURITY INVOKER、空 search_path。事实、claim、事件不可 UPDATE/DELETE。管理员配置唯一 account/robot/runtime source/reader source；service_role 只能 SELECT runtime_bindings，不能自己准入新账户或 reader。

Edge 使用服务器内置 `SUPABASE_SECRET_KEYS.default`，或旧 `SUPABASE_SERVICE_ROLE_KEY`；显式 `GOLD2_DB_SECRET_KEY` 可覆盖。数据库 secret 始终留在服务器。`GOLD2_PAPER_ENABLED` 与 `GOLD2_CLAIM_ENABLED` 均默认 false。只有三个独立 HMAC、服务器项目身份、真实账户/机器人/两份源码绑定与 active DB binding 全部合格才可工作；实际部署仍应在验收前保持关闭。

## 已运行验证

- `node --test tests/test_gold2_paper_control.mjs`：50 项通过。覆盖角色/绑定、fresh/readback、重复/未知写、reader 权限、原文 hash、四方金额/保证金/数量漂移、历史读、拒绝 caller MATCHED、风险方向及 stale version。
- PGlite 0.3.16（实际 PostgreSQL WASM）执行两份迁移编译通过；`tests/gold2_account_coordinator_sql_probe_v2.sql`：48 项通过，全部 DIAGNOSTIC fixture 随事务 rollback。验证 OPEN/HELD/CLOSE/FLAT、拒/撤零成交保持前仓、无终态不释放、全局 command、不同账户、冻结、四方校验、权限与 append-only。
- 五张新表全部 RLS=true，anon/authenticated SELECT=false；service_role 不可改变 binding，旧 V1 claim execute 已撤销。

Node 并发测试使用原子 RPC 的 reference oracle 检验 Edge 的许可返回语义；PGlite probe 是单连接真实 SQL 行为验证。它们不等于真实多连接竞争/故障注入，也不是 SimNow 运行证据。启用前仍须真实 PostgreSQL 两连接竞争、CTP reader、信任密钥、账户身份、完整运行时接线、具体工程测试合同与终态恢复验收。

源码：`supabase/functions/gold2-paper-control/{core.mjs,service.mjs,index.ts}`；迁移 `supabase/migrations/20260926081247_gold2_account_coordinator_v2.sql` 由实际 Supabase CLI `migration new` 生成。CLI npx shim 未提供可执行入口，复用已观察到的 CLI 2.117.0 原生 binary 完成创建，没有手造 migration filename。

官方依据：[Supabase 函数权限](https://supabase.com/docs/guides/database/functions)、[Edge 环境变量与内置 secret](https://supabase.com/docs/guides/functions/secrets)、[2026-09-25 PostgreSQL 更新](https://supabase.com/changelog/postgres-15-19-17-11-breaking-changes)、[PostgreSQL SHA256](https://www.postgresql.org/docs/current/functions-binarystring.html)。本迁移不使用 ltree/btree_gist、自定义 operator 或 pgcrypto 旧加密算法。
