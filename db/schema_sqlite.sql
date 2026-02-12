CREATE TABLE IF NOT EXISTS memories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  project TEXT NOT NULL,
  tags TEXT NOT NULL DEFAULT '',
  summary TEXT NOT NULL,
  details TEXT NOT NULL DEFAULT '',
  metadata_json TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS memories_project_idx ON memories(project);
CREATE INDEX IF NOT EXISTS memories_created_at_idx ON memories(created_at);
