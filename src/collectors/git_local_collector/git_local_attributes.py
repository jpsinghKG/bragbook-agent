from __future__ import annotations

from pydantic import BaseModel, Field


class GitLocalCommitAttrs(BaseModel):
    repo_path: str
    files: list[str] = Field(default_factory=list)
    insertions: int = 0
    deletions: int = 0
    is_merge: bool = False
    patch: str | None = None  # full diff text; redaction decides if the LLM sees it
