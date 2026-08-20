from datetime import UTC
import os

from collectors.git_local_collector.git_local_collector import collect as collect_git_local_events
from collectors.github_collector.github_collector import collect as collect_github_events
from collectors.linear_collector.linear_collector import collect as collect_linear_events
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

from store import connect, upsert_events
from models.event import Event
from utils.collectors import parse_identities, parse_roots

load_dotenv()

now = datetime.now(UTC)
since = now - timedelta(days=1)
until = now + timedelta(days=1)


def get_git_local_events() -> list[Event]:
    roots = parse_roots(os.getenv("GIT_LOCAL_ROOTS"))
    identities = parse_identities(os.getenv("GIT_LOCAL_IDENTITIES"))
    include_patch = False

    return collect_git_local_events(roots, identities, since, until, include_patch)


def get_github_events() -> list[Event]:
    identities = parse_identities(os.getenv("GITHUB_IDENTITIES"))
    include_patch = False

    return collect_github_events(identities, since, until, include_patch)


if __name__ == "__main__":
    git_local_events = get_git_local_events()
    github_events = get_github_events()
    linear_events = collect_linear_events(since, until)

    events = [
        *git_local_events, 
        *github_events, 
        *linear_events
    ]

    conn = connect(Path("db/bragbook.db"))
    upsert_events(conn, events)
