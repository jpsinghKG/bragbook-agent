from datetime import UTC

from collectors.git_local_collector.git_local_collector import collect as collect_git_local_events
from collectors.github_collector.github_collector import collect as collect_github_events
from collectors.linear_collector.linear_collector import collect as collect_linear_events
from collectors.user_input_collector.user_input_collector import (
    collect as collect_user_input_events,
)
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

from store import connect, upsert_events, get_events
from redact import Redactor
from summarize import Summarizer
from sinks.markdown import write_markdown
from models.event import Event
from utils.events import dedupe_commits
from config.settings import Settings

load_dotenv()

settings = Settings()
now = datetime.now(UTC)
since = now - timedelta(days=settings.app.days_since)
until = now + timedelta(days=1)


def get_git_local_events() -> list[Event]:
    roots = settings.git_local.roots
    identities = settings.git_local.identities
    include_patch = settings.git_local.include_patch

    return collect_git_local_events(roots, identities, since, until, include_patch)


def get_github_events() -> list[Event]:
    identities = settings.github.identities
    include_patch = settings.github.include_patch

    return collect_github_events(identities, since, until, include_patch)


if __name__ == "__main__":
    # collect and persist events
    git_local_events = get_git_local_events() if settings.sources.git_local else []
    github_events = get_github_events() if settings.sources.github else []
    linear_events = collect_linear_events(since, until) if settings.sources.linear else []
    user_input_events = (
        collect_user_input_events(since, until) if settings.sources.user_input else []
    )

    events = dedupe_commits(
        [
            *git_local_events,
            *github_events,
            *linear_events,
            *user_input_events,
        ]
    )

    conn = connect(Path("db/bragbook.db"))
    upsert_events(conn, events)

    # redact
    events = get_events(conn, since, until)

    redactor = Redactor(settings.app.redaction_level)
    redacted_events = redactor.redact(events)

    if not redacted_events:
        print("no events today, skipping summary")
    else:
        # summarize
        summarizer = Summarizer()
        summary = summarizer.summarize(
            redacted_events, settings.llm.provider, settings.llm.model, settings.llm.max_tokens
        )

        # persist to md or gdoc
        path = write_markdown(summary, now)
        print(f"wrote summary to {path}")
