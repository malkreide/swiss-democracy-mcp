# CLAUDE.md

## Vor der Arbeit

Klon-Aktualität prüfen: `git fetch origin main && git rev-list --count HEAD..origin/main`
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

**ruff-Pin divergiert.** `.github/workflows/ci.yml` installiert
`ruff==0.16.1`. Eine `.pre-commit-config.yaml` gibt es nicht, und
`pyproject.toml` deklariert im `dev`-Extra nur `ruff>=0.4.0`. Ein
`pip install ".[dev]"` zieht also die jeweils neueste Version — nicht die
des Gates. Lokal explizit `pip install ruff==0.16.1` nachschieben.

Gates, wörtlich aus `ci.yml` (Python 3.11/3.12/3.13):

```
python -m ruff check src/ tests/ scripts/
python -m ruff format --check src/ tests/ scripts/
PYTHONPATH=src python -m pytest tests/ -m "not live" -v
python scripts/check_version_sync.py
```

Dazu ein Gitleaks-Secret-Scan über die volle Historie (`fetch-depth: 0`).

**Live-Tests: DRIFT-005 erfüllt.** `.github/workflows/live-tests.yml` läuft
geplant (`cron: "13 5 * * 1"`, dazu `workflow_dispatch`) gegen
`api.srgssr.ch` und öffnet/schliesst bei Bedarf ein `upstream`-Issue. Die
PR-CI schliesst die Live-Tests per `-m "not live"` aus — das ist hier kein
Verstoss, weil der geplante Lauf existiert. `schedule` greift nur auf dem
Default-Branch: Änderungen an dieser Datei wirken erst nach dem Merge,
vorher von Hand per `workflow_dispatch` auslösen.
