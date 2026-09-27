# GOLD2-AU-V1｜证据、权限与验收矩阵

本文件记录**验收合同**，不是验收通过回执。日期：2026-09-25。任何 `PASS` 必须附可复核的实际运行产物、代码/配置 SHA、输入版本与独立读回；候选代码、设计文档、旧项目回执都不能自动替代本项目的实测证据。

## 1. 为什么要分账

用户原设计提出实际利率、美元信用与避险三类机制。V1 把 DFII10 与广义美元用作入场过滤，把官方购金和 ATR 用于缩小风险预算。央行买金不能单独证明“美元信用恶化”，价格残差也不是信用贡献。旧 B2 月频模型相对简单基准约 1.58% 的 RMSE 改善和 B3 未过跨阶段门槛保持原判；新 AU 规则必须从零取得自己的验证成绩。

三条不可穿越的边界是：`历史同期归因 ≠ 前向信号`、`前向信号 ≠ ActionContract`、`ActionContract ≠ SimNow 成交/结算`。每一步使用自己的版本、授权和结果合同。研究失败与执行失败分别记录，不能相互抵销。YEX0 的 `ResearchAuthority != CapitalAuthority != ExecutionAuthority`、`UNKNOWN = DENY`、`Receipt = Ledger; Status = Projection`、四方对账都适用。

## 2. 来源与数据等级

| 证据等级 | 可用于何处 | 绝不声称 |
| --- | --- | --- |
| `STRICT_PIT` | 当时已发布、已取得、已可用的版本，可用于严格 08:30 回放/前向信号 | 仅凭观测日期推定已知。 |
| `CONSERVATIVE_RECONSTRUCTION` | 用有依据的保守延迟重构历史；单独披露规则与缺口 | 等同真实历史首发捕获。 |
| `LATEST_VINTAGE_ONLY` | 历史覆盖、敏感性和探索性诊断 | 无泄漏回测、当时可交易成绩。 |
| `UNKNOWN` | 缺口显示、无信号、风险预算缩小 | 用今天的补采值或语言补全历史。 |

每条记录最少可回溯到原始来源定位、原文哈希、具体经济序列/合约、单位、测量口径、观测时点、首发时刻、取得时刻、可用时刻和版本。相同事件的修订或多供应商表示不构成独立市场样本。H.10 日观测的**周发布**、WGC 报告约两个月滞后、期货夜盘和日线标签都要各自说明；不得以供应商展示日期代替交易决策可用时间。现有 Wind 长端实质利率/DXY 与 DFII10/H.10 不混系数。

YSIP 的来源/路由职责是 `SENSE → IDENTIFY → NORMALIZE → PROVE → ROUTE → OBSERVE`。本项目候选 `provider_id` 为 `youquant_history`、`shfe_public`、`fred_or_federal_reserve`、`wgc_official`、`simnow_account`，具体 Provider Registry 映射/授权尚须核查；这些是待登记的来源候选，不是已获批 provider enum。市场数据与账户事件要分别建 Reality Event；原始日线、交易所对照文件和后续图表可属于同一交易日事实的不同表示。YSIP 只形成证据，不授予交易权；知识晋级、GBrain Recall 和跨任务 Learning 各由其独立门槛验收。

**截至本文件编写时的 YSIP 状态**：已在仓外取得 2019-07—2026-09 的供应商原始包、1,759 份上期所日报、宏观原始包及逐份哈希核验回执；这属于本轮研究采集证据。目标 `DISCOVER`；正式 `DISCOVER/SENSE/IDENTIFY/NORMALIZE/PROVE/ROUTE/OBSERVE` 均为 `PENDING`，因为尚无完整 Provider Registry/权限记录、生产传感器回执、Reality Event identity 与健康证明。不能把研究原始包自动晋级为全链 PASS。`reality_event_id=UNRESOLVED`；`action_authority=none`。`ACCEPT_THROUGH=NONE; OPEN=DISCOVER`。待正式产物形成后按来源更新，不用文档自身作证据。

## 3. ShareSpec 本域审计界限

本仓已有 [绑定](../../../governance/shared-spec/yuanli-shared-spec-binding.v0.1.yaml)：域仓 `moonstachain/yuanli-invest`；Registry 指向 `moonstachain/yuanli-strategy-soul` 的 `governance/mpe0/shared-spec-registry.v0.2.yaml`，本地记录的 `verified_owner_commit=a48675a22c6419973f2a0404fee01375fe83b9e8`，`last_verified_at=2026-09-19T01:31:00+08:00`。槽位为 UniversalBootstrap、MissionBattle、TaskContract、HumanAuthorization、ProviderContract、EvolutionCandidate。既有偏差 `YIP-RESEARCH-TRADE-SEPARATION` 和 `YIP-RUNTIME-PINNING` 恰好约束本项目。

