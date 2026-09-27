# GOLD2 AU｜本地每日研究准备流水线

2026-09-26：四个 macOS 用户级定时任务已加载，均 `RunAtLoad=false`，本次安装未执行定时任务。它们只取得公开研究数据、保存本地证据和研究判断；不连接订单网关，不授予 PaperGrant。已加载不等于每日真实运行已验收。

| 北京时间 | 入口 | 产物与失败行为 |
|---|---|---|
| 08:05 | `gold_au_shfe_archive_worker.py` | 按经原文核验的上期所年度日历保留前 273 个交易日报告；最多补抓 5 日，08:10 后不接收新抓取。周末、休市先跳过；缺口更大、原文冲突或日期错误停止。 |
| 08:10 | `gold_macro_daily_worker.py` | 取得当日 FRED 分发的 DFII10、DTWEXBGS 原文，保存实际取得时间。工作日计时器可能在上期所节假日取得研究数据；不会由此生成交易日。 |
| 08:25 | `gold_au_daily_request.py` | 只读取显式来源目录和当日文件，逐项记录缺资料；全部核验通过才原子发布当日候选请求。 |
| 08:30 | `gold_au_decision_worker.py` | 重读来源并验证装配时冻结的回执哈希，保存研究判断。没有请求或输入不合格时留下 `SKIPPED` 记录。 |

本机必须在这些时点开机、唤醒、联网并保持用户会话。迟到不补造 08:30 决策；本地哈希链不等于独立外部时间见证。日历覆盖 2025、2026 年，未覆盖年份或未来期限拒绝使用；年度计划还须注意后续交易所调整。

## 私有来源与日文件

运行根目录为 `~/.yuanli/runtime/gold_au_decision`，权限 0700。`daily_request_sources.json` 指定：

```json
{
  "schema_version": "gold-au-daily-request-sources.v1",
  "calendar_receipt_path": "EXPLICIT_VERIFIED_OFFICIAL_CALENDAR_RECEIPT",
  "h10_mapping_receipt_path": "sources/h10-mapping-20260926/receipt.json",
  "cost_receipt_path": "cost_receipts/{decision_date}/receipt.json",
  "shfe_manifest_paths": ["shfe_archives/{decision_date}/manifest.json"]
}
```

日宏观文件必须为 `macro_captures/YYYY-MM-DD/manifest.json`，不替用前日文件。费用及保证金回执必须是决策当日上海日期取得的真实来源，包含指定合约实际适用条款和原文哈希；现阶段账户未连接，**该输入仍缺失，自动取得费用的桥接尚未实现**。不能用 SimNow 产品页的通用展示值填补账户条款。缺 WGC 首发证据维持未知、风险预算减半。

`shfe_archive_sources.json` 指定已核验日历及有界种子档。9 月 26 日已从既有官方原文离线准备 `shfe_seeds/2026-09-28/manifest.json`：前 273 日为 2025-08-13 至 2026-09-24，未发网络请求，保留每条原文最早真实取得时间。周一正常任务将另生成当天归档；种子不是周一已经执行的证明。

装配尝试保存在 `request_evidence/YYYY-MM-DD/<内容哈希>.json`。同日缺资料后可以补齐再产生新的不可变证据，但已发布的 `requests/YYYY-MM-DD.json` 不允许换成另一个候选。08:30 验证全部回执的完整清单及原文；存在修改、多余、遗漏或冲突即跳过。

## 安装与下一道门

在已配置私有目录、Python ≥3.12、上海时区的主机上：

```bash
.venv/bin/python scripts/install_gold_au_shfe_archive_schedule.py --runtime-dir "$GOLD_AU_RUNTIME" --activate
.venv/bin/python scripts/install_gold_macro_capture_schedule.py --runtime-dir "$GOLD_AU_RUNTIME" --activate
.venv/bin/python scripts/install_gold_au_daily_request_schedule.py --runtime-dir "$GOLD_AU_RUNTIME" --activate
.venv/bin/python scripts/install_gold_au_decision_schedule.py --runtime-dir "$GOLD_AU_RUNTIME" --activate
```

这里只用专用变量 `GOLD_AU_RUNTIME` 指向明确私有目录；安装器不执行研究或交易。各安装器不带 `--activate` 时仅生成任务文件。

下一次云端 CTP 只读检查预计 9 月 28 日 09:15；失败停止重复尝试，成功也不自动获得订单权。需要随后补齐当天适用成本、独立账户身份、持仓/委托/现金对账、七个真实交易端读回回调、签名网关与远端一次性认领，才能进入工程测试单和正式模拟盘。当前云端解释器版本问题另见[本轮回执](RESUME-RECEIPT-20260926.md)。30 天模拟盘观察尚未开始计时。
