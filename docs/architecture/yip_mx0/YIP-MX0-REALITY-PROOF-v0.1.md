# YIP-MX0｜Miaoxiang API Reality Proof × Gold Golden Query

## Authority
- Provider: Eastmoney Miaoxiang (`mx-ds-mcp`)
- Provider authority: `EVIDENCE_ONLY`
- Research: authorized
- Capital / sizing / execution / broker action / Canon promotion: **not authorized**
- Credential: runtime-only through `EM_API_KEY` or macOS Keychain; never committed to Git
- Raw provider payloads: private runtime only; never committed to Git

## 2026-09-17 Reality Proof
- MCP authentication: PASS
- Server: `mx-ds-mcp` v1.0.0
- Discovered MCP tools: 11
- Golden tool: `mx_macro_data`
- Latest known date returned: 2026-09-16

## Gold Triangle Readback
| Driver | Miaoxiang | Wind shadow | State |
|---|---:|---:|---|
| London gold | 4263 USD/oz | 4328.2 USD/oz | semantic reconciliation required |
| DXY | 100.321 | 100.3293 | aligned (<0.01% gap) |
| US real yield | tenor points: 10Y 2.68%, 20Y 2.93%, 30Y 3.09% | >10Y average 3.06% | not directly comparable |

The gold gap is preserved as evidence. No provider failure is inferred from the gap alone. The two labels are similar but the observation/fixing convention is not yet proven identical.

## Admission Decision
`MIAOXIANG_API_REALITY_PROOF = PASS`

`GOLD_PROVIDER_SEMANTIC_EQUIVALENCE = NOT_PROVEN`

Miaoxiang is admitted as a replaceable research/evidence provider. It is not admitted as an execution source or as an automatic Canon promotion source.
