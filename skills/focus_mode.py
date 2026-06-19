"""Pomodoro and site-blocking focus mode."""
class FocusMode:
    """Plan host-file blocks and quiet notifications for focus sessions."""
    def __init__(self, settings): self.settings=settings
    def blocked_sites(self): """Return configured distracting sites."""; return self.settings.get('focus_blocked_sites', [])
    def start(self, minutes: int=25): """Return focus session metadata."""; return {'minutes':minutes,'blocked':self.blocked_sites()}
