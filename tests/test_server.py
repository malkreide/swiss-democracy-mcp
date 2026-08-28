"""
Tests für swiss-democracy-mcp
Einheitstests (mit respx-Mocking) und Live-Tests (markiert mit @pytest.mark.live).
Ausführung: PYTHONPATH=src pytest tests/ -m "not live" -v
"""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest
import respx
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import SecretStr

from swiss_democracy_mcp.server import (
    BFS_NATIONAL_PACKAGE,
    POLIS_BASE,
    SRGSSR_TOKEN_URL,
    BfsVoteResultInput,
    ListDatesInput,
    PolisListInput,
    VoteDetailInput,
    VoteSearchInput,
    _host_allowed,
    _validate_outbound,
    democracy_bfs_get_vote_results,
    democracy_bfs_list_vote_dates,
    democracy_get_cantonal_results,
    democracy_get_party_positions,
    democracy_get_vote_detail,
    democracy_list_vote_dates,
    democracy_polis_list_votations,
    democracy_search_votes,
)

# ---------------------------------------------------------------------------
# Minimal Sample CSV – nur die für Tests relevanten Spalten
# ---------------------------------------------------------------------------


def _build_sample_csv() -> str:
    """Baut eine minimale CSV mit nur den nötigen Spalten für Unit-Tests."""
    CANTONS = [
        "zh",
        "be",
        "lu",
        "ur",
        "sz",
        "ow",
        "nw",
        "gl",
        "zg",
        "fr",
        "so",
        "bs",
        "bl",
        "sh",
        "ar",
        "ai",
        "sg",
        "gr",
        "ag",
        "tg",
        "ti",
        "vd",
        "vs",
        "ne",
        "ge",
        "ju",
    ]

    # Basis-Spalten
    base_cols = [
        "\ufeffanr",
        "datum",
        "titel_kurz_d",
        "titel_kurz_f",
        "titel_kurz_e",
        "titel_off_d",
        "titel_off_f",
        "stichwort",
        "swissvoteslink",
        "anzahl",
        "rechtsform",
        "br-pos",
        "nr-pos",
        "nrja",
        "nrnein",
        "sr-pos",
        "srja",
        "srnein",
        "info_br-de",
        "info_br-en",
        "web-yes-1-de",
        "web-yes-2-de",
        "web-yes-3-de",
        "web-no-1-de",
        "web-no-2-de",
        "web-no-3-de",
        "p-fdp",
        "p-sps",
        "p-svp",
        "p-mitte",
        "p-evp",
        "p-gps",
        "p-glp",
        "p-pda",
        "p-sd",
        "p-edu",
        "annahme",
        "berecht",
        "stimmen",
        "bet",
        "leer",
        "ungultig",
        "gultig",
        "volkja",
        "volknein",
        "volkja-proz",
        "kt-ja",
        "kt-nein",
        "ktjaproz",
        "ja-lager",
        "nein-lager",
        "finanz-ja-tot",
        "finanz-nein-tot",
        "unter_g",
        "swissvoteslink",
        "anneepolitique",
    ]
    # Kantonale Spalten (je 8: berecht, stimmen, bet, gultig, ja, nein, japroz, annahme)
    cantonal_cols = []
    for kt in CANTONS:
        cantonal_cols += [
            f"{kt}-berecht",
            f"{kt}-stimmen",
            f"{kt}-bet",
            f"{kt}-gultig",
            f"{kt}-ja",
            f"{kt}-nein",
            f"{kt}-japroz",
            f"{kt}-annahme",
        ]

    all_cols = base_cols + cantonal_cols

    # Kantonale Werte: Zürich (ZH) hat 54.7% Ja, alle anderen ~60% Ja, accepted=1
    kt_values: dict[str, list[str]] = {}
    zh_vals = ["900000", "600000", "66.7", "590000", "323330", "266670", "54.7", "1"]
    for kt in CANTONS:
        if kt == "zh":
            kt_values[kt] = zh_vals
        else:
            kt_values[kt] = ["200000", "130000", "65", "128000", "83200", "44800", "65.0", "1"]

    # Zeile 551: Volksinitiative "AHV 21", angenommen
    row: dict[str, str] = {
        "\ufeffanr": "551",
        "datum": "2022-09-25",
        "titel_kurz_d": "AHV 21",
        "titel_kurz_f": "AVS 21",
        "titel_kurz_e": "AVS 21",
        "titel_off_d": "Volksinitiative AHV 21",
        "titel_off_f": "Initiative AVS 21",
        "stichwort": "AHV",
        "swissvoteslink": "https://swissvotes.ch/vote/551",
        "anzahl": "1",
        "rechtsform": "3",
        "br-pos": "2",
        "nr-pos": "2",
        "nrja": "80",
        "nrnein": "120",
        "sr-pos": "2",
        "srja": "14",
        "srnein": "29",
        "info_br-de": "Der Bundesrat empfiehlt die Ablehnung.",
        "info_br-en": "The Federal Council recommends rejection.",
        "web-yes-1-de": "https://ja-ahv21.ch",
        "web-yes-2-de": "",
        "web-yes-3-de": "",
        "web-no-1-de": "https://nein-ahv21.ch",
        "web-no-2-de": "",
        "web-no-3-de": "",
        "p-fdp": "1",  # FDP: Ja
        "p-sps": "2",  # SP: Nein
        "p-svp": "2",
        "p-mitte": "1",
        "p-evp": "1",
        "p-gps": "2",
        "p-glp": "2",
        "p-pda": "2",
        "p-sd": "2",
        "p-edu": "2",
        "annahme": "1",
        "berecht": "5500000",
        "stimmen": "3200000",
        "bet": "58.2",
        "leer": "12000",
        "ungultig": "8000",
        "gultig": "3180000",
        "volkja": "1700000",
        "volknein": "1480000",
        "volkja-proz": "53.5",
        "kt-ja": "15",
        "kt-nein": "11",
        "ktjaproz": "57.7",
        "ja-lager": "FDP, Die Mitte, EVP",
        "nein-lager": "SP, SVP, GPS, GLP",
        "finanz-ja-tot": "5000000",
        "finanz-nein-tot": "3000000",
        "unter_g": "108000",
        "anneepolitique": "https://anneepolitique.swiss/551",
    }
    for kt in CANTONS:
        suffixes = ["berecht", "stimmen", "bet", "gultig", "ja", "nein", "japroz", "annahme"]
        for i, suf in enumerate(suffixes):
            row[f"{kt}-{suf}"] = kt_values[kt][i]

    header = ";".join(all_cols)
    values = ";".join(row.get(c, "") for c in all_cols)
    return header + "\n" + values + "\n"


