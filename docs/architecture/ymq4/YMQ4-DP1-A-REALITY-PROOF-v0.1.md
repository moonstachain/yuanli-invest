# YMQ4-DP1-A｜External Runtime × Source Authority Reality Proof v0.1

Status: `IMPLEMENTATION_CANDIDATE / CLOUD_GATE_OPEN`

## Mission

Prove one physical, auditable path:

`GitHub Actions → FRED/ALFRED → immutable raw SHA → Supabase private object → evidence.source_snapshots → pit.observations → readback → reality_gate_runs`.

The proof does **not** authorize B2–B7, trading, allocation, evidence promotion, A9 canon switch, or Supabase→GitHub Canon mutation.

## Authority boundary

- GitHub remains normative Canon / contract authority.
- Supabase is an operational research-state and evidence-metadata plane only.
- GitHub Actions is an external execution plane.
- `yuanli-health` is explicitly out of scope; DP1-A requires a dedicated investment project.
- Public repo contains code/contracts only. Raw source payloads and secrets must never be committed.

## Minimal proof object

DP1-A intentionally uses one revisionable official statistic: `CPIAUCSL`, observation `2020-02-01`.

The FRED API request must use `output_type=4` (initial release). `realtime_start` from that row is frozen as release/vintage/known-as-of for the proof. A second as-of request at that exact date must return the same value.

## PASS conditions

1. GitHub-hosted runner resolves and reaches FRED hosts.
2. FRED secret is present only as a GitHub Actions secret.
3. Initial-release row exposes four-clock semantics.
4. Same-day as-of cross-check matches initial release.
5. Raw evidence envelope is written to a **private** Supabase Storage bucket.
6. SHA-256 after authenticated readback equals the pre-upload SHA.
7. `evidence.source_snapshots` row is written and read back.
8. `pit.observations` row is written with all four clocks and read back.
9. `runtime.reality_gate_runs` stores a non-secret PASS receipt tied to Git SHA.
10. No raw payload or secret is committed to the public repository.

Any failed condition means `FAIL_CLOSED`.

## Human/cloud gates still required

- Create a dedicated Supabase project, recommended name `yuanli-invest-runtime`.
- Apply the candidate DP1-A migration to that project.
- Add GitHub Actions secrets: `FRED_API_KEY`, `YMQ4_SUPABASE_URL`, `YMQ4_SUPABASE_SERVICE_ROLE_KEY`.
- Manually dispatch `YMQ4 DP1-A Reality Proof` with `mode=full`.

## Source authority upgrade for 1978–79

When DP1-A passes and historical backfill begins, use Federal Reserve trade-weighted dollar history (`TWEXMMTH`/successor lineage) instead of a private DXY mirror where coverage permits. Keep `TB3MS - trailing known CPI YoY` explicitly labelled `HISTORICAL_PROXY`; it is not equivalent to 10Y TIPS real yield.

## Stop condition

DP1-A PASS authorizes only the next data-plane battle (`DP1-B historical backfill candidate`). It does not authorize model tuning after reality reveal.
