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
# 1. 跑一次性 wizard 抓取 key + 启动本地 infra
bash scripts/setup.sh

# 2. 启动应用栈（仅 backend / worker / frontend；infra 已外部就绪）
docker-compose up -d

# 3. 等后端 /readyz 就绪
curl -fsS http://localhost:8000/readyz

# 4. 初始化 fixtures（测试用户 / Langfuse prompts / ground truth）
docker-compose exec backend python -m app.fixtures.bootstrap --all

# 5. 登录种子账号（密码在 fixtures bootstrap 输出中）
# 访问前端 http://localhost:5173
```

> **关于 `scripts/setup.sh`**：交互式 wizard，引导你逐项抓 Langfuse / Anthropic / Tavily 等 key 并写入 `.env`，还提供 Postgres + Redis 的本地 `docker run` 命令。幂等 — 跑多次也安全（已存在的值不会被覆盖）。详见脚本内 stage 说明。

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

## 本地开发（不用 Docker）

```bash
# 1. 装依赖
make install

# 2. 配 backend/.env（一次性，已通过 wizard 引导）
bash scripts/setup.sh

# 3. 起 Postgres + Redis（任选其一：docker run / 本地服务 / brew）
#    wizard Stage 1 提供 docker run 命令

# 4. 三个 terminal 分别跑（或用 make dev 一起起）
make dev-backend     # uvicorn --reload :8000（在 backend/.env 中读配置）
make dev-worker      # arq worker（Phase 2+）
make dev-frontend    # Vite :5173

# 5. 跑测试（在 backend/ 下）
make test            # pytest -v

# 6. lint + 校验
make lint
make docker-config   # YAML 语法
```

`make help` 列全部 target。`make verify` = lint + test + compose 校验，是 CI 入口。

### Python 版本

`backend/.python-version` 锁定 **3.11**（pyenv / asdf / uv 自动识别）。与 `backend/pyproject.toml` 的 `requires-python = ">=3.11,<3.12"` 一致。

### IDE 配置（PyCharm / VS Code）

- **Python 解释器**: 选 `backend/.venv/bin/python`（**不要**选系统 Python 或根目录 `.venv`）
- **测试运行器**: 优先用 `make test`（会自动 cd backend）；若 IDE 直接调 pytest，把 Working Directory 设为 `backend/`
- **uv 用户**: 在 `backend/` 目录跑 `uv sync`（或 `uv pip install -e ".[dev]"`）会创建/使用 `backend/.venv`；**不要**从仓库根跑 `uv run`，否则 uv 会新建根 `.venv` 没用项目依赖

## 许可证

内部使用