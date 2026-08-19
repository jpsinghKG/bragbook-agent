from git import GitCommandError
from git import InvalidGitRepositoryError
import os

from git import Repo, Commit, NULL_TREE
from pathlib import Path
from datetime import datetime

from models.event import Event, EventType
from collectors.git_local_collector.git_local_attributes import GitLocalCommitAttrs


class GitLocalCollector:
    def __init__(self, repo_path, include_patch=False):
        path = Path(repo_path)
        if not path.exists():
            raise FileNotFoundError(f"Repository not found at {repo_path}")
        if not path.is_dir():
            raise ValueError(f"Path {repo_path} is not a directory")

        self.repo = Repo(repo_path)
        self.include_patch = include_patch

    def getCommits(
        self,
        identities: list[str],
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
    ) -> list[Event]:
        return [
            self._commitToEvent(commit)
            for commit in self.repo.iter_commits(
                rev="--all", author=identities, since=from_datetime, until=to_datetime
            )
        ]

    def _commitToEvent(self, commit: Commit) -> Event:
        attrs = GitLocalCommitAttrs(
            repo_path=self.repo.working_tree_dir,
            files=list(commit.stats.files.keys()),
            insertions=commit.stats.total["insertions"],
            deletions=commit.stats.total["deletions"],
            is_merge=len(commit.parents) > 1,
            patch=self._patch_for(commit) if self.include_patch else None,
        )

        return Event(
            source="git",
            external_id=commit.hexsha,
            type=EventType.COMMIT,
            occurred_at=commit.authored_datetime,
            ended_at=None,
            title=commit.message.splitlines()[0] if commit.message else "",
            body="\n".join(commit.message.splitlines()[1:]) if commit.message else "",
            url=self._get_remote_url(commit.repo),
            project=Path(self.repo.working_tree_dir).name,
            subtype=None,
            attributes=attrs.model_dump(),
        )

    def _get_remote_url(self, repo: Repo) -> str | None:
        if not repo.remotes:
            return None

        for remote in repo.remotes:
            if remote.name == "origin":
                return remote.url

        return repo.remotes[0].url

    def _patch_for(self, commit) -> str:
        if commit.parents:
            diffs = commit.parents[0].diff(commit, create_patch=True)
        else:
            diffs = commit.diff(NULL_TREE, create_patch=True, R=True)

        return "\n".join(d.diff.decode() if isinstance(d.diff, bytes) else d.diff for d in diffs)


def discover_repos(
    roots: list[Path], max_depth: int = 4, exclude: frozenset[Path] = frozenset()
) -> list[Path]:
    found = []
    for root in roots:
        root = root.expanduser().resolve()

        for dirpath, dirnames, _ in os.walk(root):
            depth = len(Path(dirpath).relative_to(root).parts)
            if depth >= max_depth:
                dirnames[:] = []
                continue

            if ".git" in dirnames:
                repo = Path(dirpath)
                if repo not in exclude:
                    found.append(repo)

                dirnames[:] = [d for d in dirnames if d != ".git"]

    return found


def collect(roots, identities, since, until, include_patch=False) -> list[Event]:
    events = []
    for repo_path in discover_repos(roots):
        try:
            events.extend(GitLocalCollector(repo_path, include_patch).getCommits(identities, since, until))
        except (InvalidGitRepositoryError, GitCommandError):
            continue
        
    return events


if __name__ == "__main__":
    git_collector = GitLocalCollector("/Users/jpsingh/Documents/KG/POCs/bragbook-agent")
    git_collector.getCommits()
