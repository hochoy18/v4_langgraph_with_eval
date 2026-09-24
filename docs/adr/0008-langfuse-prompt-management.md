# ADR-0008: Prompt 管理：Langfuse Prompt Management

## Status

Accepted (Phase 0)

## Context

Prompt 在深度研究中有 ~10 个关键模板（plan / dispatch / coverage / sq.extract / sq.reflect / write.outline / write.section / write.revise / write.summarize / judge.citation）。管理方式候选：

- **代码内 Python 常量**：简单，Git 版本控制
- **YAML / Markdown 文件**：可被业务同事编辑
- **DB 存 Prompt + 后台 CRUD**：动态生效
- **Langfuse Prompt Management**（SaaS / 自托管）

## Decision

采用 **Langfuse Prompt Management**（D6 已选 Langfuse，prompt 管理是其内置能力）。

用法：

```python
from langfuse import Langfuse
client = Langfuse()
prompt = client.get_prompt("deep-research/plan", label="production")
compiled = prompt.compile(query=query)
```

特点：

- 通过 `app/prompts/loader.py` 集中拉取
- 缓存 + Langfuse 不可达时回退 `app/prompts/_defaults/` 下的本地常量
- 版本化（v1, v2, …）+ 标签（`production` / `staging`）
- 热更新（无需重启）
- 与 trace / eval 同平台（D21）

## Consequences

- ✅ 业务同事可在 Langfuse 界面改 prompt，无需 PR
- ✅ A/B 测试：`label="experiment-A"` vs `"experiment-B"` 切流量
- ✅ eval 跑分可追溯 prompt 版本
- ✅ 与 trace 数据天然关联（每个 trace 显示用的 prompt 版本）
- ⚠️ Langfuse 不可达 → 回退本地常量（牺牲热更新能力）
- ⚠️ 业务同事必须熟悉 Langfuse UI

## Alternatives

- **代码常量**：简单但每次改都要 PR + 部署
- **DB + 后台**：动态但要自己写 CRUD + UI
- **YAML 文件**：可被业务同事编辑但仍走 PR，热更新困难

## References

- Plan: D21（Prompt 管理）、D22（v1 全局共享）
- 计划文档：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`