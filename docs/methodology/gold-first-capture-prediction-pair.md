# 黄金事前配对研究：Python与worker合同

本实现只产生研究证据，不连接交易账户，不声称首发版本、收益优势或可交易性。
当前生产来源时区尚未取得供应商证明，代码和合成测试不能解除来源资格门。
测试中的 `Europe/London` 是明确的合成工程记录，不是生产配置。

## 唯一结算格式

`daily_first_capture_v1` 成功回执使用 `direction`（整数 -1/0/1）、
`model_score`（整数 0/1）、`baseline_score`（整数 0/1）。
旧的 `realized_direction` 与嵌套 score 对象不作为该方法的第二种格式接受。
`future_settlement.py` 的严格方法保持原接口，两种方法不得混用。
方向用 Decimal 精确交叉乘积决定；正负0.5%的边界均为0。
显示的端点价格变化不是策略资金收益或实际成交收益。

## 自然采集与快照冻结

1. 一次读取三项原始返回：黄金10期，其余各5期；每项只读取一次。
2. `capture_once` 从黄金原始字节提取源时区中已完成的日期，保留精确日期、
   Decimal价格、原文与哈希，经 `capture_first_price` 保存；不发布、不结算。
3. `publish_receipt` 原样保留G6内容与授权来源声明的字节哈希，将
   `momentum_capture_complete` 和本批成功读回的 `momentum_capture_ids` 一并提交。
   缺省为false。失败批次不能用旧观测补成一个合格基准；原G6研究收据仍可保存。
4. Runtime决定数据库快照冻结截面与 `evidence_cutoff_at`，从已验证来源逐日期的
   earliest captures选取最新五个完整源日，冻结输入、方法版本和context哈希。
   本批ack可能是新raw产生的revision，因此匹配本批覆盖的源日，而不是要求
   earliest capture ID出现在本批ack中。Python不自行确定或提交动量方向。
5. `settle_due` 在冻结阶段之后处理到期判断，完全不再读取供应商。

只有具备供应商元数据证据的来源才可在Runtime注册为生产来源。主机调度时区、
可解析的IANA名称和数据库有效时区名称，都不能证明供应商日期的时区归属。
来源、单位、币种或时区改变时使用新来源身份，不回写历史。

## 配对wire与恢复

`list_due_claims` 保留原claim、registration、observations、settlement，增加：

```json
{
  "prediction_pair": {
    "pair_id": "...",
    "role": "human",
    "human_claim_id": "...",
    "momentum_claim_id": "...",
    "context_sha256": "...",
    "human": {"claim_id": "...", "claim": {}, "registration": {}, "settlement": null},
    "momentum": {"claim_id": "...", "claim": {}, "registration": {}, "settlement": null},
    "effective": false,
    "blocked_reason": "PAIR_NOT_BOTH_SETTLED"
  }
}
```

`record_settlement` 返回的claim view也包含更新后的pair。worker先完成本次所有
settlement，再生成learning；旧due视图不能覆盖后来的实际写入回执。
两条claim除身份及预测方向外必须冻结相同来源、版本、证据、日期、0.5%带与
不变基准。两条实际结算必须选择相同端点、方向和不变基准分数。

人工配对学习为 `gold-research-learning.v2 / comparison_receipt`，绑定两条实际
settlement哈希、context哈希、三项分数，`sample_count=1`，
`accepted_learning=false`，等待人确认。一个pair是一个预测事件，不自动证明
相互独立样本。动量学习为同版本 `internal_completion`，只使内部到期工作结束，
不能被当成人确认的第二份学习或第二个样本。
旧单条判断仍使用 `gold-research-learning.v1`。

原始claim和settlement的 `receipt_json / receipt_sha256` 在读回时直接验证，
不会重序列化既有字节或用新时钟重算已落库settlement。
人工已结算、动量未完成时只记录缺证attempt，保留人工在due队列；动量内部marker
即使先完成，仍通过pair元数据供后续人工比较引用。
学习写入失败时，下次使用原始已提交settlement恢复。
`NOT_DUE`、`INDETERMINATE_EVIDENCE`、`SYSTEM_ERROR` 均不是科学输赢结果。

## 验证范围

合成回归验证精确±0.5边界、原字节哈希、修订不替代首次记录、未完成日期过滤、
调用顺序、单次供应商读取、配对缺证、内部marker、部分成功与重启恢复。
完整Python→Edge→PostgreSQL验证需与Runtime及OS候选一并执行；
真实生产来源、自然调度、人工登记及到期结果必须另外取得实际回执，不能由
这些单测宣告完成。实现不启动调度器、不部署、不迁移数据库、不回填历史。
