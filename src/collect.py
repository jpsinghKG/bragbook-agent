"""Collection-only pipeline: gathers events and upserts them into the store.

Deliberately stops short of redaction and summarization -- those happen on
demand when the user runs main.py, not on the schedule.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from collectors.git_local_collector.git_local_collector import collect as collect_git_local_events
from collectors.github_collector.github_collector import collect as collect_github_events
from collectors.linear_collector.linear_collector import collect as collect_linear_events
from collectors.user_input_collector.user_input_collector import (
    collect as collect_user_input_events,
)
from config.settings import Settings
from store import connect, upsert_events
from utils.events import dedupe_commits

DB_PATH = Path("db/bragbook.db")


def run(settings: Settings) -> tuple[datetime, datetime]:
    """Collect from every enabled source and upsert into the store.

    Returns the (since, until) window that was collected, so callers can
    query the store for the same range without recomputing "now" themselves.
    """
    now = datetime.now(UTC)
    since = now - timedelta(days=settings.app.days_since)
    until = now + timedelta(days=1)

    git_local_events = (
        collect_git_local_events(
            settings.git_local.roots,
            settings.git_local.identities,
            since,
            until,
            settings.git_local.include_patch,
        )
        if settings.sources.git_local
        else []
    )
    github_events = (
        collect_github_events(
            settings.github.identities, since, until, settings.github.include_patch
        )
        if settings.sources.github
        else []
    )
    linear_events = collect_linear_events(since, until) if settings.sources.linear else []
    user_input_events = (
        collect_user_input_events(since, until) if settings.sources.user_input else []
    )

    events = dedupe_commits(
        [*git_local_events, *github_events, *linear_events, *user_input_events]
    )

    conn = connect(DB_PATH)
    upsert_events(conn, events)

    return since, until
