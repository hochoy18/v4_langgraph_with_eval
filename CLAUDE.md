# CLAUDE.md

本文件是 Claude Code 在此仓库的运行时配置。

## 项目概要

Deep Research 产品 — LangGraph + FastAPI + Arq + Redis Streams + Langfuse 实现的企业级 deep research 工具。完整实施计划见 `/Users/cai.he/.claude/plans/deep-research-humming-gray.md`。

技术栈：Python 3.11 / LangGraph 最新版 / FastAPI / Vite + React / Redis Streams / Postgres 16+ / Langfuse（外部）。

## Agent skills

### Issue tracker

GitHub Issues — 用 `gh` CLI 操作。完整约定见 `docs/agents/issue-tracker.md`。

### Domain docs

Single-context — 仓库根的 `CONTEXT.md` + `docs/adr/`。完整约定见 `docs/agents/domain.md`。

---

## 项目工作约定（v1 实施期）

### 构建顺序

按 `plan` 的 10 个 Phase 0–0a–1–2–3–4–5–6–7–8 顺序实施，每个阶段结束栈必须能启动且端到端验证。

### 关键技术约束

1. **基础设施外部**（D7/D12）：docker-compose 不打包 Postgres/Redis/Milvus/Langfuse；只启动 backend + worker + frontend 三个应用。
2. **决策编号**：所有功能模块引用 `D1–D29` 决策号，详见 plan 文档"已收敛的决策"小节。
3. **LangGraph 子图对称**：research 与 write 都是显式子图（research 4 + sq.workflow 4 节点；write 5 步流水线）。
4. **引用模型**：LLM 写正文用 `[cite:url-xxx]` 占位符，write.assemble 程序化替换为 `[n]`。
5. **SSE 用 Redis Streams**：支持 `Last-Event-ID` 重放。
6. **JWT 双 token**：access 30 min + refresh 7 天，httpOnly + Secure + SameSite=Strict cookie。
7. **多租户隔离**：SQLAlchemy `before_compile` 钩子强制 `WHERE tenant_id`。
8. **可观测性**：Langfuse callback handler 挂到所有 LLM 调用；eval runner 写 Langfuse scores。

### 文档同步

- 修改领域概念时同步更新 `CONTEXT.md`（v1 落地后生成）
- 重大架构变更落 ADR 到 `docs/adr/`

## 常用命令

```bash
# 后端本地开发
cd backend && uv pip install --system && uvicorn app.main:app --reload

# 跑 fixtures（测试用户 / Langfuse prompts / ground truth）
python -m app.fixtures.bootstrap --all

# 跑端到端 smoke（前提：外部 infra 可达）
# 见 plan 文档"验证"小节
```