"""
llm/claude_code.py — Claude Code CLI subprocess backend.

Uses `claude --print` for non-interactive completions. Requires the user
to already have Claude Code installed and authenticated.

Falls back with a clear error if the `claude` binary is not found.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess

from ..config import WikiConfig
from .base import LLMBackend, LLMResponse


class ClaudeCodeBackend(LLMBackend):
    def __init__(self, cfg: WikiConfig) -> None:
        self._model = cfg.llm.model
        self._max_tokens = cfg.llm.max_tokens_per_call
        self._prompt_cache: dict[str, LLMResponse] = {}

    def _find_claude(self) -> str:
        binary = shutil.which("claude")
        if not binary:
            raise RuntimeError(
                "Claude Code CLI (`claude`) not found in PATH.\n"
                "Install it from https://claude.ai/code or switch to the "
                "claude-api backend in wiki.yaml."
            )
        return binary

    def complete(self, system: str, user: str, max_tokens: int | None = None) -> LLMResponse:
        cache_key = hashlib.sha256((system + "\x00" + user).encode()).hexdigest()
        if cache_key in self._prompt_cache:
            return LLMResponse(text=self._prompt_cache[cache_key].text, cached=True)

        claude = self._find_claude()
        # Combine system + user into a single prompt for --print mode
        prompt = f"{system}\n\n{user}"

        cmd = [claude, "--print"]
        if self._model:
            cmd += ["--model", self._model]

        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0:
            # Redact potential secrets from stderr before surfacing in error messages
            sanitized = re.sub(r"sk-[A-Za-z0-9\-_]{10,}", "[REDACTED]", result.stderr)
            sanitized = re.sub(r"(?i)api[_-]?key[=:\s]+\S+", "api_key=[REDACTED]", sanitized)
            raise RuntimeError(
                f"claude CLI exited with code {result.returncode}:\n{sanitized}"
            )

        text = result.stdout.strip()
        resp = LLMResponse(text=text)
        self._prompt_cache[cache_key] = resp
        return resp

    def estimate_cost_usd(self, input_tokens: int, output_tokens: int) -> float:
        # Claude Code usage is billed to the user's subscription, not per-call.
        return 0.0
