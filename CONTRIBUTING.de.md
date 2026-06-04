# Mitwirken an swiss-democracy-mcp

[🇬🇧 English Version](CONTRIBUTING.md)

Vielen Dank für Ihr Interesse an einem Beitrag! Dieser Server ist Teil des [Swiss Public Data MCP Portfolios](https://github.com/malkreide/swiss-public-data-mcp).

## Entwicklungs-Setup

```bash
git clone https://github.com/malkreide/swiss-democracy-mcp.git
cd swiss-democracy-mcp
pip install -e ".[dev]"
```

## Tests ausführen

```bash
# Nur Unit-Tests (kein Netzwerk, schnell)
PYTHONPATH=src pytest tests/ -m "not live" -v

# Alle Tests inkl. Live-API-Aufrufe
PYTHONPATH=src pytest tests/ -v
```

## Code-Stil

Dieses Projekt nutzt [ruff](https://docs.astral.sh/ruff/) für das Linting:

```bash
python -m ruff check src/ tests/
python -m ruff check src/ tests/ --fix
```

## Neue Tools hinzufügen

1. Ein Pydantic-Input-Modell definieren (Pydantic v2, `model_config = ConfigDict(extra="forbid")`)
2. Eine `async def`-Tool-Funktion mit `@mcp.tool(name=..., annotations=...)` implementieren
3. Einen umfassenden Docstring mit Args-/Returns-Abschnitten schreiben
4. Unit-Tests mit `respx`-Mocking für HTTP-Aufrufe ergänzen
5. Live-Tests mit `@pytest.mark.live` markieren

## Hinweise zu den Datenquellen

- **Swissvotes-CSV** — 874 Spalten, semikolongetrennt, mit BOM-Präfix. Wird einmal beim Start geladen und 24h gecacht. Die Spaltennamen folgen dem Swissvotes-Codebook: https://swissvotes.ch/page/dataset
- **BFS opendata.swiss** — CKAN-API, keine Authentifizierung. Package-IDs sind stabil.
- **SRGSSR Polis** — OAuth2 Client Credentials. Tokens werden im Arbeitsspeicher gecacht.

## Pull Requests

Bitte eröffnen Sie für grössere Änderungen zuerst ein Issue. PRs sollten Tests enthalten und das `ruff`-Linting bestehen.

## Lizenz

Mit Ihrem Beitrag erklären Sie sich damit einverstanden, dass Ihre Beiträge unter der [MIT-Lizenz](LICENSE) lizenziert werden.
