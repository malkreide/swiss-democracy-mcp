"""
Tests für swiss-democracy-mcp
Einheitstests (mit respx-Mocking) und Live-Tests (markiert mit @pytest.mark.live).
Ausführung: PYTHONPATH=src pytest tests/ -m "not live" -v
"""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from swiss_democracy_mcp.server import (
    ListDatesInput,
    VoteDetailInput,
    VoteSearchInput,
    democracy_get_cantonal_results,
    democracy_get_party_positions,
    democracy_get_vote_detail,
    democracy_list_vote_dates,
    democracy_search_votes,
)

# ---------------------------------------------------------------------------
# Minimal Sample CSV – nur die für Tests relevanten Spalten
# ---------------------------------------------------------------------------

def _build_sample_csv() -> str:
    """Baut eine minimale CSV mit nur den nötigen Spalten für Unit-Tests."""
    CANTONS = ["zh","be","lu","ur","sz","ow","nw","gl","zg","fr",
               "so","bs","bl","sh","ar","ai","sg","gr","ag","tg",
               "ti","vd","vs","ne","ge","ju"]

    # Basis-Spalten
    base_cols = [
        "\ufeffanr","datum","titel_kurz_d","titel_kurz_f","titel_kurz_e",
        "titel_off_d","titel_off_f","stichwort","swissvoteslink","anzahl",
        "rechtsform","br-pos","nr-pos","nrja","nrnein","sr-pos","srja","srnein",
        "info_br-de","info_br-en",
        "web-yes-1-de","web-yes-2-de","web-yes-3-de",
        "web-no-1-de","web-no-2-de","web-no-3-de",
        "p-fdp","p-sps","p-svp","p-mitte","p-evp","p-gps","p-glp",
        "p-pda","p-sd","p-edu",
        "annahme","berecht","stimmen","bet","leer","ungultig","gultig",
        "volkja","volknein","volkja-proz","kt-ja","kt-nein","ktjaproz",
        "ja-lager","nein-lager",
        "finanz-ja-tot","finanz-nein-tot","unter_g","swissvoteslink",
        "anneepolitique",
    ]
    # Kantonale Spalten (je 8: berecht, stimmen, bet, gultig, ja, nein, japroz, annahme)
    cantonal_cols = []
    for kt in CANTONS:
        cantonal_cols += [
            f"{kt}-berecht", f"{kt}-stimmen", f"{kt}-bet", f"{kt}-gultig",
            f"{kt}-ja", f"{kt}-nein", f"{kt}-japroz", f"{kt}-annahme",
        ]

    all_cols = base_cols + cantonal_cols

    # Kantonale Werte: Zürich (ZH) hat 54.7% Ja, alle anderen ~60% Ja, accepted=1
    kt_values: dict[str, list[str]] = {}
    zh_vals = ["900000","600000","66.7","590000","323330","266670","54.7","1"]
    for kt in CANTONS:
        if kt == "zh":
            kt_values[kt] = zh_vals
        else:
            kt_values[kt] = ["200000","130000","65","128000","83200","44800","65.0","1"]

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
        "p-fdp": "1",   # FDP: Ja
        "p-sps": "2",   # SP: Nein
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
        suffixes = ["berecht","stimmen","bet","gultig","ja","nein","japroz","annahme"]
        for i, suf in enumerate(suffixes):
            row[f"{kt}-{suf}"] = kt_values[kt][i]

    header = ";".join(all_cols)
    values = ";".join(row.get(c, "") for c in all_cols)
    return header + "\n" + values + "\n"


SAMPLE_CSV = _build_sample_csv()
SWISSVOTES_URL = "https://swissvotes.ch/page/dataset/swissvotes_dataset.csv"

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
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
    params = VoteSearchInput(keyword="AHV")
    result = await democracy_search_votes(params)
    data = json.loads(result)
    assert data["total"] >= 1
    assert any("AHV" in v["title_de"] or "AHV" in v.get("title_en", "") for v in data["votes"])


@respx.mock
@pytest.mark.asyncio
async def test_search_votes_year_filter():
    """Suche mit year_from=2023 findet keine Abstimmungen aus 2022."""
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
    params = VoteSearchInput(year_from=2023)
    result = await democracy_search_votes(params)
    data = json.loads(result)
    assert data["total"] == 0


@respx.mock
@pytest.mark.asyncio
async def test_get_vote_detail():
    """Detail-Abruf für Abstimmung 551 liefert korrekte Felder."""
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
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
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
    params = VoteDetailInput(vote_number="9999")
    result = await democracy_get_vote_detail(params)
    data = json.loads(result)
    assert "error" in data


@respx.mock
@pytest.mark.asyncio
async def test_get_party_positions():
    """Parteiparolen für Abstimmung 551 sind dekodiert."""
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
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
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
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
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
    params = ListDatesInput()
    result = await democracy_list_vote_dates(params)
    data = json.loads(result)
    assert data["total_dates"] >= 1
    assert data["dates"][0]["date"] == "2022-09-25"


@respx.mock
@pytest.mark.asyncio
async def test_search_votes_result_filter_angenommen():
    """Filter 'angenommen' findet angenommene Abstimmungen."""
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
    params = VoteSearchInput(result="angenommen")
    result = await democracy_search_votes(params)
    data = json.loads(result)
    # annahme=1 in SAMPLE_CSV
    assert data["total"] == 1


@respx.mock
@pytest.mark.asyncio
async def test_search_votes_result_filter_abgelehnt():
    """Filter 'abgelehnt' findet keine Abstimmung (unsere Beispielabstimmung ist angenommen)."""
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
    params = VoteSearchInput(result="abgelehnt")
    result = await democracy_search_votes(params)
    data = json.loads(result)
    assert data["total"] == 0


@respx.mock
@pytest.mark.asyncio
async def test_search_votes_legal_form_initiative():
    """Filter 'initiative' findet Volksinitiative (rechtsform=3)."""
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
    params = VoteSearchInput(legal_form="initiative")
    result = await democracy_search_votes(params)
    data = json.loads(result)
    assert data["total"] == 1
    assert data["votes"][0]["legal_form"] == "Volksinitiative"


@respx.mock
@pytest.mark.asyncio
async def test_cantonal_zurich_result():
    """Zürich-Resultat für Abstimmung 551 ist korrekt geparst."""
    respx.get(SWISSVOTES_URL).mock(
        return_value=httpx.Response(200, text=SAMPLE_CSV)
    )
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
    """Live: Suche nach 'AHV' liefert Resultate."""
    params = VoteSearchInput(keyword="AHV")
    result = await democracy_search_votes(params)
    data = json.loads(result)
    assert data["total"] > 5


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_cantonal_results_recent():
    """Live: Kantonsresultate für eine bekannte moderne Abstimmung."""
    params = VoteDetailInput(vote_number="551")
    result = await democracy_get_cantonal_results(params)
    data = json.loads(result)
    assert "cantons" in data
    assert len(data["cantons"]) == 26
