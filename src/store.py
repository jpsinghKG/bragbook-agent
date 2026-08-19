from __future__ import annotations

import json
import logging
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from models.event import Event, EventType

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

logger = logging.getLogger(__name__)


def connect(db_path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    migrate(conn)

    return conn


def migrate(conn: sqlite3.Connection) -> list[str]:
    """Apply any migration file not yet recorded as applied, in filename order."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )

    applied = {row["version"] for row in conn.execute("SELECT version FROM schema_migrations")}

    newly_applied = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = path.stem
        if version in applied:
            continue

        with conn:
            conn.executescript(path.read_text())
            conn.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                (version, datetime.now(UTC).isoformat()),
            )

        newly_applied.append(version)

    return newly_applied


def upsert_events(conn: sqlite3.Connection, events: list[Event]) -> None:
    """Insert events, refreshing any that already exist under the same id.

    collected_at is deliberately left out of the update clause: it records
    when an event was first observed, not when it was last re-collected.
    """
    with conn:
        cursor = conn.executemany(
            """
            INSERT INTO events (
                id, source, external_id, type, occurred_at, ended_at,
                title, body, url, project, subtype, attributes, collected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                type        = excluded.type,
                occurred_at = excluded.occurred_at,
                ended_at    = excluded.ended_at,
                title       = excluded.title,
                body        = excluded.body,
                url         = excluded.url,
                project     = excluded.project,
                subtype     = excluded.subtype,
                attributes  = excluded.attributes
            """,
            [
                (
                    e.id,
                    e.source,
                    e.external_id,
                    e.type.value,
                    e.occurred_at.isoformat(),
                    e.ended_at.isoformat() if e.ended_at else None,
                    e.title,
                    e.body,
                    e.url,
                    e.project,
                    e.subtype,
                    json.dumps(e.attributes),
                    e.collected_at.isoformat(),
                )
                for e in events
            ],
        )

    logger.debug("upserted %d events (rowcount=%d)", len(events), cursor.rowcount)


def get_events(
    conn: sqlite3.Connection,
    since: datetime | None = None,
    until: datetime | None = None,
) -> list[Event]:
    """Read events back in occurred_at order, optionally bounded by a range."""
    query = "SELECT * FROM events"
    clauses, params = [], []

    if since is not None:
        clauses.append("occurred_at >= ?")
        params.append(since.isoformat())

    if until is not None:
        clauses.append("occurred_at < ?")
        params.append(until.isoformat())

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    query += " ORDER BY occurred_at"

    rows = conn.execute(query, params).fetchall()
    return [_row_to_event(row) for row in rows]


def _row_to_event(row: sqlite3.Row) -> Event:
    return Event(
        source=row["source"],
        external_id=row["external_id"],
        type=EventType(row["type"]),
        occurred_at=datetime.fromisoformat(row["occurred_at"]),
        ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
        title=row["title"],
        body=row["body"],
        url=row["url"],
        project=row["project"],
        subtype=row["subtype"],
        attributes=json.loads(row["attributes"]),
        collected_at=datetime.fromisoformat(row["collected_at"]),
    )
