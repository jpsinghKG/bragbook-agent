from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from collectors.linear_collector.linear_attributes import (
    LinearCommentAttributes,
    LinearStateTransitionAttributes,
)
from models.event import Event, EventType

LINEAR_API_URL = "https://api.linear.app/graphql"

ISSUES_QUERY = """
query MyUpdatedIssues($since: DateTimeOrDuration, $until: DateTimeOrDuration, $after: String) {
  issues(
    filter: { assignee: { isMe: { eq: true } }, updatedAt: { gte: $since, lte: $until } }
    first: 50
    after: $after
  ) {
    nodes {
      identifier
      title
      team { name }
      history(first: 50) {
        nodes {
          id
          createdAt
          fromState { name }
          toState { name }
        }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""

COMMENTS_QUERY = """
query MyComments($since: DateTimeOrDuration, $until: DateTimeOrDuration, $after: String) {
  comments(
    filter: { user: { isMe: { eq: true } }, createdAt: { gte: $since, lte: $until } }
    first: 50
    after: $after
  ) {
    nodes {
      id
      createdAt
      body
      url
      issue { identifier title team { name } }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""


class LinearCollector:
    def __init__(self):
        self.client = httpx.Client(
            base_url=LINEAR_API_URL,
            headers={
                "Authorization": os.getenv("LINEAR_API_TOKEN"),
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def _resolve_date_range(
        self, from_datetime: datetime | None, to_datetime: datetime | None
    ) -> tuple[datetime, datetime]:
        now = datetime.now(UTC)
        since = from_datetime or now - timedelta(days=1)
        until = to_datetime or now + timedelta(days=1)
        return since, until

    def _query(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        response = self.client.post("", json={"query": query, "variables": variables})
        response.raise_for_status()
        payload = response.json()
        if "errors" in payload:
            raise RuntimeError(f"Linear API error: {payload['errors']}")
        return payload["data"]

    def _paginate(self, query: str, since: str, until: str, root: str):
        after = None
        while True:
            data = self._query(query, {"since": since, "until": until, "after": after})
            connection = data[root]
            yield from connection["nodes"]
            if not connection["pageInfo"]["hasNextPage"]:
                break
            after = connection["pageInfo"]["endCursor"]

    def get_state_transitions(
        self,
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
    ) -> list[Event]:
        since, until = self._resolve_date_range(from_datetime, to_datetime)

        events = []
        for issue in self._paginate(ISSUES_QUERY, since.isoformat(), until.isoformat(), "issues"):
            for history_node in issue["history"]["nodes"]:
                if history_node["fromState"] is None or history_node["toState"] is None:
                    continue

                created_at = datetime.fromisoformat(history_node["createdAt"])
                if not (since <= created_at <= until):
                    continue

                events.append(self._transition_to_event(issue, history_node))

        return events

    def get_comments(
        self,
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
    ) -> list[Event]:
        since, until = self._resolve_date_range(from_datetime, to_datetime)

        return [
            self._comment_to_event(comment)
            for comment in self._paginate(
                COMMENTS_QUERY, since.isoformat(), until.isoformat(), "comments"
            )
        ]

    def _transition_to_event(self, issue: dict[str, Any], history_node: dict[str, Any]) -> Event:
        transition_attrs = LinearStateTransitionAttributes(
            issue_identifier=issue["identifier"],
            from_state=history_node["fromState"]["name"],
            to_state=history_node["toState"]["name"],
        )

        return Event(
            source="linear",
            external_id=history_node["id"],
            type=EventType.TICKET,
            occurred_at=history_node["createdAt"],
            ended_at=None,
            title=issue["title"],
            body=None,
            project=issue["team"]["name"],
            subtype=transition_attrs.to_state,
            attributes=transition_attrs.model_dump(),
        )

    def _comment_to_event(self, comment: dict[str, Any]) -> Event:
        comment_attrs = LinearCommentAttributes(
            issue_identifier=comment["issue"]["identifier"],
            issue_title=comment["issue"]["title"],
        )

        return Event(
            source="linear",
            external_id=comment["id"],
            type=EventType.TICKET,
            occurred_at=comment["createdAt"],
            ended_at=None,
            title=comment["issue"]["title"],
            body=comment["body"],
            url=comment["url"],
            project=comment["issue"]["team"]["name"],
            subtype="comment",
            attributes=comment_attrs.model_dump(),
        )


def collect(since, until) -> list[Event]:
    linear_collector = LinearCollector()
    return [
        *linear_collector.get_state_transitions(since, until),
        *linear_collector.get_comments(since, until),
    ]
