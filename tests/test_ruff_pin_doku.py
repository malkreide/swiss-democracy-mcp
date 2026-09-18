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
import subprocess

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_GATE = _ROOT / "scripts" / "check_ruff_pin.py"

# Dieselbe Form, die das Gate in pyproject.toml sucht, hier ohne die
# Anfuehrungszeichen: In Fliesstext steht `ruff==0.16.5` in Backticks.
#
# Die Version wird positiv gefasst, nicht negativ abgegrenzt. Eine Liste
# verbotener Folgezeichen ist dieselbe handgeschriebene Aufzaehlung wie die
# Verzeichnisliste weiter unten und war ebenso unvollstaendig: Sie schloss
# `)` und `;` aus, aber weder den Satzpunkt noch `]`, und las aus
# `Install ruff==0.16.5.` den Wert `0.16.5.` und aus
# `[ruff==0.16.5](…)` den Wert `0.16.5](…`. Beides haette die Suite rot
# gemacht, obwohl die dokumentierte Version stimmt.
#
# Eine Versionsnummer endet auf einer alphanumerischen Stelle; ein Punkt am
# Ende gehoert zum Satz, nicht zur Nummer. Das Backtracking loest das.
#
# Der Name wird so geschrieben, wie pip ihn akzeptiert, nicht so, wie er hier
# zufaellig steht: Gross-/Kleinschreibung ist bei Paketnamen bedeutungslos
# (PEP 503), und PEP 508 erlaubt Leerraum um `==`. `Ruff==0.16.3` und
# `ruff == 0.16.3` sind gueltige Schreibweisen derselben Anforderung — die
# vorige Fassung fand sie nicht und liess eine Drift still durch. Das war die
# gefaehrlichere Richtung: Ein Falsch-Rot faellt auf, ein Falsch-Gruen nicht.
#
# Der Lookbehind grenzt den Namen ab, sonst liest `xruff==0.16.3` oder
# `my-ruff==0.16.3` als ruff und macht ein fremdes Paket zur Drift.
#
# Gefangen wird der ganze Versions-Ausdruck, nicht nur sein Ziffernanfang.
# `ruff==0.16.5.*`, `ruff==0.16.5+corp1` und `ruff==0.16.5-1` sind gueltige
# Anforderungen, die etwas anderes waehlen als den exakten Pin — ein
# Wildcard-, Local- oder Post-Release. Eine Fassung, die davon nur `0.16.5`
# las, verglich den Praefix mit dem Pin, fand ihn gleich und liess die Doku
# durch, obwohl ihr zu folgen ein anderes ruff installiert.
#
# Der Punkt ist dabei nicht am Zeichen zu erkennen, sondern am folgenden:
# In `Install ruff==0.16.5.` schliesst er den Satz, in `ruff==0.16.5.*`
# gehoert er zur Anforderung. Deshalb endet der Fang auf einer
# alphanumerischen Stelle oder `*` — das Backtracking trennt beide Faelle,
# ohne dass hier eine Liste von Satzzeichen stuende.
_IN_DOKU = re.compile(
    r"(?<![\w-])ruff\s*==\s*([0-9][0-9a-zA-Z.*+!_-]*[0-9a-zA-Z*]|[0-9])",
    re.IGNORECASE,
)

