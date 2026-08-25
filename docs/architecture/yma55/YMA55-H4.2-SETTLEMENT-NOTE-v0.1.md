# YMA55-H4.2｜Machine Qualification Settlement Note

Final machine-qualified head before Human Review:

`b50d536180d121747653b67ed89f447fc6699859`

Exact-head repository-gates run:

`#476 = SUCCESS`

Verified on that exact head:

- governance: PASS;
- contracts: PASS;
- `validate_yma55_h4_reference.py`: PASS;
- `validate_yma55_h4_1_qualification.py`: PASS;
- `validate_yma55_h4_2_benchmark.py`: PASS;
- full unit suite: PASS.

Machine state:

`machine_qualified_same_case_benchmark_candidate`

Primary settlement:

- B0 Naive Primary: `3/11`, hard-negative `0/8`, forced partial resolution = true;
- B1 Evidence-Gated Primary: `3/11`, hard-negative `0/8`, forced partial resolution = false;
- B2 Competing / No Breaker: `9/10`, hard-negative `6/8`;
- B3 H1+H2 Full Resolver: `10/11`, hard-negative `7/8`;
- B4 H1+H2+H3 Historical-Only: `10/11`, hard-negative `7/8`.

Epistemic settlement:

- evidence gating: supported as abstention discipline, not standalone mechanism-accuracy improvement;
- competing mechanisms: dominant measured increment within this constructed challenge set;
- falsifier/breaker/coverage: smaller positive increment within the challenge set;
- exact superiority versus pre-H1/H2/H3 YMA55: not established;
- H3 incremental contribution: not identifiable in historical-only replay;
- out-of-sample predictive superiority: not established.

Authority remains frozen. This settlement grants no Historical Gold admission, Canon promotion, Engine Registry mutation, Portfolio/sizing/signal/trading/live-execution authority, H4.3 execution authority, or merge authority.

Human Review remains separate and requires `20/20 PASS` under `YMA55-H4.2-HUMAN-REVIEW-CARD-v0.1.md` before the recommended acceptance token may be used.
