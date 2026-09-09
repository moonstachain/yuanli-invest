# YIOS-G1-A0｜Gold Genesis Case Constitution Freeze — Design

Date: 2026-09-09  
Status: `DESIGN_CANDIDATE / G0_HUMAN_ACCEPTANCE_REQUIRED`  
Parent architecture: `YIOS0 v1.0`  
Repository: `moonstachain/yuanli-invest`

## 0｜Purpose

YIOS-G1 is the first end-to-end Gold integration case for the accepted YIOS0 v1.0 mother loop:

`Reality → Knowledge → Trial → Settlement → Capital → Execution → Reality → Learning`

A0 freezes the experiment before any answer is run. It does **not** research Gold, unlock future data, settle a thesis, authorize capital, invoke VeighNa, connect a broker, or move real money.

Primary system question:

> Can YIOS0 take one Gold case from a strict historical point-in-time evidence boundary through a defeatable research claim, independent settlement, capital-admission logic, synthetic action translation, reconciliation, and learning without hindsight leakage or authority escalation?

A0 success means only:

`CASE_CONSTITUTION_FROZEN_CANDIDATE`

It does not mean:

`GOLD_THESIS_SUPPORTED`, `CAPITAL_PASS`, `EXECUTION_PASS`, or `TRADE_AUTHORIZED`.

---

## 1｜Two-clock law

This case uses two separate clocks.

### 1.1 Historical observation clock

Frozen decision cutoff:

`T0 = 2024-01-31T23:59:59-05:00 (America/New_York)`

Only evidence with:

`known_as_of <= T0`

may enter `GoldEvidencePack@T0`, `GoldState@T0`, or any candidate claim.

Market observations use the last official fix / close / published observation available on or before T0.

### 1.2 Experiment-governance clock

The protocol is designed in 2026 under YIOS0 v1.0 and may use existing YIOS0/YMQ4/YGR0 artifacts **only as protocol lineage, benchmark references, or hard negatives**.

2026 artifacts must never be injected into the historical T0 knowledge state.

In particular:

- YMQ4-B2 may be used as a protocol-side fixed-beta reference benchmark, but not as evidence that was historically known at T0.
- YMQ4-B3 may be used only as a governance / negative-evidence control; its 2026 result is forbidden from entering the T0 claim.
- YGR0 may be used as historical research-OS lineage, but may not rewrite the T0 evidence boundary.

Invariant:

`GOVERNANCE_KNOWLEDGE_2026 != HISTORICAL_KNOWLEDGE_AT_T0`

---

## 2｜Case identity

Stable identities:

```text
program_id: YIOS-G1
stage_id: YIOS-G1-A0
case_id: YIOS-GOLD-001
target_id: GOLD
architecture_version: YIOS0-1.0.0
case_type: END_TO_END_REALITY_LOOP_GENESIS_CASE
```

Primary claim identity to be tested later:

`GOLD_EARLY_MONETARY_REGIME_REPRICING`

The claim is a candidate research claim only. It does not imply a buy/sell/hold instruction.

---

## 3｜Evidence boundary

A future A1 Reality run must build a point-in-time evidence pack from eight domains:

1. `MONETARY_POLICY` — Fed policy stance, policy rate path, major central-bank policy.
2. `REAL_RATE` — real-yield curve / TIPS-derived real-rate evidence.
3. `USD` — broad dollar / DXY-equivalent market state.
4. `INFLATION` — CPI/PCE/breakeven evidence available at T0.
5. `OFFICIAL_DEMAND` — central-bank / official-sector Gold demand.
6. `PRIVATE_DEMAND` — ETF, China/India physical demand and other identifiable private channels.
7. `FISCAL_SOVEREIGN_CREDIBILITY` — deficit, debt-service, Treasury supply, reserve-diversification evidence.
8. `NARRATIVE_REFLEXIVITY` — contemporaneous market narrative, explicitly lower authority than primary factual data.

Each evidence object must carry at least:

```text
source_id
authority_level
observation_date
release_date
vintage_date
known_as_of
retrieved_at
revision_status
content_hash
```

### Authority hierarchy

- `A_PRIMARY`: official / first-party primary evidence.
- `B_MARKET_PRIMARY`: exchange, benchmark administrator, fund issuer, market-data primary source.
- `C_SECONDARY`: reputable secondary interpretation.
- `D_UNVERIFIED`: inadmissible for decisive claims.

A decisive scientific settlement may not be supported by `C_SECONDARY` alone. `D_UNVERIFIED` is never decisive evidence.

Future leakage count must equal zero.

---

## 4｜State Compiler contract

The future State Compiler must produce `GoldState@T0` with exactly these top-level state objects:

```text
IdentityState
RealityState
MonetaryState
PriceState
DemandState
NarrativeState
RegimeState
UnknownState
FalsifierState
AuthorityState
```

The State Compiler may summarize evidence; it may not invent evidence or decide the scientific outcome.

Candidate ontology labels are explicitly provisional:

```text
species_candidate: Monetary Scarcity
engine_candidate: S / R
state_candidate: Early Monetary-Regime Repricing
```

