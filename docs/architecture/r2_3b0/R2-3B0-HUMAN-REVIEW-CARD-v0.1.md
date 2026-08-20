# R2.3-B0 Human Review Card | Capability Contract Architecture Freeze

Current stage: `R2_3B0_CAPABILITY_CONTRACT_ARCHITECTURE_FREEZE`

Human Gate token:

`ACCEPT_R2_3B0_CAPABILITY_CONTRACT_ARCHITECTURE_FREEZE`

Acceptance does not imply merge.

## D1 | Universal contract architecture

Question: Does the candidate define one reusable `ResearchCapability` contract architecture without turning the Capability into a prompt, report, vendor schema, scalar score or trading action?

Expected PASS evidence:

- 11 mandatory blocks from identity through runtime/governance;
- stable research question as durable identity;
- algorithms may evolve without silently changing the question.

## D2 | Evidence and point-in-time discipline

Question: Are `as_of`, evidence cutoff, evidence authority, falsifier and point-in-time replay mandatory rather than optional prose?

Expected PASS evidence:

- `Claim Authority <= Evidence Authority`;
- event fact / mechanism hypothesis / expectation interpretation / asset attribution remain separately typed;
- future outcomes cannot leak backward into historical evidence.

## D3 | Provider-independent inputs

Question: Is economic meaning separated from Wind/vendor/native field names?

Expected PASS evidence:

- canonical input fields carry economic definitions, units, frequency, lag, revision semantics and missingness policy;
- provider mapping remains an adapter concern.

## D4 | Typed outputs / no scalar regression

Question: Does the output remain a typed multidimensional `ResearchState` rather than one Force/PNX/macro master score?

Expected PASS evidence:

- direction/magnitude/persistence/uncertainty can be typed where relevant;
- target price, recommended weight, buy/sell and execution remain prohibited canonical outputs.

## D5 | Falsification + fail closed

Question: Can the Capability lose authority when evidence, timing or regime validity degrades?

Expected PASS evidence:

- falsification rules, revision triggers, known failure regimes and degrade behavior are mandatory;
- valid fail-closed states include `insufficient_evidence`, `research_only`, `stale`, `unsupported`.

## D6 | Benchmark scientific discipline

Question: Does the contract force comparison against simpler baselines and prevent complexity from becoming self-justifying?

Expected PASS evidence:

- point-in-time / OOS policy;
- regime holdout;
- false-alarm accounting;
- calibration when probability is claimed;
- multiple-testing policy;
- complexity penalty and failure receipts.

## D7 | Settlement + learning

Question: Can every Capability be settled against future reality without hindsight rewriting?

Expected PASS evidence:

- settlement horizon, observables, rule, replay and revision rule are mandatory;
- point-in-time state is preserved.

## D8 | Invocation reproducibility

Question: Can every Wind/Codex/Agent result say exactly which Canon and Capability contract produced it?

Expected PASS evidence:

- mandatory `InvocationEnvelope` includes canon revision/hash, capability version, target, A0/A1, as_of, evidence cutoff and runtime;
- mandatory `ResearchReceipt` records algorithm family, evidence refs, output version and degrade state.

## D9 | P0 profile integrity

Question: Do CAP-R-01 / CAP-V-01 / CAP-XS-01 preserve the accepted R2.3-A semantics?

Expected PASS evidence:

- R remains `P.capital` decomposition, not fourth world;
- V is Price-Implied Expectations, not target-price ontology;
- Xs is Structural Asymmetry Source, with Value Control Point only an equity implementation.

## D10 | N-02 latency closure

Question: Does B0 close the reserved N-02 architecture requirement without inventing one arbitrary SLA for every asset?

Expected PASS evidence:

- typed SLA is mandatory;
- V/Xa/Xp re-underwrite is mandatory after expectation break;
- overdue reassessment degrades to `research_only` or `stale`;
- universal latency number remains unfrozen until calibrated by capability / asset / time sensitivity.

## D11 | Governance boundary

Question: Does B0 remain architecture freeze only?

Must remain false / unauthorized:

- Capability implementation;
- Capability promotion;
- benchmark execution;
- Evidence/Outcome admission;
- A9 operational switch;
- RSI promotion;
- target price;
- recommended weight / position size;
- buy/sell/live execution.

## Review disposition

Machine qualification must pass on the exact review head before Human Acceptance.
