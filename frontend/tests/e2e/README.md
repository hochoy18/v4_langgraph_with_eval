# Frontend E2E tests

占位。Phase 8 收尾时填入 Playwright e2e 测试。

## 计划

- `login.spec.ts` — 登录流程
- `research.spec.ts` — 提交研究 → SSE 事件流 → PlanApproval → 报告展示
- `report.spec.ts` — 报告渲染 / 引用悬停 / 反馈按钮

## 跑法（待实现）

```bash
cd frontend
npm run e2e         # 启 backend 后跑
```