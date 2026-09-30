# GOLD2 私有回执服务：账户互斥与终态释放的最小接口

状态：设计提案，未修改远端服务或正式运行时。当前 Edge `claimEnabled:false` 必须保持，直到账户互斥、独立终态读回和真实客户端连接都验收。

## 源码中已经存在什么、缺什么

`order_claims.command_id` 为永久唯一键，解决同一命令跨重启重复提交；两个不同 command_id 仍能同时取得 `CLAIMED`。现有 ledger 行锁只按 `(account_id, robot_id)` 串行，不能覆盖同账户不同机器人。Edge 已显式禁用 claim，原因正是缺少账户范围的 pending-order 释放／对账协议。

正式运行时已有本地终态处理：独立 SimNow order/account readback ≤30秒、明确 FILLED／REJECTED／CANCELED、实际量为0或1、四方金额／仓位匹配，然后追加 `ReconciliationMatched` 与终态事件。最后只写本地 `_G` 和外部账本 anchor，没有远端 account slot 的原子终态提交／释放回执。现在也没有给已提交但返回未知的账户级占位做跨机器人恢复查询。

## 最小数据结构

新增 `account_execution_state`，主键为 `(environment, account_id)`，不包含 robot_id。字段：单调递增 `version`、`pending_claim_id`、`owner_robot_id`、`position_quantity`（0／1）、`position_origin_claim_id`、`phase`、最新 broker evidence hash／observed_at、最新对账及 ledger 根、冻结原因、服务器更新时间。

`phase` 最少区分 `IDLE`、`CLAIMED`、`SUBMIT_ATTEMPTED`、`BROKER_PENDING`、`HELD`、`FROZEN`。持有一手与仍有未决委托是不同事实；入场成交并对账后清空 pending slot，同时保留 HELD 仓位状态。退出必须绑定持仓 origin，不能把一次已成交的开仓 claim 重新当成可提交指令。

原 `order_claims` 保留不可变、永久消费语义。追加 `claim_events` 保存每次状态变化与事实哈希；可变 head 只是其投影。所有新增表／RPC沿用无 anon/authenticated 权限、server-role-only、固定 search_path、独立信号／运行时 HMAC scope。运行时密钥还应在服务端绑定唯一环境、账户及准入机器人；不能只相信请求里的 account_id。

## 最小接口

| 操作 | 必需输入 | 原子行为与返回 |
|---|---|---|
| `claim_order_v2` | account、robot、command、ActionContract hash、action、expected account version、合格最新账户／委托证据引用、账本根 | 创建账户行并 `SELECT FOR UPDATE`；检查账户状态与唯一 command；同事务插入永久 claim、claim事件和更新 pending slot。返回 claim_id／version／fresh one-shot `claimed:true`。同命令重复只返回 `ALREADY_CLAIMED`，永不再授权提交。 |
| `read_account_state_v2` | 服务端绑定 account | 只读返回当前 version／pending／持仓与冻结状态，用于超时、重启、跨机器人核对。查询本身不解除冻结或授予提交权。 |
| `record_submit_attempt_v2` | claim_id、expected version、已持久化并被外部 anchor 读回的 `OrderSubmitAttempted` 根 | 只允许当前 owner／当前 pending claim；追加状态事件。必须在 broker API 前成功且独立读回；返回不明即停，不能重发订单。 |
| `record_terminal_v2` | claim_id／order identity、expected version、独立终态证据、四方对账材料、对应已锚定终态 ledger head | 服务器检查当前占位、命令／订单／账户／环境一致、量0／1、证据时效、四方金额及仓位匹配，并确认终态 ledger prefix。一个事务中追加 terminal／reconciliation receipt、更新账户持仓并清空 pending。随后单独 readback；未知结果只查询，不再次下单。 |
| `freeze_account_v2` | current claim／version、事件根、原因代码 | 只向更保守状态变化，保留 pending 与 evidence，拒绝新入场；不能用 freeze 接口释放占位。 |

`claim_order_v2` 首先锁账户行，之后再查永久 command 与 stream head，所有 RPC 统一锁顺序，避免跨 stream／账户反向锁造成死锁。同账户不同命令只能一个成功；不同账户不互相阻塞。

首次实现不提供“TTL 到期自动释放”。时间过期不能证明旧委托不存在，也不能阻止失联旧进程稍后触碰 broker。版本／fencing token 只对受控服务和受控客户端有效，CTP 本身不会替这个服务执行 fencing；不能把它宣传成对任意旧客户端的防重复保证。只准入一个明确账户、一版已审源码、一个机器人，确认没有其他自动交易机器人共享该账户。

## 真实客户端需补的两个回调

在现有 `YouQuantBridge` 增加账户状态／submit-attempt receipt 与 terminal receipt 回调。claim 后、持久化 before broker 的步骤使用账户 version；失败／超时马上冻结。`settle_order` 在现有独立 terminal truth 与四方对账验证后，先 anchor 终态账本，再提交远端 `record_terminal_v2`，最后 readback 当前账户状态；不能只在本地清空 pending。

终态输入必须来自实际 CTP 委托／成交／账户读取和它们的原文哈希，不能把 `GetOrders()` 空列表当作“从未下过单”，也不能把调用者标记 `MATCHED` 当作已验真。服务端如果暂不能独立检索 broker，其证据接收范围应明确是受信、绑定源码的 reader 上报；任意客户端伪造字典不能成为自动释放凭据。

`PRE_SUBMIT_DENIED_NO_BROKER_CALL` 也不能随便解锁：最小版保留冻结，待一次明确的独立核对后释放，永久 claim 不删除。已成交的 OPEN 释放 pending 后进入 HELD；CLOSE 可以取得下一次 slot。若未决入场与已确认长仓并存，先核对／取消并确认原委托终态，再安排风险退出；如果要求在这种不确定状态直接提交保护平仓，需要另外设计绑定 origin 的风险减仓通道，不能把普通账户互斥的锁绕过去。

## 验收后才能打开 claim

至少覆盖：不同机器人／不同command竞争只有一个fresh claim；同command永久重复拒绝；API超时已提交后只能readback；崩溃／重启／旧version不能释放；终态错订单、旧读回、金额漂移和未知部分成交保持冻结；OPEN成交后只能受控CLOSE；CLOSE成交回到FLAT；拒单／撤单确认0成交才清pending；无终态事实时不因时间推移自动解锁。全部依赖真实账户 reader 与真实 ledger anchor 回调，源码单测不能充作账户运行证据。

源码定位：`supabase/migrations/20260925072235_gold2_paper_private_receipts.sql` 的 claim与per-robot ledger；`supabase/functions/gold2-paper-control/index.ts` 的claim禁用；`scripts/youquant_gold_simnow_strategy.py` 的 `claim_order`、`process_command` 与 `settle_order`。
