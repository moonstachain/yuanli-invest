# YHF-INV0｜Open Financial Intelligence Radar v0.1

> Status: `RESEARCH_CANDIDATE / HUMAN_REVIEW_REQUIRED`
>
> Scope: external benchmark/environment/model references for `yuanli-invest`. No live trading authority. No benchmark result may be interpreted as investment advice.

## 0. Strategic conclusion

The highest-value Hugging Face references for Yuanli Invest are **not stock-picking models**. They are methods for evaluating financial agents under realistic evidence and time constraints.

Priority order:

1. **FinQA OpenEnv** — tool-using financial environment;
2. **Finance Agent Benchmark** — expert-authored real-world research task taxonomy;
3. **FinIndices** — long-context structural/accounting reasoning and adversarial traps;
4. **Chronos-2 / TimesFM / MOMENT** — time-series challengers/baselines, not alpha authority.

## 1. Fit with current Yuanli Invest

The repository already requires:

- point-in-time evidence;
- preregistration;
- simpler baselines;
- walk-forward / OOS evaluation;
- held-out tests;
- future settlement;
- Human Gate;
- no acceptance merely because narratives sound intelligent.

Therefore Hugging Face should strengthen the existing replay/evaluation substrate, not replace the research philosophy.

## 2. Candidate A｜FinQA Environment

Source: https://huggingface.co/docs/openenv/environments/finqa

### What it does externally

FinQA evaluates agents that must inspect company financial tables, discover available tools, query SEC 10-K-derived data, calculate results, and submit answers in a bounded environment.

### Yuanli translation

Build a `Point-in-Time Research Environment` where the agent can only access data eligible at T0.

Candidate interface:

- `reset(case_id, T0)`
- `list_tools()`
- `query_evidence(source, as_of=T0)`
- `calculate()`
- `submit_research_candidate()`
- `state()`

All retrieved records must carry source/provenance/snapshot identifiers.

### Critical adaptation

FinQA has a numerical answer reward. Yuanli must support richer outcomes:

- evidence correctness;
- temporal integrity;
- reasoning trace quality;
- calibration;
- abstention when evidence is insufficient;
- survival/risk awareness.

State: `P0 / DESIGN_QUALIFIED`

## 3. Candidate B｜Finance Agent Benchmark

Sources:

- Paper: https://huggingface.co/papers/2508.00828
- Dataset: https://huggingface.co/datasets/vals-ai/finance_agent_benchmark

### External value

The benchmark uses expert-authored real-world finance research tasks based on recent SEC filings and a taxonomy built with practitioners from banks, hedge funds, and private equity.

### Yuanli use

Use it as a **task-taxonomy challenger**, not as the Yuanli test set.

Audit the Yuanli Golden Query taxonomy against at least these task families:

- evidence retrieval;
- calculation / reconciliation;
- financial statement interpretation;
- multi-document synthesis;
- modeling;
- scenario comparison;
- investment research memo support;
- missing-evidence abstention;
- auditability.

State: `P0 / TAXONOMY_REFERENCE`

## 4. Candidate C｜FinIndices

Source: https://huggingface.co/papers/2607.28661

### Why it matters

FinIndices exposes two failure classes highly relevant to Yuanli Invest:

1. **Knowledge Bottleneck** — formula/financial semantics are not reliably internalized;
2. **Structural Bottleneck** — reasoning degrades under multi-metric, multi-period, long-context table construction.

It also includes adversarial cases where the correct answer is insufficient information.

### Yuanli translation

Add a dedicated EBDD axis:

`Long-Horizon Structural Reasoning`

Required failure tests:

- wrong reporting period;
- cumulative vs standalone period confusion;
- stock vs flow mismatch;
- consolidated vs parent caliber mismatch where applicable;
- missing-report hallucination;
- adjacent-column shortcut;
- formula-without-evidence hallucination.

State: `P0 / EBDD_REFERENCE`

## 5. Candidate D｜Time-Series Foundation Models

### Chronos-2
https://huggingface.co/amazon/chronos-2

