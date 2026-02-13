import argparse
import json
import sys
from datetime import datetime

from db import connect
from core.chroma_sync import ChromaSync
from core.config import get_bool, load_settings


def _csv_or_json_list(raw: str):
    if not raw:
        return []
    s = raw.strip()
    if not s:
        return []
    try:
        parsed = json.loads(s)
        if isinstance(parsed, list):
            return [str(v) for v in parsed if str(v).strip()]
    except Exception:
        pass
    return [p.strip() for p in s.split(",") if p.strip()]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--summary", required=False)
    p.add_argument("--details", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--meta", default="")
    p.add_argument("--type", default="discovery")
    p.add_argument("--concepts", default="")
    p.add_argument("--files-read", default="")
    p.add_argument("--files-modified", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    summary = args.summary
    if not summary:
        summary = sys.stdin.read().strip()
    if not summary:
        raise SystemExit("summary required (use --summary or stdin)")

    concepts = _csv_or_json_list(args.concepts)
    files_read = _csv_or_json_list(args.files_read)
    files_modified = _csv_or_json_list(args.files_modified)

    metadata_obj = {}
    if args.meta:
        try:
            metadata_obj = json.loads(args.meta)
            if not isinstance(metadata_obj, dict):
                metadata_obj = {"value": metadata_obj}
        except Exception:
            metadata_obj = {"raw": args.meta}

    metadata_obj.setdefault("concepts", concepts)
    metadata_obj.setdefault("files_read", files_read)
    metadata_obj.setdefault("files_modified", files_modified)
    metadata_json = json.dumps(metadata_obj)

    created_at_epoch = int(datetime.utcnow().timestamp())

    conn, dialect = connect()

    if dialect == "sqlite":
        with conn:
            cur = conn.execute(
                """
                INSERT INTO memories
                (project, tags, summary, details, metadata_json, type, created_at_epoch, concepts, files_read, files_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    args.project,
                    args.tags,
                    summary,
                    args.details,
                    metadata_json,
                    args.type,
                    created_at_epoch,
                    json.dumps(concepts),
                    json.dumps(files_read),
                    json.dumps(files_modified),
                ),
            )
            memory_id = int(cur.lastrowid)
    else:
        with conn:
            cur = conn.execute(
                """
                INSERT INTO memories
                (project, tags, summary, details, metadata_json, type, created_at_epoch, concepts, files_read, files_modified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    args.project,
                    args.tags,
                    summary,
                    args.details,
                    metadata_json,
                    args.type,
                    created_at_epoch,
                    json.dumps(concepts),
                    json.dumps(files_read),
                    json.dumps(files_modified),
                ),
            )
            row = cur.fetchone()
            memory_id = int(row[0])

    settings = load_settings()
    vector_enabled = get_bool(settings, "CODEX_MEM_VECTOR_ENABLED")
    if vector_enabled and dialect == "sqlite":
        chroma = ChromaSync(settings)
        chroma.sync_memory(
            {
                "id": memory_id,
                "project": args.project,
                "type": args.type,
                "tags": args.tags,
                "summary": summary,
                "details": args.details,
                "created_at_epoch": created_at_epoch,
            }
        )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
