# 0007 — Privacy level is configurable, global with per-repo override

**Status:** Accepted

## Context

The repositories in scope are not uniform. Some are client work, some are internal projects, some are personal side projects. A single global answer to "how much reaches the LLM" is either too permissive for client code or too restrictive to produce useful summaries of personal work.

## Decision

Three levels — metadata only, metadata plus diffstat, or full diffs — set
globally in config and overridable per repository. Redaction is applied between
the store and the LLM, not at collection time.

## Consequences

- Client repositories can be held at metadata-only while personal projects send
  diffstat or diffs, in one configuration.
- Because redaction sits downstream of the store, changing the setting takes
  effect on the next summarization without re-collecting anything. The store
  keeps what was collected; the boundary decides what leaves the machine.
- The default must be the most restrictive level. A permissive default sends
  client source to a third party on first run, before anyone has read the
  config file.
- Per-repo configuration is one more thing to keep current. A repository with
  no explicit entry inherits the global level, so a newly cloned client repo
  is governed by whatever the global default is — which is the reason that
  default has to be conservative.
