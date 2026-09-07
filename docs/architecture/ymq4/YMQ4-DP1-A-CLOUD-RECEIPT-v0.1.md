# YMQ4-DP1-A｜Cloud Resource Receipt v0.1

Status: `CLOUD_PROJECT_READY / CREDENTIAL_GATE_OPEN`

This receipt records non-secret infrastructure facts only.

- Supabase project name: `yuanli-invest-runtime`
- project ref: `tbmoimbdhsrltvospwpu`
- organization: `pitqhsyptqbxknxrcpzo`
- region: `us-east-2`
- project state observed after creation: `ACTIVE_HEALTHY`
- project creation cost confirmed by Human Gate: `$0/month`
- DP1-A base migration: applied
- DP1-A service-role-only RPC hardening migration: applied
- private raw Storage bucket `ymq4-raw-evidence`: created and verified `public=false`
- RLS: enabled on all four DP1-A internal tables
- `anon` / `authenticated` RPC execute privilege: denied
- `service_role` RPC execute privilege: allowed
- performance hardening: PIT observation source-snapshot FK index created
- full credentialed source→raw→ledger→readback proof: not yet run

No credential value, raw FRED payload, or Canon promotion is recorded here.
