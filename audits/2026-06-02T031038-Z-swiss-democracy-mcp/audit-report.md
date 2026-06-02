# MCP-Server Audit-Report — `swiss-democracy-mcp`

**Audit-Datum:** 2026-06-02
**Skill-Version:** 1.0.0
**Catalog-Version:** v1.0.0 (hash 091f446b2796)

---

## 1. Executive Summary

Server `swiss-democracy-mcp` wurde gegen 36 anwendbare Best-Practice-Checks geprüft. 9 bestanden, 27 Findings dokumentiert (5 critical, 12 high, 10 medium, 0 low). Production-Readiness: NICHT erreicht — blockierend: SDK-001, SEC-004, SEC-005, SEC-016, SEC-021.

**Production-Readiness:** NO

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
| ARCH | 4 | 2 | 5 | 0 | 0 |
| CH | 0 | 0 | 1 | 0 | 0 |
| OBS | 1 | 1 | 2 | 0 | 0 |
| OPS | 0 | 0 | 3 | 0 | 0 |
| SCALE | 0 | 0 | 1 | 0 | 0 |
| SDK | 0 | 1 | 3 | 0 | 0 |
| SEC | 4 | 4 | 4 | 0 | 0 |
| **Total** | **9** | **8** | **19** | **0** | **0** |

---

## 4. Findings-Übersicht

_Policy: `fail-or-partial`_

| ID | Category | Severity | Status |
|---|---|---|---|
| ARCH-005 | ARCH | critical | partial |
| SEC-004 | SEC | critical | fail |
| SEC-009 | SEC | critical | partial |
| SEC-016 | SEC | critical | fail |
| SEC-019 | SEC | critical | partial |
| ARCH-004 | ARCH | high | partial |
| OBS-001 | OBS | high | partial |
| OBS-002 | OBS | high | partial |
| OPS-001 | OPS | high | partial |
| OPS-003 | OPS | high | partial |
| SCALE-002 | SCALE | high | partial |
| SDK-001 | SDK | high | fail |
| SDK-004 | SDK | high | partial |
| SEC-005 | SEC | high | fail |
| SEC-007 | SEC | high | partial |
| SEC-013 | SEC | high | partial |
| SEC-021 | SEC | high | fail |
| ARCH-002 | ARCH | medium | partial |
| ARCH-003 | ARCH | medium | partial |
| ARCH-008 | ARCH | medium | fail |
| ARCH-011 | ARCH | medium | partial |
| ARCH-012 | ARCH | medium | fail |
| CH-004 | CH | medium | partial |
| OBS-003 | OBS | medium | fail |
| OPS-002 | OPS | medium | partial |
| SDK-002 | SDK | medium | partial |
| SDK-003 | SDK | medium | partial |

**Gesamt:** 27 Findings

---

## 5. Detail-Findings

### ARCH-002

## Finding: ARCH-002

**Severity:** medium
**Status:** Open
**Check:** ARCH-002  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Beschreibungen sind prosaisch und ausführlich, enthalten aber keine maschinell trennscharfen Use-Case-Tags.

### Evidence
- Tool-Descriptions sind ausführlich (>100 Zeichen Median), mit Args/Returns
- Differenzierung ähnlicher Tools (search vs detail vs cantonal) klar

### Gaps
- Keine strukturierten `<use_case>`/`<important_notes>`/`<example>`-Tags (0 Treffer in src/)

### Expected Behavior
≥80% der Tools mit `<use_case>`-Tag plus Caveats in `<important_notes>`.

### Remediation
Pro Tool die Description um `<use_case>`/`<important_notes>`-Tags ergänzen (siehe ARCH-002 Pass-Pattern).

### Effort
S — pro Tool 5–10 Min.


### ARCH-003

## Finding: ARCH-003

**Severity:** medium
**Status:** Open
**Check:** ARCH-003  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Leere Resultate werden ohne Heuristik/Vorschläge zurückgegeben; Lookup-Tools liefern blosse Fehlermeldung.

### Evidence
- `democracy_search_votes` liefert strukturiertes Envelope mit total/count/has_more auch bei 0 Treffern (server.py:452-459)

### Gaps
- Kein `match_type`-Feld, kein Fuzzy-/Suggestion-Mechanismus
- Detail-/Party-/Cantonal-Tools geben bei Nicht-Treffer nur `{"error": "...nicht gefunden"}` zurück (server.py:512,597,665)

