"""Pytest configuration and fixtures for backend tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient wrapping the app (no lifespan startup side-effects)."""
    # Import inside fixture so settings are loaded after env is in place
    from app.main import app

    with TestClient(app) as c:
        yield c