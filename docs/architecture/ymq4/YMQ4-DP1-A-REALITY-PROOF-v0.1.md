# YMQ4-DP1-A｜External Runtime × Source Authority Reality Proof v0.1

Status: `CLOUD_PROJECT_READY / CREDENTIAL_GATE_OPEN`

## Mission

Prove one physical, auditable path:

`GitHub Actions → FRED/ALFRED → immutable raw SHA → Supabase private S3 object → service-role-only RPC → evidence.source_snapshots → pit.observations → readback → reality_gate_runs`.

The proof does **not** authorize B2–B7, trading, allocation, evidence promotion, A9 canon switch, or Supabase→GitHub Canon mutation.

## Authority boundary

- GitHub remains normative Canon / contract authority.
- Supabase is an operational research-state and evidence-metadata plane only.
- GitHub Actions is an external execution plane.
- `yuanli-health` is explicitly out of scope; DP1-A uses the dedicated `yuanli-invest-runtime` project.
- Public repo contains code/contracts only. Raw source payloads and secrets must never be committed.

## Cloud resource frozen for this proof

- Supabase project: `yuanli-invest-runtime`
- Project ref: `tbmoimbdhsrltvospwpu`
- Region: `us-east-2`
- Private raw bucket: `ymq4-raw-evidence`

The project URL and project ref are identifiers, not credentials. Elevated keys remain secret-only.

## Minimal proof object

DP1-A intentionally uses one revisionable official statistic: `CPIAUCSL`, observation `2020-02-01`.

The FRED API request must use `output_type=4` (initial release). `realtime_start` from that row is frozen as release/vintage/known-as-of for the proof. A second as-of request at that exact date must return the same value.

## Credential separation

The GitHub worker must use four repository secrets and no secret may be pasted into source control:

- `FRED_API_KEY`
- `YMQ4_SUPABASE_SECRET_KEY` — a modern `sb_secret_...` backend key, sent to PostgREST on the `apikey` header only.
- `YMQ4_SUPABASE_S3_ACCESS_KEY_ID` — dedicated server-side Storage S3 credential.
- `YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY` — paired S3 secret.

The legacy JWT-based service-role key is deliberately not required by DP1-A.

## PASS conditions

1. GitHub-hosted runner resolves and reaches FRED, Supabase API and Supabase Storage hosts.
2. FRED and Supabase elevated credentials exist only as GitHub Actions secrets.
3. Initial-release row exposes four-clock semantics.
4. Same-day as-of cross-check matches initial release.
5. Raw evidence envelope is written to the private Supabase S3 bucket.
6. SHA-256 after S3 readback equals the pre-upload SHA and object metadata carries the same SHA.
7. Service-role-only RPC writes `evidence.source_snapshots` and `pit.observations`.
8. RPC readback returns identical value, four clocks, raw SHA and object locator.
9. `runtime.reality_gate_runs` stores a non-secret PASS receipt tied to Git SHA.
10. No raw payload or secret is committed to the public repository.

Any failed condition means `FAIL_CLOSED`.

## Current machine/cloud state

- dedicated investment Supabase project: `PASS`
- DB project health: `ACTIVE_HEALTHY`
- evidence/pit/runtime migration: `PASS`
- RLS enabled on all DP1-A internal tables: `PASS`
- anon/authenticated execute privilege on DP1-A RPCs: `DENIED`
- service_role execute privilege on DP1-A RPCs: `ALLOWED`
- private raw bucket: `PASS`
- GitHub-hosted external runtime preflight: `PASS`
- full credentialed physical proof: `OPEN`

Security Advisor's `RLS Enabled No Policy` notices on the internal DP1-A tables are intentional fail-closed posture: no anon/authenticated table policy is created. The external worker reaches these objects only through the narrow service-role-only RPC surface.

## Remaining Human Gate

Create/copy the four secrets above in their native provider dashboards, then enter them under GitHub repository **Settings → Secrets and variables → Actions**. Do not paste secret values into chat, issues, PR comments, workflow YAML, or source files.

After those four secrets exist, manually dispatch `YMQ4 DP1-A Reality Proof` on branch `ymq4-dp1a-external-runtime-reality-proof` with `mode=full` unless an authorized workflow-dispatch tool is available.

## Source authority upgrade for 1978–79

When DP1-A passes and historical backfill begins, use Federal Reserve trade-weighted dollar history (`TWEXMMTH`/successor lineage) instead of a private DXY mirror where coverage permits. Keep `TB3MS - trailing known CPI YoY` explicitly labelled `HISTORICAL_PROXY`; it is not equivalent to 10Y TIPS real yield.

## Stop condition

DP1-A PASS authorizes only the next data-plane battle (`DP1-B historical backfill candidate`). It does not authorize model tuning after reality reveal.
