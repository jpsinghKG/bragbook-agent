# Brag Book Agent

Summarizes the work you did on a given day and appends it to a brag book.

Runs locally, once a day. Collects from local git and GitHub, distills the day
with an LLM of your choosing, and writes the result to a Google Doc.

## Status

Scaffold only. Nothing is implemented yet. The design is written down in
[docs/](docs/) — [scope](docs/scope.md), [architecture](docs/architecture.md),
and [decisions](docs/decisions/README.md).

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- `gh` CLI, authenticated (`gh auth status`)
- An LLM: a provider API key, or [Ollama](https://ollama.com) running locally

## Setup

```sh
uv sync
```

## Configuration

Config lives in a TOML file and covers, at minimum:

- **identity** — the git emails and account handles that count as you
- **llm** — provider and model (`anthropic`, `openai`, `gemini`, `ollama`)
- **sources** — which collectors are enabled, and their settings
- **git roots** — directories to scan, plus a repo denylist
- **privacy** — how much reaches the LLM (metadata only, metadata plus
  diffstat, or full diffs), settable globally and overridable per repo
- **schedule** — run time, timezone, and the day boundary

Days with no detected activity are skipped rather than logged.

See [docs/architecture.md](docs/architecture.md) for how the pieces fit together
and [docs/scope.md](docs/scope.md) for what is deliberately out of scope.
