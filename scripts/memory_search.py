import argparse
from datetime import datetime

from db import connect


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--q", required=True)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--json", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    conn, dialect = connect()

    if dialect == "sqlite":
        rows = conn.execute(
            """
            SELECT id, created_at, project, tags, summary, details
            FROM memories
            WHERE project = ? AND (summary LIKE ? OR details LIKE ?)
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (args.project, f"%{args.q}%", f"%{args.q}%", args.limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT id, created_at, project, tags, summary, details
            FROM memories
            WHERE project = %s AND (summary ILIKE %s OR details ILIKE %s)
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (args.project, f"%{args.q}%", f"%{args.q}%", args.limit),
        ).fetchall()

    if args.json:
        for r in rows:
            print(dict(r))
        return 0

    if not rows:
        print("no results")
        return 0

    for r in rows:
        print(f"#{r['id']} {r['created_at']} [{r['project']}] ({r['tags']})")
        print(r["summary"])
        if r["details"]:
            print(r["details"])
        print("-")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
