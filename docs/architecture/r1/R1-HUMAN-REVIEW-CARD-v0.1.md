# R1 Human Review Card v0.1

Review only after exact-head `repository-gates` PASS.

## Decisions to review

1. **Object boundary** — accept Theory / Hypothesis / Factor / Algorithm / Benchmark / Skill / CanonicalDataField / ProviderAdapter / ResearchCapability as the formal R1 object set.
2. **ID law** — accept immutable semantic IDs and no ID recycling.
3. **Provider law** — accept that vendor-specific fields may exist only in ProviderAdapter; Factor/Algorithm/Capability depend on canonical economic fields.
4. **Lifecycle law** — accept `concept → specified → implemented → replicated → benchmark_passed → shadow_qualified → canon → deprecated` with no silent promotion.
5. **Canon law** — entering `canon` requires Human Gate and does not imply trading authority.
6. **Bootstrap law** — R1 registries begin empty; R0 12 seeds are not silently promoted. R2 performs the first Gold capability compilation.
7. **Existing-lane law** — Q1 / A6 / M1.2 governance state is unchanged by R1.

## Decision tokens

- `ACCEPT_R1_CAPABILITY_REGISTRY_BOOTSTRAP`
- `ACCEPT_R1_WITH_CHANGES`
- `REJECT_R1_CAPABILITY_REGISTRY_BOOTSTRAP`

Acceptance authorizes only `R2｜PNX-S Gold Capability Pack`. It does not authorize Evidence/Outcome admission, A9 operational-canon switch, RSI promotion, target prices, position sizing or live execution.