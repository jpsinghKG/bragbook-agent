from __future__ import annotations

from datetime import datetime
from pathlib import Path

SUMMARIES_DIR = Path("summaries")


def write_markdown(summary: str, when: datetime) -> Path:
    """Write summary to summaries/<local-date>.md, appending if today's file exists."""
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

    local_date = when.astimezone().date()
    path = SUMMARIES_DIR / f"{local_date:%Y-%m-%d}.md"

    is_new = not path.exists() or path.stat().st_size == 0
    with path.open("a") as f:
        if not is_new:
            f.write("\n\n---\n\n")
        f.write(summary.strip() + "\n")

    return path
