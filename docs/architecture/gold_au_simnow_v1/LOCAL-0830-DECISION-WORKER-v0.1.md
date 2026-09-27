# GOLD2 AU｜08:30 本地只读决策时钟

`scripts/gold_au_decision_worker.py` 在北京时间工作日 08:30 调用现有 `LocalDecisionLog.capture()`，每个日期只允许一条记录。它读取私人运行目录的 `requests/YYYY-MM-DD.json`；请求缺失或身份无效时照样在日志中登记 `SKIPPED`，并在终端摘要中显示 `MISSING_DAILY_REQUEST` 或 `INVALID_DAILY_REQUEST`。它不连接优宽、不产生 ActionContract、不发送订单；本地 SQLite 哈希链也不是独立时间证明。

预先建立仅本人可读写的运行目录，再审阅 launchd 配置：

```bash
install -d -m 700 "$HOME/.yuanli/runtime/gold_au_decision"
.venv/bin/python scripts/install_gold_au_decision_schedule.py \
  --runtime-dir "$HOME/.yuanli/runtime/gold_au_decision"
```

`--activate` 才会加载 `com.yuanli.gold2-au-0830-research-decision`。该任务只在周一至周五 08:30 运行，`RunAtLoad=false`；非交易日若进入 worker，会通过官方日历输入缺失或不匹配被记为跳过。可用 `launchctl print gui/$(id -u)/com.yuanli.gold2-au-0830-research-decision` 读回加载状态。每天的完整记录位于私人 `gold_au_decisions.sqlite`；`logs` 仅含状态摘要/失败码。

同一私人目录还可运行 `scripts/install_gold_macro_capture_schedule.py`。它在工作日 08:10 将当时 FRED 分发的 `DFII10`、`DTWEXBGS` CSV 原文和捕获时点写入 `macro_captures/YYYY-MM-DD/`；当天目标已存在则拒绝覆盖。它不会把观测日当作发布时间，也不能替代美联储首发版本证明。2026-09-25 本机的两个只读 launchd 任务均已加载并从 `launchctl print` 读回，`runs=0`；首次计划触发还未发生，数据捕获结果未知。Mac 必须在触发时开机且用户会话可运行，失去执行时段应留下缺口，不能事后补写为前向捕获。

要取得 `READY_STRICT_RESEARCH_SIGNAL`，须在 08:30 前准备当天请求、最近 273 个正式交易日的上期所原始日报、当时捕获的 DFII10/H.10、正式交易日历、H.10 映射证明及当时费用/保证金回执。任一缺失会跳过；不能补采后回填当天事前信号。即使本地结果为 `READY`，也必须由独立系统在 08:30 分钟内锚定精确记录，且执行网关与 SimNow 运行时的其他门槛全部通过，才可考虑形成交易指令。本任务不向执行网关发送内容。
