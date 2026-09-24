# ADR-0011: OpenAI 作为默认 LLM，支持 OpenAI-compatible base_url

## Status

Accepted (Phase 0+)

## Context

原计划默认 LLM 是 Anthropic Claude。实际开发中发现：

- 国内访问 Anthropic / OpenAI 官方均需代理
- DeepSeek / Moonshot / GLM 等国内大模型价格低 5-10×、延迟更短
- 本地部署 vLLM / Ollama 用 OpenAI 兼容 API
- 团队已有 DeepSeek API key

## Decision

**OpenAI 作为默认 LLM provider**，所有节点级 model 默认值改为 OpenAI gpt-4.1 (高质量) / gpt-4.1-mini (便宜)。

**支持 `OPENAI_BASE_URL` env var**，通过 base_url 切换到任意 OpenAI-compatible 端点：

| Provider | base_url |
|---|---|
| OpenAI 官方 | `https://api.openai.com/v1` |
| DeepSeek | `https://api.deepseek.com` |
| Moonshot Kimi | `https://api.moonshot.cn/v1` |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4/` |
| vLLM 本地 | `http://localhost:8000/v1` |
| Ollama (经 openai-ollama) | `http://localhost:11434/v1` |

**Anthropic 路径保留**：`MODEL_<NODE>=anthropic:claude-sonnet-5` 仍可切回。

## 实现

```python
# core/llm.py
@lru_cache(maxsize=32)
def _build_chat_model(node: NodeName):
    provider, model = _parse_model_string(_NODE_TO_CONFIG[node])
    kwargs = {"model": model, "model_provider": provider}
    if provider == "openai" and settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return init_chat_model(**kwargs)
```

```bash
# .env
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_MAIN_PLAN=openai:gpt-4.1
# ... 10 个 MODEL_<NODE> 默认 openai:gpt-4.1[-mini]
```

## Consequences

- ✅ 国内 / 海外双轨：默认 DeepSeek，海外改 base_url 即可
- ✅ 成本优化：DeepSeek 价格 ≈ OpenAI 1/5
- ✅ 本地 LLM：vLLM / Ollama 同协议可用
- ✅ Anthropic 路径不破坏：所有现有 `MODEL_<NODE>=anthropic:...` 仍有效
- ⚠️ OpenAI-compatible API 可能不支持某些高级特性（structured output / tools），用前需验证
- ⚠️ `init_chat_model` + `model_provider="openai"` + `base_url` 路径需 LangChain 0.3+ 支持（已在 pyproject.toml）

## Alternatives

- **保持 Anthropic 默认**：海外质量最高，但国内不可用、价格高
- **抽象 LLM Provider 接口 + 工厂**：与 SearchProvider 类似（ADR 0007），可支持任意 provider。但 LLM 调用方（节点代码）通常不依赖 provider-specific 特性，过度抽象反而复杂。当前 `_parse_model_string` + `init_chat_model` 路径已足够灵活。

## References

- Plan: D5（多供应商）、D29（per-node 配置）
- ADR 0007：SearchProvider 多供应商抽象（设计思路类似）
- LangChain 0.3 `init_chat_model`：https://python.langchain.com/docs/how_to/chat_models_universal_init/