from __future__ import annotations

import os

from pydantic_ai import Agent

SUPPORTED_PROVIDERS = {"openai", "anthropic", "google", "ollama"}

def get_agent(system_prompt: str) -> Agent[None, str]:
    """Build an Agent for the provider/model configured via env vars.

    LLM_PROVIDER selects the provider (openai, anthropic, google, or ollama).
    LLM_MODEL is the model name for that provider (e.g. gpt-4o, claude-sonnet-5,
    gemini-2.5-flash, qwen3.5).

    Each provider reads its own credentials from the environment:
    OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY (or GEMINI_API_KEY), or
    for ollama, OLLAMA_BASE_URL (and optional OLLAMA_API_KEY).
    """
    provider = os.getenv("LLM_PROVIDER")
    if provider not in SUPPORTED_PROVIDERS:
        raise RuntimeError(
            f"LLM_PROVIDER must be one of {sorted(SUPPORTED_PROVIDERS)}, got {provider!r}"
        )

    model_name = os.getenv("LLM_MODEL")
    if not model_name:
        raise RuntimeError("LLM_MODEL environment variable must be set")

    return Agent(f"{provider}:{model_name}", system_prompt=system_prompt)
