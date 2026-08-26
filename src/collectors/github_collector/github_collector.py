from datetime import UTC
import os
from github import Auth, Github
from datetime import datetime, timedelta
from models.event import Event, EventSource, EventType
from collectors.github_collector.github_attributes import (
    GithubCommitAttributes,
    GithubCommitFile,
    GithubIssueAttributes,
    GithubPullRequestAttributes,
    GithubPullRequestFile,
    GithubReviewAttributes,
)


class GithubCollector:
    def __init__(self, include_patch: bool = False):
        self.token = os.getenv("GITHUB_API_TOKEN")
        self.auth = Auth.Token(self.token)
        self.github = Github(auth=self.auth)
        self.include_patch = include_patch

    def _validate_identities(self, identities: list[str]) -> None:
        if not identities:
            raise ValueError("Identities cannot be empty")
        if len(identities) > 2:
            raise ValueError("Number of identities cannot be greater than 2")

    def _resolve_date_range(
        self, from_datetime: datetime | None, to_datetime: datetime | None
    ) -> tuple[datetime, datetime, str]:
        now = datetime.now(UTC)
        since = from_datetime or now - timedelta(days=1)
        until = to_datetime or now + timedelta(days=1)
        return since, until, f"{since:%Y-%m-%dT%H:%M:%SZ}..{until:%Y-%m-%dT%H:%M:%SZ}"

    def get_commits(
        self,
        identities: list[str],
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
    ):
        self._validate_identities(identities)
        _, _, date_range = self._resolve_date_range(from_datetime, to_datetime)

        seen = {}
        for identity in identities:
            query = f"author:{identity} author-date:{date_range}"

            for commit in self.github.search_commits(query):
                seen[commit.sha] = commit

        return [self._commit_to_event(commit) for commit in list(seen.values())]

    def get_pull_requests(
        self,
        identities: list[str],
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
    ):
        self._validate_identities(identities)
        _, _, date_range = self._resolve_date_range(from_datetime, to_datetime)

        seen = {}
        for identity in identities:
            query = f"author:{identity} type:pr updated:{date_range}"

            for issue in self.github.search_issues(query):
                pr = issue.as_pull_request()
                seen[pr.id] = pr

        return [self._pr_to_event(pr) for pr in list(seen.values())]

    def get_issues(
        self,
        identities: list[str],
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
    ):
        self._validate_identities(identities)
        _, _, date_range = self._resolve_date_range(from_datetime, to_datetime)

        seen = {}
        for identity in identities:
            query = f"author:{identity} type:issue updated:{date_range}"

            for issue in self.github.search_issues(query):
                seen[issue.id] = issue

        return [self._issue_to_event(issue) for issue in list(seen.values())]

    def get_reviews(
        self,
        identities: list[str],
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
    ):
        self._validate_identities(identities)
        since, until, date_range = self._resolve_date_range(from_datetime, to_datetime)
        lowered_identities = {identity.lower() for identity in identities}

        seen = {}
        for identity in identities:
            query = f"type:pr reviewed-by:{identity} updated:{date_range}"

            for issue in self.github.search_issues(query):
                pr = issue.as_pull_request()

                for review in pr.get_reviews():
                    if review.user.login.lower() not in lowered_identities:
                        continue
                    if review.submitted_at is None or not (since <= review.submitted_at <= until):
                        continue

                    seen[review.id] = (pr, review)

        return [self._review_to_event(pr, review) for pr, review in seen.values()]

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
            source=EventSource.GITHUB,
            external_id=commit.sha,
            type=EventType.COMMIT,
            occurred_at=commit.commit.author.date,
            ended_at=None,
            title=commit.commit.message.splitlines()[0] if commit.commit.message else "",
            body="\n".join(commit.commit.message.splitlines()[1:]) if commit.commit.message else "",
            project=self._extract_project_from_url(commit.url),
            attributes=commit_attrs.model_dump(),
        )

    def _pr_to_event(self, pr) -> Event:
        pr_attrs = GithubPullRequestAttributes(
            state="merged" if pr.merged else pr.state,
            merged=pr.merged,
            draft=pr.draft,
            base_branch=pr.base.ref,
            head_branch=pr.head.ref,
            insertions=pr.additions,
            deletions=pr.deletions,
            changed_files=pr.changed_files,
            commits=pr.commits,
            files=[
                GithubPullRequestFile(
                    filename=file.filename,
                    insertions=file.additions,
                    deletions=file.deletions,
                    patch=file.patch,
                )
                for file in pr.get_files()
            ]
            if self.include_patch
            else [],
        )

        return Event(
            source=EventSource.GITHUB,
            external_id=str(pr.id),
            type=EventType.PULL_REQUEST,
            occurred_at=pr.created_at,
            ended_at=pr.merged_at or pr.closed_at,
            title=pr.title,
            body=pr.body,
            url=pr.html_url,
            project=pr.base.repo.name,
            subtype=pr_attrs.state,
            attributes=pr_attrs.model_dump(),
        )

    def _issue_to_event(self, issue) -> Event:
        issue_attrs = GithubIssueAttributes(
            state=issue.state,
            comments=issue.comments,
            labels=[label.name for label in issue.labels],
        )

        return Event(
            source=EventSource.GITHUB,
            external_id=str(issue.id),
            type=EventType.TICKET,
            occurred_at=issue.created_at,
            ended_at=issue.closed_at,
            title=issue.title,
            body=issue.body,
            url=issue.html_url,
            project=issue.repository.name,
            subtype=issue_attrs.state,
            attributes=issue_attrs.model_dump(),
        )

    def _review_to_event(self, pr, review) -> Event:
        review_attrs = GithubReviewAttributes(
            state=review.state.lower(),
            pr_number=pr.number,
            pr_title=pr.title,
            pr_url=pr.html_url,
        )

        return Event(
            source=EventSource.GITHUB,
            external_id=str(review.id),
            type=EventType.REVIEW,
            occurred_at=review.submitted_at,
            ended_at=None,
            title=pr.title,
            body=review.body,
            url=review.html_url,
            project=pr.base.repo.name,
            subtype=review_attrs.state,
            attributes=review_attrs.model_dump(),
        )

    def _extract_project_from_url(self, url) -> str:
        # Expected format: https://api.github.com/repos/jpsinghKG/bragbook-agent/commits/6cc03b6826eb39e32ad4ea8cd72b3f86afc46c03
        return url.split("/repos/")[1].split("/commits/")[0].split("/")[-1]


def collect(identities, since, until, include_patch=False) -> list[Event]:
    github_collector = GithubCollector(include_patch)
    return [
        *github_collector.get_commits(identities, since, until),
        *github_collector.get_pull_requests(identities, since, until),
        *github_collector.get_issues(identities, since, until),
        *github_collector.get_reviews(identities, since, until),
    ]
