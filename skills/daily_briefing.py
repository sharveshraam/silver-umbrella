"""Daily briefing composition."""
import datetime as dt
import requests
class DailyBriefing:
    """Build a morning summary from local reminders and optional APIs."""
    def __init__(self, settings=None, memory=None): self.settings=settings; self.memory=memory
    def compose(self, user: str = "Sir") -> str:
        """Compose weather, reminders, and status into a spoken briefing."""
        parts = [f"Good morning, {user}. Here is your briefing."]
        if self.settings:
            key = self.settings.get("openweather_api_key", ""); city = self.settings.get("location_manual_override", "") or "auto"
            if key and city != "auto":
                try:
                    r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric", timeout=5)
                    w = r.json(); desc = w["weather"][0]["description"]; temp = round(w["main"]["temp"])
                    parts.append(f"Weather in {city}: {desc}, {temp}°C.")
                except Exception: pass
        if self.memory:
            try:
                today = dt.date.today().isoformat()
                with self.memory.connect() as con:
                    rows = con.execute("SELECT text FROM reminders WHERE done=0 AND due_at LIKE ?", (f"{today}%",)).fetchall()
                if rows: parts.append(f"You have {len(rows)} reminder(s) today: " + "; ".join(r[0] for r in rows) + ".")
                else: parts.append("No reminders scheduled for today.")
            except Exception: pass
        parts.append("Systems are nominal. Ready when you are."); return " ".join(parts)
