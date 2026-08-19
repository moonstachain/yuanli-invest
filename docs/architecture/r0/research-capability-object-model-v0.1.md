# Research Capability Object Model v0.1

## 1. Core object

`ResearchCapability` 是可被研究 Agent 调用、可被测试、可版本化的最小复用研究能力。

建议 ID：

```text
CAP-{DOMAIN}-{NNN}
```

Domain：`P | N | XS | XA | XP | V | S | E | CROSS`。

示例：`CAP-N-003-NARRATIVE-VELOCITY`。

## 2. Object graph

```text
TheoryObject ───────┐
PaperReference ─────┤
                    ▼
               Mechanism
                    ▼
            HypothesisObject
                    ▼
               FactorObject
                    ▼
             AlgorithmObject
                    ▼
          ResearchCapability
             ┌──────┴──────┐
             ▼             ▼
       BenchmarkObject   SkillContract
             │             │
             └──────┬──────┘
                    ▼
              Runtime Result
```

横向对象：

```text
CanonicalDataField ↔ ProviderAdapter
EvidenceReference
ReferenceImplementation
```

## 3. TheoryObject

回答：理论从哪里来，解释什么机制？

最低字段：

- `theory_id`
- `title`
- `authors`
- `year`
- `source_locator`
- `source_class`: original_paper / book / replication / survey / practitioner_claim
- `mechanisms`
- `pnxs_mapping`
- `claim_boundary`
- `evidence_status`

禁止把 practitioner claim 写成 established theory。

## 4. HypothesisObject

回答：理论如何变成可被数据推翻的命题？

最低字段：

- `hypothesis_id`
- `statement`
- `null_hypothesis`
- `target_variable`
- `horizon`
- `eligible_universe`
- `conditioning_state`
- `expected_direction`
- `falsification_rule`
- `point_in_time_requirement`
- `status`: proposed / preregistered / tested / supported / unsupported / mixed / deprecated

## 5. FactorObject

回答：理论中的机制如何被观测？

最低字段：

- `factor_id`
- `hypothesis_ids`
- `economic_mechanism`
- `formula_or_reference_algorithm`
- `canonical_input_fields`
- `frequency`
- `lookback`
- `publication_lag_rule`
- `expected_direction`
- `normalization`
- `neutralization`
- `known_failure_regimes`
- `missingness_policy`
- `reference_implementation`
- `benchmark_ids`

## 6. AlgorithmObject

回答：如何从输入推断状态、概率、尾部或 payoff？

最低字段：

- `algorithm_id`
- `algorithm_family`
- `research_question`
- `assumptions`
- `input_contract`
- `output_contract`
- `simpler_baselines`
- `known_failure_modes`
- `reference_sources`
- `reference_implementation`
- `test_contract`
- `benchmark_ids`

## 7. BenchmarkObject

回答：什么结果足以支持或否定该能力？

最低字段：

- `benchmark_id`
- `metric_set`
- `baseline`
- `split_method`
- `point_in_time_policy`
- `lookahead_prohibited`
- `multiple_testing_policy`
- `calibration_requirement`
- `regime_holdout`
- `acceptance_threshold`
- `complexity_penalty`

## 8. SkillContract

回答：Wind AI / Codex / Agent 如何调用？

最低字段：

- `skill_id`
- `capability_id`
- `runtime_class`: wind_ai / codex / reference_quant / generic_agent
- `input_schema`
- `output_schema`
- `data_requirements`
- `task_instructions`
- `prohibited_outputs`
- `failure_behavior`
- `version_pin`

## 9. CanonicalDataField

回答：算法真正需要的经济语义是什么，而不是某个 vendor 字段名是什么？

最低字段：

- `field_id`
- `canonical_name`
- `economic_definition`
- `unit`
- `frequency`
- `point_in_time_semantics`
- `revision_semantics`
- `allowed_transformations`
- `provider_mappings`

## 10. ResearchCapability

ResearchCapability 聚合而不复制上游对象：

```text
capability_id
name
domain
purpose
theory_ids
hypothesis_ids
factor_ids
algorithm_ids
benchmark_ids
canonical_input_fields
output_contract
skill_ids
reference_implementation
known_failure_regimes
maturity_state
```

候选 maturity：

```text
concept
specified
implemented
replicated
benchmark_passed
shadow_qualified
canon
 deprecated
```

其中 `canon` 不代表可交易；只代表该研究能力达成当前 Canon 接纳标准。

## 11. Anti-patterns

拒绝以下对象作为 Capability：

- 只有一个未经出处说明的公式；
- 只有 LLM prompt，没有输入/输出 contract；
- 只有历史收益，没有 point-in-time 与 benchmark；
- vendor-specific field 直接成为算法本体；
- 单一综合 PNX score；
- 无 falsifier 的“投资逻辑”；
- 把 feature importance / Granger lead 自动写成 causal effect。