SAMPLE_CSV = _build_sample_csv()
SWISSVOTES_URL = "https://swissvotes.ch/page/dataset/swissvotes_dataset.csv"


@pytest.fixture(autouse=True)
def reset_cache():
    """Resette den Swissvotes-Cache vor jedem Test."""
    import swiss_democracy_mcp.server as srv

    srv._swissvotes_cache = None
    srv._swissvotes_loaded_at = 0.0
    yield
    srv._swissvotes_cache = None
    srv._swissvotes_loaded_at = 0.0


@respx.mock
@pytest.mark.asyncio
async def test_search_votes_by_keyword():
    """Suche nach 'AHV' findet die gemockte Abstimmung."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = VoteSearchInput(keyword="AHV")
    result = await democracy_search_votes(params)
    data = json.loads(result)
    assert data["total"] >= 1
    assert any("AHV" in v["title_de"] or "AHV" in v.get("title_en", "") for v in data["votes"])


@respx.mock
@pytest.mark.asyncio
async def test_search_votes_year_filter():
    """Suche mit year_from=2023 findet keine Abstimmungen aus 2022."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = VoteSearchInput(year_from=2023)
    result = await democracy_search_votes(params)
    data = json.loads(result)
    assert data["total"] == 0


@respx.mock
@pytest.mark.asyncio
async def test_get_vote_detail():
    """Detail-Abruf für Abstimmung 551 liefert korrekte Felder."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = VoteDetailInput(vote_number="551")
    result = await democracy_get_vote_detail(params)
    data = json.loads(result)
    assert data["vote_number"] == "551"
    assert "AHV" in data["title_short_de"]
    assert data["result"]["yes_percent"] is not None


@respx.mock
@pytest.mark.asyncio
async def test_get_vote_detail_not_found():
    """Detail-Abruf für unbekannte Nummer gibt Fehlermeldung zurück."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = VoteDetailInput(vote_number="9999")
    result = await democracy_get_vote_detail(params)
    data = json.loads(result)
    assert "error" in data


