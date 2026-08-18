# Codex Task Spec｜Yuanli Quant AI Equity Research System v1

Status: `NOT_AUTHORIZED_TO_IMPLEMENT_UNTIL_HG_Q0_ACCEPTED`

## Mission

After Q0 Human Review acceptance, implement the smallest reproducible read-only system that can produce point-in-time Force candidate research for the frozen 30-asset seed universe.

Do not reinterpret architecture during implementation. If a contract is ambiguous, stop and open an architecture question rather than inventing authority.

## Inputs

Primary architecture files:

- `docs/architecture/YUANLI-QUANT-AI-EQUITY-RESEARCH-SYSTEM-v1.md`
- `docs/architecture/q0/repository-layout-v1.md`
- `docs/architecture/q0/duckdb-logical-schema-v1.sql`
- `docs/architecture/q0/agent-contracts-v1.md`
- `docs/architecture/q0/mcp-tool-contract-v1.md`
- `docs/architecture/q0/mvp-universe-30-v1.json`
- `docs/architecture/q0/replay-eval-contract-v1.md`
- `docs/architecture/q0/ci-human-gate-v1.md`
- `docs/architecture/q0/90-day-implementation-plan-v1.md`
- candidate schemas under `docs/architecture/q0/contracts/`.

Existing production constraints:

- `yuanli-invest` main currently has P/N/X contracts and A5 candidate reconstruction;
- `quant-workspace` remains current A9 operational canon;
- `yuanli-invest-rsi/FROZEN.md` must not be changed;
- raw licensed evidence stays outside Git.

## Work Packages

### WP1｜Q1 Universe Qualification

Target repo: `quant-workspace` plus contract PR in `yuanli-invest`.

Implement:

1. asset identifier registry for 30 seeds;
2. vendor symbol mapping;
3. listing validity intervals;
4. data coverage probe;
5. point-in-time publication metadata audit;
6. coverage report artifact.

Acceptance:

- 30/30 assets resolve without silent symbol substitution;
- invalid/missing coverage is explicit;
- no Force state other than `unknown` is generated.

### WP2｜DuckDB Point-in-Time Store

Target repo: `quant-workspace`.

Implement migrations based on logical schema. Split raw/staging/curated namespaces if useful, but preserve semantics.

Acceptance:

- same snapshot ingested twice is idempotent;
- historical query accepts `as_of` and rejects future publication leakage;
- database/raw files are gitignored;
- schema migration tests pass.

### WP3｜Feature Registry

Target repo: `quant-workspace`.

Implement deterministic feature protocol:

```python
FeatureResult(
  feature_id,
  subject_id,
  as_of,
  formula_version,
  value,
  unit,
  source_snapshot_ids,
  quality_state,
)
```

Start with market, fundamental, survival, convexity-left-tail families. Do not derive a Force scalar.

Acceptance: same manifest -> same feature rows/hash.

### WP4｜Read-only MCP Server

Target repo: `quant-workspace`.

Expose only Q0 R0 tools first:

- `get_asset_master`
- `get_market_snapshot`
- `get_fundamental_facts`
- `get_estimate_snapshot`
- `get_industry_facts`
- `get_quant_features`
- `get_macro_regime_snapshot`

Add evidence/narrative tools only after Evidence index exists.

Acceptance:

- every response carries provenance envelope;
- replay-mode `as_of` is enforced server-side;
- no write/execution tools exist in the first server.

### WP5｜Agent Runtime Skeleton

Target repo: `yuanli-invest`.

Create `packages/agent-runtime` only after candidate schemas are promoted by HG-Q0 implementation PR.

Implement:

- runtime profile config;
- ForceCIOAgent;
- six specialists;
- structured output types;
- tracing;
- point-in-time and prohibited-action guardrails;
- mocked R0 tools for unit tests.

Acceptance:

- no network required for unit tests;
- specialists cannot produce approved/admitted state;
- CIO can return `unknown` gracefully;
- prohibited fields fail tests.

### WP6｜A4/A5 Replay Harness

Target repo: `yuanli-invest`.

Reuse existing historical calibration fixtures. Do not change T0 definitions.

Acceptance:

- three cases rerun from frozen manifest;
- post-T0 source injection test fails closed;
- current/future estimate backfill test fails closed;
- run artifact captures runtime profile and trace ID.

### WP7｜Force Radar Read Model

Target repo: `yuanli-invest` or thin UI projection after contract review.

Build read model only; no investment action surface.

Views:

- 30-asset radar;
- asset evidence page;
- change queue.

Acceptance:

- every visible state links to evidence/feature provenance;
- no ranking by predicted return;
- no buy/sell/target/position fields.

## Branch / PR Discipline

- each WP uses its own branch and Draft PR;
- no direct push to main;
- cross-repo dependency pinned by exact SHA;
- no stacked PR unless explicitly declared;
- architecture deviations require a separate ADR/architecture PR;
- merges remain Human Review.

## Required Tests

At minimum:

```text
test_schema_strictness
test_no_force_scalar
test_no_trade_fields
test_asof_blocks_future_fundamental
test_asof_blocks_future_estimate
test_same_day_timestamp_is_not_auto_eligible
test_provenance_envelope_required
test_specialist_cannot_promote_canon
test_g1_tools_absent_from_specialists
test_replay_manifest_hash_stable
test_seed_universe_unique
test_seed_states_all_unknown
test_raw_artifacts_not_tracked
```

## Stop Conditions

Stop and request Human Review if:

- Wind access semantics/licensing are unclear;
- a source cannot supply point-in-time publication metadata;
- implementation would require changing `yuanli-invest-rsi/FROZEN.md`;
- an operational-canon switch appears necessary;
- a live execution/broker integration is proposed;
- a scalar composite score is introduced as a shortcut;
- agent outputs outperform only after using post-T0 information.

## Completion Receipt per WP

Each PR must include:

- base SHA / head SHA;
- files changed;
- tests run + results;
- exact architecture contracts implemented;
- known gaps;
- authority boundaries preserved;
- next gate.
