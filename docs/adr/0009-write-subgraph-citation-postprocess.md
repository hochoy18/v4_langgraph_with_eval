# ADR-0009: Write 节点 = 5 步子图（大纲 → 分节 → 组装 → 修正 → 概要），引用用占位符+后处理

## Status

Accepted (Phase 0)

## Context

研究报告的生成通常有两条路：

- **单次写完**：一次 LLM 调用出完整报告。简单，但上下文压力大、引用编号不可控、质量参差。
- **流水线 + 程序化后处理**：分多步生成，最后用程序保证引用编号、参考文献列表等机械正确性。

## Decision

Write 节点拆成 **5 步子图**：

```
write.outline (haiku)         — 输入 plan + sub_results，输出 List[SectionSpec]
  ↓
write.sections (sonnet, Send)  — 每节一次 LLM 调用，输出含 [cite:url-xxx] 占位符
  ↓
write.assemble (程序化)        — 拼接 + 引用后处理：扫描占位符按首次出现顺序映射为 [1][2][3]…
  ↓
write.revise (sonnet)          — 自审一次（引用准确性 / 未支撑断言 / 章节一致性）
  ↓
write.summarize (haiku)        — 基于全文写 ~400 tokens summary_md
```

## 引用模型

- LLM 写正文用 `[cite:url-xxx]` 占位符（语义：这里引用 URL `xxx`）
- `write.assemble` 程序化扫描：按 URL 首次出现顺序映射 `[1]` / `[2]` / `[3]`…
- 文末追加 `## References` 区
- 双输出：`summary_md` + `report_md`

## Consequences

- ✅ 引用编号确定性，LLM 不会编 `[n]`（它在写 `[cite:url-xxx]`，后处理负责编号）
- ✅ 质量可调（每节独立 sonnet 调用，受上下文压力小）
- ✅ Langfuse trace 中保留 `sections`（初稿）+ `sections_revised`（修订稿），可对比修订幅度
- ✅ `write.assemble` 纯程序化（无 LLM），200ms 内完成
- ⚠️ token 消耗约 x1.8–2.5（多次 LLM 调用）
- ⚠️ 总报告生成 p95 ≈ 60s（`outline 5 + sections 15 + assemble 0.2 + revise 15 + summarize 8 + persist 0.2` ≈ 43s + 并行节省）

## Alternatives

- **单次写完**：快但质量不稳，引用编号经常乱
- **Map-Reduce 写**：每子问题独立写一段，再综合。质量上限较低
- **大纲 → 单次写完**：用大纲约束结构但不拆节，token 省但质量仍不稳

## References

- Plan: D14a（Write 节点结构）、D15（报告长度）、D18（写节点）、D20（引用模型）
- 计划文档：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`