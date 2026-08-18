# Architecture

## Shape

```
                  ┌──────────────┐
  scheduler ─────►│  collectors  │  deterministic, no LLM
  (launchd)       │  git, github │
                  └──────┬───────┘
                         │ Event records
                         ▼
                  ┌──────────────┐
                  │ event store  │  source of truth (local, on disk)
                  │   (sqlite)   │
                  └──────┬───────┘
                         │ one day's events
                         ▼
                  ┌──────────────┐
                  │  redaction   │  applies the configured privacy level
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │  summarizer  │  the only component that calls an LLM
                  │ (pydantic-ai)│
                  └──────┬───────┘
                         │ DayDigest
                         ▼
                  ┌──────────────┐
                  │  Google Doc  │  rendered mirror
                  └──────────────┘
```

## Why the store sits in the middle

Collection and summarization are separated by a durable store rather than
being one pass. This is the central structural decision
([0004](decisions/0004-separate-collection-from-summarization.md)) and
everything else follows from it:

- Prompts can be rewritten and days re-summarized without re-fetching anything.
- Backfill is the same code path as a normal run, with a different date range.
- Re-runs are idempotent, because events dedupe on `(source, external_id)`.
- Weekly and monthly rollups are a second reader of the same table, not a
  second collection pipeline.

Collection must be _exhaustive and verifiable_ — you can diff a collector's
output against `git log` and know it is right. Summarization is inherently
lossy and non-deterministic. Keeping them on opposite sides of a boundary means
a bad summary never costs you the underlying record.

## Components

**Collectors** turn one source into `Event` records. Each produces a stable
`external_id` per artifact so re-runs dedupe. Collectors never call an LLM and
never decide what matters — they gather. Adding a source means adding a
collector, not touching anything downstream.

**Event store** holds normalized events on disk. Append-only in practice;
the dedupe key makes writes idempotent.

**Redaction** applies the configured privacy level
([0007](decisions/0007-configurable-privacy-levels.md)) between the store and
the LLM. The store keeps whatever was collected; this layer decides what
leaves the machine. Placing it here rather than in the collectors means
changing the privacy setting doesn't require re-collecting.

**Summarizer** reads a day's redacted events and returns a structured
`DayDigest`. The only LLM call in the system, behind a provider abstraction
([0006](decisions/0006-configurable-llm-provider.md)).

**Sink** renders digests into the Google Doc. The Doc is written _from_ the
store and is never read back as authoritative
([0005](decisions/0005-google-doc-is-a-mirror.md)).

## Planned module layout

```
src/bragbook/
  cli.py              typer entry point
  config.py           TOML schema, validated on load
  models.py           Event, DayDigest, Accomplishment
  store.py            sqlite persistence
  redact.py           privacy levels
  llm.py              provider abstraction
  summarize.py        events -> DayDigest
  collectors/
    git_local.py
    github.py
  sinks/
    gdocs.py
  schedule.py         launchd plist installation
```

## Failure posture

A run that collects nothing writes nothing
([0011](decisions/0011-skip-empty-days.md)). A collector that fails should not
prevent the others from writing their events — a broken GitHub token should
cost you the GitHub half of a day, not the whole day. Because the store is the
source of truth and summarization is re-runnable, any day damaged by a partial
failure can be re-collected and re-summarized later without manual repair.
