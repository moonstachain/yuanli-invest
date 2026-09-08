# YMQ4-DP1-A｜External Runtime × Source Authority Reality Proof v0.1

Status: `REALITY_PROOF_PASS / READY_FOR_DP1-B`

## Mission

Prove one physical, auditable path:

`GitHub Actions → FRED/ALFRED → immutable raw SHA → Supabase private S3 object → service-role-only RPC → evidence.source_snapshots → pit.observations → readback → reality_gate_runs`.

The proof does **not** authorize trading, allocation, evidence promotion, A9 Canon switch, broker connection, or live execution.

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

DP1-A intentionally used one revisionable official statistic: `CPIAUCSL`, observation `2020-02-01`.

The FRED API request used `output_type=4` (initial release). `realtime_start` from that row was frozen as release/vintage/known-as-of. A second as-of request at that exact date returned the same value.

## Credential separation

The GitHub worker uses four repository secrets and no secret is stored in source control:

- `FRED_API_KEY`
- `YMQ4_SUPABASE_SECRET_KEY` — modern `sb_secret_...` backend key, sent to PostgREST on the `apikey` header only.
- `YMQ4_SUPABASE_S3_ACCESS_KEY_ID` — dedicated server-side Storage S3 credential.
- `YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY` — paired S3 secret.

The legacy JWT-based service-role key is deliberately not required by DP1-A.

## PASS conditions and settlement

All ten DP1-A PASS conditions were satisfied in workflow run `34183899109` at Git SHA `218546da8ea792d297c2c5b0f5e893cfdb77704e`:

1. GitHub-hosted runner reached FRED, Supabase API and Supabase Storage.
2. Elevated credentials existed only as GitHub Actions secrets and were masked in logs.
3. Initial-release row exposed four-clock semantics.
4. Same-day as-of cross-check matched the initial release.
5. Raw evidence envelope was written to the private Supabase S3 bucket.
6. SHA-256 after S3 readback matched the pre-upload SHA and object metadata.
7. Service-role-only RPC wrote `evidence.source_snapshots` and `pit.observations`.
8. RPC readback returned identical value, four clocks, raw SHA and object locator.
9. `runtime.reality_gate_runs` stored a non-secret PASS receipt tied to Git SHA.
10. No raw payload or secret was committed to the public repository.

## Frozen Reality Receipt

- source: `FRED/ALFRED`
- series: `CPIAUCSL`
- value: `259.05`
- observation: `2020-02-01`
- release: `2020-03-11`
- vintage: `2020-03-11`
- known-as-of: `2020-03-11`
- raw SHA-256: `411f658127c93fee114a329d2845ec35436728f0740ae64affa9000a0d28051f`
- snapshot: `842dee92-7504-4657-ac03-c1d90663f8b9`
- PIT observation: `f1b48838-e581-486c-b68c-41a569a5db6a`
- reality gate run: `eacbb25e-74ea-4843-aa0a-c9e3d7535912`
- artifact: `10039841220`

Security Advisor's `RLS Enabled No Policy` notices on the internal DP1-A tables remain intentional fail-closed posture: no anon/authenticated table policy is created. The external worker reaches these objects only through the narrow privileged RPC surface.

Repository `governance` passed. Repository `contracts` remains red at the pre-existing YIM0 methodology projection scope-window check and is classified `NON_DP1A_BLOCKER`; DP1-A did not modify unrelated Canon to make that check green.

## DP1-B authority now opened

DP1-A PASS authorizes only the historical data-plane extension `YMQ4-DP1-B｜Gold 1978–2026 Historical PIT Backfill` under the already frozen rule:

`DATA REVEAL → MODEL FREEZE`

DP1-B may add governed historical evidence and PIT/as-of materialization. It may not tune, alter, or execute B2–B7 model logic merely because historical outcomes become visible.

## Measurement-regime boundary for DP1-B

For 1978–2002, real-rate exposure remains a historical proxy rather than a modern TIPS-equivalent measure. Historical market series may be explicitly classified `PIT_MARKET_RECONSTRUCTED`; that label must never be silently upgraded to strict-vintage evidence.

## Final settlement

`YMQ4-DP1-A｜REALITY PROOF PASS`
