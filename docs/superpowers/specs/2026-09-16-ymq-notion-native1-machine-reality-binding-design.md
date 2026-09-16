# YMQ-NOTION-NATIVE1｜Machine Reality Binding × Event-Driven State Transition

**Status:** ACCEPTED / IMPLEMENTATION_PLAN_READY  
**Date:** 2026-09-16  
**Repository:** `moonstachain/yuanli-invest`  
**Supabase Reality Plane:** `yuanli-invest-runtime` (`tbmoimbdhsrltvospwpu`)  
**Parent initiative:** `YMQ-NOTION-NATIVE0｜Human Intelligence Workbench`

> **Accepted design body unchanged from the reviewed Written Spec.**  
> The complete implementation plan is frozen at `docs/superpowers/plans/2026-09-16-ymq-notion-native1-machine-reality-binding.md`.  
> Historical reviewed design content remains available in PR #97 history at commit `5447e5f770124fe661720dbf242e276a64cfb092`.

## Accepted Design Invariants

1. `Reality > Belief`; `ClaimAuthority <= EvidenceAuthority`; `UNKNOWN = DENY`.
2. GitHub remains Law Plane; Supabase remains Reality/Evidence Ledger; Notion remains Human Work Graph / projection only.
3. `ResearchAuthority != CapitalAuthority != ExecutionAuthority` and `ResearchPass != CapitalPass`.
4. Machine-to-Notion flow is `Reality/Evidence → transactional outbox → fail-closed transition evaluation → Notion machine-owned projection → immutable delivery receipt`.
5. Native1 event set is closed to `CLAIM_RECEIPT_CREATED`, `RESEARCH_PROJECTION_CREATED`, `REALITY_GATE_SETTLED`, `LEARNING_DELTA_CREATED`, `AUTHORITY_DENIED`.
6. Automatic forward movement advances at most one Journey Stage. Machine evidence `UNKNOWN/BLOCKED` may regress any research stage to `02 EVIDENCE`.
7. `04 TRANSMISSION → 05 AUDIT` is the only Native1 automatic forward research transition and requires a bound Human Context, admitted evidence, a research projection, and a non-empty defeat condition.
8. `AUDIT → SHADOW` is denied by default; Native1 grants no Shadow, Capital, or Execution authority.
9. Notion machine-owned fields never silently overwrite user-authored thesis/body content.
10. Every machine projection carries event/source identity, `known_as_of/as_of`, authority, idempotency, and delivery receipt.
11. Outbox delivery is durable and idempotent; duplicate/stale events cannot overwrite newer machine state.
12. No secret literal is committed. Notion integration credential provisioning remains a Human Security Gate.
13. Machine qualification requires a physically verified automatic wake-up and durable retry/recovery path, not a one-time manual invocation.
14. Historical rows are never silently presented as live events; explicit replay carries `REPLAY` metadata.
15. No second repository or competing truth schema is created.

## Verified Starting State

- Supabase project `yuanli-invest-runtime` (`tbmoimbdhsrltvospwpu`) is healthy.
- Existing runtime lineage includes `evidence.claim_receipts`, `runtime.agent_runs`, `runtime.research_projections`, `runtime.learning_deltas`, `runtime.reality_gate_runs`.
- At design time: 0 claim receipts, 1 agent run, 1 research projection, 0 learning deltas, 7 reality gate runs.
- No Supabase Edge Function existed at design time.
- `pg_cron` and `pg_net` are available but not installed; `supabase_vault` is installed.
- Native0 five Notion Human Object data sources exist and the DEMO Capital Question page is `3dd8e1aa-ace4-8121-a06e-dfe05b699035`.
- Native0 has `Journey Stage`, `Gate Status`, `Block Reason`, but machine Reality binding and automatic transition enforcement are not yet live.

## Implementation Reference

Follow the approved plan exactly:

`docs/superpowers/plans/2026-09-16-ymq-notion-native1-machine-reality-binding.md`

The implementation plan defines nine tasks: contract freeze, pure transition engine, pure Notion patch builder, Supabase outbox/RPC migration, Edge Function adapter, Notion machine-owned schema + DEMO binding, durable wake path, adversarial E2E replay, protected CI + qualification receipt.

## Final Allowed Qualification Status

`YMQ_NOTION_NATIVE1_MACHINE_QUALIFIED / NOTION_PROJECTION_ONLY / CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED / SHADOW_NOT_AUTHORIZED`

If any physical proof or credential gate remains incomplete, use an explicit blocked status rather than upgrading authority.