"""DuckDB storage layer for Daily Stack."""

import os
from datetime import datetime, timezone

import duckdb

DB_DIR = os.path.expanduser("~/data/daily-stack")
DB_PATH = os.path.join(DB_DIR, "daily-stack.duckdb")

_conn = None


def get_conn() -> duckdb.DuckDBPyConnection:
    """Return a module-level DuckDB connection, creating DB dir + schema if needed."""
    global _conn
    if _conn is not None:
        return _conn
    os.makedirs(DB_DIR, exist_ok=True)
    _conn = duckdb.connect(DB_PATH)
    _init_schema(_conn)
    return _conn


def _init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            date      VARCHAR NOT NULL,
            habit_id  VARCHAR NOT NULL,
            done      BOOLEAN NOT NULL DEFAULT true,
            toggled_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
            PRIMARY KEY (date, habit_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS focus (
            date       VARCHAR PRIMARY KEY,
            text       VARCHAR NOT NULL DEFAULT '',
            updated_at TIMESTAMP NOT NULL DEFAULT current_timestamp
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            date       VARCHAR PRIMARY KEY,
            text       VARCHAR NOT NULL DEFAULT '',
            updated_at TIMESTAMP NOT NULL DEFAULT current_timestamp
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS journal (
            date       VARCHAR NOT NULL,
            period     VARCHAR NOT NULL,
            text       VARCHAR NOT NULL DEFAULT '',
            updated_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
            PRIMARY KEY (date, period)
        )
    """)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Habits ---


def upsert_habit(date: str, habit_id: str, done: bool) -> None:
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO habits (date, habit_id, done, toggled_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (date, habit_id)
        DO UPDATE SET done = excluded.done, toggled_at = excluded.toggled_at
        """,
        [date, habit_id, done, _now()],
    )


def get_habits(date: str) -> dict[str, bool]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT habit_id, done FROM habits WHERE date = ?", [date]
    ).fetchall()
    return {row[0]: row[1] for row in rows if row[1]}


# --- Focus ---


def upsert_focus(date: str, text: str) -> None:
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO focus (date, text, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT (date)
        DO UPDATE SET text = excluded.text, updated_at = excluded.updated_at
        """,
        [date, text, _now()],
    )


def get_focus(date: str) -> dict:
    conn = get_conn()
    row = conn.execute(
        "SELECT text, updated_at FROM focus WHERE date = ?", [date]
    ).fetchone()
    if not row:
        return {"text": "", "updated_at": None}
    return {"text": row[0], "updated_at": str(row[1])}


# --- Reflections ---


def upsert_reflection(date: str, text: str) -> None:
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO reflections (date, text, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT (date)
        DO UPDATE SET text = excluded.text, updated_at = excluded.updated_at
        """,
        [date, text, _now()],
    )


def get_reflection(date: str) -> dict:
    conn = get_conn()
    row = conn.execute(
        "SELECT text, updated_at FROM reflections WHERE date = ?", [date]
    ).fetchone()
    if not row:
        return {"text": "", "updated_at": None}
    return {"text": row[0], "updated_at": str(row[1])}


# --- Journal ---


def upsert_journal(date: str, period: str, text: str) -> None:
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO journal (date, period, text, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (date, period)
        DO UPDATE SET text = excluded.text, updated_at = excluded.updated_at
        """,
        [date, period, text, _now()],
    )


def get_journal(date: str) -> dict:
    conn = get_conn()
    rows = conn.execute(
        "SELECT period, text, updated_at FROM journal WHERE date = ?", [date]
    ).fetchall()
    result = {
        "morning": {"text": "", "updated_at": None},
        "evening": {"text": "", "updated_at": None},
    }
    for period, text, updated_at in rows:
        result[period] = {"text": text, "updated_at": str(updated_at)}
    return result


# --- Export ---


def export_all() -> dict:
    conn = get_conn()

    habits_rows = conn.execute(
        "SELECT date, habit_id, done, toggled_at FROM habits ORDER BY date, habit_id"
    ).fetchall()
    habits = {}
    for date, habit_id, done, toggled_at in habits_rows:
        habits.setdefault(date, {})[habit_id] = {
            "done": done,
            "toggled_at": str(toggled_at),
        }

    focus_rows = conn.execute(
        "SELECT date, text, updated_at FROM focus ORDER BY date"
    ).fetchall()
    focus = {row[0]: {"text": row[1], "updated_at": str(row[2])} for row in focus_rows}

    reflection_rows = conn.execute(
        "SELECT date, text, updated_at FROM reflections ORDER BY date"
    ).fetchall()
    reflections = {
        row[0]: {"text": row[1], "updated_at": str(row[2])} for row in reflection_rows
    }

    journal_rows = conn.execute(
        "SELECT date, period, text, updated_at FROM journal ORDER BY date, period"
    ).fetchall()
    journal = {}
    for date, period, text, updated_at in journal_rows:
        journal.setdefault(date, {})[period] = {
            "text": text,
            "updated_at": str(updated_at),
        }

    return {
        "habits": habits,
        "focus": focus,
        "reflections": reflections,
        "journal": journal,
    }
