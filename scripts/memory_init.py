from pathlib import Path

from db import connect
from core.config import load_settings


def load_schema(dialect: str) -> str:
    base = Path(__file__).resolve().parent.parent / "db"
    if dialect == "sqlite":
        return (base / "schema_sqlite.sql").read_text()
    return (base / "schema_postgres.sql").read_text()


def ensure_sqlite_migrations(conn) -> None:
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


def main() -> int:
    load_settings()
    conn, dialect = connect()
    schema = load_schema(dialect)
    with conn:
        conn.executescript(schema) if dialect == "sqlite" else conn.execute(schema)
        if dialect == "sqlite":
            ensure_sqlite_migrations(conn)

    print(f"Initialized {dialect} schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
