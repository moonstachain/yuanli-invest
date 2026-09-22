# YOS-FIN1-G0｜Machine Qualification Receipt v0.1

**State:** `AWAITING_PROVIDER_CREDENTIALS`

## Implemented
- Provider-neutral Source Contract with anti-echo and hard authority ceilings.
- Finance router for macro facts, listed-company facts, and natural-language screens.
- Read-only Wind adapter with typed failure taxonomy.
- Eastmoney MiaoXiang adapter for official Skill endpoint `mkapi2.dfcfs.com/finskillshub/api/claw/query`.
- iWenCai OpenAPI adapter marked `COMMUNITY_DOCUMENTED_RUNTIME_VERIFICATION_REQUIRED` plus browser/CLI discovery descriptor.
- Cross-provider comparator that refuses same-provider requery as corroboration and surfaces PIT/semantic mismatch.

## Reality Proof Status
- Wind bounded macro probe: `FAIL_CLOSED / ENTITY_UNRESOLVED`.
- MiaoXiang credential discovery: `HUMAN_GATE / MIAOXIANG_CREDENTIAL_REQUIRED`.
- iWenCai credential discovery: `HUMAN_GATE / IWENCAI_CREDENTIAL_REQUIRED`.
- iWenCai local browser CLI: `NOT_INSTALLED`; no hidden installation performed.

## Probe Status
- Probe A macro corroboration: `PARTIAL_WIND_FAIL_CLOSED_MIAOXIANG_HUMAN_GATE`.
- Probe B listed-company fundamental: `MIAOXIANG_HUMAN_GATE`.
- Probe C natural-language screen: `IWENCAI_HUMAN_GATE`.

## Non-Claims
This receipt does not claim the three-source Reality Proof passed. It does not claim MiaoXiang or iWenCai live connectivity. It does not upgrade screening output to evidence. It does not authorize capital, sizing, execution, broker, VeighNa, scheduler, or Canon promotion.

## Required Human Gates
1. Provide/configure an Eastmoney MiaoXiang API key through `MX_APIKEY` or `EASTMONEY_APIKEY`.
2. Provide/configure an iWenCai OpenAPI key through `IWENCAI_API_KEY`, if the account has OpenAPI access.
3. Separately decide whether a discovery-only browser CLI should ever be installed; G0 does not install it automatically.
