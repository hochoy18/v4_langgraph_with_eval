# ADR-0001: LangGraph 而非 Autogen / CrewAI

## Status

Accepted (Phase 0)

## Context

需要选择一个 multi-agent 编排框架，支持：

- Plan / Research / Write 多 agent 协作
- 单中断点的 HITL pause / resume
- 节点级 SSE 事件流
- 异步执行 + Redis Streams 重放
- 与外部 Langfuse trace 集成

候选：

- **LangGraph**（LangChain 官方）
- **Microsoft Autogen**
- **CrewAI**

## Decision

采用 **LangGraph**（最新版）。

## Consequences

- 与 LangChain 生态原生集成：`init_chat_model`、`langchain-mcp-adapters`、`langchain-anthropic`
- 与 v3 参考实现（`open_deep_research`）一致
- `interrupt_before` + `Command(resume=...)` 是 LangGraph 原生能力，HITL 接线简单
- `Send` API 提供 send-to-multiple 模式，研究子问题的并行 spawn 自然
- Postgres checkpointer 内置，State 持久化免自建
- 单进程线程模型与 FastAPI async 集成需要小心（用 `ainvoke`）

## Alternatives

- **Autogen**：多 agent 聊天模式更适合对话场景，研究流水线不如 LangGraph 直观
- **CrewAI**：高层抽象，定制能力弱，HITL 与 Redis Streams 集成需更多胶水

## References

- Plan: D13（Research 拓扑）、D14（sq.workflow 粒度）、D15（双层预算）
- 计划文档：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`