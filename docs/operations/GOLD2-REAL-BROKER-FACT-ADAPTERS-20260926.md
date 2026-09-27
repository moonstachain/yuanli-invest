# GOLD2 真实只读事实适配与未接线边界

本轮实现的是可在真实优宽宿主调用的只读 reader，不是一份把历史 fixture 宣称为实时账户的采集器。实现位于 `src/yuanli_invest/gold_au_broker_facts.py`，对应测试位于 `tests/test_gold_au_broker_facts.py`。导入和构造都不发请求；实例方法只调用注入的真实 `exchange`。本轮没有用真实账户运行该 reader，没有创建或启用交易授权，没有下单或撤单。

`OfficialDailyHistoryReader` 位于独立本地模块 `src/yuanli_invest/gold_au_official_exit_history.py`，直接依赖本地官方日线和年历核验；云端 `gold_au_broker_facts` 不导入、不重新导出该类。生产云包保留 `daily_close_history` 外部注入位，由独立已认证生产者提供核验后的日线回执，本地采集 pipeline 不随订单运行时迁入云端。

## 宿主与官方接口

唯一执行候选仍为既有优宽云端、SimNow 第一套正常交易环境。这个模块不增加第二个宿主，也不决定 Python 解释器；解释器、原生接口可用性和最终 bootstrap 是另一个验收门。

`BrokerFactsReader.read_current(contract)` 实际编排 `IO("status")`、`GetAccount`、`ReqQryTradingAccount`、`GetPositions`、`GetOrders`、`SetContractType` 和 `GetTicker`。`GetOrders` 仅代表当前全账户未完成委托，空数组不会生成成交或撤单终态。

`terminal_truth(order_id)` 实际使用 `IO("api", ...)` 查询 `ReqQryTradingAccount`、`ReqQryOrder`、`ReqQryTrade`、全账户 `ReqQryInvestorPosition`，并重新取得全账户当前挂单。成交状态必须同时与 native 报单、去重后的真实成交数量、账户和持仓吻合；已明确观察到的未成交排队订单返回 `PENDING`，允许继续监控或期限撤单，但不允许终态结算或释放 claim。未知、缺报单、缺成交、短仓、外部合约持仓、超过一手或“宣称终态却依然挂单”均阻断。

官方依据：

