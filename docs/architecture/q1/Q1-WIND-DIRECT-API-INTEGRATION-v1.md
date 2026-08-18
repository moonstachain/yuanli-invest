# Q1｜Wind Direct API Integration v1

Status: `official_contract_discovered_runtime_probe_pending`

Official upstream pinned at:

`Wind-Information-Co-Ltd/wind-skills@384e95796ad572a2a9402c14084de73a122f0a10`

This replaces the earlier assumption that Wind qualification must be manually operated in Alice. The licensed API key can drive two distinct paths, with different evidentiary authority.

## 1. Structured data path — preferred for Q1

Wind's official skill publishes MCP endpoints authenticated with `Authorization: Bearer <WIND_API_KEY>` and JSON/SSE responses.

Primary Q1 endpoints:

- stock data: `https://mcp.wind.com.cn/vserver_stock_data/mcp/`
- financial documents/news: `https://mcp.wind.com.cn/vserver_financial_docs/mcp/`
- economic data: `https://mcp.wind.com.cn/vserver_economic_data/mcp/`
- analytics: `https://mcp.wind.com.cn/vserver_analytics_data/mcp/`

The official client initializes MCP protocol `2025-03-26`, then calls `tools/call`.

For the frozen 30-stock universe, use structured tools before Alice:

- `get_stock_basicinfo`
- `get_stock_kline`
- `get_stock_fundamentals`
- `get_stock_events`
- `get_company_announcements`
- `get_financial_news`

Q1 will use this path for identity, coverage and point-in-time qualification wherever the endpoint exposes auditable fields.

## 2. Alice Agent path — discovery / synthesis only

Official endpoint:

`https://mcp.wind.com.cn/skills/alice`

Protocol: JSON-RPC `message/stream` over SSE. Official request metadata uses `chatMode=12`, `originalChatMode=4`, `switchMode=auto`, timezone `Asia/Shanghai`.

Alice may help locate sources, synthesize research or invoke a named Alice Skill, but Alice prose is not admitted Evidence by itself.

## 3. Authority rule

```text
Wind MCP structured response
  -> vendor qualification / source locator / candidate fact
  -> PIT + license + provenance checks
  -> Q1 qualification record

Wind Alice response
  -> discovery / synthesis only
  -> locate underlying Wind record / filing / news item
  -> same PIT + license + provenance checks
```

Neither path can promote P/N/X, Force classification, Outcome or Canon during Q1.

## 4. Secret policy

The real API key is runtime-only. It must never appear in:

- Git history;
- PR body/comment;
- workflow YAML;
- test fixture/snapshot;
- agent trace/log;
- Evidence locator metadata.

Runtime reference is `WIND_API_KEY` only. Because a key was shared in conversational text, it should be rotated after integration validation; the replacement should remain outside Git.

## 5. Current implementation

Operational adapter is implemented in `moonstachain/quant-workspace` Q1 Draft PR under:

- `src/data/wind_direct.py`
- `scripts/q1_wind_live_probe.py`
- `tests/test_wind_direct.py`

The adapter pins the official upstream contract and has offline CI tests. A real vendor qualification remains `not_run` until a networked runtime executes the live probe; no hash, vendor mapping or coverage claim may be fabricated before that.
