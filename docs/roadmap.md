# Roadmap — swiss-democracy-mcp

Phased architecture (audit OPS-003). The server is currently **Phase 1**.

## Phase 1 — Read-only (current)
- All tools are read-only (`readOnlyHint: true`, no write/destructive tools).
- Sources: Swissvotes (1848+), BFS/opendata.swiss (1981+), SRGSSR Polis (1900+).
- Scope of this phase: stable tool surface, SSRF-hardened egress, provenance
  on every response.

### Exit criteria Phase 1 → Phase 2
- [x] Audit run completed (see `audits/`)
- [x] Blocking security findings remediated (SEC-004/005/016/021, SDK-001)
- [ ] Test coverage for all tools incl. BFS/Polis (audit OPS-001)
- [ ] DSG/processing-record review (no PII expected — aggregate data only)

## Phase 2 — Write / interaction (not started)
No write tools planned. Any future write capability requires HITL confirmation
and a documented Architecture Decision Record (audit HITL/SEC-019).

## Phase 3 — Multi-agent (not started)

## Scaling note (audit SCALE-002)
The server is **stdio-first** and its tools are **stateless** (the only in-memory
state is a 24h Swissvotes CSV cache, which is a cache, not session state).
For the optional Streamable-HTTP transport a single instance is assumed. Before
horizontal scaling, configure sticky sessions on `Mcp-Session-Id` at the
ingress/LB, or a shared session store.