Open, Apache-2.0; supports univariate, multivariate and covariate-informed probabilistic forecasting.

### TimesFM
Candidate open checkpoints include:
https://huggingface.co/google/timesfm-2.5-200m-transformers

Important: later versions may use different licenses; license is a per-version hard gate.

### MOMENT
https://huggingface.co/AutonLab/MOMENT-1-base

Supports general time-series tasks such as forecasting, classification, anomaly detection and imputation.

### Yuanli role

These models are **challengers/baselines/features**, never direct investment authority.

Allowed uses:

- zero-shot forecast baseline;
- anomaly detection challenger;
- regime/feature comparison;
- forecasting ablation;
- model-diversity benchmark.

Forbidden inference:

> Better generic forecasting benchmark score ⇒ better investment decision.

State: `P1 / SANDBOX_ONLY`

## 6. P0 Battle｜YHF-INV0-PIT-ENV

### Goal

Prove that a bounded, point-in-time tool environment reduces look-ahead leakage and improves auditability versus unconstrained LLM research.

### Case pack

Start with 12 cases, not hundreds:

- 4 historical company cases;
- 4 cross-asset/macro cases;
- 2 missing-evidence cases;
- 2 adversarial temporal leakage cases.

Each case freezes:

- T0;
- eligible sources;
- prohibited future information;
- required calculations;
- baseline answer/research process;
- evaluation rubric;
- T1/T2 settlement evidence.

### Baselines

B0: unconstrained LLM with full prompt context

B1: existing Yuanli point-in-time replay path

C1: Yuanli PIT Environment candidate

### Primary metrics

1. `PIT_LEAKAGE_RATE`
2. `EVIDENCE_TRACE_COMPLETENESS`
3. `NUMERICAL_CORRECTNESS`
4. `STRUCTURAL_REASONING_SCORE`
5. `ABSTENTION_PRECISION`
6. `CALIBRATION`
7. `COST_PER_QUALIFIED_CASE`

### Hard fail

Any future-information leakage in a preregistered hard-negative case is a fail regardless of narrative quality.

### Pass condition

Candidate environment must:

- reduce PIT leakage versus B0;
- preserve or improve evidence correctness versus current baseline;
- expose every data/tool call in an auditable trace;
- abstain correctly on missing evidence;
- remain read-only / non-trading.

Target state:

`YHF-INV0-PIT-ENV = QUALIFIED / SHADOW_REPLAY_READY`

## 7. P1 Battle｜YHF-INV0-LONG-STRUCT

Use FinIndices-inspired cases to test long-context financial structure.

Minimum pack:

- 10 single-index/reconciliation tasks;
- 10 multi-period table tasks;
- 5 insufficient-information tasks;
- 5 adversarial accounting/period tasks.

Target:

`LONG_HORIZON_STRUCTURAL_REASONING_BENCHMARK_FROZEN`

## 8. P2 Battle｜YHF-INV0-TSFM-CHALLENGER

Compare Chronos-2, TimesFM and MOMENT against simple statistical baselines on a **non-trading** historical forecasting benchmark.

Required baselines:

- naive last value / drift where appropriate;
- moving average;
- simple AR/ETS baseline where appropriate.

No model advances if it only beats another foundation model but not the simple baseline after costs and stability are considered.

## 9. Adoption policy

### Adopt now as methodology references

- FinQA environment pattern
- Finance Agent Benchmark task taxonomy
- FinIndices adversarial structural reasoning concepts

### Sandbox only

- Chronos-2
- TimesFM
- MOMENT

### Explicitly prohibited at this stage

- live trade execution;
- autonomous portfolio changes;
- model-generated target prices treated as authority;
- training/evaluation leakage across historical cases.

## 10. Success criterion

The program wins when external HF methods make Yuanli Invest more **falsifiable, point-in-time clean, auditable, calibrated and reusable** — not when it adds more AI models.

Target program state:

`YHF-INV0 = EXTERNAL_FINANCIAL_EVAL_PATTERNS_QUALIFIED / REALITY_REPLAY_PENDING`
