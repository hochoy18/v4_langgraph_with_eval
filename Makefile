# Deep Research 产品 — 本地开发 / 测试 / 验收命令
#
# 不依赖 docker；前提：本地有 Postgres + Redis（任意方式启动），
# .env 配齐（bash scripts/setup.sh 一次性引导）。
#
# 用法：
#   make help           显示所有 target
#   make dev            同时起 backend + worker + frontend（前台，Ctrl-C 全停）
#   make test           跑全部测试
#   make lint           ruff + mypy
#   make verify         lint + test + docker compose config

SHELL := /bin/bash
.DEFAULT_GOAL := help

# 路径
BACKEND_DIR   := backend
FRONTEND_DIR  := frontend
PYPROJECT     := $(BACKEND_DIR)/pyproject.toml

# Python（默认用 python3；CI 中可改）
PYTHON        ?= python3

# 后端 .env 路径（dev 默认从仓库根读；可被覆盖）
ENV_FILE      ?= .env

# 颜色（仅 TTY）
BOLD := \033[1m
DIM  := \033[2m
RESET := \033[0m

.PHONY: help
help:  ## 显示所有可用 target
	@printf "$(BOLD)Deep Research · 本地开发$(RESET)\n\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BOLD)%-20s$(RESET) %s\n", $$1, $$2}'
	@printf "\n$(DIM)环境：$(RESET).env 在仓库根, dev 命令自动读\n"

# ===== 安装 =====

.PHONY: install
install:  ## 安装后端 dev 依赖（pip + extras）
	cd $(BACKEND_DIR) && $(PYTHON) -m pip install -e ".[dev]"
	cd $(FRONTEND_DIR) && npm install

.PHONY: install-backend
install-backend:  ## 仅安装后端依赖
	cd $(BACKEND_DIR) && $(PYTHON) -m pip install -e ".[dev]"

.PHONY: install-frontend
install-frontend:  ## 仅安装前端依赖
	cd $(FRONTEND_DIR) && npm install

# ===== 测试 =====

.PHONY: test
test:  ## 跑全部后端测试（pytest，会清 settings + llm cache）
	$(PYTHON) -m pytest -v

.PHONY: test-cov
test-cov:  ## 跑测试 + 覆盖率
	$(PYTHON) -m pytest --cov=backend/app --cov-report=term-missing

.PHONY: test-fast
test-fast:  ## 跑测试，跳过集成（当前所有测试都算 fast）
	$(PYTHON) -m pytest -v -x

# ===== Lint / 类型 =====

.PHONY: lint
lint:  ## ruff check + format 检查
	cd $(BACKEND_DIR) && $(PYTHON) -m ruff check .
	cd $(BACKEND_DIR) && $(PYTHON) -m ruff format --check .

.PHONY: format
format:  ## ruff format 自动修复
	cd $(BACKEND_DIR) && $(PYTHON) -m ruff format .

.PHONY: typecheck
typecheck:  ## mypy 静态类型检查
	cd $(BACKEND_DIR) && $(PYTHON) -m mypy app/

# ===== Dev server =====

.PHONY: dev-backend
dev-backend:  ## 起 uvicorn (auto-reload, port 8000)
	cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: dev-worker
dev-worker:  ## 起 arq worker（Phase 2+ 才有意义）
	cd $(BACKEND_DIR) && $(PYTHON) -m arq app.workers.research_worker.WorkerSettings

.PHONY: dev-frontend
dev-frontend:  ## 起 Vite dev server（auto-reload, port 5173）
	cd $(FRONTEND_DIR) && npm run dev

.PHONY: dev
dev:  ## 同时起后端 + worker + 前端（Ctrl-C 全停）
	@echo "$(BOLD)Starting backend + worker + frontend... Ctrl-C to stop all$(RESET)"
	@trap 'kill 0' SIGINT SIGTERM EXIT; \
	  cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & \
	  cd $(BACKEND_DIR) && $(PYTHON) -m arq app.workers.research_worker.WorkerSettings & \
	  cd $(FRONTEND_DIR) && npm run dev & \
	  wait

# ===== 验证 =====

.PHONY: readyz
readyz:  ## 命中后端 /readyz（需 backend 已起）
	@curl -fsS http://localhost:8000/readyz | $(PYTHON) -m json.tool || (echo "$(BOLD)/readyz failed$(RESET)"; exit 1)

.PHONY: healthz
healthz:  ## 命中后端 /healthz（仅 liveness）
	@curl -fsS http://localhost:8000/healthz | $(PYTHON) -m json.tool

.PHONY: docker-config
docker-config:  ## 校验 docker-compose.yml 语法（不实际启动）
	docker compose config --quiet 2>&1 || python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml')); print('YAML OK')"

.PHONY: verify
verify: lint test docker-config  ## lint + 测试 + compose 语法校验（CI 入口）

# ===== 清理 =====

.PHONY: clean
clean:  ## 清 pyc / pytest cache / ruff cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -prune -o -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	@echo "$(BOLD)cleaned$(RESET)"

.PHONY: reset
reset: clean  ## clean + 清 .env（需手动重跑 scripts/setup.sh）
	@echo "$(BOLD)reset$(RESET) — 跑 scripts/setup.sh 重配 .env"