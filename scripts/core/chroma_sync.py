import json
from pathlib import Path
from typing import Dict, List, Optional


class ChromaSync:
    def __init__(self, settings: Dict[str, str]):
        self.settings = settings
        self.collection_name = settings.get("CODEX_MEM_VECTOR_COLLECTION", "codex-mem")
        self.turns_collection_name = settings.get("CODEX_MEM_VECTOR_COLLECTION_TURNS", "codex-mem-turns")
        self.data_dir = Path(settings.get("CODEX_MEM_DATA_DIR", str(Path.home() / ".codex-mem")))
        self.vector_dir = self.data_dir / "vector-db"
        self.vector_dir.mkdir(parents=True, exist_ok=True)

        self._client = None
        self._collection = None
        self._turns_collection = None
        self._error: Optional[str] = None
        self._init_client()

    def _init_client(self) -> None:
        try:
            import chromadb  # type: ignore

            self._client = chromadb.PersistentClient(path=str(self.vector_dir))
            self._collection = self._client.get_or_create_collection(name=self.collection_name)
            self._turns_collection = self._client.get_or_create_collection(name=self.turns_collection_name)
        except Exception as exc:
            self._error = str(exc)
            self._client = None
            self._collection = None
            self._turns_collection = None

    @property
    def available(self) -> bool:
        return self._collection is not None

    @property
    def error(self) -> Optional[str]:
        return self._error

    def _doc_id(self, memory_id: int) -> str:
        return f"mem_{memory_id}"

    def _turn_doc_id(self, turn_id: int) -> str:
        return f"turn_{turn_id}"

    def sync_memory(self, memory: Dict[str, object]) -> None:
        if not self.available:
            return

        memory_id = int(memory["id"])
        summary = str(memory.get("summary", ""))
        details = str(memory.get("details", ""))
        document = (summary + "\n\n" + details).strip() or summary

        metadata = {
            "sqlite_id": memory_id,
            "project": str(memory.get("project", "")),
            "type": str(memory.get("type", "")),
            "tags": str(memory.get("tags", "")),
            "created_at_epoch": int(memory.get("created_at_epoch", 0)),
        }

        if self._collection is None:
            return

        self._collection.upsert(
            ids=[self._doc_id(memory_id)],
            documents=[document],
            metadatas=[metadata],
        )

    def query(self, query: str, limit: int, project: Optional[str] = None) -> Dict[str, object]:
        if not self.available or self._collection is None:
            return {"ids": [], "distances": [], "metadatas": []}

        where = {"project": project} if project else None
        response = self._collection.query(
            query_texts=[query],
            n_results=max(limit, 1),
            where=where,
            include=["metadatas", "distances"],
        )

        ids: List[int] = []
        metadatas = (response.get("metadatas") or [[]])[0]
        distances = (response.get("distances") or [[]])[0]

        for meta in metadatas:
            if not isinstance(meta, dict):
                continue
            sqlite_id = meta.get("sqlite_id")
            try:
                sqlite_id_int = int(sqlite_id)
            except Exception:
                continue
            if sqlite_id_int not in ids:
                ids.append(sqlite_id_int)

        return {"ids": ids, "distances": distances, "metadatas": metadatas}

    def sync_turn(self, turn: Dict[str, object]) -> None:
        if not self.available:
            return

        turn_id = int(turn["id"])
        role = str(turn.get("role", ""))
        content = str(turn.get("content", ""))
        context = str(turn.get("context_json", ""))
        document = (role + "\n\n" + content + "\n\n" + context).strip() or content

        metadata = {
            "sqlite_id": turn_id,
            "project": str(turn.get("project", "")),
            "session_id": str(turn.get("session_id", "")),
            "role": role,
            "created_at_epoch": int(turn.get("created_at_epoch", 0)),
        }

        if self._turns_collection is None:
            return

        self._turns_collection.upsert(
            ids=[self._turn_doc_id(turn_id)],
            documents=[document],
            metadatas=[metadata],
        )

    def query_turns(
        self, query: str, limit: int, project: Optional[str] = None, session_id: Optional[str] = None
    ) -> Dict[str, object]:
        if not self.available or self._turns_collection is None:
            return {"ids": [], "distances": [], "metadatas": []}

        where_parts = []
        if project:
            where_parts.append({"project": project})
        if session_id:
            where_parts.append({"session_id": session_id})

        where = None
        if len(where_parts) == 1:
            where = where_parts[0]
        elif len(where_parts) > 1:
            where = {"$and": where_parts}

        response = self._turns_collection.query(
            query_texts=[query],
            n_results=max(limit, 1),
            where=where,
            include=["metadatas", "distances"],
        )

        ids: List[int] = []
        metadatas = (response.get("metadatas") or [[]])[0]
        distances = (response.get("distances") or [[]])[0]

        for meta in metadatas:
            if not isinstance(meta, dict):
                continue
            sqlite_id = meta.get("sqlite_id")
            try:
                sqlite_id_int = int(sqlite_id)
            except Exception:
                continue
            if sqlite_id_int not in ids:
                ids.append(sqlite_id_int)

        return {"ids": ids, "distances": distances, "metadatas": metadatas}

    def backfill(self, memories: List[Dict[str, object]]) -> int:
        if not self.available:
            return 0
        synced = 0
        for memory in memories:
            self.sync_memory(memory)
            synced += 1
        return synced

    def backfill_turns(self, turns: List[Dict[str, object]]) -> int:
        if not self.available:
            return 0
        synced = 0
        for turn in turns:
            self.sync_turn(turn)
            synced += 1
        return synced
