# Q1｜Wind Operator Task Spec v1

Role: `Vendor Qualification Operator / Machine Data Analyst`

This task is for a licensed Wind Professional / Wind Alice environment. It is not authority to modify Git canon or assign Force classifications.

## Inputs

- Q0 seed universe: `docs/architecture/q0/mvp-universe-30-v1.json`
- Q0 accepted commit: `f9ab0aba57be052cccf2323716731602ca028039`
- Q1 contract: `docs/architecture/q1/Q1-UNIVERSE-DATA-CONTRACT-QUALIFICATION-v1.md`

## Mission

For all 30 seed assets, produce a reproducible qualification package covering identity, Wind/vendor mapping, listing history, historical data availability, publication-time semantics and missingness.

Do not produce investment recommendations, P/N/X states, target prices, position sizes, expected returns or rankings.

## Phase 1｜Identifier qualification

For every asset return:

- Q0 `asset_id`;
- legal company name in English and local language where available;
- current ticker and exchange;
- Wind security code / Wind instrument identifier;
- historical ticker/name/exchange changes;
- listing start date and delisting/end date if applicable;
- corporate-action identifier notes relevant to longitudinal joins;
- regulator identifier where available (e.g. US CIK);
- source / Wind field used to verify each mapping;
- qualification state.

If the Q0 seed ticker is wrong or stale, do not silently overwrite it. Emit `identifier_exception` with old value, proposed value, reason and source.

## Phase 2｜Coverage matrix

For each asset and each domain below, report earliest available date, latest available date, frequency, point-in-time timestamp support, and material gaps:

1. daily market data;
2. corporate actions;
3. financial statements;
4. filing/publication dates;
5. consensus estimates and historical snapshots;
6. announcements/filings;
7. news metadata;
8. industry/operating metrics where available.

Use states only from:

`verified / partial / missing / ambiguous_identifier_history / vendor_unavailable / license_blocked / timestamp_unqualified`.

## Phase 3｜Point-in-time audit

For each data domain answer explicitly:

- what is the event/effective date?
- what is the first-publication or vendor-availability timestamp?
- can a query be reconstructed as of a past date without current-value backfill?
- are revisions/restatements separately timestamped?
- can historical estimate snapshots be retrieved, or only latest consensus?

Any domain lacking a reliable availability timestamp must be marked `timestamp_unqualified` for replay use.

## Phase 4｜Wind licensing/storage boundary

State what the Wind license allows for:

- local cache;
- NAS archival;
- programmatic export;
- derived metadata;
- sharing raw licensed rows in GitHub;
- storing query recipes / Wind field names / coverage receipts.

Do not guess. If the client/license-specific boundary cannot be verified, mark `license_blocked` and identify the exact question requiring account-owner confirmation.

## Phase 5｜AI value-chain evidence

For each Q0 `primary_node`, locate at least one company-origin or filing-origin source supporting that mapping. Return only citation metadata / short factual claim / locator. A market-consensus narrative alone is insufficient.

## Required outputs

Return these seven blocks/files:

1. `01_ASSET_IDENTIFIER_REGISTRY.json`
2. `02_WIND_VENDOR_MAPPING.csv`
3. `03_DATA_COVERAGE_MATRIX.csv`
4. `04_POINT_IN_TIME_AUDIT.md`
5. `05_WIND_LICENSE_BOUNDARY.md`
6. `06_VALUE_CHAIN_EVIDENCE.json`
7. `07_Q1_EXCEPTION_REPORT.md`

## Required summary

At the end report:

- assets verified / 30;
- identifier exceptions;
- domains with historical point-in-time support;
- domains that are current-only;
- missing coverage hot spots;
- licensing questions still open;
- whether the package is `READY_FOR_Q1_HUMAN_REVIEW` or `PARTIAL_BLOCKED`.

`READY_FOR_Q1_HUMAN_REVIEW` does not authorize Q2 or any production ingestion.