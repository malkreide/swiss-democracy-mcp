# swiss-democracy-mcp

[![CI](https://github.com/malkreide/swiss-democracy-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/malkreide/swiss-democracy-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/swiss-democracy-mcp.svg)](https://pypi.org/project/swiss-democracy-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/swiss-democracy-mcp.svg)](https://pypi.org/project/swiss-democracy-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Swiss Public Data MCP](https://img.shields.io/badge/portfolio-swiss--public--data--mcp-blue)](https://github.com/malkreide/swiss-public-data-mcp)

> **Part of the [Swiss Public Data MCP Portfolio](https://github.com/malkreide/swiss-public-data-mcp)** — connecting AI models to Swiss institutional data sources.

An MCP server providing access to Swiss direct democracy data, covering all federal popular votes since 1848 and elections since 1900.

---

## Demo Query

```
«Wie hat der Kanton Zürich bei der AHV 21 Initiative 2022 abgestimmt,
 und welche Parteien unterstützten die Vorlage?»
```

→ `democracy_search_votes(keyword="AHV 21", year_from=2022)`  
→ `democracy_get_cantonal_results(vote_number="551")`  
→ `democracy_get_party_positions(vote_number="551")`

---

## Data Sources

| Source | Coverage | Auth |
|---|---|---|
| **[Swissvotes](https://swissvotes.ch)** (Uni Bern) | All federal votes since 1848 · 874 columns · party positions · cantonal results | None ✓ |
| **[BFS / opendata.swiss](https://opendata.swiss/de/dataset/echtzeitdaten-am-abstimmungstag-zu-eidgenoessischen-abstimmungsvorlagen)** | Real-time & archive (since 1981) · municipality level | None ✓ |
| **[SRGSSR Polis](https://developer.srgssr.ch/api-catalog/srgssr-polis)** | Votes & elections since 1900 · municipality detail | OAuth2 key |

---

## Tools

### Phase 1 — Swissvotes (No Auth Required)

| Tool | Description |
|---|---|
| `democracy_search_votes` | Search all federal popular votes since 1848 by keyword, date range, legal form, outcome, policy domain |
| `democracy_get_vote_detail` | Full details for a specific vote: official title, parliamentary positions, national result, signatures |
| `democracy_get_party_positions` | Party recommendations (FDP, SP, SVP, Die Mitte, GPS, GLP, …) with campaign finance data |
| `democracy_get_cantonal_results` | Results for all 26 cantons: yes%, turnout, accepted flag |
| `democracy_list_vote_dates` | List all voting dates with number of proposals per date |

### Phase 2 — BFS Real-Time (No Auth Required)

| Tool | Description |
|---|---|
| `democracy_bfs_list_vote_dates` | List all BFS voting dates (archive + current) |
| `democracy_bfs_get_vote_results` | Real-time or archived results at national, cantonal, or municipality level |

### Phase 3 — SRGSSR Polis (API Key Required)

| Tool | Description |
|---|---|
| `democracy_polis_list_votations` | Historical votations since 1900 with municipality-level data |
| `democracy_polis_get_votation_detail` | Full Polis detail, optionally with all municipality results |
| `democracy_polis_list_elections` | National Council, Council of States, and cantonal elections since 1900 |

---

## Installation

### Claude Desktop (stdio)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "swiss-democracy": {
      "command": "uvx",
      "args": ["swiss-democracy-mcp"],
      "env": {
        "SRGSSR_CONSUMER_KEY": "your_key_here",
        "SRGSSR_CONSUMER_SECRET": "your_secret_here"
      }
    }
  }
}
```

> The `SRGSSR_*` variables are optional. Without them, all Swissvotes and BFS tools remain fully functional. Only the Polis tools require credentials.

### Cloud / Render.com (Streamable HTTP)

```bash
pip install swiss-democracy-mcp
MCP_TRANSPORT=streamable_http MCP_PORT=8000 python -m swiss_democracy_mcp.server
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Claude / LLM Host              │
└──────────────┬──────────────────────────────┘
               │ MCP (stdio / Streamable HTTP)
┌──────────────▼──────────────────────────────┐
│         swiss-democracy-mcp                 │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Swissvotes CSV Cache (24h TTL)     │   │
│  │  All 874 columns, since 1848        │   │
│  └──────────────┬──────────────────────┘   │
│                 │                           │
│  ┌──────────────▼──────────────────────┐   │
│  │  BFS / opendata.swiss (no auth)     │   │
│  │  Real-time & archive since 1981     │   │
│  └──────────────┬──────────────────────┘   │
│                 │                           │
│  ┌──────────────▼──────────────────────┐   │
│  │  SRGSSR Polis (OAuth2, optional)    │   │
│  │  Votes & elections since 1900       │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Transport:** stdio for Claude Desktop · Streamable HTTP for cloud/Render.com  
**Auth pattern:** No-Auth-First — Swissvotes & BFS work without any credentials  
**Cache:** Swissvotes CSV is loaded once at startup and cached for 24 hours

---

## Portfolio Synergy

Combine with other servers in the Swiss Public Data MCP portfolio:

- **[zurich-opendata-mcp](https://github.com/malkreide/zurich-opendata-mcp)** — add Zurich city-level statistics to vote analysis
- **[swiss-statistics-mcp](https://github.com/malkreide/swiss-statistics-mcp)** — enrich with BFS demographic data by canton
- **[srgssr-mcp](https://github.com/malkreide/srgssr-mcp)** — link SRF news archive content to specific vote dates

Example multi-server query:  
*«Vergleiche die Abstimmungsresultate zur AHV-Reform mit der Altersstruktur der Kantone»*  
→ `swiss-democracy-mcp` + `swiss-statistics-mcp`

---

## Known Limitations

- **Swissvotes coverage:** Cantonal-level results are available since 1848; municipality-level results only via SRGSSR Polis (since ~1990s depending on the vote).
- **BFS archive:** Real-time service covers federal votes since 1981 only.
- **Polis tools:** Require free registration at [developer.srgssr.ch](https://developer.srgssr.ch). Non-commercial use only.
- **CSV cache:** The Swissvotes dataset is ~several MB and is cached in memory for 24 hours. Memory footprint is accordingly higher than API-only servers.

---

## Testing

```bash
# Unit tests (no network required)
PYTHONPATH=src pytest tests/ -m "not live" -v

# Live tests (require network access)
PYTHONPATH=src pytest tests/ -m "live" -v
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](LICENSE).

Data licenses:
- Swissvotes: [Creative Commons BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- BFS / opendata.swiss: [Open use](https://opendata.swiss/de/terms-of-use)
- SRGSSR Polis: Non-commercial use only — see [developer.srgssr.ch](https://developer.srgssr.ch)
