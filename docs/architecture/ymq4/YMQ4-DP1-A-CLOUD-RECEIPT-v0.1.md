# YMQ4-DP1-A｜Cloud Resource Receipt v0.1

Status: `REALITY_PROOF_PASS / CLOSED_FOR_IMPLEMENTATION`

This receipt records non-secret infrastructure and Reality Proof facts only.

- Supabase project name: `yuanli-invest-runtime`
- project ref: `tbmoimbdhsrltvospwpu`
- organization: `pitqhsyptqbxknxrcpzo`
- region: `us-east-2`
- project state: `ACTIVE_HEALTHY`
- project creation cost confirmed by Human Gate: `$0/month`
- DP1-A base migration: applied
- DP1-A service-role-only RPC hardening migration: applied
- private raw Storage bucket `ymq4-raw-evidence`: `public=false`
- RLS: enabled on all four DP1-A internal tables
- `anon` / `authenticated` RPC execute privilege: denied
- `service_role` RPC execute privilege: allowed
- performance hardening: PIT observation source-snapshot FK index created

## Physical Reality Proof

- workflow run: `34183899109` — `success`
- Git SHA: `218546da8ea792d297c2c5b0f5e893cfdb77704e`
- artifact: `10039841220` — `ymq4-dp1a-reality-receipt`
- source: `FRED/ALFRED`
- series: `CPIAUCSL`
- value: `259.05`
- observation date: `2020-02-01`
- release date: `2020-03-11`
- vintage date: `2020-03-11`
- known as of: `2020-03-11`
- raw SHA-256: `411f658127c93fee114a329d2845ec35436728f0740ae64affa9000a0d28051f`
- source snapshot: `842dee92-7504-4657-ac03-c1d90663f8b9`
- PIT observation: `f1b48838-e581-486c-b68c-41a569a5db6a`
- reality gate run: `eacbb25e-74ea-4843-aa0a-c9e3d7535912`

All DP1-A machine checks passed: external runtime, source reachability, initial release, same-day as-of cross-check, raw-storage SHA readback, modern secret RPC ingest, provenance readback, and PIT ledger write/readback.

Repository `governance` passed. Repository `contracts` remains red only at the pre-existing YIM0 methodology projection scope-window check and is recorded as `NON_DP1A_BLOCKER`.

No credential value, raw FRED payload, Canon promotion, B2–B7 execution, broker connection, or trading action is recorded here.
