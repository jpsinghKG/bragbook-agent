# 0008 — Identity is explicit configuration, never inferred

**Status:** Accepted

## Context

Attribution turned out to be non-trivial on the target machine. The global
git config names only the noreply one, so trusting `git config user.email`
would silently drop most of the person's own commits. GitHub, GitLab, Jira, and
Slack each add another distinct handle.

## Decision

An `identity` block in config lists every email and account handle that counts
as the user. All collectors match against it. Nothing is inferred from
`git config` or from the environment.

## Consequences

- Adding a source means adding its handle to one place rather than teaching
  each collector how to recognize the user.
- Silent under-collection is the characteristic failure of this system: a
  missing address produces an empty day, which looks exactly like a day off.
  A `bragbook doctor`-style check that reports events found per identity per
  source is worth building early for this reason.
- A forgotten address means quietly missing work for as long as it goes
  unnoticed.