### Expected Behavior
Bei nicht-sensiblen Such-Tools: Fuzzy-Fallback + `match_type` + actionable Hinweis.

### Remediation
Bei `search_votes` Fuzzy-/Vorschlags-Logik ergänzen, `match_type` (exact/fuzzy/none) ins Envelope. Daten sind public → Heuristik unbedenklich.

### Effort
S — ~30 Min pro Such-Tool.


### ARCH-004

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


### ARCH-005

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


### ARCH-008

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


### ARCH-011

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


### ARCH-012

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


### CH-004

## Finding: CH-004

**Severity:** medium
**Status:** Open
**Check:** CH-004  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Lizenz-Attribution ist im README vorbildlich, fehlt aber in den maschinenlesbaren Tool-Antworten.

### Evidence
- README dokumentiert alle Quellen mit Lizenzen (Data Sources, Safety&Limits, License-Sektion: Swissvotes CC BY 4.0 etc.)

### Gaps
- Tool-Antworten enthalten kein `source`/`license`-Feld (0 Treffer im Code)
- Keine Per-Record-Provenance im Response-Envelope

### Expected Behavior
Tool-Antworten mit `source`+`license`-Feld; Provenance pro Datensatz.

### Remediation
Response-Envelope um `source`/`license`/`attribution` ergänzen (CC BY 4.0: Autor, Quelle, Lizenz).

### Effort
S — < 1 Tag.


### OBS-001

## Finding: OBS-001

**Severity:** high
**Status:** Open
**Check:** OBS-001  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Anwendungsfehler werden gefangen, aber als erfolgreicher Tool-Output mit «Fehler:»-Text geliefert statt mit isError-Flag.

### Evidence
- Tool-Handler fangen Exceptions ab und crashen nicht (`_handle_error`, server.py:236-249)
- Test deckt Not-Found-Pfad ab (test_get_vote_detail_not_found)

### Gaps
- Fehler werden als normaler String/JSON zurückgegeben, NICHT als `isError`-Tool-Result markiert
- Keine standardisierten Protocol-Error-Codes; kein Test für Protocol-Error-Pfad

### Expected Behavior
Execution-Errors mit `isError: true`; Protocol-Errors mit Standard-Codes.

### Remediation
Fehler über das FastMCP-Error-Signaling (Exception → isError) statt String-Return; Protocol-Error-Test ergänzen.

### Effort
M — 1–3 Tage.


### OBS-002

## Finding: OBS-002

**Severity:** high
**Status:** Open
**Check:** OBS-002  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Fehlerdetails werden grösstenteils maskiert, aber FastMCP-seitig nicht hart erzwungen und der Catch-all-Zweig leakt Exception-Repr.

### Evidence
- `_handle_error` liefert benutzerfreundliche, gemaskte Meldungen (keine Stacktraces)
- Kein `traceback.format_exc()` im Code

### Gaps
- `mask_error_details=True` im FastMCP-Konstruktor nicht gesetzt (server.py:275)
- Generischer Fallback `f"Fehler: {type(e).__name__}: {e}"` (server.py:249) kann Internals exponieren

### Expected Behavior
`mask_error_details=True` + ausschliesslich user-friendly Messages.

### Remediation
`FastMCP(..., mask_error_details=True)`; generischen Fallback durch generische Meldung ersetzen, Original nur ins (stderr-)Log.

### Effort
S — < 1 Tag.


### OBS-003

## Finding: OBS-003

**Severity:** medium
**Status:** Open
**Check:** OBS-003  |  **Result:** fail
**Server:** swiss-democracy-mcp

### Observed Behavior
Der Server hat überhaupt kein Logging — weder strukturiert noch unstrukturiert.

### Evidence
- Kein Logging-Code vorhanden

### Gaps
- Kein Structured Logger (structlog/loguru) in dependencies
- Keine Severity-Stufen, kein bound context pro Tool-Call

### Expected Behavior
Structured Logger (structlog) mit JSON/logfmt, ≥4 Severity-Stufen, bound context.

### Remediation
structlog einführen, Logger auf stderr (siehe OBS-004), pro Tool-Call tool/correlation-id binden.

### Effort
S — < 1 Tag.


### OPS-001

## Finding: OPS-001

