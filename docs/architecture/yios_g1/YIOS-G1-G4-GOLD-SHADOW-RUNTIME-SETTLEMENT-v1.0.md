# YIOS-G1-G4｜Gold Shadow Runtime Settlement v1.0

## Purpose

Validate the complete YIOS0 action boundary using Gold Genesis Case without granting real capital or execution authority.

## Frozen Principle

Research Settlement != Capital Admission != Execution Authority.

A successful research outcome cannot silently become a trade instruction.

## Runtime Flow

```
Research Settlement
        ↓
Capital Admission
        ↓
Shadow Position Passport
        ↓
Synthetic Action Contract
        ↓
Execution Shadow
        ↓
Four-Way Reconciliation
        ↓
Execution Settlement
        ↓
Learning Receipt
```

## Current Gold Settlement Input

Primary research settlement:

```
INDETERMINATE
```

Therefore:

- Capital Admission: DENY
- Position Sizing: NONE
- Real Execution: NOT AUTHORIZED

## Shadow Position Passport

Allowed:

- represent hypothetical decision state
- preserve research-to-action translation path
- test reconciliation contracts

Forbidden:

- portfolio mutation
- broker instruction
- order submission
- real capital movement

## Synthetic Action Contract

Execution mode:

```
shadow
```

Required invariant:

```
quantity_delta = 0
max_notional = 0
```

## Execution Settlement

Valid outcomes include:

- ACCEPTED_SHADOW_DECISION
- REJECTED_SHADOW_DECISION
- INDETERMINATE
- FAIL_CLOSED

A denial is a valid runtime outcome.

## Four-Way Reconciliation

The system must compare:

1. Capital Intent
2. Yuanli Execution Shadow
3. Execution Engine OMS
4. Broker/Custodian Reality

For this G4 case:

- Capital Intent: simulated match
- Yuanli Execution: simulated match
- Execution Engine OMS: not applicable
- Broker/Custodian: not applicable

## Non-Authorization

This document does not authorize:

- YVN1-A1 runtime
- VeighNa invocation
- broker credentials
- broker paper orders
- live execution
- real capital movement

## Learning Objective

The success condition is not profit.

The success condition is:

> Reality can update the system without allowing belief, research, or simulation to bypass authority boundaries.
