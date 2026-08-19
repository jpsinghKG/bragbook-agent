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


class GithubPullRequestFile(BaseModel):
    filename: str
    insertions: int = 0
    deletions: int = 0
    patch: str | None = None


class GithubIssueAttributes(BaseModel):
    state: str
    comments: int = 0
    labels: list[str] = Field(default_factory=list)


class GithubPullRequestAttributes(BaseModel):
    state: str
    merged: bool = False
    draft: bool = False
    base_branch: str
    head_branch: str
    insertions: int = 0
    deletions: int = 0
    changed_files: int = 0
    commits: int = 0
    files: list[GithubPullRequestFile] = Field(default_factory=list)


class GithubReviewAttributes(BaseModel):
    state: str
    pr_number: int
    pr_title: str
    pr_url: str
