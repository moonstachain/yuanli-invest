# YIOS-G1-G1｜Machine Qualification Receipt — Gold Reality Trial

**Case:** `YIOS-GOLD-001`  
**Stage:** `YIOS-G1-G1`  
**Recorded:** 2026-09-09  
**Qualified implementation head:** `03d7d522c710d50d7da5efb00c8c0eb70c439e6b`  

## TDD evidence

### RED

- branch head: `853999d7971d713be178998c7df5f7762b8041ee`
- repository-gates: `#719` / run `34345253903`
- expected failure: `ModuleNotFoundError: No module named 'scripts.validate_yios_g1_gold_reality_trial'`
- governance remained green; contracts failed only at full unittest discovery because the production validator did not yet exist.

### GREEN

- branch head: `03d7d522c710d50d7da5efb00c8c0eb70c439e6b`
- repository-gates: `#727` / run `34346019361`
- conclusion: `success`
- governance: `success`
- contracts: `success`
- `python scripts/validate_yios_g1_gold_reality_trial.py`: `success`
- full unittest discovery: `success`

## Machine scientific readback

```text
PIT Integrity                         PASS
H1 Official Demand Structural         INDETERMINATE
H2 Traditional Macro Decoupling       SUPPORTED
H3 Price Confirmation                 SUPPORTED
H4 Narrative / Private Demand         EXPLORATORY_ONLY
Primary Research Settlement Candidate INDETERMINATE
Authority                             RESEARCH_SETTLEMENT_CANDIDATE_ONLY
```

The primary result remains `INDETERMINATE` because H1 is mandatory and its exact coherent T0-vintage 2010–2019 rolling-12m P75 threshold is not available with adequate evidence authority. No later-vintage patch is admitted.

## System-integrity qualification

The validator confirms:

- exact T0 unchanged;
- `known_as_of <= T0` preserved;
- zero post-T0 leakage into `GoldState@T0`;
- B2/B3 later outcomes not retrojected into T0;
- corrected forward window begins after T0;
- H2/H3 values are frozen and reproduced;
- price-up-only hard negative is rejected;
- `UNKNOWN = DENY` is enforced for H1;
- Candidate cannot self-settle;
- Research does not auto-promote to Capital or Execution.

## Non-authorizations

Still false:

- Capital Admission;
- PositionPassport / sizing authority;
- YVN1-A1 runtime;
- VeighNa installation / invocation;
- broker credentials / connection;
- Broker Paper;
- Live Execution;
- real capital movement;
- automatic research-to-execution.

## Current Gate

`YIOS_G1_G1_MACHINE_QUALIFIED / AWAITING_G2_HUMAN_RESEARCH_SETTLEMENT`

Required token:

`ACCEPT_GOLD_G1_RESEARCH_SETTLEMENT`

This token will not authorize Shadow Action; that remains separately gated by `AUTHORIZE_GOLD_G1_SHADOW_ACTION`.
