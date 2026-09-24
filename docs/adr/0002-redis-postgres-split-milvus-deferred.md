# ADR-0002: Redis + Postgres + Milvus 全部外部部署，本仓库 compose 不打包

## Status

Accepted (Phase 0)

## Context

`docker-compose.yml` 默认会自带依赖服务（Postgres / Redis / Langfuse 等），便于"一键起栈"。本仓库的现状是：

- 用户已有 Postgres 16+ / Redis 7+ / Milvus 2.5 / Langfuse 的部署
- 我们要在 GitHub 上开源 v1，让外部用户 fork 后接到自己的 infra
- 本仓库只承担"应用代码 + 编排"

## Decision

`docker-compose.yml` **仅打包应用**（backend / worker / frontend）。基础设施通过 `.env` 中的连接串 / API key 接入。

具体来说：

| 资源 | 部署方 | 连接方式 |
|---|---|---|
| Postgres 16+ | 外部 | `DATABASE_URL` |
| Redis 7+ | 外部 | `REDIS_URL` |
| Milvus 2.5 | 外部 | `MILVUS_URI`（v1 暂不连接） |
| Langfuse | 外部 | `LANGFUSE_HOST` / `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` |
| Tavily API | SaaS | `TAVILY_API_KEY` |
| 阿里云百炼 MCP | SaaS | `BAILIAN_MCP_URL` / `BAILIAN_MCP_TOKEN` |
| LLM providers | SaaS | `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` |

## Consequences

- ✅ 与生产配置零 drift（生产用啥，本地连啥）
- ✅ 镜像体积小，CI/CD 缓存友好
- ✅ fork 用户可以接到自己的 infra
- ⚠️ 新贡献者需要先自己起 infra 才能 `docker-compose up`
- ⚠️ `docker-compose.yml` 不是"一键起栈"，需在 README 中明确这一点

## Alternatives

- **`docker-compose.yml` 完整起 Postgres/Redis**：体验好，但与生产 drift、需要维护 docker 配置、镜像大
- **用云托管服务（Vercel / Neon / Upstash 等）**：可以但锁定单一云，违背"infra 外部"原则

## References

- Plan: D7（持久化分库）、D12（部署）、D18（Milvus 推迟）
- 计划文档：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`