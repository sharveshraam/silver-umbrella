"""Stealth mode state and silent text routing for JARVIS."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

STEALTH_ON_MESSAGE = "[ Stealth mode activated. I'll keep it quiet, Sir. ]"
STEALTH_OFF_MESSAGE = "[ Stealth mode disabled. Voice systems restored, Sir. ]"

@dataclass
class StealthMode:
    """Manage text-only assistant mode without touching microphone input.

    Stealth mode mutes all speech output while leaving typed input and STT
    transcription available. UI widgets subscribe through ``on_message`` so the
    sidebar and HUD can reflect state changes without coupling core logic to Qt.
    """
    enabled: bool = False
    on_message: Callable[[str, str], None] | None = None

    def activate(self, user_name: str = "Sir") -> str:
        """Enable stealth mode and return the required silent confirmation."""
        self.enabled = True
        message = f"[ Stealth mode activated. I'll keep it quiet, {user_name}. ]"
        self._emit("JARVIS", message)
        return message

    def deactivate(self, user_name: str = "Sir") -> str:
        """Disable stealth mode and return a text confirmation."""
        self.enabled = False
        message = f"[ Stealth mode disabled. Voice systems restored, {user_name}. ]"
        self._emit("JARVIS", message)
        return message

    def toggle(self, user_name: str = "Sir") -> str:
        """Toggle stealth mode on or off."""
        return self.deactivate(user_name) if self.enabled else self.activate(user_name)

    def format_message(self, speaker: str, text: str) -> str:
        """Format a timestamped sidebar chat line."""
        return f"[{datetime.now():%H:%M:%S}] {speaker}: {text}"

    def should_speak(self) -> bool:
        """Return False while stealth is active so TTS callers can stay silent."""
        return not self.enabled

    def _emit(self, speaker: str, text: str) -> None:
        """Notify UI subscribers of a stealth message."""
        if self.on_message:
            self.on_message(speaker, self.format_message(speaker, text))
