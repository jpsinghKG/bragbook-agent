from __future__ import annotations

from datetime import datetime

import typer

from collectors.user_input_collector.inbox import append_entry
from models.event import EventType

app = typer.Typer()


@app.command()
def log(
    text: str,
    type: EventType = typer.Option(
        EventType.MESSAGE, "--type", "-t", help="Event type for this entry."
    ),
) -> None:
    """Record something you did that no collector would otherwise catch."""
    entry = append_entry(text, type, when=datetime.now().astimezone())
    typer.echo(f"logged ({entry['type']}): {entry['text']}")


if __name__ == "__main__":
    app()
