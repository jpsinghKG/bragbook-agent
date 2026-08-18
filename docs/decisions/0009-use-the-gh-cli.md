# 0009 — Use the `gh` CLI rather than a GitHub API client

**Status:** Proposed

## Context

GitHub collection can go through a library such as PyGithub, or shell out to
the `gh` CLI. `gh` is already installed and authenticated on the target machine and is
near-universal among developers who would adopt this.

## Decision

Shell out to `gh` with `--json` output.

## Consequences

- No token provisioning, storage, or refresh in this project. Authentication is
  something the user already did, and `gh auth status` is the diagnostic.
- Pagination and rate limiting are handled by `gh`.
- Adds a runtime dependency on an external binary and its output format. The
  `--json` interface is stable enough for this, but it is a real coupling.
- If `gh` is missing or logged out, the GitHub collector fails while others
  continue — the failure posture described in the architecture doc.
- Not yet ratified.
