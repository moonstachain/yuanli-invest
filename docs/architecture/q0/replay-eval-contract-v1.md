# Q0｜Replay / Eval Contract v1

Status: `architecture_freeze_candidate`

## 1. Purpose

The system is not accepted because its stories sound intelligent. It is accepted only if point-in-time replay, held-out evaluation and future settlement show measurable improvement without governance leakage.

## 2. Evaluation Layers

### E0 Contract / Safety

Hard gates; any failure blocks promotion.

- JSON Schema valid;
- prohibited trading fields absent;
- `scalar_score_prohibited = true`;
- every material claim has evidence IDs;
- `published_at <= as_of` in replay mode;
- same-day unresolved timestamps do not silently pass;
- required counterevidence/falsifier present;
- tool calls stay inside allow-list;
- input manifest hash and runtime profile recorded.

### E1 Evidence Fidelity

Question: did the model describe the source correctly?

Metrics:

- claim-support precision;
- wrong-locator rate;
- source-date error rate;
- circular-source rate;
- unsupported-claim rate;
- counterevidence recall on curated cases.

Gold adjudication remains human-supervised.

### E2 P/N/X Reconstruction Quality

Question: given only T0 information, does the system reconstruct disciplined states?

Current immutable seed Gold cases:

- PC / Netscape / 1995-08-09;
- Mobile / Apple / 2008-07-10;
- AI / NVIDIA / 2023-02-01.

Q1-Q6 target: expand `3 -> 30` cases with winners, losers, bubbles, survivors, incumbents disrupted, false positives and false negatives.

Metrics:

- exact state agreement where Gold exists;
- adjacent-state agreement for ordered stages;
- overclaim rate;
- `unknown` preservation rate when evidence is intentionally insufficient;
- hindsight leakage = 0 required.

### E3 Agent System Quality

Question: does multi-agent orchestration improve over a single-agent baseline?

Compare:

A. single reasoning model + same evidence;
B. CIO + P/N/X/Fundamental specialists;
C. B + Red Team;
D. C + Evidence Judge.

Measure:

- evidence fidelity delta;
- counterevidence recall delta;
- unsupported claim delta;
- token/cost/latency;
- Human Review correction rate;
- run failure / tool error rate.

Keep a simpler architecture if it performs as well.

### E4 Research Usefulness

Human reviewer labels each run:

- `decision_relevant`
- `useful_but_non_decisive`
- `noise`
- `misleading`

Track whether the system changes research priority for a reason the reviewer considers evidence-grounded.

### E5 Future Market Settlement

This layer is delayed and cannot be used to rewrite T0 inputs.

For explicit probabilistic claims, store pre-registered probability and settle with Brier / log-loss where appropriate.

For Force research candidates, track:

- false-positive rate;
- false-negative rate;
- survival after thesis break;
- realized fundamental confirmation/denial;
- right-tail capture relative to matched control set;
- drawdown and time-to-resolution for shadow/paper portfolios.

No single return metric can promote a methodology change.

## 3. Dataset Splits

```text
Gold Public Set      -> visible calibration / regression
Shadow Set           -> routine internal comparison
Held-out Private Set -> model/runtime promotion gate
Future Settlement    -> slowest, hardest-to-game score
```

RSI may consume only approved eval receipts and future settlement data through its own sandbox contract; Q0 does not modify RSI FROZEN.

## 4. Replay Input Manifest

Each replay freezes:

```json
{
  "replay_id": "...",
  "subject_id": "...",
  "t0": "...",
  "allowed_source_ids": [],
  "excluded_source_ids": [],
  "feature_snapshot_ids": [],
  "macro_snapshot_id": "...",
  "runtime_profile": "...",
  "prompt_contract_revision": "...",
  "schema_revisions": [],
  "input_manifest_hash": "...",
  "outcome_locked": true
}
```

## 5. Promotion Rules

A runtime/prompt/agent change can become `candidate_better` only if:

- E0 all pass;
- no regression on hindsight leakage;
- evidence fidelity is non-inferior;
- held-out score improves or materially lowers cost/latency with no quality loss;
- Red Team confirms no benchmark gaming;
- Human Review accepts the delta.

A `candidate_better` result is not Canon promotion.

## 6. Initial Q0 Eval Matrix

| Eval | Baseline | Candidate | Gate |
|---|---|---|---|
| schema/prohibited fields | deterministic validator | agent output | 100% pass |
| lookahead | A4/A5 validator | Q0 runtime | 0 leakage |
| evidence entailment | human-labelled sample | EvidenceJudge | target set in Q2 after baseline |
| P/N/X replay | A5 three cases | multi-agent | no worse than accepted candidate reconstruction |
| Red Team | CIO only | CIO + Red Team | must improve counterevidence recall |
| cost/latency | measured | measured | report, not optimize before quality |

## 7. Exit to Scale

Do not expand 30 seed assets to 300 until:

- 30-asset data completeness passes agreed threshold;
- point-in-time estimate/history coverage is verified;
- at least 30 replay cases exist;
- leakage remains zero on held-out checks;
- Human Review correction rate is trending down;
- paper/shadow pipeline can rerun deterministically from manifests.
