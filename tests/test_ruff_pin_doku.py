"""Eine Versionsangabe in der Doku, die den Pin wiederholt, driftet.

Am 18.9.2026 nannte `CLAUDE.md` `ruff==0.16.3`, waehrend das `dev`-Extra in
`pyproject.toml` `0.16.5` pinnte. Der Absatz war mit «eine Quelle»
ueberschrieben und wiederholte den Wert daneben selbst; der Satz zwei
Abschnitte darueber verlangt, die Gates mit der gepinnten Version zu fahren.
Wer der Doku folgte, installierte `0.16.3` und erzeugte genau die
Abweichungen, vor denen sie warnt.

Gemessen wurde, dass kein bestehendes Gate das sieht: Mit wieder
eingefuegter Kopie meldete `scripts/check_ruff_pin.py` «Ruff-Pin OK» — es
vergleicht das *installierte* ruff gegen `pyproject.toml` und liest keine
Doku — und `scripts/check_version_sync.py` prueft die Paketversion, nicht
diese. Beide blieben gruen. Der Fall war ungedeckt, nicht bloss theoretisch.

Der Test verbietet die Angabe nicht, er gleicht sie ab: Wer sie mit Absicht
hinschreibt, darf das, solange sie stimmt. Und er liest den Pin nicht mit
einem zweiten Regex, sondern durch `pinned_version()` aus dem Gate — sonst
stuenden fuer dieselbe Frage wieder zwei Quellen da.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_GATE = _ROOT / "scripts" / "check_ruff_pin.py"

# Dieselbe Form, die das Gate in pyproject.toml sucht, hier ohne die
# Anfuehrungszeichen: In Fliesstext steht `ruff==0.16.5` in Backticks.
_IN_DOKU = re.compile(r"ruff==([0-9][^\s`'\"),;]*)")


def _pin() -> str:
    """Der gepinnte Wert, gelesen vom Gate selbst — eine Quelle, ein Leser."""
    spec = importlib.util.spec_from_file_location("_check_ruff_pin", _GATE)
    assert spec is not None and spec.loader is not None
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul.pinned_version()


def _markdown() -> list[pathlib.Path]:
    """Jede Doku-Datei des Repos, ohne die Verzeichnisse von Werkzeugen."""
    aus = {".git", ".venv", "node_modules", ".mypy_cache", ".ruff_cache"}
    return sorted(p for p in _ROOT.rglob("*.md") if not any(teil in aus for teil in p.parts))


def test_gate_liefert_den_pin() -> None:
    """Positivkontrolle: Ohne sie misst der Test unten seine eigene Stille."""
    pin = _pin()
    assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", pin), pin


def test_markdown_wird_wirklich_gelesen() -> None:
    """Zweite Positivkontrolle: Ein leeres Dateiglob wuerde nie etwas finden."""
    dateien = _markdown()
    assert dateien, "Keine Markdown-Datei gefunden — der Test misst nichts."
    assert _ROOT / "CLAUDE.md" in dateien


def test_keine_abweichende_ruff_version_in_der_doku() -> None:
    """Nennt ein Text eine ruff-Version, ist es die gepinnte — oder keine."""
    pin = _pin()
    abweichend = []
    for pfad in _markdown():
        text = pfad.read_text(encoding="utf-8")
        for nummer, zeile in enumerate(text.splitlines(), start=1):
            for gefunden in _IN_DOKU.findall(zeile):
                if gefunden != pin:
                    stelle = pfad.relative_to(_ROOT)
                    abweichend.append(f"{stelle}:{nummer} nennt {gefunden}")
    if abweichend:
        orte = "\n  ".join(abweichend)
        grund = f"Gepinnt ist {pin} (pyproject.toml, dev-Extra). Abweichend:"
        rat = "Die Version im Fliesstext streichen und auf pyproject.toml"
        rat2 = "verweisen — sie driftet dort, wo niemand sie nachfuehrt."
        raise AssertionError(f"{grund}\n  {orte}\n{rat} {rat2}")
