# YMQ-OS0-G1｜Machine Qualification Receipt v0.1

**Qualification target:** `YMQ-OS0-G1｜Sovereign Intelligence Stack`

**Reviewed implementation head:** `3ed43daf762bd25b93eb65c760062d9c0a925e5e`

**Protected CI:** `repository-gates #840 / 34918034608 = SUCCESS`

## GitHub Law Plane

- Repository: `moonstachain/yuanli-invest`
- Branch: `ymq-os0-g1-sovereign-stack-physical-build`
- Protected check names preserved: `contracts`, `governance`.
- `contracts` explicitly executes `python scripts/validate_ymq_os0_g1.py`.
- Full `python -m unittest discover -s tests -p 'test_*.py' -v` passed in the same protected job.
- Final authority hardening rejects every non-`RESEARCH` runtime authority and rejects Notion projections that claim Capital or Execution authority.

## Supabase Reality Plane

- Project: `yuanli-invest-runtime`
- Project ref: `tbmoimbdhsrltvospwpu`
- Existing `evidence / pit / runtime` lineage was reused; no competing truth schema was created.
- G1 additive objects physically read back: `evidence.claim_receipts`, `runtime.agent_runs`, `runtime.research_projections`, `runtime.learning_deltas`.
- RLS physically read back as enabled on all G1 tables.
- FK covering-index hardening physically read back for `claim_receipts.source_snapshot_id` and `learning_deltas.source_run_id`.
- Runtime receipt: `46bf317f-43a7-4b74-ad28-e58b2b9a33aa`.
- Projection receipt: `9ef0d7cf-0650-4a33-a25b-4d989023722c`.
- Runtime granted authority: `RESEARCH` only.
- Projection facts: `canonical_truth = false`, `can_grant_authority = false`.

## Hugging Face Experiment Plane

- Provider role: `COMPUTE_ONLY`.
- Job ID: `6aa801b2f76d6a098a708898`.
- Job state: `COMPLETED`.
- Deterministic fixture SHA256: `e1b8faf005c35fce9ad045f5cd51a66a55ef9e0b60a1cfec5b4504bfe1f6e238`.
- No HF Canon, Capital, or Execution authority is created by this proof.

## Agent Runtime

- Deterministic Context Compiler admits only evidence available at or before `as_of` and rejects UNKNOWN / missing authority.
- Router and validator deny `position_sizing`, `broker_order`, `real_capital_move`, and every requested authority other than `RESEARCH`.
- Qualification requires no LLM call; provider intelligence remains replaceable behind the protocol boundary.

## Notion Human Projection

- Parent: `原力投研`.
- Page ID: `3dc8e1aa-ace4-81d0-b610-efe7b9f73af7`.
- Page: `YMQ｜原力投研·宏观量化｜Founder Intelligence`.
- Physical readback confirms the five-plane stack, six navigation surfaces, and explicit non-authority statement.
- Notion remains `PROJECTION_ONLY` and its manifest must keep both `capital_authorized = false` and `execution_authorized = false`.

## Settlement

`YMQ_OS0_G1_MACHINE_QUALIFIED`

`CAPITAL_NOT_AUTHORIZED`

`EXECUTION_NOT_AUTHORIZED`

This receipt qualifies the research infrastructure only. It does not merge the branch, grant portfolio sizing authority, create broker authority, authorize live trading, or move real capital.
