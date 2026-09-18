"""Der Identitaets-Stempel, den Spec 2026-07-28 auf jede Antwort setzt.

`Implementation.version` ist im Schema ein PFLICHTFELD, und `MCPServer` fuellt
es mit `""` vor, wenn der Aufruf es auslaesst. Ein Pflichtfeld, das sich selbst
befriedigt, faellt nirgends auf: die Suite war vollstaendig gruen, waehrend
dieser Server jedem Aufrufer `version: ""` meldete — in beiden Protokoll-Aeren.
(Beim Fund am 18.9.2026 waren das 103 Tests; die Zahl steht hier als Datum des
Befunds, nicht als laufender Stand.)

Warum das unter 2026-07-28 schwerer wiegt als davor: die Handshake-Aera nennt
`serverInfo` genau einmal, in der `initialize`-Antwort. Die moderne Aera hat
keinen Handshake und stempelt die Identitaet stattdessen als
`_meta["io.modelcontextprotocol/serverInfo"]` auf JEDE Antwort (Spec #3002).
Der Leerwert war dort nicht eine Auskunft, sondern jede.

Gemessen statt gelesen. `tests/test_protocol_version.py` haengt an den
SDK-Konstanten und nennt das selbst die schwaechere Form; hier gehen echte
Anfragen durch den zusammengebauten ASGI-Stack. Ein Blick auf das
`MCPServer(...)`-Argument waere kein Test: es kann gesetzt sein und trotzdem
nie auf dem Draht ankommen, und genau diese Strecke ist das, was «nativ auf
2026-07-28» behauptet.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from mcp import Client as McpClient
from mcp.server.mcpserver import MCPServer
from mcp.shared.inbound import MCP_METHOD_HEADER, MCP_PROTOCOL_VERSION_HEADER
from mcp_types import (
    CLIENT_CAPABILITIES_META_KEY,
    CLIENT_INFO_META_KEY,
    PROTOCOL_VERSION_META_KEY,
    SERVER_INFO_META_KEY,
)
from mcp_types.version import LATEST_HANDSHAKE_VERSION, LATEST_MODERN_VERSION
from starlette.testclient import TestClient

from swiss_democracy_mcp import __version__
from swiss_democracy_mcp.server import REPOSITORY_URL, USER_AGENT, _build_http_app, mcp

ENDPOINT = "/mcp"

# Der Host, unter dem `build_transport_security` diesen Server erwartet. Ohne
# ihn meldet sich `TestClient` als `testserver`, und die Host-Pruefung
# beantwortet jede Anfrage mit 421 — ein Fehlschlag, der wie ein Protokoll-
# Problem aussieht und keines ist.
BASE_URL = "http://127.0.0.1:8000"

# Die modernen Methoden, deren Antwort den Stempel tragen muss. `server/discover`
# ist die Ankunftsseite der Aera — sie ersetzt den Handshake —, `tools/list` die
# Methode, die ein Client danach als erstes ruft.
MODERN_METHODS = ("server/discover", "tools/list")


def _modern_body(method: str) -> dict[str, Any]:
    """Eine Anfrage im Pro-Request-Envelope von 2026-07-28.

    Die `_meta`-Schluessel kommen aus `mcp_types` statt als Literale: sie sind
    die Drahtform, und eine abgeschriebene Fassung wuerde bei einer
    Umbenennung still weiter ein 400 provozieren, das wie ein Server-Fehler
    aussieht.
    """
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "_meta": {
                PROTOCOL_VERSION_META_KEY: LATEST_MODERN_VERSION,
                CLIENT_CAPABILITIES_META_KEY: {},
                CLIENT_INFO_META_KEY: {"name": "test", "version": "1"},
            }
        },
    }


def _modern_headers(method: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        MCP_PROTOCOL_VERSION_HEADER: LATEST_MODERN_VERSION,
        MCP_METHOD_HEADER: method,
    }


def _result(response: Any) -> dict[str, Any]:
    """Das `result` einer Antwort, gleich ob sie als JSON oder als SSE kam.

    Der moderne Pfad entscheidet erst waehrend der Bearbeitung, ob er auf
    `text/event-stream` festlegt. Ein Test, der nur `response.json()` kennt,
    faellt dann an der Formatgrenze statt an der Sache.
    """
    text = response.text
    if text.lstrip().startswith("event:"):
        text = text[text.index("{") :]
    payload = json.loads(text)
    assert "error" not in payload, payload["error"]
    return payload["result"]


def _stamp(response: Any) -> dict[str, Any]:
    meta = _result(response).get("_meta") or {}
    stamp = meta.get(SERVER_INFO_META_KEY)
    assert stamp is not None, f"keine {SERVER_INFO_META_KEY}-Stempelung in {meta}"
    return stamp


@pytest.fixture
def client() -> Any:
    """`with`, nicht blosses `TestClient(...)`: ohne Lifespan hat der
    Session-Manager keine Task-Group und jeder POST endet im RuntimeError."""
    with TestClient(_build_http_app(), base_url=BASE_URL) as c:
        yield c


# ── Die moderne Aera wird wirklich bedient ─────────────────────────────────
#
# Die Tests dieses Abschnitts sichern nicht eigenen Code, sondern die
# Strecke: dass das SDK ueber die App DIESES Servers die moderne Aera bedient.
# Eine Gegenprobe an `server.py` bewegt sie deshalb nicht — sie fallen erst,
# wenn ein SDK-Bump die Aera anders bedient oder gar nicht mehr. Das ist ihr
# Zweck und derselbe wie bei `test_ein_server_ohne_hinweise_sagt_nichts` in
# `test_cache_hints.py`; es steht hier benannt statt unausgesprochen.


@pytest.mark.parametrize("method", MODERN_METHODS)
def test_die_moderne_aera_beantwortet_eine_anfrage(client: TestClient, method: str) -> None:
    """Zuerst die Strecke selbst, vor jeder Aussage ueber ihren Inhalt.

    Ein 400 hier hiesse, dass dieser Server 2026-07-28 gar nicht bedient — und
    dann sagen alle Zusicherungen darunter nichts.
    """
    resp = client.post(ENDPOINT, json=_modern_body(method), headers=_modern_headers(method))
    assert resp.status_code == 200, resp.text


async def test_die_moderne_aera_zeigt_dieselben_werkzeuge(client: TestClient) -> None:
    """Nicht nur «200», sondern derselbe Bestand wie auf dem anderen Weg.

    Verglichen wird gegen den In-Memory-`Client` statt gegen eine Zahl. Ein
    `len(...) == 10` waere eine Kopie der Werkzeugliste im Test: es fiele beim
    naechsten Werkzeug, ohne dass etwas kaputt ist, und sagte auch dann nichts
    darueber, ob es DIESELBEN sind. Die Gegenueberstellung faellt genau
    dann, wenn die moderne Aera einen anderen Bestand zeigt — und das ist die
    Frage.
    """
    async with McpClient(mcp) as inmemory:
        erwartet = {t.name for t in (await inmemory.list_tools()).tools}

    resp = client.post(
        ENDPOINT, json=_modern_body("tools/list"), headers=_modern_headers("tools/list")
    )
    assert {t["name"] for t in _result(resp)["tools"]} == erwartet


def test_discover_nennt_die_moderne_revision(client: TestClient) -> None:
    """`server/discover` ist die Stelle, an der ein Client die Aera erfaehrt."""
    resp = client.post(
        ENDPOINT, json=_modern_body("server/discover"), headers=_modern_headers("server/discover")
    )
    assert LATEST_MODERN_VERSION in _result(resp)["supportedVersions"]


# ── Der Stempel ────────────────────────────────────────────────────────────


@pytest.mark.parametrize("method", MODERN_METHODS)
def test_jede_moderne_antwort_nennt_die_paketversion(client: TestClient, method: str) -> None:
    """Der eigentliche Defekt, an beiden Methoden gemessen.

    Ueber `method` parametrisiert und nicht an einer Methode geprueft, weil
    «auf jeder Antwort» genau die Zusicherung ist, die 2026-07-28 von der
    Handshake-Aera unterscheidet. Eine Stichprobe an `tools/list` bliebe gruen,
    wenn der Stempel nur dort haengt.
    """
    resp = client.post(ENDPOINT, json=_modern_body(method), headers=_modern_headers(method))
    stamp = _stamp(resp)
    assert stamp["version"] == __version__
    assert stamp["version"], "leere Version — das Pflichtfeld befriedigt sich selbst"


def test_der_stempel_traegt_titel_und_repo_adresse(client: TestClient) -> None:
    """Die beiden optionalen Felder, die mit dem Stempel mitfahren.

    Beide stehen hier, weil eine Gegenprobe sie einzeln gefordert hat: ohne die
    `title`-Zeile blieb die Suite gruen, als `title=` aus dem Konstruktor
    entfernt wurde — eine Zusicherung, die der Code traegt und kein Test
    gehalten haette.
    """
    resp = client.post(
        ENDPOINT, json=_modern_body("tools/list"), headers=_modern_headers("tools/list")
    )
    stamp = _stamp(resp)
    assert stamp["title"] == "Swiss Democracy MCP"
    assert stamp["websiteUrl"] == REPOSITORY_URL


def test_ein_server_ohne_version_stempelt_leer() -> None:
    """Negativkontrolle: gleiches SDK, gleicher Draht, kein `version=`.

    Ohne sie belegt der Test darueber nur, dass irgendwo eine Version steht —
    nicht, dass unser Konstruktor-Argument sie dorthin bringt. Sie faellt an
    dem Tag, an dem das SDK selbst einen Default setzt; dann pruefen die
    Zusicherungen oben naemlich nicht mehr, dass wir ihn setzen.
    """
    with TestClient(MCPServer("kontrolle").streamable_http_app(), base_url=BASE_URL) as c:
        resp = c.post(
            ENDPOINT, json=_modern_body("tools/list"), headers=_modern_headers("tools/list")
        )
        assert _stamp(resp)["version"] == ""


# ── Die Handshake-Aera daneben ─────────────────────────────────────────────


def _initialize(client: TestClient, offered: str) -> dict[str, Any]:
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": offered,
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1"},
        },
    }
    resp = client.post(
        ENDPOINT,
        json=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    assert resp.status_code == 200, resp.text
    return _result(resp)


def test_der_handshake_nennt_dieselbe_version(client: TestClient) -> None:
    """Derselbe Defekt auf dem anderen Draht.

    Er steht getrennt, weil `serverInfo` hier aus `create_initialization_options`
    kommt und nicht aus `server_info_stamp` — zwei Wege zu derselben Identitaet,
    die einzeln brechen koennen.
    """
    assert _initialize(client, LATEST_HANDSHAKE_VERSION)["serverInfo"]["version"] == __version__


def test_der_handshake_deckelt_bei_der_handshake_revision(client: TestClient) -> None:
    """Gemessen, was `test_protocol_version.py` nur aus Konstanten schliesst.

    Ein Client, der die moderne Revision im `initialize` anbietet, hat den
    Envelope gerade nicht benutzt — er bekommt die Handshake-Obergrenze, nicht
    2026-07-28. Faellt das zusammen, bedient dieser Server zwei Aeren mit
    derselben Nummer und die Trennung in den READMEs ist falsch.
    """
    assert _initialize(client, LATEST_MODERN_VERSION)["protocolVersion"] == LATEST_HANDSHAKE_VERSION


# ── Eine Quelle fuer die Repo-Adresse ──────────────────────────────────────


def test_der_user_agent_bleibt_unveraendert() -> None:
    """Haelt fest, dass `REPOSITORY_URL` den User-Agent nicht verschoben hat.

    Die Adresse stand zweimal im Code; sie steht jetzt einmal, und der
    User-Agent leitet sich daraus ab. Diese Zeile ist der Beleg, dass die
    Ableitung dieselbe Zeichenkette ergibt wie das Literal davor — eine
    Umstellung, die eine ausgehende Kennung veraendert, waere keine
    Aufraeumung.
    """
    assert (
        USER_AGENT
        == f"swiss-democracy-mcp/{__version__} (github.com/malkreide/swiss-democracy-mcp)"
    )
    assert REPOSITORY_URL == "https://github.com/malkreide/swiss-democracy-mcp"
