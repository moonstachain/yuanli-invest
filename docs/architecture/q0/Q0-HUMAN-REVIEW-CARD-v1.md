# Q0 Human Review Card｜Yuanli Quant AI Equity Research System v1

Scope: architecture freeze only. No production authorization.

## Decision

Choose one:

- `ACCEPT_Q0_ARCHITECTURE_FREEZE`
- `ACCEPT_Q0_WITH_CHANGES`
- `REJECT_Q0_ARCHITECTURE`

## Seven required review questions

1. **Authority** — Is the four-repo split correct: `yuanli-invest` research Canon candidate, `quant-workspace` current operational quant plane, `yiru-macro-cockpit` provider only, `yuanli-invest-rsi` isolated challenger?
2. **P/N/X ontology** — Does the architecture preserve state/evidence logic and prohibit arbitrary scalar P×N×X scoring?
3. **Data truth** — Is Local/NAS Evidence Vault the correct raw-source boundary while GitHub stores contracts/metadata/hash/locator/reviewed objects?
4. **Agent design** — Is Manager + specialists-as-tools preferable to free-form multi-agent handoffs for auditability and cost control?
5. **Wind boundary** — Is Wind/Wind Alice correctly positioned as data/retrieval and Machine Evidence Analyst, not final Evidence Reviewer?
6. **30-asset MVP** — Is a 15 US + 15 China/HK coverage-first seed universe small enough to qualify deeply before scaling, and does it avoid implying recommendations?
7. **90-day sequence** — Is the order `data qualification -> point-in-time store -> evidence/narrative -> agents -> radar -> replay/eval -> shadow portfolio` correct, or should replay/eval move even earlier?

## Red-team questions

Reviewer should actively challenge:

- Are we overengineering with seven agents before a single-agent baseline is measured?
- Is N measurable enough to deserve its own engine, or does it risk becoming LLM sentiment theater?
- Does the 30-asset seed over-represent known AI winners and create survivorship bias?
- Are China point-in-time consensus/news histories truly obtainable under Wind licensing?
- Is `quant-workspace` legacy strategy code likely to contaminate the new evidence-first architecture?
- Are macro signals actually decision-relevant for P/N/X, or should the macro adapter stay optional?
- Does any proposed schema accidentally permit an agent to promote its own research state?

## Suggested acceptance conditions

If accepted, recommend adding these as Q1/Q2 hard checks rather than blocking Q0:

1. Add a separate control/counterexample set before predictive evaluation.
2. Establish single-agent baseline before proving multi-agent value.
3. Require exact Wind point-in-time coverage matrix before choosing historical estimate features.
4. Keep all seed Force states `unknown` until data qualification.
5. Do not promote Q0 candidate schemas into `packages/contracts/schemas/` until HG-Q0 receipt exists.

## Acceptance meaning

`ACCEPT_Q0_ARCHITECTURE_FREEZE` means only:

> The architecture is coherent enough for Codex to begin Q1 implementation through separate Draft PRs.

It does NOT mean:

- the 30 assets are approved investments;
- the Force Triangle predicts alpha;
- Evidence is admitted;
- A9 operational canon is switched;
- RSI FROZEN may change;
- any live trading system is authorized.
