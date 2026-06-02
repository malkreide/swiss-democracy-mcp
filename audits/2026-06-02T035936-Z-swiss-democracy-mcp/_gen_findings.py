#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-audit generator for swiss-democracy-mcp after remediation PRs #2/#3/#6.
Reproducible — no inline heredocs. Same profile/catalog hash as the baseline
run (2026-06-02T031038) for direct comparability."""
from __future__ import annotations
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

# (id, cat, sev, status, [evidence], [gaps], observed, expected, remediation, effort)
CHECKS = [
 ("ARCH-001","ARCH","medium","pass",
  ["10 Tools, snake_case `democracy_*`, konsistent; ausführliche Docstrings"],[], "","","",""),
 ("ARCH-002","ARCH","medium","pass",
  ["<use_case>-Tags in allen 10 Tool-Docstrings ergänzt (server.py)",
   "Descriptions >100 Zeichen, differenziert"],[], "","","",""),
 ("ARCH-003","ARCH","medium","pass",
  ["`democracy_search_votes` liefert `match_type` (exact/none) + bei 0 Treffern actionable `note`",
   "Strukturiertes Envelope mit total/count/has_more"],[], "","","",""),
 ("ARCH-004","ARCH","high","pass",
  ["Zentrale `Settings(BaseSettings)` statt Modul-Globals (server.py)",
   "Geteilter Lifespan (@asynccontextmanager); Handler transport-agnostisch; Dual-Transport"],[], "","","",""),
 ("ARCH-005","ARCH","critical","pass",
  ["Keine Hardcoded Secrets; SRGSSR-Creds als `SecretStr`",
   ".gitignore + .env.example vorhanden; Gitleaks-Secret-Scan in CI (.github/workflows/ci.yml)"],[], "","","",""),
 ("ARCH-006","ARCH","high","pass",["10 Tools, use-case-orientiert"],[], "","","",""),
 ("ARCH-007","ARCH","medium","pass",["Tools liefern abgeschlossene Resultate"],[], "","","",""),
 ("ARCH-008","ARCH","medium","pass",
  ["README/README.de «MCP-Primitive»-Sektion begründet Tools-only (Phase-1-Wrapper)"],[], "","","",""),
 ("ARCH-009","ARCH","high","pass",["Alle Tools mit expliziten Annotations"],[], "","","",""),
 ("ARCH-011","ARCH","medium","pass",
  ["CHANGELOG.md (Keep-a-Changelog) ergänzt; README/README.de, LICENSE, pyproject, src/, tests/, CI vorhanden"],[], "","","",""),
 ("ARCH-012","ARCH","medium","partial",
  ["CHANGELOG.md + Dependabot (.github/dependabot.yml) + README «MCP Protocol Version»-Sektion",
   "Dependabot bereits aktiv (PR #5 gemergt)"],
  ["`protocolVersion` nicht hart im Code gepinnt — Version wird vom mcp-SDK ausgehandelt und im README/CHANGELOG dokumentiert"],
  "Spec-Versionierungs-Disziplin grösstenteils hergestellt; ein hartes Pinning der protocolVersion im Code erfolgt nicht (vom SDK verwaltet).",
  "protocolVersion explizit pinnen.",
  "S — abhängig von SDK-Support für explizites Pinning.",""),
 ("CH-004","CH","medium","pass",
  ["`source`/`license`-Feld (CC BY 4.0 etc.) in allen Tool-Antworten via `_emit()`",
   "README dokumentiert alle Quellen-Lizenzen; je Tool genau eine Quelle (Provenance pro Antwort)"],[], "","","",""),
 ("OBS-001","OBS","high","pass",
  ["Ausführungsfehler werfen `ToolError` → FastMCP liefert isError (server.py `_fail`)",
   "Polis-No-Creds bleibt freundlicher Normal-Hinweis; Test deckt Execution-Error-Pfad ab"],[], "","","",""),
 ("OBS-002","OBS","high","partial",
  ["`_friendly_error` maskiert Details (keine Stacktraces); Original nur via stderr-Log",
   "ToolError-Message ist user-friendly"],
  ["`mask_error_details=True` nicht gesetzt — Parameter existiert in der genutzten mcp-SDK-Version nicht"],
  "Fehlerdetails werden im Code maskiert und nur die freundliche Meldung exponiert; das FastMCP-Flag `mask_error_details` ist in dieser SDK-Version nicht verfügbar.",
  "`mask_error_details=True` sobald die SDK-Version es unterstützt.",
  "S — bei SDK-Upgrade.",""),
 ("OBS-003","OBS","medium","pass",
  ["structlog JSON-Logging auf stderr; per-Request bound context (host/source); Severity-Stufen"],[], "","","",""),
 ("OBS-004","OBS","critical","pass",["Kein print() in src/; stdout bleibt fürs Protocol frei; Logging auf stderr"],[], "","","",""),
 ("OPS-001","OPS","high","partial",
  ["respx-Mocking, @pytest.mark.live, CI `-m \"not live\"`",
   "Neu: Unit-Tests für BFS-list/results und Polis (no-creds + gemockter Token/Endpoint); 29 Tests"],
  ["Richtwert ≥5 Unit + ≥1 Live pro Tool noch nicht überall erreicht; kein separater nightly Live-Workflow"],
  "Test-Abdeckung deutlich verbessert (BFS/Polis jetzt abgedeckt), aber der quantitative Richtwert pro Tool ist noch nicht durchgängig erfüllt.",
  "Pro Tool ≥5 Unit + ≥1 Live-Test; nightly Live-Workflow.",
  "M — 1–3 Tage.",""),
 ("OPS-002","OPS","medium","pass",
  ["README mit Configuration-Sektion, Architektur-Diagramm, Limits, License; CHANGELOG; README.de parallel; docs/"],[], "","","",""),
 ("OPS-003","OPS","high","pass",
  ["docs/roadmap.md mit Phasenmodell + Übergangskriterien + Single-Instance-/Scaling-Hinweis"],[], "","","",""),
 ("SCALE-002","SCALE","high","partial",
  ["Tools zustandslos; Single-Instance-Annahme + Sticky-Session-Empfehlung in docs/roadmap.md dokumentiert"],
  ["Sticky-Sessions / Shared-State-Session-Manager nicht implementiert (nur dokumentiert)"],
  "Die Scaling-Strategie ist dokumentiert (Single-Instance + Sticky-Session-Empfehlung), aber für horizontales Scaling ist kein LB-/Session-Mechanismus implementiert. Praktisches Risiko gering (zustandslose Tools).",
  "Sticky-Sessions auf Mcp-Session-Id ODER Shared-State.",
  "M — nur bei tatsächlichem Scaling.",""),
 ("SDK-001","SDK","high","pass",
  ["Geteilter, gepoolter `httpx.AsyncClient` via @asynccontextmanager-Lifespan; Cleanup im finally"],[], "","","",""),
 ("SDK-002","SDK","medium","partial",
  ["`Literal`-Typen für level/lang; einheitlicher Envelope mit `source`/count via `_emit()`; Pydantic ≥2 Inputs"],
  ["Tool-Returns weiterhin JSON-`str` statt typisierter BaseModel/TypedDict-Returns (bewusst, Contract-Stabilität)"],
  "Inputs stark typisiert; Returns sind weiterhin JSON-Strings mit einheitlichem source-Envelope und Literal-Enums. Voll-typisierte Model-Returns wurden zugunsten der Contract-Stabilität nicht umgesetzt.",
  "Typisierte BaseModel/TypedDict-Returns.",
  "M — Contract-Migration.",""),
 ("SDK-003","SDK","medium","pass",
  ["`ctx: Context | None` in allen Tools; CSV-Initialload meldet ctx.report_progress() + ctx.info()"],[], "","","",""),
 ("SDK-004","SDK","high","pass",
  ["CORS-Middleware für Streamable-HTTP: expose_headers + allow_headers enthalten `Mcp-Session-Id`",
   "Origins via MCP_CORS_ORIGINS; HTTP via uvicorn mit umhüllter App"],[], "","","",""),
 ("SEC-004","SEC","critical","pass",
  ["`_validate_outbound`: HTTPS-Enforcement + Host-Allow-List (frozenset) vor jedem Request",
   "User-`result_url` zusätzlich DNS-aufgelöst + IP-Blocklist (169.254.169.254/privat/loopback)"],[], "","","",""),
 ("SEC-005","SEC","high","partial",
  ["Einmalige getaddrinfo-Resolution + IP-Blocklist-Check für caller-supplied URLs",
   "Fixe Host-Allow-List eliminiert den Rebinding-Vektor für vertrauenswürdige Hosts"],
  ["Kein literales TLS-IP-Pinning (gepinnte IP in TCP-Connection bei erhaltenem SNI) — httpx löst beim Request selbst auf"],
  "DNS-Rebinding ist durch die fixe Allow-List + Single-Resolution-IP-Check praktisch neutralisiert; ein literales IP-Pinning auf TLS-Ebene ist nicht implementiert.",
  "PinnedTransport (resolved IP in TCP-Connection, Original-Host für SNI) oder Egress-Proxy.",
  "M — 1–3 Tage.",""),
 ("SEC-006","SEC","high","pass",["Default-Transport stdio; HTTP nur via MCP_TRANSPORT; README dokumentiert"],[], "","","",""),
 ("SEC-007","SEC","high","pass",
  ["Gehärtetes Dockerfile: non-root USER 10001, Multi-Stage; read-only-ready (CMD-Hinweis --read-only/--cap-drop)"],[], "","","",""),
 ("SEC-008","SEC","medium","pass",
  ["Keine install-Hooks; transparenter Install; PyPI Trusted Publisher (publish.yml)"],[], "","","",""),
 ("SEC-009","SEC","critical","partial",
  ["Keine eigene Session-Verwaltung; Tools zustandslos; auth_model=none (keine user-spezifischen Privilegien)"],
  ["Keine kryptografische Session-Generierung/Binding im Code (verlässt sich auf FastMCP)"],
  "Kein eigenes Session-Binding. Da unauthentifiziert und zustandslos, ist der Hijacking-Impact gering — der Check ist formal anwendbar (dual transport), praktisch niedrige Kriminalität.",
  "Kryptografische Session-IDs an validierte user_id gebunden (relevant erst mit Auth/State).",
  "M — nur bei Einführung von Auth/State.",""),
 ("SEC-013","SEC","high","pass",
  ["SRGSSR-Creds als `SecretStr`; docs/secret-management.md begründet Stufe 1 (Public Open Data) + Hardening-Pfad"],[], "","","",""),
 ("SEC-016","SEC","critical","pass",
  ["MCP_HOST-Default `127.0.0.1`; Warnung bei 0.0.0.0; README/docs erklären lokal/Container"],[], "","","",""),
 ("SEC-018","SEC","high","pass",
  ["Alle Tool-Args via Pydantic (extra=forbid, ge/le, max_length); result_url zusätzlich host-validiert"],[], "","","",""),
 ("SEC-019","SEC","critical","pass",
  ["docs/security.md mit Lethal-Trifecta-Bewertung: ≤2 Fähigkeiten (public data + GET-only, kein Write/Send)"],[], "","","",""),
 ("SEC-020","SEC","critical","pass",["Keine os.system/subprocess/eval/shell=True (grep clean)"],[], "","","",""),
 ("SEC-021","SEC","high","pass",
  ["Code-Layer `frozenset`-Allow-List + Pre-Request-Check `_validate_outbound` vor jedem Call",
   "docs/security.md dokumentiert Hosts + empfiehlt Network-Layer-Egress-Policy"],[], "","","",""),
]


def main():
    raw_meta = json.loads((OUT/"audit-meta.json").read_text(encoding="utf-8"))
    meta = dict(raw_meta.get("audit_meta", raw_meta))
    meta["audit_date"] = meta.get("started_at", "")[:10]
    meta["catalog_version"] = f"v{meta.get('skill_version','?')} (hash {meta.get('catalog_hash','')[:12]})"
    results = {}
    raw_dir = OUT/"raw"; raw_dir.mkdir(exist_ok=True)
    find_dir = OUT/"findings"; find_dir.mkdir(exist_ok=True)
    for (cid,cat,sev,status,ev,gaps,obs,exp,rem,eff,*_) in CHECKS:
        results[cid] = {"status":status,"category":cat,"severity":sev,"evidence":ev,"gaps":gaps}
        rl=[f"# {cid} — re-audit ({status.upper()})","","## Evidence"]+[f"- {e}" for e in ev]
        if gaps: rl+=["","## Gaps"]+[f"- {g}" for g in gaps]
        (raw_dir/f"{cid}.txt").write_text("\n".join(rl)+"\n",encoding="utf-8")
        if status in ("fail","partial"):
            f=[f"## Finding: {cid}","",f"**Severity:** {sev}","**Status:** Open",
               f"**Check:** {cid}  |  **Result:** {status}","**Server:** swiss-democracy-mcp","",
               "### Observed Behavior",obs or "(siehe Evidence)","","### Evidence"]+[f"- {e}" for e in ev]+[""]
            if gaps: f+=["### Gaps"]+[f"- {g}" for g in gaps]+[""]
            f+=["### Expected Behavior",exp or "—","","### Remediation",rem or "—","","### Effort",eff or "—",""]
            (find_dir/f"{cid}-{cid.lower()}.md").write_text("\n".join(f)+"\n",encoding="utf-8")
    (OUT/"verification-results.json").write_text(
        json.dumps({"audit_meta":meta,"results":results},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    p=sum(1 for c in results.values() if c['status']=='pass')
    pa=sum(1 for c in results.values() if c['status']=='partial')
    fa=sum(1 for c in results.values() if c['status']=='fail')
    print(f"PASS={p} PARTIAL={pa} FAIL={fa} TOTAL={len(results)}")

if __name__=="__main__":
    main()
