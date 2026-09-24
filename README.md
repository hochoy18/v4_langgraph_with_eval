# Deep Research 产品 (v4)

企业级 deep research 产品 — LangGraph + FastAPI + Arq + Redis Streams + Langfuse。

## 5 分钟快速启动

### 前提

- Python 3.11+
- Node 20+
- Docker + docker-compose
- 外部已就绪：**Postgres 16+ / Redis 7+ / Langfuse**
- （可选）Milvus 2.5、阿里云百炼 MCP

### 步骤

```bash
# 1. 复制环境变量模板
cp .env.example .env
# 编辑 .env，填入连接串与 API key

# 2. 启动应用栈
docker-compose up -d

# 3. 等后端 /readyz 就绪
curl -fsS http://localhost:8000/readyz

# 4. 初始化 fixtures（测试用户 / Langfuse prompts / ground truth）
docker-compose exec backend python -m app.fixtures.bootstrap --all

# 5. 登录种子账号（密码在 fixtures bootstrap 输出中）
# 访问前端 http://localhost:5173
```

### 目录导览

```
backend/       FastAPI + LangGraph + Arq worker
frontend/      Vite + React SPA
tests/         （Phase 1+ 填充）
docs/
├── CONTEXT.md       # Phase 0a 从 plan 导入
├── agents/          # Claude Code agent 配置（已就绪）
└── adr/             # Phase 0a 批量生成 10 个 ADR
```

## 详细文档

- 实施计划：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`
- 运维手册：见 `docs/runbook.md`（Phase 8 收尾时生成）
- 架构决策：见 `docs/adr/`
- 领域术语表：见 `docs/CONTEXT.md`（Phase 0a 填充）

## 许可证

内部使用