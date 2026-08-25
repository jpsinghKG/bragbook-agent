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
- Never cite line/insertion/deletion counts, commit counts, or file counts as \
an achievement in themselves ("461 insertions" is not an accomplishment). If \
a count is the only detail available for an item, omit the item rather than \
padding it with a number.
- Don't use generic claims of impact ("improved reliability", "increased \
functionality", "kept project momentum strong") unless the event's own title \
or body states a concrete outcome. If you can't ground a claim in the actual \
data, state the plain fact instead of dressing it up.
- Prefer the specific language from event titles/descriptions over invented \
paraphrasing.

Output in markdown format.

Here's an example format to use:
# [Date (YYYY-MM-DD)]

## Highlights

- **[Project/Theme]:** [One-liner about what was accomplished]
- **[Project/Theme]:** [One-liner about what was accomplished]
"""


class Summarizer:
    def __init__(self, system_prompt: str = SYSTEM_PROMPT):
        self.system_prompt = system_prompt

    def summarize(self, events: list[Event]) -> str:
        agent = get_agent(self.system_prompt)
        payload = json.dumps([event.model_dump(mode="json") for event in events], indent=2)
        result = agent.run_sync(f"Events:\n{payload}")
        return result.output
