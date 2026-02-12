import os
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_DB_URL = "sqlite://" + str(Path.home() / ".codex-mem" / "codex-mem.db")


def get_db_url() -> str:
    return os.getenv("CODEX_MEM_DATABASE_URL", DEFAULT_DB_URL)


def parse_db_url(db_url: str):
    if db_url.startswith("sqlite://"):
        path = db_url.replace("sqlite://", "", 1)
        return ("sqlite", path)
    return ("postgres", db_url)


def connect():
    db_url = get_db_url()
    dialect, target = parse_db_url(db_url)

    if dialect == "sqlite":
        db_path = Path(target).expanduser()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

    # PostgreSQL
    try:
        import psycopg  # type: ignore
    except Exception as exc:
        raise SystemExit(
            "psycopg is required for PostgreSQL. Install with: pip install psycopg"
        ) from exc

    conn = psycopg.connect(target)
    return conn, "postgres"
