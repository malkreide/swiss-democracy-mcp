## Finding: ARCH-003

**Severity:** medium
**Status:** Open
**Check:** ARCH-003  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Leere Resultate werden ohne Heuristik/Vorschläge zurückgegeben; Lookup-Tools liefern blosse Fehlermeldung.

### Evidence
- `democracy_search_votes` liefert strukturiertes Envelope mit total/count/has_more auch bei 0 Treffern (server.py:452-459)

### Gaps
- Kein `match_type`-Feld, kein Fuzzy-/Suggestion-Mechanismus
- Detail-/Party-/Cantonal-Tools geben bei Nicht-Treffer nur `{"error": "...nicht gefunden"}` zurück (server.py:512,597,665)

### Expected Behavior
Bei nicht-sensiblen Such-Tools: Fuzzy-Fallback + `match_type` + actionable Hinweis.

### Remediation
Bei `search_votes` Fuzzy-/Vorschlags-Logik ergänzen, `match_type` (exact/fuzzy/none) ins Envelope. Daten sind public → Heuristik unbedenklich.

### Effort
S — ~30 Min pro Such-Tool.

