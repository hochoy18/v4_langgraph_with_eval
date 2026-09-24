"""FastAPI 应用入口。

启动时挂载：
  - CORS（dev 默认 localhost:5173）
  - 结构化 JSON 日志
  - /healthz（liveness）
  - /readyz（DB / Redis / Langfuse / search provider 可达性）
  - API 路由（占位，Phase 1+ 接入）

Phase 0 仅交付 /healthz + /readyz，其余路由在后续 Phase 接入。
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动 / 关闭钩子。"""
    configure_logging()
    logger.info(
        "app.startup",
        env=settings.app_env,
        port=settings.app_port,
    )
    yield
    logger.info("app.shutdown")


app = FastAPI(
    title="Deep Research API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS（dev 默认放行 localhost:5173）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- 健康检查 -----


@app.get("/healthz", tags=["health"])
async def healthz() -> dict:
    """Liveness — 进程是否在跑。无依赖检查。"""
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
async def readyz(response: Response) -> dict:
    """Readiness — DB / Redis / Langfuse / 选定 search provider 是否可达。

    任何依赖不可达时返回 503。Phase 0 暂只检查 DB 与 Redis；Langfuse 与
    search provider 检查在 Phase 4 / Phase 0a 后接入。
    """
    checks: dict[str, str] = {}
    overall_ok = True

    # ---- Postgres（Phase 1 后才有 app/core/db.py） ----
    try:
        from sqlalchemy import text

        from app.core.db import async_session  # noqa: F401

        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except ImportError:
        checks["postgres"] = "skip (Phase 1 not yet implemented)"
    except Exception as e:
        checks["postgres"] = f"fail: {type(e).__name__}"
        overall_ok = False

    # ---- Redis ----
    try:
        import redis.asyncio as redis_async

        r = redis_async.from_url(settings.redis_url)
        await r.ping()
        await r.aclose()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"fail: {type(e).__name__}"
        overall_ok = False

    if not overall_ok:
        response.status_code = 503
    return {"status": "ok" if overall_ok else "degraded", "checks": checks}


# ----- 路由占位（后续 Phase 接入） -----


@app.get("/", tags=["root"])
async def root() -> dict:
    return {
        "name": "deep-research-backend",
        "version": "0.1.0",
        "phase": 0,
        "docs": "/docs",
    }