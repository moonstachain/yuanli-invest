# YF3N0-C｜三非前瞻预测与现实结算协议 v0.1

> 过去：历史回放告诉我们“它能解释什么”。  
> 现在：前瞻预注册要求它“在不知道答案时先下注自己的解释”。

# 预测不是事后解释

YF3N0-C 的目的不是证明“三非一定正确”，而是在未来结果未知时，提前冻结：

1. 今天知道什么；
2. 今天相信什么；
3. 什么事实会证明判断错误；
4. 未来用什么规则结算。

流程：

```text
Evidence Seal
    ↓
Atomic Prediction + Resolution Seal
    ↓
Future Evidence
    ↓
Blind Resolution
    ↓
Settlement
    ↓
Full vs Ablations vs Baseline
    ↓
Qualification
```

## 对人仍然叫“三非”

- **非理性痴迷**：长期被某类问题牵引；
- **非对称优势**：相对明确任务和参考群体的可验证差异；
- **非线性回报**：优势进入真实杠杆机制后的非比例潜在放大。

## 对机器使用更严格的因果本体

```text
PIP ∧ EAA ∧ NLP
```

- `PIP` = Persistent Intrinsic Pull；
- `EAA` = Evidenced Asymmetric Advantage；
- `NLP` = Nonlinear Leverage Potential。

三者是 **AND**，不是平均分。一个 primitive 被 `FALSIFIED`，不能因为另外两个很强就继续声称 `FULL_FORCE_CANDIDATE`。

## Triple Seal

### 1. Evidence Seal
冻结 evidence cutoff，之后的信息不能倒灌进最初判断。

### 2. Atomic Prediction + Resolution Seal
Prediction 与 Resolution Rule 必须在同一 preregistration timestamp 下原子封存。不能先预测，看到部分结果以后再改“怎么算对”。

### 3. Settlement
未来证据只能产生新的 append-only SettlementRecord，不能改写 sealed prediction。

## 五个比较模型

每个可比较事件必须让以下模型面对**同一个 outcome definition 和同一个 resolution rule**：

```text
FULL
ABLATE_PIP
ABLATE_EAA
ABLATE_NLP
BASELINE
```

这使我们能问：少掉任何“一非”以后，解释力是否真的下降。

## 两种结算通道

可清晰二元化的未来事件可以给概率，并用 Brier Score 结算。

机制型判断不强行伪量化，使用：

```text
SUPPORTED
PARTIALLY_SUPPORTED
FALSIFIED
INDETERMINATE
```

`INDETERMINATE` 是合法答案，不算支持、不算失败、不计算 Brier。

## 三个必选时间窗

```text
T90
T180
T365
```

`T730` 只有在最初 preregistration 时明确声明才可以存在，不能结果不理想以后临时延长观察期。

## 三非不是万能成功预测器

YF3N0 研究的是**主体内生的非平均价值生成机制**，不是所有财富和所有成功的统一预测器。

因此 YF3N0-C 不预测“谁一定成功”，而测试：

- PIP 是否真的带来更持久的投入；
- EAA 是否真的维持 benchmark-relative advantage；
- NLP 是否真的出现非比例放大机制；
- 三者同时成立是否比少一项的模型产生额外解释价值。

## v0.1 的硬边界

当前实现只包含机器合同、12 个空结构 slot、完全虚构 Gold fixture、Hard Negatives 和 validator。

```text
Real-case enrollment: NOT AUTHORIZED
Prediction clock start: NOT AUTHORIZED
Canon promotion: NOT AUTHORIZED
Merge: NOT AUTHORIZED
```

因此本版本**不会启动任何真实世界前瞻实验**。
