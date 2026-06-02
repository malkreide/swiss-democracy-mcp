"""
Swiss Democracy MCP Server
==========================
Provides AI models with access to Swiss direct democracy data:

- Swissvotes (Uni Bern): All federal popular votes since 1848 with party
  positions, cantonal breakdowns, turnout, policy domains (874 columns, CSV)
- opendata.swiss / BFS: Real-time and archived vote results (federal + cantonal)
- SRGSSR Polis (optional): Historical votations and elections since 1900,
  including municipality-level results

Authentication:
    Swissvotes and BFS data require NO authentication.
    For SRGSSR Polis: Set SRGSSR_CONSUMER_KEY and SRGSSR_CONSUMER_SECRET.
    Register at https://developer.srgssr.ch to obtain credentials.
    Without Polis credentials, the Polis tools return a helpful registration hint.

Demo query:
    «Wie hat der Kanton Zürich bei der AHV-Initiative 1995 abgestimmt?»
    → democracy_search_votes(keyword="AHV", year_from=1995, year_to=1995)
    → democracy_get_cantonal_results(vote_number=<anr>)
"""

from __future__ import annotations

import asyncio
import base64
import csv
import io
import ipaddress
import json
import socket
import sys
import time
from contextlib import asynccontextmanager
from typing import Any, Literal
from urllib.parse import urlparse

import httpx
import structlog
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SWISSVOTES_CSV_URL = "https://swissvotes.ch/page/dataset/swissvotes_dataset.csv"
BFS_NATIONAL_PACKAGE = (
    "https://opendata.swiss/api/3/action/package_show"
    "?id=echtzeitdaten-am-abstimmungstag-zu-eidgenoessischen-abstimmungsvorlagen"
)
BFS_CANTONAL_PACKAGE = (
    "https://opendata.swiss/api/3/action/package_show"
    "?id=echtzeitdaten-am-abstimmungstag-zu-kantonalen-abstimmungsvorlagen"
)
SRGSSR_BASE = "https://api.srgssr.ch"
SRGSSR_TOKEN_URL = f"{SRGSSR_BASE}/oauth/v1/accesstoken"
POLIS_BASE = f"{SRGSSR_BASE}/polis/v1"

TIMEOUT = 30.0
USER_AGENT = "swiss-democracy-mcp/1.0.0 (github.com/malkreide/swiss-democracy-mcp)"

# ---------------------------------------------------------------------------
# Settings (audit findings ARCH-004 / SEC-013 / ARCH-005)
# ---------------------------------------------------------------------------
# Central, typed configuration loaded from the environment. Secrets are held as
# pydantic SecretStr so they never leak through reprs or logs.


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    srgssr_consumer_key: SecretStr | None = None
    srgssr_consumer_secret: SecretStr | None = None
    mcp_transport: str = "stdio"
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 8000
    log_level: str = "INFO"


settings = Settings()

# ---------------------------------------------------------------------------
# Structured logging to stderr (audit findings OBS-003 / OBS-004)
# ---------------------------------------------------------------------------
# JSON logs go to stderr — stdout stays reserved for the stdio JSON-RPC stream.

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.WriteLoggerFactory(file=sys.stderr),
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(__import__("logging"), settings.log_level.upper(), 20)
    ),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger("swiss_democracy_mcp")

# ---------------------------------------------------------------------------
# Data-source provenance (audit finding CH-004 — OGD-CH licence attribution)
# ---------------------------------------------------------------------------
SOURCES: dict[str, dict[str, str]] = {
    "swissvotes": {
        "name": "Swissvotes — Université de Berne / Année Politique Suisse",
        "license": "CC BY 4.0",
        "url": "https://swissvotes.ch",
    },
    "bfs": {
        "name": "Bundesamt für Statistik (BFS) / opendata.swiss",
        "license": "opendata.swiss terms (mostly CC BY / Open by Default)",
        "url": "https://opendata.swiss",
    },
    "polis": {
        "name": "SRG SSR — Polis",
        "license": "SRGSSR developer terms (free tier, non-commercial)",
        "url": "https://developer.srgssr.ch",
    },
}


def _emit(payload: dict, source_key: str) -> str:
    """Attach source/licence provenance and serialise to JSON (CC BY 4.0 attribution)."""
    payload["source"] = SOURCES[source_key]
    return json.dumps(payload, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Egress allow-list & SSRF prevention (audit findings SEC-004 / SEC-005 / SEC-021)
# ---------------------------------------------------------------------------
# Outbound HTTP is restricted to this fixed set of trusted Swiss open-data hosts.
# A subdomain of an allowed host (e.g. *.bfs.admin.ch) is also permitted. This is
# the primary defence against SSRF: even an attacker-controlled tool argument
# (e.g. BFS `result_url`) can only ever reach a known-good host.
ALLOWED_HOSTS = frozenset(
    {
        "swissvotes.ch",
        "opendata.swiss",
        "bfs.admin.ch",
        "api.srgssr.ch",
    }
)

# Resolved IPs in these ranges are rejected — blocks cloud-metadata endpoints,
# loopback and private/link-local networks (defence-in-depth + DNS-rebinding).
BLOCKED_NETWORKS = [
    ipaddress.ip_network(n)
    for n in (
        "0.0.0.0/8",
        "10.0.0.0/8",
        "100.64.0.0/10",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "::1/128",
        "fc00::/7",
        "fe80::/10",
    )
]


def _host_allowed(host: str | None) -> bool:
    """True iff `host` is an allow-listed host or a subdomain of one."""
    if not host:
        return False
    host = host.lower()
    return any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS)


