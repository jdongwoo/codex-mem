import argparse
import json
import sys
from datetime import datetime

from db import connect


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--summary", required=False)
    p.add_argument("--details", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--meta", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    summary = args.summary
    if not summary:
        summary = sys.stdin.read().strip()
    if not summary:
        raise SystemExit("summary required (use --summary or stdin)")

    metadata_json = ""
    if args.meta:
        try:
            metadata_json = json.dumps(json.loads(args.meta))
        except Exception:
            metadata_json = args.meta

    conn, dialect = connect()

    if dialect == "sqlite":
        with conn:
            conn.execute(
                "INSERT INTO memories (project, tags, summary, details, metadata_json) VALUES (?, ?, ?, ?, ?)",
                (args.project, args.tags, summary, args.details, metadata_json),
            )
    else:
        with conn:
            conn.execute(
                "INSERT INTO memories (project, tags, summary, details, metadata_json) VALUES (%s, %s, %s, %s, %s)",
                (args.project, args.tags, summary, args.details, metadata_json),
            )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
