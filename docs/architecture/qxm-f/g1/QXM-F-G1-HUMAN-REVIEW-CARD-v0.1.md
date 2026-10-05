# QXM-F G1｜Selective Registry Admission — Human Review Card v0.1

Status: `ready_for_human_review_candidate`

Human Gate token if accepted:

`ACCEPT_QXM_F_G1_SELECTIVE_ADMISSION`

## 1. What this gate decides

G1 decides **identity admission only**. It asks which QXM2 Shadow TheoryObjects and Shadow HypothesisObjects deserve a formal Registry identity, and which Benchmark Seeds deserve to advance toward formal benchmark specification.

G1 does **not** preregister a hypothesis, execute a benchmark, promote a capability, activate runtime, or authorize trading.

The machine-generated candidate ledger contains exactly:

- 12 Shadow TheoryObjects;
- 12 Shadow HypothesisObjects;
- 6 Benchmark Seeds;
- 30 total objects.

All `human_disposition` fields remain `null` until this Human Gate.

## 2. Legal Human dispositions

For TheoryObject / HypothesisObject rows choose exactly one:

`ADMIT | ADMIT_WITH_BOUNDARY | KEEP_SHADOW | REJECT`

For BenchmarkSeed rows choose exactly one:

`FORMALIZE | DEFER | REJECT`

Human Acceptance of this card authorizes the accepted **identity dispositions** to be compiled in the next G1 apply step. It does not authorize G2 preregistration, benchmark execution, capability promotion, runtime activation, or trading.

## 3. Recommended disposition summary

### Fundamental Driver Decomposition

Recommended:
- both theory anchors: `ADMIT_WITH_BOUNDARY`;
- HYP-P-201 and HYP-P-202: `ADMIT_WITH_BOUNDARY` as `proposed` hypotheses only;
- benchmark seed: `FORMALIZE`.

Review question: does the combination preserve the distinction between analytical decomposition and causal driver identification, and does it require incremental value versus simpler headline-growth baselines?

### Three-Statement Integrity & Cash Conversion

Recommended:
- Dechow (1994) and Sloan (1996): `ADMIT_WITH_BOUNDARY`;
- HYP-P-203 and HYP-P-204: `ADMIT_WITH_BOUNDARY` as `proposed` hypotheses only;
- benchmark seed: `FORMALIZE`.

Review question: is the boundary strong enough that cash/earnings divergence cannot be silently converted into a fraud diagnostic or a universal mispricing signal?

### Credit & Balance-Sheet Transmission

Recommended:
- Bernanke–Gertler and Kiyotaki–Moore theory anchors: `ADMIT_WITH_BOUNDARY`;
- HYP-P-205 and HYP-P-206: `ADMIT_WITH_BOUNDARY` as `proposed` hypotheses only;
- benchmark seed: `FORMALIZE`.

Review question: does the admission preserve borrower/constraint-state mechanics and prohibit aggregate credit correlation from receiving causal-transmission authority?

### Opportunity-Cost / Discount-Rate Bridge

Recommended:
- Sharpe and Campbell–Shiller theory anchors: `ADMIT_WITH_BOUNDARY`;
- HYP-V-201 expectation decomposition: `ADMIT_WITH_BOUNDARY` as an interpretation/reconstruction hypothesis;
- HYP-V-202 OOS discount-rate prediction: **`KEEP_SHADOW`**;
- expectation-decomposition benchmark seed: `FORMALIZE`, explicitly interpretation-only.

Review question: is the `interpretation_only` result from QXM2 fully preserved? No row in this candidate pack requests predictive or timing authority.

### Stress Exit Liquidity

Recommended:
- Kyle and Brunnermeier–Pedersen: `ADMIT_WITH_BOUNDARY`;
- HYP-S-201 and HYP-S-202: `ADMIT_WITH_BOUNDARY` as `proposed` hypotheses only;
- benchmark seed: `FORMALIZE`.

Review question: does the pack preserve `ADV/spread != stress exitability` and leave room for later `DEFER` if credible stress/funding samples are insufficient?

### Return Source Attribution

Recommended:
- Brinson–Hood–Beebower and Campbell (1991): `ADMIT_WITH_BOUNDARY`;
- HYP-CROSS-201 and HYP-CROSS-202: `ADMIT_WITH_BOUNDARY` as `proposed` hypotheses only;
- benchmark seed: `FORMALIZE` using held-out ResearchReceipt/episode reconstruction and thesis-fidelity discrimination.

Review question: does the admission preserve `P&L identity != causal explanation`, and does it avoid forcing an attribution/learning capability into a forecasting benchmark?

## 4. Cross-pack epistemic review

Before accepting, verify all of the following:

1. Every admitted TheoryObject is being admitted as **theory ancestry with an explicit claim boundary**, not as proof that the corresponding capability works.
2. Every admitted HypothesisObject remains `status = proposed` in G1. `ADMIT` is not `preregistered`.
3. Every Benchmark Seed marked `FORMALIZE` remains a request to build a future BenchmarkObject; it is not a Benchmark PASS claim and does not authorize execution.
4. `CAP-R-01` and `CAP-V-01` remain mother capabilities with QXM profiles; G1 does not overwrite their mother semantics.
5. Discount-Rate Bridge remains interpretation-only; `HYP-V-202-OOS-DISCOUNT-RATE` is recommended `KEEP_SHADOW`.
6. No object derives authority merely from Qin Xiaoming practitioner material; Qin remains provenance/seed authority.
7. `Claim Authority <= Evidence Authority` remains satisfied for all 30 rows.
8. No target price, buy/sell/hold instruction, recommended weight, position size, broker action, live execution, or trading authority is introduced.

## 5. Recommended Human decision

Recommended decision: **ACCEPT WITH FROZEN BOUNDARIES**.

The candidate ledger is deliberately selective rather than blanket-promotional: 12 theory anchors are recommended `ADMIT_WITH_BOUNDARY`; 11 of 12 hypotheses are recommended `ADMIT_WITH_BOUNDARY`; the predictive discount-rate hypothesis remains `KEEP_SHADOW`; all six benchmark seeds are recommended for formal specification, not execution.

If accepted, the next governed action is G1 apply: write the accepted Theory/Hypothesis Registry pack while keeping hypotheses `proposed`, write the G1 Acceptance/Admission receipts, update Registry indices deterministically, run exact-head CI, and then stop for the separate merge authority `AUTHORIZE_QXM_F_G1_MERGE`.
