# 原力投研 · Yuanli Invest

原力投研把数据、研究判断和复盘证据放在一起，回答：**现在观察到了什么、较上次有什么变化、还有什么不知道？**

当前可用能力是黄金三指标观察、每日变化比较、历史回归与漂移诊断，以及研究资料和契约校验。日常观察的研究标签部分沿用配置；它不是每日重新完成的估值或预测。此仓库没有 Web 前端或 HTTP 服务，`api/openapi.yaml` 是设计契约。

## 五分钟运行

需要 Python 3.12 或以上版本。从仓库根目录执行：

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt

# 无需账号、网络或生产数据的合成示例
.venv/bin/python -m scripts.invest compare \
  fixtures/ymq_gold2/demo-prior.json fixtures/ymq_gold2/demo-current.json

# 查看本地最新观察、数据截止时间、未知项和匹配的每日变化
.venv/bin/python -m scripts.invest status
```

示例结果：黄金变化 `+1.500%`、实际利率变化 `+12.00bp`、美元变化 `+1.000%`。示例文件标记为 `synthetic`，不代表市场数据或投资建议。

两个命令均为离线只读。加 `--json` 获取完整机器结果；`status --runtime-dir /path/to/runtime` 可读取指定目录。未找到回执时显示明确的空状态；学习回执损坏不遮蔽可读的观察结果。

## 使用真实数据

已有 Wind CLI 和运行配置的机器可运行：

```sh
.venv/bin/python -m scripts.ymq_gold2_live_shadow
```

它在现有试运行日期范围内，并行读取黄金、实际利率、美元三个指标，保存观察回执并调用每日变化计算。`WIND_MCP_CLI` 指定 Wind CLI；`YMQ_GOLD2_SHADOW_DIR` 指定本地运行目录。默认目录为 `~/.yuanli/runtime/ymq_gold2_live_shadow`。外部产品同步沿用已有配置，详情见 [运行配置](config/ymq_gold2/gold2_live_shadow.activation.v0.1.json) 和 [机器运行脚本](scripts/run_ymq_gold2_live_shadow_machine.sh)。

每次运行保存独立的 `YYYY-MM-DD/receipt-*.json`，`latest.json` 是原子更新的便捷快照。学习结果位于 `learning/`，以源回执哈希绑定本次观察。凭据和原始供应商数据不提交到仓库。

| 需要做什么 | 入口 |
|---|---|
| 查看状态、比较两日变化 | `python -m scripts.invest` |
| 获取黄金每日观察 | `python -m scripts.ymq_gold2_live_shadow` |
| 固定历史回归、漂移诊断、历史窗口回放 | `scripts/ymq4_b2_fixed_beta.py`、`scripts/ymq_gold2_property_drift.py`、`scripts/ymq_gold2_blind_replay.py` |
| 验证功能 | `python -m unittest discover -s tests -p 'test_*.py'` |
| 检查当前代码架构和改造依据 | [ARCHITECTURE.md](ARCHITECTURE.md)、[工程审查](docs/architecture/engineering-simplification.md) |
| 阅读研究方法与历史决策 | [方法论](docs/methodology/README.md)、[研究正典](docs/os-vnext/README.md) |

历史计算仍依赖其明确指定的数据面板和环境；未预注册判断的观察不评分。目前 G7 提供变化比较，完整的到期判断结算尚未在主线实现。

## 研究语义与历史兼容

研究正典：**Yuanli Investment Research Intelligence Canon / Research Capability Canon**。长期积累对象是 `ResearchCapability`。Compile investment knowledge into machine-callable research intelligence.

- 编译链：Theory → Mechanism → Hypothesis → Factor → Algorithm → Benchmark → Skill。
- Wind AI：Market Reality Runtime；Codex：Research Engineering Runtime。
- Current A9 operational canon：`moonstachain/quant-workspace`。
- GitHub **不是 Data Warehouse**；研究 `canon` 不代表可交易。
- Receipt = Ledger; Status = Projection。历史回执不随算法维护重写，状态投影可用 `python scripts/build_canon_status.py --check` 校验。

阶段沿革由 [状态投影](docs/architecture/CANON-STATUS.json) 与对应历史证据记录。当前操作从上面的实际命令开始，无需先学习战役代号或架构层数。
