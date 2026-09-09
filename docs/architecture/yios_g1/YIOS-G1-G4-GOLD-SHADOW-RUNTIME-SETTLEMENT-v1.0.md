# YIOS-G1-G4｜Gold Shadow Runtime Settlement v1.0

## Purpose

Validate the complete YIOS0 action boundary for the Gold Genesis Case after A0 Constitution, G1 Research Settlement, and G3 Shadow Action are physically present on protected main.

This stage validates governance and runtime fidelity. It does **not** validate investment performance and it does **not** create trading authority.

## Frozen Principle

`Research Settlement != Capital Admission != Execution Authority`

A successful or interesting research outcome cannot silently become a trade instruction.

## Canonical input

The accepted scientific input remains:

- PIT Integrity = `PASS`
- H1 Official Demand Structural = `INDETERMINATE`
- H2 Traditional Macro Decoupling = `SUPPORTED`
- H3 Price Confirmation = `SUPPORTED`
- Primary Gold Monetary-Regime Repricing claim = `INDETERMINATE`

Later Gold price performance cannot rewrite this settlement.

## Runtime flow

```text
Research Settlement
        ↓
Capital Admission
        ↓
Shadow Position State
        ↓
Synthetic Runtime
        ↓
Four-Way Reconciliation
        ↓
Execution Settlement
        ↓
Learning
```

## Fail-closed result

Because the mandatory scientific input remains `INDETERMINATE` and the frozen unknown semantics are `UNKNOWN = DENY`:

- Capital Admission = `DENY`
- max_notional = `0`
- max_loss = `0`
- quantity_delta = `0`
- runtime mode = `SHADOW`
- provider = `INTERNAL_SYNTHETIC_ONLY`
- OMS invocation = `false`
- broker invocation = `false`
- VeighNa invocation = `false`
- OrderSubmitted / OrderAccepted / PartialFillReceived / FillReceived = forbidden
- Execution Settlement = `FAIL_CLOSED`

A denial is a valid runtime outcome.

## Four-Way Reconciliation

The runtime must reconcile four surfaces even when external execution is intentionally absent:

1. Capital Intent → `MATCHED`
2. Yuanli Execution Shadow → `SIMULATED_MATCH`
3. Execution Engine OMS → `NOT_APPLICABLE`
4. Broker/Custodian Reality → `NOT_APPLICABLE`

No unexplained orders, fills, position deltas, or cash deltas are permitted.

## Machine evidence

- Runtime object: `config/yios_g1/gold_g4_shadow_runtime_settlement.v1.json`
- Validator: `scripts/validate_yios_g1_gold_shadow_runtime.py`
- Focused test: `tests/test_yios_g1_gold_shadow_runtime.py`
- Settlement receipt: `docs/architecture/yios_g1/YIOS-G1-G4-RUNTIME-SETTLEMENT-RECEIPT-v1.0.json`
- Learning delta: `docs/architecture/yios_g1/YIOS-G1-G4-LEARNING-DELTA-v1.0.md`

## Non-Authorization

No YVN1-A1 runtime.

No VeighNa installation or invocation.

No broker credentials or broker connection.

No broker paper orders.

No live execution.

No real capital movement.

No portfolio-weight or position-sizing authority.

No automatic research-to-execution.

## Settlement meaning

`FAIL_CLOSED_VALID` means the system faithfully propagated an unresolved research state through the Capital and Execution firewalls without manufacturing an executable action.

It does not mean Gold is unattractive, and it does not mean the research thesis is disproven. It means the system preserved its own evidence and authority laws.
