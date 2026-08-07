# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **Eine Strukturänderung von opendata.swiss wurde zu «keine Abstimmungsdaten».**
  `democracy_bfs_list_vote_dates` schrieb
  `resources = data.get("result", {}).get("resources", [])`. Fällt `result` weg
  oder wandert es, war `resources` leer, die Schleife lief nullmal, und das
  Werkzeug antwortete mit `total: 0` und einer leeren Liste.

  Für das Modell ist das nicht davon zu unterscheiden, dass das BFS gerade
  keine Abstimmungsdaten führt. Nur führt das Archiv Abstimmungen **seit 1981**
  — `total: 0` ist dort nie eine plausible Antwort, und trotzdem hätte niemand
  etwas gemerkt.

  `result` und `resources` werden jetzt bestätigt; bei Abweichung fliegt
  `UpstreamSchemaError` und wird über `_fail` zu einem `isError: true`-Ergebnis,
  wie jeder andere Fehler dieses Servers. Der Typ erbt von `ValueError`, weil
  `_friendly_error` genau diese Meldungen wörtlich durchreicht — dort stehen die
  tatsächlich vorhandenen Schlüssel, und die braucht der nächste Schritt.

  `resources: []` bleibt ein normales Ergebnis: Bestätigt wird die
  **Anwesenheit** des Schlüssels, nicht sein Inhalt. Ein Wächter, der die echte
  Leermenge mitfängt, wird nach dem zweiten Fehlalarm abgeschaltet.

  Gefunden im Portfolio-Durchlauf zu
  [`FID-006`](https://github.com/malkreide/mcp-audit-skill/blob/main/checks/FID-006.md)
  am 2026-08-07: Acht Server im Portfolio sprechen mit CKAN, alle acht prüfen
  das `success`-Envelope, sieben defaulteten `result` danach.

## [0.2.5] - 2026-08-02

### Fixed

- **`structlog` carried no upper bound, and the index already serves a major past
  the floor.** The declared range was `structlog>=24.1.0`; PyPI has been serving
  `26.1.0`. The artefact does not change — the resolver's answer to the next
  fresh install does, and that is exactly how `swiss-energy-mcp` 0.3.3 became
  uninstallable when `mcp` 2.0.0 removed the module it imported.

  Now `structlog>=24.1.0,<27`. The bound is measured rather than guessed: this package
  installs and imports against `structlog 26.1.0` today, so the cap admits what
  demonstrably works and stops only the next, unknown major.

A dependency range only reaches users through a new release, hence the
version bump. No code changed.

## [v0.2.4] — 2026-07-30

### Fixed

- **The User-Agent reports the actual package version again.** The published
  `0.2.3` sent `swiss-democracy-mcp/1.0.0` to every upstream — the version string was
  hardcoded and had been left behind by earlier bumps. The version now comes
  from the package metadata, so it can no longer drift from the package.

- **Capped `mcp` at `<2`.** `mcp` 2.0.0, published 2026-07-28, removed
  `mcp.server.fastmcp` — the module this server imports. With the previous
  unbounded `>=1.28.1` every fresh resolve picked 2.0.0 and failed at import
  with `ModuleNotFoundError`, in CI and for anyone running `pip install` alike.
  Verified in both directions: 2.0.0 fails, `<2` resolves to 1.29.0 and imports
  cleanly. Migrating to the 2.x API (`mcp.server.mcpserver`) stays a separate,
  deliberate piece of work.

## [v0.2.0] — 2026-06-02

### Audit verification
- **Production-ready:** ✅ yes
- **Audit run-id:** `2026-06-02T035936-Z-swiss-democracy-mcp`
- **Skill version:** `1.0.0` · **Catalog hash:** `091f446b2796…`
- **Check results:** 29 pass · 0 fail · 7 partial (non-blocking) · 0 todo

### Added
- Execution errors now surface as `isError` tool results via `ToolError`,
  instead of error strings in a successful result; the friendly message is
  shown, the original is logged to stderr (audit OBS-001).
- MCP `Context` injection: long-running tools report progress / log via
  `ctx` (e.g. the initial Swissvotes CSV download) (audit SDK-003).
- CORS middleware for the Streamable-HTTP transport, exposing/allowing the
  `Mcp-Session-Id` header; origins configurable via `MCP_CORS_ORIGINS`
  (audit SDK-004).
- Unit-test coverage for the BFS and Polis tools incl. the no-credentials hint
  (audit OPS-001).
- Egress allow-list + HTTPS enforcement + IP blocklist for all outbound
  requests; DNS resolution + private/metadata-IP rejection for caller-supplied
  URLs (audit SEC-004 / SEC-005 / SEC-021).
- Shared pooled `httpx.AsyncClient` via server lifespan (audit SDK-001).
- Structured JSON logging to stderr via `structlog` (audit OBS-003 / OBS-004).
- `source`/`license` provenance field on tool responses — CC BY 4.0 attribution
  (audit CH-004).
- Central `Settings` (pydantic-settings) with `SecretStr` for SRGSSR credentials
  (audit ARCH-004 / SEC-013 / ARCH-005).
- `match_type` + guidance note on empty search results (audit ARCH-003).
- `<use_case>` tags in tool descriptions (audit ARCH-002).
- `Literal` types for `level` / `lang` arguments (audit SDK-002).
- `.gitignore`, `.env.example`, hardened `Dockerfile`, `CHANGELOG.md`,
  Dependabot config, `docs/roadmap.md`, `docs/security.md`,
  `docs/secret-management.md`.
- Gitleaks secret-scan job in CI (audit ARCH-005).

### Changed
- `MCP_HOST` now defaults to `127.0.0.1`; binding to `0.0.0.0` logs a warning
  and is intended for container/cloud only (audit SEC-016).

## [0.1.0] — 2026-05
### Added
- Initial release: Swissvotes (1848+), BFS opendata.swiss, SRGSSR Polis (1900+)
  read-only tools.

## MCP Protocol Version
This server targets the MCP protocol version negotiated by `mcp[cli]>=1.6.0`
(FastMCP). SDK updates are tracked monthly via Dependabot; protocol-version
bumps are noted here.
