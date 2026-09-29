import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "todos.db"


def get_db_path() -> Path:
    configured_path = os.getenv("TODO_DATABASE_PATH")
    if configured_path:
        return Path(configured_path).expanduser()
    return DEFAULT_DB_PATH


def ensure_db_ready() -> Path:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL CHECK (trim(text) != ''),
                completed INTEGER NOT NULL CHECK (completed IN (0, 1)) DEFAULT 0,
                notes TEXT NOT NULL DEFAULT ''
            )
            """
        )
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(todos)")
        }
        if "notes" not in columns:
            connection.execute(
                "ALTER TABLE todos ADD COLUMN notes TEXT NOT NULL DEFAULT ''"
            )
        connection.commit()
    finally:
        connection.close()

    return db_path


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection
