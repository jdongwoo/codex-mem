import argparse
import json

from db import connect
from core.chroma_sync import ChromaSync
from core.config import get_bool, load_settings


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--project", default="")
    p.add_argument("--limit", type=int, default=0)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    settings = load_settings()

    if not get_bool(settings, "CODEX_MEM_VECTOR_ENABLED"):
        print("vector search is disabled (CODEX_MEM_VECTOR_ENABLED=false)")
        return 0

    conn, dialect = connect()
    if dialect != "sqlite":
        print("backfill currently supports sqlite only")
        return 0

    chroma = ChromaSync(settings)
    if not chroma.available:
        message = chroma.error or "chroma unavailable"
        raise SystemExit(f"failed to initialize chroma: {message}")

    params = []
    where = []
    if args.project:
        where.append("project = ?")
        params.append(args.project)

    sql = (
        "SELECT id, project, type, tags, summary, details, created_at_epoch "
        "FROM memories "
        + ("WHERE " + " AND ".join(where) + " " if where else "")
        + "ORDER BY created_at_epoch DESC"
    )
    if args.limit and args.limit > 0:
        sql += " LIMIT ?"
        params.append(args.limit)

    rows = conn.execute(sql, tuple(params)).fetchall()
    payload = [dict(r) for r in rows]
    synced = chroma.backfill(payload)

    print(json.dumps({"synced": synced, "rows": len(payload)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