async def _validate_outbound(url: str, *, resolve: bool = True) -> None:
    """Gate every outbound request: HTTPS-only + host allow-list (+ IP blocklist).

    Args:
        url: the target URL.
        resolve: if True, resolve DNS once and reject private/link-local/
            metadata IPs. Used for caller-supplied URLs (SSRF vector). For
            compile-time-constant trusted URLs `resolve=False` keeps the check
            network-free.

    Raises:
        ValueError: if the URL is not HTTPS, the host is not allow-listed, or
            it resolves into a blocked network range.
    """
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Nur HTTPS-URLs sind erlaubt (erhalten: '{parsed.scheme or '?'}').")
    host = parsed.hostname
    if not _host_allowed(host):
        raise ValueError(
            f"Host '{host}' steht nicht auf der Egress-Allow-List. "
            f"Erlaubt sind: {', '.join(sorted(ALLOWED_HOSTS))}."
        )
    if not resolve:
        return
    loop = asyncio.get_event_loop()
    try:
        addrinfo = await loop.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise ValueError(f"DNS-Auflösung für '{host}' fehlgeschlagen: {e}") from e
    for *_, sockaddr in addrinfo:
        ip = ipaddress.ip_address(sockaddr[0])
        for blocked in BLOCKED_NETWORKS:
            if ip in blocked:
                raise ValueError(
                    f"Aufgelöste IP {ip} liegt im gesperrten Bereich {blocked} "
                    f"(SSRF-Schutz)."
                )


# ---------------------------------------------------------------------------
# Shared HTTP client (audit finding SDK-001): one pooled AsyncClient for the
# whole process instead of a fresh client per tool call. Created lazily and
# closed by the server lifespan.
# ---------------------------------------------------------------------------

_http_client: httpx.AsyncClient | None = None


def _client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=TIMEOUT,
            follow_redirects=False,
            headers={"User-Agent": USER_AGENT},
        )
    return _http_client


@asynccontextmanager
async def _lifespan(_server: FastMCP):
    """Shared lifecycle: dispose the pooled HTTP client on shutdown."""
    try:
        yield
    finally:
        global _http_client
        if _http_client is not None and not _http_client.is_closed:
            await _http_client.aclose()
        _http_client = None

# Rechtsform codes in Swissvotes
RECHTSFORM_MAP = {
    "1": "Obligatorisches Referendum",
    "2": "Fakultatives Referendum",
    "3": "Volksinitiative",
    "4": "Gegenentwurf",
    "5": "Stichfrage",
    "6": "Direkter Gegenentwurf",
}

# Party column names in Swissvotes CSV → human-readable label
PARTY_COLUMNS = {
    "p-fdp": "FDP",
    "p-sps": "SP",
    "p-svp": "SVP",
    "p-mitte": "Die Mitte",
    "p-evp": "EVP",
    "p-gps": "GPS (Grüne)",
    "p-glp": "GLP",
    "p-pda": "PdA",
    "p-edu": "EDU",
    "p-lega": "Lega",
}

# Cantonal abbreviations → full name
CANTON_NAMES = {
    "zh": "Zürich", "be": "Bern", "lu": "Luzern", "ur": "Uri",
    "sz": "Schwyz", "ow": "Obwalden", "nw": "Nidwalden", "gl": "Glarus",
    "zg": "Zug", "fr": "Freiburg", "so": "Solothurn", "bs": "Basel-Stadt",
    "bl": "Basel-Landschaft", "sh": "Schaffhausen", "ar": "Appenzell AR",
    "ai": "Appenzell AI", "sg": "St. Gallen", "gr": "Graubünden",
    "ag": "Aargau", "tg": "Thurgau", "ti": "Tessin", "vd": "Waadt",
    "vs": "Wallis", "ne": "Neuenburg", "ge": "Genf", "ju": "Jura",
}

# Position codes (Bundesrat, NR, SR)
POSITION_MAP = {
    "1": "Ja / Annahme", "2": "Nein / Ablehnung", "3": "Keine Stimmempfehlung",
    "8": "Keine/nicht relevant", "9": "Unbekannt",
}

# ---------------------------------------------------------------------------
# In-memory cache for Swissvotes CSV
# ---------------------------------------------------------------------------

_swissvotes_cache: list[dict[str, str]] | None = None
_swissvotes_loaded_at: float = 0.0
CACHE_TTL = 86400.0  # 24 hours


async def _load_swissvotes() -> list[dict[str, str]]:
    """Downloads and caches the Swissvotes CSV dataset (semicolon-delimited)."""
    global _swissvotes_cache, _swissvotes_loaded_at
    now = time.time()
    if _swissvotes_cache is not None and (now - _swissvotes_loaded_at) < CACHE_TTL:
        return _swissvotes_cache

    await _validate_outbound(SWISSVOTES_CSV_URL, resolve=False)
    log.info("swissvotes_csv_refresh", host=urlparse(SWISSVOTES_CSV_URL).hostname, source="swissvotes")
    resp = await _client().get(SWISSVOTES_CSV_URL, timeout=60.0, follow_redirects=True)
    resp.raise_for_status()
    content = resp.text

    reader = csv.DictReader(io.StringIO(content), delimiter=";")
    rows = list(reader)
    # Strip BOM from first key if present
    if rows and rows[0]:
        first_key = next(iter(rows[0]))
        if first_key.startswith("\ufeff"):
            clean_key = first_key.lstrip("\ufeff")
            for row in rows:
                row[clean_key] = row.pop(first_key)

    _swissvotes_cache = rows
    _swissvotes_loaded_at = now
    return _swissvotes_cache


# ---------------------------------------------------------------------------
# SRGSSR OAuth2 token management
# ---------------------------------------------------------------------------

_token_cache: dict[str, Any] = {"access_token": None, "expires_at": 0.0}


def _get_polis_credentials() -> tuple[str, str] | None:
    if settings.srgssr_consumer_key is None or settings.srgssr_consumer_secret is None:
        return None
    key = settings.srgssr_consumer_key.get_secret_value()
    secret = settings.srgssr_consumer_secret.get_secret_value()
    if not key or not secret:
        return None
    return key, secret


