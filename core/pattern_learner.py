"""Behavior logging and suggestion generation."""
import datetime as dt, json
class PatternLearner:
    """Lightweight local analytics for repeated user behavior."""
    def __init__(self, memory): self.memory=memory
    def log_event(self, event: str, **metadata) -> None:
        """Record a timestamped behavioral event."""
        with self.memory.connect() as con: con.execute('INSERT INTO patterns(event,metadata,created_at) VALUES(?,?,?)',(event,json.dumps(metadata),dt.datetime.now().isoformat(timespec='seconds')))
    def suggestions(self) -> list[str]:
        """Return simple frequency-based suggestions for the current hour."""
        hour=f'{dt.datetime.now():%H}'
        with self.memory.connect() as con: rows=con.execute("SELECT event,count(*) FROM patterns WHERE strftime('%H',created_at)=? GROUP BY event HAVING count(*)>=3",(hour,)).fetchall()
        return [f'Sir, you often start {e} around now. Shall I begin?' for e,_ in rows]
