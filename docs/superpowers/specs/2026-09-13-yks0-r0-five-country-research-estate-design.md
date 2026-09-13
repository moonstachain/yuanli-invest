# YKS0-R0｜Five-Country 1990–2026 Research Estate × Evidence Pack — Written Spec

**Status:** `WRITTEN_SPEC_HUMAN_ACCEPTED`
**Human decision:** `ACCEPT_YKS0_R0_RESEARCH_ESTATE_WRITTEN_SPEC`
**Program:** `YKS0｜K-Shaped Society × Reality Distribution Regime`
**Child battle:** `YKS0-R0｜Five-Country 1990–2026 Research Estate × Evidence Pack`
**Parent Canon:** `YKS0-G0｜K-Shaped Society Constitution × Nine-Dimensional K Vector × Five-Country Replay Freeze`
**Base main SHA:** `8b30065d00f1c6aa321c9caf875b36b8a0b2d754`
**Authority state:** `DESIGN_ONLY / RESEARCH_CANDIDATE_ONLY`
**Implementation authority:** `NOT_AUTHORIZED`
**Merge authority:** `NOT_AUTHORIZED`
**Production runtime mutations:** `0`

## 0. Why this battle exists

YKS0-G0 froze the research constitution, nine-dimensional K Vector, five-country frame, hypotheses, 50-case replay program, baselines, hard negatives, and downstream G1–G6 sequencing. Subsequent desktop research on the United States, Germany, Japan, South Korea, and China produced valuable country evidence, macro-divergence hypotheses, asset-return mappings, and falsifiers that currently exist partly in conversational context and external source pages rather than as a durable Yuanli research asset.

YKS0-R0 converts that ephemeral research into a governed Research Estate without prematurely claiming that the five-country Point-in-Time replay has passed. It MUST keep three layers separate:

1. `Source Fact` — what an admissible source actually states;
2. `Research Inference` — the interpretation Yuanli Research draws from those facts;
3. `Scientific Status` — whether the inference is a desktop prior, preregistered hypothesis, replay-qualified result, or falsified claim.

R0 is an evidence and research-asset hardening lane, not a scientific validation lane and not a runtime-data lane.

## 1. Mother question

> Can Yuanli preserve the full five-country 1990–2026 K-shaped research corpus as a machine-addressable, evidence-bearing, Point-in-Time-aware Research Estate while keeping desktop findings explicitly below formal replay authority?

The estate must let a human or AI resolve: what is known by country/dimension; which sources support/contradict each claim; what remains a desktop prior; where PIT evidence is missing; which apparent K episodes are actually hard negatives; and where G2/G3 must obtain vintage-safe Reality instead of hindsight.

## 2. Authority architecture

### GitHub / `yuanli-invest`
Role: `Research Canon Candidate / Evidence Manifest / Research Synthesis`.
May contain source registries, country dossiers, K-dimension evidence maps, desktop synthesis, candidate hypotheses/falsifiers, replay-case candidate stubs, unknowns/gaps, and machine-readable manifests.
MUST NOT claim historical PIT reconstruction, replay qualification, asset alpha, Capital Admission, or Execution Authority.

### Soul / Ontology
Role: semantic authority for what K objects mean.
R0 MUST NOT mutate Soul ontology, create a second ontology root, mint new top-level operational namespaces, or alter R01–R37 relation law. G1 owns that architecture separately.

### Supabase / Object Storage
Future G2 role: runtime Reality store for raw time series, vintages, PIT observations, compiled states, replay receipts, and physical lineage.
R0 MUST NOT write production Supabase tables or upload production data.

### Notion / Web / ChatGPT
Role: human projection / experience plane only.
R0 MUST NOT create Notion truth authority, direct Canon mutation, or production projection dependencies.

### UIG / Brain Context Gateway
Future role: read-side federation and bounded context assembly.
R0 may define stable GitHub paths but MUST NOT mutate production UIG registries or Context Gateway runtime.

## 3. Research-estate topology

Implementation target:

