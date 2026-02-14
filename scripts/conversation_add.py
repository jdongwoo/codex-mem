import argparse
import json
import sys
from datetime import datetime

from db import connect
from core.chroma_sync import ChromaSync
from core.config import get_bool, load_settings

VALID_ROLES = {"system", "user", "assistant", "tool"}


def _parse_json_object(raw: str, field_name: str):
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except Exception as exc:
        raise SystemExit(f"{field_name} must be valid JSON object") from exc
    if not isinstance(parsed, dict):
        raise SystemExit(f"{field_name} must be JSON object")
    return parsed


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--session-id", required=True)
    p.add_argument("--role", required=True, choices=sorted(VALID_ROLES))
    p.add_argument("--content", required=False)
    p.add_argument("--context", default="")
    p.add_argument("--meta", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    content = args.content
    if not content:
        content = sys.stdin.read().strip()
    if not content:
        raise SystemExit("content required (use --content or stdin)")

    context_obj = _parse_json_object(args.context, "context")
    metadata_obj = _parse_json_object(args.meta, "meta")

    created_at_epoch = int(datetime.utcnow().timestamp())
    conn, dialect = connect()

    if dialect == "sqlite":
        with conn:
            cur = conn.execute(
                """
                INSERT INTO conversation_turns
                (project, session_id, role, content, context_json, metadata_json, created_at_epoch)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    args.project,
                    args.session_id,
                    args.role,
                    content,
                    json.dumps(context_obj),
                    json.dumps(metadata_obj),
                    created_at_epoch,
                ),
            )
            turn_id = int(cur.lastrowid)
    else:
        with conn:
            cur = conn.execute(
                """
                INSERT INTO conversation_turns
                (project, session_id, role, content, context_json, metadata_json, created_at_epoch)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    args.project,
                    args.session_id,
                    args.role,
                    content,
                    json.dumps(context_obj),
                    json.dumps(metadata_obj),
                    created_at_epoch,
                ),
            )
            row = cur.fetchone()
            turn_id = int(row[0])

    settings = load_settings()
    vector_enabled = get_bool(settings, "CODEX_MEM_VECTOR_ENABLED")
    if vector_enabled and dialect == "sqlite":
        chroma = ChromaSync(settings)
        chroma.sync_turn(
            {
                "id": turn_id,
                "project": args.project,
                "session_id": args.session_id,
                "role": args.role,
                "content": content,
                "context_json": json.dumps(context_obj),
                "created_at_epoch": created_at_epoch,
            }
        )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
