"""Normalized event record shared by every collector."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, computed_field


class EventSource(StrEnum):
    """Which collector produced this event."""

    GIT = "git"
    GITHUB = "github"
    LINEAR = "linear"


class EventType(StrEnum):
    """Small, stable category used for cross-source grouping and rollups.

    Deliberately short. A new source should map onto one of these rather
    than growing the list -- the list is what makes "how many reviews this
    week" answerable across GitHub, GitLab, and Jira at once.
    """

    COMMIT = "commit"
    PULL_REQUEST = "pull_request"
    REVIEW = "review"
    TICKET = "ticket"
    DOCUMENT = "document"
    MEETING = "meeting"
    MESSAGE = "message"


class Event(BaseModel):
    """One thing you did, normalized across sources.

    `(source, external_id)` is the dedupe key. Every collector must derive
    external_id from the artifact itself (a sha, a PR url, an issue key) so
    re-running a collector never produces a duplicate row.
    """

    source: EventSource
    external_id: str
    type: EventType
    occurred_at: datetime
    ended_at: datetime | None = None

    title: str
    body: str | None = None
    url: str | None = None

    project: str | None = None
    subtype: str | None = None

    attributes: dict[str, Any] = Field(default_factory=dict)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @computed_field
    @property
    def id(self) -> str:
        """The dedupe key, derived so it can never drift from source/external_id."""
        return f"{self.source}:{self.external_id}"
