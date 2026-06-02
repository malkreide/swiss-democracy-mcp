## Finding: ARCH-004

**Severity:** high
**Status:** Open
**Check:** ARCH-004  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
IoC teilweise erfüllt: Handler sind transport-agnostisch und Dual-Transport ist gegeben, aber Konfiguration/Setup ist nicht über ein Settings-/Lifespan-Objekt zentralisiert.

### Evidence
- Tool-Handler greifen nicht auf Transport-Internals (`request.`/headers) zu — voll transport-agnostisch
- Dual-Transport via `MCP_TRANSPORT` stdio|streamable_http unterstützt (server.py:1118-1125)

### Gaps
- Konfiguration über Modul-globale Vars + `os.environ`, kein Pydantic-Settings-Objekt
- Kein Lifespan/Dependency-Injection; `httpx.AsyncClient` wird pro Call erzeugt (siehe SDK-001)

### Expected Behavior
Settings-Objekt (pydantic-settings) + gemeinsamer Lifespan für alle Transports.

### Remediation
`Settings(BaseSettings)` einführen, geteilten `@asynccontextmanager`-Lifespan registrieren (Synergie SDK-001).

### Effort
M — 1–3 Tage.

