# Codex Memory Workflow (Template)

Use this file in your project root when you want Codex to keep long-term memory in a SQL database.

## Rules

- At the start of a task, run:
  - `python3 codex-mem/scripts/memory_search.py --project <project> --q "<task keywords>" --limit 5`
- At the end of a task, run:
  - `python3 codex-mem/scripts/memory_add.py --project <project> --summary "<concise summary>" --details "<key decisions or links>" --tags <comma-separated>`

## Notes

- Replace `<project>` with your repo or workspace name.
- Use `CODEX_MEM_DATABASE_URL` if you want PostgreSQL.
