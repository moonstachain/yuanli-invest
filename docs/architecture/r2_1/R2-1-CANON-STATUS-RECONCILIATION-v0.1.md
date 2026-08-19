# R2.1｜Canon Status Reconciliation v0.1

## Purpose

R2.1 closes control-plane drift after R2 merge before any R3A runtime work begins.

It does four things only:

1. reconciles README human navigation with accepted/merged R0-R2 state;
2. closes R1 handoff and installs the R2 merge receipt;
3. creates `docs/architecture/CANON-STATUS.json` as the single machine-readable project-state projection;
4. reclassifies the stale M1.2 and Q1 lanes without carrying their old branch history forward as semantic authority.

R2.1 does **not** implement R3A, run Wind data, execute benchmarks, admit Evidence/Outcome, switch A9 operational canon, modify RSI FROZEN, or authorize trading.

## Canon status law

`README.md` is human navigation, not state authority.

Machine state precedence after R2.1:

```text
stage receipts / exact merge facts
        ↓
stage STATE files
        ↓
docs/architecture/CANON-STATUS.json
        ↓
README human projection
```

`CANON-STATUS.json` must fail closed if stage facts drift.

## Updated roadmap

```text
R2 MERGED
  ↓
R2.1 Canon Status Reconciliation
  ↓
R3A Gold Vertical Slice
  ├ P  Technology Cost Curve
  ├ N  Narrative Velocity
  ├ Xa Conditional Tail Activation
  └ V  Price-Implied Expectations
  ↓
Wind AI ↔ Codex ↔ Reference Quant Runtime
  ↓
R4A Benchmark Closure
  ↓
First Benchmark-Passed Capabilities
  ↓
Remaining Gold 8
  ↓
Shadow Qualification
  ↓
Capability Ratchet / RSI
```

No second Gold pack is authorized before at least the first vertical-slice capabilities receive real benchmark evidence.

## M1.2 governance closure

The old PR #16 remains valuable for runtime object design, but its semantic authority has been superseded by the R2 Constitution.

Its successor scope is:

> **Runtime State Contract**

It may define how a runtime research snapshot references:

- asset-level `Xs / Xa / Xp`;
- `V` price context;
- `IssuerDurability`;
- portfolio-level `S` as a separate object.

It may not redefine PNX-S ontology, create a scalar score, merge issuer durability into portfolio survival, or silently migrate historical replay.

The stale PR is to be closed as superseded; any successor must branch from current `main` after R2.1 merge.

## Q1 governance closure

The old PR #12 is no longer a data-foundation critical path. Its durable purpose is absorbed into:

> **Wind Provider Qualification**

The successor lane validates:

```text
CanonicalDataField
       ↓
Wind Provider Mapping
       ↓
PIT / revision semantics
       ↓
entitlement + legal storage boundary
       ↓
runtime compatibility receipt
```

A Wind API billing issue cannot block Theory / Factor / Algorithm / Capability Canon work. Wind AI manual/professional runtime may be used where lawful, while GitHub stores only provider-neutral contracts, mappings/locators and safe receipts.

The stale PR is to be closed as superseded; any successor must branch from current `main` after R2.1 merge.

## R3A authority

R3A is authorized only after R2.1 is Human Accepted and merged.

R3A should use vertical-slice-first rather than `12 capabilities × 2 runtimes` breadth-first implementation.

The first four slices are fixed for R3A planning:

1. `CAP-P-001-TECHNOLOGY-COST-CURVE`
2. `CAP-N-001-NARRATIVE-VELOCITY`
3. `CAP-XA-001-CONDITIONAL-TAIL-ACTIVATION`
4. `CAP-V-001-REVERSE-DCF-EXPECTATIONS`

For V, R3A must explicitly test whether the stable Capability identity should migrate in a future governed version toward **Price-Implied Expectations**, leaving Reverse DCF as one Algorithm rather than silently renaming the R2 object.

## Exit gate

R2.1 can pass only if:

- R2 merge receipt matches PR #19 / merge commit;
- R0/R1/R2 states are reconciled;
- README matches the canonical projection;
- M1.2/Q1 old lanes are recorded as superseded without deleting historical evidence;
- A9, Evidence/Outcome, RSI and live-execution boundaries remain unchanged;
- exact-head CI passes.

Human acceptance token after CI:

`ACCEPT_R2_1_CANON_STATUS_RECONCILIATION`