**Severity:** high
**Status:** Open
**Check:** OPS-001  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Test-Infrastruktur ist solide (respx, live-Marker, CI), aber die Abdeckung der BFS-/Polis-Tools fehlt.

### Evidence
- respx-HTTP-Mocking in Unit-Tests (tests/test_server.py:12,155ff)
- Live-Tests mit `@pytest.mark.live` markiert, Marker in pyproject registriert
- CI läuft `pytest -m "not live"` (ci.yml)

### Gaps
- BFS- und Polis-Tools haben keine Unit-Tests (nur Swissvotes getestet)
- Nur ~11 Unit-Tests / 2 Live-Tests — unter dem Richtwert ≥5 Unit + ≥1 Live pro Tool
- Separater nightly Live-Test-Workflow fehlt

### Expected Behavior
≥5 Unit + ≥1 Live-Test pro Tool, separater Live-Workflow.

### Remediation
Unit-Tests für `bfs_*`- und `polis_*`-Tools (respx-Mocks) ergänzen; nightly Live-Workflow hinzufügen.

### Effort
M — 1–3 Tage.


### OPS-002

## Finding: OPS-002

**Severity:** medium
**Status:** Open
**Check:** OPS-002  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Dokumentation ist umfangreich und bilingual, aber CHANGELOG fehlt und Konfiguration ist nicht gebündelt.

### Evidence
- README mit Demo, Installation, Tools, Architektur (ASCII-Diagramm), Safety&Limits, Known Limitations, License
- README.de.md parallel mit gleichen Top-Level-Sektionen
- CONTRIBUTING.md vorhanden

### Gaps
- `CHANGELOG.md` fehlt
- Keine dedizierte Configuration-Sektion (Env-Vars nur in Installation gestreut)

### Expected Behavior
Alle 8 Pflicht-Sektionen inkl. CHANGELOG + Configuration.

### Remediation
CHANGELOG anlegen; «Configuration»-Sektion (MCP_TRANSPORT/HOST/PORT, SRGSSR_*) ergänzen.

### Effort
S–M.


### OPS-003

## Finding: OPS-003

**Severity:** high
**Status:** Open
**Check:** OPS-003  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Phasenmodell ist im README angelegt und konsistent, aber Roadmap und Übergangskriterien fehlen.

### Evidence
- Phasen explizit im README deklariert (Phase 1/2/3 in Tools-Sektion)
- Phasen konsistent mit Annotations (alle read-only = Phase 1)

### Gaps
- Kein Roadmap-File
- Phasenübergangs-Voraussetzungen (Audit/ISDS/DSG) nicht dokumentiert
- Kein CHANGELOG für Phasenübergänge

### Expected Behavior
Explizite Phase + Roadmap-File + dokumentierte Übergangskriterien.

### Remediation
`docs/roadmap.md` mit Phasen-Tasks und Übergangskriterien; aktuelle Phase prominent deklarieren.

### Effort
S.


### SCALE-002

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


### SDK-001

## Finding: SDK-001

**Severity:** high
**Status:** Open
**Check:** SDK-001  |  **Result:** fail
**Server:** swiss-democracy-mcp

### Observed Behavior
Pro Tool-Call wird ein neuer HTTP-Client samt Connection-Pool aufgebaut — explizites Anti-Pattern des Katalogs.

### Evidence
- Kein `lifespan`/`@asynccontextmanager`/`AsyncExitStack` (0 Treffer)
- `httpx.AsyncClient(...)` wird in jedem Helper pro Tool-Call neu erzeugt (server.py:115,165,196,212)

### Gaps
- Kein geteilter Client/Connection-Pool über Lifespan

### Expected Behavior
Lifespan mit `@asynccontextmanager`, geteilter `httpx.AsyncClient`, Cleanup im finally.

### Remediation
`@asynccontextmanager`-Lifespan einführen, `httpx.AsyncClient` einmalig erzeugen und via Context/State injizieren; `FastMCP(..., lifespan=...)`.

### Effort
S — < 1 Tag.


### SDK-002

## Finding: SDK-002

**Severity:** medium
**Status:** Open
**Check:** SDK-002  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Inputs sind stark typisiert, aber Tool-Returns sind unstrukturierte JSON-Strings ohne typisierten Envelope.

### Evidence
- Pydantic ≥2 für alle Input-Modelle; Field-Defaults via `Field(default=...)`

