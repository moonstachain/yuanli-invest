# GOLD2 剩余交易运行时接线与验收

审查日期：2026-09-26。当前状态是：研究与严格重算、运行时校验核心及若干基础设施已有实现；真实交易宿主 bootstrap、七个真实数据回调、账户级并发协议和安全密钥注入仍有工程工作。不能把“等待周一交易时段”写成全部工程完成。本文只读核对源码并列出既定范围的剩余任务，不启用订单。

## 七个真实数据回调

统一注入点为 `scripts/youquant_gold_simnow_strategy.py::YouQuantBridge.__init__`。七项是下面的账户/交易事实回调；`ledger_anchor` 和 `atomic_claim` 是另外两项远端服务回调，不计入七项。现有校验与合成测试不等于生产采集器。

| 回调与代码消费点 | 当前准确状态 | 可立即完成的工程任务 | 必须等真实数据的验收 |
| --- | --- | --- | --- |
| `account_attestation()` → `snapshot()`、`_verified_added_ctp_binding()`、`_api_result()` | 已有接口和身份校验；真实独立采集/注入尚未实现 | 接 authenticated `GetPlatformList` 与 `GetRobotDetail` 的有界只读客户端；固定来源哈希、取得时间及机器人/CTP对象映射，实际未知响应形状失败关闭 | 账户已添加CTP对象与正在运行的机器人确实绑定；前置/9999匹配第一套正常环境；CTP `GetAccount.Info` 的真实投资者身份匹配。控制面只读可提前做，真实CTP连接不能由模板替代 |
| `current_margin(contract)` → `snapshot()`、`admit_command()` | 已有必需接口；没有真实“一手订单保证金”适配。只读原生查询候选不证明确切冻结金额 | 封装实际账户合约保证金、保证金价格基础及附加冻结政策证据，未知绝不回退到合约模板或研究占位值 | 原生账户/合约/投机身份一致、时点新鲜，能说明一手需要冻结的保证金，实际资金/保证金占用核对一致 |
| `current_round_trip_fee_upper(contract)` → `snapshot()`、网关/`admit_command()` | 已有必需接口；账户手续费率候选不等于完整开平费用上界 | 接账户费率与费用计价基础，分别处理开仓、平今、平昨，完成有证据的上界推导和缺失拒绝 | 实际账户费率及当前合约正确，含按金额/按手计费；上界覆盖相应退出成本，与模拟成交/结算费用核对 |
| `reconciliation_probe()` → 开仓 `snapshot()` | 已有 `True` 必需门及 `reconcile_four_way()` 算法；真实四方采集/判定回调未实现 | 从资本意图、原力执行事件、OMS和broker分别取得快照，统一身份/时点/单位；只有全部匹配才返回True，不能配置常量True | SimNow现金、冻结、持仓、成交与其余三方在真实开平/拒单/撤单/重启后匹配；不能把API ACK当成交 |
| `strategy_equity_mark()` → `append_equity_mark()`、`gold_paper.validate_strategy_equity_mark()` | 已有独立、新鲜权益标记校验和事件投影；真实策略核算器未实现；现合同只支持专用账户权益相等 | 建立明确的500万元策略资金范围、PnL/费用/浮盈亏和权益高水位账；先解决与实际账户总权益的范围关系，禁止直接复制账户余额 | 标记15秒内、同账户、证据哈希和独立对账成立；当前专用账户合同还要求策略权益与broker权益差额≤0.01元，无法满足时不得虚报或删除校验 |
| `daily_close_history(contract, now)` → `YouQuantBridge.verified_trend_history()`、`trend_exit_reason()` | 已有日线校验、5/20交易日和10日退出逻辑；真实合约历史输入回调未实现 | 接明确官方交易日与已完成日线，构建真实当前可知的连续价格指数/换月历史；缺日、未完成日或晚发布版本拒绝 | 当前合约/交易日一致，夜盘归属、换月和真实取得时点正确；盘中不会误用当日完整收盘，软退出/满期与账中入场交易日可复算 |
| `terminal_truth(order_id)` → `settle_order()`、`refresh_pending()`、换月/紧急平仓读回 | 已有终态核验、独立读回与四方结算消费接口；完整真实订单/成交/账户历史适配未实现 | 建立 order_id 与CTP委托/成交的明确映射；终态、成交手数、今昨仓、现金/冻结同截面读回，未知只核对不补单 | 实际 FILLED/REJECTED/CANCELED 与完整交易端历史一致；一手结果为0或1；提交结果不明、部分/未成交、撤单、重连及结算均保留证据。仅 `GetOrders` 当前挂单为空不能证明历史终态 |

七项采集器、接口接线、故障处理与合成测试可以现在实施。真实账号/CTP结构、账户费率、成交/结算事实只能在获准的真实只读连接和模拟工程测试中验证。09:15成本查询不能回填08:30：当前研究模式固定不授予执行权限；成本证据取得后仍需后续自然决策及完整准入。

## 远端服务、互斥与密钥通道

