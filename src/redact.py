from __future__ import annotations

from typing import Any

from models.event import Event
from models.redaction_level import RedactionLevel

# Field names dropped wherever they appear in an event's attributes, regardless
# of which collector produced them (git patches, filenames, links, free-text
# titles duplicated inside attributes, labels, branch names).
SENSITIVE_ATTRIBUTE_KEYS = {
    "patch",
    "filename",
    "files",
    "repo_path",
    "url",
    "pr_url",
    "labels",
    "base_branch",
    "head_branch",
}


class Redactor:
    def __init__(self, redaction_level: RedactionLevel):
        self.redaction_level = redaction_level

    def redact(self, events: list[Event]) -> list[Event]:
        return [self.redact_event(event) for event in events]

    def redact_event(self, event: Event) -> Event:
        if self.redaction_level == RedactionLevel.NONE:
            return event

        data = event.model_dump(exclude={"id"})
        data["title"] = ""
        data["body"] = None
        data["url"] = None
        data["attributes"] = self._strip_sensitive(data["attributes"])
        return Event(**data)

    def _strip_sensitive(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: self._strip_sensitive(val)
                for key, val in value.items()
                if key not in SENSITIVE_ATTRIBUTE_KEYS
            }
        if isinstance(value, list):
            return [self._strip_sensitive(item) for item in value]
        return value
