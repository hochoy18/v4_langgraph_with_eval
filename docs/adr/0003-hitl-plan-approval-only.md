# ADR-0003: HITL 仅在计划审批（不在研究途中或报告后）

## Status

Accepted (Phase 0)

## Context

Deep research 流程中的 HITL（Human-in-the-Loop）可以有多个候选位置：

1. **研究开始前**：用户审批 / 编辑多方案计划
2. **研究途中**：发现方向错误想重定向 / 补充上下文
3. **报告完成后**：用户审阅初稿要求改写

每个 HITL 点都意味着：

- 多一个 `interrupt_before` / `interrupt_after` 节点
- 多一份 resume 状态机复杂度
- 多一份前端审批 UI 工作量
- 多一份 Langfuse trace 分支
- 多一份 token 浪费（LLM 已生成的内容若被中断则丢弃）

## Decision

**仅 1 个 HITL 点**：在 `main.plan` 与 `research.dispatch` 之间中断，由用户审批 / 编辑多方案计划。

## Consequences

- ✅ 状态机简单（一个 interrupt_before，单一 Command(resume) 路径）
- ✅ 用户对研究方向有最终决定权，避免"研究完了发现跑偏了"
- ✅ 报告完成后不再交互，UX 更"出炉"（用户只读 + 点赞）
- ⚠️ 研究途中无法重定向：若用户对初始方向有疑虑，只能 cancel + 重提
- ⚠️ 报告初稿不支持交互改写：只能 re-run

## Alternatives

- **多 HITL 点（plan + research + draft）**：用户体验最完整，但状态机 ×3，UX 复杂度 ×3
- **完全无 HITL**：研究完了给报告，用户只能点赞。最简单但跑偏风险大

## References

- Plan: D3（HITL 颗粒度）、D17（执行模式 / Command(resume=...)）
- 计划文档：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`