@respx.mock
@pytest.mark.asyncio
async def test_get_party_positions():
    """Parteiparolen für Abstimmung 551 sind dekodiert."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = VoteDetailInput(vote_number="551")
    result = await democracy_get_party_positions(params)
    data = json.loads(result)
    assert "party_positions" in data
    # FDP = 1 → "Ja"
    assert data["party_positions"]["FDP"] == "Ja"
    # SP = 2 → "Nein"
    assert data["party_positions"]["SP"] == "Nein"


@respx.mock
@pytest.mark.asyncio
async def test_get_cantonal_results():
    """Kantonsresultate enthalten alle 26 Kantone."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = VoteDetailInput(vote_number="551")
    result = await democracy_get_cantonal_results(params)
    data = json.loads(result)
    assert "cantons" in data
    assert len(data["cantons"]) == 26
    assert "zh" in data["cantons"]
    assert data["cantons"]["zh"]["name"] == "Zürich"
    assert data["cantons"]["zh"]["yes_percent"] is not None


@respx.mock
@pytest.mark.asyncio
async def test_list_vote_dates():
    """Abstimmungsdaten-Liste gibt 1 Datum zurück."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = ListDatesInput()
    result = await democracy_list_vote_dates(params)
    data = json.loads(result)
    assert data["total_dates"] >= 1
    assert data["dates"][0]["date"] == "2022-09-25"


@respx.mock
@pytest.mark.asyncio
async def test_search_votes_result_filter_angenommen():
    """Filter 'angenommen' findet angenommene Abstimmungen."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = VoteSearchInput(result="angenommen")
    result = await democracy_search_votes(params)
    data = json.loads(result)
    # annahme=1 in SAMPLE_CSV
    assert data["total"] == 1


@respx.mock
@pytest.mark.asyncio
async def test_search_votes_result_filter_abgelehnt():
    """Filter 'abgelehnt' findet keine Abstimmung (unsere Beispielabstimmung ist angenommen)."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = VoteSearchInput(result="abgelehnt")
    result = await democracy_search_votes(params)
    data = json.loads(result)
    assert data["total"] == 0


@respx.mock
@pytest.mark.asyncio
async def test_search_votes_legal_form_initiative():
    """Filter 'initiative' findet Volksinitiative (rechtsform=3)."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = VoteSearchInput(legal_form="initiative")
    result = await democracy_search_votes(params)
    data = json.loads(result)
    assert data["total"] == 1
    assert data["votes"][0]["legal_form"] == "Volksinitiative"


@respx.mock
@pytest.mark.asyncio
async def test_cantonal_zurich_result():
    """Zürich-Resultat für Abstimmung 551 ist korrekt geparst."""
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=SAMPLE_CSV))
    params = VoteDetailInput(vote_number="551")
    result = await democracy_get_cantonal_results(params)
    data = json.loads(result)
    zh = data["cantons"]["zh"]
    assert zh["yes_percent"] == 54.7
    assert zh["accepted"] == 1


