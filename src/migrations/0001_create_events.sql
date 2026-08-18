CREATE TABLE IF NOT EXISTS events (
    id           TEXT PRIMARY KEY,
    source       TEXT NOT NULL,
    external_id  TEXT NOT NULL,
    type         TEXT NOT NULL,
    occurred_at  TEXT NOT NULL,
    ended_at     TEXT,
    title        TEXT NOT NULL,
    body         TEXT,
    url          TEXT,
    project      TEXT,
    subtype      TEXT,
    attributes   TEXT NOT NULL DEFAULT '{}',
    collected_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_occurred_at ON events (occurred_at);
