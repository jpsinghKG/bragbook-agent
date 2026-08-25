# Brag Book Agent

Summarizes the work you did on a given day and appends it to a brag book.

Runs locally, once a day. Collects from local git and GitHub, distills the day
with an LLM of your choosing, and writes the result to a Google Doc.

## Status

Scaffold only. Nothing is implemented yet. The design is written down in
[docs/](docs/) — [scope](docs/scope.md), [architecture](docs/architecture.md),
and [decisions](docs/decisions/README.md).

## Requirements

- macOS
- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- `gh` CLI, authenticated (`gh auth status`)
- A GitHub personal access token (for the GitHub collector)
- A Linear API token (for the Linear collector)
- An LLM: a provider API key (Anthropic, OpenAI, or Google), or
  [Ollama](https://ollama.com) running locally

## macOS setup

1. **Install Homebrew**, if you don't already have it:

   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install uv**:

   ```sh
   brew install uv
   ```

3. **Install Python 3.13**. uv can manage this for you — no separate pyenv
   install needed:

   ```sh
   uv python install 3.13
   ```

4. **Install and authenticate the `gh` CLI**:

   ```sh
   brew install gh
   gh auth login
   gh auth status   # should report "Logged in"
   ```

5. **Clone the repo and install dependencies**:

   ```sh
   git clone https://github.com/jpsinghKG/bragbook-agent.git
   cd bragbook-agent
   uv sync
   ```

6. **Create your `.env`** from the template and fill in the values below:

   ```sh
   cp .env.example .env
   ```

7. **(Optional) Install Ollama**, if you'd rather run the LLM locally instead
   of using a provider API key:

   ```sh
   brew install ollama
   ollama serve
   ```

## Configuration

Configuration is environment variables, loaded from `.env` (see
[.env.example](.env.example)):

- **`GIT_LOCAL_IDENTITIES`** — comma-separated git usernames that count as you
- **`GIT_LOCAL_ROOTS`** — comma-separated absolute paths to scan for local git
  activity
- **`GITHUB_IDENTITIES`** — comma-separated GitHub handles that count as you
- **`GITHUB_API_TOKEN`** — a GitHub personal access token
- **`LINEAR_API_TOKEN`** — a Linear API token
- **`LLM_PROVIDER`** — `anthropic`, `openai`, `google`, or `ollama`
- **`LLM_MODEL`** — the model name for that provider
- **`LLM_MAX_TOKENS`** — optional, raise for reasoning models that burn tokens
  on thinking
- One of **`ANTHROPIC_API_KEY`**, **`OPENAI_API_KEY`**, **`GOOGLE_API_KEY`**,
  or **`OLLAMA_BASE_URL`**, matching `LLM_PROVIDER`

## Running

```sh
make run
```

This collects the last day of activity from local git, GitHub, Linear, and any
manually logged entries, summarizes it with the configured LLM, and writes the
result to [summaries/](summaries/) as a Markdown file. Days with no detected
activity are skipped rather than logged.

### Logging manual entries

For things no collector would otherwise catch (a meeting, a conversation, work
done outside git/GitHub/Linear):

```sh
make log MSG="Mentored Alice on the onboarding project" TYPE=meeting
```

`TYPE` is optional (defaults to `message`) and must be one of the `EventType`
values in [src/models/event.py](src/models/event.py). Entries are appended to
`db/user_input.jsonl` and picked up by the next run.

## Common commands

```sh
make install     # uv sync, also installs the pre-commit hook
make hooks       # install the pre-commit hook (runs automatically via install)
make run         # run the pipeline once
make log         # MSG="..." TYPE=... — log a manual entry
make format      # ruff format
make lint        # ruff check
make lint-fix    # ruff check --fix
make test        # run tests
make clean       # remove caches
```

See [docs/architecture.md](docs/architecture.md) for how the pieces fit together
and [docs/scope.md](docs/scope.md) for what is deliberately out of scope.
