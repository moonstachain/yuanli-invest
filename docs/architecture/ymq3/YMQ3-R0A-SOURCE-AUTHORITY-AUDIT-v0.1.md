# YMQ3-R0A｜Source Authority Audit v0.1

**Stage:** `YMQ3-R0A`  
**Status:** `IMPLEMENTATION_CANDIDATE / NOT_CANON`  
**Registry:** `config/ymq3/r0a_source_registry.v0.1.json`

## 1｜Purpose

This audit decides what each candidate source is allowed to do inside YMQ3-R0A. It does not ask only whether a URL opens. It separates access from authority.

For every source, the machine registry records four independent rights axes:

1. processing authority;
2. raw-storage authority;
3. derived-feature-storage authority;
4. redistribution authority.

`PUBLICLY_READABLE != RAW_STORAGE_ALLOWED`.

`UNKNOWN = DENY` for the requested action.

## 2｜Authority classes

- `ADMIT` — the source can participate for its declared role under the recorded rights boundary.
- `ANNOTATION_ONLY` — human chronology/annotation support only; it cannot become the primary Story corpus unless separately admitted.
- `UNKNOWN_DENY` — unresolved rights/provenance; no machine Story admission.
- `REJECT` — explicitly unsuitable for the declared role.

Timestamp authority remains independent:

- `TS1_SOURCE_NATIVE`
- `TS2_ARCHIVE_VERIFIED`
- `TS3_PROVIDER_INDEXED`
- `TS4_INFERRED_RETROSPECTIVE`

`TS4` is forbidden from Story features.

## 3｜Key physically verified findings

### ALFRED / FRED

ALFRED is explicitly designed to preserve real-time periods for values as originally released and later revised. It is therefore an admitted U.S. macro-vintage source. FRED terms can depend on underlying source rights, so the registry does not infer unrestricted raw redistribution rights for every series.

Evidence:
- https://fred.stlouisfed.org/docs/api/fred/alfred.html
- https://fred.stlouisfed.org/legal/

### SEC EDGAR

SEC documents free public access/download, structured indexes, APIs and fair-access automation. EDGAR reaches back to 1994/1995 and provides filing dates and accession paths. It is admitted for corporate-disclosure evidence and PIT chronology. Filing-body intellectual-property rights can belong to issuers, so unrestricted raw-text redistribution is not inferred.

Evidence:
- https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

### Federal Reserve Board official material

The Board states that, unless otherwise indicated, information on its website is in the public domain and may be copied/distributed with citation. Third-party material is excluded. Board-native text is admitted as an official anchor source.

Evidence:
- https://www.federalreserve.gov/disclaimer.htm

### WHO

WHO permits extracts for research/private study with acknowledgement, while substantial reproduction and commercial uses can require explicit permission unless a specific publication carries a broader Creative Commons licence. WHO is therefore annotation-only by default for this audit; exact material-specific licences may later widen rights.

Evidence:
- https://www.who.int/about/policies/terms-of-use
- https://www.who.int/about/policies/publishing/copyright

### GDELT

GDELT states that all datasets released by the project are available for unlimited and unrestricted academic, commercial or governmental use, without fee, and may be redistributed with citation. GDELT 2.0 begins on 2015-02-19 and provides 15-minute updates plus Mentions timestamps; GDELT 1.0 provides a longer event-history layer.

Important boundary: GDELT dataset rights do not grant rights to republish third-party article bodies linked from GDELT. R0A therefore admits GDELT metadata/dataset fields, not mirrored publisher article text.

Evidence:
- https://gdeltproject.org/about.html
- https://gdeltproject.org/data.html
- https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/
- https://blog.gdeltproject.org/the-datasets-of-gdelt-as-of-february-2016/

### Google Books Ngram

Google states that Ngram Viewer graphs and data may be freely used for any purpose. It is therefore rights-clean as a contextual dataset, but its book/annual semantics do not make it a weekly contemporaneous news Story corpus.

Evidence:
- https://books.google.com/ngrams/info

### Google Trends

Google describes Trends as sampled, normalized search-interest data containing statistical noise and explicitly warns that it is not a scientific poll or perfect mirror of search activity. No Story-truth authority is granted. It remains an attention proxy, and machine-use/storage rights remain unresolved in this registry.

Evidence:
- https://support.google.com/trends/answer/4365533

### Internet Archive Wayback

Wayback can support archive-capture provenance, but archive access does not transfer the copyright/processing rights of third-party captured pages. Until a specific use/right path is verified, it remains `UNKNOWN_DENY` for machine Story processing.

Evidence:
- https://archive.org/about/terms

### China official sources

CSRC, PBOC, NBS, SSE, SZSE and CNINFO are retained as candidate chronology/official-primary sources. Dated official releases may support annotation and vintage reconstruction. However, this audit does not infer machine-processing, raw-storage or redistribution rights from public readability. Those axes remain unresolved unless later verified.

A critical temporal constraint is already known: GDELT 2.0 starts in February 2015, so it cannot by itself cover the `C3_CHINA_LEVERAGE` case from 2014-07-01.

## 4｜Unresolved capability classes

Two capability placeholders remain deliberately fail-closed:

- `LICENSED_EN_NEWS_ARCHIVE`
- `LICENSED_CN_FIN_NEWS_ARCHIVE`

Neither is a provider. Both remain `UNKNOWN_DENY` until a named vendor/product, machine-access path and contractual text/data-mining rights are physically audited.

They cannot be converted to `ADMIT` because a vendor marketing page says historical news is available.

## 5｜Scientific implications

This audit already rules out several shortcuts:

- SEC filings alone cannot prove broad Dot-com Narrative diffusion.
- GDELT 1.0 event metadata cannot be silently promoted into a multi-publisher full-text Story corpus.
- Google Trends cannot substitute for Narrative truth.
- Current revised Chinese macro series cannot substitute for dated historical releases.
- Open web accessibility cannot substitute for computational-research rights.

The next stage must therefore probe source families physically, then measure case-level weekly corpus sufficiency. No Story feature or model is authorized by this document.
