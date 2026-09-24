# Gold Future Settlement — offline candidate v0.1

This candidate closes the mechanical gap between a supplied preregistered claim
and a matured research outcome. Existing G6/G7 scheduling and activation contracts
are unchanged. It is not a registered ResearchCapability, accepted learning,
production deployment, or an investment-effectiveness result.

## Run the engineering example

From the repository root, with Python 3.12 or later:

```sh
python scripts/ymq_gold2_future_settlement.py --input fixtures/ymq_gold2/future_settlement.synthetic.v1.json
python -m unittest tests.test_ymq_gold2_future_settlement -v
```

The supplied fixture is `SYNTHETIC_ENGINEERING_ONLY`, including the claim,
registry receipt, source prices, and hashes. The illustrative 2% return is not a
market observation, prospective forecast, investment return, or real success.

## Contract

Inputs are separate claim, preregistration and observation objects. The claim
freezes its capability version, target, exact series, currency, unit, T0, exact
horizon end, decision-evidence cutoff, model direction, baseline direction and
neutral-return band. Decimal arithmetic classifies the exact neutral-band
boundaries; the JSON numeric return is for display, and its decimal string
is also included. Direction values are -1, 0 and 1. No trading calendar or
nearby observation is substituted: an absent exact endpoint stays indeterminate.

The preregistration references an external registry record and binds the entire
claim by canonical SHA256. Decision evidence must be known by the registry recorded time, which must
not exceed T0. Explicit registry/source kinds separate fixture declarations
from external record declarations; neither self-authenticates a real record. All timestamps require an explicit timezone. Observation clocks
must satisfy `observed_at <= available_at <= captured_at <= settlement_as_of`.
Both endpoints must match the frozen identity and be first-release observations.
Revisions cannot replace an absent original or overwrite a settled measurement.
Conflicting first releases fail closed. Missing data do not count as losses or wins.

The deterministic receipt distinguishes `NOT_DUE`, `INDETERMINATE_EVIDENCE` and
`SETTLED_RESEARCH_CANDIDATE`. Invalid inputs produce `FAIL_CLOSED` and CLI exit 2.
Direction scores compare the same simple price return against the two separately
frozen directions. It reports no P&L, sizing, costs, alpha or statistical significance.

## Trust and integration boundary

A local hash verifies record consistency, not external authorship, historical
publication or timestamp authenticity. Every receipt therefore retains
`preregistration_verification=EXTERNAL_READBACK_REQUIRED`,
`observation_verification=EXTERNAL_READBACK_REQUIRED`,
`source_authenticity=UNVERIFIED`, and all learning,
capital, sizing, execution, broker and Canon authorities remain false. A supplied
JSON record can be forged; independently read back its registry entry and raw
source evidence before accepting any real result.

There is deliberately no claim generator, external provider call, database
write, scheduler hook or automatic promotion. A real pilot next needs immutable
registry readback, provider-specific point-in-time adapters, a sample-level
benchmark report including missing observations, and an independent acceptance
receipt. Directional correctness alone cannot settle the existing H1 official
demand / monetary-regime thesis, which remains separately governed.

## Verification

19 adversarial unit tests cover matured scoring, pre-horizon outcome injection,
late registration, post-T0 decision evidence, claim tampering, series/currency/
unit/endpoint mismatch, release/capture availability, missing initial releases,
revision contamination, conflicting first releases, invalid numbers, invalid
clocks, missing preregistration, mixed synthetic/real evidence, timezones and
deterministic replay. The full suite passed 308 tests at the source snapshot
`705dbedf8866453f12d42dde58dbd95dbc032ee7` plus this local candidate.

## Narrow G6/G7 input hardening in the same candidate

G6 now rejects nonnumeric, boolean and nonfinite observations before producing
a successful receipt. G7 rejects nonfinite values and verifies each individual
metric date is at or before both the receipt as-of date and declared maximum
known-as-of date. Six additional tests cover malformed/future individual dates,
nonfinite values and compatibility with legitimately differing observation dates.
No freshness TTL, market calendar, model state, deployment or authority field
was changed. Stale data remain a separate domain-policy backlog item.
