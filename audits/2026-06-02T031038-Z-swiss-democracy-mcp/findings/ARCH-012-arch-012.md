## Finding: ARCH-012

**Severity:** medium
**Status:** Open
**Check:** ARCH-012  |  **Result:** fail
**Server:** swiss-democracy-mcp

### Observed Behavior
Keine Spec-Versionierungs-Disziplin: kein Pinning, kein CHANGELOG, keine automatisierten SDK-Updates.

### Evidence
- FastMCP-Default-Protocol genutzt

### Gaps
- `protocolVersion` nicht explizit gepinnt
- Kein CHANGELOG.md
- Keine README-Sektion «MCP Protocol Version»
- Kein Dependabot/Renovate (.github/dependabot.yml fehlt)

### Expected Behavior
protocolVersion gepinnt + CHANGELOG + README-Protocol-Sektion + Dependabot.

### Remediation
1) Protocol-Version im README dokumentieren. 2) CHANGELOG anlegen. 3) `.github/dependabot.yml` für pip.

### Effort
S — < 1 Tag.

