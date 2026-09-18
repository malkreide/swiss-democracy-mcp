"""Der Pin-Leser muss den Pin auch sehen, wenn er anders geschrieben ist.

`scripts/check_ruff_pin.py` liest den ruff-Pin aus `pyproject.toml`. Sein
Muster verlangte `ruff==` woertlich: klein geschrieben, ohne Leerraum. Nach
PEP 503 ist die Gross-/Kleinschreibung eines Paketnamens bedeutungslos, nach
PEP 508 ist Leerraum um `==` erlaubt — `"Ruff == 0.16.5"` ist derselbe Pin.

Dass die engere Fassung ihn uebersah, war nicht immer laut, und darin liegt
der Grund fuer diese Datei. Steht ein so geschriebener Pin allein, faellt die
Pruefung mit «Kein exakter ruff-Pin». Steht er als ZWEITER Eintrag neben
einem klein geschriebenen, faellt sie gar nicht: Sie sieht nur den einen und
meldet «genau einer» — waehrend ein widersprechender danebensteht, den pip
sehr wohl liest. Am 18.9.2026 nachgestellt: `"ruff==0.16.5"` und
`"Ruff==0.16.3"` nebeneinander ergaben «Ruff-Pin OK (0.16.5)», exit 0.

Der Leser bleibt beim Operator eng: Eine Spanne ist kein Pin, und ein
fremdes Paket, dessen Name auf «ruff» endet, ist keiner.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_GATE = _ROOT / "scripts" / "check_ruff_pin.py"

_RUMPF = """[project]
name = "beispiel"

[project.optional-dependencies]
dev = [
    "pytest",
{eintraege}
]
"""


def _gate_mit(eintraege: list[str], tmp_path: pathlib.Path):
    """Das Gate, frisch geladen, auf einer eigenen pyproject.toml.

    Frisch geladen statt gepatcht: So traegt kein Test die Datei des
    naechsten mit sich, und es wird nichts im Prozess veraendert, was
    ausserhalb dieses Tests noch gilt.
    """
    spec = importlib.util.spec_from_file_location("_pin_leser", _GATE)
    assert spec is not None and spec.loader is not None
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    datei = tmp_path / "pyproject.toml"
    zeilen = "\n".join(f'    "{e}",' for e in eintraege)
    datei.write_text(_RUMPF.format(eintraege=zeilen), encoding="utf-8")
    modul.PYPROJECT = datei
    return modul


@pytest.mark.parametrize(
    "eintrag",
    [
        "ruff==0.16.5",
        "Ruff==0.16.5",
        "RUFF==0.16.5",
        "ruff == 0.16.5",
        "Ruff  ==  0.16.5",
    ],
)
def test_gueltige_schreibweisen_liefern_den_pin(eintrag, tmp_path):
    """Jede Schreibweise, die pip als denselben Pin liest, wird gelesen."""
    gate = _gate_mit([eintrag], tmp_path)
    assert gate.pinned_version() == "0.16.5"


def test_zwei_schreibweisen_desselben_pins_sind_einer(tmp_path):
    """Gleicher Wert, andere Schreibweise: kein Widerspruch, kein Fehler."""
    gate = _gate_mit(["ruff==0.16.5", "Ruff == 0.16.5"], tmp_path)
    assert gate.pinned_version() == "0.16.5"


def test_widersprechender_zweiter_pin_faellt_auf(tmp_path):
    """Der Kernfall: Die engere Fassung meldete hier «OK» und exit 0."""
    gate = _gate_mit(["ruff==0.16.5", "Ruff==0.16.3"], tmp_path)
    with pytest.raises(SystemExit) as fehler:
        gate.pinned_version()
    meldung = str(fehler.value)
    assert "Mehrere ruff-Pins" in meldung
    assert "0.16.3" in meldung
    assert "0.16.5" in meldung


@pytest.mark.parametrize(
    "eintrag",
    [
        "ruff>=0.16.5",
        "ruff",
        "xruff==0.16.5",
        "my-ruff==0.16.5",
        "ruff-lsp==0.1.0",
    ],
)
def test_was_kein_exakter_ruff_pin_ist(eintrag, tmp_path):
    """Eine Spanne ist kein Pin, und ein fremdes Paket ist kein ruff."""
    gate = _gate_mit([eintrag], tmp_path)
    with pytest.raises(SystemExit) as fehler:
        gate.pinned_version()
    assert "Kein exakter ruff-Pin" in str(fehler.value)
