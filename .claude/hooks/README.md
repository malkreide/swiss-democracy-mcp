# SessionStart-Hook: Klon-Aktualität

`session-start.sh` meldet beim Sessionstart, wie viele Commits der
ausgecheckte Stand hinter `origin/<default-branch>` liegt. Liegt er nicht
zurück, sagt er nichts.

Registriert in `../settings.json` (strenges JSON, deshalb steht der Grund
hier und nicht dort).

## Grund

Ein veralteter Klon hat am 3.8.2026 zweimal eine rote CI erzeugt, deren
Ursache nicht im Diff stand — die fehlenden Commits waren jeweils genau die,
die das Gate einführten, an dem der Branch scheiterte. Man sucht den Fehler
dann in den geänderten Dateien, und dort ist er nicht. Die Prüfung kostet
eine Sekunde und ersetzt eine Fehlersuche in den falschen Dateien.

## Was der Hook garantiert

**Er blockiert die Session nie.** Kein `set -e`, kein `set -o pipefail`,
jeder Pfad endet in `exit 0`. Ein Hook, der bei Netzproblemen die Arbeit
anhält, wird nach dem zweiten Mal abgeschaltet und schützt danach gar nichts.
Still durch gehen:

| Fall | Verhalten |
| --- | --- |
| Kein Git-Repo | still `exit 0` |
| Kein Remote `origin` | still `exit 0` |
| Detached HEAD | still `exit 0` — kein Branch, der hinterherhinken könnte |
| Kein Netz / DNS flattert / Auth fehlt | `fetch` scheitert, still `exit 0` |
| Netz hängt | Zeitgrenze greift (Default 5 s), still `exit 0` |
| Default-Branch nicht ermittelbar | still `exit 0` — lieber schweigen als raten |
| 0 Commits zurück | still `exit 0` |

Ausgabe gibt es also nur im einen Fall, der eine Handlung auslöst: es fehlen
tatsächlich Commits.

## Zeitgrenze

Netz-Kommandos (`fetch`, notfalls `ls-remote`) laufen unter einer harten
Grenze von 5 Sekunden, überschreibbar per `CLAUDE_STALENESS_TIMEOUT`.
Fehlt `timeout` im Image, greift ein portabler Ersatz (Hintergrundprozess +
Poll + Kill), damit die Grenze auch dort real ist. Zusätzlich sind
`GIT_TERMINAL_PROMPT=0`, `GIT_ASKPASS` und `ssh -o BatchMode=yes` gesetzt:
eine Passwortabfrage auf einem Hook ohne TTY blockiert genau so lange wie
ein hängendes Netz.

In `settings.json` steht zusätzlich `"timeout": 15` als zweite Bremse — falls
die skriptinterne Grenze je versagt, beendet Claude Code den Hook selbst.

## Default-Branch

Wird ermittelt, nicht angenommen:

1. `git symbolic-ref refs/remotes/origin/HEAD` — lokal, kostet kein Netz.
2. Falls der Zeiger fehlt: `git ls-remote --symref origin HEAD`, unter
   derselben Zeitgrenze.
3. Bleibt beides leer: schweigen. Kein Rateschritt auf `main`.

`main` anzunehmen ist nicht theoretisch falsch, sondern praktisch: im
Portfolio heissen `openlex-mcp`, `swiss-courts-mcp` und `swisstopo-mcp` ihren
Default-Branch `master`. Genau diese Annahme hat schon einmal einen Branch
15 Commits alt werden lassen — die Prüfung schlug still fehl, und niemand
sah es.

## Warum kein Vergleich gegen ein veraltetes lokales `origin/<branch>`

Scheitert das `fetch`, könnte der Hook gegen den zuletzt bekannten Remote-Ref
zählen. Tut er nicht: diese Zahl sähe aus wie eine Messung, wäre aber so alt
wie der letzte erfolgreiche Fetch. Eine falsche Zahl ist schlechter als keine.

## Lokal testen

```bash
CLAUDE_PROJECT_DIR="$PWD" .claude/hooks/session-start.sh; echo "exit=$?"
```

Stiller Lauf mit `exit=0` heisst: Stand ist aktuell (oder einer der
Ausnahmefälle oben griff).
