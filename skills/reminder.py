"""Reminder creation and notification."""
import datetime as dt
class ReminderSkill:
    """Manage reminder records and callbacks."""
    def __init__(self, memory): self.memory=memory
    def create(self, text: str, due_at: str, recurrence: str='') -> int:
        """Create a reminder in SQLite."""
        with self.memory.connect() as con:
            cur=con.execute('INSERT INTO reminders(text,due_at,recurrence) VALUES(?,?,?)',(text,due_at,recurrence)); return int(cur.lastrowid)
    def due(self):
        """Return due reminder rows."""
        now=dt.datetime.now().isoformat(timespec='seconds')
        with self.memory.connect() as con: return con.execute('SELECT id,text,due_at FROM reminders WHERE done=0 AND due_at<=?',(now,)).fetchall()
