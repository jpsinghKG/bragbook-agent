# 0012 — Days with no detected activity produce nothing

**Status:** Accepted

## Context

A run that finds no events can write a "no activity" entry, write nothing, or
write nothing while logging locally.

## Decision

Write nothing to the Doc and make no LLM call.

## Consequences

- The brag book stays dense. At review time it reads as a list of things
  accomplished rather than a diary with gaps to scroll past.
- No spend and no model call on quiet days.
- Silence becomes ambiguous: a broken collector, an expired token, and a
  genuine day off all produce the same empty output. This is the direct cost of
  the decision, and it makes a local run log — recording that the job ran and
  what each collector returned — effectively mandatory even though it is not
  part of the Doc.
