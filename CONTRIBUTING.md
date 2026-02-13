# Contributing

Thanks for considering a contribution to `codex-mem`.

## Contribution Types

- Bug fixes
- Search quality improvements
- CLI ergonomics
- Docs and examples
- New integration ideas (proposed first, then implemented)

## Development Setup

```bash
git clone https://github.com/jdongwoo/codex-mem.git
cd codex-mem
python3 scripts/memory_init.py
python -m py_compile scripts/*.py
```

Optional semantic search dependency:

```bash
pip install chromadb
```

## First Contribution Guide

1. Pick an issue labeled `good first issue` or `help wanted`.
2. Comment on the issue to claim it and align on scope.
3. Keep PRs focused (one behavior change per PR).
4. Add or update docs for user-facing behavior changes.
5. Run `python -m py_compile scripts/*.py` before opening PR.

## Pull Request Expectations

- Clear problem statement and motivation
- Concise change summary
- Verification notes (manual or automated)
- Backward compatibility notes when behavior changes

Use `.github/PULL_REQUEST_TEMPLATE.md`.

## Design Direction

- Avoid ad-hoc feature patching.
- Keep domain logic separate from interfaces.
- Prefer explicit contracts and incremental architecture changes.

## Code Style

- Keep code simple and explicit.
- Prefer small functions and predictable control flow.
- Avoid broad refactors unless discussed in an issue first.

## Reporting Issues

Use issue templates for bug reports and feature requests.  
For questions, use GitHub Discussions.
