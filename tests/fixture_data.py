"""Zugriff auf die aufgezeichneten Fixtures.

Ein fehlender Name ist hier ein Fehler und keine leere Struktur. Ein Loader,
der bei einem Tippfehler `[]` zurueckgibt, erzeugt einen Test, der nichts mehr
prueft und trotzdem Erfolg meldet — die teuerste Sorte gruen.

Herkunft, Datum und Auswahlregel stehen in `fixtures/PROVENANCE.md`.
"""

from __future__ import annotations

import csv
import io
import json
from functools import cache
from pathlib import Path
from typing import Any

FIXTURES = Path(__file__).parent / "fixtures"


@cache
def raw(name: str) -> str:
    """Der aufgezeichnete Text, unveraendert — samt BOM, wo die Quelle eins setzt."""
    path = FIXTURES / name
    if not path.exists():
        available = sorted(p.name for p in FIXTURES.iterdir() if p.suffix in (".csv", ".json"))
        raise FileNotFoundError(
            f"Fixture {name!r} gibt es nicht. Vorhanden: {available}. "
            "Neu aufzeichnen mit `python scripts/record_fixtures.py`."
        )
    return path.read_text(encoding="utf-8")


def payload(name: str) -> Any:
    """Eine aufgezeichnete JSON-Antwort."""
    return json.loads(raw(name))


def swissvotes_rows() -> list[dict[str, str]]:
    """Die aufgezeichneten Swissvotes-Zeilen, gelesen wie der Server sie liest.

    Bewusst mit `encoding="utf-8"` statt `utf-8-sig`: Das BOM steht in der
    Datei, weil die Quelle es setzt, und der Server entfernt es selbst. Wer es
    hier wegnaehme, pruefte diesen Schritt nicht mehr.
    """
    return list(csv.DictReader(io.StringIO(raw("swissvotes_rows.csv")), delimiter=";"))
