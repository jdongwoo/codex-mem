import argparse
import json

from db import connect
from core.config import get_bool, load_settings
from core.search import SearchOrchestrator, SearchRequest


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--q", required=False, default="")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--json", action="store_true")
    p.add_argument("--strategy", default="auto", choices=["auto", "sqlite", "chroma", "hybrid"])
    p.add_argument("--type", dest="type_filter", default="")
    p.add_argument("--tags", dest="tags_filter", default="")
    p.add_argument("--concept", dest="concept_filter", default="")
    p.add_argument("--file", dest="file_filter", default="")
    p.add_argument("--since", default="")
    p.add_argument("--until", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    settings = load_settings()
    vector_enabled = get_bool(settings, "CODEX_MEM_VECTOR_ENABLED")

    conn, dialect = connect()

    if dialect != "sqlite":
        # Advanced search paths are optimized for sqlite in this release.
        vector_enabled = False

    orchestrator = SearchOrchestrator(conn, dialect, settings, vector_enabled=vector_enabled)
    result = orchestrator.search(
        SearchRequest(
            project=args.project,
            query=args.q.strip() or None,
            limit=args.limit,
            strategy=args.strategy,
            type_filter=args.type_filter or None,
            tags_filter=args.tags_filter or None,
            concept_filter=args.concept_filter or None,
            file_filter=args.file_filter or None,
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
    for r in rows:
        print(f"#{r['id']} {r['created_at']} [{r['project']}] ({r['tags']}) type={r.get('type', '')}")
        print(r["summary"])
        if r.get("details"):
            print(r["details"])
        print("-")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
