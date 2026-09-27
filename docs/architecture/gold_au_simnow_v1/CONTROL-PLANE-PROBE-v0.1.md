# GOLD2-AU｜优宽控制面只读探针

`scripts/youquant_control_plane_probe.py` 是本地控制面探针，不是策略、交易网关或账户连接认证。默认只列出将查询的方法，不读取密钥、不联网。仅显式加 `--execute` 后，才从环境变量 `YOUQUANT_ACCESS_KEY`、`YOUQUANT_SECRET_KEY` 读取专用 API Key，向固定 `https://www.youquant.com/api/v1` 发送 token 签名表单 POST。代码白名单只有 `GetPlatformList`、`GetRobotDetail`、可选的 `GetRobotList` 与 `GetNodeList`；没有 `CommandRobot`、创建/重启机器人或任何交易方法。密钥应由用户在可信环境中配置，不能写入命令行参数、仓库或本页。API Key 权限只授予实际要查询的方法，不能使用 `*`。

在仓库根目录运行：

```bash
.venv/bin/python scripts/youquant_control_plane_probe.py
.venv/bin/python scripts/youquant_control_plane_probe.py --robot-id <已知机器人ID> --include-robot-list --include-node-list
.venv/bin/python scripts/youquant_control_plane_probe.py --execute --include-robot-list
.venv/bin/python scripts/youquant_control_plane_probe.py --execute --robot-id <已知机器人ID>
```

前两条均为 dry-run。当前账号尚无机器人时，第三条可只读核查已添加交易所和机器人数量；建立专用机器人并取得其 ID 后才用第四条核查详情。`GetRobotDetail` 需要明确的正整数机器人 ID，不会猜测或遍历。`GetRobotList` 和 `GetNodeList` 未指定分页时，摘要分别报告 API `all` 总数与本次返回是否完整；不能把局部列表误认为全部对象。

成功仅输出时间、方法、**原始响应字节** SHA-256、计数、配置形状和“机器人绑定是否指向本次返回的已添加 CTP 对象”。任何 `profiles` 原文、账号、前置地址、机器人 ID、密钥、签名及原始响应都不打印、不落盘。官方 `GetPlatformList.profiles` 示例只给占位符；探针仅将直层 `BrokerId`、`TDFront`、`MDFront` 对象（或同形状 JSON 字符串）计入可识别配置，其余记为未知，不猜字段。即使与第一套正常环境配置相符，结果仍固定 `broker_connection_verified=false`、`paper_authority_enabled=false`：控制面配置不能证明 CTP 登录、持仓/委托、实际连接、SimNow 结算或运行时身份。

官方 token 规则为对 `version|method|args|nonce|SecretKey` 做 MD5，`nonce` 是毫秒时间戳，需递增并落在平台允许的时钟窗口内。探针在一次运行内单调递增，不复用失败请求，也不跨进程存储 nonce；需保证本机时钟准确、同一 Key 不并发调用。遇到 nonce/权限/签名错误、网络异常、重定向、非 200、超大响应、重复 JSON 键或结构不符，固定错误码失败关闭，不重试。HTTPS 使用系统证书验证，关闭环境代理与重定向，10 秒超时，单次响应上限 256 KiB；官方旧 Python 示例关闭 TLS 验证的语句**不能**复制进此探针。

只读 API 结果也可能包含敏感信息，尤其 `profiles`。本程序只把原始哈希输出到终端；它不是可重放的 API 原文回执，也不能直接充当策略内 `account_attestation` 的可信来源。正式 `PaperGrant` 仍需独立来源的账户/连接读回、运行时绑定、外部账本与授权审查。

依据：[优宽 token 验证](https://www.youquant.com/user-guide/%E6%89%A9%E5%B1%95api%E6%8E%A5%E5%8F%A3/%E9%AA%8C%E8%AF%81%E6%96%B9%E5%BC%8F/token%E9%AA%8C%E8%AF%81)、[GetPlatformList](https://www.youquant.com/user-guide/%E6%89%A9%E5%B1%95api%E6%8E%A5%E5%8F%A3/%E6%89%A9%E5%B1%95api%E6%8E%A5%E5%8F%A3%E8%AF%A6%E8%A7%A3/getplatformlist)、[GetRobotDetail](https://www.youquant.com/user-guide/%E6%89%A9%E5%B1%95api%E6%8E%A5%E5%8F%A3/%E6%89%A9%E5%B1%95api%E6%8E%A5%E5%8F%A3%E8%AF%A6%E8%A7%A3/getrobotdetail)、[API Key 权限](https://www.youquant.com/user-guide/%E6%89%A9%E5%B1%95api%E6%8E%A5%E5%8F%A3/%E5%88%9B%E5%BB%BAapikey)。
