import argparse
import json

from db import connect
from core.config import get_bool, load_settings
from core.conversation_search import ConversationSearchOrchestrator, ConversationSearchRequest


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--session-id", default="")
    p.add_argument("--role", default="")
    p.add_argument("--q", required=False, default="")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.add_argument("--strategy", default="auto", choices=["auto", "sqlite", "chroma", "hybrid"])
    p.add_argument("--since", default="")
    p.add_argument("--until", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    settings = load_settings()
    vector_enabled = get_bool(settings, "CODEX_MEM_VECTOR_ENABLED")
    conn, dialect = connect()

    if dialect != "sqlite":
        vector_enabled = False

    orchestrator = ConversationSearchOrchestrator(conn, dialect, settings, vector_enabled=vector_enabled)
    result = orchestrator.search(
        ConversationSearchRequest(
            project=args.project,
            query=args.q.strip() or None,
            limit=args.limit,
            strategy=args.strategy,
            session_id=args.session_id or None,
            role=args.role or None,
            since=args.since or None,
            until=args.until or None,
        )
    )

    rows = result["rows"]
    if args.json:
        print(
            json.dumps(
                {
                    "strategy": result["strategy"],
                    "used_chroma": result["used_chroma"],
                    "fell_back": result["fell_back"],
                    "count": len(rows),
                    "rows": rows,
                },
                ensure_ascii=False,
            )
        )
        return 0

    if not rows:
        print("no results")
        return 0

    marker = f"strategy={result['strategy']} used_chroma={result['used_chroma']} fell_back={result['fell_back']}"
    print(marker)
    for row in rows:
        print(
            f"#{row['id']} {row['created_at']} [{row['project']}] "
            f"session={row['session_id']} role={row['role']}"
        )
        print(row["content"])
        print("-")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
