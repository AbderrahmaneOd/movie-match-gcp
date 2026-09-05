import os
import sqlite3

from flask import g


def get_db(app):
    if "database" not in g:
        conn = sqlite3.connect(app.config["DATABASE_PATH"])
        conn.row_factory = sqlite3.Row
        g.database = conn
    return g.database


def close_db(error=None):
    conn = g.pop("database", None)
    if conn is not None:
        conn.close()


def init_db(app):
    db_path = app.config["DATABASE_PATH"]
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            movie_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            poster_path TEXT,
            release_date TEXT,
            vote_average REAL,
            year INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE (session_id, movie_id)
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            movie_id INTEGER,
            session_id TEXT,
            metadata TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_favorites_session
            ON favorites (session_id);
        CREATE INDEX IF NOT EXISTS idx_events_type
            ON events (event_type);
        """
    )
    conn.close()