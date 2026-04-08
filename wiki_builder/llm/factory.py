"""
llm/factory.py — Backend factory.

Creates the appropriate LLMBackend from the WikiConfig.
"""

from __future__ import annotations

from ..config import WikiConfig
from .base import LLMBackend


def create_backend(cfg: WikiConfig) -> LLMBackend:
    """Return an LLMBackend instance based on cfg.llm.backend."""
    backend = cfg.llm.backend.lower()

    if backend == "claude-api":
        from .claude_api import ClaudeAPIBackend
        return ClaudeAPIBackend(cfg)

    if backend in ("openai-compat", "openai", "ollama", "openrouter", "groq"):
        from .openai_compat import OpenAICompatBackend
        return OpenAICompatBackend(cfg)

    if backend in ("claude-code", "claude-cli"):
        from .claude_code import ClaudeCodeBackend
        return ClaudeCodeBackend(cfg)

    raise ValueError(
        f"Unknown LLM backend: {backend!r}. "
        "Choose from: claude-api, openai-compat, claude-code"
    )
