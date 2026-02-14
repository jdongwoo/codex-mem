# Architecture

codex-mem mirrors the workflow pattern of claude-mem but uses scripts and Codex rules instead of a plugin system.

## Flow

1. Codex reads memory before work (search script)
2. Work happens
3. Codex writes a summary (add script)
4. Memories live in SQL for long-term retrieval
5. Conversation turns and context are stored in SQL and optionally indexed in Chroma
