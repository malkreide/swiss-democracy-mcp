## Finding: ARCH-005

**Severity:** critical
**Status:** Open
**Check:** ARCH-005  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Kern erfüllt (keine Hardcoded Secrets), aber die Defense-in-Depth-Hygiene fehlt vollständig.

### Evidence
- Keine Hardcoded Secrets im Code (grep clean)
- SRGSSR-Credentials werden aus `os.environ.get` geladen, ohne Real-Key-Defaults (server.py:145-146)
- Keine Secrets in Logs (kein Logging vorhanden)

### Gaps
- Keine `.gitignore` im Repo → `.env` nicht ausgeschlossen
- Keine `.env.example` mit Platzhaltern
- Kein CI-Secret-Scan (gitleaks/trufflehog) in den Workflows
- Credentials als `str`, nicht `SecretStr`

### Expected Behavior
Env-Vars als Minimum + .gitignore/.env.example + CI-Secret-Scan + SecretStr-Repräsentation.

### Remediation
1) `.gitignore` mit `.env`,`.env.*` (ausser `.env.example`). 2) `.env.example` committen. 3) gitleaks-Action in CI. 4) Credentials als `SecretStr`.

### Effort
S — < 1 Tag.

