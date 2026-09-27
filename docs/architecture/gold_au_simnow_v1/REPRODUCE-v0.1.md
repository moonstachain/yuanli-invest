# GOLD2-AU-V1｜本轮研究复算

从本仓工作树根目录执行。原始响应与研究输出在仓外同级目录 `../outputs/`；每次写入使用新的输出目录，不覆盖旧证据。命令只读已采集的市场文件并生成研究报告，不接入账户或发单。先建立 Python 环境并安装本仓依赖，例如 `python3 -m venv .venv` 和 `.venv/bin/python -m pip install -e '.[dev]'`。

```sh
.venv/bin/python scripts/gold_au_shfe_merge.py \
  --provider-manifest ../outputs/gold-au-history-shanghai-boundary-2026-09-25/manifest.json \
  --shfe-manifest ../outputs/gold-au-shfe-repair-2019-2021-20260925/manifest.json \
  --shfe-manifest ../outputs/gold-au-shfe-repair-2021-2023-20260925/manifest.json \
  --shfe-manifest ../outputs/gold-au-shfe-repair-2023-2026-20260925/manifest.json \
  --output-dir ../outputs/gold-au-shfe-full-replay --execute

.venv/bin/python scripts/gold_au_dataset_assemble.py \
  --au-manifest ../outputs/gold-au-history-shanghai-boundary-2026-09-25/manifest.json \
  --macro-manifest ../outputs/gold-macro-20260925-curl/manifest.json \
  --shfe-manifest ../outputs/gold-au-shfe-full-replay/manifest.json \
  --audit-report ../outputs/gold-au-shfe-audit-boundary-corrected-2026-09-25/report.json \
  --output-dir ../outputs/gold-au-assembled-replay --execute

.venv/bin/python scripts/gold_au_attribution.py \
  --dataset ../outputs/gold-au-assembled-replay/dataset.json \
  --assembly-report ../outputs/gold-au-assembled-replay/report.json \
  --output ../outputs/gold-au-assembled-replay/attribution-exploratory.json

.venv/bin/python scripts/gold_au_backtest.py \
  --input ../outputs/gold-au-assembled-replay/dataset.json \
  --pit-mode reconstructed \
  --output ../outputs/gold-au-assembled-replay/backtest-exploratory.json

.venv/bin/python scripts/gold_au_backtest.py \
  --input ../outputs/gold-au-assembled-replay/dataset.json \
  --pit-mode strict \
  --output ../outputs/gold-au-assembled-replay/backtest-strict-denied.json
```

这条链会校验 89 份优宽逐合约原始响应、两份宏观原始响应与 1,759 份可读取的上期所日报。20 个上期所 HTTP 错误日期和优宽周末标签保持隔离；缺首发版本、官方交易日历独立核验、盘中成交与账户成本，所以结果仍是 `DATA_QUALITY_BLOCKED_EXPLORATORY`。`strict` 模式应为零笔，不能把 `reconstructed` 的账面收益称为事前交易成绩。确切的最终文件 SHA-256 见[实施回执](IMPLEMENTATION-RECEIPT-20260925.md)。

日常前向模式需要另外取得上一已完成交易日的上期所日报、两项宏观捕获、正式交易日历和费用读回的原始回执；`scripts/gold_au_live_snapshot.py --help` 给出本地只读快照输入。若任何证据缺失，产出跳过而非自动补旧值。仅运行这些命令不会启动优宽、SimNow 或 PaperGrant。
