"""Was der geplante Live-Lauf erreicht — und was er nur behauptet.

Dieser Server bedient drei Quellen: swissvotes.ch (CSV-Datensatz),
opendata.swiss/BFS und die SRGSSR-Polis-API. Der Workflow `live-tests.yml`
hiess bis zu diesem Test «Live-Suite gegen api.srgssr.ch» und legte seine
Issues unter demselben Namen an — ausgerechnet die eine Quelle, die er nicht
erreichen kann: Polis verlangt SRGSSR_CONSUMER_KEY/-SECRET, und der Workflow
reicht keine herein.

Das ist kein Schoenheitsfehler. Die Konvention lautet, bei rotem Live-Test
zuerst die Quelle abzufragen und nicht aus der Fehlermeldung zu schliessen —
und genau dafuer nennt das Issue die falsche Quelle. Wer ihm folgt, prueft
developer.srgssr.ch, waehrend der Swissvotes-Datensatz seine Kopfzeile
geaendert hat.

Ein Name in einem Workflow faellt nicht von selbst um. Deshalb steht er hier
gegen zwei mechanisch abgeleitete Groessen: gegen die Umgebung, die der
Workflow tatsaechlich mitgibt, und gegen die Werkzeuge, die die `-m live`-Tests
tatsaechlich aufrufen.
"""

from __future__ import annotations

import ast
import pathlib

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_WORKFLOW = _ROOT / ".github" / "workflows" / "live-tests.yml"
_SERVER = _ROOT / "src" / "swiss_democracy_mcp" / "server.py"
_TESTS = _ROOT / "tests" / "test_server.py"

# Quellen, die ohne Zugangsdaten nichts herausgeben, und die Variablen, unter
# denen der Server sie erwartet. Ein Workflow, der eine solche Quelle als sein
# Ziel ausgibt, muss sie auch mitgeben.
_QUELLEN_MIT_ZUGANGSDATEN = {
    "api.srgssr.ch": ("SRGSSR_CONSUMER_KEY", "SRGSSR_CONSUMER_SECRET"),
}

# Werkzeuge ohne Live-Abdeckung, je mit dem Grund. Wer ein Werkzeug ergaenzt,
# ordnet es hier ein oder deckt es live ab — sonst faellt der Test unten.
_BEWUSST_OHNE_LIVE_TEST = {
    "democracy_bfs_list_vote_dates": "opendata.swiss/BFS — keine Live-Abdeckung",
    "democracy_bfs_get_vote_results": "opendata.swiss/BFS — keine Live-Abdeckung",
    "democracy_polis_list_votations": "Polis — braucht SRGSSR-Zugangsdaten",
    "democracy_polis_get_votation_detail": "Polis — braucht SRGSSR-Zugangsdaten",
    "democracy_polis_list_elections": "Polis — braucht SRGSSR-Zugangsdaten",
    "democracy_get_vote_detail": "swissvotes.ch — von der Live-Suite nicht beruehrt",
    "democracy_get_party_positions": "swissvotes.ch — von der Live-Suite nicht beruehrt",
    "democracy_list_vote_dates": "swissvotes.ch — von der Live-Suite nicht beruehrt",
}


def _werkzeuge() -> set[str]:
    """Alle mit `@mcp.tool` ausgezeichneten Funktionen aus server.py."""
    baum = ast.parse(_SERVER.read_text(encoding="utf-8"))
    gefunden = set()
    for knoten in ast.walk(baum):
        if not isinstance(knoten, ast.AsyncFunctionDef | ast.FunctionDef):
            continue
        for schmuck in knoten.decorator_list:
            ziel = schmuck.func if isinstance(schmuck, ast.Call) else schmuck
            if isinstance(ziel, ast.Attribute) and ziel.attr == "tool":
                gefunden.add(knoten.name)
    return gefunden


def _live_abgedeckte_werkzeuge() -> set[str]:
    """Werkzeuge, die aus einem `@pytest.mark.live`-Test heraus aufgerufen werden.

    Abgeleitet, nicht aufgeschrieben: Wer einen Live-Test entfernt, aendert
    dieses Ergebnis, ohne diese Datei anzufassen.
    """
    baum = ast.parse(_TESTS.read_text(encoding="utf-8"))
    gefunden = set()
    for knoten in ast.walk(baum):
        if not isinstance(knoten, ast.AsyncFunctionDef | ast.FunctionDef):
            continue
        marken = {
            s.attr
            for s in knoten.decorator_list
            if isinstance(s, ast.Attribute) and isinstance(s.value, ast.Attribute)
        }
        if "live" not in marken:
            continue
        for innen in ast.walk(knoten):
            if isinstance(innen, ast.Call) and isinstance(innen.func, ast.Name):
                if innen.func.id.startswith("democracy_"):
                    gefunden.add(innen.func.id)
    return gefunden


