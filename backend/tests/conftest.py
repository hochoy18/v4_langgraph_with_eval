"""Pytest configuration and fixtures for backend tests."""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient


# Env vars that, if set in the developer's .env, would make tests try to
# hit real infrastructure (Langfuse health check, Postgres, etc.). Tests
# explicitly mock these as needed; the autouse fixture clears them so
# tests don't accidentally depend on real services.
_TEST_ENV_DEFAULTS = {
    "LANGFUSE_HOST": "",           # → _check_langfuse returns "skip"
    "DATABASE_URL": "",             # → no Postgres connection attempted
    "REDIS_URL": "redis://localhost:6379/0",  # mocked per-test as needed
    "OPENAI_API_KEY": "sk-test-not-used",
    "ANTHROPIC_API_KEY": "sk-ant-test-not-used",
    "TAVILY_API_KEY": "tvly-test-not-used",
    "JWT_SECRET": "test-secret-" + "x" * 48,
}


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch):
    """Pin env vars to test-safe defaults before each test, then reset caches.

    `monkeypatch.setenv` with `raising=False` ignores missing keys.
    """
    for k, v in _TEST_ENV_DEFAULTS.items():
        monkeypatch.setenv(k, v)

    from app.core.config import get_settings
    from app.core.llm import clear_cache as clear_llm_cache

    get_settings.cache_clear()
    clear_llm_cache()
    yield
    get_settings.cache_clear()
    clear_llm_cache()


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient wrapping the app (no lifespan startup side-effects)."""
    from app.main import app

    with TestClient(app) as c:
        yield c