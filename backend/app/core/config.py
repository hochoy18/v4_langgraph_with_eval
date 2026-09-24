"""应用配置 — pydantic-settings 单例。

通过 .env 注入。所有运行时可调参数集中在此。
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- 应用 ----
    app_env: Literal["development", "staging", "production"] = "development"
    app_port: int = 8000
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # ---- 外部基础设施 ----
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/deep_research"
    redis_url: str = "redis://localhost:6379/0"
    milvus_uri: str = "http://localhost:19530"

    # ---- Langfuse ----
    langfuse_host: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""

    # ---- LLM ----
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    # OpenAI-compatible provider base URL. 默认 DeepSeek (国内可用、价格低)；
    # 官方 OpenAI 改成 https://api.openai.com/v1 即可。
    openai_base_url: str = "https://api.deepseek.com"
    # 节点级模型（Phase 7 A/B 用）；默认 OpenAI，可随时改 MODEL_<NODE>=anthropic:... 切回
    model_main_plan: str = "openai:gpt-4.1"
    model_research_dispatch: str = "openai:gpt-4.1-mini"
    model_research_coverage_check: str = "openai:gpt-4.1"
    model_sq_extract: str = "openai:gpt-4.1"
    model_sq_reflect: str = "openai:gpt-4.1-mini"
    model_write_outline: str = "openai:gpt-4.1-mini"
    model_write_sections: str = "openai:gpt-4.1"
    model_write_revise: str = "openai:gpt-4.1"
    model_write_summarize: str = "openai:gpt-4.1-mini"
    model_judge_citation: str = "openai:gpt-4.1"

    # ---- 检索 ----
    search_provider: Literal["tavily", "bailian_mcp"] = "tavily"
    tavily_api_key: str = ""
    bailian_mcp_url: str = ""
    bailian_mcp_token: str = ""

    # ---- 预算（D15 / D25） ----
    session_max_tokens_input: int = 100_000
    session_max_tokens_output: int = 5_000
    session_max_wall_time_seconds: int = 600
    session_max_cost_usd: float = 2.0
    research_max_iterations: int = 2
    sq_max_sub_iterations: int = 3

    # ---- 覆盖率（D16） ----
    min_facts_per_sq: int = 3
    min_critical_facts: int = 5

    # ---- 限流（D29） ----
    rate_limit_user_concurrent: int = 5
    rate_limit_user_hour: int = 20
    rate_limit_user_day: int = 100
    rate_limit_tenant_concurrent: int = 20
    rate_limit_tenant_hour: int = 200
    rate_limit_tenant_day: int = 1000
    rate_limit_global_concurrent: int = 50

    # ---- JWT（D10） ----
    jwt_secret: str = "REPLACE-ME-IN-PRODUCTION"
    jwt_access_ttl_minutes: int = 30
    jwt_refresh_ttl_days: int = 7


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()