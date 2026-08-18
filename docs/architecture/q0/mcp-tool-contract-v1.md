# Q0｜Research MCP / Tool Contract v1

Status: `architecture_freeze_candidate`

## 1. Principle

All agent access to market, Wind, evidence, macro and quant data crosses an explicit tool boundary. Agents do not read arbitrary local paths or databases directly.

Tool classes:

- `R0`: read-only / deterministic / no approval;
- `R1`: expensive or broad read / policy-limited;
- `W1`: proposal write / Human approval;
- `G1`: governance write / always Human Gate;
- `X`: unavailable by design.

## 2. Read-only Tools

### `get_asset_master`

Risk: `R0`

Input:
```json
{"asset_id":"string","as_of":"ISO-8601"}
```

Output: identity, ticker/exchange validity, currency, listing state, value-chain mappings.

### `get_market_snapshot`

Risk: `R0`

Input:
```json
{"asset_id":"string","as_of":"ISO-8601","window":"1d|20d|63d|252d"}
```

Output: point-in-time prices/liquidity/volatility with source snapshot IDs.

### `get_fundamental_facts`

Risk: `R0`

Input:
```json
{"asset_id":"string","as_of":"ISO-8601","metrics":["string"]}
```

Must only return facts publicly available by `as_of`, preserving original `published_at`.

### `get_estimate_snapshot`

Risk: `R0`

Input:
```json
{"asset_id":"string","as_of":"ISO-8601","metrics":["string"]}
```

Output: historical point-in-time consensus; latest-current consensus is forbidden in replay if after T0.

### `get_industry_facts`

Risk: `R0`

Input:
```json
{"node_id":"string","as_of":"ISO-8601","metrics":["string"]}
```

### `get_quant_features`

Risk: `R0`

Input:
```json
{"subject_id":"string","as_of":"ISO-8601","feature_ids":["string"]}
```

Only deterministic versioned features from `quant-workspace`.

### `get_macro_regime_snapshot`

Risk: `R0`

Input:
```json
{"as_of":"ISO-8601"}
```

Returns an immutable/versioned snapshot produced by `yiru-macro-cockpit`, including source repo revision.

### `search_evidence_index`

Risk: `R0`

Input:
```json
{"query":"string","subject_id":"string|null","as_of":"ISO-8601","limit":20}
```

Returns SourceRecord/Evidence metadata, never unrestricted local filesystem content.

### `get_evidence_object`

Risk: `R0`

Input:
```json
{"evidence_id":"string"}
```

Output must include source snapshot ID, locator, published_at, reviewer state and T0 eligibility.

### `get_narrative_events`

Risk: `R0`

Input:
```json
{"narrative_id":"string","as_of":"ISO-8601","lookback_days":90,"cohorts":["string"]}
```

### `get_replay_case`

Risk: `R0`

Input:
```json
{"replay_id":"string"}
```

Returns frozen T0, input manifest and prohibited future information rules.

## 3. Wind Adapter Tools

Wind is an external professional data source. Q0 does not assume a specific undocumented Wind API surface; the adapter wraps whatever licensed terminal/export/API access is legally available to the user.

### `wind_query_structured`

Risk: `R1`

Purpose: request point-in-time market/fundamental/consensus/industry data.

Required response metadata:

- `wind_request_id` or equivalent;
- query parameters;
- data timestamp/as-of;
- extraction timestamp;
- fields/units;
- raw export locator/hash if persisted.

### `wind_search_research`

Risk: `R1`

Purpose: discovery of announcements/news/reports.

Rule: Wind/Alice summary is `discovery_only` until the underlying source is captured/located. Machine summary alone cannot become Evidence.

### `wind_export_snapshot`

Risk: `W1`

Purpose: write an immutable export into designated Evidence Vault worker.

Requires approval because it writes external/raw artifacts. Result must return filename, capture timestamp, SHA-256 if actually computed, and vault locator. Never fabricate hashes.

## 4. Proposal Write Tools

### `create_research_candidate`

Risk: `W1`

Writes a candidate artifact only, never approved Canon.

Required approval context:

- run ID;
- input manifest hash;
- diff summary;
- no prohibited fields;
- target branch/workspace.

### `open_research_pr`

Risk: `W1`

May open Draft PR with candidate outputs. Must not merge.

## 5. Governance Tools

The following are `G1`, always Human Gate and SHOULD NOT be exposed to normal specialists:

- `admit_evidence`
- `promote_force_snapshot`
- `accept_outcome`
- `activate_a9_operational_canon`
- `modify_rsi_frozen`
- `merge_governance_pr`

## 6. Unavailable Tools

Risk: `X`

- broker order placement;
- portfolio allocation execution;
- target-price publication;
- personalized buy/sell actions;
- secret/key retrieval;
- arbitrary shell/local filesystem access from research agents.

## 7. Point-in-time Guard

Every data tool accepting `as_of` MUST enforce:

```text
published_at <= as_of
AND effective_at <= as_of where applicable
AND no latest-current backfill into historical replay
```

Same-day sources with unresolved precise timestamp return `same_day_timestamp_review` rather than silently passing.

## 8. Provenance Envelope

Every tool response must be wrapped with:

```json
{
  "tool": "name",
  "request_id": "id",
  "as_of": "timestamp",
  "source_revision": "string",
  "source_snapshot_ids": [],
  "generated_at": "timestamp",
  "quality_state": "verified|partial|unknown",
  "payload": {}
}
```

Agents are forbidden from stripping provenance before passing results to other agents.
