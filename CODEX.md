# codex-mem: Developer Instructions

codex-mem mirrors the high-level pattern of claude-mem, but targets Codex.

## Architecture

- **CLI Scripts**: `scripts/*.py` for add/search/init
- **Database**: SQLite by default, PostgreSQL supported via `CODEX_MEM_DATABASE_URL`
- **Workflow**: Enforced through `AGENTS.md` (project rules)

## Commands

```bash
python3 scripts/memory_init.py
python3 scripts/memory_add.py --project <project> --summary "..."
python3 scripts/memory_search.py --project <project> --q "..."
```

## Files

- **Source**: `scripts/`
- **Schema**: `db/`
- **Default DB**: `~/.codex-mem/codex-mem.db`
