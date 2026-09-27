# GOLD2 联动保护退出 V3：实现完成与现实验收边界

本轮是受控 SimNow 工程的代码闭环，不代表已连通或已成交。生产新开仓继续明确拒绝，原因更新为 `LINKED_PROTECTIVE_EXIT_REAL_ACCEPTANCE_REQUIRED`。没有新增采购、发放密钥、配置真实账户 binding、打开交易开关或发出任何真实委托。

## 完整可测试的最小风险协议

母开仓 native 已精确确认一手 FILLED，但四方账尚缺失时，不再通过旧 V2 空闲账户 claim 绕锁。V3 独立证据账只接受隔离 broker_reader 身份写入，并明确区分 `NATIVE_ORDER` 与 `PAIRED_TERMINAL`。

`NATIVE_ORDER` 必须保留命令 ID、claim ID、真实 AU 合约、原生订单映射、独立身份以及账户／委托／成交／持仓查询的哈希。原始开仓的签名范围须已存在于外部锚定 ActionAdmitted 账中。母单确切 FILLED 一手、全账户只有这一手多头、没有未决挂单，且确属该母 claim 时，才允许对同一合约建立一次风险减仓子 claim。

账户行先加锁，再核对版本和外部账头。子 claim 占据 pending 状态；母 claim 与子 claim 的关联永久保留，母单只能关联一个自动保护子单。原 signed entry 所限定的止损、趋势、期限或换月退出可触发减仓，但不能产生新的持仓、另一个合约或两手订单。父子两个 claim 都不能通过原 V2 终态函数或其私有原实现跳过配对协议。

提交依然先落本地不可篡改链和外部锚，再登记远端提交尝试，取得精确回执后才调用 Sell。委托结果不明、服务不明、重启、子单拒绝或撤销都不获得再次 Sell 的权限。当前每个母单只允许一次自动子单；拒绝或撤销后仍可能持有一手，冻结账户并进入人工恢复合同，不能静默循环重试。

子 close 原生 FILLED 且当前空仓，只能记 `EmergencyCloseObserved`，不直接记策略成功或四方一致。后续必须取得配对证据：两个不同的原生订单 ID；四个不同的经认证生产者；每方都确认开、平各一手、最终零持仓，且现金、可用和冻结额误差不超过一分钱。配对证据和外部账都通过后才把父子本地 pending 清除，远端继续保持 FROZEN，停止新开仓等待复核。

## 不明提交与服务失联

不明 Buy/Sell 结果只接受独立签名的 command_id／claim_id／订单三元绑定。已实现 `BrokerFactsReader.native_order_evidence_v3`：实际调用 allowlist 中的 ReqQryTradingAccount、ReqQryOrder、ReqQryTrade、ReqQryInvestorPosition 和挂单读取，并校验原生 Direction／Offset、平台原生绑定哈希。它不扫描相似价格、相近时间的订单来猜归属，不生成其他三方凭证，也不发单。

找到准确绑定后，仅把原订单 ID 记入审计链并继续原生终态读取；永不重发原订单。缺绑定、跨交易日原始档案缺失或服务不可用时继续未决。

ReceiptClient 的未知写冻结不会被此恢复代码解除。同一被冻结实例发现 native 订单 ID 后，仅返回只读观察，不修改账或调用交易端。只有另一个新进程在外部账根、序号与账户占位逐项核验一致后，才有可能接入窄保护路径。外部账不一致或服务仍不可用，不会购买第二宿主、绕过锚服务或声称持续止损已经得到保证。

## 本轮验证

- Python 风险、native adapter、协调器及收讫相关 125 项通过，其中新增联动风险情境 10 项、新原生转换 5 项、独立逆向收讫审查 8 项。
- Node 新增 V3 协议及 Edge 22 项通过；原 V2 50 项仍通过。
- 隔离 PostgreSQL 26 个断言通过，BEGIN／ROLLBACK 后 native_facts、linked_claims、bindings 均为零。覆盖 SQL 缺失／null reason、V2 和私有函数旁路、一次性子单、版本冲突、native 空仓不能替代配对账、四方漂移、配对后冻结及再次开仓拒绝。
- 上述全部是离线实现证据。PGlite 的单连接结果不替代真实 PostgreSQL 多连接竞争验收，也不替代 SimNow 行情、账户、持仓、委托、成交和日结。

## 尚需取得的现实证明

1. 正常交易窗口实际只读连接，优宽原生 Python 3.12 及真实独立账户身份。
2. 独立的 command／claim／平台／CTP 原生订单绑定生产者，不把 runtime 本身或 fixture 当独立 reader。
3. 隔离 broker_reader 密钥及已审 source 绑定、真实 V3 ingest／read 回执。factory 提供注入接口，但目前没有真实独立 reader 运行证明。
4. 开平父子配对四方生产者、500 万元子账真实费用和日结生产者以及跨交易日原生档案。本轮不填充虚构四方值。
5. 工程一手开平、撤拒单、重启、服务中断、精确恢复、今昨仓和日结的独立验收；只有完成后才允许讨论取消生产准入硬门和启动 30 日运营观察。

数据库 migration 由 Supabase CLI `migration new gold2_linked_protective_exit_v3` 创建为 `20260926113459_gold2_linked_protective_exit_v3.sql`。本实现交付阶段没有部署后端或云策略；根任务可在核验完整源码之后部署禁用后端候选，仍不能推断交易启用。
