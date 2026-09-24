# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, or
- **`CONTEXT-MAP.md`** at the repo root if it exists: it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`docs/adr/`**: read ADRs that touch the area you're about to work in. In multi-context repos, also check `src/<context>/docs/adr/` for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## File structure

Single-context repo (this repo):

```
/
├── CONTEXT.md                       # 术语表（v1 暂未生成，由 Phase 0a 完成后从计划导入）
├── docs/
│   ├── adr/                         # 架构决策记录（10 个待写）
│   │   ├── 0001-langgraph-over-autogen.md
│   │   └── ...
│   └── agents/                      # 本目录（agent 配置）
│       ├── issue-tracker.md
│       └── domain.md
└── src/                             # backend/, frontend/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_

## 本仓库的特殊约定

- **领域术语**已在 `/Users/cai.he/.claude/plans/deep-research-humming-gray.md` 的"领域术语表"小节完整定义，Phase 0a 完成时导入到 `CONTEXT.md`。
- **ADR** 共 10 条已列出标题与理由（见 plan 文档"需要落 ADR 的关键决策"小节），需在实施过程中补完整文件内容。