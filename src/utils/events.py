from __future__ import annotations

from models.event import Event, EventSource, EventType


def dedupe_commits(
    events: list[Event], preferred_source: EventSource = EventSource.GITHUB
) -> list[Event]:
    """Collapse commit events for the same SHA seen under multiple sources.

    Commits present under only one source pass through untouched; when a SHA
    shows up under preferred_source and another source, the other copy is
    dropped.
    """
    preferred_shas = {
        event.external_id
        for event in events
        if event.type == EventType.COMMIT and event.source == preferred_source
    }

    return [
        event
        for event in events
        if not (
            event.type == EventType.COMMIT
            and event.source != preferred_source
            and event.external_id in preferred_shas
        )
    ]