# Schreibweisen, in denen eine Version in Markdown vorkommt, je mit dem Wert,
# den das Muster herauslesen muss. Festgehalten, weil die erste Fassung an
# den beiden ersten Zeilen scheiterte.
_SCHREIBWEISEN = [
    ("Install ruff==0.16.5.", ["0.16.5"]),
    ("siehe [ruff==0.16.5](https://example.org)", ["0.16.5"]),
    ("`ruff==0.16.5`", ["0.16.5"]),
    ('    "ruff==0.16.5",', ["0.16.5"]),
    ("ruff==0.16.5, dann weiter", ["0.16.5"]),
    ("ruff==0.16.5; danach", ["0.16.5"]),
    ("ruff==0.16.3 (veraltet)", ["0.16.3"]),
    ("ruff==0.16.5rc1 als Vorabversion", ["0.16.5rc1"]),
    # Gueltige Schreibweisen derselben Anforderung (PEP 503/508).
    ("Ruff==0.16.3", ["0.16.3"]),
    ("RUFF==0.16.3", ["0.16.3"]),
    ("ruff == 0.16.3", ["0.16.3"]),
    ("Ruff  ==  0.16.3", ["0.16.3"]),
    # Anforderungen, die NICHT den exakten Pin waehlen. Der ganze Ausdruck
    # muss herauskommen, sonst vergleicht der Abgleich nur den Praefix und
    # haelt sie faelschlich fuer den Pin.
    ("ruff==0.16.5.*", ["0.16.5.*"]),
    ("ruff==0.16.5+corp1", ["0.16.5+corp1"]),
    ("ruff==0.16.5-1", ["0.16.5-1"]),
    ("ruff==1!2.0", ["1!2.0"]),
    ("ruff==0.16.5.post1", ["0.16.5.post1"]),
    # Fremde Pakete. Ohne die Abgrenzung faende das Muster hier eine Drift,
    # die es gar nicht gibt.
    ("xruff==0.16.3", []),
    ("my-ruff==0.16.3", []),
    ("ruff-lsp==0.1.0", []),
]


def _pin() -> str:
    """Der gepinnte Wert, gelesen vom Gate selbst — eine Quelle, ein Leser."""
    spec = importlib.util.spec_from_file_location("_check_ruff_pin", _GATE)
    assert spec is not None and spec.loader is not None
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul.pinned_version()


def _markdown() -> list[pathlib.Path]:
    """Die versionierten Markdown-Dateien. Git fuehrt sie, nicht eine Liste hier.

    Ein `rglob` sammelt auch ein, was in `venv/`, `build/` oder
    `.pytest_cache/` liegt: erzeugte Dateien, die niemand pflegt. Ein alter
    Pin im Changelog eines installierten Pakets haette die Suite rot gemacht,
    ohne dass an der Projektdoku etwas falsch war — nachgestellt am 18.9.2026,
    `venv/lib/CHANGELOG.md` mit `ruff==0.16.3` genuegte.

    Eine handgeschriebene Ausschlussliste behebt das nicht, sie kodiert nur
    die Annahme des Autors, welche Verzeichnisse es gibt: Die erste Fassung
    fuehrte `.venv`, aber weder `venv` noch `build` oder `env`. `.gitignore`
    weiss das bereits, und `git ls-files` liest es — eine Quelle statt einer
    Aufzaehlung, die beim naechsten Werkzeug wieder unvollstaendig waere.
    """
    ruf = ["git", "-C", str(_ROOT), "ls-files", "-z", "--", "*.md"]
    try:
        roh = subprocess.run(ruf, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as fehler:
        # Nicht stillschweigend ueberspringen: Ohne die Dateiliste misst der
        # Test nichts, und das muss man ihm ansehen.
        raise AssertionError(f"`git ls-files` nicht auswertbar: {fehler}") from fehler
    return sorted(_ROOT / teil for teil in roh.split("\0") if teil)


def test_gate_liefert_den_pin() -> None:
    """Positivkontrolle: Ohne sie misst der Test unten seine eigene Stille.

    Geprueft wird nicht eine eigene Vorstellung von der Form — `X.Y.Z` waere
    enger als das, was `pinned_version()` zulaesst, und ein Vorabversions-Pin
    wie `0.16.5rc1` faellt dann hier, ohne dass etwas falsch ist. Geprueft
    wird die Bedingung, auf die es ankommt: dass das Doku-Muster genau den
    Wert wiedererkennt, den das Gate liest. Laufen die beiden auseinander,
    geht der Abgleich unten ins Leere oder auf einen abgeschnittenen Wert.
    """
    pin = _pin()
    assert pin, "Kein Pin gelesen."
    assert _IN_DOKU.findall(f"ruff=={pin}") == [pin]


def test_muster_trifft_die_gueltigen_schreibweisen() -> None:
    """Jede gueltige Schreibweise trifft, jedes fremde Paket nicht."""
    for zeile, erwartet in _SCHREIBWEISEN:
        assert _IN_DOKU.findall(zeile) == erwartet, zeile


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
