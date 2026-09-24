# ADR-0005: 行级 tenant_id 而非 schema-per-tenant

## Status

Accepted (Phase 0)

## Context

企业级多租户隔离有两种主流策略：

- **行级隔离**：所有业务表带 `tenant_id` 列，查询自动 `WHERE tenant_id = :current_tenant`
- **Schema-per-tenant**：Postgres 每租户一个 schema
- **DB-per-tenant**：每租户独立数据库

## Decision

采用 **行级隔离**：

- 每张业务表带 `tenant_id`（UUID）
- SQLAlchemy `before_compile` 事件钩子强制每条 SELECT / INSERT / UPDATE / DELETE 自动加 `WHERE tenant_id`
- 跨租户 GET / PUT / DELETE 测试覆盖全部返回 404

## Consequences

- ✅ 实现简单：一个 SQLAlchemy hook + 每张表一列
- ✅ 跨租户 JOIN / 聚合查询仍然可行（ad-hoc 分析场景）
- ✅ 备份 / 迁移只一份
- ✅ 单库单 connection pool，运维便宜
- ⚠️ `WHERE tenant_id` 必须强制（漏一处 = 数据泄露）
- ⚠️ 数据量与租户数线性相关，规模化后需考虑 schema 拆分

## Alternatives

- **Schema-per-tenant**：迁移独立，但 schema 数多起来管理困难
- **DB-per-tenant**：隔离最强（适合金融 / 医疗合规），但运维成本高

## When to revisit

- 租户数 × 行数 > 1e9 时考虑 schema 拆分
- 出现强合规需求（如 HIPAA）时考虑 DB-per-tenant

## References

- Plan: D24（多租户隔离）、D10（认证 / 租户）
- Security 小节：Tenant 越权 缓解
- 计划文档：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`