"""Die CKAN-Hülle wird bestätigt, nicht angenommen (FID-006).

`democracy_bfs_list_vote_dates` schrieb:

    resources = data.get("result", {}).get("resources", [])

Fällt `result` weg oder wandert es, war `resources` leer, die Schleife lief
nullmal, und das Werkzeug antwortete mit `total: 0` und einer leeren Liste von
Abstimmungsdaten. Für das Modell ist das nicht davon zu unterscheiden, dass das
BFS gerade keine Abstimmungsdaten führt — und die Archivdaten reichen bis 1981
zurück, `total: 0` ist dort also nie eine plausible Antwort.

Der Portfolio-Durchlauf am 2026-08-07 fand acht Server, die mit CKAN sprechen;
alle acht prüfen das `success`-Envelope, sieben defaulteten `result` danach.
"""

from __future__ import annotations

import json

import httpx
import pytest
import respx
from mcp.server.mcpserver.exceptions import ToolError

from swiss_democracy_mcp.server import (
    BFS_NATIONAL_PACKAGE,
    UpstreamSchemaError,
    _ckan_resources,
    democracy_bfs_list_vote_dates,
)


def _mock(payload):
    return respx.get(BFS_NATIONAL_PACKAGE).mock(return_value=httpx.Response(200, json=payload))


# --- Der Fund ----------------------------------------------------------------


@respx.mock
async def test_a_missing_result_is_not_a_package_without_data():
    """Die Kernzusage. Vorher: `total: 0` und ein zufriedener Aufrufer.

    Der Fehler erreicht den Client als `isError: true` (`ToolError`), nicht als
    normales Ergebnis mit einem Fehlertext darin — dieselbe Zusage, die
    `_fail` für alle anderen Fehler dieses Servers gibt.
    """
    _mock({"success": True, "help": "https://opendata.swiss/api/3/"})
    with pytest.raises(ToolError):
        await democracy_bfs_list_vote_dates()


@respx.mock
async def test_a_result_without_resources_is_rejected():
    _mock({"success": True, "result": {"title": "Echtzeitdaten"}})
    with pytest.raises(ToolError):
        await democracy_bfs_list_vote_dates()


@respx.mock
async def test_the_message_reaches_the_model_with_the_keys_in_it():
    """`UpstreamSchemaError` erbt von `ValueError`, damit genau das gilt.

    `_friendly_error` reicht `ValueError`-Meldungen wörtlich durch; jeder
    andere Typ landet im `f"{type(e).__name__}: {e}"`-Zweig. Die vorhandenen
    Schlüssel stehen in der Antwort — sie dem Modell vorzuenthalten, wäre eine
    Entscheidung gegen die Diagnose.
    """
    _mock({"success": True, "help": "…", "payload": {}})
    with pytest.raises(ToolError) as excinfo:
        await democracy_bfs_list_vote_dates()
    message = str(excinfo.value)
    assert "'help'" in message and "'payload'" in message, message
    assert "keine Leermenge" in message
    assert "UpstreamSchemaError:" not in message, "die Meldung selbst, nicht ihr Typname"


# --- Die Gegenrichtung -------------------------------------------------------


@respx.mock
async def test_a_package_with_resources_still_parses():
    _mock(
        {
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
    )
    data = json.loads(await democracy_bfs_list_vote_dates())
    assert data["total"] == 1
    assert data["vote_dates"][0]["format"] == "JSON"


@respx.mock
async def test_an_empty_resource_list_is_still_a_normal_answer():
    """`resources: []` ist eine Aussage der Quelle, kein Strukturfehler.

    Ein Wächter, der die mitfängt, wird nach dem zweiten Fehlalarm
    abgeschaltet — deshalb bestätigt der Helfer die **Anwesenheit** des
    Schlüssels und nicht seinen Inhalt.
    """
    _mock({"success": True, "result": {"resources": []}})
    data = json.loads(await democracy_bfs_list_vote_dates())
    assert data["total"] == 0


@respx.mock
async def test_a_failed_envelope_still_returns_the_old_error_json():
    """`success: false` bleibt, was es war — die Quelle hat Nein gesagt."""
    _mock({"success": False, "error": {"message": "Not found"}})
    data = json.loads(await democracy_bfs_list_vote_dates())
    assert "error" in data


# --- Der Helfer selbst -------------------------------------------------------


def test_the_helper_separates_a_missing_key_from_an_empty_list():
    assert _ckan_resources({"result": {"resources": []}}, "test") == []
    with pytest.raises(UpstreamSchemaError):
        _ckan_resources({"result": {}}, "test")
    with pytest.raises(UpstreamSchemaError):
        _ckan_resources({}, "test")


def test_the_helper_rejects_a_non_object_result():
    with pytest.raises(UpstreamSchemaError) as excinfo:
        _ckan_resources({"result": ["a", "b"]}, "test")
    assert "list" in str(excinfo.value)
