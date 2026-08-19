# R1 Capability Lifecycle Rules v0.1

## 1. Capability maturity

```text
concept
→ specified
→ implemented
→ replicated
→ benchmark_passed
→ shadow_qualified
→ canon
→ deprecated
```

Transitions are directional by default. A failed review may return an object to an earlier state or deprecate it, but no state may be skipped without an explicit migration receipt.

## 2. Minimum evidence by transition

| Transition | Minimum evidence |
|---|---|
| concept → specified | theory/hypothesis linkage + input/output contract + failure regimes |
| specified → implemented | reference implementation + deterministic tests |
| implemented → replicated | independent or clean-room replication receipt |
| replicated → benchmark_passed | preregistered benchmark receipt, PIT/OOS rules satisfied |
| benchmark_passed → shadow_qualified | shadow runtime receipts across defined regimes |
| shadow_qualified → canon | Human Gate + exact-head CI + acceptance receipt |
| any → deprecated | reason + replacement/supersession pointer when available |

## 3. Object-specific states

`HypothesisObject` may use:

```text
proposed | preregistered | tested | supported | unsupported | mixed | deprecated
```

`TheoryObject` evidence status may use:

```text
primary_source_verified | replication_supported | survey_only | practitioner_claim | disputed | deprecated
```

These statuses do not imply Capability maturity.

## 4. No silent promotion

A registry edit cannot silently change maturity. Every promotion requires:

- from_state / to_state;
- triggering evidence/benchmark IDs;
- exact object revision;
- actor/runtime;
- timestamp;
- machine validation result;
- Human Gate when entering `canon`.

## 5. Fail closed

Missing provenance, missing PIT semantics, missing benchmark, broken provider mapping, invalid schema or stale reference means the Capability remains at the previous safe state.

## 6. Trading boundary

`canon` means: accepted research capability under the current Yuanli Research Capability Canon. It does **not** authorize target prices, buy/sell signals, position sizing, portfolio weights, broker actions or live execution.