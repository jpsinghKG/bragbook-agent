# 0005 — Output to a Google Doc, treated as a mirror

**Status:** Accepted

## Context

The requested output was a single Google Doc with daily entries. Markdown files
in a git repository were the proposed alternative, and were rejected in favour
of the Doc.

Two problems come with that choice. The Docs API requires a Google Cloud
project, an OAuth consent screen, and a hand-downloaded `credentials.json` —
roughly fifteen minutes of manual setup that cannot be scripted. More
importantly, a Doc has no dedupe: appending to it blind means a re-run or a
backfill can silently write a day twice, with no reliable way to detect it.

## Decision

Keep the Google Doc as the output, but write it *from* the local event store
rather than treating it as the record. The store determines which days exist
and what they contain; the sync step renders them into the Doc in order. The
Doc is never read back as authoritative.

## Consequences

- The requested output is delivered, without the append-blind duplication risk.
- Collection and summarization work from day one while OAuth setup is still
  pending — the Doc sink is the last wire, not a prerequisite.
- A Doc edited by hand will be overwritten or diverge. Hand annotations belong
  in a separate document until an explicit merge story exists.
- Weekly and monthly rollups later are a different renderer over the same
  store, not a rewrite.