### Gaps
- Tool-Returns sind `-> str` (json.dumps), keine BaseModel/TypedDict-Return-Typen
- Kein konsistenter Envelope mit `source`/`provenance`
- Keine `Literal`-Typen für enumerable Felder (level, lang)

### Expected Behavior
Typisierte Returns (BaseModel/TypedDict) mit source/provenance/results/count; Literal-Types.

### Remediation
Return-Modelle definieren; `level`/`lang` als `Literal[...]`; Envelope mit source/count vereinheitlichen (Synergie CH-004/SDK-002).

### Effort
S — < 1 Tag.


### SDK-003

## Finding: SDK-003

**Severity:** medium
**Status:** Open
**Check:** SDK-003  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Keine Context-Injektion; langlaufende Operationen (initialer CSV-Download) ohne Progress/Logging.

### Evidence
- Tools sind grösstenteils schnell (Swissvotes-CSV gecacht 24h)

### Gaps
- Kein `ctx: Context`-Parameter in irgendeinem Tool
- Kein `ctx.report_progress()` bei potenziell langsamen Calls (CSV-Initial-Download mehrere MB)
- Fehler werden nicht via `ctx.warning/error` gemeldet

### Expected Behavior
`ctx: Context` für Tools >2s; `ctx.report_progress()`; `ctx.warning/error` statt stummem Schlucken.

### Remediation
`ctx: Context`-Parameter ergänzen, beim CSV-Initial-Load `ctx.report_progress()` senden.

### Effort
S — < 1 Tag.


### SDK-004

## Finding: SDK-004

**Severity:** high
**Status:** Open
**Check:** SDK-004  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Im HTTP-Modus ist keine CORS-Konfiguration vorhanden; Browser-basierte Clients erhalten `Mcp-Session-Id` nicht.

### Evidence
- HTTP-Transport (streamable_http) wird unterstützt

### Gaps
- Keine CORS-Middleware konfiguriert (kein `expose_headers`/`allow_headers`)
- `Mcp-Session-Id` nicht explizit für Browser-Clients exponiert

### Expected Behavior
CORS mit `expose_headers`/`allow_headers` inkl. `Mcp-Session-Id`, explizite Origins in Prod.

### Remediation
CORS-Middleware für HTTP-Transport konfigurieren; `allow_origins` als explizite Liste (kein `*`).

### Effort
S — < 1 Tag.


### SEC-004

## Finding: SEC-004

**Severity:** critical
**Status:** Open
**Check:** SEC-004  |  **Result:** fail
**Server:** swiss-democracy-mcp

### Observed Behavior
Das BFS-Result-Tool fetcht eine frei wählbare URL ohne jegliche Validierung — klassische SSRF. Ein manipuliertes Tool-Argument (z.B. `http://169.254.169.254/...`) zwingt den Server, interne/Cloud-Metadata-Endpunkte abzurufen.

### Evidence
- `democracy_bfs_get_vote_results(result_url)` reicht einen beliebigen User/LLM-URL direkt an `_bfs_get` → `httpx.get(url)` weiter (server.py:837-853,210-215)
- `result_url` hat nur min/max_length (10/500), KEINE Scheme-/Host-Validierung (server.py:809-817)
- Kein HTTPS-Enforcement, keine IP-Blocklist, kein Egress-Proxy

### Gaps
- Cloud-Metadata-IP 169.254.169.254 nicht blockiert
- Private/Loopback-Ranges nicht blockiert

### Expected Behavior
HTTPS-Enforcement + Resolved-IP gegen Blocklist (privat/link-local/loopback) + DNS-Pinning; Cloud-Metadata explizit blockiert.

### Remediation
1) `result_url` gegen Allow-List der bekannten BFS-Hosts (opendata.swiss/bfs.admin.ch) prüfen statt freier URL. 2) HTTPS erzwingen. 3) Resolved-IP-Blocklist + DNS-Pinning (siehe SEC-004 Pass-Pattern). 4) Idealerweise: nur Resource-ID statt voller URL als Tool-Arg akzeptieren.

### Effort
M — 1–3 Tage.


### SEC-005

## Finding: SEC-005

**Severity:** high
**Status:** Open
**Check:** SEC-005  |  **Result:** fail
**Server:** swiss-democracy-mcp

### Observed Behavior
Da keinerlei SSRF-Schutz existiert, fehlt auch die DNS-Rebinding-Mitigation (TOCTOU) vollständig.

