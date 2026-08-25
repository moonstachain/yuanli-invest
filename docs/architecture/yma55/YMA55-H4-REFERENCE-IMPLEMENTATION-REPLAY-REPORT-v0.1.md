# YMA55-H4｜Reference Implementation & Controlled Gold/Hard-Negative Replay Migration v0.1

**Status:** `reference_candidate`  
**Date:** 2026-08-24  
**Repository:** `moonstachain/yuanli-invest`  
**Branch:** `yma55-h1-h3-causal-prior-hardening`  
**Capital / trading authority:** none

## 0. Mission

H4 is the first executable proof of the accepted H1/H2/H3 epistemic contracts.

It does **not** attempt to migrate the full 56-episode YMA55 universe. It deliberately constrains the first implementation to three mechanism families:

- `MRM-D | Duration`
- `MRM-CR | Credit`
- `MRM-SC | Scarcity`

Each mechanism has four replay roles:

- `GOLD` — intended positive-pattern candidate;
- `NEAR_MISS` — superficially similar case where the primary mechanism should not be accepted;
- `WRONG_MECHANISM` — price direction may look right while causal attribution is wrong or incomplete;
- `WRONG_STRIKE` — thesis may be intelligible while timing, price, carry, horizon or expression makes the position bad.

This produces the controlled Genesis matrix:

`3 mechanisms × 4 replay roles = 12 candidate episodes`.

**Important:** `GOLD` in this H4 matrix is a replay-role label only. It does not mean historical Gold admission. Every current H4 fixture is `needs_primary_hydration` and `gold_qualified=false`.

---

## 1. H0.1 prerequisite settlement

Before H4, the pre-existing YIM0 lifetime-scope CI bug was repaired.

YIM0 previously diffed its historical implementation base against current `HEAD`, so any legitimate post-YIM0 program appeared as a YIM0 scope violation. H0.1 now freezes YIM0 changed-path scope at its recorded semantic merge commit while continuing to validate current YIM0 authority and state artifacts.

Machine evidence:

- `repository-gates` run `#408`
- governance: PASS
- contracts: PASS
- YIM0 validator: PASS
- full unit test discovery: PASS

This repair changes no YIM0 semantic or authority boundary.

---

## 2. Executable H1 layer

H4 introduces `research_runtime.yma55` and preserves the H1 human kernel exactly:

```text
WORLD → CONSTRAINT → TRANSMISSION → MECHANISM → SETTLEMENT
```

The runtime includes immutable research objects for:

- World state;
- Structural constraint;
- Transmission state;
- Mechanism hypothesis;
- Mechanism hypothesis set;
- Transferability assessment;
- Prior violation record;
- Reality settlement.

The implementation does not replace ME0 `ENG-C / ENG-R / ENG-X` with macro mechanism families.

Invariant remains:

`MacroReturnMechanism != ReturnEngine`.

---

## 3. Executable H2 competition contract

The runtime fails closed unless every material hypothesis set has:

- exactly one `PRIMARY`;
- `1..3` `ALTERNATIVE` hypotheses;
- exactly one `NULL`;
- a PIT freeze;
- causal chain;
- required conditions;
- predicted observables;
- expected sequence and horizon;
- falsifiers;
- breaker;
- evidence references.

Normal causal-chain complexity is bounded to six nodes unless an explicit complexity exception exists.

This design makes `UNRESOLVED`, alternative-best-supported and null-best-supported outcomes structurally possible rather than forcing the primary story to win.

---

## 4. Executable H3 transferability and prior-violation contract

The runtime freezes all five transferability dimensions:

1. monetary regime;
2. fiscal capacity;
3. market structure;
4. global order;
5. policy toolkit.

Blocking structural mismatch forces `NON_TRANSFERABLE`.

The qualitative prior-violation evaluator distinguishes:

- not evaluable;
- surprise only;
- sign violation;
- sequence violation;
- magnitude violation;
- persistence violation;
- policy-reaction violation;
- cross-asset confirmation violation;
- no violation.

It produces research-state effects only. It has no `trade_action`, `position_size`, target weight or execution authority.

---

## 5. Replay isolation law

Each candidate fixture physically separates:

```text
T0 research packet
        │
        │ settlement unavailable
        ▼
Frozen Research State
        │
        ▼
Reality Settlement
```

`run_replay_case()` passes only:

- episode identity;
- mechanism family;
- replay role;
- as-of timestamp;
- evidence cutoff;
- evidence status;
- T0 five-layer inputs.

Settlement is only attached after the research state is frozen.

This prevents outcome leakage from silently contaminating the original thesis.

---

## 6. Genesis 12-case candidate matrix

| Mechanism | GOLD role | Near Miss | Wrong Mechanism | Wrong Strike |
|---|---|---|---|---|
| Duration | UST 1982 disinflation | UST 1994 tightening | UST 2008 crisis rally | UST 2020 zero-bound / reflation turn |
| Credit | 2009 spread compression | 2015 energy-credit stress | 2020 policy backstop | 2006 early subprime protection |
| Scarcity | Gold 1971 regime break | Oil 2008 demand collapse | Gold 2020 real-rate/liquidity competition | Gold 1980 parabolic peak |

These episode identities are **candidate research anchors**, not settled Gold episodes. Historical factual claims, exact T0 states, dates, sequencing and evidence roles must still be hydrated from primary/contemporaneous evidence before Gold admission.

---

## 7. What H4 proves now

H4 can already test whether the system architecture prevents these epistemic errors:

1. human compression deleting machine distinctions;
2. primary mechanism existing without genuine alternatives;
3. structural story existing without a null;
4. retrospective settlement leaking into T0;
5. a non-transferable prior retaining current authority;
6. a prior violation directly generating a trade action;
7. a profitable wrong-mechanism outcome being scored as epistemic success;
8. an unresolved case being force-resolved;
9. an unhydrated historical candidate claiming Gold qualification.

This is a **contract and replay-integrity proof**, not yet a proof that the chosen historical interpretations are correct.

---

## 8. Machine qualification evidence before dedicated CI gate

Observed green checkpoints:

- H0.1 repair: run `#408` PASS;
- H4 runtime contract: run `#414` PASS;
- prior-violation evaluator: run `#416` PASS;
- complete 12-case candidate replay matrix: run `#431` PASS;
- H4 fail-closed validator + hard-negative tests: run `#433` PASS.

A dedicated `validate_yma55_h4_reference.py` workflow step is added next; exact-head qualification after that step is the final machine gate for this battle.

---

## 9. Authority freeze

H4 grants no:

- historical Gold admission;
- Engine Registry admission or mutation;
- Canon promotion;
- Constitution mutation;
- Portfolio authority;
- position sizing;
- buy/sell/hold signal authority;
- trading;
- live execution;
- merge authority.

`Research PASS != Capital PASS` remains intact.

---

## 10. Next research gate after machine qualification

The correct next step is not to add more episodes.

It is:

### `YMA55-H4.1｜Primary Evidence Hydration & Blind Replay Qualification`

For the 12 candidates, hydrate contemporaneous and primary evidence, freeze source admission and publication-time semantics, then run blind mechanism discrimination. Only after those tests may any candidate be proposed for historical Gold / Hard-Negative admission.

The purpose of H4.1 is to answer:

> Did H1/H2/H3 merely create a more disciplined-looking schema, or do they actually distinguish mechanism, transferability, failure mode and wrong-strike cases better than the previous historical-analogy approach?
