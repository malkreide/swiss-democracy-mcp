"""Inbound Host/Origin validation on the HTTP transport (audit SEC-005).

The SDK leaves DNS-rebinding protection off while ``transport_security`` is
unset. This server never set it, so there was no Host check at all. These tests
pin the new behaviour and fail if the protection is ever dropped again.
"""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from swiss_democracy_mcp.server import Settings, build_transport_security, mcp

_INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1"},
    },
}
_HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}


def test_loopback_bind_enables_protection():
    sec = build_transport_security("127.0.0.1", 8000)
    assert sec is not None
    assert sec.enable_dns_rebinding_protection is True
    assert "127.0.0.1:8000" in sec.allowed_hosts


def test_non_local_bind_without_allowlist_stays_off(monkeypatch):
    """0.0.0.0 with no MCP_ALLOWED_HOSTS: the reachable name is unknowable.

    Guessing would reject every real request, so the protection stays off
    (unchanged behaviour) and the caller warns.
    """
    monkeypatch.setattr("swiss_democracy_mcp.server.settings", Settings(mcp_allowed_hosts=""))
    assert build_transport_security("0.0.0.0", 8000) is None


def test_non_local_bind_with_allowlist_enables_protection(monkeypatch):
    monkeypatch.setattr(
        "swiss_democracy_mcp.server.settings",
        Settings(mcp_allowed_hosts="mcp.example.ch,mcp.example.ch:443"),
    )
    sec = build_transport_security("0.0.0.0", 8000)
    assert sec is not None
    assert "mcp.example.ch" in sec.allowed_hosts
    assert "127.0.0.1:8000" in sec.allowed_hosts  # health checks keep working


def test_wildcard_cors_is_not_copied_into_allowed_origins(monkeypatch):
    """"*" is matched literally by the SDK, so copying it in would be a no-op
    that reads like a wildcard. It must not appear."""
    monkeypatch.setattr("swiss_democracy_mcp.server.settings", Settings(mcp_cors_origins="*"))
    sec = build_transport_security("127.0.0.1", 8000)
    assert "*" not in sec.allowed_origins


def test_explicit_cors_origin_passes_transport_check(monkeypatch):
    monkeypatch.setattr(
        "swiss_democracy_mcp.server.settings",
        Settings(mcp_cors_origins="https://claude.ai"),
    )
    sec = build_transport_security("127.0.0.1", 8000)
    assert "https://claude.ai" in sec.allowed_origins


def _post_with_host(host_header: str):
    # mcp 2.x: transport_security is a per-app kwarg, not a setting.
    with TestClient(
        mcp.streamable_http_app(transport_security=build_transport_security("127.0.0.1", 8000))
    ) as client:
        return client.post("/mcp", headers={"Host": host_header, **_HEADERS}, json=_INIT)


def test_allowed_host_is_served():
    assert _post_with_host("127.0.0.1:8000").status_code == 200


def test_foreign_host_is_rejected():
    assert _post_with_host("evil.example.com").status_code == 421


def test_right_host_wrong_port_is_rejected():
    """The load-bearing case.

    Rejecting ``evil.example.com`` alone proves little — a fallback localhost
    policy rejects that too. Only right-hostname/wrong-port distinguishes a
    port-precise allow-list from no policy, and it fails the moment
    ``transport_security`` stops being set.
    """
    assert _post_with_host("127.0.0.1:9999").status_code == 421


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "::1"])
def test_all_loopback_forms_are_local(host):
    assert build_transport_security(host, 8000) is not None