```text
research/k-shaped-society/
├── README.md
├── reports/
│   ├── YKS0-R0-FIVE-COUNTRY-1990-2026-RESEARCH.md
│   └── YKS0-R0-DIVERGENCE-ASSET-MAP.md
├── countries/
│   ├── US.md
│   ├── DE.md
│   ├── JP.md
│   ├── KR.md
│   └── CN.md
├── evidence/
│   ├── source-registry.json
│   ├── evidence-claims.json
│   └── source-authority-policy.md
├── dimensions/
│   └── k-dimension-evidence-matrix.json
├── hypotheses/
│   └── hypothesis-registry.json
├── replay/
│   ├── case-candidate-registry.json
│   └── pit-readiness-matrix.json
├── settlements/
│   └── YKS0-R0-DESKTOP-SETTLEMENT.md
└── manifests/
    └── research-estate-manifest.json
```

R0 deliberately does not create G2 raw datasets, Supabase migrations, HF datasets/jobs, 50 fully reconstructed vintage-safe replay cases, scientific PASS receipts, Notion pages, or portfolio/capital/action objects.

## 4. Existing-system compatibility

### Evidence compatibility
The repository already has `packages/contracts/schemas/evidence.schema.json`. R0 may add country, K-dimension, release/vintage, PIT-readiness, and retrieval metadata, but MUST remain semantically compatible and MUST NOT create a conflicting global evidence authority.

### PIT compatibility
The existing Gold `Evidence Pack @ T0` establishes: `known_as_of <= T0`; later physical retrieval does not grant later information to T0; unavailable thresholds remain `UNKNOWN / FAIL_CLOSED`; later outcomes and scientific settlements may not leak into T0 state.

### Registry compatibility
R0 does not create a tenth global Research Capability Registry. It is a bounded domain research estate whose objects may later compile into existing governed interfaces.

## 5. Evidence authority model

Local grades:
- `A1` official national primary;
- `A2` official international primary/analysis;
- `A3` peer-reviewed or high-quality academic;
- `B1` index-provider / industry-primary / audited disclosure;
- `B2` transparent working paper / research institution;
- `B3` reputable secondary synthesis;
- `C1` practitioner interpretation with evidence links;
- `C2` narrative/press hypothesis-generation input;
- `D` unverified, ambiguous, inaccessible, or incompatible.

Compatibility projection to the repository's coarse grades:

```text
A1/A2 -> A
A3/B1 -> B
B2/B3/C1 -> C
C2/D -> D
```

No projection may silently increase authority.

Every decisive claim MUST keep `source_fact` separate from `research_inference`, and include exact locator, issuer, publication date when available, source type, country/scope, hypothesis IDs, K dimensions, PIT status, and revision/reconstruction notes. If exact `known_as_of` or original vintage cannot be established, the source may support desktop research but MUST NOT be labeled PIT-qualified.

## 6. Five-country scope

Countries: `US / DE / JP / KR / CN`.
Target research window: `1990-01-01` through `2026-09-13`.
This does not claim continuous comparable data for every dimension back to 1990.

Every country dossier MUST state: strongest K evidence, strongest counterevidence, data-availability boundary, likely K-regime episodes, candidate hard negatives, three divergence targets, asset-mapping evidence, PIT readiness by period, unresolved comparability issues, and current scientific status.

## 7. Nine-dimensional K evidence matrix

Preserve exactly:
`K01 INDUSTRY / K02 FIRM / K03 PROFIT / K04 EMPLOYMENT / K05 LABOR / K06 WEALTH / K07 REGION / K08 OPPORTUNITY / K09 POLICY`.

For each country × dimension pair record: source count, highest evidence grade, earliest/latest reliable history, PIT-vintage availability (`YES/PARTIAL/NO/UNKNOWN`), comparability (`COMMON_DEFINITION / DOCUMENTED_CROSSWALK / COUNTRY_NATIVE_ONLY / NOT_COMPARABLE`), direction candidate (`WIDENING / NARROWING / MIXED / UNKNOWN`), constructability of Level/Delta/Delta2/Breadth/Dispersion, key support/counterevidence IDs, and unresolved gaps.

R0 MUST NOT compress the 9D vector into a scalar K score.

## 8. Three divergence targets

### D-A｜Index–Median Divergence
Does a cap-weighted equity index or large-cap cohort materially outperform the median/equal-weight/broader-market representation while leadership breadth narrows? Formal replay requires historical constituents, weights, delistings, corporate actions, accounting data, and availability reconstruction. Strongest expected dimensions: `K02/K03/K06`.

