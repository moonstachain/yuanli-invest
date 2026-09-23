# YMQ-OS0｜Physical Plane Freeze v0.1

**Stage:** `YMQ-OS0-G0`  
**Status:** `IMPLEMENTATION_CANDIDATE / NOT_CANON`

## 1｜Freeze principle

YMQ-OS freezes **authority roles**, not cloud vendors. Each physical plane has one primary authority role. Providers may be replaced if contracts, provenance and deterministic replay are preserved.

## 2｜P1 Law & Control Plane

**Plane ID:** `LAW_CONTROL`  
**Primary authority role:** `LAW_CONTRACT_VERSION_ADMISSION`  
**Current provider:** GitHub.

Owns constitutions, schemas, code lineage, preregistration, validators, tests, CI, Human gates and admission receipts.

GitHub is not the raw time-series database and does not gain Reality authority from repository convenience alone.

## 3｜P2 Evidence & Runtime Truth Plane

**Plane ID:** `EVIDENCE_RUNTIME_TRUTH`  
**Primary authority role:** `IMMUTABLE_EVIDENCE_PIT_RUNTIME_READBACK`  
**Current provider species:** Postgres/Supabase + Object Storage/NAS.

Owns immutable snapshots, PIT observations, derived runtime-state indexes, run receipts and independent readback truth.

A UI, HF repository or generated report cannot overwrite this plane merely because it is easier to inspect.

## 4｜P3 Experiment Compute Plane

**Plane ID:** `EXPERIMENT_COMPUTE`  
**Primary authority role:** `EPHEMERAL_REPRODUCIBLE_COMPUTE`  
**Current provider species:** Hugging Face Jobs / replaceable container runner.

Allowed work includes feature generation, replay, model fitting, baseline/ablation/hard-negative evaluation and artifact hashing.

**Authority:** none. Compute may produce evidence for settlement; it cannot grant Canon, Capital or Execution authority. Runner replacement is allowed when the frozen input/output contract remains satisfied.

## 5｜P4 Experience & Projection Plane

**Plane ID:** `EXPERIENCE_PROJECTION`  
**Primary authority role:** `HUMAN_AI_INSPECTION_PROJECTION`  
**Current provider species:** Web, HF Space, ChatGPT, Notion.

Allowed work includes state cockpit, provenance drill-down, replay comparison, Human review surfaces and reasoning over authorized Context.

**Authority:** projection-only. It may not silently mutate Canon or Evidence/PIT truth and must surface `known_as_of`/freshness where relevant.

## 6｜Execution is outside YMQ-OS

VeighNa, broker connectivity, paper/live orders and real capital movement are **not a fifth YMQ plane**.

A future accepted ResearchSettlement can only be consumed by a separately governed Capital Admission layer.

`YMQ ResearchSettlement != CapitalPass != ExecutionAuthorization`

## 7｜G0 physical non-actions

This freeze does not itself:

- apply a Supabase migration;
- create/write HF Dataset, Model or Space;
- ingest live data;
- execute YMQ3-R0;
- connect VeighNa or a broker;
- create any paper/live order.

A GitHub file that describes a physical plane is not evidence that the physical plane changed.

## 8｜Reality test for provider replacement

A provider replacement is admissible only when it preserves the same object/time contracts, evidence hashes, exact run identity, defeat conditions, settlement axes and independent readback semantics. If those cannot be proven, replacement is `UNKNOWN → DENY`.
