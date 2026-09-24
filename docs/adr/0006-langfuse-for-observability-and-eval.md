# ADR-0006: Langfuse 而非 LangSmith

## Status

Accepted (Phase 0)

## Context

LLM 应用的可观测性平台主流选项：

- **LangSmith**（LangChain 官方商业 SaaS）
- **Langfuse**（开源，自托管 / 云）
- **自建**（OpenTelemetry + 自家存储）

需满足：

- 节点级 trace（每个 LangGraph 节点 + LLM call）
- Token 用量 / 成本 / 延迟指标
- Eval score 接入
- Prompt 版本管理 / A/B
- 多租户 trace tag 隔离

## Decision

采用 **Langfuse**（外部已部署）。本仓库**不打包 Langfuse**，仅通过 `LANGFUSE_HOST` / `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` 接入。

## Consequences

- ✅ 开源：fork 用户可接入自家 Langfuse
- ✅ 与 trace/eval 同平台（D8 四种 eval 全部写入 Langfuse scores）
- ✅ Prompt Management（D21）内置版本化 + A/B + 热更新
- ✅ Langfuse `langchain` callback handler 集成 LangGraph 简单
- ⚠️ Langfuse 不可达时 callback handler 必须容错（不能阻塞主流程）
- ⚠️ trace 数据隔离按 `tenant_id` tag 配置需要 Langfuse 后台策略

## Alternatives

- **LangSmith**：与 LangGraph 集成同样丝滑，但 SaaS 锁定 + 按用量计费
- **自建 OTel**：完全可控，与云原生 tracing 一致，但学习成本高 + 自建 score 系统

## References

- Plan: D4（可观测性）、D8（评估）、D21（Prompt 管理）
- 计划文档：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`