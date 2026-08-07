"""Die Swissvotes-Verarbeitung gegen aufgezeichnete echte Zeilen halten.

WARUM ES DIESE DATEI GIBT. Die uebrigen Testmodule pruefen gegen
handgeschriebene CSV-Zeilen. Die stammen aus derselben Lektuere des Codebuchs
wie der Produktivcode; wo beide irren, irren beide gleich, und die Suite bleibt
gruen. Genau so ist der Fuellwert-Fehler unbemerkt geblieben: Wer eine Zeile von
Hand schreibt, schreibt `p-fdp;1` — niemand erfindet `9999`.

Die Zeilen hier sind aufgezeichnet, datiert und **nach Merkmal ausgewaehlt**:
Quelle, Datum und Auswahlregel je Datei stehen in `fixtures/PROVENANCE.md`.

WAS SIE NICHT KOENNEN: Sie sind ein datierter Ausschnitt aus 714 Zeilen, kein
Abonnement. Aendert Swissvotes morgen seine Codes, faellt das hier nicht auf.
"""

from __future__ import annotations

import json

import pytest
from fixture_data import payload, swissvotes_rows

from swiss_democracy_mcp import server

# Die Fuellwerte, um die es geht. Aus dem Produktivcode gelesen statt hier
# ausgeschrieben — sonst pruefte der Test seine eigene Annahme.
SENTINELS = tuple(k for k in server.SWISSVOTES_MISSING if k)


def _anr(row: dict[str, str]) -> str:
    return (row.get("﻿anr") or row.get("anr") or "").strip()


# ---------------------------------------------------------------------------
# Die Fixture selbst
# ---------------------------------------------------------------------------


def test_the_fixture_still_carries_what_it_is_for():
    """Ohne Fuellwerte in der Datei prueft alles darunter nichts.

    Die Auswahlregel im Aufzeichnungsskript sucht die Zeilen nach genau diesem
    Merkmal. Faellt dieser Test, ist die Fixture beim letzten Lauf still
    harmlos geworden.
    """
    rows = swissvotes_rows()
    assert rows, "keine Zeilen gelesen — Trennzeichen oder Fixture kaputt"
    cells = [
        (col, value)
        for row in rows
        for col, value in row.items()
        if (value or "").strip() in SENTINELS
    ]
    assert cells, f"keine Zelle mit {SENTINELS} in der Fixture"
    party_cells = [c for c, _ in cells if c in server.PARTY_COLUMNS]
    assert party_cells, "kein Fuellwert in einer Parteispalte"
    assert any(c == "br-pos" for c, _ in cells), "kein Fuellwert in `br-pos`"


def test_the_bom_is_still_there_because_the_source_sets_it():
    """Der Server entfernt das BOM ausdruecklich — die Fixture muss eines haben.

    Eine BOM-freie Fixture liesse den Schritt ungeprueft und wuerde beim
    naechsten Quellenwechsel niemandem auffallen.
    """
    rows = swissvotes_rows()
    first_key = next(iter(rows[0]))
    assert first_key.startswith("﻿"), (
        f"erste Spalte heisst {first_key!r} ohne BOM — dann prueft der "
        "BOM-Abschnitt in `_load_swissvotes` nichts mehr"
    )


def test_the_csv_is_semicolon_delimited():
    """Mit Komma gelesen ergaebe die Datei genau eine Spalte."""
    rows = swissvotes_rows()
    assert len(rows[0]) > 100, f"{len(rows[0])} Spalten — das Trennzeichen `;` wirkt nicht"


# ---------------------------------------------------------------------------
# Der Befund
# ---------------------------------------------------------------------------


def test_a_missing_party_position_is_named_not_passed_through():
    """`9999` ist keine Parole, sondern deren Abwesenheit.

    Vorher stand `PAROLE_MAP.get(code, code)` im Werkzeug, und fuer 667 der 714
    Abstimmungen landete mindestens ein `9999` oder `.` als scheinbarer Wert in
    der Antwort. `{"FDP": "9999"}` liest sich wie ein Code oder eine Zahl; ein
    Modell, das darueber schreibt, kann nicht erkennen, dass dort nichts steht.
    """
    for sentinel in SENTINELS:
        decoded = server._decode(sentinel, {"1": "Ja"})
        assert decoded == server.SWISSVOTES_MISSING[sentinel]
        assert sentinel not in decoded, (
            f"{sentinel!r} steht noch im Ergebnis {decoded!r} — der Fuellwert "
            "ist damit weiterhin sichtbar"
        )


def test_an_unknown_code_is_labelled_as_unknown():
    """Ein Code, den niemand kennt, darf nicht wie ein Wert aussehen."""
    decoded = server._decode("77", {"1": "Ja"})
    assert "Unbekannt" in decoded and "77" in decoded, decoded


