# YIOS-TG1-G1R｜Machine Runtime Projection v0.2

Status: **HUMAN AUTHORIZED / MACHINE TOKEN CANONIZED / KEYCHAIN PROJECTION PROVEN / EDGE GATEWAY ACTIVE / LAUNCHD ACTIVATION CANDIDATE**

## Final architecture

```text
1Password Canon
  └─ Yuanli-Machine-YIOS-TG1
       └─ YIOS-TG1-Machine-Ingest-Token
             ↓ one-time controlled projection
macOS Keychain
  └─ yuanli.yios-tg1.machine-ingest-token
             ↓ runtime only
run_ymq_gold2_live_shadow_machine.sh
             ↓
G6 / G7
             ↓
yios_tg1_gold2_machine_sink.py
             ↓ scoped token only
Supabase Edge Function: yios-tg1-g1-ingest
             ↓ cloud-internal service authority
G1 governed RPC
             ↓
Evidence / PIT / Data Health / GOLD Research State
```

## Security result

The M4 machine **does not receive Supabase service-role authority**.

The local machine token is scoped only to:

`YIOS_TG1_G1_GOLD2_INGEST_ONLY`

The live token value is not stored in Git, Notion, LaunchAgent plist or logs.

1Password remains Canon. macOS Keychain is the native unattended runtime projection.

## Proven Reality

- dedicated machine vault created;
- single-purpose ingest token generated in 1Password;
- token fingerprint registered in Supabase runtime;
- Keychain projection fingerprint equals the 1Password Canon fingerprint;
- Edge Gateway deployed with custom token authentication;
- real 2026-09-22 GOLD2 receipt passed through the Edge Gateway;
- write returned the same governed ingest key / state / observation IDs;
- authority remained `SHADOW_ONLY`;
- no machine-side service-role secret was required.

## Launchd rules

The legacy installer remains available and unchanged.

Machine activation uses:

`scripts/install_ymq_gold2_live_shadow_machine_launchd.sh`

The generated plist contains only non-secret configuration:

- Wind CLI path
- runtime directory
- machine sink client path
- Edge endpoint
- client id
- Keychain service name

The machine ingest token itself is fetched from Keychain at process start and exported only to the child runtime environment.

## Fail-closed semantics

- missing Keychain projection → wrapper exits before G6;
- missing machine client → installer/wrapper fails closed;
- invalid machine token → Edge returns 401;
- provider failure → G1 Data Health = DEGRADED, 0 observations, no new research state;
- product sink failure never rewrites the persisted G6/G7 receipt;
- no path grants capital / sizing / execution / Broker / VeighNa / Canon promotion.

## Remaining acceptance

After source PRs are merged and the machine installer is activated:

1. run an immediate same-day idempotent activation smoke;
2. verify no duplicate sample creation;
3. verify plist contains no secret material;
4. verify next independent natural-day G6/G7 receipt auto-sinks exactly once;
5. only after that mark G1R fully accepted.
