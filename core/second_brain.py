"""Searchable second-brain helpers."""
from pathlib import Path
from core.memory import MemoryStore
class SecondBrain:
    """Knowledge-base facade for notes, ideas, and exports."""
    def __init__(self, store: MemoryStore): self.store=store
    def remember_idea(self, idea: str, tags: str='idea') -> int:
        """Store a user idea with optional tags."""; return self.store.remember('idea', idea, tags)
    def recall(self, query: str):
        """Recall matching knowledge entries."""; return self.store.search(query)
    def export_markdown(self, output: str='second_brain.md') -> Path:
        """Export recent memories to Markdown."""
        out=Path(output)
        with self.store.connect() as con: rows=con.execute('SELECT kind,content,tags,created_at FROM entries ORDER BY created_at DESC').fetchall()
        out.write_text('\n'.join(f'## {r[0]} — {r[3]}\nTags: {r[2]}\n\n{r[1]}\n' for r in rows), encoding='utf-8'); return out
