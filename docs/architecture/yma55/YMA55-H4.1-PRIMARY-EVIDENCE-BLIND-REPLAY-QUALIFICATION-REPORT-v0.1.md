# YMA55-H4.1｜Primary Evidence Hydration & Blind Replay Qualification

## Executive settlement

YMA55-H4.1 closes the first end-to-end evidence-and-blind-replay loop for the H1/H2/H3 causal-prior hardening architecture across Duration, Credit, and Scarcity.

The package contains 12 historical candidates: one positive-pattern role, one near miss, one wrong-mechanism challenge, and one wrong-strike challenge for each mechanism family.

The machine-qualified reference result is:

- 12 total cases;
- 11 fully hydrated at T0 under the E0 + independent E1 rule;
- 1 partial hydration: 1971 Gold;
- 10 post-unblinding mechanism matches;
- 1 mechanism mismatch: 2020 Gold;
- 1 evidence abstention: 1971 Gold;
- fully hydrated mechanism accuracy: 10/11;
- correct-or-safe-abstention outcome: 11/12.

This qualifies the blind replay pipeline as a reference candidate. It does **not** establish that H1/H2/H3 outperform the pre-H1/H2/H3 framework or a simpler baseline, because no same-case baseline has yet been frozen and replayed.

## 1. Evidence hydration discipline

The evidence layer was required to fail closed.

A case can reach `EVIDENCE_HYDRATED` only when at least one admissible E0 source and an independent E1 source are both available before the T0 cutoff. E3/E4 retrospective material is excluded from the blind resolver. Forward observations are stored behind a later resolver cutoff and cannot enter the initial T0 evidence pack.

The important negative result is 1971 Gold. It remained `PARTIAL_HYDRATION` because the available T0 pack did not satisfy the independent-E1 requirement. The system was not allowed to manufacture independence simply to make the matrix complete.

This matters because the epistemic objective is not maximum historical coverage. It is maximum truthful discrimination under evidence constraints.

## 2. Blind Resolution Freeze

Blind packets were stripped of historical case role, settlement, outcome class, role-bearing episode identifiers, and original fixture paths.

The resolver saw only opaque IDs `H41-B01` through `H41-B12`, the PIT-frozen competing hypotheses, and admitted evidence signals.

The role-blind outputs were committed and frozen at:

`805a5c52f6918c0f4339128ef5e95883de5fbf89`

The frozen output was then validated by recomputation from the blind packets alone. The freeze artifact is immutable after unblinding, and the post-resolution unblinding artifact did not exist at the freeze commit.

Frozen machine resolutions:

| Blind case | Resolution |
| --- | --- |
| H41-B01 | PRIMARY_LEADS |
| H41-B02 | ALTERNATIVE_LEADS |
| H41-B03 | ALTERNATIVE_LEADS |
| H41-B04 | ALTERNATIVE_LEADS |
| H41-B05 | PRIMARY_LEADS |
| H41-B06 | ALTERNATIVE_LEADS |
| H41-B07 | ALTERNATIVE_LEADS |
| H41-B08 | PRIMARY_LEADS |
| H41-B09 | INSUFFICIENT_EVIDENCE |
| H41-B10 | ALTERNATIVE_LEADS |
| H41-B11 | PRIMARY_LEADS |
| H41-B12 | ALTERNATIVE_LEADS |

## 3. Post-resolution unblinding

Only after the freeze passed CI was `sealed_mapping.json` used to reveal historical episode and challenge role.

The result was not scored mechanically by role. In particular, `WRONG_STRIKE` is not equivalent to “primary mechanism must be correct.” Some wrong-strike cases also contain a mechanism reversal. Therefore the post-resolution adjudication uses each episode's settlement mechanism resolution rather than the role label itself.

### Duration

- 1982 UST positive pattern: PRIMARY_LEADS — match.
- 1994 UST near miss: ALTERNATIVE_LEADS — match.
- 2008 UST wrong mechanism: ALTERNATIVE_LEADS — match.
- 2020 UST wrong strike: ALTERNATIVE_LEADS — match; reflation repricing displaced the low-rate duration primary, while expression/path risk remained separately relevant.

### Credit

