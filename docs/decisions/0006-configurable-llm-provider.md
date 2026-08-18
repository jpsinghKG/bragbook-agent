# 0006 — Configurable LLM provider from day one, defaulting to Ollama

**Status:** Accepted

## Context

The tool needs to be adoptable by peers with different provider access, so
the choice among Anthropic, OpenAI, Gemini, and local Ollama has to be a config
value rather than a code change. Building the abstraction later would mean
threading it through a summarizer already written against one SDK.

## Decision

Use `pydantic-ai` as the provider abstraction, selected by provider and model
fields in the config file. Ship `ollama` / `qwen3.5` as the default.

## Consequences

- The tool produces real output on first run with no key, no signup, and no
  spend, which shortens the loop while the prompt is still being tuned.
- Nothing leaves the machine under the default configuration, which makes the
  privacy question ([0007](0007-configurable-privacy-levels.md)) far less sharp
  for a first-time user.
- Summary quality under a local model is meaningfully below a frontier model.
  The default is a starting point, not a recommendation for daily use.
- `pydantic-ai` gives typed structured output with validation retries, which
  matters more than usual when a small local model is producing the structure.
