## Finding: SCALE-002

**Severity:** high
**Status:** Open
**Check:** SCALE-002  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Die Scaling-Strategie ist dokumentiert (Single-Instance + Sticky-Session-Empfehlung), aber für horizontales Scaling ist kein LB-/Session-Mechanismus implementiert. Praktisches Risiko gering (zustandslose Tools).

### Evidence
- Tools zustandslos; Single-Instance-Annahme + Sticky-Session-Empfehlung in docs/roadmap.md dokumentiert

### Gaps
- Sticky-Sessions / Shared-State-Session-Manager nicht implementiert (nur dokumentiert)

### Expected Behavior
Sticky-Sessions auf Mcp-Session-Id ODER Shared-State.

### Remediation
M — nur bei tatsächlichem Scaling.

### Effort
—

