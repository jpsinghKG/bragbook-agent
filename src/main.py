from datetime import UTC, datetime

from dotenv import load_dotenv

import collect
from config.settings import Settings
from redact import Redactor
from sinks.markdown import write_markdown
from store import connect, get_events
from summarize import Summarizer

load_dotenv()

settings = Settings()

if __name__ == "__main__":
    # collect and persist events
    since, until = collect.run(settings)

    # redact
    conn = connect(collect.DB_PATH)
    events = get_events(conn, since, until)

    redactor = Redactor(settings.app.redaction_level)
    redacted_events = redactor.redact(events)

    if not redacted_events:
        print("no events today, skipping summary")
    else:
        # summarize
        summarizer = Summarizer()
        summary = summarizer.summarize(
            redacted_events, settings.llm.provider, settings.llm.model, settings.llm.max_tokens
        )

        # persist to md or gdoc
        path = write_markdown(summary, datetime.now(UTC))
        print(f"wrote summary to {path}")