These labels have `RESEARCH_CANDIDATE` authority only until settlement.

---

## 5｜Baselines

The case freezes two baseline classes.

### B0｜Traditional Macro Baseline

Protocol-side baseline using only:

```text
gold_usd_oz
usd
inflation_yoy
real_rate
```

The frozen form is a fixed linear macro baseline. For comparability with existing YMQ4 lineage, the default training window is:

`1978-02-28 → 2006-12-31`

The B0 baseline is an evaluation benchmark. It is **not** evidence that a 2024 decision-maker had access to the later YMQ4-B2 receipt.

### B1｜Null / Price-Only Baseline

A simple intercept / historical-mean baseline is retained to prevent a complex candidate from winning only because the comparator is weak.

No baseline may be changed after A0 Human Acceptance.

---

## 6｜Pre-registered hypotheses

### H1｜OFFICIAL_DEMAND_STRUCTURAL — mandatory

Claim:

> Official-sector Gold demand remains structurally elevated rather than reverting to the pre-2020 norm.

The threshold is computed **only from data known at T0**:

`official_demand_threshold = P75(rolling_12m_official_net_purchases, 2010-01-01..2019-12-31)`

Support law:

- rolling-12m official net purchases at T+12M and T+24M are both above the frozen threshold.

Defeat law:

- either T+12M or T+24M is at or below the threshold, unless evidence authority is insufficient, in which case status is `INDETERMINATE`.

### H2｜TRADITIONAL_MACRO_DECOUPLING — mandatory

Claim:

> Gold produces persistent positive residual performance relative to the frozen traditional macro baseline.

For each settlement window, compute cumulative actual Gold return minus cumulative B0-implied return.

Support law:

- residual is positive in at least 3/4 settlement windows; and
- T+12M residual > 0; and
- T+24M residual > 0.

Defeat law:

- T+12M residual <= 0 or T+24M residual <= 0.

### H3｜PRICE_CONFIRMATION — mandatory

Claim:

> The candidate state is confirmed by durable, not one-off, price behavior.

Support law:

- cumulative Gold return from T0 is positive in at least 3/4 settlement windows; and
- T+12M return > 0; and
- T+24M return > 0.

Defeat law:

- T+12M return <= 0 or T+24M return <= 0.

### H4｜NARRATIVE_PRIVATE_DEMAND_BROADENING — exploratory / non-decisive

This hypothesis records whether private demand and market narrative broaden beyond official-sector demand. It may enrich Learning but cannot independently cause a primary `SUPPORTED` settlement.

---

## 7｜Primary scientific victory law

The primary claim `GOLD_EARLY_MONETARY_REGIME_REPRICING` is settled as:

### `SUPPORTED`

Only if all are true:

```text
H1 == SUPPORTED
H2 == SUPPORTED
H3 == SUPPORTED
no_hard_falsifier == true
PIT_integrity == PASS
```

### `PARTIALLY_SUPPORTED`

If evidence supports meaningful parts of the mechanism but one mandatory H1/H2/H3 condition fails without triggering a stronger falsifier, and the evidence remains sufficient to distinguish partial support from indeterminacy.

### `NOT_SUPPORTED`

If a mandatory H1/H2/H3 defeat law is triggered with sufficient evidence authority, or a hard scientific falsifier is triggered.

### `INDETERMINATE`

If decisive evidence is unavailable, non-PIT, materially conflicting, or below required authority.

Price appreciation alone can never produce `SUPPORTED`.

---

## 8｜Settlement windows

Calendar settlement cutoffs are frozen now:

```text
T+3M   = 2024-04-30T23:59:59-04:00
T+6M   = 2024-07-31T23:59:59-04:00
T+12M  = 2025-01-31T23:59:59-05:00
T+24M  = 2026-01-31T23:59:59-05:00
```

For a non-trading-day cutoff, market price uses the latest valid market observation on or before the cutoff. Economic data use the latest release whose `known_as_of` is on or before that settlement cutoff.

No future window may be dropped after results are opened.

---

## 9｜Metrics

### Scientific metrics

- H1 threshold result at T+12M / T+24M.
- cumulative Gold return at all four windows.
- cumulative B0 residual at all four windows.
- B0 and B1 RMSE / MAE over the sealed forward monthly evaluation period where mathematically applicable.
- sign accuracy is secondary only; it cannot override H1/H2/H3 defeat laws.

### System-integrity metrics

```text
future_leakage_count == 0
decisive_evidence_with_provenance == 100%
claim_has_pre_registered_defeat_condition == true
candidate_cannot_self_settle == true
research_authority_does_not_auto_promote == true
action_path_fail_closed_without_authority == true
historical_negative_evidence_not_rewritten == true
```

System success and scientific success are independent axes.

---

## 10｜Ablations

At least these ablations are frozen:

### ABL-1｜Remove Official Demand

Remove `OFFICIAL_DEMAND` from the explanatory state. Test whether the remaining traditional macro state can explain the sealed future outcome.

### ABL-2｜Remove Fiscal / Narrative Inputs

