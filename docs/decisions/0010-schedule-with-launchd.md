# 0011 — Schedule with launchd rather than cron

**Status:** Proposed

## Context

The tool must run unattended once a day on macOS. On a laptop, cron simply
skips any run whose scheduled time falls while the machine is asleep, and gives
no indication it did so. For a tool whose entire value is uninterrupted daily
accrual, silently missing every day the laptop was closed at the scheduled hour
is a serious failure.

## Decision

Install a launchd agent using `StartCalendarInterval`, which fires on wake for
a missed interval. Ship a `bragbook install-schedule` command that writes the
plist rather than asking users to hand-author one.

## Consequences

- Runs survive sleep, which is the normal state of a laptop at any fixed hour.
- Ties scheduling to macOS. A Linux user would need a systemd timer; the
  installer should fail clearly rather than silently doing nothing.
- plist installation is fiddly enough that hand-written instructions would go
  stale, which is why it is a command.
- Missed-run recovery is still worth having independently: if the machine was
  off for two days, the next run should backfill rather than skip, which the
  store makes cheap ([0004](0004-separate-collection-from-summarization.md)).
- Not yet ratified.