这是**本地绑定的历史记录**，并非 2026-09-25 对 Soul 当前活动 registry、Usage Contract、Domain Binding Protocol 和 exact pin 的新鲜核验。当前审计模式为 `AUDIT`，`owner_resolution=LOCAL_BINDING_ONLY`、`freshness_state=UNKNOWN`、`compatibility_state=NOT_REVALIDATED`、`writes=THIS_LOCAL_CANDIDATE_ONLY`。本目录不复制共有规范、不自动推进 exact pin、不创建新共享法律。下一合法动作是在拟激活高效应纸面运行时之前重读 Soul 当前权威与本域 profile，刷新绑定/兼容性证据；任何共享语义变更须另外走 owner 与 Human Gate。这个审计记录不授予 Capability、知识或执行权。

## 4. 分阶段验收表

| 门 | 可验收的证据 | 当前状态 |
| --- | --- | --- |
| A. 机制冻结与蒙熊第一次审核 | V1 配置/代码/证据哈希、反例、基准、停止条件；蒙熊本人在看新结果前的原文提交与时间 | `PENDING`；模板不算专家意见。 |
| B. 2019-07 起数据 | 逐合约覆盖矩阵；跨年份/换月/高波动日期上期所对照；合约元数据冲突和成交量差异单列；PIT 等级和零未来信息入模 | `PARTIAL / BLOCKED`；1,759 份官方日报已替换最终日线，20 个未取得日期隔离；交易日历、历史首发和成交级证明未齐。 |
| C. 固定规则回顾 | 三个冻结区块，价格/利率/美元/完整过滤器/持有空仓同口径基准，2/5 跳双边成本，四格敏感性，被过滤后上涨机会和所有失败 | `EXPLORATORY_COMPLETE / NOT_ACCEPTED`；14 组回顾已跑，历史首发版本与成交级证据缺失，投资门仍未通过。 |
| D. 事前信号 | 每日 08:30 输入/代码/配置/证据哈希、开/跳过原因、5/20 日结果事前登记、无后来信息；每次可复算 | `PENDING`。 |
| E. 蒙熊第二次盲审 | 蒙熊、RAY、机器同一冻结证据截面分别封存，后揭盲并记录分歧；历史已知案例另标记 | `PENDING`；机器生成卡不是专家确认。 |
| F. SimNow 只读预检 | 第一套正常交易环境与账户身份从交易端读回；AU 合约、行情、委托、持仓、资金、今昨仓和费用/保证金核查 | `PENDING`；不能凭优宽登录状态推定。 |
| G. 一手工程测试 | 独立标记的实际 SimNow 开/平仓，订单/成交/账户/结算回执、异常演练和四方对账 | `PENDING`；任何本地合成事件都不算。 |
| H. 30 日运营 | 正式激活后连续 30 日历日，零重复提交、零未解释仓位/现金差异；成功、跳过、拒单、部分成交、重连与日结算可重放 | `PENDING`；仅能证明流程可运行。 |
| I. 投资增量 | 至少 12 个月且 30 笔独立正式入场；每笔事前 5/20 日结算，冻结基准、真实费用和回撤门槛共同评估 | `PENDING / UNPROVEN`；时间与样本门槛都不能缩短。 |

门 G/H 不得用“策略在优宽回测成交”代替真实 SimNow 订单；门 I 不得用 30 日运营替代。门 B/C 成绩不利或数据不合格时保留失败，不通过新阈值回填 V1。门 E 有分歧时记录分歧，不投票把问题变成“专家真值”。

## 5. 外部依赖与权限状态

- **账户与凭据**：需要使用者在 SimNow 和优宽官方页面准备第一套正常环境、云托管、专用机器人、交易所连接与最小权限 `CommandRobot`。本目录不存储账号密码、令牌或私有持仓。
- **项目纸面授权**：需独立、可核对、有效期内的 PaperGrant/人的批准引用；既有 YEX0/YVN1 接受回执列出的 `broker_paper_authorized=false` 不因这份计划或研究 PASS 自动翻转。单次 ActionContract 的边界只能等于或小于项目授权。
- **专家意见**：需要蒙熊本人两轮真实提交；用户附件和本模板不能代填。RAY 的判断亦须本人提交，机器意见带版本和证据截面。
- **日历时间**：30 日正式运营与 12 月/30 笔投资验证必须经历真实时间，不能通过历史重放压缩完成。
- **数据许可与订阅**：本轮不购买新的数据订阅；无首发版或权限不足的来源降级为未知或只做前向采集。
- **真实资金**：始终不在 V1；任何账户身份无法从交易端证明是 SimNow 第一环境，直接拒绝，不靠人工描述兜底。

工程实现完成后仍只意味着可供审查的候选。任何 `PASS` 需要在其当次真实证据后追加独立回执；本文件、代码编译、单元测试或旧项目成功均不是纸面实际成交与 30 日运行证明。
