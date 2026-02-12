# codex-mem

![license](https://img.shields.io/github/license/jdongwoo/codex-mem)
![stars](https://img.shields.io/github/stars/jdongwoo/codex-mem?style=flat)
![issues](https://img.shields.io/github/issues/jdongwoo/codex-mem)

Persistent memory for Codex using a local SQL database.

- Fast, simple CLI workflow
- SQLite by default, PostgreSQL supported
- Project-scoped summaries and decisions

## Quick Start

```bash
python3 scripts/memory_init.py
python3 scripts/memory_add.py --project my-project --summary "Initialized codex-mem"
python3 scripts/memory_search.py --project my-project --q "Initialized"
```

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

## Project Rules

Use `AGENTS.md` to make the memory workflow automatic in your Codex projects.

## License

Apache-2.0
