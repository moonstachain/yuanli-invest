# YMQ-OS0-G1｜Machine Qualification Receipt v0.1

**Qualification target:** `YMQ-OS0-G1｜Sovereign Intelligence Stack`

**Implementation head:** `e7b979912aa331cb36f9734ea5af8272d90b78e4`

**Protected CI:** `repository-gates #837 / 34917736034 = SUCCESS`

## GitHub Law Plane

- Repository: `moonstachain/yuanli-invest`
- Branch: `ymq-os0-g1-sovereign-stack-physical-build`
- Protected check names preserved: `contracts`, `governance`
- `contracts` explicitly executes `python scripts/validate_ymq_os0_g1.py`
- Full `python -m unittest discover -s tests -p 'test_*.py' -v` passed in the same protected job.

## Supabase Reality Plane

- Project: `yuanli-invest-runtime`
- Project ref: `tbmoimbdhsrltvospwpu`
- Existing `evidence / pit / runtime` lineage was reused; no competing truth schema was created.
- G1 additive objects physically read back: `evidence.claim_receipts`, `runtime.agent_runs`, `runtime.research_projections`, `runtime.learning_deltas`.
- RLS physically read back as enabled on all G1 tables.
- Runtime receipt: `46bf317f-43a7-4b74-ad28-e58b2b9a33aa`
- Projection receipt: `9ef0d7cf-0650-4a33-a25b-4d989023722c`
- Runtime granted authority: `RESEARCH` only.
- Projection facts: `canonical_truth = false`, `can_grant_authority = false`.

## Hugging Face Experiment Plane

- Provider role: `COMPUTE_ONLY`
- Job ID: `6aa801b2f76d6a098a708898`
- Job state: `COMPLETED`
- Deterministic fixture SHA256: `e1b8faf005c35fce9ad045f5cd51a66a55ef9e0b60a1cfec5b4504bfe1f6e238`
- No HF Canon, Capital, or Execution authority is created by this proof.

## Agent Runtime

- Deterministic Context Compiler admits only evidence available at or before `as_of` and rejects UNKNOWN / missing authority.
- Router denies `position_sizing`, `broker_order`, `real_capital_move`, and any requested `CAPITAL` or `EXECUTION` authority.
- Qualification requires no LLM call; provider intelligence remains replaceable behind the protocol boundary.

## Notion Human Projection

- Parent: `原力投研`
- Page ID: `3dc8e1aa-ace4-81d0-b610-efe7b9f73af7`
- Page: `YMQ｜原力投研·宏观量化｜Founder Intelligence`
- Physical readback confirms the five-plane stack, six navigation surfaces, and explicit non-authority statement.
- Notion remains `PROJECTION_ONLY`.

## Settlement

`YMQ_OS0_G1_MACHINE_QUALIFIED`

`CAPITAL_NOT_AUTHORIZED`

`EXECUTION_NOT_AUTHORIZED`

This receipt qualifies the research infrastructure only. It does not merge the branch, grant portfolio sizing authority, create broker authority, authorize live trading, or move real capital.