### D-B｜GDP–Household Divergence
Does aggregate output/productivity remain resilient while median real wage, median disposable income, labor share, household consumption, or employment quality fails to diffuse proportionately? Consumer confidence is auxiliary. Strongest expected dimensions: `K01/K04/K05/K06/K09`.

### D-C｜Profit–Employment Divergence
Do frontier/large firms capture a rising share of profits, sales, exports, or productivity while employment share or marginal job creation fails to diffuse at the same rate? Strongest expected dimensions: `K02/K03/K04/K05`.

Current desktop prior may be recorded only as candidate: `D-C > D-B > D-A`.

## 9. Asset-return mapping boundary

R0 MUST NOT encode `KRegime -> Buy/Sell Asset`.
Allowed chain:

```text
KRegime
  -> Value Capture
  -> Earnings / Cash-flow Distribution
  -> Ownership Distribution
  -> Price / Valuation / Discount Rate / Liquidity
  -> Relative Return Candidate
```

Asset conclusions are relative transmission hypotheses, not absolute-return forecasts or portfolio instructions. Forbidden outputs: target price, recommended weight, position size, broker action, execution instruction.

## 10. Initial evidence anchors

Implementation should include and revalidate at least:
- OECD `Decoupling of wages from productivity`;
- Autor et al. `The Fall of the Labor Share and the Rise of Superstar Firms`;
- OECD Short-term Economic Statistics Revisions;
- FRED/ALFRED real-time periods;
- Federal Reserve Distributional Financial Accounts;
- S&P Dow Jones Indices concentration/equal-weight evidence;
- OECD Germany collective-bargaining/productivity-to-wage evidence;
- STOXX DAX vs broad Germany market evidence;
- Bank of Japan wage/productivity-gap evidence;
- BOJ small-vs-large firm profit-per-employee evidence;
- JPX TOPIX Large70 vs TOPIX falsifier evidence;
- OECD Korea chaebol/trickle-down evidence;
- OECD Korea SME productivity catch-up evidence;
- STOXX South Korea 200 concentration/relative-return evidence;
- China NBS GDP/productivity/income/consumption evidence;
- China NBS industrial-profit dispersion evidence;
- World Bank WDI China Gini evidence.

No source is automatically formal-PIT admissible merely because it is authoritative for current or retrospective description.

## 11. Hypothesis registry

Carry H1–H8 from G0: Frontier Divergence; Winner-Less-Hiring; Asset Carrier Switch / Ownership Amplification; Regional Agglomeration; Service Re-diffusion; Policy Slope Compression; Index–Median Divergence; K-to-Asset Transmission.

Each entry MUST contain statement, null, expected direction where applicable, decisive dimensions, baseline competitors, falsifier, desktop evidence state, contradictory evidence, relevant countries/cases, and formal replay status.

R0 may refine H7/H8 to reflect that K structure is more naturally a relative-return/breadth/concentration predictor than a standalone absolute-index timing signal. This remains `CANDIDATE_RESEARCH_INFERENCE` until separately admitted.

## 12. Hard negatives

Preserve `HN1 CYCLICAL_DISPERSION / HN2 AGGREGATE_STAGNATION / HN3 VALUATION_BUBBLE / HN4 DATA_ARTIFACT / HN5 POLICY_COMPRESSION / HN6 ASSET_LEVEL_DROP / HN7 SECTOR_ROTATION / HN8 REGIONAL_CATCHUP`.

Include candidate examples: Japan 1990s aggregate-stagnation control; Japan 2025 Large70 underperforming TOPIX as D-A falsifier; Germany large-index outperformance as sector/global-exposure confounder; Korea 2013–2024 SME productivity catch-up as rediffusion/counter-signal. These remain candidate examples until exact T0 construction.

## 13. PIT readiness model

Every evidence source/candidate case declares exactly one of:
- `PIT_NATIVE`
- `PIT_RECONSTRUCTABLE`
- `CURRENT_ONLY`
- `BACKTEST_OR_RESTATED`
- `UNKNOWN`

Formal replay admission requires `PIT_NATIVE` or separately validated `PIT_RECONSTRUCTABLE`. All others may support desktop synthesis but fail closed for historical T0 visibility.

