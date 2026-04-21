# Use Cases & Examples — swiss-democracy-mcp

Real-world queries by audience. Indicate per example whether an API key is required.

### 🏫 Bildung & Schule
Lehrpersonen, Schulbehörden, Fachreferent:innen

**Abstimmungsgeschichte im Unterricht**
«Wie hat sich das Stimmverhalten bei Vorlagen zum Thema 'Bildung' in den letzten 20 Jahren entwickelt, und wie stimmten die Kantone?»
→ `democracy_search_votes(policy_domain="Bildung", year_from=2004, year_to=2024)`
→ `democracy_get_cantonal_results(vote_number="500")`
*(Kein API-Key nötig)*

Warum nützlich: Erlaubt Lehrpersonen, historische Entwicklungen anhand konkreter Datenquellen für den Staatskundeunterricht aufzubereiten.

**Analyse von Parteistrategien**
«Welche Parteien haben die letzte grosse Bildungsreform unterstützt und gab es einen Unterschied zwischen der Empfehlung des Bundesrates und dem Volk?»
→ `democracy_search_votes(keyword="Bildung", limit=5)`
→ `democracy_get_party_positions(vote_number="600")`
→ `democracy_get_vote_detail(vote_number="600")`
*(Kein API-Key nötig)*

Warum nützlich: Fördert das kritische Denken von Schüler:innen durch den Vergleich von Parteiparolen mit dem tatsächlichen Abstimmungsverhalten.

### 👨‍👩‍👧 Eltern & Schulgemeinde
Elternräte, interessierte Erziehungsberechtigte

**Familienpolitische Vorlagen im Fokus**
«Wie wurde in der Vergangenheit über Vorlagen zur familienergänzenden Kinderbetreuung oder Mutterschaftsversicherung abgestimmt?»
→ `democracy_search_votes(keyword="Mutterschaft", year_from=1990)`
→ `democracy_get_vote_detail(vote_number="511")`
*(Kein API-Key nötig)*

Warum nützlich: Hilft Eltern, die politische Entwicklung von familienrelevanten Themen besser einzuordnen.

**Kantonale Unterschiede bei Familienthemen**
«Haben städtische Kantone wie Zürich oder Basel-Stadt familienergänzende Vorlagen häufiger angenommen als ländliche Kantone?»
→ `democracy_get_cantonal_results(vote_number="511")`
*(Kein API-Key nötig)*

Warum nützlich: Macht kantonale Unterschiede bei Abstimmungen greifbar, die direkte Auswirkungen auf den Familienalltag haben.

### 🗳️ Bevölkerung & öffentliches Interesse
Allgemeine Öffentlichkeit, politisch und gesellschaftlich Interessierte

**Echtzeit-Resultate am Abstimmungssonntag**
«Wie sehen die aktuellen Resultate der heutigen Abstimmung auf nationaler und kantonaler Ebene aus?»
→ `democracy_bfs_list_vote_dates()`
→ `democracy_bfs_get_vote_results(result_url="https://opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-eidgenoessischen-abstimmungsvorlagen", level="cantonal")`
*(Kein API-Key nötig)*

Warum nützlich: Bietet der Bevölkerung direkte, unverfälschte Live-Daten ohne Umweg über Medienportale.

**Historische Vergleiche aktueller Debatten**
«Wurde schon früher über ähnliche AHV-Reformen abgestimmt, und wie fielen die Resultate damals aus?»
→ `democracy_search_votes(keyword="AHV", year_from=1970)`
→ `democracy_get_cantonal_results(vote_number="651")`
*(Kein API-Key nötig)*

Warum nützlich: Ermöglicht es Bürger:innen, aktuelle politische Debatten in einen grösseren historischen Kontext zu setzen.

### 🤖 KI-Interessierte & Entwickler:innen
MCP-Enthusiast:innen, Forscher:innen, Prompt Engineers, öffentliche Verwaltung

**Detaillierte Gemeindeanalysen (Polis)**
«Wie unterschied sich das Abstimmungsverhalten bei der letzten Steuerreform auf Gemeindeebene zwischen Stadt und Land?»
→ `democracy_polis_list_votations(year_from=2015, limit=10)`
→ `democracy_polis_get_votation_detail(votation_id="12345", include_municipalities=true)`
*(API-Key nötig)*

Warum nützlich: Demonstriert die Leistungsfähigkeit von granularen Datenabfragen über die SRGSSR Polis-API für tiefergehende Analysen.

**Kombination mit Demografiedaten (Multi-Server)**
«Vergleiche die kantonalen Resultate der Abstimmung zur 'Ehe für alle' mit dem Durchschnittsalter der Kantone.»
→ `democracy_search_votes(keyword="Ehe für alle")` (aus swiss-democracy-mcp)
→ `democracy_get_cantonal_results(vote_number="647")` (aus swiss-democracy-mcp)
→ `stat_get_data(...)` (aus [swiss-statistics-mcp](https://github.com/malkreide/swiss-statistics-mcp))
*(Kein API-Key nötig)*

Warum nützlich: Zeigt die Stärke der Multi-Server-Orchestrierung, um Abstimmungsverhalten mit soziodemografischen Faktoren zu korrelieren.

### 🔧 Technische Referenz: Tool-Auswahl nach Anwendungsfall

| Ich möchte… | Tool(s) | Auth nötig? |
|---|---|---|
| …historische Abstimmungen zu einem Thema finden | `democracy_search_votes` | Nein |
| …sehen, wer für oder gegen eine Vorlage war | `democracy_get_party_positions`, `democracy_get_vote_detail` | Nein |
| …wissen, wie die einzelnen Kantone abgestimmt haben | `democracy_get_cantonal_results` | Nein |
| …Live-Ergebnisse am Abstimmungssonntag verfolgen | `democracy_bfs_list_vote_dates`, `democracy_bfs_get_vote_results` | Nein |
| …Resultate bis auf Gemeindeebene analysieren | `democracy_polis_list_votations`, `democracy_polis_get_votation_detail` | Ja (Polis API-Key) |
| …historische Wahlen ab 1900 recherchieren | `democracy_polis_list_elections` | Ja (Polis API-Key) |
