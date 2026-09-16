# YOS-FIN1-G0｜Wind × MiaoXiang × WenCai Three-Source Reality Proof — Design

## Status
USER_APPROVED_FOR_IMPLEMENTATION

## Mother Question
Can Yuanli Investment OS route a finance research request to Wind, Eastmoney MiaoXiang, or iWenCai without allowing any provider to become sovereign research authority, and can it distinguish independent evidence from discovery/screening output?

## Scope
G0 is a bounded three-probe qualification, not a production migration and not a trading system.

1. Macro corroboration: one macro fact queried from Wind and MiaoXiang.
2. Equity fact corroboration: one listed-company fundamental queried from Wind and MiaoXiang.
3. Natural-language screening: one A-share screen from iWenCai, followed by provider verification of returned candidates where available.

## Provider Authority
- Wind structured data: `REALITY_EVIDENCE / EVIDENCE_ONLY`.
- MiaoXiang structured data: `REALITY_EVIDENCE / EVIDENCE_ONLY` only after source/provenance and as-of fields are present.
- MiaoXiang search/AI text: `AUTHORED_KNOWLEDGE / KNOWLEDGE_CANDIDATE_INPUT`.
- iWenCai official/open structured data: `RESEARCH_CANDIDATE`; may become evidence only after explicit PIT/provenance validation.
- iWenCai natural-language screening: `RESEARCH_CANDIDATE / NO_EVIDENCE_AUTHORITY`.
- Browser automation / reverse-engineered iWenCai: `DISCOVERY_ONLY / NO_CANON_AUTHORITY`.

## Architecture
`Research Request → Finance Source Router → Provider Adapter → Normalized Provider Receipt → Cross-Provider Comparator → Research Candidate`

Provider-specific field names never redefine canonical economic semantics. Raw provider bodies and secrets do not enter Git. Independent corroboration requires distinct provider roots; repeated queries against one provider do not increase evidence-root count.

## G0 Provider Contract
Each adapter exposes a provider-neutral result envelope with:
- provider
- provider_class
- request_kind
- query_fingerprint
- observed_at
- effective_at / known_as_of when available
- instrument_or_series
- normalized_fields
- provenance
- authority_ceiling
- evidence_root_id
- response_hash
- raw_body_persisted=false
- error_code / error_class on fail-closed paths

## Probe A — Macro
Target: US long real yield (or the nearest semantically equivalent official series available in each provider).
Victory condition: both providers return independently rooted, time-stamped values or one provider fails closed with a typed reason; no forced numerical agreement.

## Probe B — Equity Fundamental
Target: Kweichow Moutai / 600519.SH ROE and/or PB with explicit reporting/trading date semantics.
Victory condition: both providers return comparable fields with explicit period semantics, or mismatch is surfaced as `SEMANTIC_MISMATCH` / `PIT_MISMATCH` rather than averaged away.

## Probe C — Natural-Language Screening
Query: low PB + stable/high ROE A-share universe, with a small deterministic result cap.
Victory condition: iWenCai produces a candidate universe; the result remains research-candidate only; at least one returned candidate can be verified through a structured provider when credentials/provider access permit.

## Routing Policy
- `macro_fact` → Wind first, MiaoXiang corroboration.
- `listed_company_fact` → Wind or MiaoXiang; corroborate when material.
- `natural_language_screen` → iWenCai first; verification delegated to structured providers.
- Provider unavailability never silently falls back to general model knowledge.

## Failure Taxonomy
`AUTH_MISSING`, `AUTH_REJECTED`, `QUOTA_OR_CREDIT_BLOCK`, `ENDPOINT_DRIFT`, `SCHEMA_DRIFT`, `ENTITY_UNRESOLVED`, `PIT_MISSING`, `SEMANTIC_MISMATCH`, `PROVIDER_UNAVAILABLE`, `DISCOVERY_ONLY`, `UNKNOWN`.

## Security
Credentials are read only from user-local config/env and never printed. Git stores only sanitized metadata, tests, adapters, and receipts with hashes. No cookies, bearer tokens, API keys, or raw authenticated payloads are committed.

## Non-Authorizations
G0 does not authorize capital, sizing, execution, broker calls, VeighNa, portfolio changes, automatic Canon promotion, or automatic evidence admission into higher-authority investment conclusions.

## Done Definition
- contract + router + adapters + comparator exist;
- provider-specific tests pass;
- at least one real Wind probe executes or fails closed for the already-known credit/key issue;
- MiaoXiang and iWenCai credential discovery is performed without secret disclosure;
- if credentials are present, bounded live probes run; if absent, exact Human Gate is recorded;
- repository regression passes;
- secret scan passes;
- Draft PR opened and stopped at Human Review before any production scheduler or Canon promotion.
