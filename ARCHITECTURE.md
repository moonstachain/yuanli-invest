# Architecture

原力投研采用“GitHub 正典 + Evidence Vault 原文 + 双投影”的边界。

```text
公开来源 -> Evidence Vault -> SourceRecord / Evidence PR
行情双源 -> Raw / Parquet -> Observation / MarketSnapshot
审核事件 -> approved snapshot
                         +-> internal_full
                         +-> public_safe
Outcome / Replay -> LearningCandidate -> human-reviewed PR
```

## Repository responsibilities

- `packages/contracts`: JSON Schema、API envelope 与状态机契约。
- `packages/research-core`: 确定性计算与准入规则；Bootstrap 阶段只冻结接口。
- `canon`: 版本化研究对象，不允许覆盖历史版本。
- `events`: 每个审核事件一个不可变 JSON 文件。
- `projections`: `internal_full` 与 `public_safe` 的确定性生成器。
- `receipts`: exact-SHA 构建、发布与 Outcome 回执。
- `docs/methodology`: 研究方法与历史回放规范。

原始 PDF、Excel、网页快照、Parquet 与 DuckDB 不进入 Git。

## API boundary

内部 API 固定为只读查询和受约束 Copilot：

- `GET /api/v1/status`
- `GET /api/v1/narratives`
- `GET /api/v1/companies/{id}`
- `GET /api/v1/evidence/{id}`
- `GET /api/v1/theses`
- `GET /api/v1/replays/{id}`
- `POST /api/v1/copilot/query`

响应统一使用 `api-envelope` 契约。Copilot 不返回买卖、仓位、目标价或收益承诺。
