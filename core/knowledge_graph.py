"""SQLite nodes, edges, and personal timeline for COPE."""
from __future__ import annotations

import datetime as dt
import sqlite3
from pathlib import Path


class KnowledgeGraph:
    """Project/file/session graph plus a queryable personal timeline."""

    def __init__(self, db_path: str | Path = "data/knowledge_graph.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        """Open a WAL-enabled SQLite connection."""
        con = sqlite3.connect(self.db_path)
        con.execute("PRAGMA journal_mode=WAL")
        return con

    def _init_db(self) -> None:
        with self.connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS nodes(
                    id INTEGER PRIMARY KEY,
                    kind TEXT,
                    name TEXT,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS edges(
                    id INTEGER PRIMARY KEY,
                    src INTEGER,
                    dst INTEGER,
                    relation TEXT,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS timeline(
                    id INTEGER PRIMARY KEY,
                    event_type TEXT,
                    entity TEXT,
                    description TEXT,
                    extra TEXT,
                    created_at TEXT
                );
                """
            )

    def add_node(self, kind: str, name: str) -> int:
        """Insert a graph node and return its id."""
        now = dt.datetime.now().isoformat(timespec="seconds")
        with self.connect() as con:
            cur = con.execute(
                "INSERT INTO nodes(kind,name,created_at) VALUES(?,?,?)",
                (kind, name, now),
            )
            return int(cur.lastrowid)

    def add_edge(self, src: int, dst: int, relation: str) -> int:
        """Link two nodes (project/file/session)."""
        now = dt.datetime.now().isoformat(timespec="seconds")
        with self.connect() as con:
            cur = con.execute(
                "INSERT INTO edges(src,dst,relation,created_at) VALUES(?,?,?,?)",
                (src, dst, relation, now),
            )
            return int(cur.lastrowid)

    def add_event(self, event_type: str, entity: str, description: str, extra: str = "") -> int:
        """Append a personal-timeline event and a matching node."""
        now = dt.datetime.now().isoformat(timespec="seconds")
        with self.connect() as con:
            con.execute(
                "INSERT INTO nodes(kind,name,created_at) VALUES(?,?,?)",
                (event_type, entity, now),
            )
            cur = con.execute(
                "INSERT INTO timeline(event_type,entity,description,extra,created_at) VALUES(?,?,?,?,?)",
                (event_type, entity, description, extra, now),
            )
            return int(cur.lastrowid)

    def timeline_query(self, text: str) -> str:
        """Search the personal timeline with a meaning-preserving keyword filter."""
        keywords = [w for w in text.lower().split()
                    if len(w) >= 4
                    and w not in {"when", "what", "show", "were", "working",
                                  "timeline", "with", "that", "this", "from",
                                  "have", "been", "tell", "about"}]
        with self.connect() as con:
            if not keywords:
                rows = con.execute(
                    "SELECT event_type, entity, description, created_at FROM timeline ORDER BY created_at DESC LIMIT 12"
                ).fetchall()
            else:
                clauses = []
                params: list[str] = []
                for word in keywords:
                    like = f"%{word}%"
                    clauses.append("(description LIKE ? OR entity LIKE ? OR event_type LIKE ?)")
                    params.extend([like, like, like])
                sql = (
                    "SELECT event_type, entity, description, created_at FROM timeline "
                    f"WHERE {' OR '.join(clauses)} ORDER BY created_at DESC LIMIT 20"
                )
                rows = con.execute(sql, params).fetchall()
        if not rows:
            return "No timeline events match that query."
        lines = [f"- [{row[3]}] {row[0]} / {row[1]}: {row[2]}" for row in rows]
        return "Timeline:\n" + "\n".join(lines)
