"""State persistence: SQLite checkpointer for resumable long-running tasks."""

import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

from .config import DEFAULT_DB_PATH


def get_checkpointer(db_path: Path | str | None = None) -> SqliteSaver:
    """Return a SqliteSaver checkpointer. Creates DB dir if needed."""
    path = Path(db_path or DEFAULT_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    return SqliteSaver(conn)
