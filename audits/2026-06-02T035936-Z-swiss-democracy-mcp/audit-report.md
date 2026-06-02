# MCP-Server Audit-Report — `swiss-democracy-mcp`

**Audit-Datum:** 2026-06-02
**Skill-Version:** 1.0.0
**Catalog-Version:** v1.0.0 (hash 091f446b2796)

---

## 1. Executive Summary

Server `swiss-democracy-mcp` wurde gegen 36 anwendbare Best-Practice-Checks geprüft. 29 bestanden, 7 Findings dokumentiert (1 critical, 4 high, 2 medium, 0 low). Production-Readiness: erreicht.

**Production-Readiness:** YES

---

## 2. Profil-Snapshot

| Feld | Wert |
|---|---|
| Server-Name | `swiss-democracy-mcp` |
| Audit-Datum | 2026-06-02 |
| Skill-Version | 1.0.0 |
| Catalog-Version | v1.0.0 (hash 091f446b2796) |
| transport | `dual` |
| auth_model | `none` |
| data_class | `Public Open Data` |
| write_capable | `False` |
| deployment | `['local-stdio']` |
| uses_sampling | `False` |
| tools_make_external_requests | `True` |
| stadt_zuerich_context | `False` |
| schulamt_context | `False` |
| data_source.is_swiss_open_data | `True` |

---

## 3. Applicability

### Status pro Kategorie

| Kategorie | Pass | Fail | Partial | Todo | N/A |
|---|---|---|---|---|---|
| ARCH | 10 | 0 | 1 | 0 | 0 |
| CH | 1 | 0 | 0 | 0 | 0 |
| OBS | 3 | 0 | 1 | 0 | 0 |
| OPS | 2 | 0 | 1 | 0 | 0 |
| SCALE | 0 | 0 | 1 | 0 | 0 |
| SDK | 3 | 0 | 1 | 0 | 0 |
| SEC | 10 | 0 | 2 | 0 | 0 |
| **Total** | **29** | **0** | **7** | **0** | **0** |

---

## 4. Findings-Übersicht

_Policy: `fail-or-partial`_

| ID | Category | Severity | Status |
|---|---|---|---|
| SEC-009 | SEC | critical | partial |
| OBS-002 | OBS | high | partial |
| OPS-001 | OPS | high | partial |
| SCALE-002 | SCALE | high | partial |
| SEC-005 | SEC | high | partial |
| ARCH-012 | ARCH | medium | partial |
| SDK-002 | SDK | medium | partial |

**Gesamt:** 7 Findings

---

## 5. Detail-Findings

### ARCH-012

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


### OBS-002

## Finding: OBS-002

**Severity:** high
**Status:** Open
**Check:** OBS-002  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Fehlerdetails werden im Code maskiert und nur die freundliche Meldung exponiert; das FastMCP-Flag `mask_error_details` ist in dieser SDK-Version nicht verfügbar.

### Evidence
- `_friendly_error` maskiert Details (keine Stacktraces); Original nur via stderr-Log
- ToolError-Message ist user-friendly

### Gaps
- `mask_error_details=True` nicht gesetzt — Parameter existiert in der genutzten mcp-SDK-Version nicht

### Expected Behavior
`mask_error_details=True` sobald die SDK-Version es unterstützt.

### Remediation
S — bei SDK-Upgrade.

### Effort
—


### OPS-001

## Finding: OPS-001

**Severity:** high
**Status:** Open
**Check:** OPS-001  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Test-Abdeckung deutlich verbessert (BFS/Polis jetzt abgedeckt), aber der quantitative Richtwert pro Tool ist noch nicht durchgängig erfüllt.

### Evidence
- respx-Mocking, @pytest.mark.live, CI `-m "not live"`
- Neu: Unit-Tests für BFS-list/results und Polis (no-creds + gemockter Token/Endpoint); 29 Tests

### Gaps
- Richtwert ≥5 Unit + ≥1 Live pro Tool noch nicht überall erreicht; kein separater nightly Live-Workflow

### Expected Behavior
Pro Tool ≥5 Unit + ≥1 Live-Test; nightly Live-Workflow.

### Remediation
M — 1–3 Tage.

### Effort
—


### SCALE-002

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


### SDK-002

## Finding: SDK-002

**Severity:** medium
**Status:** Open
**Check:** SDK-002  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Inputs stark typisiert; Returns sind weiterhin JSON-Strings mit einheitlichem source-Envelope und Literal-Enums. Voll-typisierte Model-Returns wurden zugunsten der Contract-Stabilität nicht umgesetzt.

### Evidence
- `Literal`-Typen für level/lang; einheitlicher Envelope mit `source`/count via `_emit()`; Pydantic ≥2 Inputs

### Gaps
- Tool-Returns weiterhin JSON-`str` statt typisierter BaseModel/TypedDict-Returns (bewusst, Contract-Stabilität)

### Expected Behavior
Typisierte BaseModel/TypedDict-Returns.

### Remediation
M — Contract-Migration.

### Effort
—


### SEC-005

## Finding: SEC-005

**Severity:** high
**Status:** Open
**Check:** SEC-005  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
DNS-Rebinding ist durch die fixe Allow-List + Single-Resolution-IP-Check praktisch neutralisiert; ein literales IP-Pinning auf TLS-Ebene ist nicht implementiert.

### Evidence
- Einmalige getaddrinfo-Resolution + IP-Blocklist-Check für caller-supplied URLs
- Fixe Host-Allow-List eliminiert den Rebinding-Vektor für vertrauenswürdige Hosts

### Gaps
- Kein literales TLS-IP-Pinning (gepinnte IP in TCP-Connection bei erhaltenem SNI) — httpx löst beim Request selbst auf

### Expected Behavior
PinnedTransport (resolved IP in TCP-Connection, Original-Host für SNI) oder Egress-Proxy.

### Remediation
M — 1–3 Tage.

### Effort
—


### SEC-009

## Finding: SEC-009

**Severity:** critical
**Status:** Open
**Check:** SEC-009  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Kein eigenes Session-Binding. Da unauthentifiziert und zustandslos, ist der Hijacking-Impact gering — der Check ist formal anwendbar (dual transport), praktisch niedrige Kriminalität.

### Evidence
- Keine eigene Session-Verwaltung; Tools zustandslos; auth_model=none (keine user-spezifischen Privilegien)

### Gaps
- Keine kryptografische Session-Generierung/Binding im Code (verlässt sich auf FastMCP)

### Expected Behavior
Kryptografische Session-IDs an validierte user_id gebunden (relevant erst mit Auth/State).

### Remediation
M — nur bei Einführung von Auth/State.

### Effort
—


---

## 6. Remediation-Plan

### Empfohlene Reihenfolge

1. **SEC-009** (critical, partial)
2. **OBS-002** (high, partial)
3. **OPS-001** (high, partial)
4. **SCALE-002** (high, partial)
5. **SEC-005** (high, partial)
6. **ARCH-012** (medium, partial)
7. **SDK-002** (medium, partial)

---

## 7. Audit-Metadata

| Feld | Wert |
|---|---|
| skill_version | `1.0.0` |
| catalog_version | `v1.0.0 (hash 091f446b2796)` |
| audit_date | `2026-06-02` |


_Generated by tools/build_report.py — do not edit by hand._
