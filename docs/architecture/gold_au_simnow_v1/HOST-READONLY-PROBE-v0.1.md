# GOLD2 AU｜优宽单编辑器只读宿主探针

`scripts/youquant_gold_simnow_readonly_probe.py` 是一份可单独放入优宽 Python 策略编辑器的源码。它不导入本仓库模块，不包含账户凭据、`PaperGrant` 或下单授权。代码加载时不查询宿主；由优宽调用一次 `main()` 后，它以 1 秒间隔、最多 30 秒等待 `exchange.IO("status")` 就绪，再依序调用 `SetContractType`、`GetAccount`、`GetPositions`、`GetOrders`、`GetTicker`。超时即停，不进行后续查询。`SetContractType` 只选择／订阅指定到期合约，不提交委托。没有 `GetCommand`、`_G`、`CommandRobot`、`Buy`、`Sell`、`CancelOrder` 或 `SetDirection`。

2026-09-25 优宽托管者预检读回 Python 3.9.2。此探针本身以 Python 3.9 为最低诊断版本，报告中 `probe_python_supported` 表示探针可运行，`python_supported` 仍表示正式纸面交易核心要求的 Python 3.12 是否满足。前者为真、后者为假时允许做只读账户核验，但**不能启动交易核心或授予下单权限**。

使用时先在源码顶部确认 `PROBE_CONTRACT` 是当前合格的上期所真实到期月 `auYYMM`，且交割月距当月至少两个月。当前默认 `au2612` 仅供 2026 年 9—10 月预检，之后须更新。将整份源码放入**独立的只读探针策略**，只绑定用户自行在优宽／SimNow 官方页面配置的专用模拟交易连接，在该合约有实时行情的时段运行一次。不要把密码、API Key 或 SimNow 私有信息粘入代码。仅在账户绑定和平台费用经用户核对后再启动云托管实例；保存草稿本身可以先做。

成功报告是 `HOST_READBACK_OBSERVED_UNATTESTED`：证明这次宿主确实返回了连通状态、严格匹配 `SHFE/auYYMM` 的合约规格（1000 克／手、0.02 元最小跳动、对应交割年月、可交易）、可识别的账户、仓位／未完成委托列表以及不晚于 15 秒的行情。报告还给出 Python 版本、各查询是否尝试、仓位及委托数量、非目标合约仓位数量、报价年龄和对**所选只读字段**的 SHA-256。账户 ID、订单 ID、资金、仓位明细、报价和原始回包不会写入日志；异常文本也不会写入日志。`selected_readback_sha256` 是选择字段哈希，不是供应商原始完整回包哈希，也不替代受控原始证据留存。

任何缺失、断线、错合约、错交易所、规格不符、账号 Broker ID 非 `9999`、不可读仓位／订单、过期或未来行情都会给出 `HOST_READBACK_BLOCKED` 和固定原因码；不会继续后续查询或尝试下单。2026-09-25 22:42 的优宽机器人 `479509` 实际检查了 31 次、等待约 30 秒，仍返回 `EXCHANGE_NOT_CONNECTED_TIMEOUT`；账户、持仓、订单和行情查询均未发生。前置地址、Broker ID 和投资者代码已与官方页面核对一致，但该状态不能单独区分新账户生效时间、密码、认证、交易时段或网络问题。闭市时行情通常过期，应在交易时段重新检查，不能把闭市阻断解释成平台永久不兼容。

**即使成功，也不证明**这是 SimNow 第一套正常环境、当前账号绑定了哪一台机器人、优宽控制面 `GetPlatformList`／`GetRobotDetail` 与策略内账户是一体、费用及保证金独立读回、外部时间锚和原子命令认领可用，更不产生模拟盘交易许可。必须继续按 [部署预检](DEPLOY-PREFLIGHT-v0.1.md) 和 [运行手册](RUNBOOK-v0.1.md) 的独立认证、对账、工程测试和授权门槛推进。探针的 `paper_authority_enabled`、`simnow_first_normal_attested`、`broker_account_identity_attested` 与 `robot_binding_attested` 恒为 `false`。

本地离线验证：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest tests.test_youquant_gold_simnow_readonly_probe -q
```

优宽 API 口径：[设置商品期货合约](https://www.youquant.com/syntax-guide/fun/futures/exchange.setcontracttype)、[账户查询](https://www.youquant.com/syntax-guide/fun)、[持仓查询](https://www.youquant.com/syntax-guide/fun/futures/exchange.getpositions)、[未完成委托查询](https://www.youquant.com/syntax-guide/fun/trade/exchange.getorders)、[行情查询](https://www.youquant.com/syntax-guide/fun/market/exchange.getticker)。
