"""Was der Verzeichniseintrag ueber diesen Server behauptet.

`server.json` ist die einzige Datei des Repos, die niemand beim Arbeiten
liest: Sie wirkt erst im MCP-Verzeichnis, und der Eintrag dort ist das, was
ein Mensch vor der Installation sieht. Entsprechend lange stand darin
«Parliament OData, Swissvotes, referendums, voting results» — eine
Schnittstelle (`ws.parlament.ch`), die dieser Server nicht anbindet, waehrend
zwei der drei tatsaechlichen Quellen fehlten.

Gemessen, bevor diese Datei entstand: Mit genau dieser Zeile liefen alle vier
CI-Gates gruen, 114 Tests eingeschlossen. `check_version_sync.py` vergleicht
Versionsfelder und ruehrt die Beschreibung nicht an, und kein Test las
`server.json`. Der Fall fiel also nirgends — deshalb steht hier etwas.

Was die Pruefungen NICHT leisten: Sie lesen keinen Text. Eine sachlich
schiefe, aber marker-treue Beschreibung kommt durch. Sie fangen zwei
mechanische Klassen — eine fehlende Quelle und eine namentlich bekannte
fremde — und behaupten darueber hinaus nichts.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from swiss_democracy_mcp.server import SOURCES

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_SERVER_JSON = _ROOT / "server.json"

# Die harte Grenze aus dem Registry-Schema, das `server.json` selbst per
# `$schema` benennt (ServerDetail.description: minLength 1, maxLength 100).
# Sie steht hier als Zahl, weil der Test sonst im CI-Lauf ans Netz muesste;
# die Herkunft ist der `$schema`-Wert der Datei.
_MAX_LAENGE = 100

# Je Quelle aus `SOURCES` die Schreibweisen, von denen mindestens eine in der
# Beschreibung vorkommen muss. Die SCHLUESSEL sind nicht aufgeschrieben,
# sondern werden unten gegen `SOURCES` gehalten: Wer eine vierte Quelle
# anbindet, traegt sie dort ein (sonst wirft `_emit` einen KeyError) und faellt
# damit hier auf, solange er sie im Verzeichniseintrag verschweigt.
_MARKER: dict[str, tuple[str, ...]] = {
    "swissvotes": ("Swissvotes",),
    "bfs": ("BFS", "opendata.swiss"),
    "polis": ("Polis", "SRGSSR", "SRG SSR"),
}

# Quellen, die dieser Server NICHT anbindet und mit denen er schon verwechselt
# wurde — je mit dem Grund. Der Positiv-Teil oben faengt das nicht: In 100
# Zeichen haben alle drei echten Marker und eine erfundene vierte Quelle
# nebeneinander Platz, genau wie in der Zeile, die jahrelang dort stand.
_NICHT_ANGEBUNDEN: dict[str, str] = {
    "Parliament OData": "ws.parlament.ch — kein Client, keine Basis-URL, kein Werkzeug; "
    "die NR/SR-Empfehlungen sind ein Feld INNERHALB des Swissvotes-Datensatzes",
    "parlament.ch": "dieselbe Verwechslung, als Host geschrieben",
}


def _beschreibung() -> str:
    return json.loads(_SERVER_JSON.read_text(encoding="utf-8"))["description"]


def test_die_beschreibung_haelt_die_schema_grenze() -> None:
    """Zu lang faellt sonst erst beim Release — und dort zu spaet.

    `publish.yml` haengt `publish-mcp` per `needs: publish` hinter den
    PyPI-Job. Ein Manifest, das die Registry zurueckweist, bricht also ab,
    nachdem das Paket bereits veroeffentlicht ist: Die Version steht auf PyPI,
    der Verzeichniseintrag fehlt, und zuruecknehmen laesst sich das erste
    nicht. Die Grenze hier kostet einen String-Vergleich.
    """
    beschreibung = _beschreibung()
    assert beschreibung, "leere Beschreibung — das Schema verlangt minLength 1"
    assert len(beschreibung) <= _MAX_LAENGE, (
        f"{len(beschreibung)} Zeichen, erlaubt sind {_MAX_LAENGE}. Die Beschreibung "
        "aus pyproject.toml ist 104 Zeichen lang und passt deshalb NICHT "
        "unveraendert hierher — die beiden Felder koennen sich nicht gleichen."
    )


@pytest.mark.parametrize("schluessel", sorted(SOURCES))
def test_jede_angebundene_quelle_steht_im_verzeichniseintrag(schluessel: str) -> None:
    """Was der Server bedient, muss der Eintrag auch nennen.

    Ueber die Quellen parametrisiert statt in einer Schleife: Faellt es, soll
    der Testname sagen, WELCHE Quelle fehlt.
    """
    marker = _MARKER.get(schluessel)
    assert marker is not None, (
        f"Quelle {schluessel!r} ist in SOURCES angebunden, aber in _MARKER nicht "
        "eingeordnet. Dort die Schreibweisen eintragen, unter denen sie in der "
        "Beschreibung erscheinen darf."
    )
    beschreibung = _beschreibung()
    assert any(m in beschreibung for m in marker), (
        f"server.json nennt {schluessel!r} nicht (erwartet eine von {list(marker)}), "
        f"obwohl SOURCES sie als {SOURCES[schluessel]['name']!r} fuehrt. "
        "Der Verzeichniseintrag verschweigt damit eine bediente Quelle."
    )


@pytest.mark.parametrize("fremd", sorted(_NICHT_ANGEBUNDEN))
def test_der_eintrag_nennt_keine_quelle_die_es_nicht_gibt(fremd: str) -> None:
    """Der Rueckfall in genau den Fehler, der diese Datei ausgeloest hat."""
    assert fremd.lower() not in _beschreibung().lower(), (
        f"server.json nennt {fremd!r}: {_NICHT_ANGEBUNDEN[fremd]}"
    )


def test_die_ableitung_findet_ueberhaupt_etwas() -> None:
    """Sichert die Parametrisierungen oben gegen leere Eingaben ab.

    Waere `SOURCES` leer, erzeugte der Quellen-Test null Faelle und die Suite
    bliebe gruen, ohne den Eintrag angesehen zu haben — gruen aus Mangel an
    Pruefung. Dieselbe Rolle wie `test_die_beiden_scans_finden_ueberhaupt_etwas`
    in `test_live_abdeckung.py`.
    """
    assert SOURCES, "SOURCES ist leer — der Quellen-Test prueft dann nichts"
    assert _NICHT_ANGEBUNDEN, "_NICHT_ANGEBUNDEN ist leer — der Negativ-Test prueft dann nichts"
    veraltet = set(_MARKER) - set(SOURCES)
    assert not veraltet, f"_MARKER nennt Quellen, die SOURCES nicht mehr fuehrt: {sorted(veraltet)}"