# ---------------------------------------------------------------------------
# Live tests (require network + Swissvotes availability)
# ---------------------------------------------------------------------------


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_search_ahv():
    """Live: Suche nach 'AHV' liefert Resultate — mit Inhalt, nicht nur mit Anzahl.

    `total` allein deckt die Titelspalten ab, denn danach wird gefiltert. Die
    Felder der Treffer kommen aus anderen Spalten (`datum`, `volkja-proz`,
    `bet`), und die pruefte hier nichts: Wuerde die Quelle sie umbenennen,
    kaeme dieselbe Trefferzahl mit lauter leeren Vorlagen zurueck.
    """
    params = VoteSearchInput(keyword="AHV")
    result = await democracy_search_votes(params)
    data = json.loads(result)
    assert data["total"] > 5
    assert data["votes"], "Treffer gezaehlt, aber keine Vorlage geliefert"

    # Gemessen am 28.8.2026 ueber die erste Seite: `date`, `title_de`,
    # `yes_percent` und `turnout_percent` sind in 20 von 20 Treffern belegt.
    # `accepted` bewusst NICHT — es fehlt in einem der zwanzig (zurueckgezogene
    # Vorlage), und eine Zusicherung, die an echten Daten schon heute wackelt,
    # meldet spaeter Drift, die keine ist.
    for feld in ("date", "title_de", "yes_percent", "turnout_percent"):
        leer = [v["vote_number"] for v in data["votes"] if v.get(feld) in (None, "")]
        assert not leer, f"{feld} fehlt bei Abstimmung(en) {leer} — Spalte umbenannt?"


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_cantonal_results_recent():
    """Live: Kantonsresultate für eine bekannte moderne Abstimmung.

    `len(cantons) == 26` allein war zahnlos: Die Schluessel kommen aus
    `CANTON_NAMES`, nicht aus der Quelle. Gegengeprobt am 28.8.2026 — mit
    umbenannten Kantonsspalten liefert das Werkzeug 26 Kantone mit null
    belegten Datenfeldern, und der Test blieb gruen. Genau dieser Ausfall ist
    am 3.8.2026 im Portfolio passiert (Kopfzeile umbenannt, produktiv kaputt,
    alle Tests gruen), und ihn zu sehen ist der Zweck der Live-Suite.

    Die Zusicherungen stehen deshalb auf den Werten, nicht auf der Form.
    """
    params = VoteDetailInput(vote_number="551")
    result = await democracy_get_cantonal_results(params)
    data = json.loads(result)
    assert "cantons" in data
    kantone = data["cantons"]
    # Strukturell — haelt auch ohne jede Zahl aus der Quelle. Steht hier, damit
    # ein verlorener Kanton auffaellt, nicht als Beleg fuer Daten.
    assert len(kantone) == 26

    felder = (
        "eligible_voters",
        "votes_cast",
        "turnout_percent",
        "valid_votes",
        "yes_votes",
        "no_votes",
        "yes_percent",
        "accepted",
    )
    for feld in felder:
        leer = sorted(ab for ab, k in kantone.items() if k.get(feld) is None)
        assert not leer, f"{feld} fehlt in {len(leer)} Kanton(en): {leer} — Spalte umbenannt?"

    # Rechnet die Quelle mit sich selbst auf? Diese Zusicherung kommt ohne
    # hartkodierte Zahl aus und faellt auch dann, wenn die Spalten nicht
    # verschwinden, sondern verrutschen — dann stehen zwar Zahlen da, aber die
    # falschen, und die Arithmetik geht nicht mehr auf.
    for ab, k in kantone.items():
        abgegeben = k["yes_votes"] + k["no_votes"]
        assert abgegeben == k["valid_votes"], (
            f"{ab}: ja+nein={abgegeben}, gueltig={k['valid_votes']}"
        )
        assert abs(100.0 * k["yes_votes"] / abgegeben - k["yes_percent"]) < 0.05, (
            f"{ab}: Ja-Anteil passt nicht zur Stimmenzahl"
        )
        assert 0 < k["votes_cast"] <= k["eligible_voters"], (
            f"{ab}: {k['votes_cast']} Stimmende bei {k['eligible_voters']} Berechtigten"
        )
        assert k["accepted"] in (0, 1), f"{ab}: annahme={k['accepted']!r}"
        # Angenommen heisst mehr Ja als Nein — die beiden Spalten gehoeren
        # zusammen, und nur zusammen belegen sie, dass keine verrutscht ist.
        assert k["accepted"] == (1 if k["yes_percent"] > 50 else 0), (
            f"{ab}: annahme={k['accepted']} bei {k['yes_percent']}% Ja"
        )


# ---------------------------------------------------------------------------
# Geteilter HTTP-Client ueber Event-Loop-Grenzen hinweg
# ---------------------------------------------------------------------------
#
# Diese Tests laufen bewusst OHNE `-m live` und ohne Netz: Sie pruefen die
# Auswahl des Clients, nicht die Quelle. Der Fehler, der sie noetig gemacht
# hat, war nur im woechentlichen Live-Lauf sichtbar — dort schlug er zu, wo
# ihn keine PR-CI je gesehen haette.


@pytest.fixture
def frischer_client():
    """Client-Globals vor und nach dem Test leeren.

    Ausdruecklich NICHT `autouse`: Wuerde der Client vor jedem Test genullt,
    liefe die Live-Suite auch ohne die Loop-Pruefung in `_client()` gruen
    durch — die Fixture wuerde den Fehler zudecken, den zu zeigen ihr Zweck
    waere. Nur diese beiden Tests, die den Loop selbst in der Hand haben,
    bekommen sie.
    """
    import swiss_democracy_mcp.server as srv

    srv._http_client = None
    srv._http_client_loop = None
    yield srv
    srv._http_client = None
    srv._http_client_loop = None


def test_client_wird_pro_event_loop_neu_gebaut(frischer_client):
    """Ein neuer Loop bekommt einen neuen Client — der alte Pool ist dort tot.

    Gegenprobe: Faellt die Loop-Pruefung in `_client()` weg, liefert der
    zweite `asyncio.run` dasselbe Objekt zurueck und dieser Test faellt.
    """
    srv = frischer_client

    async def hole():
        return srv._client()

    erster = asyncio.run(hole())
    zweiter = asyncio.run(hole())
    assert erster is not zweiter