## 14. Case-candidate registry

R0 does not populate the final 50-case G3 dataset. It creates a candidate registry preserving the G0 target of 10 cases per country. Each record contains case ID candidate, country, provisional T0, proposed visible cutoff, hidden horizon, divergence targets, implicated dimensions, baselines, hard-negative class if any, PIT readiness, source IDs, leakage risks, and status.

Allowed statuses: `CANDIDATE_DESKTOP / PIT_AUDIT_REQUIRED / PREREGISTRATION_READY / REJECTED`.
No R0 case may be labeled `REPLAY_PASS` or `SETTLED`.

## 15. Desktop settlement

Maximum R0 authority:
`STRONG_PRIOR / FORMAL_PIT_VALIDATION_REQUIRED`.

The settlement must separately report physical evidence coverage, scientific status, authority status, and runtime status. If final evidence continues to support it, the current posture may state: H1 strong evidence; H2 strong evidence; H3 strong U.S. evidence/cross-country pending; H4 plausible/PIT incomplete; H5 plausible/counterexamples required; H6 institutionally supported/quantitative replay pending; H7 conditional and relative; H8 not proven as an absolute-return predictor.

The settlement MUST NOT use unconditional `PASS`.

## 16. Research-estate manifest

`manifests/research-estate-manifest.json` provides one machine-readable discovery root for future UIG/Context Gateway. Minimum fields:

```json
{
  "estate_id": "YKS0-R0",
  "program": "YKS0",
  "title": "Five-Country 1990-2026 Research Estate × Evidence Pack",
  "authority_state": "RESEARCH_CANDIDATE",
  "reality_state": "DESKTOP_EVIDENCE_HARDENED",
  "runtime_state": "NOT_STARTED",
  "countries": ["US", "DE", "JP", "KR", "CN"],
  "dimensions": ["K01", "K02", "K03", "K04", "K05", "K06", "K07", "K08", "K09"],
  "root": "research/k-shaped-society/README.md",
  "source_registry": "research/k-shaped-society/evidence/source-registry.json",
  "pit_readiness": "research/k-shaped-society/replay/pit-readiness-matrix.json",
  "desktop_settlement": "research/k-shaped-society/settlements/YKS0-R0-DESKTOP-SETTLEMENT.md",
  "production_runtime_authorized": false,
  "capital_authorized": false,
  "execution_authorized": false
}
```

The manifest is a locator/discovery object, not scientific authority.

## 17. Validation design

Future implementation must fail closed unless: all manifest paths exist; five countries exist exactly once; all nine dimensions exist and no scalar K-score field exists; every decisive claim references sources; every source has authority and PIT status; `source_fact` and `research_inference` remain separate; no case is replay-qualified; non-PIT sources cannot be used as T0-qualified evidence; structured registries contain no forbidden investment/action outputs; no production Supabase/HF/Notion/UIG config changes; country files disclose counterevidence/gaps; and desktop settlement does not claim unconditional scientific PASS.

## 18. Estate hard negatives

Reject at minimum: conversation-only knowledge; citation laundering; fact/inference collapse; PIT laundering; backtest laundering; country-definition collapse; K-score resurrection; asset-authority escalation; counterevidence deletion; desktop-to-science escalation; source-recency substitution; and projection-as-truth.

## 19. Acceptance criteria

The Human Principal must agree that R0 is an evidence-hardening side lane; GitHub remains research/evidence authority while runtime waits for G2; five-country material is preserved without claiming full PIT reconstruction; 9D stays non-scalar; three divergence targets remain explicit; asset mapping is transmission research only; counterevidence/hard negatives are first-class; every source is typed by PIT readiness; desktop settlement remains below formal replay authority; implementation and merge remain separately gated.

Required Human Acceptance token:

`ACCEPT_YKS0_R0_RESEARCH_ESTATE_WRITTEN_SPEC`

Acceptance authorizes only a separate implementation plan. It does not authorize implementation, external production mutation, or merge.

## 20. Current stop line

Written Spec is Human Accepted. Implementation remains `NOT_AUTHORIZED` until a separate execution token is issued. Do not create research-estate files, populate machine registries, add validators, mutate Supabase/HF/Notion/UIG, claim R0 complete, or merge anything before that token.