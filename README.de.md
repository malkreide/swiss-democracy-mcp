# 🗳️ swiss-democracy-mcp

[![CI](https://github.com/malkreide/swiss-democracy-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/malkreide/swiss-democracy-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/swiss-democracy-mcp.svg)](https://pypi.org/project/swiss-democracy-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/swiss-democracy-mcp.svg)](https://pypi.org/project/swiss-democracy-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple)](https://modelcontextprotocol.io/)
[![Swiss Public Data MCP](https://img.shields.io/badge/portfolio-swiss--public--data--mcp-blue)](https://github.com/malkreide/swiss-public-data-mcp)

> 🇨🇭 **Teil des [Swiss Public Data MCP Portfolios](https://github.com/malkreide/swiss-public-data-mcp)** — KI-Modelle mit Schweizer Behördendaten verbinden.

**[🇬🇧 English Version](README.md)** | 🌐 **Deutsch**

Ein MCP-Server für Daten zur direkten Demokratie der Schweiz: alle eidgenössischen Volksabstimmungen seit 1848 und Wahlen seit 1900.

![Demo: Claude nutzt democracy_search_votes, democracy_get_cantonal_results und democracy_get_party_positions](docs/assets/demo.svg)

---

## Demo-Abfrage

```
«Wie hat der Kanton Zürich bei der AHV 21 Initiative 2022 abgestimmt,
 und welche Parteien unterstützten die Vorlage?»
```

→ `democracy_search_votes(keyword="AHV 21", year_from=2022)`  
→ `democracy_get_cantonal_results(vote_number="551")`  
→ `democracy_get_party_positions(vote_number="551")`
[→ Weitere Anwendungsbeispiele nach Zielgruppe →](EXAMPLES.md)

---

## Datenquellen

| Quelle | Abdeckung | Authentifizierung |
|---|---|---|
| **[Swissvotes](https://swissvotes.ch)** (Uni Bern) | Alle Bundesabstimmungen seit 1848 · 874 Spalten · Parteistimmempfehlungen · Kantonsresultate | Keine ✓ |
| **[BFS / opendata.swiss](https://opendata.swiss/de/dataset/echtzeitdaten-am-abstimmungstag-zu-eidgenoessischen-abstimmungsvorlagen)** | Echtzeit & Archiv (seit 1981) · Gemeindeebene | Keine ✓ |
| **[SRGSSR Polis](https://developer.srgssr.ch/api-catalog/srgssr-polis)** | Abstimmungen & Wahlen seit 1900 · Gemeindedetail | OAuth2-Key |

---

## Tools

### Phase 1 — Swissvotes (keine Authentifizierung)

| Tool | Beschreibung |
|---|---|
| `democracy_search_votes` | Alle eidgenössischen Volksabstimmungen seit 1848 durchsuchen (Stichwort, Zeitraum, Rechtsform, Ergebnis, Politikbereich) |
| `democracy_get_vote_detail` | Vollständige Details: offizieller Titel, Parlamentsempfehlungen, Nationalergebnis, Unterschriften |
| `democracy_get_party_positions` | Parteistimmempfehlungen (FDP, SP, SVP, Die Mitte, GPS, GLP, …) mit Kampagnenfinanzierung |
| `democracy_get_cantonal_results` | Resultate aller 26 Kantone: Ja-%, Beteiligung, Annahme |
| `democracy_list_vote_dates` | Alle Abstimmungsdaten mit Anzahl Vorlagen |

### Phase 2 — BFS Echtzeit (keine Authentifizierung)

| Tool | Beschreibung |
|---|---|
| `democracy_bfs_list_vote_dates` | Alle BFS-Abstimmungsdaten (Archiv + aktuell) |
| `democracy_bfs_get_vote_results` | Echtzeit- oder Archivresultate auf nationaler, kantonaler oder Gemeindeebene |

### Phase 3 — SRGSSR Polis (API-Key erforderlich)

| Tool | Beschreibung |
|---|---|
| `democracy_polis_list_votations` | Historische Volksabstimmungen seit 1900 |
| `democracy_polis_get_votation_detail` | Polis-Detail, optional mit Gemeinderesultaten |
| `democracy_polis_list_elections` | National- und Ständeratswahlen, kantonale Wahlen seit 1900 |

---

## Installation

### Claude Desktop (stdio)

In `claude_desktop_config.json` einfügen:

```json
{
  "mcpServers": {
    "swiss-democracy": {
      "command": "uvx",
      "args": ["swiss-democracy-mcp"],
      "env": {
        "SRGSSR_CONSUMER_KEY": "dein_key",
        "SRGSSR_CONSUMER_SECRET": "dein_secret"
      }
    }
  }
}
```

> Die `SRGSSR_*`-Variablen sind optional. Ohne sie funktionieren alle Swissvotes- und BFS-Tools vollständig. Nur die Polis-Tools benötigen Credentials.

### Cloud / Render.com (Streamable HTTP)

```bash
pip install swiss-democracy-mcp
# An alle Interfaces binden NUR in einer Container-/Cloud-Umgebung:
MCP_TRANSPORT=streamable_http MCP_HOST=0.0.0.0 MCP_PORT=8000 python -m swiss_democracy_mcp.server
```

`MCP_HOST` ist standardmässig `127.0.0.1` (loopback). Setze `MCP_HOST=0.0.0.0`
**ausschliesslich** in einer abgesicherten Container-/Cloud-Umgebung — nie auf
einem lokalen Rechner, da der Server sonst im ganzen Netzwerk erreichbar wäre.

---

## Konfiguration

Alle Konfiguration erfolgt über Umgebungsvariablen (siehe [`.env.example`](.env.example)):

| Variable | Default | Zweck |
|---|---|---|
| `MCP_TRANSPORT` | `stdio` | `stdio` (lokal) oder `streamable_http` (Cloud) |
| `MCP_HOST` | `127.0.0.1` | HTTP-Bind-Adresse — `0.0.0.0` **nur** im Container |
| `MCP_PORT` | `8000` | HTTP-Port |
| `LOG_LEVEL` | `INFO` | strukturierte JSON-Logs auf **stderr** |
| `SRGSSR_CONSUMER_KEY` / `SRGSSR_CONSUMER_SECRET` | — | optional, nur für `democracy_polis_*` |

Secrets werden als `SecretStr` gehalten und nie geloggt. Siehe
[docs/secret-management.md](docs/secret-management.md) und
[docs/security.md](docs/security.md).

## MCP-Primitive

Dieser Server exponiert bewusst **nur Tools** (keine Resources/Prompts). Er ist
ein Phase-1-Read-only-Wrapper (siehe [docs/roadmap.md](docs/roadmap.md)): kleine
Tool-Oberfläche (10 use-case-orientierte Tools), jede Antwort ist in sich
abgeschlossen und enthält Quellenangaben. Resources (z.B. `vote://{anr}`) sind
ein Kandidat für eine spätere Phase.

## MCP-Protokoll-Version

Die Protokoll-Version entspricht der von `mcp[cli]>=1.6.0` (FastMCP)
ausgehandelten. SDK-Updates werden monatlich via Dependabot verfolgt; Bumps sind
im [CHANGELOG.md](CHANGELOG.md) dokumentiert.

---

## Portfolio-Synergie

Kombinierbar mit anderen Servern aus dem Swiss Public Data MCP Portfolio:

- **[zurich-opendata-mcp](https://github.com/malkreide/zurich-opendata-mcp)** — Zürcher Stadtstatistiken ergänzen
- **[swiss-statistics-mcp](https://github.com/malkreide/swiss-statistics-mcp)** — BFS-Bevölkerungsdaten nach Kanton
- **[srgssr-mcp](https://github.com/malkreide/srgssr-mcp)** — SRF-Nachrichtenarchiv zu Abstimmungsdaten verknüpfen

---

## Sicherheit & Limits

- **Nur lesend:** Alle Tools führen ausschliesslich HTTP-GET-Anfragen aus — keine Daten werden upstream geschrieben, verändert oder gelöscht.
- **Egress-Allow-List (SSRF-Schutz):** Ausgehende Anfragen sind auf eine feste Allow-List vertrauenswürdiger Hosts beschränkt (`swissvotes.ch`, `opendata.swiss`, `*.bfs.admin.ch`, `api.srgssr.ch`), ausschliesslich HTTPS. Vom Aufrufer übergebene URLs (BFS-`result_url`) werden zusätzlich aufgelöst und abgelehnt, wenn sie auf private, Loopback- oder Cloud-Metadata-IP-Bereiche zeigen.
- **Keine personenbezogenen Daten:** Swissvotes, BFS und SRGSSR Polis liefern aggregierte demokratische Daten (Abstimmungsresultate, Parteiparolen, kantonale/kommunale Auszählungen). Es werden keine Personendaten (PII) verarbeitet oder gespeichert.
- **Rate Limits:** Swissvotes wird als CSV einmal pro 24h geladen und im Arbeitsspeicher gecacht. BFS / opendata.swiss und SRGSSR Polis sind öffentliche APIs ohne dokumentierte Rate Limits — `limit`- und Datumsbereiche bitte zurückhaltend setzen. Der Server erzwingt einen 30-Sekunden-Timeout pro Anfrage.
- **Datenaktualität:** Echtzeit-BFS-Resultate spiegeln den Upstream-Feed zum Abfragezeitpunkt (kein lokaler Cache). Swissvotes wird alle 24h vom Uni-Bern-Mirror aktualisiert.
- **Nutzungsbedingungen:** Die Daten unterliegen den ToS der jeweiligen Quelle — [swissvotes.ch](https://swissvotes.ch) (CC BY 4.0, Uni Bern), [opendata.swiss](https://opendata.swiss) (meist CC-BY / Open by Default), [SRGSSR Polis](https://developer.srgssr.ch) (Free Tier, nur nicht-kommerzielle Nutzung). Quelle in abgeleiteten Produkten bitte zitieren.
- **Keine Garantien:** Dieser Server ist ein Community-Projekt und nicht mit der Universität Bern, dem Bundesamt für Statistik oder der SRG SSR affiliiert. Die Verfügbarkeit hängt von den Upstream-APIs ab.

---

## Bekannte Einschränkungen

- **Swissvotes:** Kantonsresultate seit 1848; Gemeinderesultate nur via SRGSSR Polis.
- **BFS-Archiv:** Deckt Bundesabstimmungen erst ab 1981 ab.
- **Polis-Tools:** Kostenlose Registrierung auf [developer.srgssr.ch](https://developer.srgssr.ch) nötig. Nur nichtkommerziell.
- **CSV-Cache:** Der Swissvotes-Datensatz wird im Arbeitsspeicher gecacht (24 Stunden TTL).

---

## Tests

```bash
# Unit-Tests (kein Netzwerk nötig)
PYTHONPATH=src pytest tests/ -m "not live" -v

# Live-Tests (Netzwerk erforderlich)
PYTHONPATH=src pytest tests/ -m "live" -v
```

---

## Mitwirken

Siehe [CONTRIBUTING.de.md](CONTRIBUTING.de.md) ([🇬🇧 English](CONTRIBUTING.md)).

---

## Sicherheit

Siehe [SECURITY.de.md](SECURITY.de.md) ([🇬🇧 English](SECURITY.md)) für die Sicherheitslage und das Melden von Schwachstellen.

---

## Lizenz

MIT — siehe [LICENSE](LICENSE).

Datenlizenz:
- Swissvotes: [Creative Commons BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- BFS / opendata.swiss: [Freie Nutzung](https://opendata.swiss/de/terms-of-use)
- SRGSSR Polis: Nur nichtkommerzielle Nutzung — [developer.srgssr.ch](https://developer.srgssr.ch)
