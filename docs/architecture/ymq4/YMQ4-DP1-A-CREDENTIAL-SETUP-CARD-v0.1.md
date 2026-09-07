# YMQ4-DP1-A｜Credential Setup Card v0.1

Status: `HUMAN_INPUT_REQUIRED`

Do **not** paste any credential into ChatGPT, GitHub issues/PR comments, source files, workflow YAML, or Notion.

## 1. FRED

Create or retrieve a FRED API key from the FRED account/API key page.

Add it to `moonstachain/yuanli-invest` → **Settings → Secrets and variables → Actions → New repository secret** as:

`FRED_API_KEY`

## 2. Supabase backend secret key

Project: `yuanli-invest-runtime` (`tbmoimbdhsrltvospwpu`).

In Supabase Dashboard → project → **Settings → API Keys** → **Publishable and secret API keys**, create a dedicated server-side secret key named, for example:

`ymq4-dp1a-github-worker`

Copy the `sb_secret_...` value once and store it as GitHub Actions repository secret:

`YMQ4_SUPABASE_SECRET_KEY`

Do not use a publishable key and do not use the legacy JWT service-role key for this proof.

## 3. Supabase Storage S3 server credentials

In Supabase Dashboard → project → **Storage → S3 / S3 configuration**, create a dedicated server-side S3 credential pair for the DP1-A GitHub worker.

Store the pair as GitHub Actions repository secrets:

- `YMQ4_SUPABASE_S3_ACCESS_KEY_ID`
- `YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY`

These S3 credentials are elevated server credentials and bypass Storage RLS. Never expose them to client code.

## 4. Completion signal

After all four repository secrets exist, return to the research conversation and reply only:

`DP1A_CREDENTIALS_READY`

No secret values are required in the message.

The next machine action is to dispatch `YMQ4 DP1-A Reality Proof` on branch `ymq4-dp1a-external-runtime-reality-proof` with `mode=full`, then independently verify raw SHA, four clocks, PIT ledger, provenance and reality-gate readback.
