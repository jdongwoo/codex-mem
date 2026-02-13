# codex-mem

![logo](docs/logo.svg)

![license](https://img.shields.io/github/license/jdongwoo/codex-mem)
![stars](https://img.shields.io/github/stars/jdongwoo/codex-mem?style=flat)
![issues](https://img.shields.io/github/issues/jdongwoo/codex-mem)

Persistent memory for Codex using a local SQL database.

If this is useful, please star the repo.

- Fast CLI workflow (init/add/search/backfill)
- SQLite by default, PostgreSQL supported
- Hybrid search: SQLite filters + optional Chroma semantic retrieval
- Project-scoped summaries and decisions

## Quick Start

```bash
python3 scripts/memory_init.py
python3 scripts/memory_add.py --project my-project --summary "Initialized codex-mem"
python3 scripts/memory_search.py --project my-project --q "Initialized"
python3 scripts/memory_backfill.py --project my-project
```

## Demo

![demo](docs/demo.svg)

## Why It Works

codex-mem enforces a repeatable memory loop:

1. Search before you act
2. Summarize after you act
3. Store it in SQL for long-term recall

## Database

Default location:

```
~/.codex-mem/codex-mem.db
```

PostgreSQL:

```bash
export CODEX_MEM_DATABASE_URL=postgresql://user:pass@localhost:5432/codex_mem
python3 scripts/memory_init.py
```

## Search Strategies

`memory_search.py` supports:

- `--strategy auto` (default): Hybrid (vector + SQLite filters) when available, then fallback
- `--strategy sqlite`: SQL-only search/filter
- `--strategy chroma`: Semantic-only retrieval + SQLite hydration
- `--strategy hybrid`: Semantic ranking intersected with SQLite metadata filters

Useful filters:

```bash
python3 scripts/memory_search.py --project my-project --q "migration" --type bugfix --concept database --file schema --since 2026-01-01
```

## Settings

First run creates:

```
~/.codex-mem/settings.json
```

Supported keys:

- `CODEX_MEM_DATA_DIR`
- `CODEX_MEM_VECTOR_ENABLED` (`true`/`false`)
- `CODEX_MEM_VECTOR_PROVIDER` (`chroma`)
- `CODEX_MEM_VECTOR_COLLECTION`
- `CODEX_MEM_VECTOR_TOP_K`

Install optional semantic search dependency:

```bash
pip install chromadb
```

## Project Rules

Use `AGENTS.md` to make the memory workflow automatic in your Codex projects.

## Auto-Start With Codex

To run `codex-mem` automatically whenever you launch `codex`, add this wrapper to `~/.zshrc`:

```bash
codex() {
  local ROOT PROJECT MEM
  ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  PROJECT="$(basename "$ROOT")"
  MEM="/Users/a123/proj/kn-codex-pro/codex-mem/scripts"

  python3 "$MEM/memory_init.py" >/dev/null 2>&1 || true
  python3 "$MEM/memory_search.py" \
    --project "$PROJECT" \
    --q "recent decisions architecture bugs" \
    --limit 5 \
    --strategy auto || true

  command codex "$@"
}
```

Apply it:

```bash
source ~/.zshrc
```

## License

Apache-2.0
