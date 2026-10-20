# RCN0 Replay #1 Industrial Distance Map v0.1

Replay: `RCN-REPLAY-20260820-CN-INNOVATIVE-DRUG-MRNA`

Status: `target_mapping_in_progress`

## 1. Definition

Industrial Distance `D_R` measures how many economically binding gates separate the external catalyst from a target's realizable cash flow.

`D_R` is not concept membership and not semantic similarity.

Minimum gates:

1. directly comparable technology/platform;
2. relevant product/pipeline;
3. IP/economic-right ownership;
4. clinical/regulatory stage;
5. commercialization rights/path;
6. order/revenue linkage;
7. profit/cash-flow recognition.

## 2. State vocabulary

No numeric score is authorized. Stock-level states are:

- `direct_or_near_direct`
- `intermediate`
- `far`
- `unresolved`

A target remains `unresolved` unless T0 evidence supports the required gates.

## 3. Current mapping by chain

### Near Narrative bucket | vaccine/mRNA mapping chain

Names frozen from T0 source:

百克生物 / 沃森生物 / 康华生物 / 悦康药业 / 康泰生物 / 智飞生物 / 康辰药业

Current D_R state: `unresolved_target_specific` for all seven.

Reason: the T0 source establishes strong **semantic** proximity to the `mRNA oncology` story but explicitly warns that the external Phase 3 success does not establish equivalent domestic individualized-neoantigen pipeline, IP/economic rights, regulatory stage or near-term earnings entitlement. Generic vaccine or mRNA labels are insufficient to call direct industrial exposure.

### Medium Narrative bucket | innovative-drug BD / pipeline chain

Recovered names:

泽璟制药 / 神州细胞 / 贝达药业 / 迈威生物 / 迪哲医药 / 复星医药 / 益方生物 / 科伦药业 / 荣昌生物 / 百济神州 / 微芯生物 / 恒瑞医药

Five source-declared names remain unresolved at universe-extraction level.

Current D_R state: `heterogeneous_unresolved`.

Reason: oncology and innovative-drug exposure makes the chain industrially closer to the disease domain than generic healthcare, but direct economic exposure to the specific personalized mRNA-neoadjuvant/adjuvant platform cannot be inferred from oncology membership. Target-level pipeline/right mapping is required.

Special T0 note: 恒瑞医药 has strong direct innovative-drug economics but same-day company-specific reality was negative due to earnings disappointment. This is industrial validation for its own portfolio, not direct economic exposure to the external mRNA catalyst.

### Farther Narrative bucket | CXO/service chain

泰格医药 / 凯莱英 / 昭衍新药 / 康龙化成 / 药明康德

Current D_R state: `intermediate_to_far_indirect` at chain level; stock-level mapping pending.

Reason: these companies can benefit from broader R&D/clinical/manufacturing demand without owning the therapeutic IP. T0 evidence shows actual order/profit validation, especially for 药明康德, but that validation is sector-service economics rather than direct ownership of the specific mRNA oncology asset.

## 4. Key distinction exposed by Replay #1

A target may have:

- `D_N = near` but `D_R = far/unresolved` — strong narrative mapping, weak direct industrial entitlement;
- `D_N = farther` but stronger contemporaneous operating validation — less story proximity, stronger current cash-flow evidence.

This is precisely the structure RCN0 is designed to expose.

## 5. Current D_R falsifier

H-RCN-02 fails if independent T0 evidence shows that the strongest near-bucket price leaders also possessed the strongest direct technology, economic-right, clinical and near-term commercialization exposure to the external mRNA catalyst.

Current source evidence does not establish that condition, but primary target-level mapping remains required before H-RCN-02 can be considered closed.

## 6. Completion requirements

For each of the 29 A-share targets, store:

`target / T0_source / technology_comparability / pipeline / rights / clinical_stage / regulatory_path / commercialization_right / current_revenue_link / current_profit_link / D_R_state / confidence / falsifier`

Until then: `D_R = BLOCKING_FOR_GOLD`.