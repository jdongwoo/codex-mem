CREATE TABLE IF NOT EXISTS memories (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
  project TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'discovery',
  tags TEXT NOT NULL DEFAULT '',
  summary TEXT NOT NULL,
  details TEXT NOT NULL DEFAULT '',
  concepts TEXT NOT NULL DEFAULT '[]',
  files_read TEXT NOT NULL DEFAULT '[]',
  files_modified TEXT NOT NULL DEFAULT '[]',
  metadata_json TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS memories_project_idx ON memories(project);
CREATE INDEX IF NOT EXISTS memories_created_at_idx ON memories(created_at);
CREATE INDEX IF NOT EXISTS memories_created_at_epoch_idx ON memories(created_at_epoch);
CREATE INDEX IF NOT EXISTS memories_type_idx ON memories(type);

CREATE TABLE IF NOT EXISTS conversation_turns (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
  project TEXT NOT NULL,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  context_json TEXT NOT NULL DEFAULT '{}',
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS conversation_turns_project_idx ON conversation_turns(project);
CREATE INDEX IF NOT EXISTS conversation_turns_session_idx ON conversation_turns(session_id);
CREATE INDEX IF NOT EXISTS conversation_turns_created_at_epoch_idx ON conversation_turns(created_at_epoch);
CREATE INDEX IF NOT EXISTS conversation_turns_role_idx ON conversation_turns(role);