Remove `FISCAL_SOVEREIGN_CREDIBILITY` and `NARRATIVE_REFLEXIVITY`. Test whether the core H1/H2/H3 settlement changes.

### ABL-3｜Authority Downgrade

Replace decisive A/B evidence with C-level secondary evidence. Expected system behavior: settlement must downgrade to `INDETERMINATE` rather than preserve confidence.

### ABL-4｜B0-only Reconstruction

Use only the traditional macro baseline and compare with the full candidate state. This tests whether new explanatory dimensions add anything beyond legacy drivers.

No ablation result may retroactively alter the primary preregistration.

---

## 11｜Hard negatives

The following cases are preregistered as anti-cheating controls:

1. `PRICE_UP_ONLY` — Gold rises, but H1 or H2 fails. Primary claim must not pass.
2. `OFFICIAL_DEMAND_ONLY` — official demand stays elevated, but Gold does not decouple from B0. Primary claim must not pass.
3. `NARRATIVE_ONLY` — narrative becomes bullish without decisive factual support. Primary claim must not pass.
4. `POST_T0_LEAKAGE` — any future evidence enters T0 state. Case is invalidated / fail-closed.
5. `B2_B3_RETROJECTION` — 2026 YMQ4 B2/B3 outcomes enter T0 knowledge. Case is invalidated / fail-closed.
6. `NEGATIVE_EVIDENCE_REWRITE` — YMQ4-B3 scientific no-go is renamed or reframed as success. Governance failure.
7. `RESEARCH_TO_CAPITAL_AUTO_PROMOTION` — Research Settlement directly creates capital permission. Governance failure.
8. `RESEARCH_TO_EXECUTION_AUTO_PROMOTION` — Research Claim or Settlement directly creates broker/VeighNa action. Governance failure.

---

## 12｜Capital and action boundary

A0 authorizes **no capital action**.

Even after a future Research Settlement, the next allowed object is at most a **Shadow PositionPassport** after separate Human authorization.

A future synthetic action sequence, if separately authorized, is:

```text
ResearchSettlement
→ CapitalAdmission
→ Shadow PositionPassport
→ ExecutionIntent
→ Synthetic ActionContract
→ Authorization Firewall
→ Provider-Independent Synthetic Execution
→ Synthetic Reconciliation
→ Execution Settlement
```

Explicitly forbidden under A0:

```text
YVN1-A1 runtime
VeighNa installation / invocation
broker credentials
broker connection
Broker Paper
Live Execution
real capital movement
portfolio sizing authority
position sizing authority
automatic research-to-execution
```

---

## 13｜Learning law

Future Learning Delta must use:

```text
What We Believed
What Evidence Was Admissible
What Reality Did
What Survived
What Failed
What Changed
What Remains Unknown
```

Learning may change the future state. It may not rewrite T0 evidence, the preregistered hypotheses, thresholds, settlement windows, or failed claims.

Invariant:

`LEARNING_CAN_REVISE_FUTURE_STATE; LEARNING_CANNOT_REWRITE_CASE_HISTORY`

---

## 14｜Gates

### G0｜Case Constitution Acceptance

Required token:

`ACCEPT_GOLD_G1_CASE_CONSTITUTION`

G0 accepts only the frozen case design. It does not authorize the Reality trial.

### G1｜Reality Trial Authorization

Required later token:

`AUTHORIZE_GOLD_G1_REALITY_TRIAL`

Only after G1 may the system build the PIT evidence pack, compile `GoldState@T0`, execute the preregistered trial, and open the sealed future settlement windows.

### G2｜Research Settlement Acceptance

Required later token:

`ACCEPT_GOLD_G1_RESEARCH_SETTLEMENT`

This does not authorize capital.

### G3｜Shadow Capital / Action Trial

Required later token:

`AUTHORIZE_GOLD_G1_SHADOW_ACTION`

This may authorize only provider-independent synthetic capital/action testing unless a separate higher execution authority is explicitly granted in another governed program.

---

## 15｜A0 completion criteria

A0 is complete only when:

```text
T0 frozen
Evidence domains frozen
Authority hierarchy frozen
State schema frozen
Baselines frozen
Hypotheses frozen
Defeat conditions frozen
Settlement windows frozen
Metrics frozen
Ablations frozen
Hard negatives frozen
Capital / execution non-authorizations explicit
Human review card present
Draft PR open / unmerged
No future outcome opened
```

Machine-independent stage label before G0:

`YIOS_G1_A0_CASE_CONSTITUTION_CANDIDATE / AWAITING_G0_HUMAN_ACCEPTANCE`

---

## 16｜Central design decision

The key A0 decision is:

> Gold is used to validate whether YIOS0 can preserve point-in-time truth, allow a thesis to lose, keep research/capital/execution authority separate, and turn outcome into learning. Gold price appreciation is not itself the system victory condition.

Compressed law:

`SYSTEM_PASS != GOLD_BULLISH_OUTCOME`

and:

`PRICE_UP != THESIS_PROVEN != CAPITAL_AUTHORIZED != EXECUTION_AUTHORIZED`
