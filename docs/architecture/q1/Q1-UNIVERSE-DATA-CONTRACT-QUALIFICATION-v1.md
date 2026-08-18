# Q1｜China-US AI Universe & Data Contract Qualification v1

Status: `started_pending_vendor_qualification`

Accepted Q0 commit: `f9ab0aba57be052cccf2323716731602ca028039`
Quant implementation base: `moonstachain/quant-workspace@ce7a960d78c6f302b2ffa0ab9483797240d2e1a6`

## Mission

Qualify the frozen 30-asset China/US/HK AI seed universe for reproducible point-in-time research before any P/N/X state is generated.

Q1 answers only four questions:

1. Is each security identity unambiguous across time?
2. Can required market/fundamental/estimate/news data be retrieved with explicit vendor provenance?
3. Can publication/event time be enforced so historical queries cannot see the future?
4. Is the AI value-chain mapping evidentially defensible?

Q1 does **not** classify any asset as `golden_extreme`, `latent_dragon`, or any other Force state. All Force states remain `unknown`.

## Source of truth and repo split

- Seed universe authority: `docs/architecture/q0/mvp-universe-30-v1.json` at Q0 merge commit above.
- Business/method contract: `yuanli-invest`.
- Operational identifier/data qualification and future ingestion: `quant-workspace`.
- Wind licensed environment: vendor/data provider, not Git canon.
- Raw licensed exports and large source payloads: local/NAS only.
- GitHub may store schemas, mappings, coverage metadata, hashes/receipts, tests and non-restricted derived metadata.

## Required asset identity contract

Every seed must eventually have one qualification record containing:

- `asset_id` — immutable Q0 identifier;
- `legal_name` and common display name;
- `market` and exchange identifier;
- current local ticker;
- listing validity interval(s);
- vendor symbol(s), including Wind where available;
- US regulator identifier such as CIK where applicable;
- corporate-action / rename / ticker-change history sufficient for point-in-time joins;
- verification sources and timestamps;
- explicit ambiguity state if any field cannot be resolved.

No silent ticker substitution is allowed.

## Data domains to qualify

For every asset, publish an availability matrix for:

- daily market data;
- corporate actions;
- financial statements and filing/publication dates;
- consensus estimates with historical snapshot date if available;
- company announcements / filings;
- news / narrative-source metadata;
- industry or operating metrics where applicable.

Coverage must distinguish `current availability` from `historical point-in-time availability`.

## Data quality states

Only these states are allowed in Q1 qualification artifacts:

- `pending`
- `verified`
- `partial`
- `missing`
- `ambiguous_identifier_history`
- `vendor_unavailable`
- `license_blocked`
- `timestamp_unqualified`

Unknown or missing data is first-class; it must never be backfilled silently from current values.

## Point-in-time contract

A record is historically eligible only when the system can identify the information-availability time relevant to the requested `as_of`.

Examples:

- financial facts require filing/publication availability time, not only fiscal-period end;
- estimates require the vendor snapshot timestamp or effective date of the estimate set;
- corporate actions require validity intervals so historical symbols are not overwritten by current symbols;
- same-day material without a reliable release time remains `timestamp_unqualified` for intraday replay;
- a later restatement or corrected data point cannot appear in an earlier replay unless explicitly modeled as a later revision.

## Wind contract

Wind may be used to resolve identifiers and measure coverage, but Q1 must record the distinction between:

- metadata safe to persist in Git;
- licensed raw data that may only be stored locally/NAS;
- query recipes / field names / coverage receipts that are reproducible without copying restricted raw payloads.

If Wind licensing or export semantics are unclear, stop at `license_blocked` rather than improvising storage.

## AI value-chain mapping

The Q0 `primary_nodes` are hypotheses. Q1 must attach at least one evidence reference per material node or mark it `partial`/`missing`.

No value-chain mapping may be justified only by current market narrative. Prefer company disclosures, product pages, filings and segment data.

## Controls

Q1 may prepare 5–10 control/counterexample assets for later evals, but they must be stored in a separate control registry and must not expand the 30-asset product radar without a later Human Gate.

## Work sequence

### Q1A｜Identifier Registry

Resolve 30/30 legal/listing/vendor identities and history.

### Q1B｜Coverage Qualification

Measure market/fundamental/estimate/news coverage and missingness.

### Q1C｜Point-in-Time Qualification

Verify publication timestamps, estimate snapshots, corporate-action validity and lookahead controls.

### Q1D｜Value-Chain Evidence

Attach evidence-backed AI value-chain mappings.

### Q1E｜Human Review

Review exceptions, Wind licensing boundary and whether Q2 data-plane implementation is authorized.

## Exit criteria

Q1 cannot close until:

- 30/30 seed identities are resolved or explicit blocking exceptions are Human-reviewed;
- vendor symbols and listing histories are published without silent substitution;
- coverage matrix is complete for all required domains;
- publication-time semantics are documented and tested for every domain used by Q2;
- Wind storage/licensing boundary is accepted;
- AI value-chain mappings have evidence or explicit gaps;
- all Force states remain `unknown`;
- no buy/sell/target/position/expected-return fields exist;
- Human Review accepts the Q1 qualification package.

## Current state

This branch starts the Q1 contract and execution package. It does not claim that Wind or other vendor qualification has already run.