### Evidence
- Kein `getaddrinfo`/DNS-Pinning im Code; httpx-Default mit impliziter Doppel-Auflösung
- Folgt direkt aus fehlender SSRF-Prevention (SEC-004)

### Gaps
- Kein gepinnter IP-Request, kein Host-Header-Erhalt für TLS-SNI

### Expected Behavior
Einmalige DNS-Resolution + gepinnte IP für den Request + Original-Host für TLS-SNI.

### Remediation
Custom `PinnedTransport` (SEC-005 Pass-Pattern) oder Egress-Proxy (Smokescreen). Voraussetzung: SEC-004 zuerst.

### Effort
M — 1–3 Tage.


### SEC-007

## Finding: SEC-007

**Severity:** high
**Status:** Open
**Check:** SEC-007  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Es existiert keinerlei Sandboxing-Artefakt. Für einen lokalen stdio-Server ist das Defense-in-Depth, fehlt hier aber komplett — relevant sobald der dokumentierte Cloud-/Render-Pfad genutzt wird.

### Evidence
- Server ist als PyPI-Paket via uvx/pip lauffähig

### Gaps
- Kein Dockerfile / keine Container-Hardening (USER non-root, readOnlyRootFilesystem, cap drop)
- Kein seccomp/SecurityContext

### Expected Behavior
Gehärtetes Dockerfile (non-root, read-only FS, cap drop) für den Container-/Cloud-Pfad.

### Remediation
Multi-Stage-Dockerfile mit `USER 10001`, read-only FS + tmpfs; bei K8s SecurityContext setzen.

### Effort
S — < 1 Tag.


### SEC-009

## Finding: SEC-009

**Severity:** critical
**Status:** Open
**Check:** SEC-009  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Es gibt keine eigene Session-Bindung. Da der Server unauthentifiziert und zustandslos ist (keine user-spezifischen Daten/Privilegien), ist der Hijacking-Impact gering — der Check ist hier formal anwendbar (dual transport), aber praktisch von niedriger Kriminalität.

### Evidence
- Keine eigene Session-Verwaltung im Code; Tools sind zustandslos
- `auth_model=none` → keine User-Identität, keine privilegierten Operationen pro Session

### Gaps
- Keine kryptografische Session-Generierung/Binding im Code (verlässt sich auf FastMCP-Defaults)
- Kein explizites TTL / keine serverseitige Invalidierung

### Expected Behavior
Kryptografische Session-IDs an validierte user_id gebunden — relevant erst mit Auth/State.

### Remediation
FastMCP-Session-ID-Generierung verifizieren/dokumentieren; bei zukünftiger Auth/State Binding gemäss SEC-009 implementieren.

### Effort
M — nur bei Einführung von Auth/State.


### SEC-013

## Finding: SEC-013

**Severity:** high
**Status:** Open
**Check:** SEC-013  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Plain-Env-Var-Storage ist für Public-Open-Data vertretbar, aber weder dokumentiert noch via SecretStr abgesichert.

### Evidence
- SRGSSR-Credentials werden aus Env-Vars geladen (Stufe 1), keine Hardcoded Keys
- Datenklasse Public Open Data → Stufe 1 grundsätzlich akzeptabel

### Gaps
- Kein Secret-Manager (Stufe 3) und keine dokumentierte Begründung für Stufe 1
- Credentials als `str` statt `SecretStr`

### Expected Behavior
Stufe-1-Begründung dokumentieren ODER Secret-Manager (Stufe 3); SecretStr-Repräsentation.

### Remediation
`docs/secret-management.md` mit Stufe-1-Begründung; Credentials als `SecretStr`.

### Effort
S — < 1 Tag.


### SEC-016

## Finding: SEC-016

**Severity:** critical
**Status:** Open
**Check:** SEC-016  |  **Result:** fail
**Server:** swiss-democracy-mcp

### Observed Behavior
Im HTTP-Modus lauscht der Server defaultmässig auf allen Interfaces (0.0.0.0) — NeighborJack-Risiko: jeder im selben Netz erreicht den Port.

### Evidence
- HTTP-Modus bindet per Default an `0.0.0.0`: `os.environ.get("MCP_HOST", "0.0.0.0")` (server.py:1121)

