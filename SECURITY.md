# Security Policy & Posture

[🇩🇪 Deutsche Version](SECURITY.de.md)

`swiss-democracy-mcp` was hardened against the internal MCP best-practice audit
catalogue. This document summarises the security posture and records the
**accepted-risk** decisions for controls that are deliberately handled at the
portfolio/gateway layer rather than inside this single server.

## Reporting a vulnerability

Please open a private security advisory on the GitHub repository, or contact the
maintainer listed in `README.md`. Do not file public issues for exploitable
vulnerabilities.

## Posture summary

This is a **read-only**, **no-PII**, **public-open-data** MCP server. All 10
tools only issue HTTP GET requests against a fixed allow-list of Swiss public
data sources (Swissvotes, BFS / opendata.swiss, SRGSSR Polis). Hardening already
in place:

| Area | Control |
|---|---|
| Egress | HTTPS-only to a fixed host allow-list (`swissvotes.ch`, `opendata.swiss`, `*.bfs.admin.ch`, `api.srgssr.ch`) (SEC-004/021) |
| SSRF | Caller-supplied URLs (the BFS `result_url`) are DNS-resolved and rejected if they map to private, loopback, link-local or cloud-metadata ranges (SEC-004/005) |
| TLS | Certificate verification on by default (httpx default); never disabled (SEC-005) |
| Binding | Network transports default to `127.0.0.1`; `0.0.0.0` requires an explicit `MCP_HOST` opt-in (SEC-016 / SDK-004) |
| Input | Pydantic v2 strict validation (`extra="forbid"`) on every tool input model (SEC-008/018) |
| Tools | Every tool sets `readOnlyHint: True`; no write, mutate, or delete paths exist (ARCH) |
| Secrets | The optional SRGSSR OAuth2 credentials are held as `SecretStr` and never logged (ARCH-005/SEC-013) |
| Errors | Upstream error bodies are logged to stderr only; the model receives a generic, non-leaking message (OBS-002/SEC-022) |
| Stdout | Reserved for the JSON-RPC stream; all logging pinned to stderr (OBS-004) |
| Resilience | Bounded retries, a 30s per-request timeout, and a 24h in-memory cache for the Swissvotes CSV to avoid hammering the upstream (SCALE-002/003) |

The latest audit run (`2026-06-02T035936-Z-swiss-democracy-mcp`) reports
**29 pass · 0 fail · 7 partial · 0 n/a**. See `audits/` for the full report and
`CHANGELOG.md` for the hardening history. Additional detail is documented in
[docs/security.md](docs/security.md) and [docs/secret-management.md](docs/secret-management.md).

## Accepted risks (portfolio-level controls)

The following audit checks are **not** implemented inside this server by design.
They are portfolio-wide concerns best enforced at an MCP gateway / host layer,
and the residual risk here is low because the server is read-only and only
reaches a fixed allow-list of trusted public-data providers.

### SEC-014 — Tool allow-listing via an MCP gateway

**Status:** accepted risk (portfolio-level).
A per-tool allow-list belongs to the MCP host/gateway that aggregates multiple
servers, not to an individual server that exposes a fixed, read-only tool set.
If/when a central gateway is introduced for the portfolio, tool allow-listing
should be configured there. Until then, the risk is bounded: every tool is
read-only and constrained to the host allow-list above.

### SEC-015 — Pre-flight tool-poisoning detection

**Status:** accepted risk (portfolio-level) — with a local guard in place.
Tool-poisoning (malicious tool descriptions / rug-pulls) is a supply-chain and
host-side concern. This server's tool definitions are version-controlled,
authored in-repo, and reviewed via PR; there is no dynamic or remote tool
registration. Cross-server poisoning detection remains a gateway/host
responsibility tracked at the portfolio level.

## Re-evaluation triggers

These acceptances should be revisited if the server ever:

- gains **write** capability or starts processing **PII**, or
- adds an **authentication** model for inbound callers (then implement bound,
  TTL'd, server-side-invalidated session IDs and re-audit before merge), or
- registers tools **dynamically** / from remote sources, or
- is aggregated behind a shared MCP gateway (then enable the gateway's tool
  allow-listing and tool-poisoning detection).
