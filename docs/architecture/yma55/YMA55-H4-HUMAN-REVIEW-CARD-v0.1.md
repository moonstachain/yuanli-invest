# YMA55-H4｜Reference Implementation & Replay Migration — Human Review Card v0.1

**Status:** `ready_for_human_review`  
**Machine status before this review:** `machine_qualified_reference_candidate`  
**Capital / trading authority:** none

## A｜H0.1 prerequisite — 3 checks

1. **PASS / FAIL** — YIM0 lifetime scope is frozen at its recorded semantic merge commit after merge, rather than drifting to current HEAD.
2. **PASS / FAIL** — Current YIM0 artifacts and authority are still validated; the repair does not weaken the original YIM0 scope allowlist or semantic guards.
3. **PASS / FAIL** — `repository-gates` run #408 proves governance + contracts + YIM0 validator + full unit tests pass after the repair.

## B｜H1 executable kernel — 4 checks

4. **PASS / FAIL** — Human runtime kernel is exactly `WORLD → CONSTRAINT → TRANSMISSION → MECHANISM → SETTLEMENT`.
5. **PASS / FAIL** — Runtime types preserve Constraint / Transmission / Mechanism / Settlement distinctions rather than collapsing them into one macro narrative.
6. **PASS / FAIL** — `MacroReturnMechanism != ReturnEngine`; H4 does not mutate ME0 `ENG-C / ENG-R / ENG-X` authority.
7. **PASS / FAIL** — Research outputs contain no Portfolio, sizing, buy/sell/hold, trading or execution authority.

## C｜H2 mechanism competition — 4 checks

8. **PASS / FAIL** — Every H4 candidate has one Primary, 1–3 genuine Alternatives and exactly one Null.
9. **PASS / FAIL** — Every candidate freezes causal chain, required conditions, expected observables, sequence, horizon, falsifiers and breaker at T0.
10. **PASS / FAIL** — Wrong-mechanism lucky outcomes are not scored as epistemic success merely because price direction was profitable.
11. **PASS / FAIL** — The system can preserve `UNRESOLVED`; it is not forced to make the Primary story win.

## D｜H3 transferability / violation — 4 checks

12. **PASS / FAIL** — Five transferability dimensions are structurally mandatory: monetary regime, fiscal capacity, market structure, global order, policy toolkit.
13. **PASS / FAIL** — Blocking mismatch can retire a current historical-prior application; non-transferable history cannot retain current authority.
14. **PASS / FAIL** — Surprise and Prior Violation remain distinct; violation is a research-state update, never a direct trade action.
15. **PASS / FAIL** — Sign, sequence, magnitude, persistence, policy-reaction and cross-asset-confirmation violation paths are executable in the reference evaluator.

## E｜Replay integrity / evidence honesty — 5 checks

16. **PASS / FAIL** — Genesis matrix is exactly `Duration × Credit × Scarcity × {GOLD, Near Miss, Wrong Mechanism, Wrong Strike}` = 12 cases.
17. **PASS / FAIL** — Settlement is physically excluded from T0 runner input and is attached only after frozen research state.
18. **PASS / FAIL** — All 12 current cases are explicitly `needs_primary_hydration` and `gold_qualified=false`.
19. **PASS / FAIL** — H4 `GOLD` is understood only as a positive-pattern replay role, not evidence-qualified historical Gold admission.
20. **PASS / FAIL** — Primary evidence hydration and blind replay are required before any candidate may be proposed for Gold / Hard-Negative admission.

## F｜Machine qualification — 3 checks

21. **PASS / FAIL** — H4 contract tests passed on run #414.
22. **PASS / FAIL** — Complete 12-case replay matrix and H4 validator passed on runs #431 and #433.
23. **PASS / FAIL** — Dedicated CI gate `python scripts/validate_yma55_h4_reference.py` passed after entry-path repair on run #437; governance and contracts both passed.

## Review threshold

`23/23 PASS` is required to accept H4 as a **reference implementation / replay candidate**.

Even `23/23 PASS` does **not** imply:

- historical Gold admission;
- Canon promotion;
- Engine Registry mutation;
- Portfolio authority;
- sizing;
- trading;
- live execution;
- merge authority.

## Recommended acceptance token

If and only if all 23 checks pass:

`ACCEPT_YMA55_H4_REFERENCE_IMPLEMENTATION_REPLAY_CANDIDATE`

After H4 acceptance, the next research battle should be:

`YMA55-H4.1｜Primary Evidence Hydration & Blind Replay Qualification`
