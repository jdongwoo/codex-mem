# codex-mem: Developer Instructions

codex-mem mirrors the high-level pattern of claude-mem, but targets Codex.

## Architecture

- **CLI Scripts**: `scripts/*.py` for add/search/init/backfill
- **Database**: SQLite by default, PostgreSQL via `CODEX_MEM_DATABASE_URL`
- **Search**: Strategy-based orchestrator (`sqlite`, `chroma`, `hybrid`, `auto`)
- **Vector DB**: Optional Chroma persistent index under `~/.codex-mem/vector-db`
- **Conversation Store**: `conversation_turns` SQL table with optional vector index
- **Workflow**: Enforced through `AGENTS.md` (project rules)

## Commands

```bash
python3 scripts/memory_init.py
python3 scripts/memory_add.py --project <project> --summary "..."
python3 scripts/memory_search.py --project <project> --q "..." --strategy auto
python3 scripts/memory_backfill.py --project <project>
python3 scripts/conversation_add.py --project <project> --session-id <session> --role user --content "..."
python3 scripts/conversation_search.py --project <project> --session-id <session> --q "..." --strategy auto
python3 scripts/conversation_backfill.py --project <project>
```

## Files

- **Source**: `scripts/` and `scripts/core/`
- **Schema**: `db/`
- **Settings**: `~/.codex-mem/settings.json`
- **Default DB**: `~/.codex-mem/codex-mem.db`
