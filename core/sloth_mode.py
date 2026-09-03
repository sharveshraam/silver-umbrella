"""Full deep-sleep / DND state manager for JARVIS."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Any
import importlib.util
psutil = None
if importlib.util.find_spec("psutil"):
    import psutil

SLOTH_ON_MESSAGE = "[ Sloth mode on. Rest well, Sir. Wake me when you need me. ]"

@dataclass
class SlothMode:
    """Suspend wake detection, workflows, reminders, sound, and animations.

    Sloth is intentionally stronger than mute or stealth: callers should check
    ``is_active`` before doing background work, clap detection, reminders, or
    alerts. Only explicit UI/hotkey/timer wake paths should call ``wake``.
    """
    active: bool = False
    paused_workflows: list[dict[str, Any]] = field(default_factory=list)
    snoozed_reminders: list[dict[str, Any]] = field(default_factory=list)
    last_sleep_at: datetime | None = None

    def sleep(self, workflows: list[dict[str, Any]] | None = None, reminders: list[dict[str, Any]] | None = None) -> str:
        """Enter Sloth Mode and snapshot resumable state."""
        self.active = True
        self.last_sleep_at = datetime.now()
        if workflows:
            self.paused_workflows.extend(workflows)
        if reminders:
            self.snoozed_reminders.extend(reminders)
        return SLOTH_ON_MESSAGE

    def wake(self, user_name: str = "Sir") -> str:
        """Wake JARVIS and report snoozed reminder count."""
        self.active = False
        count = len(self.snoozed_reminders)
        self.paused_workflows.clear()
        self.snoozed_reminders.clear()
        return f"Good to be back, {user_name}. You have {count} snoozed reminders."

    def is_active(self) -> bool:
        """Return whether JARVIS should ignore all automatic triggers."""
        return self.active

    def should_auto_sleep_for_processes(self, process_names: list[str]) -> bool:
        """Return True if a configured game/process is currently running."""
        wanted = {name.lower() for name in process_names}
        if not wanted:
            return False
        if psutil is None:
            return False
        for proc in psutil.process_iter(attrs=["name"]):
            name = (proc.info.get("name") or "").lower()
            if name in wanted:
                return True
        return False

    def is_in_schedule_window(self, sleep_at: str, wake_at: str, now: time | None = None) -> bool:
        """Return whether the current local time is inside the sleep window."""
        current = now or datetime.now().time()
        sleep_t = time.fromisoformat(sleep_at)
        wake_t = time.fromisoformat(wake_at)
        if sleep_t <= wake_t:
            return sleep_t <= current < wake_t
        return current >= sleep_t or current < wake_t
