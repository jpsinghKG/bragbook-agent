"""Append-only local inbox for manually logged events.

Entries are never deleted after collection -- collect() re-reads the whole
file each run and relies on the store's (source, external_id) dedupe, same
as every other collector re-polling its source.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from models.event import EventType

DEFAULT_INBOX_PATH = Path("db/user_input.jsonl")


def append_entry(
    text: str, type: EventType, when: datetime, path: Path = DEFAULT_INBOX_PATH
) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": when.isoformat(),
        "type": type.value,
        "text": text,
    }
    with path.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def read_entries(path: Path = DEFAULT_INBOX_PATH) -> list[dict]:
    if not path.exists():
        return []

    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]
