# 0004 — Separate collection from summarization with a durable store

**Status:** Accepted

## Context

The straightforward implementation fetches a day's activity and summarizes it
in one pass. That couples two operations with opposite requirements: collection
must be exhaustive, deterministic, and verifiable, while summarization is lossy
and non-deterministic by nature.

The prompt will be rewritten many times in the first month. Under a single-pass
design, every rewrite means re-hitting every API, and any day whose source data
has since aged out is permanently stuck with whatever the old prompt produced.

## Decision

Collectors write normalized `Event` records to a local store. A separate pass
reads a date range from the store and produces summaries. The store is the
source of truth.

## Consequences

- Prompts and models can change and days can be re-summarized with no
  re-fetching.
- Backfill is the ordinary code path with a different date range.
- Re-runs are idempotent, because events dedupe on `(source, external_id)`.
  Every collector is therefore obliged to produce a stable `external_id`.
- Weekly and monthly rollups become a second reader over the same table rather
  than a second pipeline.
- Costs an extra component and a schema to maintain. Accepted deliberately:
  it is the structural decision the rest of the design depends on.