async def test_party_positions_contain_no_raw_sentinel():
    """Die Antwort des Werkzeugs traegt keinen Fuellwert mehr.

    Geprueft wird am Werkzeug, nicht an `_decode`: Dass die Hilfsfunktion
    stimmt, sagt nichts darueber, ob das Werkzeug sie benutzt.
    """
    rows = swissvotes_rows()
    row = next(
        (
            r
            for r in rows
            if any((r.get(c) or "").strip() in SENTINELS for c in server.PARTY_COLUMNS)
        ),
        None,
    )
    assert row is not None, "keine Zeile mit Fuellwert in einer Parteispalte"

    async def fake_load(_ctx=None):
        return rows

    original, server._load_swissvotes = server._load_swissvotes, fake_load
    try:
        out = json.loads(
            await server.democracy_get_party_positions(
                server.VoteDetailInput(vote_number=_anr(row))
            )
        )
    finally:
        server._load_swissvotes = original

    positions = out["party_positions"]
    assert positions, "keine Parteiparolen in der Antwort"
    for party, value in positions.items():
        assert value not in SENTINELS, (
            f"{party} meldet den rohen Fuellwert {value!r} — ein Ausfall, der "
            "wie eine Angabe aussieht"
        )
    assert any(v == "Keine Angabe" for v in positions.values()), (
        f"keine Parole als «Keine Angabe» ausgewiesen: {positions}"
    )


async def test_the_federal_council_position_is_named_too():
    """`br-pos` traegt in 129 der 714 Abstimmungen ein `.`.

    Dieselbe Stelle, dasselbe Muster, ein zweites Werkzeug: Die Suchantwort
    meldete den Punkt roh als Position des Bundesrats.
    """
    rows = swissvotes_rows()
    row = next((r for r in rows if (r.get("br-pos") or "").strip() in SENTINELS), None)
    assert row is not None, "keine Zeile mit Fuellwert in `br-pos`"

    summary = server._row_to_vote_summary(row)
    assert summary["federal_council_position"] not in SENTINELS, (
        f"Position des Bundesrats ist {summary['federal_council_position']!r}"
    )
    assert summary["federal_council_position"] in server.SWISSVOTES_MISSING.values()


# ---------------------------------------------------------------------------
# Zahlen
# ---------------------------------------------------------------------------


def test_a_suppressed_number_becomes_none_not_a_number():
    """Eine unterdrueckte Zahl darf keine Zahl werden.

    Swissvotes markiert fehlende Zahlen mit `.`; `float(".")` wirft, also
    liefert der Parser `None`. Das ist richtig und wird hier festgehalten,
    damit es richtig bleibt: Eine Null an dieser Stelle waere eine Summe, aus
    der stillschweigend etwas fehlt.
    """
    assert server._parse_float(".") is None
    assert server._parse_int(".") is None
    assert server._parse_float("") is None

    rows = swissvotes_rows()
    row = next((r for r in rows if (r.get("zh-japroz") or "").strip() == "."), None)
    assert row is not None, "keine Zeile mit unterdrueckter Zahl in `zh-japroz`"
    assert server._parse_float(row["zh-japroz"]) is None


def test_a_real_number_still_parses():
    """Die Gegenprobe: Der Parser darf nicht einfach immer `None` liefern."""
    rows = swissvotes_rows()
    row = next(
        (r for r in rows if (r.get("volkja-proz") or "").strip() not in SENTINELS + ("",)), None
    )
    assert row is not None, "keine Zeile mit echtem Ja-Anteil — Fixture pruefen"
    value = server._parse_float(row["volkja-proz"])
    assert value is not None and 0.0 <= value <= 100.0, value


def test_a_complete_row_survives_the_summary():
    """Eine vollstaendige Zeile ergibt eine vollstaendige Zusammenfassung."""
    rows = swissvotes_rows()
    row = next(
        (
            r
            for r in rows
            if all((r.get(c) or "").strip() not in SENTINELS + ("",) for c in server.PARTY_COLUMNS)
        ),
        None,
    )
    assert row is not None, "keine vollstaendige Zeile in der Fixture"
    summary = server._row_to_vote_summary(row)
    assert summary["vote_number"] and summary["date"] and summary["title_de"]
    assert summary["yes_percent"] is not None
    assert summary["legal_form"] not in SENTINELS


# ---------------------------------------------------------------------------
# Die CKAN-Pakete
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label", ["national", "cantonal"])
def test_bfs_package_carries_resources_and_the_real_count(label):
    """`resources` ist gekuerzt, `num_resources` ist es nicht.

    Die Zahl sagt, wie viel **nicht** in der Datei steht. Waere sie
    mitgekuerzt, behauptete die Fixture stillschweigend, das Paket sei
    kleiner, als es ist.
    """
    data = payload(f"bfs_package_{label}.json")
    resources = server._ckan_resources(data, "test")
    assert resources, "keine `resources`"
    num = data["result"].get("num_resources")
    assert num and num > len(resources), (
        f"num_resources={num} bei {len(resources)} Ressourcen — die Fixture "
        "belegt den Unterschied nicht mehr"
    )
    for res in resources:
        assert res.get("download_url") or res.get("url"), f"Ressource ohne URL: {res.get('name')}"


def test_ckan_shape_change_is_loud():
    """Eine Antwort ohne `result` ist keine Leermenge.

    Gegenprobe zu FID-006: Der Aufruf muss werfen und dabei sagen, was
    stattdessen da war.
    """
    with pytest.raises(server.UpstreamSchemaError) as excinfo:
        server._ckan_resources({"success": True, "help": "…"}, "package_show")
    assert "result" in str(excinfo.value)
