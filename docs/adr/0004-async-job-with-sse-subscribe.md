# ADR-0004: 异步任务（job_id + SSE 订阅）而非同步 SSE

## Status

Accepted (Phase 0)

## Context

LangGraph 的 `graph.astream()` / `graph.ainvoke()` 都可以用 SSE 把 token 实时推到前端。两种风格：

- **同步 SSE**（一个 HTTP 连接保持打开直到整个图跑完）
- **异步 job_id + SSE 订阅**（HTTP 立即返回 `job_id`，SSE 仅订阅事件流）

同步 SSE 在 LangGraph 官方 demo 与社区示例中更常见。异步风格需要 Arq / Celery 之类的任务队列配合。

## Decision

采用 **异步任务 + SSE 订阅**：

- `POST /api/research` 立即返回 `job_id`
- 后端 Arq worker 跑 LangGraph，事件通过 Redis Streams 持久化
- `GET /api/research/{id}/events` 用 `XREAD BLOCK` 订阅，支持 `Last-Event-ID` 重放
- 前端断线后可重新订阅，恢复丢失事件

## Consequences

- ✅ 后端 worker 可独立扩缩容（worker 进程可重启不丢 job）
- ✅ State 由 Postgres checkpointer 持久化，worker 崩溃后 Arq 重启自动恢复
- ✅ 前端断网 / SSE 代理超时 / 用户关闭浏览器都不丢事件（Redis Streams 重放）
- ✅ 端到端延迟可达数分钟（D28 p95 ≤ 6min），远超同步 SSE 代理超时（典型 60s）
- ⚠️ 增加 worker 进程部署复杂度（Docker / K8s 多一份 service）
- ⚠️ 比同步 SSE 多一层（Redis Streams）

## Consequences（量化）

- D28 p95 端到端 6 分钟 → 必须异步
- D22 resume 走 `Command(resume=...)` → 必须 checkpointer → 必须 Postgres → 必须 worker
- D15 双层预算在 worker 内做，崩溃可重启恢复

## Alternatives

- **同步 SSE**：简洁但代理超时 / 崩溃即失败；不满足 D28 p95 6min
- **Celery + SSE**：等价方案但 Celery 配置比 Arq 重
- **WebSocket**：双工通道但企业网络 / FW 兼容性差

## References

- Plan: D17（执行模式）、D22（异步 + SSE）、D28（性能目标）
- 计划文档：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`