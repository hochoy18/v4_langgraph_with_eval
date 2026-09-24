# ADR-0010: Research 节点 = 显式子图 + 双层预算

## Status

Accepted (Phase 0)

## Context

Research 是深度研究中耗时最长的环节。两条路：

- **扁平结构**：单次 search / fetch / extract / reflect 循环，预算仅一层
- **嵌套子图**：显式外层子图（research sub-graph）+ 内层 sq.workflow（每个子问题的 sub-sub-graph）

## Decision

**显式 research 子图 + 双层预算**：

```
research 子图 (4 个外层节点)
├── research.dispatch (haiku)
├── research.fan_out (Send API)
├── research.aggregate
└── research.coverage_check (sonnet)
    ↓ 不足则回 dispatch
    (loop, 受 max_iterations=2 约束)

sq.workflow (每子问题的 sub-sub-graph)
├── sq.search
├── sq.fetch
├── sq.extract (sonnet)
└── sq.reflect (sonnet)
    ↓ 不足则回 search
    (loop, 受 max_sub_iterations=3 约束)
```

**双层预算**：

| 层级 | 上限 | 控制对象 |
|---|---|---|
| Session（外层）| `max_iterations=2` | research 回到 dispatch 次数 |
| 子问题（内层）| `max_sub_iterations=3` | sq 回到 search 次数 |

## Coverage 判定（D16）

research.coverage_check 通过下列硬指标判定（任一不满足即回 dispatch）：

1. 每子问题事实数 ≥ `MIN_FACTS_PER_SQ=3`
2. 关键子问题（plan 中 `priority="critical"`）事实数 ≥ `MIN_CRITICAL_FACTS=5`
3. LLM 显式给出的 `gaps: List[str]` 为空
4. 至少 1 个子问题引用了 ≥ 2 个不同信源

## Consequences

- ✅ 与 write 子图对称 — 顶层 graph 更清晰
- ✅ Trace 细粒度 — Langfuse 可分析每个 sq 的 token / 耗时
- ✅ 内外两层循环可独立设预算
- ✅ 内部 4 节点（search/fetch/extract/reflect）每步可独立优化 / A/B
- ⚠️ 节点数翻倍 — 调试更复杂，LangGraph state schema 更繁琐
- ⚠️ D13b 双层预算需要文档说明为什么这么设

## Alternatives

- **扁平结构**：少一层循环，但所有子问题共享单一预算，颗粒度粗
- **Map-Reduce 写**：并行但控制力弱

## References

- Plan: D13（Research 拓扑）、D14（sq.workflow 粒度）、D15（双层预算）、D16（Coverage 判定）
- 计划文档：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`