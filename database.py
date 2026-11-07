"""SQLite persistence helpers. The database file survives app restarts."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3
from flask import current_app


def _connect(path):
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def get_connection():
    connection = _connect(current_app.config["DATABASE_PATH"])
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db(path):
    """Create the required tables and indexes without removing existing data."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    schema_path = Path(__file__).resolve().parent / "database" / "schema.sql"
    connection = _connect(path)
    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()


def fetch_all(sql, params=()):
    if not isinstance(params, (tuple, list)):
        params = (params,)
    with get_connection() as connection:
        return [dict(row) for row in connection.execute(sql, params).fetchall()]


def fetch_one(sql, params=()):
    if not isinstance(params, (tuple, list)):
        params = (params,)
    with get_connection() as connection:
        row = connection.execute(sql, params).fetchone()
        return dict(row) if row else None
