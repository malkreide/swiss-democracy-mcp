## Finding: ARCH-008

**Severity:** medium
**Status:** Open
**Check:** ARCH-008  |  **Result:** fail
**Server:** swiss-democracy-mcp

### Observed Behavior
Server nutzt ausschliesslich das Tools-Primitiv, ohne Resources/Prompts und ohne dokumentierte Begründung.

### Evidence
- Nur `@mcp.tool` verwendet — keine `@mcp.resource`, keine `@mcp.prompt` (0 Treffer)

### Gaps
- Keine Begründung im README für Tools-only-Ansatz
- Read-only-Lookups (vote_detail, cantonal) sind Resource-Kandidaten

### Expected Behavior
Mind. zwei Primitive ODER dokumentierte Begründung im README.

### Remediation
README-Sektion «MCP-Primitive» mit Begründung (Phase-1-Wrapper) ergänzen; optional read-only Lookups als Resources (`vote://{anr}`) prüfen.

### Effort
S — Begründung < 1 Tag; M bei Resource-Migration.

