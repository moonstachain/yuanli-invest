# 原力投研代码架构

系统的工作是把外部数据转换为可复现的研究观察，保存当时证据，再向用户展示现状与变化。当前规模适合一个 Python 工程；没有拆成微服务、消息总线或通用工作流引擎的实际需求。

## 当前执行链

```text
Wind CLI ── 三路独立读取 ──> live_shadow.build_receipt
                                  │
                     校验指标身份、有限数、数据日期
                                  │
                     receipt_store.write_receipt
                                  │
                  learning_live.process_current_receipt
                                  │
                      每日变化 + 未知项 + 源哈希
                                  │
                    CLI status / 已有外部 product sink
```

| 内部职责 | 当前代码 | 对外约定 |
|---|---|---|
| 数据获取和规范化 | `scripts/ymq_gold2_live_shadow.py`、`scripts/ymq4_dp1b_backfill.py` | 外部错误在入口处理；不向下游传部分成功的三指标集合 |
| 研究计算 | `scripts/ymq_gold2_compiler.py`、`scripts/ymq_gold2_property_drift.py`、`scripts/ymq_gold2_learning_live.py` | 计算与网络分离；日期、阈值和研究标签显式；相同输入的计算结果可复现 |
| 回执存储 | `scripts/receipt_store.py` | 每次写入唯一文件；完整 JSON 原子替换 latest；历史记录保留 |
| 用户呈现 | `scripts/invest.py`、已有 product sink | 从同一回执读取，展示状态、日期、变化与未知项；学习必须与源回执匹配 |

现有脚本命令和 JSON 字段继续兼容。方法论平面保留在 `docs/os-vnext/` 和 `docs/architecture/yios0/`；它们是研究语义与历史设计资料，不等同于已部署服务。

## 简化原则

1. 验证外部输入与持久化边界，内部已检查的数据直接计算。独立可调用的公共计算函数仍自行验证输入。
2. 只有两个实际调用方需要时才抽公共能力：观察回执和学习回执共用一次存储实现；不添加通用 repository/factory/event-bus 层。
3. 冻结实验与持续观察分开理解。固定 B2 窗口有科学意义，不能在性能改造中延长实验窗口、重写历史结论。
4. 状态是数据投影。`latest.json` 可重建，源回执保留；产品只引用与本次观察绑定的学习结果。
5. 测试计算结果、真实输入错误、写入失败和用户入口；CI 对已有完整集成测试覆盖的校验器只执行一次。

## 后续结构

继续演进时，将上述四项职责整理到一个正式 `yuanli_invest` 包：`observations`、`research`、`receipts`、`cli`。仅当第二个真实运行方需要替换实现时增加 adapter interface；现阶段保留脚本导入路径，避免以改名代替实质改进。

下一个功能缺口是明确的判断到期结算：判断包含作出时间、证据、可检验条件和到期时间；结果引用原判断与实际观察。它应作为研究计算的一部分，并让呈现层显示“待验证 / 支持 / 不支持 / 证据不足”。当前 G7 的 `PENDING_FUTURE_HORIZON` 不代表已经完成这一能力。

工程发现、已修项、测试与性能证据见 [工程审查](docs/architecture/engineering-simplification.md)。
