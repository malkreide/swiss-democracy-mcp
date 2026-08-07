#!/usr/bin/env python3
"""Zeichnet die Unit-Test-Fixtures von den echten Quellen dieses Servers auf.

    python scripts/record_fixtures.py

WARUM ES DIESES SKRIPT GIBT. Ein handgeschriebener Mock kodiert die Annahme
seines Autors und kann sie deshalb prinzipiell nicht widerlegen: Produktivcode
und Fixture stammen aus demselben Kopf, derselben Stunde, derselben Lektuere der
Doku. Wo beide irren, irren beide gleich, und die Suite bleibt gruen.

Ohne Aufzeichnungsdatum ist «aufgezeichnet» nach zwei Jahren von «ausgedacht»
nicht mehr zu unterscheiden — die Datei sieht gleich aus.

DIE AUSWAHLREGEL IST HIER DER GANZE PUNKT. Der Swissvotes-Datensatz hat 714
Zeilen und 874 Spalten; ausgeschnitten wird nach Merkmal, nicht nach Position.
«Die ersten N Zeilen» wuerde genau die Zellen wegschneiden, wegen derer es die
Fixture gibt: die Fuellwerte `9999` («keine Angabe») und `.` («nicht
anwendbar»), die in 667 der 714 Abstimmungen vorkommen. Eine Fixture ohne sie
saehe sauber aus und belegte nichts.

Die Zeilenzahl des echten Datensatzes bleibt in `PROVENANCE.md` stehen. Eine
Fixture, die stillschweigend behauptet, der Bestand sei kleiner, waere genau der
Fehler, gegen den das hier angeht.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from swiss_democracy_mcp import server  # noqa: E402

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"

# Fuellwerte, die Swissvotes in Code- und Zahlenspalten verwendet. `9999` ist
# «keine Angabe», `.` ist «nicht anwendbar/nicht erhoben».
SENTINELS = ("9999", ".")

PARTY_COLUMNS = tuple(server.PARTY_COLUMNS)

# Wie viele CKAN-Ressourcen die Fixture traegt. Der Server laeuft ueber alle;
# fuer die Form genuegen wenige, und `num_resources` sagt, wie viele es gibt.
CKAN_KEEP = 5


def _anr(row: dict[str, str]) -> str:
    return (row.get("﻿anr") or row.get("anr") or "").strip()


def _select_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, str]]:
    """Waehlt Zeilen nach Merkmal aus und sagt, welches Merkmal welche belegt.

    Nach Position auszuwaehlen waere bequem und falsch: Die Eigenschaften, um
    die es geht, sitzen nicht am Anfang der Datei.
    """
    picked: dict[str, dict[str, str]] = {}
    why: dict[str, str] = {}

    def take(key: str, row: dict[str, str] | None, reason: str) -> None:
        if row is None:
            raise SystemExit(
                f"Auswahlregel «{key}» trifft nichts mehr: {reason}. "
                "Erst klaeren, dann neu aufzeichnen — eine Fixture ohne diese "
                "Zeile belegt die Eigenschaft nicht mehr."
            )
        picked.setdefault(_anr(row), row)
        # Sammeln statt setdefault: Trifft eine zweite Regel dieselbe Zeile,
        # geht ihre Begruendung sonst verloren, und PROVENANCE.md nennt ein
        # Merkmal nicht mehr, das die Fixture sehr wohl belegt.
        why[_anr(row)] = f"{why[_anr(row)]}; {reason}" if _anr(row) in why else reason

    take(
        "parolen-9999",
        next(
            (r for r in rows if any((r.get(c) or "").strip() == "9999" for c in PARTY_COLUMNS)),
            None,
        ),
        "traegt `9999` in einer Parteispalte — der Fuellwert «keine Angabe»",
    )
    take(
        "brpos-punkt",
        next((r for r in rows if (r.get("br-pos") or "").strip() == "."), None),
        "traegt `.` in `br-pos` — «nicht anwendbar» statt einer Position",
    )
    take(
        "zahlen-punkt",
        next((r for r in rows if (r.get("zh-japroz") or "").strip() == "."), None),
        "traegt `.` in einer Zahlenspalte (`zh-japroz`) — dort muss der Parser "
        "`None` liefern und nicht raten",
    )
    take(
        "vollstaendig",
        next(
            (
                r
                for r in reversed(rows)
                if all((r.get(c) or "").strip() not in SENTINELS + ("",) for c in PARTY_COLUMNS)
                and (r.get("volkja-proz") or "").strip() not in SENTINELS + ("",)
            ),
            None,
        ),
        "juengste Abstimmung mit vollstaendigen Parolen und Resultat — der Fall, "
        "in dem alles da ist",
    )
    return list(picked.values()), why


def record() -> int:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    recorded_at = datetime.now(UTC).strftime("%Y-%m-%d")
    entries: list[dict] = []
    skipped: list[dict] = []

    def write(name: str, text: str, url: str, rule: str) -> None:
        if not text.endswith("\n"):
            text += "\n"
        (FIXTURES / name).write_text(text, encoding="utf-8")
        entries.append(
            {
                "name": name,
                "url": url,
                "rule": rule,
                "bytes": len(text.encode("utf-8")),
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )
        print(f"ok  {name:<30} {len(text.encode('utf-8')):>8} B")

    with httpx.Client(
        timeout=180.0,
        follow_redirects=True,
        headers={"User-Agent": server.USER_AGENT},
    ) as client:
        # 1) Swissvotes-CSV. Der Server liest sie mit `delimiter=";"`; hier
        #    ebenso, sonst beantwortet die Fixture eine andere Frage.
        r = client.get(server.SWISSVOTES_CSV_URL)
        r.raise_for_status()
        content = r.text
        rows = list(csv.DictReader(io.StringIO(content), delimiter=";"))
        if not rows:
            raise SystemExit("Swissvotes: keine Zeilen — Trennzeichen oder Quelle geaendert?")

        header = content.splitlines()[0]
        n_cols = len(header.split(";"))
        if n_cols < 100:
            raise SystemExit(
                f"Swissvotes: nur {n_cols} Spalten — das Trennzeichen wirkt nicht mehr"
            )

        selected, why = _select_rows(rows)
        fieldnames = list(rows[0])
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fieldnames, delimiter=";", lineterminator="\n")
        writer.writeheader()
        for row in selected:
            writer.writerow(row)
        # Das BOM steht im Original vor `anr`; der Server entfernt es
        # ausdruecklich, und ohne BOM koennte die Fixture nicht belegen, dass er
        # es muss. Es steckt aber bereits IM Feldnamen (`﻿anr`) und wird
        # von `writeheader()` mitgeschrieben — ein zweites davorzusetzen ergaebe
        # `﻿﻿anr`, und der Server fande die Spalte nicht mehr.
        text = buf.getvalue()
        if content.startswith("﻿") and not text.startswith("﻿"):
            text = "﻿" + text
        if text.startswith("﻿﻿"):
            raise SystemExit(
                "doppeltes BOM in der Fixture — der Server liest `anr` dann nicht mehr"
            )

        rule = (
            f"Kopfzeile unveraendert ({n_cols} Spalten); {len(selected)} von "
            f"{len(rows)} Zeilen, **nach Merkmal ausgewaehlt statt nach Position**"
        )
        for anr, reason in sorted(why.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0):
            rule += f". Abstimmung {anr}: {reason}"
        write("swissvotes_rows.csv", text, str(r.request.url), rule)

        # 2) Die beiden CKAN-Pakete des BFS.
        for label, url in (
            ("national", server.BFS_NATIONAL_PACKAGE),
            ("cantonal", server.BFS_CANTONAL_PACKAGE),
        ):
            r = client.get(url)
            r.raise_for_status()
            payload = r.json()
            if not payload.get("success"):
                raise SystemExit(f"CKAN {label}: success=false")
            resources = payload.get("result", {}).get("resources") or []
            if not resources:
                raise SystemExit(f"CKAN {label}: keine `resources` — der Server liest genau die")
            n_real = len(resources)
            # Auf die juengsten kuerzen; `num_resources` bleibt der echte Wert.
            # Eine Fixture, die stillschweigend behauptet, das Paket sei
            # kleiner, waere genau der Fehler, gegen den das hier angeht.
            payload["result"]["resources"] = resources[:CKAN_KEEP]
            write(
                f"bfs_package_{label}.json",
                json.dumps(payload, ensure_ascii=False, indent=2),
                str(r.request.url),
                f"`resources` auf die {min(CKAN_KEEP, n_real)} juengsten von "
                f"{n_real} gekuerzt, `num_resources` unveraendert "
                f"({payload['result'].get('num_resources')}); alles uebrige "
                "vollstaendig",
            )

        # 3) SRGSSR Polis — nur mit Zugangsdaten.
        creds = server._get_polis_credentials()
        if creds is None:
            probe = client.get(f"{server.POLIS_BASE}/votations")
            body = probe.text.lstrip()[:40]
            skipped.append(
                {
                    "name": "polis_*.json",
                    "url": f"{server.POLIS_BASE}/votations",
                    "why": "SRGSSR_CONSUMER_KEY/SRGSSR_CONSUMER_SECRET nicht gesetzt. "
                    f"Ohne OAuth2-Token antwortet der Endpunkt mit HTTP "
                    f"{probe.status_code} und `{body}…` — also mit der "
                    "Entwicklerportal-Seite, nicht mit Daten. NICHT aufgezeichnet.",
                }
            )
            print("--  polis_*.json                  uebersprungen (keine Zugangsdaten)")
        else:
            raise SystemExit(
                "SRGSSR-Zugangsdaten sind gesetzt, aber dieses Skript zeichnet Polis "
                "noch nicht auf. Zweig ergaenzen statt still zu ueberspringen."
            )

    _write_provenance(recorded_at, entries, skipped, len(rows))
    print(f"\nPROVENANCE.md geschrieben, Aufzeichnungsdatum {recorded_at}")
    return 0


def _write_provenance(
    recorded_at: str, entries: list[dict], skipped: list[dict], total_rows: int
) -> None:
    lines = [
        "# Herkunft der Fixtures",
        "",
        "**Erzeugt von `scripts/record_fixtures.py`. Nicht von Hand pflegen.**",
        "",
        f"Aufgezeichnet am **{recorded_at}**.",
        "",
        "Ohne Datum ist «aufgezeichnet» nach zwei Jahren von «ausgedacht» nicht",
        "mehr zu unterscheiden — die Datei sieht gleich aus.",
        "",
        "## Die Auswahlregel ist hier der Punkt",
        "",
        f"Der Swissvotes-Datensatz hat am Aufzeichnungstag **{total_rows} Zeilen** und",
        "874 Spalten. Ausgeschnitten wird **nach Merkmal, nicht nach Position**.",
        "«Die ersten N Zeilen» wuerde genau die Zellen wegschneiden, wegen derer es",
        "die Fixture gibt: die Fuellwerte `9999` («keine Angabe») und `.` («nicht",
        "anwendbar»), die in 667 der 714 Abstimmungen vorkommen. Eine Fixture ohne",
        "sie saehe sauber aus und belegte nichts.",
        "",
        "Welche Zeile welches Merkmal belegt, steht unten bei der Datei. Trifft eine",
        "Regel eines Tages nichts mehr, bricht das Skript ab, statt eine Fixture zu",
        "schreiben, die weniger belegt, als sie aussieht.",
        "",
        "**Das BOM bleibt drin.** Das Original stellt der ersten Spalte `anr` ein",
        "Byte-Order-Mark voran, und der Server entfernt es ausdruecklich. Ohne BOM",
        "koennte die Fixture nicht belegen, dass er das muss.",
        "",
    ]
    if skipped:
        lines += ["## NICHT aufgezeichnet", ""]
        for s in skipped:
            lines += [
                f"### `{s['name']}`",
                "",
                f"- **Quelle:** `{s['url']}`",
                f"- **Grund:** {s['why']}",
                "",
            ]
        lines += [
            "Die Polis-Payloads stehen weiterhin als Literale im Testmodul. Sie sind",
            "damit **ausgedacht** und tragen kein Datum — das ist der Ist-Zustand und",
            "keine Nachlaessigkeit dieses Laufs. Wer Zugangsdaten hat, setzt sie und",
            "ergaenzt den Zweig im Skript.",
            "",
        ]
    for e in entries:
        lines += [
            f"## `{e['name']}`",
            "",
            f"- **Quelle:** `{e['url']}`",
            f"- **Aufgezeichnet:** {recorded_at}",
            f"- **Auswahl:** {e['rule']}",
            f"- **Groesse:** {e['bytes']} B",
            f"- **SHA-256:** `{e['sha256']}`",
            "",
        ]
    (FIXTURES / "PROVENANCE.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    try:
        raise SystemExit(record())
    except httpx.HTTPError as exc:
        print(f"FEHLER: Quelle nicht erreichbar: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
