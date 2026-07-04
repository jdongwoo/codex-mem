# codex-mem

Persistent, project-scoped memory for the Codex CLI, backed by a local SQL database.

Codex forgets everything between sessions. codex-mem gives it a durable memory loop: search stored context before acting, summarize after acting, and keep the result in SQL for long-term recall.

- CLI workflow: init, add, search, backfill
- SQLite by default, PostgreSQL supported
- Hybrid search: SQL metadata filters combined with optional Chroma semantic retrieval
- Project-scoped summaries and decisions
- Conversation turns persisted with optional vector retrieval

## Quick start

```bash
python3 scripts/memory_init.py
python3 scripts/memory_add.py --project my-project --summary "Initialized codex-mem"
python3 scripts/memory_search.py --project my-project --q "Initialized"
python3 scripts/memory_backfill.py --project my-project
python3 scripts/conversation_add.py --project my-project --session-id s1 --role user --content "How does search work?"
python3 scripts/conversation_search.py --project my-project --session-id s1 --q "search" --strategy auto
```

## Demo

![demo](docs/demo.svg)

## Database

Default location:

```
~/.codex-mem/codex-mem.db
```

To use PostgreSQL instead:

```bash
export CODEX_MEM_DATABASE_URL=postgresql://user:pass@localhost:5432/codex_mem
python3 scripts/memory_init.py
```

Schemas for both backends live in `db/`.

## Search strategies

`memory_search.py` supports:

- `--strategy auto` (default): hybrid (vector + SQLite filters) when available, with fallback
- `--strategy sqlite`: SQL-only search and filtering
- `--strategy chroma`: semantic-only retrieval, hydrated from SQLite
- `--strategy hybrid`: semantic ranking intersected with SQLite metadata filters

Filters can be combined:

```bash
python3 scripts/memory_search.py --project my-project --q "migration" --type bugfix --concept database --file schema --since 2026-01-01
```

## Settings

The first run creates `~/.codex-mem/settings.json`. Supported keys:

- `CODEX_MEM_DATA_DIR`
- `CODEX_MEM_VECTOR_ENABLED` (`true`/`false`)
- `CODEX_MEM_VECTOR_PROVIDER` (`chroma`)
- `CODEX_MEM_VECTOR_COLLECTION`
- `CODEX_MEM_VECTOR_COLLECTION_TURNS`
- `CODEX_MEM_VECTOR_TOP_K`

Semantic search is optional and requires:

```bash
pip install chromadb
```

## Automatic startup with Codex

To load recent project memory whenever you launch `codex`, add a wrapper to your shell profile (adjust the path to your clone):

```bash
codex() {
  local ROOT PROJECT MEM
  ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  PROJECT="$(basename "$ROOT")"
  MEM="/path/to/codex-mem/scripts"

  python3 "$MEM/memory_init.py" >/dev/null 2>&1 || true
  python3 "$MEM/memory_search.py" \
    --project "$PROJECT" \
    --q "recent decisions architecture bugs" \
    --limit 5 \
    --strategy auto || true

  command codex "$@"
}
```

See `AGENTS.md` for project rules that make the memory workflow automatic inside Codex sessions.

## Architecture

An overview of the storage model and search pipeline is in `docs/architecture.md`.

## Contributing

Contributions are welcome. Start with `CONTRIBUTING.md`; issues labeled `good first issue` are a reasonable entry point. Useful starter areas:

- CLI argument UX (`scripts/memory_*.py`)
- Search ranking and filtering (`scripts/core/search.py`)
- Documentation examples and troubleshooting (`README.md`, `docs/`)

## License

Apache-2.0
