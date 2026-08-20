from __future__ import annotations

from pydantic import BaseModel


class LinearStateTransitionAttributes(BaseModel):
    issue_identifier: str
    from_state: str | None
    to_state: str


class LinearCommentAttributes(BaseModel):
    issue_identifier: str
    issue_title: str
