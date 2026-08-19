from collectors.github_collector.github_attributes import GithubCommitFile
from datetime import UTC
import os
from github import Auth, Github
from datetime import datetime, timedelta
from models.event import Event, EventType
from collectors.github_collector.github_attributes import GithubCommitAttributes


class GithubCollector:
    def __init__(self, include_patch: bool = False):
        self.token = os.getenv("GITHUB_API_TOKEN")
        self.auth = Auth.Token(self.token)
        self.github = Github(auth=self.auth)
        self.include_patch = include_patch

    def get_commits(
        self,
        identities: list[str],
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
    ):
        if not identities or len(identities) == 0:
            raise ValueError("Identities cannot be empty")
        if len(identities) > 2:
            raise ValueError("Number of identities cannot be greater than 2")

        now = datetime.now(UTC)
        since = from_datetime or now - timedelta(days=1)
        until = to_datetime or now + timedelta(days=1)
        date_range = f"{since:%Y-%m-%dT%H:%M:%SZ}..{until:%Y-%m-%dT%H:%M:%SZ}"

        seen = {}
        for identity in identities:
            query = f"author:{identity} author-date:{date_range}"

            for commit in self.github.search_commits(query):
                seen[commit.sha] = commit

        return [self._commit_to_event(commit) for commit in list(seen.values())]

    def _commit_to_event(self, commit) -> Event:
        commit_attrs = GithubCommitAttributes(
            files=[
                GithubCommitFile(
                    filename=file.filename,
                    insertions=file.additions,
                    deletions=file.deletions,
                    patch=file.patch if self.include_patch else None,
                )
                for file in commit.files
            ],
            insertions=commit.stats.additions,
            deletions=commit.stats.deletions,
            is_merge=len(commit.parents) > 1,
        )

        return Event(
            source="github",
            external_id=commit.sha,
            type=EventType.COMMIT,
            occurred_at=commit.commit.author.date,
            ended_at=None,
            title=commit.commit.message.splitlines()[0] if commit.commit.message else "",
            body="\n".join(commit.commit.message.splitlines()[1:]) if commit.commit.message else "",
            project=self._extract_project_from_url(commit.url),
            attributes=commit_attrs.model_dump(),
        )

    def _extract_project_from_url(self, url) -> str:
        # Expected format: https://api.github.com/repos/jpsinghKG/bragbook-agent/commits/6cc03b6826eb39e32ad4ea8cd72b3f86afc46c03
        return url.split("/repos/")[1].split("/commits/")[0].split("/")[-1]
