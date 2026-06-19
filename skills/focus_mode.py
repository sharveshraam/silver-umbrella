"""Pomodoro and site-blocking focus mode."""
import time, threading
from pathlib import Path
HOSTS = Path("C:/Windows/System32/drivers/etc/hosts")
REDIRECT = "127.0.0.1"
class FocusMode:
    """Plan and apply hosts-file blocks for focus sessions."""
    def __init__(self, settings): self.settings=settings; self.active=False
    def blocked_sites(self): """Return configured distracting sites."""; return self.settings.get('focus_blocked_sites', [])
    def start(self, minutes: int=25, on_complete=None):
        """Block sites, start timer, call on_complete when done."""
        self._block_sites(); self.active=True
        def _timer():
            time.sleep(minutes * 60); self._unblock_sites(); self.active=False
            if callable(on_complete): on_complete()
        threading.Thread(target=_timer, daemon=True).start()
        return f"Focus mode started. {minutes} minutes. Blocking: {', '.join(self.blocked_sites())}."
    def stop(self) -> str:
        """End focus mode and unblock configured sites."""; self._unblock_sites(); self.active=False; return "Focus mode ended."
    def _block_sites(self):
        """Append hosts-file entries for configured sites when permitted."""
        try:
            content = HOSTS.read_text(encoding="utf-8") if HOSTS.exists() else ""; additions = ""
            for site in self.blocked_sites():
                entry = f"{REDIRECT} {site}"
                if entry not in content: additions += f"\n{entry}"
            if additions:
                with HOSTS.open("a", encoding="utf-8") as f: f.write(additions)
        except (PermissionError, OSError): pass
    def _unblock_sites(self):
        """Remove hosts-file entries for configured sites when permitted."""
        try:
            if not HOSTS.exists(): return
            lines = HOSTS.read_text(encoding="utf-8").splitlines(); cleaned = [l for l in lines if not any(s in l for s in self.blocked_sites())]
            HOSTS.write_text("\n".join(cleaned), encoding="utf-8")
        except (PermissionError, OSError): pass
