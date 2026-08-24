# YMA55-H4.2｜Human Review Card

## Review object

`YMA55-H4.2｜Same-Case Baseline Benchmark & H1/H2/H3 Ablation`

Machine state before Human Review:

`machine_qualified_same_case_benchmark_candidate`

This review is about the epistemic settlement only. It does **not** authorize merge, Historical Gold admission, Canon promotion, Portfolio authority, sizing, signals, or trading.

## Review checks

### A. Experimental integrity

- [ ] A1. Exactly the same 12 H4.1 cases are used.
- [ ] A2. The same PIT evidence packets and settlement labels are reused across variants.
- [ ] A3. B0 is explicitly a naive-primary baseline, not mislabeled as an exact replica of old YMA55.
- [ ] A4. The challenge set is not presented as IID or out-of-sample.

### B. Result integrity

- [ ] B1. B0 result is preserved as `3/11`, hard-negative `0/8`, with forced partial-case resolution.
- [ ] B2. B1 result is preserved as `3/11`, hard-negative `0/8`, with the 1971 Gold abstention.
- [ ] B3. B2 result is preserved as `9/10`, hard-negative `6/8`, with two abstentions.
- [ ] B4. B3 result is preserved as `10/11`, hard-negative `7/8`, with one mismatch and one abstention.
- [ ] B5. B4 is identical to B3 in historical-only replay.
- [ ] B6. 2020 Gold remains visible as the critical mechanism mismatch.
- [ ] B7. 1971 Gold remains visible as the evidence abstention.

### C. Causal attribution discipline

- [ ] C1. Evidence gating is credited for abstention discipline, not mechanism-accuracy improvement.
- [ ] C2. Competing mechanisms are identified as the dominant measured increment within this challenge set.
- [ ] C3. Falsifier/breaker/coverage logic receives only the narrower additional contribution supported by B2→B3.
- [ ] C4. H1 individual numerical contribution is not claimed to be cleanly isolated.
- [ ] C5. H3 incremental contribution remains `NOT_IDENTIFIABLE_IN_HISTORICAL_ONLY_REPLAY`.

### D. Authority discipline

- [ ] D1. No exact old-YMA55 superiority claim is made.
- [ ] D2. No out-of-sample predictive claim is made.
- [ ] D3. No Historical Gold admission occurs.
- [ ] D4. No Canon or Engine Registry mutation occurs.
- [ ] D5. No Portfolio, sizing, signal, execution, or merge authority is granted.

## Threshold

Human Acceptance requires **20 / 20 PASS**.

Recommended acceptance token only if all checks pass:

`ACCEPT_YMA55_H4_2_SAME_CASE_BASELINE_ABLATION_SETTLEMENT`

## Next gate after acceptance — not authorized by this card

`YMA55-H4.3｜H3 Transferability & Prior-Violation Paired Challenge`
