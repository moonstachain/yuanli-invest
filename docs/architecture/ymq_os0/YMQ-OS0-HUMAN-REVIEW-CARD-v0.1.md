# YMQ-OS0-G0｜Human Review Card v0.1

**Candidate only. This card records review questions; it grants no authority.**

## Review basis

- Written Spec: `docs/superpowers/specs/2026-09-13-ymq-os0-g0-macro-quant-constitution-design.md`
- Machine contract: `config/ymq_os0/ymq_os0_contract.v0.1.json`
- Object schemas: `packages/contracts/schemas/ymq/`
- Constitution/Object Model/Physical Plane Freeze under `docs/architecture/ymq_os0/`

## Human acceptance questions

| # | Question | Required answer |
|---|---|---|
| 1 | Is YMQ-OS explicitly a YIOS0 L2–L8 research subsystem, not a parallel Investment OS? | YES |
| 2 | Are the four physical planes exact and does each have one bounded primary authority role? | YES |
| 3 | Are providers replaceable without transferring Canon authority to provider identity? | YES |
| 4 | Are the nine canonical research objects exact and separately governed? | YES |
| 5 | Is `known_as_of <= T0` the PIT replay law and `UNKNOWN = DENY`? | YES |
| 6 | Are `ResearchPass`, `CapitalPass` and `ExecutionAuthority` strictly separated? | YES |
| 7 | Can `PHYSICAL_PASS / SCIENTIFIC_NO_GO` remain a valid settlement? | YES |
| 8 | Is `ClaimAuthority <= EvidenceAuthority` machine-enforced? | YES |
| 9 | Are past Evidence and Settlement immutable and LearningDelta forward-only? | YES |
| 10 | Are YMQ4 historical IDs preserved without silently aliasing YMQ4 to MQE4 Canon? | YES |
| 11 | Does YMQ4-B3 remain visible as scientific NO-GO with no Canon authority? | YES |
| 12 | Do the machine schemas and docs contain zero Capital/Execution authority escalation? | YES |
| 13 | Is G0 law-only, with no Supabase/HF runtime mutation implied? | YES |
| 14 | Is Execution explicitly outside YMQ-OS? | YES |

## Boundaries that remain false after G0 acceptance

Even a future explicit Human acceptance of G0 would **not** by itself authorize:

- protected-main merge;
- Supabase migration or runtime mutation;
- HF Dataset/Model/Space write;
- YMQ3-R0 canonical physical Reality run;
- Market Clock implementation;
- portfolio weighting or position sizing;
- VeighNa invocation;
- broker credentials/connection;
- broker paper or live order submission;
- real capital movement;
- automatic research-to-capital or research-to-execution promotion.

## Gate sequence

`MACHINE_QUALIFIED` and `HUMAN_ACCEPTED` are separate facts.

The implementation plan requires the independent Human token:

`ACCEPT_YMQ_OS0_G0_MACHINE_QUALIFICATION`

Only after that acceptance is separately recorded may the later protected-main merge gate be considered, and that merge itself requires:

`AUTHORIZE_YMQ_OS0_G0_MERGE`

No token may be inferred from this review card, from CI success, or from a prior Written Spec acceptance.