async def _get_polis_token() -> str | None:
    """Returns a valid OAuth2 access token for SRGSSR Polis, or None if no credentials."""
    creds = _get_polis_credentials()
    if creds is None:
        return None

    now = time.time()
    if _token_cache["access_token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["access_token"]

    key, secret = creds
    credentials = base64.b64encode(f"{key}:{secret}".encode()).decode()

    await _validate_outbound(SRGSSR_TOKEN_URL, resolve=False)
    resp = await _client().post(
        SRGSSR_TOKEN_URL,
        params={"grant_type": "client_credentials"},
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    resp.raise_for_status()
    data = resp.json()

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = now + int(data.get("expires_in", 3600))
    return _token_cache["access_token"]


_NO_POLIS_CREDS = (
    "SRGSSR Polis-Credentials fehlen. "
    "Bitte SRGSSR_CONSUMER_KEY und SRGSSR_CONSUMER_SECRET setzen. "
    "Kostenlose Registrierung: https://developer.srgssr.ch"
)


async def _polis_get(path: str, params: dict | None = None) -> dict:
    """Authenticated GET to SRGSSR Polis API."""
    token = await _get_polis_token()
    if token is None:
        raise ValueError(_NO_POLIS_CREDS)

    full_url = f"{POLIS_BASE}{path}"
    await _validate_outbound(full_url, resolve=False)
    resp = await _client().get(
        full_url,
        params=params,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    resp.raise_for_status()
    return resp.json()


async def _bfs_get(url: str, params: dict | None = None, *, resolve: bool = False) -> dict:
    """Unauthenticated GET for BFS/opendata.swiss endpoints.

    `resolve=True` is used for caller-supplied URLs (the BFS `result_url` tool
    argument) so the resolved IP is checked against the SSRF blocklist.
    """
    await _validate_outbound(url, resolve=resolve)
    log.info("outbound_request", host=urlparse(url).hostname, source="bfs")
    resp = await _client().get(url, params=params)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _parse_float(val: str) -> float | None:
    try:
        return float(val.replace(",", ".")) if val.strip() else None
    except (ValueError, AttributeError):
        return None


def _parse_int(val: str) -> int | None:
    try:
        return int(float(val)) if val.strip() else None
    except (ValueError, AttributeError):
        return None


def _handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Fehler: Ressource nicht gefunden. Bitte ID prüfen."
        elif e.response.status_code == 401:
            return f"Fehler: Authentifizierung fehlgeschlagen. {_NO_POLIS_CREDS}"
        elif e.response.status_code == 429:
            return "Fehler: Rate-Limit erreicht. Bitte kurz warten."
        return f"Fehler: API-Anfrage fehlgeschlagen (HTTP {e.response.status_code})."
    elif isinstance(e, httpx.TimeoutException):
        return "Fehler: Anfrage-Timeout. Bitte erneut versuchen."
    elif isinstance(e, ValueError):
        return str(e)
    return f"Fehler: {type(e).__name__}: {e}"


def _row_to_vote_summary(row: dict[str, str]) -> dict:
    """Convert a Swissvotes CSV row to a clean summary dict."""
    anr_raw = row.get("\ufeffanr") or row.get("anr") or ""
    rechtsform_code = row.get("rechtsform", "")
    return {
        "vote_number": anr_raw.strip(),
        "date": row.get("datum", ""),
        "title_de": row.get("titel_kurz_d", ""),
        "title_fr": row.get("titel_kurz_f", ""),
        "title_en": row.get("titel_kurz_e", ""),
        "legal_form": RECHTSFORM_MAP.get(rechtsform_code, rechtsform_code),
        "accepted": _parse_int(row.get("annahme", "")),
        "yes_percent": _parse_float(row.get("volkja-proz", "")),
        "turnout_percent": _parse_float(row.get("bet", "")),
        "federal_council_position": POSITION_MAP.get(row.get("br-pos", ""), row.get("br-pos", "")),
        "swissvotes_url": row.get("swissvoteslink", ""),
    }


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "swiss_democracy_mcp",
    lifespan=_lifespan,
    instructions=(
        "Dieser Server bietet Zugang zu Schweizer Demokratie-Daten: "
        "alle eidgenössischen Volksabstimmungen seit 1848 (Swissvotes), "
        "BFS-Echtzeitdaten am Abstimmungssonntag (opendata.swiss) sowie "
        "historische Wahlen und Abstimmungen seit 1900 (SRGSSR Polis). "
        "Für Polis-Tools sind SRGSSR_CONSUMER_KEY und SRGSSR_CONSUMER_SECRET nötig. "
        "Alle anderen Tools funktionieren ohne Authentifizierung."
    ),
)

# ===========================================================================
# PHASE 1 – Swissvotes (No Auth)
# ===========================================================================


class VoteSearchInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    keyword: str | None = Field(
        default=None,
        description="Suchbegriff im Titel (Deutsch oder Englisch), z.B. 'AHV', 'Strom', 'Asyl'",
        max_length=200,
    )
    year_from: int | None = Field(
        default=None, description="Startjahr (z.B. 1990)", ge=1848, le=2100
    )
    year_to: int | None = Field(
        default=None, description="Endjahr (z.B. 2024)", ge=1848, le=2100
    )
    legal_form: str | None = Field(
        default=None,
        description=(
            "Rechtsform: 'initiative' (Volksinitiative), "
            "'obligatorisch' (Obligatorisches Referendum), "
            "'fakultativ' (Fakultatives Referendum)"
        ),
    )
    result: str | None = Field(
        default=None,
        description="Ergebnis-Filter: 'angenommen' oder 'abgelehnt'",
    )
    policy_domain: str | None = Field(
        default=None,
        description=(
            "Politikbereich-Filter (Suchbegriff), z.B. 'Soziale Sicherheit', "
            "'Bildung', 'Umwelt', 'Wirtschaft', 'Verkehr'"
        ),
        max_length=100,
    )
    limit: int = Field(
        default=20, description="Maximale Anzahl Resultate (1–100)", ge=1, le=100
    )
    offset: int = Field(default=0, description="Offset für Pagination", ge=0)

    @field_validator("year_to")
    @classmethod
    def year_to_after_from(cls, v: int | None, info: Any) -> int | None:
        year_from = info.data.get("year_from")
        if v is not None and year_from is not None and v < year_from:
            raise ValueError("year_to muss >= year_from sein")
        return v


@mcp.tool(
    name="democracy_search_votes",
    annotations={
        "title": "Volksabstimmungen suchen (Swissvotes)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def democracy_search_votes(params: VoteSearchInput) -> str:
    """Durchsucht alle eidgenössischen Volksabstimmungen seit 1848 (Swissvotes-Datenbank).

    <use_case>Politische/journalistische Recherche: Vorlagen nach Thema, Zeitraum oder Ergebnis finden.</use_case>

    Filtert nach Stichwort, Zeitraum, Rechtsform, Ergebnis und Politikbereich.
    Gibt Titel, Datum, Rechtsform, Ja-Anteil, Beteiligung und Bundesratsempfehlung zurück.

    Args:
        params (VoteSearchInput): Suchparameter mit optionalen Feldern:
            - keyword (str): Freitextsuche im Titel (DE/EN)
            - year_from/year_to (int): Zeitraumfilter
            - legal_form (str): 'initiative', 'obligatorisch', 'fakultativ'
            - result (str): 'angenommen' oder 'abgelehnt'
            - policy_domain (str): Politikbereich-Stichwort
            - limit (int): Max. Resultate (Standard: 20)
            - offset (int): Pagination-Offset

    Returns:
        str: JSON mit 'total', 'count', 'offset', 'has_more', 'votes' (Liste von
             Vote-Objekten mit vote_number, date, title_de, legal_form,
             accepted, yes_percent, turnout_percent, federal_council_position)
    """
    try:
        rows = await _load_swissvotes()
    except Exception as e:
        return _handle_error(e)

    filtered: list[dict] = []

    kw = params.keyword.lower() if params.keyword else None
    lf_filter = (params.legal_form or "").lower()
    result_filter = (params.result or "").lower()
    pd_filter = (params.policy_domain or "").lower()

    # Rechtsform mapping for filter
    rechtsform_targets: set[str] = set()
    if lf_filter:
        for code, label in RECHTSFORM_MAP.items():
            if lf_filter in label.lower() or (
                lf_filter == "initiative" and code == "3"
            ) or (
                lf_filter == "obligatorisch" and code == "1"
            ) or (
                lf_filter == "fakultativ" and code == "2"
            ):
                rechtsform_targets.add(code)

    for row in rows:
        datum = row.get("datum", "")
        year_str = datum[:4] if datum else ""

        # Year filter
        if params.year_from and year_str:
            try:
                if int(year_str) < params.year_from:
                    continue
            except ValueError:
                pass
        if params.year_to and year_str:
            try:
                if int(year_str) > params.year_to:
                    continue
            except ValueError:
                pass

        # Keyword filter
        if kw:
            title_d = (row.get("titel_kurz_d") or "").lower()
            title_e = (row.get("titel_kurz_e") or "").lower()
            title_off = (row.get("titel_off_d") or "").lower()
            stichwort = (row.get("stichwort") or "").lower()
            if not any(kw in t for t in [title_d, title_e, title_off, stichwort]):
                continue

        # Legal form filter
        if rechtsform_targets:
            if row.get("rechtsform", "") not in rechtsform_targets:
                continue

        # Result filter
        if result_filter:
            annahme = row.get("annahme", "")
            if result_filter in ("angenommen", "ja") and annahme != "1":
                continue
            if result_filter in ("abgelehnt", "nein") and annahme != "0":
                continue

        # Policy domain filter (d1e1 contains BFS codes – search in title/keywords)
        if pd_filter:
            combined = " ".join([
                row.get("stichwort", ""),
                row.get("titel_off_d", ""),
                row.get("info_br-de", ""),
            ]).lower()
            if pd_filter not in combined:
                continue

        filtered.append(row)

    total = len(filtered)
    page = filtered[params.offset : params.offset + params.limit]

    result_list = [_row_to_vote_summary(r) for r in page]
    response: dict[str, Any] = {
        "total": total,
        "count": len(result_list),
        "offset": params.offset,
        "has_more": total > params.offset + len(result_list),
        "match_type": "exact" if total else "none",
        "votes": result_list,
    }
    if total == 0:
        response["note"] = (
            "Keine Treffer für diese Filter. Tipp: Suchbegriff kürzen oder anderssprachig "
            "(de/en) probieren, Zeitraum erweitern, oder mit democracy_list_vote_dates "
            "verfügbare Abstimmungsdaten prüfen."
        )
    return _emit(response, "swissvotes")


class VoteDetailInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    vote_number: str = Field(
        ...,
        description=(
            "Abstimmungsnummer (anr) aus democracy_search_votes, z.B. '551.9' oder '546'"
        ),
        min_length=1,
        max_length=20,
    )


@mcp.tool(
    name="democracy_get_vote_detail",
    annotations={
        "title": "Abstimmungsdetails (Swissvotes)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def democracy_get_vote_detail(params: VoteDetailInput) -> str:
    """Gibt vollständige Details zu einer eidgenössischen Volksabstimmung zurück.

    <use_case>Vertiefung zu einer konkreten Vorlage (Parlamentsempfehlungen, Resultat, Beteiligung).</use_case>

    Inkl. offiziellem Titel, Rechtsform, Parlamentsempfehlungen (NR, SR, Bundesrat),
    Abstimmungsresultat (national und kantonal), Beteiligung, Finanzierungsdaten
    und Link zur Swissvotes-Seite.

    Args:
        params (VoteDetailInput): Enthält:
            - vote_number (str): Abstimmungsnummer (anr) aus democracy_search_votes

    Returns:
        str: JSON mit vollständigen Vote-Details oder Fehlermeldung
    """
    try:
        rows = await _load_swissvotes()
    except Exception as e:
        return _handle_error(e)

    target = params.vote_number.strip()
    row = None
    for r in rows:
        anr = (r.get("\ufeffanr") or r.get("anr") or "").strip()
        if anr == target:
            row = r
            break

    if row is None:
        return json.dumps({"error": f"Abstimmung '{target}' nicht gefunden."}, ensure_ascii=False)

    rechtsform_code = row.get("rechtsform", "")
    annahme_val = _parse_int(row.get("annahme", ""))

    detail = {
        "vote_number": target,
        "date": row.get("datum", ""),
        "title_short_de": row.get("titel_kurz_d", ""),
        "title_short_fr": row.get("titel_kurz_f", ""),
        "title_short_en": row.get("titel_kurz_e", ""),
        "title_official_de": row.get("titel_off_d", ""),
        "title_official_fr": row.get("titel_off_f", ""),
        "keyword": row.get("stichwort", ""),
        "legal_form": RECHTSFORM_MAP.get(rechtsform_code, rechtsform_code),
        "swissvotes_url": row.get("swissvoteslink", ""),
        "annee_politique_url": row.get("anneepolitique", ""),
        "parliamentary_positions": {
            "federal_council": POSITION_MAP.get(row.get("br-pos", ""), row.get("br-pos", "")),
            "national_council": POSITION_MAP.get(row.get("nr-pos", ""), row.get("nr-pos", "")),
            "national_council_yes": _parse_int(row.get("nrja", "")),
            "national_council_no": _parse_int(row.get("nrnein", "")),
            "council_of_states": POSITION_MAP.get(row.get("sr-pos", ""), row.get("sr-pos", "")),
            "council_of_states_yes": _parse_int(row.get("srja", "")),
            "council_of_states_no": _parse_int(row.get("srnein", "")),
        },
        "result": {
            "accepted": annahme_val,
            "accepted_label": "Angenommen" if annahme_val == 1 else "Abgelehnt" if annahme_val == 0 else "Unbekannt",
            "popular_vote_yes": _parse_int(row.get("volkja", "")),
            "popular_vote_no": _parse_int(row.get("volknein", "")),
            "yes_percent": _parse_float(row.get("volkja-proz", "")),
            "cantons_yes": _parse_int(row.get("kt-ja", "")),
            "cantons_no": _parse_int(row.get("kt-nein", "")),
            "cantons_yes_percent": _parse_float(row.get("ktjaproz", "")),
            "eligible_voters": _parse_int(row.get("berecht", "")),
            "votes_cast": _parse_int(row.get("stimmen", "")),
            "turnout_percent": _parse_float(row.get("bet", "")),
            "valid_votes": _parse_int(row.get("gultig", "")),
            "blank_votes": _parse_int(row.get("leer", "")),
            "invalid_votes": _parse_int(row.get("ungultig", "")),
        },
        "federal_council_info_de": row.get("info_br-de", ""),
        "federal_council_info_en": row.get("info_br-en", ""),
        "signatures_valid": _parse_int(row.get("unter_g", "")),
    }
    return _emit(detail, "swissvotes")


@mcp.tool(
    name="democracy_get_party_positions",
    annotations={
        "title": "Parteiparolen zu einer Abstimmung (Swissvotes)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def democracy_get_party_positions(params: VoteDetailInput) -> str:
    """Gibt die Parteiparolen der grossen Schweizer Parteien zu einer Volksabstimmung zurück.

    <use_case>Analyse von Parteilinien und Kampagnen-Finanzierung zu einer Vorlage.</use_case>

    Dekodiert die numerischen Parolen-Codes aus Swissvotes in lesbare Labels:
    1=Ja, 2=Nein, 3=Stimmfreigabe, 4=Nein zum Gegenentwurf, 5=Ja zum Gegenentwurf,
    66=Keine Parole gefasst, 9=Unbekannt.

    Args:
        params (VoteDetailInput): Enthält:
            - vote_number (str): Abstimmungsnummer (anr)

    Returns:
        str: JSON mit Parteiparolen und Links zu Ja-/Nein-Komitees
    """
    try:
        rows = await _load_swissvotes()
    except Exception as e:
        return _handle_error(e)

    target = params.vote_number.strip()
    row = next(
        (r for r in rows
         if (r.get("\ufeffanr") or r.get("anr") or "").strip() == target),
        None,
    )
    if row is None:
        return json.dumps({"error": f"Abstimmung '{target}' nicht gefunden."}, ensure_ascii=False)

    PAROLE_MAP = {
        "1": "Ja", "2": "Nein", "3": "Stimmfreigabe",
        "4": "Nein (zu Gegenentwurf)", "5": "Ja (zu Gegenentwurf)",
        "66": "Keine Parole gefasst", "9": "Unbekannt", "": "Keine Angabe",
    }

    parties: dict[str, str] = {}
    for col, label in PARTY_COLUMNS.items():
        code = row.get(col, "")
        parties[label] = PAROLE_MAP.get(code, code)

    result = {
        "vote_number": target,
        "date": row.get("datum", ""),
        "title_de": row.get("titel_kurz_d", ""),
        "party_positions": parties,
        "ja_lager": row.get("ja-lager", ""),
        "nein_lager": row.get("nein-lager", ""),
        "yes_committees": [
            row.get("web-yes-1-de", ""), row.get("web-yes-2-de", ""), row.get("web-yes-3-de", "")
        ],
        "no_committees": [
            row.get("web-no-1-de", ""), row.get("web-no-2-de", ""), row.get("web-no-3-de", "")
        ],
        "finance_yes_total": _parse_int(row.get("finanz-ja-tot", "")),
        "finance_no_total": _parse_int(row.get("finanz-nein-tot", "")),
    }
    return _emit(result, "swissvotes")


@mcp.tool(
    name="democracy_get_cantonal_results",
    annotations={
        "title": "Kantonsresultate zu einer Abstimmung (Swissvotes)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def democracy_get_cantonal_results(params: VoteDetailInput) -> str:
    """Gibt die Abstimmungsresultate aller 26 Kantone für eine eidgenössische Volksabstimmung zurück.

    <use_case>Kantonsvergleich und Ständemehr-Analyse zu einer Vorlage.</use_case>

    Inkl. Stimmberechtigte, abgegebene Stimmen, gültige Stimmen, Ja- und Nein-Stimmen,
    Ja-Prozent und ob der Kanton angenommen hat (für Ständemehr-Zählung).

    Args:
        params (VoteDetailInput): Enthält:
            - vote_number (str): Abstimmungsnummer (anr)

    Returns:
        str: JSON mit kantonalen Resultaten (26 Kantone), nationalem Total und
             Stimmenmehr/Ständemehr-Übersicht
    """
    try:
        rows = await _load_swissvotes()
    except Exception as e:
        return _handle_error(e)

    target = params.vote_number.strip()
    row = next(
        (r for r in rows
         if (r.get("\ufeffanr") or r.get("anr") or "").strip() == target),
        None,
    )
    if row is None:
        return json.dumps({"error": f"Abstimmung '{target}' nicht gefunden."}, ensure_ascii=False)

    cantonal: dict[str, dict] = {}
    for abbr, name in CANTON_NAMES.items():
        cantonal[abbr] = {
            "name": name,
            "eligible_voters": _parse_int(row.get(f"{abbr}-berecht", "")),
            "votes_cast": _parse_int(row.get(f"{abbr}-stimmen", "")),
            "turnout_percent": _parse_float(row.get(f"{abbr}-bet", "")),
            "valid_votes": _parse_int(row.get(f"{abbr}-gultig", "")),
            "yes_votes": _parse_int(row.get(f"{abbr}-ja", "")),
            "no_votes": _parse_int(row.get(f"{abbr}-nein", "")),
            "yes_percent": _parse_float(row.get(f"{abbr}-japroz", "")),
            "accepted": _parse_int(row.get(f"{abbr}-annahme", "")),
        }

    annahme_val = _parse_int(row.get("annahme", ""))
    result = {
        "vote_number": target,
        "date": row.get("datum", ""),
        "title_de": row.get("titel_kurz_d", ""),
        "legal_form": RECHTSFORM_MAP.get(row.get("rechtsform", ""), row.get("rechtsform", "")),
        "national_result": {
            "accepted": annahme_val,
            "yes_percent": _parse_float(row.get("volkja-proz", "")),
            "cantons_yes": _parse_int(row.get("kt-ja", "")),
            "cantons_no": _parse_int(row.get("kt-nein", "")),
        },
        "cantons": cantonal,
    }
    return _emit(result, "swissvotes")


class ListDatesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    year_from: int | None = Field(default=None, ge=1848, le=2100)
    year_to: int | None = Field(default=None, ge=1848, le=2100)
    limit: int = Field(default=50, ge=1, le=200)


@mcp.tool(
    name="democracy_list_vote_dates",
    annotations={
        "title": "Abstimmungsdaten auflisten (Swissvotes)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def democracy_list_vote_dates(params: ListDatesInput) -> str:
    """Listet alle eidgenössischen Abstimmungsdaten auf, an denen Vorlagen zur Abstimmung kamen.

    <use_case>Orientierung/Navigation vor einer Detailabfrage.</use_case>

    Gibt für jedes Datum die Anzahl Vorlagen zurück. Nützlich zur Orientierung
    vor einer Detailabfrage.

    Args:
        params (ListDatesInput): Optionaler Zeitraumfilter (year_from, year_to)

    Returns:
        str: JSON mit Liste von Abstimmungsdaten und Anzahl Vorlagen pro Datum
    """
    try:
        rows = await _load_swissvotes()
    except Exception as e:
        return _handle_error(e)

    dates: dict[str, int] = {}
    for row in rows:
        datum = row.get("datum", "")
        if not datum:
            continue
        year_str = datum[:4]
        try:
            yr = int(year_str)
        except ValueError:
            continue
        if params.year_from and yr < params.year_from:
            continue
        if params.year_to and yr > params.year_to:
            continue
        dates[datum] = dates.get(datum, 0) + 1

    sorted_dates = sorted(dates.items(), reverse=True)[: params.limit]
    return _emit(
        {"total_dates": len(dates), "dates": [{"date": d, "vote_count": c} for d, c in sorted_dates]},
        "swissvotes",
    )


# ===========================================================================
# PHASE 2 – opendata.swiss BFS Real-Time & Archive (No Auth)
# ===========================================================================


@mcp.tool(
    name="democracy_bfs_list_vote_dates",
    annotations={
        "title": "BFS-Abstimmungsdaten (opendata.swiss)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def democracy_bfs_list_vote_dates() -> str:
    """Listet alle verfügbaren eidgenössischen Abstimmungsdaten im BFS-Echtzeit-Webservice auf.

    <use_case>Einstieg in BFS-Echtzeit-/Archivdaten; liefert die Ressourcen-URLs für democracy_bfs_get_vote_results.</use_case>

    Die Daten werden am Abstimmungssonntag ab 12:00 Uhr laufend aktualisiert.
    Das Archiv enthält eidgenössische Abstimmungen seit 1981.

    Returns:
        str: JSON mit verfügbaren Abstimmungsdaten und deren Ressource-URLs
    """
    try:
        data = await _bfs_get(BFS_NATIONAL_PACKAGE)
    except Exception as e:
        return _handle_error(e)

    if not data.get("success"):
        return json.dumps({"error": "BFS-Paket nicht abrufbar."}, ensure_ascii=False)

    resources = data.get("result", {}).get("resources", [])
    dates_info = []
    for res in resources:
        name = res.get("name", {})
        name_de = name.get("de", "") if isinstance(name, dict) else str(name)
        dates_info.append({
            "name": name_de,
            "date": res.get("issued", ""),
            "url": res.get("download_url", res.get("url", "")),
            "format": res.get("format", ""),
        })

    dates_info.sort(key=lambda x: x.get("date", ""), reverse=True)
    return _emit({"total": len(dates_info), "vote_dates": dates_info[:50]}, "bfs")


class BfsVoteResultInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    result_url: str = Field(
        ...,
        description=(
            "Direkte JSON-URL eines Abstimmungsdatums aus democracy_bfs_list_vote_dates, "
            "z.B. 'https://www.bfs.admin.ch/bfsstatic/dam/assets/.../master'"
        ),
        min_length=10,
        max_length=500,
    )
    level: Literal["national", "cantonal", "municipality"] = Field(
        default="national",
        description=(
            "Aggregationsebene: 'national' (Schweiz gesamt), "
            "'cantonal' (alle Kantone), 'municipality' (Gemeinden)"
        ),
    )


@mcp.tool(
    name="democracy_bfs_get_vote_results",
    annotations={
        "title": "BFS-Abstimmungsresultate (opendata.swiss)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def democracy_bfs_get_vote_results(params: BfsVoteResultInput) -> str:
    """Ruft Echtzeit- oder Archiv-Abstimmungsresultate vom BFS ab.

    <use_case>Resultate auf Gemeinde-/Kantons-/Bundesebene, v.a. am Abstimmungssonntag.</use_case>

    Nutzt die direkte JSON-URL eines Abstimmungsdatums (aus democracy_bfs_list_vote_dates).
    Gibt Resultate pro Vorlage auf nationaler, kantonaler oder Gemeindeebene zurück.
    Am Abstimmungssonntag werden die Daten laufend aktualisiert.

    Args:
        params (BfsVoteResultInput): Enthält:
            - result_url (str): URL aus democracy_bfs_list_vote_dates
            - level (str): 'national', 'cantonal' oder 'municipality'

    Returns:
        str: JSON mit Abstimmungsresultaten pro Vorlage
    """
    try:
        data = await _bfs_get(params.result_url, resolve=True)
    except Exception as e:
        return _handle_error(e)

    votes_raw = data if isinstance(data, list) else data.get("schweiz", {}).get("vorlagen", [])
    if not votes_raw and isinstance(data, dict):
        votes_raw = data.get("vorlagen", [])

    level = params.level.lower()
    results = []

    def _extract_result(r: dict) -> dict:
        return {
            "eligible_voters": r.get("gueltigeLegitimationen"),
            "votes_cast": r.get("eingelegteStimmzettel"),
            "turnout": r.get("stimmbeteiligung"),
            "yes_votes": r.get("jaStimmenInProzent"),
            "yes_absolute": r.get("jaStimmenAbsolut"),
            "no_absolute": r.get("neinStimmenAbsolut"),
            "accepted": r.get("gebietAusgezaehlt"),
        }

    for vorlage in votes_raw:
        vorlage_id = vorlage.get("vorlagenId", "")
        title_info = vorlage.get("vorlagenTitel", [{}])
        title_de = next(
            (t.get("text", "") for t in title_info if t.get("langKey") == "de"), ""
        )
        entry: dict[str, Any] = {
            "vorlage_id": vorlage_id,
            "title_de": title_de,
            "accepted": vorlage.get("vorlageAngenommen"),
        }

        schweiz = vorlage.get("schweiz", {})
        if level == "national":
            entry["result"] = _extract_result(schweiz.get("resultat", {}))

        elif level == "cantonal":
            kantone = vorlage.get("kantone", [])
            entry["cantons"] = [
                {
                    "id": k.get("geoLevelId"),
                    "name": k.get("geoLevelname"),
                    "result": _extract_result(k.get("resultat", {})),
                    "accepted": k.get("annahmeBerechnet"),
                }
                for k in kantone
            ]

        elif level == "municipality":
            gemeinden = []
            for kt in vorlage.get("kantone", []):
                for gem in kt.get("gemeinden", []):
                    gemeinden.append({
                        "id": gem.get("geoLevelId"),
                        "name": gem.get("geoLevelname"),
                        "canton": kt.get("geoLevelname"),
                        "result": _extract_result(gem.get("resultat", {})),
                    })
            entry["municipalities"] = gemeinden

        results.append(entry)

    return _emit(
        {"level": level, "total_vorlagen": len(results), "results": results},
        "bfs",
    )


# ===========================================================================
# PHASE 3 – SRGSSR Polis (requires API key)
# ===========================================================================


class PolisListInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    year_from: int | None = Field(
        default=None, description="Startjahr (z.B. 1960), min. 1900", ge=1900, le=2100
    )
    year_to: int | None = Field(
        default=None, description="Endjahr (z.B. 2024)", ge=1900, le=2100
    )
    lang: Literal["de", "fr", "it", "rm", "en"] = Field(
        default="de",
        description="Sprache der Resultate: 'de', 'fr', 'it', 'rm', 'en'",
    )
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


@mcp.tool(
    name="democracy_polis_list_votations",
    annotations={
        "title": "Polis – Volksabstimmungen seit 1900 (SRGSSR, API-Key nötig)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def democracy_polis_list_votations(params: PolisListInput) -> str:
    """Ruft historische Volksabstimmungen aus dem SRGSSR Polis-System ab (seit 1900).

    <use_case>Historische Analysen mit Gemeinde-Granularität.</use_case>

    Polis enthält Resultate auf Gemeinde-Ebene, was für historische Analysen
    besonders wertvoll ist. Benötigt SRGSSR_CONSUMER_KEY und SRGSSR_CONSUMER_SECRET.

    Args:
        params (PolisListInput): Enthält:
            - year_from/year_to (int): Zeitraumfilter
            - lang (str): Sprache ('de', 'fr', 'it', 'rm', 'en')
            - limit/offset (int): Pagination

    Returns:
        str: JSON mit Polis-Abstimmungsliste oder Hinweis zur Registrierung
    """
    query_params: dict[str, Any] = {"lang": params.lang, "limit": params.limit}
    if params.year_from:
        query_params["yearFrom"] = params.year_from
    if params.year_to:
        query_params["yearTo"] = params.year_to

    try:
        data = await _polis_get("/votations", params=query_params)
    except Exception as e:
        return _handle_error(e)

    votations = data.get("votationList", data.get("votations", []))
    total = data.get("total", len(votations))

    lines = [
        f"# Polis Volksabstimmungen ({total} total)\n",
        f"{'Datum':<14} {'Titel':<60} {'Ja%':<8} {'Angenommen'}",
        "-" * 100,
    ]
    for v in votations:
        v_date = v.get("date", v.get("votationDate", "?"))
        v_title = (v.get("title") or v.get("name") or "")[:58]
        yes_pct = v.get("yesVotePercent") or v.get("percentageYes") or ""
        yes_pct_str = f"{yes_pct:.1f}%" if isinstance(yes_pct, (int, float)) else str(yes_pct)
        accepted = "✓" if v.get("accepted") or v.get("result") == "accepted" else "✗"
        lines.append(f"{v_date:<14} {v_title:<60} {yes_pct_str:<8} {accepted}")

    return "\n".join(lines)


class PolisVotationDetailInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    votation_id: str = Field(
        ...,
        description="Polis Abstimmungs-ID aus democracy_polis_list_votations",
        min_length=1,
        max_length=50,
    )
    lang: Literal["de", "fr", "it", "rm", "en"] = Field(
        default="de", description="Sprache: 'de', 'fr', 'it', 'rm', 'en'"
    )
    include_municipalities: bool = Field(
        default=False,
        description="Wenn True: Gemeinde-Resultate einschliessen (grössere Antwort)",
    )


@mcp.tool(
    name="democracy_polis_get_votation_detail",
    annotations={
        "title": "Polis – Abstimmungsdetail mit Gemeinderesultaten (SRGSSR)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def democracy_polis_get_votation_detail(params: PolisVotationDetailInput) -> str:
    """Gibt detaillierte Polis-Daten zu einer Volksabstimmung zurück.

    <use_case>Gemeindescharfe Detailanalyse einer historischen Abstimmung.</use_case>

    Optional mit Gemeinde-Resultaten – ideal für Fragen wie
    «Wie hat die Stadt Zürich bei der AHV-Reform abgestimmt?».
    Benötigt SRGSSR_CONSUMER_KEY und SRGSSR_CONSUMER_SECRET.

    Args:
        params (PolisVotationDetailInput): Enthält:
            - votation_id (str): Polis-ID aus democracy_polis_list_votations
            - lang (str): Ausgabesprache
            - include_municipalities (bool): Gemeinderesultate einschliessen

    Returns:
        str: JSON mit Polis-Abstimmungsdetails, kantonalen und optionalen Gemeindedaten
    """
    try:
        data = await _polis_get(f"/votations/{params.votation_id}", params={"lang": params.lang})
    except Exception as e:
        return _handle_error(e)

    if not params.include_municipalities:
        # Remove municipality details to keep response manageable
        for canton in data.get("cantons", []):
            canton.pop("municipalities", None)

    return _emit(data, "polis")


class PolisElectionInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    year_from: int | None = Field(default=None, ge=1900, le=2100)
    year_to: int | None = Field(default=None, ge=1900, le=2100)
    lang: Literal["de", "fr", "it", "rm", "en"] = Field(default="de")
    limit: int = Field(default=20, ge=1, le=100)


@mcp.tool(
    name="democracy_polis_list_elections",
    annotations={
        "title": "Polis – Wahlen seit 1900 (SRGSSR, API-Key nötig)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def democracy_polis_list_elections(params: PolisElectionInput) -> str:
    """Ruft historische Wahlen (National-/Ständerat, Regierungsrat) aus Polis ab.

    <use_case>Wahlanalysen (Kandidierende, Parteistimmen) seit 1900.</use_case>

    Polis enthält Wahlresultate seit 1900, inkl. Kandidatinnen- und Parteistimmen.
    Benötigt SRGSSR_CONSUMER_KEY und SRGSSR_CONSUMER_SECRET.

    Args:
        params (PolisElectionInput): Enthält:
            - year_from/year_to (int): Zeitraumfilter
            - lang (str): Ausgabesprache
            - limit (int): Max. Resultate

    Returns:
        str: JSON mit Wahlliste oder Hinweis zur Registrierung
    """
    query_params: dict[str, Any] = {"lang": params.lang, "limit": params.limit}
    if params.year_from:
        query_params["yearFrom"] = params.year_from
    if params.year_to:
        query_params["yearTo"] = params.year_to

    try:
        data = await _polis_get("/elections", params=query_params)
    except Exception as e:
        return _handle_error(e)

    elections = data.get("electionList", data.get("elections", []))
    total = data.get("total", len(elections))

    lines = [
        f"# Polis Wahlen ({total} total)\n",
        f"{'Datum':<14} {'Titel':<70} {'Typ'}",
        "-" * 100,
    ]
    for el in elections:
        el_date = el.get("date", el.get("electionDate", "?"))
        el_title = (el.get("title") or el.get("name") or "")[:68]
        el_type = el.get("type", el.get("electionType", ""))
        lines.append(f"{el_date:<14} {el_title:<70} {el_type}")

    return "\n".join(lines)


# ===========================================================================
# Transport entry point
# ===========================================================================

if __name__ == "__main__":
    if settings.mcp_transport == "streamable_http":
        # Bind to loopback by default (audit finding SEC-016: NeighborJack).
        # Set MCP_HOST=0.0.0.0 explicitly only inside a container/cloud deploy.
        host = settings.mcp_host
        port = settings.mcp_port
        if host == "0.0.0.0":  # noqa: S104 — opt-in, container-only
            log.warning(
                "binding_all_interfaces",
                host=host,
                hint="Nur in abgesicherter Container-/Cloud-Umgebung verwenden, "
                "nicht auf einem lokalen Entwicklungsrechner.",
            )
        mcp.run(transport="streamable_http", host=host, port=port)
    else:
        mcp.run()