### Gaps
- Default sollte `127.0.0.1` sein; 0.0.0.0 nur explizit im Container
- README erklärt die lokal/container-Differenzierung beim Binding nicht
- Keine Warnung beim Start auf 0.0.0.0

### Expected Behavior
Default-Host `127.0.0.1`; `0.0.0.0` nur explizit (z.B. im Dockerfile).

### Remediation
Default auf `127.0.0.1` ändern; `MCP_HOST=0.0.0.0` nur im Dockerfile setzen; README-Hinweis + optionale Start-Warnung.

### Effort
S — < 1 Tag.


### SEC-019

## Finding: SEC-019

**Severity:** critical
**Status:** Open
**Check:** SEC-019  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Der Server hält ≤2 Trifecta-Fähigkeiten (gut), dokumentiert die Bewertung aber nicht. Die offene SSRF-Lücke (SEC-004) untergräbt die «kein Exfil»-Annahme bis zur Behebung.

### Evidence
- Nur 2 der 3 Trifecta-Fähigkeiten: liest (öffentliche) Daten + externe Requests; KEIN Write/Send
- Alle Tools read-only (GET)

### Gaps
- Trifecta-Bewertung nicht im README/docs dokumentiert
- SSRF (SEC-004) schafft de-facto einen Forge-/Exfil-Kanal — verschärft die Bewertung bis SEC-004 gefixt ist

### Expected Behavior
Dokumentierte Trifecta-Bewertung; max. zwei Fähigkeiten.

### Remediation
Kurze Trifecta-/ADR-Notiz in `docs/`; SEC-004 schliessen, damit der Exfil-Kanal verschwindet.

### Effort
S — < 1 Tag (Bewertung).


### SEC-021

## Finding: SEC-021

**Severity:** high
**Status:** Open
**Check:** SEC-021  |  **Result:** fail
**Server:** swiss-democracy-mcp

### Observed Behavior
Es gibt keine Egress-Allow-List — weder im Code noch im Netzwerk. Zusammen mit dem freien `result_url` (SEC-004) ist ausgehender Traffic unbeschränkt.

### Evidence
- Externe Requests an feste Hosts (swissvotes.ch, opendata.swiss, api.srgssr.ch) — aber nicht erzwungen
- `result_url` (BFS) erlaubt beliebige Hosts (server.py:853)

### Gaps
- Keine Code-Layer-Allow-List (`frozenset` erlaubter Hosts) / kein `assert_host_allowed`
- Keine Network-Layer-Egress-Kontrolle dokumentiert
- Kein `docs/network-egress.md`

### Expected Behavior
Code-Layer-`frozenset`-Allow-List + Pre-Request-Check + Network-Layer-Egress-Policy + Doku.

### Remediation
`ALLOWED_HOSTS = frozenset({...})` + `assert_host_allowed(url)` vor jedem Request; `docs/network-egress.md`.

### Effort
M — 1–3 Tage.


---

## 6. Remediation-Plan

### Empfohlene Reihenfolge

1. **ARCH-005** (critical, partial)
2. **SEC-004** (critical, fail)
3. **SEC-009** (critical, partial)
4. **SEC-016** (critical, fail)
5. **SEC-019** (critical, partial)
6. **ARCH-004** (high, partial)
7. **OBS-001** (high, partial)
8. **OBS-002** (high, partial)
9. **OPS-001** (high, partial)
10. **OPS-003** (high, partial)
11. **SCALE-002** (high, partial)
12. **SDK-001** (high, fail)
13. **SDK-004** (high, partial)
14. **SEC-005** (high, fail)
15. **SEC-007** (high, partial)
16. **SEC-013** (high, partial)
17. **SEC-021** (high, fail)
18. **ARCH-002** (medium, partial)
19. **ARCH-003** (medium, partial)
20. **ARCH-008** (medium, fail)
21. **ARCH-011** (medium, partial)
22. **ARCH-012** (medium, fail)
23. **CH-004** (medium, partial)
24. **OBS-003** (medium, fail)
25. **OPS-002** (medium, partial)
26. **SDK-002** (medium, partial)
27. **SDK-003** (medium, partial)

---

## 7. Audit-Metadata

| Feld | Wert |
|---|---|
| skill_version | `1.0.0` |
| catalog_version | `v1.0.0 (hash 091f446b2796)` |
| audit_date | `2026-06-02` |


_Generated by tools/build_report.py — do not edit by hand._
