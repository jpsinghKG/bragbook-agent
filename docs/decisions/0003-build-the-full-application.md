# 0003 — Build the structured application, not the shell + `claude -p` hybrid

**Status:** Accepted — supersedes an earlier recommendation

## Context

An initial recommendation was to start with roughly two hours of work: a
deterministic shell script for collection plus headless `claude -p` for
summarization, scheduled with launchd. The reasoning was that most people who
build the full application first never run it for six months, and a brag book's
value is entirely in accruing unattended.

That recommendation assumed the summarizer would ride on an existing Claude
Code subscription. Once the requirement became a configurable provider across
Anthropic, OpenAI, Gemini, and Ollama
([0006](0006-configurable-llm-provider.md)), plus configurable per-repo privacy
levels ([0007](0007-configurable-privacy-levels.md)) and a Google Docs sink,
the shell version would have had to grow all of that anyway — in bash, without
config validation.

## Decision

Build the structured Python application directly.

## Consequences

- Higher up-front cost before the first entry is written, and a correspondingly
  higher risk of the tool never reaching daily use. This is the real trade being
  accepted, and it is the failure mode to watch for.
- Configuration, provider swap, and privacy controls land in a place where they
  can be validated and tested, rather than as unvalidated shell variables.
- The shell prototype's collection logic is not wasted work conceptually — the
  same `git log` and `gh` invocations become the collectors.
