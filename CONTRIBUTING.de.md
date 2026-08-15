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

## Die Live-Suite: wann sie läuft, und wer ein rotes Ergebnis sieht

**Kadenz:** jeden Montag um 05:13 UTC, dazu jederzeit von Hand über *Actions → Live-Tests → Run
workflow*. Siehe [`.github/workflows/live-tests.yml`](.github/workflows/live-tests.yml).

**Wer es sieht:** Ein roter Lauf öffnet ein Issue mit dem Label `upstream` und dem stabilen Titel «Live-Tests gegen api.srgssr.ch rot (<Datum>)». Ein zweiter roter Lauf erkennt das offene Issue am Titelanfang und hängt sich an denselben Thread, statt ein zweites aufzumachen. Wird die Suite wieder grün, schliesst sich das Issue selbst.

**Drei Antworten, nicht zwei.** `scripts/classify_live_run.py` liest das JUnit-XML statt des
Exit-Codes und unterscheidet: `clear` (gelaufen, grün), `finding` (gelaufen,
etwas gefallen) und `unknown` (nicht gelaufen — Installation gescheitert, null
Tests eingesammelt, alle übersprungen). Ein `unknown` schliesst nie ein Issue:
Zuzumachen hiesse zu behaupten, der Vergleich sei gelaufen.

**Ein roter Live-Lauf heisst nicht zwingend «unser Fehler».** Er heisst: Der
Vertrag mit der Quelle hat sich geändert, oder die Quelle ist gerade aus. Beides
gehört gesehen, nur das Erste gehört gefixt. Bitte den Lauf lesen, bevor der Job
deaktiviert wird — so stirbt dieser Check, und er ist der einzige im Repo, der
einer falschen Grundannahme über api.srgssr.ch widersprechen kann. Jeder andere Test
prüft gegen eine Fixture, und die Fixture ist aus derselben Annahme geschrieben
wie der Code.

## Lizenz

Mit Ihrem Beitrag erklären Sie sich damit einverstanden, dass Ihre Beiträge unter der [MIT-Lizenz](LICENSE) lizenziert werden.
