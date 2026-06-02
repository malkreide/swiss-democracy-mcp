# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
