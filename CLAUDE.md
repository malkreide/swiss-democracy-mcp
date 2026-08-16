# CLAUDE.md

## Vor der Arbeit

Klon-Aktualität prüfen — Standard-Branch ermitteln, nicht `main` annehmen:

```bash
B=$(git ls-remote --symref origin HEAD | sed -n 's|^ref: refs/heads/\([^[:space:]]*\).*|\1|p')
git fetch origin "${B:?Standard-Branch nicht ermittelbar}" &&
  git rev-list --count HEAD..FETCH_HEAD
```

Drei Server im Portfolio heissen ihren Standard-Branch `master`
(`openlex-mcp`, `swiss-courts-mcp`, `swisstopo-mcp`); dort scheitert ein fest
verdrahtetes `origin/main` mit «couldn't find remote ref main». Wer das für ein
Netzproblem hält, arbeitet weiter auf genau dem veralteten Klon, vor dem dieser
Absatz warnt. Den `:?`-Schutz nicht weglassen: Bei leerem `B` fetcht git still
den Remote-HEAD und endet mit 0.

Ein veralteter Klon erzeugt eine rote CI, deren Ursache nicht im Diff steht.
Am 3.8.2026 zweimal passiert — beide Male fehlten genau die Commits, die
das Gate einführten, an dem der Branch scheiterte.

Gates lokal fahren, mit der GEPINNTEN ruff-Version aus der CI. Eine andere
Version meldet Abweichungen, die niemand verursacht hat.

## Tests

Gegenprobe ist Pflicht. Ein Test, der grün bleibt, wenn man die
Implementierung entfernt, prüft nichts. Jede neue Zusicherung einzeln
neutralisieren und zeigen, dass genau die zugehörigen Tests fallen.

Zwei Fallen, die beide grün blieben:

- Eine Fake-Uhr, die nur beim Schlafen vorrückt, kann eine Zusicherung über
  echte Zeit nicht widerlegen.
- `monkeypatch.setattr(modul.asyncio, "sleep", ...)` greift ins Modul
  `asyncio` selbst und entschärft die Mechanik im ganzen Prozess. Patche
  einen Modul-Alias (`_sleep = asyncio.sleep`), nicht das fremde Modul.

Handgeschriebene Fixtures kodieren die Annahme des Autors und können sie
nicht widerlegen. Mindestens eine aufgezeichnete Antwort pro externem
Endpunkt, mit Aufnahmedatum.

## Wenn etwas rot ist

Roter Live-Test: erst die Quelle abfragen, dann einordnen. Nicht aus der
Fehlermeldung schliessen. Am 3.8.2026 hiess "nicht gefunden" nicht, dass der
Datensatz weg war, sondern dass die Quelle die Schreibweise ihrer Kopfzeile
gewechselt hatte — vier von sechs Datensätzen produktiv kaputt, alle
Unit-Tests grün.

PR ohne jeden Check ist selten ein Repo ohne CI, meistens ein
Merge-Konflikt: GitHub berechnet dafür keinen Merge-Commit und startet nichts.

Ein Codex-Review auf einem PR wird beantwortet oder behoben, nie ignoriert.

## Dieses Repo

**ruff-Pin: eine Quelle.** `pyproject.toml`, `dev`-Extra, `ruff==0.16.1`.
Die CI hat keinen eigenen Pin-Schritt — `pip install ".[dev]"` genügt, lokal
wie dort. Eine `.pre-commit-config.yaml` gibt es nicht; wenn eine dazukommt,
muss sie dieselbe Version aus `pyproject.toml` beziehen und keine zweite
nennen. Beim Anheben `ruff format` einmal über `src/ tests/ scripts/` laufen
lassen und das Ergebnis mitcommitten.

Gates, wörtlich aus `ci.yml` (Python 3.11/3.12/3.13):

```
python -m ruff check src/ tests/ scripts/
python -m ruff format --check src/ tests/ scripts/
PYTHONPATH=src python -m pytest tests/ -m "not live" -v
python scripts/check_version_sync.py
```

Alle vier laufen in einem Job auf allen drei Feldern — keine
`if:`-Ausnahme, kein zweiter lint-Job. Ein grünes 3.13 heisst hier wirklich,
dass alles auf 3.13 lief; im Portfolio ist das nicht durchgehend so. Ein
`fail-fast: false` steht nicht da.

Dazu ein Gitleaks-Secret-Scan über die volle Historie (`fetch-depth: 0`) —
als eigener Job `secret-scan`, den keiner der Befehle oben nachstellt.

**Live-Tests: DRIFT-005 erfüllt, aber die Abdeckung ist ungleich.**
`.github/workflows/live-tests.yml` läuft geplant (`cron: "13 5 * * 1"`, dazu
`workflow_dispatch`) und öffnet/schliesst bei Bedarf ein `upstream`-Issue.
Die PR-CI schliesst die Live-Tests per `-m "not live"` aus — das ist hier
kein Verstoss, weil der geplante Lauf existiert. `schedule` greift nur auf
dem Default-Branch: Änderungen an dieser Datei wirken erst nach dem Merge,
vorher von Hand per `workflow_dispatch` auslösen.

**Der Lauf erreicht `swissvotes.ch`, sonst nichts.** Zwei der zehn Werkzeuge
sind live abgedeckt; `opendata.swiss`/BFS gar nicht, Polis nicht, weil es
`SRGSSR_CONSUMER_KEY`/`-SECRET` verlangt und der Workflow keine hereinreicht.
Der Workflow nannte trotzdem `api.srgssr.ch` als sein Ziel — die eine Quelle,
die er nicht abfragt — und legte seine Issues unter diesem Namen an. Bei
rotem Lauf zuerst die Quelle abzufragen heisst dann: die falsche abfragen.
`tests/test_live_abdeckung.py` hält beides fest, und es leitet die Abdeckung
aus den `-m live`-Tests ab statt sie aufzuschreiben — ein neues Werkzeug muss
dort eingeordnet werden, sonst fällt der Test.
