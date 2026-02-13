from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Sequence

from .chroma_sync import ChromaSync


@dataclass
class SearchRequest:
    project: str
    query: Optional[str]
    limit: int
    strategy: str
    type_filter: Optional[str] = None
    tags_filter: Optional[str] = None
    concept_filter: Optional[str] = None
    file_filter: Optional[str] = None
    since: Optional[str] = None
    until: Optional[str] = None


class SearchOrchestrator:
    def __init__(self, conn, dialect: str, settings: Dict[str, str], vector_enabled: bool):
        self.conn = conn
        self.dialect = dialect
        self.vector_enabled = vector_enabled
        self.chroma = ChromaSync(settings) if vector_enabled else None

    def search(self, req: SearchRequest) -> Dict[str, object]:
        strategy = (req.strategy or "auto").lower()
        if strategy not in {"auto", "sqlite", "chroma", "hybrid"}:
            strategy = "auto"

        if not req.query:
            rows = self._sql_search(req, include_query=False)
            return self._result(rows, strategy="sqlite", used_chroma=False, fell_back=False)

        if strategy == "sqlite":
            rows = self._sql_search(req, include_query=True)
            return self._result(rows, strategy="sqlite", used_chroma=False, fell_back=False)

        attempted_chroma = strategy in {"auto", "chroma", "hybrid"} and bool(req.query) and self.vector_enabled
        if self.chroma and self.chroma.available and strategy in {"auto", "chroma", "hybrid"}:
            try:
                vector = self.chroma.query(req.query, req.limit * 4, req.project)
                ids = vector.get("ids", [])
                if strategy == "chroma":
                    rows = self._hydrate_ids(ids, req)
                    return self._result(rows, strategy="chroma", used_chroma=True, fell_back=False)

                if strategy in {"hybrid", "auto"}:
                    metadata_rows = self._sql_search(req, include_query=False, limit=req.limit * 6)
                    allowed = {int(r["id"]) for r in metadata_rows}
                    ranked = [mid for mid in ids if int(mid) in allowed]
                    if not ranked and strategy == "hybrid":
                        rows = metadata_rows[: req.limit]
                        return self._result(rows, strategy="hybrid", used_chroma=True, fell_back=False)
                    rows = self._hydrate_ids(ranked, req)
                    return self._result(rows, strategy="hybrid", used_chroma=True, fell_back=False)
            except Exception:
                pass

        rows = self._sql_search(req, include_query=True)
        return self._result(rows, strategy="sqlite", used_chroma=False, fell_back=attempted_chroma)

    def _result(self, rows: Sequence[Dict[str, object]], strategy: str, used_chroma: bool, fell_back: bool):
        return {
            "rows": list(rows),
            "strategy": strategy,
            "used_chroma": used_chroma,
            "fell_back": fell_back,
        }

    def _parse_epoch(self, value: Optional[str], end_of_day: bool = False) -> Optional[int]:
        if not value:
            return None
        try:
            if value.isdigit():
                return int(value)
        except Exception:
            pass
        try:
            dt = datetime.fromisoformat(value)
            if end_of_day and len(value) <= 10:
                dt = dt.replace(hour=23, minute=59, second=59)
            return int(dt.timestamp())
        except Exception:
            return None

    def _sql_search(self, req: SearchRequest, include_query: bool, limit: Optional[int] = None) -> List[Dict[str, object]]:
        if self.dialect == "sqlite":
            return self._sqlite_search(req, include_query, limit)
        return self._postgres_search(req, include_query, limit)

    def _sqlite_search(self, req: SearchRequest, include_query: bool, limit: Optional[int] = None) -> List[Dict[str, object]]:
        limit_value = limit if limit is not None else req.limit

        params: List[object] = [req.project]
        where: List[str] = ["project = ?"]

        if include_query and req.query:
            where.append("(summary LIKE ? OR details LIKE ?)")
            like = f"%{req.query}%"
            params.extend([like, like])

        if req.type_filter:
            where.append("type = ?")
            params.append(req.type_filter)

        if req.tags_filter:
            where.append("tags LIKE ?")
            params.append(f"%{req.tags_filter}%")

        if req.concept_filter:
            where.append("EXISTS (SELECT 1 FROM json_each(concepts) WHERE value = ?)")
            params.append(req.concept_filter)

        if req.file_filter:
            where.append(
                "(" \
                "EXISTS (SELECT 1 FROM json_each(files_read) WHERE value LIKE ?) " \
                "OR EXISTS (SELECT 1 FROM json_each(files_modified) WHERE value LIKE ?)" \
                ")"
            )
            like = f"%{req.file_filter}%"
            params.extend([like, like])

        since_epoch = self._parse_epoch(req.since)
        if since_epoch is not None:
            where.append("created_at_epoch >= ?")
            params.append(since_epoch)

        until_epoch = self._parse_epoch(req.until, end_of_day=True)
        if until_epoch is not None:
            where.append("created_at_epoch <= ?")
            params.append(until_epoch)

        sql = (
            "SELECT id, created_at, created_at_epoch, project, type, tags, summary, details, concepts, files_read, files_modified, metadata_json "
            "FROM memories "
            f"WHERE {' AND '.join(where)} "
            "ORDER BY created_at_epoch DESC "
            "LIMIT ?"
        )
        params.append(limit_value)

        rows = self.conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]

    def _postgres_search(self, req: SearchRequest, include_query: bool, limit: Optional[int] = None) -> List[Dict[str, object]]:
        limit_value = limit if limit is not None else req.limit

        params: List[object] = [req.project]
        where: List[str] = ["project = %s"]

        if include_query and req.query:
            where.append("(summary ILIKE %s OR details ILIKE %s)")
            like = f"%{req.query}%"
            params.extend([like, like])

        if req.type_filter:
            where.append("type = %s")
            params.append(req.type_filter)

        if req.tags_filter:
            where.append("tags ILIKE %s")
            params.append(f"%{req.tags_filter}%")

        if req.concept_filter:
            where.append("concepts ILIKE %s")
            params.append(f"%{req.concept_filter}%")

        if req.file_filter:
            where.append("(files_read ILIKE %s OR files_modified ILIKE %s)")
            like = f"%{req.file_filter}%"
            params.extend([like, like])

        since_epoch = self._parse_epoch(req.since)
        if since_epoch is not None:
            where.append("created_at_epoch >= %s")
            params.append(since_epoch)

        until_epoch = self._parse_epoch(req.until, end_of_day=True)
        if until_epoch is not None:
            where.append("created_at_epoch <= %s")
            params.append(until_epoch)

        sql = (
            "SELECT id, created_at, created_at_epoch, project, type, tags, summary, details, concepts, files_read, files_modified, metadata_json "
            "FROM memories "
            f"WHERE {' AND '.join(where)} "
            "ORDER BY created_at_epoch DESC "
            "LIMIT %s"
        )
        params.append(limit_value)

        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            columns = [c.name for c in cur.description]
            fetched = cur.fetchall()

        return [dict(zip(columns, row)) for row in fetched]

    def _hydrate_ids(self, ids: Sequence[int], req: SearchRequest) -> List[Dict[str, object]]:
        normalized = []
        for value in ids:
            try:
                normalized.append(int(value))
            except Exception:
                continue

        if not normalized:
            if req.strategy == "chroma":
                return []
            return self._sql_search(req, include_query=True)

        if self.dialect == "sqlite":
            placeholders = ",".join(["?"] * len(normalized))
            params: List[object] = [req.project, *normalized]
            sql = (
                "SELECT id, created_at, created_at_epoch, project, type, tags, summary, details, concepts, files_read, files_modified, metadata_json "
                "FROM memories "
                f"WHERE project = ? AND id IN ({placeholders})"
            )
            rows = self.conn.execute(sql, tuple(params)).fetchall()
            indexed = {int(row["id"]): dict(row) for row in rows}
        else:
            placeholders = ",".join(["%s"] * len(normalized))
            params = [req.project, *normalized]
            sql = (
                "SELECT id, created_at, created_at_epoch, project, type, tags, summary, details, concepts, files_read, files_modified, metadata_json "
                "FROM memories "
                f"WHERE project = %s AND id IN ({placeholders})"
            )
            with self.conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                columns = [c.name for c in cur.description]
                fetched = cur.fetchall()
            indexed = {int(row[0]): dict(zip(columns, row)) for row in fetched}

        ordered = [indexed[mid] for mid in normalized if mid in indexed]

        filtered: List[Dict[str, object]] = []
        for row in ordered:
            if req.type_filter and row.get("type") != req.type_filter:
                continue
            if req.tags_filter and req.tags_filter not in str(row.get("tags", "")):
                continue
            filtered.append(row)

        return filtered[: req.limit]
