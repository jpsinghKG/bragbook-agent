from __future__ import annotations

from datetime import datetime
from pathlib import Path

from collectors.user_input_collector.inbox import DEFAULT_INBOX_PATH, read_entries
from models.event import Event, EventSource, EventType


def collect(
    since: datetime,
    until: datetime,
    inbox_path: Path = DEFAULT_INBOX_PATH,
) -> list[Event]:
    events = []
    for entry in read_entries(inbox_path):
        occurred_at = datetime.fromisoformat(entry["timestamp"])
        if not (since <= occurred_at < until):
            continue

        events.append(
            Event(
                source=EventSource.USER_INPUT,
                external_id=entry["id"],
                type=EventType(entry["type"]),
                occurred_at=occurred_at,
                title=entry["text"],
            )
        )

    return events
