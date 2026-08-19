from __future__ import annotations

from pydantic import BaseModel, Field


class GithubCommitFile(BaseModel):
    filename: str
    insertions: int = 0
    deletions: int = 0
    patch: str | None = None


class GithubCommitAttributes(BaseModel):
    files: list[GithubCommitFile] = Field(default_factory=list)
    insertions: int = 0
    deletions: int = 0
    is_merge: bool = False
