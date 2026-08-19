from datetime import UTC
import os
from github import Auth, Github
from datetime import datetime, timedelta


class GithubCollector:
    def __init__(self):
        self.token = os.getenv("GITHUB_API_TOKEN")
        self.auth = Auth.Token(self.token)
        self.github = Github(auth=self.auth)

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

        print([commit.commit.raw_data for commit in list(seen.values())])
        return list(seen.values())
