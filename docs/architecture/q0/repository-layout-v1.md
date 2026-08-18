# Q0｜Repository Layout v1

Status: `architecture_freeze_candidate`

Q0 deliberately avoids a new monorepo. Implementation is split across existing repositories by authority.

## 1. `moonstachain/yuanli-invest`

Future business-research Canon and agent orchestration contracts.

```text
yuanli-invest/
├── docs/
│   ├── architecture/
│   │   ├── YUANLI-QUANT-AI-EQUITY-RESEARCH-SYSTEM-v1.md
│   │   └── q0/
│   └── methodology/
├── packages/
│   ├── contracts/
│   │   └── schemas/                 # promoted schemas only after Human Gate
│   ├── research-core/               # deterministic admission/classification rules
│   ├── agent-runtime/               # Q4 future package
│   │   ├── agents/
│   │   │   ├── cio.py
│   │   │   ├── paradigm.py
│   │   │   ├── narrative.py
│   │   │   ├── convexity.py
│   │   │   ├── fundamental.py
│   │   │   ├── red_team.py
│   │   │   └── evidence_judge.py
│   │   ├── tools/
│   │   ├── guardrails/
│   │   ├── runtime_profiles/
│   │   └── tracing/
│   └── radar-core/                  # ForceRadar assembly/read models
├── canon/
│   ├── evidence/
│   ├── paradigm/
│   ├── narratives/
│   ├── convexity/
│   └── force-snapshots/
├── replays/
│   ├── manifests/
│   ├── fixtures/
│   └── gold/
├── evals/
│   ├── datasets/
│   ├── graders/
│   └── receipts/
├── events/
├── receipts/
└── api/
```

Q0 candidate schemas remain under `docs/architecture/q0/contracts/`; moving them into `packages/contracts/schemas/` is a post-HG-Q0 implementation action.

## 2. `moonstachain/quant-workspace`

Current operational quant/data plane. Existing `uv + DuckDB + Streamlit` assets are reused; current example trading strategies become legacy/demo, not the Force core.

Target layout:

```text
quant-workspace/
├── src/
│   ├── data/
│   │   ├── adapters/
│   │   │   ├── wind.py
│   │   │   ├── us_market.py
│   │   │   ├── sec.py
│   │   │   └── macro_cockpit.py
│   │   ├── ingest/
│   │   ├── point_in_time/
│   │   ├── storage.py
│   │   └── quality.py
│   ├── features/
│   │   ├── market.py
│   │   ├── fundamental.py
│   │   ├── estimates.py
│   │   ├── industry.py
│   │   ├── narrative.py
│   │   ├── convexity.py
│   │   └── registry.py
│   ├── replay/
│   ├── paper/
│   └── mcp_server/
├── migrations/
├── tests/
├── data/                             # gitignored raw/local DB
└── app/                              # optional shadow research UI
```

Hard boundary: `quant-workspace` calculates; it does not self-promote Canon conclusions.

## 3. `moonstachain/yuanli-invest-rsi`

No Q0 structural rewrite. FROZEN remains untouched.

Future integration only through versioned receipts:

```text
yuanli-invest-rsi/
├── families/
│   └── force-research/               # future candidate family, not created by Q0
├── protocol/
│   └── eval-receipt-contract         # future, Human Gate required
└── FROZEN.md                         # DO NOT MODIFY
```

Input to RSI must be approved replay/eval/settlement receipts, not raw production state.

## 4. `moonstachain/yiru-macro-cockpit`

No authority change. Add only a future stable provider projection if needed:

```text
yiru-macro-cockpit/
└── projections/
    └── yuanli-invest/
        ├── macro-regime.schema.json
        └── latest.json               # deterministic versioned projection
```

A9 consumes exact repo revision + snapshot hash.

## 5. Local/NAS Evidence Vault

Not a Git repository requirement.

Suggested logical layout:

```text
EvidenceVault/
├── sources/
│   ├── wind/
│   ├── sec/
│   ├── ir/
│   ├── web/
│   └── research/
├── manifests/
├── snapshots/
├── parquet/
├── duckdb/
└── receipts/
```

Licensed/raw material stays here. Git receives only metadata/hash/locator/adjudication objects allowed by policy.

## 6. Inter-repo Contracts

```text
quant-workspace --FeatureSnapshot--> yuanli-invest
macro-cockpit --MacroSnapshot------> yuanli-invest
EvidenceVault ----EvidenceMeta-----> yuanli-invest
yuanli-invest ----EvalReceipt------> yuanli-invest-rsi (future gated)
yuanli-invest-rsi --Proposal-------> Human Review, never direct Canon write
```

Every cross-repo payload needs `schema_version`, producer repo revision, generated_at/as_of, input hashes and quality/admission state.
