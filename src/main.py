from datetime import UTC
import os

from collectors.git_local_collector.git_local_collector import collect
from collectors.github_collector.github_collector import GithubCollector
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

from store import connect, upsert_events
from models.event import Event
from utils.collectors import parse_identities, parse_roots

load_dotenv()


def get_git_local_events() -> list[Event]:
    roots = parse_roots(os.getenv("GIT_LOCAL_ROOTS"))
    identities = parse_identities(os.getenv("GIT_LOCAL_IDENTITIES"))
    since = datetime.today() - timedelta(days=1)
    until = datetime.today() + timedelta(days=1)
    include_patch = False

    return collect(roots, identities, since, until, include_patch)


def get_github_events() -> list[Event]:
    identities = parse_identities(os.getenv("GITHUB_IDENTITIES"))
    now = datetime.now(UTC)
    since = now - timedelta(days=1)
    until = now + timedelta(days=1)

    github_collector = GithubCollector()
    return github_collector.get_commits(identities, since, until)


if __name__ == "__main__":
    git_local_events = get_git_local_events()
    github_events = get_github_events()

    events = [*git_local_events, *github_events]

    conn = connect(Path("db/bragbook.db"))
    upsert_events(conn, events)
