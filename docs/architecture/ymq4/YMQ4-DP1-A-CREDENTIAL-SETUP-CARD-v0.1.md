# YMQ4-DP1-A｜Credential Setup Card v0.1

Status: `COMPLETED / ARCHIVED`

The credential setup gate is closed. This document remains as a non-secret operational record of the credential boundary used by the successful DP1-A Reality Proof.

Do **not** paste any credential into ChatGPT, GitHub issues/PR comments, source files, workflow YAML, or Notion.

## Credential contract used by DP1-A

GitHub Actions repository secrets:

- `FRED_API_KEY`
- `YMQ4_SUPABASE_SECRET_KEY`
- `YMQ4_SUPABASE_S3_ACCESS_KEY_ID`
- `YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY`

Supabase project: `yuanli-invest-runtime` (`tbmoimbdhsrltvospwpu`).

The backend API credential is a modern `sb_secret_...` server-side key. Storage uses a dedicated server-side S3 credential pair. The workflow does not require the legacy JWT service-role key.

## Closure evidence

- full workflow run: `34183899109` — `success`
- Git SHA: `218546da8ea792d297c2c5b0f5e893cfdb77704e`
- Reality settlement: `YMQ4-DP1-A｜PASS`
- secrets were consumed by GitHub Actions and remained masked in logs
- raw source evidence was stored only in the private Supabase bucket

Credential values are intentionally not recorded and cannot be reconstructed from this document.

## Rotation rule

If any credential is rotated, preserve the same GitHub secret names so the workflow contract does not change. Rotation alone does not reopen DP1-A unless the Reality Proof can no longer reproduce successfully.
