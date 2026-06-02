# Secret management — swiss-democracy-mcp

## Current posture (Stufe 1 — plain env vars, documented)
Only the optional SRGSSR Polis tools need credentials
(`SRGSSR_CONSUMER_KEY`, `SRGSSR_CONSUMER_SECRET`). They are loaded via
`pydantic-settings` and held in memory as `SecretStr`, so they do not leak
through reprs or structured logs.

Plain environment variables (Stufe 1 in the audit catalogue) are **acceptable
here** because:
- Data class is **Public Open Data** (no PII / Verwaltungsdaten).
- The SRGSSR free-tier key gates a public, rate-limited API — low blast radius.
- No secret is hardcoded; `.env` is git-ignored and `.env.example` carries only
  placeholders.

## Hardening path (if promoted beyond demo use)
- **Stufe 3 — Secret Manager:** load credentials from AWS Secrets Manager
  (eu-central-1), Azure Key Vault (Switzerland/EU) or GCP Secret Manager (EU).
- **Stufe 4 — Workload identity:** avoid long-lived keys entirely.

## CI
A Gitleaks scan runs on every push/PR to catch accidental secret commits.
