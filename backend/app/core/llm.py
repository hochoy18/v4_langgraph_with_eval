"""LLM 工厂 — init_chat_model + 节点级模型注册表（D5 / Phase 7 A/B 用）。

每个 LangGraph 节点从这里取 model 实例；不同节点默认绑不同模型，
可通过 MODEL_<NODE> 环境变量切换。

用法：
    from app.core.llm import get_model
    llm = get_model("main_plan", temperature=0.3)
    resp = await llm.ainvoke([...])
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from langchain.chat_models import init_chat_model

from app.core.config import get_settings

NodeName = Literal[
    "main_plan",
    "research_dispatch",
    "research_coverage_check",
    "sq_extract",
    "sq_reflect",
    "write_outline",
    "write_sections",
    "write_revise",
    "write_summarize",
    "judge_citation",
]


def _node_to_config(node: NodeName) -> str:
    """读最新 settings 取该节点的 model 配置字符串。

    在函数内读 settings 而非模块级常量，便于测试 + 运行时热重载。
    """
    s = get_settings()
    return {
        "main_plan": s.model_main_plan,
        "research_dispatch": s.model_research_dispatch,
        "research_coverage_check": s.model_research_coverage_check,
        "sq_extract": s.model_sq_extract,
        "sq_reflect": s.model_sq_reflect,
        "write_outline": s.model_write_outline,
        "write_sections": s.model_write_sections,
        "write_revise": s.model_write_revise,
        "write_summarize": s.model_write_summarize,
        "judge_citation": s.model_judge_citation,
    }[node]


def _parse_model_string(s: str) -> tuple[str, str]:
    """`'anthropic:claude-sonnet-5'` → `('anthropic', 'claude-sonnet-5')`"""
    if ":" not in s:
        return ("anthropic", s)
    provider, model = s.split(":", 1)
    return (provider.strip(), model.strip())


@lru_cache(maxsize=32)
def _build_chat_model(node: NodeName):
    provider, model = _parse_model_string(_node_to_config(node))
    s = get_settings()
    kwargs: dict[str, object] = {"model": model, "model_provider": provider}

    # OpenAI-compatible providers (DeepSeek / Moonshot / vLLM / Ollama 等)
    # 走 base_url 切换端点。base_url 只对 openai provider 生效。
    if provider == "openai" and s.openai_base_url:
        kwargs["base_url"] = s.openai_base_url

    return init_chat_model(**kwargs)


def get_model(node: NodeName, *, temperature: float | None = None):
    """取指定节点的 chat model；可选覆盖 temperature。"""
    model = _build_chat_model(node)
    if temperature is not None:
        return model.bind(temperature=temperature)
    return model


def clear_cache() -> None:
    """Phase 7 A/B：切换配置后清缓存。"""
    _build_chat_model.cache_clear()