# 0001 — Build a local tool rather than use hosted LLM connectors

**Status:** Accepted

## Context

The obvious cheaper path was to point ChatGPT or Claude at GitHub, Jira, and
Slack through their built-in connectors and ask for a daily summary, rather
than build anything.

Summarizing a day of commits is not a differentiated capability — every model
does it well and none does it distinctively. The hard part is *collection*:
exhaustively and verifiably answering "what did I touch on Tuesday." Framed
that way, hosted products fail this specific job for three reasons:

- **Local git is invisible to them.** Connectors reach GitHub's API, not the
  filesystem. Unpushed branches, WIP, spikes never turned into PRs, and
  throwaway investigation clones are all lost — and that is exactly the work
  most easily forgotten by review season.
- **Connectors retrieve, they don't enumerate.** They are built to search
  ("find PRs about auth"), not to guarantee complete coverage of a date range.
  Missing recall is indistinguishable from genuine absence in the output, which
  is disqualifying for a record meant to be trusted months later.
- **Unattended scheduling is the entire point.** Anything requiring you to open
  a chat window and prompt it will be abandoned inside two weeks.

Hosted options do genuinely win on Slack, Jira, and Calendar authentication,
which is real work to build. That argues for adopting MCP servers for those
sources later, not for abandoning a local tool.

## Decision

Build a local tool. Treat exhaustive, verifiable collection as the product;
treat the LLM as an interchangeable component.

## Consequences

- Local git becomes available as a source, which is the single largest
  advantage over any hosted alternative.
- Collector output can be checked by hand against `git log`, so recall is
  verifiable rather than assumed.
- Authentication for every source becomes our problem. This is the main cost,
  and it is why v1 covers only git and GitHub.
