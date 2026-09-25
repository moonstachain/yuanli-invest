# 原力投研当前交接入口

从 [README](README.md) 的离线示例开始，随后阅读 [代码架构](ARCHITECTURE.md) 和 [工程审查](docs/architecture/engineering-simplification.md)。

当前已经实现黄金数据观察、每日变化比较、历史回归与漂移诊断、研究契约校验。完整的 Web 应用和到期判断结算不在本仓主线实现范围内。不要将方法论设计文档中的服务名当作已存在的运行接口。

```sh
python -m scripts.invest compare fixtures/ymq_gold2/demo-prior.json fixtures/ymq_gold2/demo-current.json
python -m scripts.invest status
python -m unittest discover -s tests -p 'test_*.py'
```

开发从实际输入/输出与测试开始。新增判断需明确证据时间和可检验条件；修改算法时保留历史结果，创建新运行记录。

研究语义与权限仍以对应配置及历史证据为准：[状态投影](docs/architecture/CANON-STATUS.json)、[研究方法](docs/os-vnext/README.md)。更早的交接记录保存在 Git 历史，`705dbed` 版本反映当时流程，不再作为今天的待办清单。