def test_client_bleibt_innerhalb_eines_loops_derselbe(frischer_client):
    """Der Pool wird geteilt (SDK-001) — die Loop-Pruefung darf ihn nicht
    bei jedem Aufruf wegwerfen."""
    srv = frischer_client

    async def zweimal():
        return srv._client(), srv._client()

    erster, zweiter = asyncio.run(zweimal())
    assert erster is zweiter


# ---------------------------------------------------------------------------
# SSRF / Egress-Allow-List (audit findings SEC-004 / SEC-005 / SEC-021)
# ---------------------------------------------------------------------------


def test_host_allowed_accepts_known_hosts_and_subdomains():
    assert _host_allowed("swissvotes.ch")
    assert _host_allowed("opendata.swiss")
    assert _host_allowed("www.bfs.admin.ch")  # subdomain of bfs.admin.ch
    assert _host_allowed("api.srgssr.ch")


def test_host_allowed_rejects_unknown_and_lookalike_hosts():
    assert not _host_allowed("evil.com")
    assert not _host_allowed("169.254.169.254")
    assert not _host_allowed("bfs.admin.ch.evil.com")  # suffix trick
    assert not _host_allowed("notswissvotes.ch")
    assert not _host_allowed(None)


@pytest.mark.asyncio
async def test_validate_outbound_rejects_non_https():
    with pytest.raises(ValueError, match="HTTPS"):
        await _validate_outbound("http://opendata.swiss/data", resolve=False)


@pytest.mark.asyncio
async def test_validate_outbound_rejects_disallowed_host():
    with pytest.raises(ValueError, match="Egress-Allow-List"):
        await _validate_outbound("https://evil.example.com/x", resolve=False)


@pytest.mark.asyncio
async def test_bfs_get_vote_results_rejects_metadata_url():
    """SSRF: a cloud-metadata URL must be refused as an isError (ToolError)."""
    params = BfsVoteResultInput(
        result_url="http://169.254.169.254/latest/meta-data/", level="national"
    )
    with pytest.raises(ToolError) as exc:
        await democracy_bfs_get_vote_results(params)
    assert "HTTPS" in str(exc.value) or "Allow-List" in str(exc.value)


@pytest.mark.asyncio
async def test_bfs_get_vote_results_rejects_offsite_host():
    params = BfsVoteResultInput(result_url="https://attacker.example.com/exfil", level="national")
    with pytest.raises(ToolError, match="Allow-List"):
        await democracy_bfs_get_vote_results(params)


# ---------------------------------------------------------------------------
# Execution errors surface as isError / ToolError (audit finding OBS-001)
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_http_error_raises_tool_error(monkeypatch):
    import swiss_democracy_mcp.server as srv

    monkeypatch.setattr(srv, "_swissvotes_cache", None)
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(500))
    with pytest.raises(ToolError):
        await democracy_search_votes(VoteSearchInput(keyword="AHV"))


# ---------------------------------------------------------------------------
# BFS tool coverage (audit finding OPS-001)
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_bfs_list_vote_dates_parses_resources():
    package = {
        "success": True,
        "result": {
            "resources": [
                {
                    "name": {"de": "Abstimmung 2024-03-03"},
                    "issued": "2024-03-03",
                    "download_url": "https://www.bfs.admin.ch/x/master",
                    "format": "JSON",
                }
            ]
        },
    }
    respx.get(BFS_NATIONAL_PACKAGE).mock(return_value=httpx.Response(200, json=package))
    data = json.loads(await democracy_bfs_list_vote_dates())
    assert data["total"] == 1
    assert data["vote_dates"][0]["format"] == "JSON"
    assert data["source"]["url"] == "https://opendata.swiss"


