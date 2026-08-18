# Scope

## Problem

Work that isn't written down is invisible at review time. Commits, pull
requests, and reviews are all recorded somewhere, but nobody assembles them
into a narrative, and reconstructing six months of work from memory produces a
thin, generic self-review.

## What this does

Once a day, unattended, it collects what you did, distills it with an LLM, and
appends an entry to a brag book. The value is entirely in it accruing while
you aren't thinking about it, so "still running in six months" outranks every
other quality.

## In scope for v1

- **Local git** across configured roots — including work on branches that were
  never pushed, which no hosted tool can see.
- **GitHub** — commits, pull requests, and reviews left on other people's PRs.
- **Daily entries** written to a single Google Doc.
- **Configurable LLM provider** — Anthropic, OpenAI, Gemini, or local Ollama.
- **Configurable privacy** — how much of your work reaches the LLM.

## Out of scope for v1

- **Calendar, Jira, Slack, Confluence.** Planned, not built.
- **Weekly and monthly rollups.** The event store is designed to support them
  as a second pass over the same data, but v1 only writes daily entries.
- **Multi-user or hosted operation.** This runs on one laptop for one person.
  It is configurable so a coworker can adopt it, not so it can be deployed.

## Non-goals

- **Not a productivity tracker.** It records what you accomplished, not how
  long you spent or how busy you looked.
- **Not exhaustive activity logging.** An entry that lists every commit is
  useless at review time. The summarizer's job is to discard.
- **Not a scale problem.** One user, one machine, one run a day. Any design
  choice made for throughput is a wrong choice here.
