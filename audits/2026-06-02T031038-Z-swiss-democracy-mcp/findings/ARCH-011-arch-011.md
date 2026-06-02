## Finding: ARCH-011

**Severity:** medium
**Status:** Open
**Check:** ARCH-011  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Repo-Struktur weitgehend standardkonform, aber CHANGELOG.md fehlt.

### Evidence
- README.md, README.de.md, LICENSE, pyproject.toml vorhanden
- src/-Layout korrekt, tests/, .github/workflows/ (ci.yml + publish.yml) vorhanden

### Gaps
- `CHANGELOG.md` fehlt

### Expected Behavior
Alle Top-Level-Pflicht-Files inkl. CHANGELOG.md.

### Remediation
`CHANGELOG.md` im Keep-a-Changelog-Format anlegen.

### Effort
S — < 1 Tag.

