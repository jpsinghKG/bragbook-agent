# 0002 — Python 3.13 with uv

**Status:** Accepted

## Context

TypeScript was the main alternative and would have been a reasonable choice;
both toolchains were already installed on the target machine.

## Decision

Python 3.13, managed by uv, packaged with the `uv_build` backend.

## Consequences

- The libraries this project leans on hardest — provider abstraction with typed
  structured output, TOML config validation — are more mature in Python.
- `uv sync` followed by `uv run` gives a coworker a working install with no
  virtualenv ritual and no global state, which matters for a tool intended to
  be adopted by copying a directory.
- The lockfile is committed, so a coworker's install matches a known-good one.
