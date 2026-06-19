"""SQLite memory, reminders, logs, and FTS setup."""
from __future__ import annotations
from pathlib import Path
import sqlite3, datetime as dt

class MemoryStore:
    """Local SQLite storage for conversations, notes, patterns, and reminders."""
    def __init__(self, db_path: str | Path = 'data/jarvis.db') -> None:
        self.db_path = Path(db_path); self.db_path.parent.mkdir(parents=True, exist_ok=True); self.init_db()
    def connect(self) -> sqlite3.Connection:
        """Open a WAL-enabled SQLite connection."""
        con = sqlite3.connect(self.db_path); con.execute('PRAGMA journal_mode=WAL'); return con
    def init_db(self) -> None:
        """Create core tables and FTS index if they do not exist."""
        with self.connect() as con:
            con.executescript('''CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY, kind TEXT, content TEXT, tags TEXT, created_at TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(content, tags, content='entries', content_rowid='id');
CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY, text TEXT, due_at TEXT, recurrence TEXT, done INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS patterns(id INTEGER PRIMARY KEY, event TEXT, metadata TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS activity(id INTEGER PRIMARY KEY, message TEXT, created_at TEXT);''')
    def remember(self, kind: str, content: str, tags: str = '') -> int:
        """Store an item and index it for full-text search."""
        now=dt.datetime.now().isoformat(timespec='seconds')
        with self.connect() as con:
            cur=con.execute('INSERT INTO entries(kind,content,tags,created_at) VALUES(?,?,?,?)',(kind,content,tags,now)); rid=cur.lastrowid
            con.execute('INSERT INTO entries_fts(rowid,content,tags) VALUES(?,?,?)',(rid,content,tags)); return int(rid)
    def search(self, query: str, limit: int = 5) -> list[dict[str,str]]:
        """Search memories using SQLite FTS5."""
        with self.connect() as con:
            rows=con.execute('SELECT e.kind,e.content,e.tags,e.created_at FROM entries_fts f JOIN entries e ON e.id=f.rowid WHERE entries_fts MATCH ? ORDER BY rank LIMIT ?',(query,limit)).fetchall()
        return [{'kind':r[0],'content':r[1],'tags':r[2],'created_at':r[3]} for r in rows]
    def log_activity(self, message: str) -> None:
        """Append a database and daily text activity log entry."""
        now=dt.datetime.now(); Path('data/activity_log').mkdir(parents=True, exist_ok=True)
        with self.connect() as con: con.execute('INSERT INTO activity(message,created_at) VALUES(?,?)',(message,now.isoformat(timespec='seconds')))
        with Path(f'data/activity_log/{now:%Y-%m-%d}.txt').open('a',encoding='utf-8') as f: f.write(f'[{now:%H:%M:%S}] {message}\n')
