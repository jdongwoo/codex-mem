import sys
from pathlib import Path

from db import connect


def load_schema(dialect: str) -> str:
    base = Path(__file__).resolve().parent.parent / "db"
    if dialect == "sqlite":
        return (base / "schema_sqlite.sql").read_text()
    return (base / "schema_postgres.sql").read_text()


def main() -> int:
    conn, dialect = connect()
    schema = load_schema(dialect)
    with conn:
        conn.executescript(schema) if dialect == "sqlite" else conn.execute(schema)
    print(f"Initialized {dialect} schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
