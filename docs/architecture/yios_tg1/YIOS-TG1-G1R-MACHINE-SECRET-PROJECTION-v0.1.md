# YIOS-TG1-G1R｜Machine Secret Projection v0.1

Status: **IMPLEMENTATION CANDIDATE / HUMAN SECURITY GATE REQUIRED**

## Why

The GOLD2 G6/G7 launchd job is unattended. Yuanli Secret Constitution does not allow a permanent dependency on a human-unlocked personal 1Password vault.

G1 core Reality Sink is already physically proven. G1R only concerns machine-safe runtime projection.

## Candidate architecture

```text
1Password Canon
  └─ dedicated non-Personal machine vault
       └─ Supabase server credential
             ↓
1Password Service Account (read_items only)
             ↓
OP_SERVICE_ACCOUNT_TOKEN
  └─ local macOS Keychain runtime projection
             ↓
run_ymq_gold2_live_shadow_machine.sh
             ↓
op run --env-file value-free.env.op
             ↓
G6/G7
             ↓
YIOS-TG1 Product Sink hook
             ↓
Supabase service-role-only RPC
```

## Safety rules

- No secret value in Git, Notion, LaunchAgent plist, logs or `.env.op`.
- `.env.op` contains only `op://` addresses plus non-secret config.
- Service Account gets only the minimum machine vault and `read_items`.
- Service Account token is never written to the LaunchAgent plist.
- The token's local projection is macOS Keychain, retrieved at runtime.
- The wrapper refuses any `.env.op` containing the `sb_secret_` prefix.
- Sink remains opt-in and `SHADOW_ONLY`.
- G6/G7 receipt persistence occurs before Product Sink invocation.
- Product Sink failure never mutates the existing research receipt.

## Current provider capability

Installed 1Password CLI supports:

`op service-account create`

The CLI documentation states the token is returned once and must be treated like a password. Service Accounts cannot access Personal or Private vaults, so a dedicated machine-readable non-Personal vault is required.

## Human security gate

Activation requires explicit approval to create/bind a scoped machine identity and runtime token projection.

This document does not create the Service Account and does not activate launchd.

## Activation acceptance

1. dedicated machine vault exists;
2. required Supabase item is available to that vault without plaintext migration into Git/files;
3. Service Account is read-only and scoped only to the machine vault;
4. service-account token is stored in macOS Keychain without log disclosure;
5. value-free `.env.op` resolves successfully;
6. wrapper smoke check runs without printing secret material;
7. launchd ProgramArguments switch to the machine wrapper;
8. next independent G6/G7 day auto-sinks to Supabase exactly once;
9. authority remains `SHADOW_ONLY`.
