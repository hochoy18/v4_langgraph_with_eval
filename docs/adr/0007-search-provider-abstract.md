# ADR-0007: SearchProvider 多供应商抽象（Tavily + 阿里云百炼 MCP + 预留位）

## Status

Accepted (Phase 0)

## Context

Web 搜索供应商选择影响：

- 成本（按调用次数 / token 计费）
- 国内可达性（部分 SaaS 在国内延迟高 / 被墙）
- 合规（数据出境）
- 搜索质量（中文 vs 英文）

单一供应商锁定风险高。

## Decision

抽象出 `SearchProvider` Protocol：

```python
class SearchProvider(Protocol):
    async def search(self, query: str, **kwargs) -> list[SearchResult]: ...
```

实现：

1. **`TavilySearchProvider`**（默认）— `tavily-python` SDK
2. **`BailianMcpSearchProvider`** — 阿里云百炼 Web Search MCP，`langchain-mcp-adapters`
3. **`_placeholder.py`** — 预留第 3 种（`ExaSearchProvider` / `BraveSearchProvider` / …）

`SearchProviderRegistry` 按 `SEARCH_PROVIDER` 环境变量选实现。

## Consequences

- ✅ 供应商热替换：`.env` 改 `SEARCH_PROVIDER=bailian_mcp` 即可
- ✅ 国内 / 海外双轨
- ✅ 新供应商无需改业务代码（按 Protocol 实现即可）
- ⚠️ 不同供应商返回字段不一致（snippet vs summary vs content）需标准化
- ⚠️ `langchain-mcp-adapters` 版本较新，需在 Phase 0a 验证 API

## Alternatives

- **只用 Tavily**：最快上线，但国内延迟 + 单一供应商风险
- **只用百炼 MCP**：国内好，但海外与英文质量不如 Tavily

## References

- Plan: D6（数据源）、D11（检索供应商架构）
- 计划文档：`/Users/cai.he/.claude/plans/deep-research-humming-gray.md`