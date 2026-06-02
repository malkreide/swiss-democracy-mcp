## Finding: SCALE-002

**Severity:** high
**Status:** Open
**Check:** SCALE-002  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
HTTP-Transport wird ausgeliefert, aber ohne Session-/LB-Strategie. Praktisches Risiko gering, da Tools zustandslos sind.

### Evidence
- Tools sind zustandslos (kein Mcp-Session-Id-abhängiger State); In-Memory-CSV-Cache ist reiner Cache
- stdio-first; HTTP-Transport sekundär

### Gaps
- Keine Sticky-Sessions / kein Shared-State-Session-Manager (Redis o.ä.)
- Kein Failover-/Multi-Instance-Konzept dokumentiert

### Expected Behavior
Sticky-Sessions oder Shared-State + definierte TTL für horizontales Scaling.

### Remediation
Single-Instance-Annahme im README dokumentieren; bei Cloud-Scaling Sticky-Sessions auf `Mcp-Session-Id` (Ingress) konfigurieren.

### Effort
M — 1–3 Tage (nur bei Scaling).