| 接点/范围 | 已有实现与仍缺实现 | 立即工程任务与最小验收 |
| --- | --- | --- |
| 信号独立收讫：`gold_au_signal_registry.LocalSignalRegistry.gateway_adapter(anchor_verifier)` → Edge `anchor_signal/read_signal` | 本地登记/重算、远端SQL/Edge已实现并部署，但应用 `SERVICE_DISABLED`；业务HMAC客户端、同分钟远端见证接线未实现，真实自然08:30未实测 | 实现受限signal客户端、写后读回、超时只读；真实自然08:30数据库收讫时间与本地记录、哈希一致。不得补录错过时点 |
| 账本锚：`YouQuantBridge.save_ledger()` → `ledger_anchor(events,root_hash)` → `append_ledger/read_ledger` | 本地持久化/根哈希检查与远端逐流仅追加SQL已有；生产runtime客户端及宿主注入未实现。账流按(account_id,robot_id)加锁，不能当账户级订单互斥 | 实现固定可信身份的HMAC客户端，完整前缀/根哈希写后核对；断线、旧前缀、分叉、写成读不明均冻结新单，不自动重发 |
| 命令认领：`YouQuantBridge.claim_order()` → `atomic_claim()` → `claim_order/read_claim` | SQL `order_claims.command_id` 永久唯一已实现，重复命令测试和远端回滚验证已有；Edge源码 `claimEnabled:false`；生产回调尚不可用 | 先补账户级协议，未完成前维持硬关闭。不同command_id同时竞争同账户、不同机器人及重启重放须不能取得两次新增风险提交权 |
| 账户级待决互斥/终态解除 | **没有现成解除回调/RPC**。现六种操作只有anchor/read_signal、append/read_ledger、claim/read_claim；命令级永久去重不能解决两个不同命令并发 | 版本化新增账户级待决状态、持有者及事务校验，与真实终态/四方对账联动释放。UNKNOWN不自动释放；原命令永久去重记录不能删除。保护平仓/紧急平仓必须有独立的风险减少路径，不能被永久账户锁堵死，也不能借保护退出解除新开仓限制。先完成并发、网络不明和旧持有者恢复演练，再考虑启用认领 |
| 安全密钥分发 | Edge `index.ts::configuration()`已有开关/两角色不同≥32字节HMAC与server-only数据库secret校验；优宽/本地非源码秘密注入、轮换和最小权限验证仍未完成 | 分离signal/runtime服务HMAC、订单消息签名密钥、优宽CommandRobot最小权限凭据。数据库secret只留Edge；密钥不得写单文件源码/日志/浏览器草稿/证据包。验证宿主真实秘密读取、拒绝错误角色/过期签名、轮换及泄露检查后再分发 |
| 订单消息通道：`youquant_command_transport.ApiCredentials`、`DurableOutbox`与CommandRobot；运行时 `process_command()` | 单次投递/事前outbox保留、消息验签、过期与重发拒绝已有实现；真实最小权限凭据接线及端到端读回待完成 | 接受准确 `PREPARED_NOT_SENT` 合同后单次投递；断线/ACK仅当传输状态，向交易端读回实际结果，不自动重发。命令HMAC与服务HMAC用途不可混用 |
| 宿主 bootstrap：`scripts/youquant_gold_simnow_strategy.py::main()` | main需要Python≥3.12且已注入 `GOLD2_SIMNOW_RUNTIME`；类和循环已有，真实bootstrap构造/注入尚未完成。解释器安装/兼容证据不构成该注入 | 实现可信机器人身份、七项数据回调、远端两回调、真实PD_LONG/PD_LONG_YD映射、私密签名密钥及 `PaperGrant` 构造；先保持enabled=false、只读验证，门全部通过后才进入单独标记的工程测试 |

服务实际部署状态以 `GOLD2-PRIVATE-RECEIPT-DEPLOYMENT-20260926.md` 为准：基础设施存在、HTTP读回SERVICE_DISABLED、订单认领硬关闭。源码地址为 `supabase/functions/gold2-paper-control/{index.ts,service.mjs,core.mjs}` 和 `supabase/migrations/20260925072235_gold2_paper_private_receipts.sql`。迁移部署及回滚探针不能写成生产回调已接通。

## 500万元策略账与SimNow账户账

冻结研究资金为500万元。`DEFAULT_CONFIG.paper_equity_cny`、研究风险预算以及 `gold_au_gateway.build_entry_ticket()` 的策略初始基数使用500万元；`PaperLedger.strategy_equity()`从独立 `EquityMarked`事件更新权益及高水位。实际账户的Equity、Available、Frozen、保证金、成交费用和结算现金来自CTP，金额未知时必须未知，不能填500万元。

现 `gold_paper.validate_strategy_equity_mark()` 明确采用 `DEDICATED_STRATEGY_PAPER_ACCOUNT`，同时要求标记中的broker权益与实际provider相同、策略权益与broker权益相同。它没有实现“总账户里虚拟分配500万元”的映射。若真实SimNow账户规模与冻结策略基数不同，或混有别的仓位/资金变动，不能简单把账户Equity当策略权益，也不能把策略500万元当真实账户现金。必须先满足当前专用范围，或另行版本化并审核可对账的分配账映射；风险比例/回撤规则保持原冻结值，当前不放宽校验。

网关取“冻结信号预算”和“真实策略权益预算”的较小值，并分别检查账户可用资金及策略保证金比例；这能限制下单风险，却不能修复资金范围混用导致的权益高水位/回撤错误。后续验收必须同时保存策略账与账户账及其范围解释、现金/保证金/费用/PnL勾稽，不能用一套相同模拟数字宣称四方对账通过。

## 本轮如实完成边界

已有实现需实测：研究晨间自然冻结、精确current replay、签名/时间窗/风险/持仓/账本校验、订单生命周期与结算算法、单次CommandRobot投递核心、已部署但关闭的远端SQL/Edge。

已有接口需实现：七项真实数据采集与适配、runtime bootstrap、两个远端服务客户端、自然信号远端见证接线、账户级互斥与终态解除、安全密钥注入、策略资金范围账。它们可先立即工程推进，真实身份/数据/成交部分随后在交易时段验收。正式30日模拟运行、零重复单与零未解释对账差异仍未达成；没有实现的工程项不能登记为“只待周一观察”。
