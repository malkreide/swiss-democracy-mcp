# Security notes — swiss-democracy-mcp

## Transport & binding (audit SEC-006 / SEC-016)
- Default transport is **stdio** (local, Claude Desktop). No network port opens.
- Streamable HTTP is opt-in via `MCP_TRANSPORT=streamable_http`.
- `MCP_HOST` defaults to `127.0.0.1`. Use `MCP_HOST=0.0.0.0` **only** inside a
  sandboxed container/cloud deployment — never on a local machine.

## Egress / SSRF (audit SEC-004 / SEC-005 / SEC-021)
- Outbound requests are restricted to a code-layer allow-list (`ALLOWED_HOSTS`):
  `swissvotes.ch`, `opendata.swiss`, `*.bfs.admin.ch`, `api.srgssr.ch`. HTTPS only.
- Caller-supplied URLs (BFS `result_url`) are additionally DNS-resolved and
  rejected if they map to private, loopback, link-local or cloud-metadata ranges.
- Recommended defence-in-depth in production: a network-layer egress policy
  (Kubernetes NetworkPolicy / security group) limiting outbound 443 to the
  allow-listed hosts.

## Lethal-trifecta assessment (audit SEC-019)
The server holds at most **two** of the three trifecta capabilities:
1. Access to data — **only public open data** (no private/PII).
2. External communication — **GET only**, restricted to the egress allow-list.
3. Untrusted content / write-back — **none** (no write or send tools).
With no write/exfiltration channel and an HTTPS host allow-list, the trifecta
risk is low. Adding any write/send tool would require re-assessment + an ADR.

## Secrets (audit SEC-013 / ARCH-005)
See [secret-management.md](secret-management.md).
