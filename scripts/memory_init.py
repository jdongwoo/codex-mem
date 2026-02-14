from pathlib import Path

from db import connect
from core.config import load_settings

SQLITE_CREATE_MEMORIES_TABLE = """
CREATE TABLE IF NOT EXISTS memories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  created_at_epoch INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER)),
  project TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'discovery',
  tags TEXT NOT NULL DEFAULT '',
  summary TEXT NOT NULL,
  details TEXT NOT NULL DEFAULT '',
  concepts TEXT NOT NULL DEFAULT '[]',
  files_read TEXT NOT NULL DEFAULT '[]',
  files_modified TEXT NOT NULL DEFAULT '[]',
  metadata_json TEXT NOT NULL DEFAULT ''
)
"""

SQLITE_CREATE_CONVERSATION_TURNS_TABLE = """
CREATE TABLE IF NOT EXISTS conversation_turns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  created_at_epoch INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER)),
  project TEXT NOT NULL,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  context_json TEXT NOT NULL DEFAULT '{}',
  metadata_json TEXT NOT NULL DEFAULT '{}'
)
"""


def load_schema(dialect: str) -> str:
    base = Path(__file__).resolve().parent.parent / "db"
    if dialect == "sqlite":
        return (base / "schema_sqlite.sql").read_text()
    return (base / "schema_postgres.sql").read_text()


def ensure_sqlite_migrations(conn) -> None:
    conn.execute(SQLITE_CREATE_MEMORIES_TABLE)
    conn.execute(SQLITE_CREATE_CONVERSATION_TURNS_TABLE)

    cols = {r["name"] for r in conn.execute("PRAGMA table_info(memories)").fetchall()}

    if "created_at_epoch" not in cols:
        conn.execute(
            "ALTER TABLE memories ADD COLUMN created_at_epoch INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER))"
        )
    if "type" not in cols:
        conn.execute("ALTER TABLE memories ADD COLUMN type TEXT NOT NULL DEFAULT 'discovery'")
    if "concepts" not in cols:
        conn.execute("ALTER TABLE memories ADD COLUMN concepts TEXT NOT NULL DEFAULT '[]'")
    if "files_read" not in cols:
        conn.execute("ALTER TABLE memories ADD COLUMN files_read TEXT NOT NULL DEFAULT '[]'")
    if "files_modified" not in cols:
        conn.execute("ALTER TABLE memories ADD COLUMN files_modified TEXT NOT NULL DEFAULT '[]'")

    conn.execute(
        "UPDATE memories SET created_at_epoch = CAST(strftime('%s', created_at) AS INTEGER) WHERE created_at_epoch IS NULL OR created_at_epoch = 0"
    )

    conn.execute("CREATE INDEX IF NOT EXISTS memories_created_at_epoch_idx ON memories(created_at_epoch)")
    conn.execute("CREATE INDEX IF NOT EXISTS memories_type_idx ON memories(type)")

    conn.execute("CREATE INDEX IF NOT EXISTS conversation_turns_project_idx ON conversation_turns(project)")
    conn.execute("CREATE INDEX IF NOT EXISTS conversation_turns_session_idx ON conversation_turns(session_id)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS conversation_turns_created_at_epoch_idx ON conversation_turns(created_at_epoch)"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS conversation_turns_role_idx ON conversation_turns(role)")


def main() -> int:
    load_settings()
    conn, dialect = connect()
    with conn:
        if dialect == "sqlite":
            ensure_sqlite_migrations(conn)
        else:
            schema = load_schema(dialect)
            conn.execute(schema)

    print(f"Initialized {dialect} schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