@respx.mock
@pytest.mark.asyncio
async def test_bfs_get_vote_results_national(monkeypatch):
    import swiss_democracy_mcp.server as srv

    # Isolate from the SSRF DNS gate (covered separately) — focus on parsing.
    async def _noop(url, *, resolve=True):
        return None

    monkeypatch.setattr(srv, "_validate_outbound", _noop)
    payload = {
        "schweiz": {
            "vorlagen": [
                {
                    "vorlagenId": "1",
                    "vorlagenTitel": [{"langKey": "de", "text": "Testvorlage"}],
                    "vorlageAngenommen": True,
                    "schweiz": {"resultat": {"jaStimmenInProzent": 55.5}},
                }
            ]
        }
    }
    url = "https://www.bfs.admin.ch/x/master"
    respx.get(url).mock(return_value=httpx.Response(200, json=payload))
    params = BfsVoteResultInput(result_url=url, level="national")
    data = json.loads(await democracy_bfs_get_vote_results(params))
    assert data["total_vorlagen"] == 1
    assert data["results"][0]["title_de"] == "Testvorlage"
    assert data["source"]["name"].startswith("Bundesamt")


# ---------------------------------------------------------------------------
# Polis tool coverage (audit finding OPS-001)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_polis_without_credentials_returns_hint():
    """No SRGSSR creds → friendly registration hint as a NORMAL result (not isError)."""
    result = await democracy_polis_list_votations(PolisListInput())
    assert "developer.srgssr.ch" in result


@respx.mock
@pytest.mark.asyncio
async def test_polis_list_votations_with_credentials(monkeypatch):
    import swiss_democracy_mcp.server as srv

    monkeypatch.setattr(srv.settings, "srgssr_consumer_key", SecretStr("k"))
    monkeypatch.setattr(srv.settings, "srgssr_consumer_secret", SecretStr("s"))
    monkeypatch.setattr(srv, "_token_cache", {"access_token": None, "expires_at": 0.0})
    respx.post(SRGSSR_TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
    )
    respx.get(f"{POLIS_BASE}/votations").mock(
        return_value=httpx.Response(
            200,
            json={
                "total": 1,
                "votationList": [{"date": "2020-09-27", "title": "X", "accepted": True}],
            },
        )
    )
    out = await democracy_polis_list_votations(PolisListInput(limit=1))
    assert "Polis Volksabstimmungen" in out
    assert "2020-09-27" in out


# ---------------------------------------------------------------------------
# Provenance / source field (audit finding CH-004)
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_search_response_carries_source_and_license():
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=_build_sample_csv()))
    data = json.loads(await democracy_search_votes(VoteSearchInput(keyword="AHV")))
    assert data["source"]["license"] == "CC BY 4.0"
    assert "swissvotes.ch" in data["source"]["url"]


@respx.mock
@pytest.mark.asyncio
async def test_search_empty_sets_match_type_none(monkeypatch):
    import swiss_democracy_mcp.server as srv

    monkeypatch.setattr(srv, "_swissvotes_cache", None)
    respx.get(SWISSVOTES_URL).mock(return_value=httpx.Response(200, text=_build_sample_csv()))
    data = json.loads(await democracy_search_votes(VoteSearchInput(keyword="zzz-nonexistent-xyz")))
    assert data["total"] == 0
    assert data["match_type"] == "none"
    assert "note" in data


# ---------------------------------------------------------------------------
# Settings / SecretStr (audit findings ARCH-004 / SEC-013)
# ---------------------------------------------------------------------------


def test_settings_loads_srgssr_creds_as_secretstr(monkeypatch):
    from swiss_democracy_mcp.server import Settings

    monkeypatch.setenv("SRGSSR_CONSUMER_KEY", "topsecretkey")
    monkeypatch.setenv("SRGSSR_CONSUMER_SECRET", "topsecretsecret")
    s = Settings()
    # SecretStr must not expose the value in its repr
    assert "topsecretkey" not in repr(s.srgssr_consumer_key)
    assert s.srgssr_consumer_key.get_secret_value() == "topsecretkey"


def test_settings_defaults_are_safe():
    from swiss_democracy_mcp.server import Settings

    s = Settings(_env_file=None)
    assert s.mcp_host == "127.0.0.1"
    assert s.mcp_transport == "stdio"


# ---------------------------------------------------------------------------
# CORS for Streamable HTTP (audit finding SDK-004)
# ---------------------------------------------------------------------------


def test_http_app_exposes_mcp_session_id_via_cors():
    from starlette.middleware.cors import CORSMiddleware

    from swiss_democracy_mcp.server import _build_http_app

    app = _build_http_app()
    cors = [m for m in app.user_middleware if m.cls is CORSMiddleware]
    assert cors, "CORSMiddleware must be configured for HTTP transport"
    kwargs = cors[0].kwargs
    assert "Mcp-Session-Id" in kwargs["expose_headers"]
    assert "Mcp-Session-Id" in kwargs["allow_headers"]
