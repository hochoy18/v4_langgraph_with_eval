# CONTEXT.md — Deep Research 产品领域术语表

> 本文件由 `/grill-with-docs` skill 引导生成，是项目的**领域词汇权威表**。
> 修改领域概念时同步更新本文，避免代码 / 文档 / issue / commit 信息漂移。
>
> 完整决策见 `docs/adr/`；实施计划见 `/Users/cai.he/.claude/plans/deep-research-humming-gray.md`。

---

## 顶层概念

| 术语 | 定义 |
|---|---|
| **Tenant / Organization** | 顶层隔离单元。每个 User 隶属于恰好一个 Tenant。所有业务行携带 `tenant_id`。 |
| **User** | Tenant 内的认证账户。通过 JWT（httpOnly cookie）认证。 |

---

## 研究流程

| 术语 | 定义 |
|---|---|
| **Research Session** | 用户提交的一个研究查询。拥有唯一 `job_id`，受预算约束（D25），产出 0–1 个 Report。状态机：`queued → running → paused(HITL) → running → completed \| failed`。 |
| **Resume Command** | LangGraph 的 `Command(resume=value)` 机制，从 Postgres checkpointer 读取中断时的 state 并续跑。`POST /research/{id}/resume` 触发的 arq job 通过此机制恢复执行。 |
| **Plan** | `main.plan` 节点的输出：2–3 个 `PlanAlternative`，每个包含子问题、预期信源、预算估算。 |
| **PlanAlternative** | 一份候选研究计划，在 HITL 网关展示给用户。用户选一个（或编辑）。 |
| **Research Sub-question** | 选中 Plan 中的一项；由一个并行子 agent 执行。 |
| **Sub-agent Result** | 一个子问题的检索结果、抓取的页面、抽取的事实、反思。 |
| **Sub-Question Workflow (sq.workflow)** | 每个 Research Sub-question 在 `research.fan_out` 中被 spawn 的独立 sub-graph（LangGraph 技术上编译为 subgraph），业务上称为 **workflow**。内部 4 节点（search/fetch/extract/reflect）+ 子问题预算约束的内部循环。 |
| **Coverage Gap** | research.coverage_check 节点识别出的"哪些子问题证据不足 / 哪些方面没覆盖到"，用于决定是否回 research.dispatch 重跑或精化子问题。 |

---

## 报告产物

| 术语 | 定义 |
|---|---|
| **Outline** | `write.outline` 节点的产物：报告章节列表，每节指定覆盖的子问题。 |
| **Section** | `write.sections` 节点按章节生成的一段 Markdown 文本，使用 `[cite:url-xxx]` 占位符标记来源。 |
| **Citation Placeholder** | LLM 写入文本时使用的占位符，格式 `[cite:url-xxx]`，由 `write.assemble` 后处理替换为确定编号 `[n]`。 |
| **Citation** | 最终报告中 `[n]` 标记，对应文末 References 第 n 条（URL + 标题 + 抓取时间）。编号按 URL 在文中首次出现顺序确定。 |
| **References** | 报告文末的来源列表，由引用后处理生成。每条格式：`[n] <URL> — <标题>（抓取时间）`。 |
| **Report** | 最终 Markdown 制品。存为 `reports` 表中的一行；包含 `summary_md`（概要）与 `report_md`（全文）+ 生成的 PDF/DOCX。 |
| **Summary** | 报告中 ~400 tokens 的浓缩版，先于全文展示在报告页头部，供用户快速判断质量后再展开。 |

---

## 反馈与评估

| 术语 | 定义 |
|---|---|
| **Feedback Score** | 用户对 Report 的评价（👍 / 👎 / 结构化字段），写入 Langfuse。 |
| **Ground-truth Question** | 基准查询，附带人工撰写的参考答案，供 eval runner 使用。 |
| **Eval Run** | ground-truth 套件的一次执行，在 Langfuse 中产出评分。 |

---

## 运行时约束

| 术语 | 定义 |
|---|---|
| **Performance Budget**（D28） | 单 session / 单阶段的延迟 / token / 成本上限。超限立即 emit `budget_exceeded` 并停。 |
| **Rate Limit Token**（D29） | Redis 中按 user / tenant / global 三层计数的令牌桶键（`rl:user:{id}:hour` 等），HTTP middleware + Arq 入队时读取并扣减。 |
| **Fixture** | Phase 0a 创建的种子数据：测试租户 / 用户 / Langfuse prompts / ground-truth 问题集 / 样例报告。供 dev、e2e、eval 共享。 |

---

## 同义词 / 避免漂移

下表是**禁用**的别名（保持术语一致性）：

| 不要用 | 用 |
|---|---|
| "task" / "job"（指用户的研究请求时） | **Research Session** |
| "AI 生成的草稿" / "草稿" | **Report**（含 `summary_md` + `report_md`） |
| "子任务" / "子查询" | **Research Sub-question** |
| "子图"（业务语境） | **Sub-Question Workflow (sq.workflow)** |
| "搜索结果"（抽象） | **Sub-agent Result**（具体到一次 sub-question 的输出） |
| "管理员" / "owner" | **Tenant**（顶层隔离概念） |
| "客户"（指组织） | **Tenant** |

---

## 状态机速查

### Research Session
```
queued
  → running (main.plan)
    → paused (HITL: 等待用户审批 plan)
      → running (research 子图)
        → completed | failed | budget_exceeded
```
（用户 POST /resume 后从 paused 回到 running）

### 报告导出
```
report_persist (同步：DB + 入队 export_report_job)
  → export_report_job (异步 arq)
    → reports.pdf_path / docx_path 更新
      → SSE pdf_ready 事件
```
（前端 download 按钮在 `export_status="done"` 后才可点击）