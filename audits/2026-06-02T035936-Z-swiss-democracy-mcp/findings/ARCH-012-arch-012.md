## Finding: ARCH-012

**Severity:** medium
**Status:** Open
**Check:** ARCH-012  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Spec-Versionierungs-Disziplin grösstenteils hergestellt; ein hartes Pinning der protocolVersion im Code erfolgt nicht (vom SDK verwaltet).

### Evidence
- CHANGELOG.md + Dependabot (.github/dependabot.yml) + README «MCP Protocol Version»-Sektion
- Dependabot bereits aktiv (PR #5 gemergt)

### Gaps
- `protocolVersion` nicht hart im Code gepinnt — Version wird vom mcp-SDK ausgehandelt und im README/CHANGELOG dokumentiert

### Expected Behavior
protocolVersion explizit pinnen.

### Remediation
S — abhängig von SDK-Support für explizites Pinning.

### Effort
—

