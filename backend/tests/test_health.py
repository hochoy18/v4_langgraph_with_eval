"""Tests for /healthz and /readyz (S0-T1 acceptance criteria).

These verify:
- /healthz always returns 200 (liveness, no dep check)
- /readyz returns 200 when all infra is reachable
- /readyz returns 503 when any infra fails
- Langfuse check is performed
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


def test_healthz_returns_200(client):
    """Liveness — always 200 regardless of dependencies."""
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_readyz_returns_200_when_all_infra_ok(client, monkeypatch):
    """All checks ok → 200 + status='ok'."""
    # Langfuse is not configured in default test env, so 'skip' is expected
    # Postgres app.core.db doesn't exist yet (Phase 1), so 'skip'
    # Redis: needs to be pingable — but no real Redis available.
    # We mock Redis to return ok.
    fake_redis = AsyncMock()
    fake_redis.ping = AsyncMock(return_value=True)
    fake_redis.aclose = AsyncMock(return_value=None)

    with patch("redis.asyncio.from_url", return_value=fake_redis):
        resp = client.get("/readyz")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["checks"]["redis"] == "ok"


def test_readyz_returns_503_when_redis_fails(client):
    """Redis unreachable → 503 + status='degraded'."""
    # Mock redis to raise ConnectionError
    fake_redis = AsyncMock()
    fake_redis.ping = AsyncMock(side_effect=ConnectionError("simulated redis down"))
    fake_redis.aclose = AsyncMock(return_value=None)

    with patch("redis.asyncio.from_url", return_value=fake_redis):
        resp = client.get("/readyz")

    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["redis"].startswith("fail:")


def test_readyz_returns_503_when_langfuse_unreachable(client, monkeypatch):
    """Langfuse configured but unreachable → 503."""
    # Configure langfuse host
    monkeypatch.setenv("LANGFUSE_HOST", "http://nonexistent.langfuse.example.com")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")

    # Reload settings (lru_cache)
    from app.core.config import get_settings

    get_settings.cache_clear()

    # Patch the Langfuse check function directly
    async def fake_langfuse_check_fail():
        return "fail: simulated"

    with patch("app.main._check_langfuse", fake_langfuse_check_fail):
        fake_redis = AsyncMock()
        fake_redis.ping = AsyncMock(return_value=True)
        fake_redis.aclose = AsyncMock(return_value=None)

        with patch("redis.asyncio.from_url", return_value=fake_redis):
            resp = client.get("/readyz")

    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["langfuse"].startswith("fail:")
    get_settings.cache_clear()


def test_readyz_postgres_skip_phase0(client):
    """Phase 0 — app.core.db doesn't exist → postgres='skip'."""
    fake_redis = AsyncMock()
    fake_redis.ping = AsyncMock(return_value=True)
    fake_redis.aclose = AsyncMock(return_value=None)

    with patch("redis.asyncio.from_url", return_value=fake_redis):
        resp = client.get("/readyz")

    body = resp.json()
    # Either ok (skip is treated as pass) or skip message
    assert body["checks"]["postgres"].startswith("skip") or body["checks"]["postgres"] == "ok"


def test_readyz_langfuse_skip_when_unset(client):
    """Langfuse not configured (empty LANGFUSE_HOST) → 'skip'."""
    from app.core.config import get_settings

    get_settings.cache_clear()
    # Ensure LANGFUSE_HOST is empty
    monkeypatch_value = "LANGFUSE_HOST"

    import os

    old = os.environ.get("LANGFUSE_HOST", "")
    os.environ["LANGFUSE_HOST"] = ""
    try:
        get_settings.cache_clear()

        fake_redis = AsyncMock()
        fake_redis.ping = AsyncMock(return_value=True)
        fake_redis.aclose = AsyncMock(return_value=None)

        with patch("redis.asyncio.from_url", return_value=fake_redis):
            resp = client.get("/readyz")

        body = resp.json()
        assert body["checks"]["langfuse"].startswith("skip")
    finally:
        os.environ["LANGFUSE_HOST"] = old
        get_settings.cache_clear()


def test_root(client):
    """Root endpoint exposes build metadata."""
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "deep-research-backend"
    assert "phase" in body