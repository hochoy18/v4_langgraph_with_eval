"""Tests for app/core/llm.py — node-to-model dispatch + base_url plumbing."""
from __future__ import annotations

from unittest.mock import patch

import pytest


def test_parse_model_string_anthropic():
    from app.core.llm import _parse_model_string

    assert _parse_model_string("anthropic:claude-sonnet-5") == ("anthropic", "claude-sonnet-5")
    assert _parse_model_string("anthropic:claude-haiku-4-5") == ("anthropic", "claude-haiku-4-5")


def test_parse_model_string_openai():
    from app.core.llm import _parse_model_string

    assert _parse_model_string("openai:gpt-4.1") == ("openai", "gpt-4.1")
    assert _parse_model_string("openai:gpt-4.1-mini") == ("openai", "gpt-4.1-mini")
    assert _parse_model_string("openai:deepseek-chat") == ("openai", "deepseek-chat")


def test_parse_model_string_no_colon_defaults_to_anthropic():
    """Bare model string (legacy) → anthropic."""
    from app.core.llm import _parse_model_string

    assert _parse_model_string("claude-sonnet-5") == ("anthropic", "claude-sonnet-5")


def test_build_chat_model_passes_base_url_for_openai(monkeypatch):
    """When provider=openai and base_url is set, init_chat_model receives base_url."""
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    from app.core.config import get_settings
    from app.core.llm import _build_chat_model

    get_settings.cache_clear()
    try:
        # Patch init_chat_model so we can inspect the kwargs without constructing
        # a real ChatOpenAI instance
        with patch("app.core.llm.init_chat_model") as mock_init:
            mock_init.return_value = object()
            _build_chat_model("main_plan")  # default is openai:gpt-4.1
            mock_init.assert_called_once()
            kwargs = mock_init.call_args.kwargs
            assert kwargs["model"] == "gpt-4.1"
            assert kwargs["model_provider"] == "openai"
            assert kwargs["base_url"] == "https://api.deepseek.com"
    finally:
        get_settings.cache_clear()


def test_build_chat_model_no_base_url_for_anthropic(monkeypatch):
    """Anthropic path does not receive base_url (only relevant for openai)."""
    monkeypatch.setenv("MODEL_MAIN_PLAN", "anthropic:claude-sonnet-5")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "")  # ensure empty

    from app.core.config import get_settings
    from app.core.llm import _build_chat_model

    get_settings.cache_clear()
    try:
        with patch("app.core.llm.init_chat_model") as mock_init:
            mock_init.return_value = object()
            _build_chat_model("main_plan")
            kwargs = mock_init.call_args.kwargs
            assert kwargs["model"] == "claude-sonnet-5"
            assert kwargs["model_provider"] == "anthropic"
            assert "base_url" not in kwargs
    finally:
        get_settings.cache_clear()


def test_build_chat_model_openai_without_base_url_uses_default(monkeypatch):
    """If OPENAI_BASE_URL is empty, init_chat_model uses langchain's default (OpenAI official)."""
    monkeypatch.setenv("OPENAI_BASE_URL", "")

    from app.core.config import get_settings
    from app.core.llm import _build_chat_model

    get_settings.cache_clear()
    try:
        with patch("app.core.llm.init_chat_model") as mock_init:
            mock_init.return_value = object()
            _build_chat_model("sq_extract")  # openai:gpt-4.1 default
            kwargs = mock_init.call_args.kwargs
            assert kwargs["model"] == "gpt-4.1"
            assert kwargs["model_provider"] == "openai"
            assert "base_url" not in kwargs
    finally:
        get_settings.cache_clear()


def test_clear_cache_resets_models(monkeypatch):
    """After clear_cache(), next get_model builds a fresh instance."""
    monkeypatch.setenv("MODEL_MAIN_PLAN", "openai:gpt-4.1-mini")

    from app.core.config import get_settings
    from app.core.llm import _build_chat_model, clear_cache

    get_settings.cache_clear()
    try:
        with patch("app.core.llm.init_chat_model") as mock_init:
            mock_init.return_value = object()
            _build_chat_model("main_plan")
            first_kwargs = mock_init.call_args.kwargs
            assert first_kwargs["model"] == "gpt-4.1-mini"

            clear_cache()

            # After clearing, next call rebuilds
            _build_chat_model("main_plan")
            assert mock_init.call_count == 2
    finally:
        get_settings.cache_clear()