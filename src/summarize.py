from __future__ import annotations

import json

from llm import get_agent
from models.event import Event

# Starter draft — edit freely, this is the whole contract for output formatting.
SYSTEM_PROMPT = """\
You are writing a daily brag-book entry: a short, achievement-oriented summary \
of the work reflected in the events below, written in first person past tense \
as if the author is documenting their own accomplishments for a future \
performance review.

Guidelines:
- Group related activity by project when it clarifies impact, but keep the \
whole thing brief — a few sentences to a short paragraph, not a bulleted \
changelog.
- Lead with outcomes and impact, not mechanics (e.g. "shipped the Linear \
collector" rather than "made 12 commits").
- Only claim what the events actually support — no embellishing beyond what's \
in the data.
- Skip incidental noise (e.g. a single typo-fix commit) unless it's the only \
thing that happened.
- If the events list is empty, say so plainly rather than inventing activity.

Output in markdown format.

Here's an example format to use:
# [Date (YYYY-MM-DD)]

## Highlights

- **[Project/Theme]:** [One-liner about what was accomplished]
- **[Project/Theme]:** [One-liner about what was accomplished]

## What I Did

- [Specific achievement 1 and its impact]
- [Specific achievement 2 and its impact]
- [Specific achievement 3 and its impact]
"""


class Summarizer:
    def __init__(self, system_prompt: str = SYSTEM_PROMPT):
        self.system_prompt = system_prompt

    def summarize(self, events: list[Event]) -> str:
        agent = get_agent(self.system_prompt)
        payload = json.dumps([event.model_dump(mode="json") for event in events], indent=2)
        result = agent.run_sync(f"Events:\n{payload}")
        return result.output