- [优宽 CTP IO API](https://www.youquant.com/bbs-topic/3756)：完整 native API 名称、请求字段、分包和 `Name`／`Value` 返回格式。
- [优宽 CTP 接口融合说明](https://www.youquant.com/bbs-topic/9582)：`ReqQryOrder`、`ReqQryTrade` 与历史订单接口，native char 可表现为数字 ASCII。
- [GetOrders](https://www.youquant.com/syntax-guide/fun/trade/exchange.getorders)：全账户未完成订单；不依赖当前设置合约。
- [GetHistoryOrders](https://www.youquant.com/syntax-guide/fun/trade/exchange.gethistoryorders)：仅当前交易日，不是跨日历史档案。
- 用户提供的 CTP 6.7.13 SDK：native 字段与 char 常量。MarginPriceType 的 `1/2/3/4` 分别对应昨结／最新／成交均价／开仓价；代码显式映射，而不凭枚举名称推测。

## 七个 callback 的实现边界

| callback | 已实现 | 必須由独立接线提供的真实证据 |
|---|---|---|
| `account_attestation` | 先真实取得 broker InvestorID 与现金 AccountID，再核对独立控制面证明 | 已认证 GetPlatformList、GetRobotDetail 原文回执，当前 robot／账户／第一套 fronts 绑定；仅 9999 或实例名称不够 |
| `current_margin` | 查询账户、投机、具体合约绝对保证金率与计价参数，计算一手上界并向上取分 | 经独立验证的账户额外冻结政策及价格上界；metadata 或估算不能替代实际冻结规则 |
| `current_round_trip_fee_upper` | 账户开仓、平今、平昨金钱／每手费率分别计算，取平仓两种的较大者 | 未来平仓价格、费率和附加费用真实上界的有效账户政策；缺任何项阻断 |
| `reconciliation_probe` | 分别读取四个独立来源、验签／来源／账户／时点并调用现有四方核对 | 资本意图、原力执行账、OMS、broker 四个真实生产者；不能复制 broker 数值来填四方 |
| `strategy_equity_mark` | 明确预留独立会计模块调用位，缺接线阻断 | root 实现的固定 500 万分配与真实盈亏／费用／日结子账；不能复制整个 broker 权益 |
| `daily_close_history` | `OfficialDailyHistoryReader` 重读官方 JSON 字节、哈希、日期、具体合约，并使用已验证上期所年历；默认 21 日 | 本地真实官方快照读取函数、年历源文件；至少 11 个连续已完成官方交易日 |
| `terminal_truth` | 查询真实 native 报单＋成交＋账户＋全账户持仓和当前挂单 | 已独立验证的 platform order_id → CTP OrderSysID、OrderRef、FrontID、SessionID、broker TradingDay 绑定 |

`callbacks()` 返回上述七个 bound methods，可供 `YouQuantBridge` 注入。所有缺失的真实生产者默认抛出有代码的 `PaperDenied`，没有 permissive fallback。

生产 factory 的终态 callback 使用 `terminal_truth_with_four_way` 替换基础 `terminal_truth`。该 resolver 先真实取得 native broker 事实；`PENDING` 原样保留且不读取四方。真终态时再分别调用四个已有独立 reader，核验各自来源、验签、环境、账户、具体合约、时点和原文哈希，使用 core 四方核对，并额外把核对结果的订单、数量、现金、可用资金和冻结保证金绑定到刚取得的 native 事实。四个来源彼此同意但共同给出错误 broker 金额也不能通过。

来源缺失、未认证、过期、原文哈希缺失/复制或上游失败，保留真实 native truth 并标记 `reconciliation_status=UNKNOWN`；有效完整来源间漂移则标记 `DRIFTED`。只有真正匹配才附加 `four_way` 中四份实际 reader 回执。resolver 不从 broker 数值合成其它三腿，不向 DB 写入证据或释放 claim。`broker_truth_sha256` 保留加入四方信息前的真实 broker 回执哈希，新的 `raw_sha256` 覆盖完整 resolver 输出。

## 凭据与来源边界

`account_attestation_reader` 是独立控制面真实 HTTPS API reader；`account_attestation_verifier` 必须检查真实 API 回执及确切 robot／账户／fronts。模块不会从 `GetName`、订单命令、BrokerID 或自己生成一份 identity 真值。

`independent_receipt_verifier` 必须核验相应来源的身份、完整签名和真实上游证据，不能采用 `lambda _: True`，也不能把操作员任意填写的数字签名后当成 broker 成本政策。测试中使用的 HMAC 和账户都是明确的离线测试数据，不能部署。

独立执行成本政策的 source 为 `independent_account_execution_cost_policy`，必须含账户、环境、合约、整数一手、CNY、观察／过期时点、原文哈希、额外冻结及未来完整费率覆盖、保证金／开仓／未来平仓计价上界、额外费用和往返费用上界。开仓价格上界至少覆盖当前真实 native 涨停价；动态计价保证金也覆盖该上界。费用回执的计算结果若超过独立政策上界则拒绝。当前并没有已取得的真实政策，因此正式成本 callback 仍会阻断。

每个 native 回执同时保留：方法、精确请求字段、调用开始 `observed_at`、结束 `available_at`、完整 decoded canonical JSON 的 `response_sha256`、安全字段 projection 及其 `projection_sha256`。这是 Python 解码对象的规范 JSON 哈希，**不是 CTP transport wire bytes**。未知 struct、错误返回、非有限数字或过大的响应被拒绝；已知 struct 的额外字段不进入推导。身份字段留在私有内存回执用于精确核对，模块不打印回执或密钥。

`read_current` 的 position／pending order hashes 为白名单规范投影哈希；`terminal_truth` 的四个 `raw_account/orders/trades/positions_sha256` 均为相应完整 native decoded canonical 响应哈希。两种 hash 语义已在回执注明，不应混用。

每个 native 调用完成后立即保存对应 receipt 对象：当前账户、四项成本查询以及终态账户／报单／成交／持仓均使用显式局部引用；最终输出不从后续读回的动态末尾列表猜来源。因此后续行情查询、policy callback 或挂单 callback 增加无关 native 回执，也不能把行情哈希冒认为账户哈希或改变四类成本／终态证据的范围。

## 终态与账户互斥的接线

平台返回的 order_id 不会被猜测为 CTP OrderSysID。缺少真实 binding，查询明确阻断。无 exchange OrderSysID 的早期拒单目前也不能通过该路径证明；需要另行接入真实的拒单回报或可信 OMS 拒单事实。

broker TradingDay 必须从 native 账户实际读回。夜盘不通过本地自然日期猜 TradingDay。跨 broker 日未保留经验证的历史档案时返回 `CROSS_DAY_TERMINAL_ARCHIVE_UNAVAILABLE`；不能把新交易日空列表当作昨天的终态。

基础事实输出只形成 broker 一方，不自动产生 coordinator 的 command_id、claim_id 或另外三方数据；四方 resolver 只能消费已有的四个独立生产者。独立 broker_reader 需把这些真实 native 哈希、精确指令绑定和已完成的真实四方核对一起签名，取得不可变服务证据 id；运行时再引用该 id。当前 reader、runtime、DB 应用权限仍需独立配置，缺失就维持禁用。

## 时点和故障恢复

每个同步读取先后记录真实时钟，迟到超过 15 秒、时钟倒退、未来或陈旧行情均拒绝。一轮成本或终态快照整体也不得超过 15 秒。synchronous `IO(api)` 没有官方可中断超时参数；reader 能拒绝迟到返回，不能保证中途停止阻塞，必须保留外部宿主 watchdog。

官方日线 reader 拒绝休市日/当日未完成数据、缺失交易日、错合约、错 URL、原文日期不同、哈希不符或取得时点晚于输入 cutoff。其输出明确是“现在观察到的已完成历史”，不能冒充历史首发数据。消费端应在读取完成后用真实当前时钟验证观察时点，不将新的读回回填到调用前的旧时点。

## 验证状态

本模块 51 项测试通过，覆盖真实调用编排、已完成/缺成交/明确排队/未知/跨日终态、重复成交、账户/合约错配、未来/迟到、错误 struct、错误或附加字段、ASCII enums、手续费上界过小、额外冻结缺失、涨停价格上界、日历与日线原文字节绑定、四方来源独立性、缺失/伪造四方回执、共同错误金额、共同错误订单、原文哈希复制、真实现金漂移，以及嵌套后续 native 查询不会改变先前账户／成本／终态证据哈希。

这些测试证明软件在明确输入下如何处理，并不证明 SimNow 已读回或工程开平已验收。真实账户政策、order binding、四方生产者和子账都未连接前，正式运行继续阻断。
