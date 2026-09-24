"""Pytest configuration and fixtures for backend tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _reset_caches():
    """Reset module-level caches between tests so env-var-driven config + LRU
    caches don't leak state across tests."""
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
    # Import inside fixture so settings are loaded after env is in place
    from app.main import app

    with TestClient(app) as c:
        yield c