"""FastAPI 应用入口。

启动时挂载：
  - CORS（dev 默认 localhost:5173）
  - 结构化 JSON 日志
  - /healthz（liveness — 进程在跑）
  - /readyz（readiness — DB / Redis / Langfuse 可达性）
  - API 路由（占位，Phase 1+ 接入）

Phase 0 (S0-T1) 仅交付 /healthz + /readyz，其余路由在后续 Phase 接入。
"""
from __future__ import annotations

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings, settings
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动 / 关闭钩子。"""
    configure_logging()
    s = get_settings()
    logger.info(
        "app.startup",
        env=s.app_env,
        port=s.app_port,
    )
    yield
    logger.info("app.shutdown")


app = FastAPI(
    title="Deep Research API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS（dev 默认放行 localhost:5173）
_cors_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- 健康检查 -----


@app.get("/healthz", tags=["health"])
async def healthz() -> dict:
    """Liveness — 进程是否在跑。无依赖检查。"""
    return {"status": "ok"}


async def _check_postgres() -> str:
    """Probe Postgres。Phase 1 之前 app.core.db 不存在，跳过。"""
    try:
        from sqlalchemy import text  # noqa: F401

        from app.core.db import async_session  # type: ignore

        async with async_session() as session:  # type: ignore
            await session.execute(text("SELECT 1"))  # type: ignore
        return "ok"
    except ImportError:
        return "skip (Phase 1 not yet implemented)"
    except Exception as e:
        return f"fail: {type(e).__name__}"


async def _check_redis() -> str:
    """Probe Redis via PING。"""
    s = get_settings()
    try:
        import redis.asyncio as redis_async

        r = redis_async.from_url(s.redis_url)
        try:
            await r.ping()
        finally:
            await r.aclose()
        return "ok"
    except Exception as e:
        return f"fail: {type(e).__name__}"


async def _check_langfuse() -> str:
    """Probe Langfuse public health endpoint."""
    s = get_settings()
    if not s.langfuse_host:
        return "skip (LANGFUSE_HOST not configured)"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{s.langfuse_host.rstrip('/')}/api/public/health")
            if resp.status_code == 200:
                return "ok"
            return f"fail: http {resp.status_code}"
    except Exception as e:
        return f"fail: {type(e).__name__}"


@app.get("/readyz", tags=["health"])
async def readyz(response: Response) -> dict:
    """Readiness — Postgres / Redis / Langfuse 可达性。

    任何依赖 fail（不是 skip）→ 503 + 整体 degraded。
    全部 ok 或 skip → 200 + ok。
    """
    pg = await _check_postgres()
    rd = await _check_redis()
    lf = await _check_langfuse()

    checks = {"postgres": pg, "redis": rd, "langfuse": lf}

    # "fail:" 前缀视为失败；"ok" 与 "skip" 视为通过
    def is_fail(status: str) -> bool:
        return status.startswith("fail")

    overall_ok = not any(is_fail(c) for c in checks.values())

    if not overall_ok:
        response.status_code = 503

    return {
        "status": "ok" if overall_ok else "degraded",
        "checks": checks,
    }


# ----- 路由占位（后续 Phase 接入） -----


@app.get("/", tags=["root"])
async def root() -> dict:
    return {
        "name": "deep-research-backend",
        "version": "0.1.0",
        "phase": 0,
        "docs": "/docs",
    }