- 2009 spread compression positive pattern: PRIMARY_LEADS — match.
- 2015 energy credit near miss: ALTERNATIVE_LEADS — match.
- 2020 Fed backstop wrong mechanism: ALTERNATIVE_LEADS — match.
- 2006 early subprime protection wrong strike: PRIMARY_LEADS — match; this is the cleanest thesis-correct / expression-wrong case.

### Scarcity

- 1971 Gold positive pattern: INSUFFICIENT_EVIDENCE — evidence abstention, not imputed as a win or loss.
- 2008 Oil near miss: ALTERNATIVE_LEADS — match.
- 2020 Gold wrong mechanism: PRIMARY_LEADS — mismatch.
- 1980 Gold wrong strike: ALTERNATIVE_LEADS — match.

## 4. The critical miss: 2020 Gold

The main failure in the first reference set is H41-B11.

The blind resolver selected the scarcity / monetary-expansion primary, while the post-resolution settlement favored the real-rate / liquidity alternative as the more material mechanism.

This is exactly the kind of error H2 was designed to expose: the asset direction can be right while causal attribution is wrong.

The failure must remain visible. It is not averaged away by the 10 successful discriminations.

The next research step should attack why the resolver over-weighted broad monetary-expansion signals relative to real-yield transmission and whether the evidence design, hypothesis observables, or scoring rule needs refinement.

## 5. What H1/H2/H3 have demonstrated

### H1｜Five-Layer Decision Kernel

Supported as an executable compression layer. The replay can preserve World → Constraint → Transmission → Mechanism → Settlement while still separating machine-level objects and expression outcomes.

### H2｜Competing Mechanism & Null Hypothesis

Strongly supported within this challenge set. The resolver selected an alternative in seven cases and primary in four fully resolved cases rather than mechanically validating the original thesis. The 2020 Gold mismatch also proves the framework can surface a wrong-mechanism failure rather than treating price direction as validation.

### H3｜Transferability × Prior Violation

The governance and runtime contracts remain intact and prevent historical replay from receiving capital authority. H4.1 primarily tests the evidence and competing-mechanism portion; it does not yet isolate H3's incremental contribution. A same-case ablation is still required.

## 6. What has **not** been proven

H4.1 does not prove any of the following:

- that H1/H2/H3 are superior to the old historical-analogy approach;
- that they beat a simple Growth/Inflation regime baseline;
- that they beat Market Clock only;
- that each of H1, H2, and H3 contributes independent incremental value;
- that 10/11 is an out-of-sample forecast accuracy estimate;
- that any case is admitted as Historical Gold;
- that any replay output has Portfolio, sizing, signal, or trading authority.

The 12 cases are a deliberately constructed reference challenge set, not an IID statistical sample.

## 7. Epistemic interpretation

The strongest result is not the raw 10/11 number.

It is that the system demonstrated three desired behaviors at once:

1. it discriminated Primary versus Alternative mechanisms across multiple hard negatives;
2. it preserved a visible mechanism miss instead of laundering a lucky direction into research success;
3. it refused to resolve 1971 Gold when evidence independence was inadequate.

Therefore the evidence supports the narrower claim:

> H1/H2/H3 form a credible mechanism-discrimination and anti-self-deception architecture within the first controlled challenge set.

The evidence does **not yet** support the stronger claim:

> H1/H2/H3 have proven incremental superiority over the previous Yuanli historical-replay method.

## 8. Authority freeze

H4.1 grants no authority for:

- Historical Gold admission;
- Constitution mutation;
- Engine Registry mutation;
- Canon promotion;
- Portfolio allocation;
- position sizing;
- buy/sell/hold signals;
- live execution;
- merge.

`Research PASS != Capital PASS` remains binding.

## 9. Recommended next gate — not authorized by this settlement

`YMA55-H4.2｜Same-Case Baseline Benchmark & H1/H2/H3 Ablation`

The next scientifically necessary question is not “add more episodes.” It is:

> On exactly the same historical cases and evidence cutoffs, how much incremental epistemic value comes from H1, H2, and H3 versus simpler baselines, and which component actually causes the improvement?

Until that baseline + ablation exists, `incremental_superiority = NOT_YET_ESTABLISHED` remains the correct state.