def _workflow_ohne_kommentare() -> str:
    """Der Workflow ohne Kommentarzeilen — YAML (`#`) wie eingebettetes JS (`//`).

    Ohne dieses Ausschneiden loeste der erklaerende Hinweis den Test aus, der
    im Workflow an der Stelle des frueheren Namens steht und api.srgssr.ch
    zitiert. Ein Test, den seine eigene Begruendung rot macht, ist kaputt.
    """
    zeilen = [
        z
        for z in _WORKFLOW.read_text(encoding="utf-8").splitlines()
        if not z.lstrip().startswith(("#", "//"))
    ]
    return "\n".join(zeilen)


def test_der_workflow_nennt_keine_quelle_die_er_nicht_erreicht() -> None:
    """Ein Ziel ohne die noetigen Zugangsdaten ist eine Behauptung, keine Pruefung.

    Rein mechanisch: Steht der Host im Workflow, muessen auch die Variablen
    darin stehen, ohne die der Server ihn gar nicht erst abfragt.
    """
    text = _workflow_ohne_kommentare()
    for host, variablen in _QUELLEN_MIT_ZUGANGSDATEN.items():
        if host not in text:
            continue
        fehlend = [v for v in variablen if v not in text]
        assert not fehlend, (
            f"live-tests.yml nennt {host} als Ziel, reicht aber {fehlend} nicht "
            "herein. Der Lauf erreicht diese Quelle nicht — ein rotes Ergebnis "
            "wuerde auf einen Vertrag zeigen, der nie geprueft wurde."
        )


def test_die_live_suite_nennt_die_quelle_die_sie_abfragt() -> None:
    """swissvotes.ch ist es, was die `-m live`-Tests tatsaechlich anfassen."""
    text = _workflow_ohne_kommentare()
    assert "swissvotes.ch" in text, (
        "live-tests.yml nennt swissvotes.ch nicht — dann traegt das Issue bei "
        "einem roten Lauf nicht die Quelle, die gebrochen ist."
    )


def test_jedes_werkzeug_ist_eingeordnet() -> None:
    """Live abgedeckt oder ausdruecklich nicht — ein drittes gibt es nicht.

    Ein neues Werkzeug rutscht sonst stillschweigend in die Gruppe ohne
    Live-Abdeckung, und der naechtliche Lauf sieht gruen aus, obwohl er
    weniger prueft als am Tag zuvor.
    """
    werkzeuge = _werkzeuge()
    abgedeckt = _live_abgedeckte_werkzeuge()
    unbekannt = werkzeuge - abgedeckt - set(_BEWUSST_OHNE_LIVE_TEST)
    assert not unbekannt, (
        f"nicht eingeordnet: {sorted(unbekannt)}. Entweder einen `-m live`-Test "
        "dafuer schreiben oder in _BEWUSST_OHNE_LIVE_TEST mit Grund eintragen."
    )
    veraltet = set(_BEWUSST_OHNE_LIVE_TEST) - werkzeuge
    assert not veraltet, (
        f"_BEWUSST_OHNE_LIVE_TEST nennt Werkzeuge, die es nicht gibt: {sorted(veraltet)}"
    )


def test_die_beiden_scans_finden_ueberhaupt_etwas() -> None:
    """Sichert die Pruefungen oben gegen leere Eingaben ab.

    Faende `_werkzeuge()` nichts, waere die Differenz oben leer und die
    Zusicherung trivialerweise wahr — gruen, ohne etwas geprueft zu haben.
    Dasselbe gilt fuer die abgeleitete Live-Abdeckung.
    """
    werkzeuge = _werkzeuge()
    assert len(werkzeuge) >= 10, f"Werkzeug-Scan findet zu wenig: {sorted(werkzeuge)}"
    abgedeckt = _live_abgedeckte_werkzeuge()
    assert abgedeckt, "kein Werkzeug aus einem Live-Test heraus gefunden — der Scan sucht falsch"
    assert abgedeckt <= werkzeuge, f"kein Werkzeug: {sorted(abgedeckt - werkzeuge)}"
