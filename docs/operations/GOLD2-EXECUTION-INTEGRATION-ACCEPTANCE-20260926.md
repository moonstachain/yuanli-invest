# GOLD2 V2 执行集成：部署与未完成准入

本轮为最小执行闭环的实现与私有后端部署，不是 SimNow 或正式交易验收。受控模拟授权有效；真实资金和新增采购不在范围内。真实绑定、工程成交、正式成交均为零，30日运营尚未开始。

## 已实现与实际部署

- `gold_au_broker_facts.py` 实际宿主读取账户、全账户持仓/挂单/行情及CTP原生数据。明确排队返回PENDING；空挂单不代表成交。每个原生查询立即捕获自己的完整解码规范JSON哈希，不随嵌套后续查询漂移。
- `gold_au_strategy_accounting.py` 建立固定500万元虚拟分配，保留总账户未分配余额；完整成交、费用和日结事实逐项绑定，已实现/浮动/费用复算并与总账户变化核对。初始化只能从真实空仓无挂单的新账开始；未知锚定不重复初始化。
- `gold_au_receipt_client.py` 固定TLS、HMAC及角色；写入不明冻结，独立读回不自动重写或解除冻结。密钥在源码外的0700目录、0600文件，数据库secret只留服务器。
- `gold_au_account_coordinator.py` 将OrderClaimRequested、提交前OrderSubmitAttempted和OrderTerminalReconciled与独立reader证据、远端版本和账户占位绑定。重启先核对外部账；未决状态只读恢复，不能接新指令。
- `gold_au_runtime_bootstrap.py` 是唯一支持的生产构造。它强制新子账、冻结资金和风险范围、V2客户端及官方LONG常量；旧低层runtime不能进入生产main。当前新开仓仍由源码明确拒绝，拒绝原因是未验收的联动保护退出。
- `build_gold_au_integrated_bundle.py` 用明确审查的七模块SHA manifest构建单文件。模块命名空间隔离、3.12检查先于解码/导入/host调用、无运行时或授权注入、输出新私有文件。`AUDIT_APPROVED`只批准源码字节。
- `gold_au_operations_status.py` 输出已有证据的只读HTML/JSON，分开当前回执时效、历史状态和缺失；不能把协调器默认FLAT或未知仓位当真实空仓。官方已完成退出日线生产者位于本地`gold_au_official_exit_history.py`，通过真实外部reader向云端注入，不把本地研究pipeline搬进云端包。

已在既有Supabase项目实际应用`20260926081247_gold2_account_coordinator_v2.sql`，部署`gold2-paper-control`第2版。远端自动回滚探针成功，随后读取五张新表均0行；九张私有表RLS启用且anon/authenticated无SELECT，V1 claim执行权撤销。端点实测HTTP503 SERVICE_DISABLED。没有配置真实binding、发放执行密钥或启用委托。

## 必须保留的阻断

1. 正常交易窗口的SimNow只读回执尚未成功取得；账户标签与回读不是独立身份认证。
2. 优宽原生解释器仍3.9.2。既有3.12子进程纯核心成功不能替代原生API；工单5163待受理。宿主方案暂定既有云主机单一原生3.12 OMS，不新增双进程桥接。
3. 独立控制面身份、成本政策上界、平台订单ID到CTP原生ID、跨交易日成交/费用/结算档案及四方生产者尚无真实运行证明。独立reader和runtime必须隔离签名权，不能由同一未隔离进程自报四方一致。
4. native已确认开仓而四方证据缺失时，原开仓claim仍占账户。旧provisional平仓不能绕V2锁；尚需明确联动风险减仓和收讫服务不可用的恢复协议。此缺口未验收前连工程新开仓也不启用。
5. 真实PostgreSQL多连接竞争尚未验收；Node原子RPC oracle不是生产并发证据。

## 下一轮可验收成果

9月28日自然08:30研究与09:15–09:20唯一一次只读探针分别留真实回执。四个本地任务RunAtLoad=false，未自动补跑，当前runs=0；Mac离线记缺失。成本09:15到达不能回填08:30。

取得实际回读后补齐上述独立生产者；联动保护退出需覆盖原开仓确切终态/一手仓位、无挂单、原签名退出范围、永久去重、网络不明不重发、关闭后继续冻结新开仓及后续合并对账。完整工程合同通过后再验证一手开平、今/昨仓、拒撤单、重启和日结。成功工程单单独标记，不计策略投资样本。

正式开始时间只能在工程验收之后登记。运营观察30个日历日允许无信号；投资增量至少12个月且30笔独立入场，两者同时满足。蒙熊两次独立审核尚无完成回执，不用专家观点代替模型或成交真值。

依据：[优宽仓位常量](https://www.youquant.com/syntax-guide/var)、[Supabase私有函数权限](https://supabase.com/docs/guides/database/functions)。实际私有回执和运营页面保存在本轮独立输出目录，不投影账户或密钥进仓库。
