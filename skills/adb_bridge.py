"""COPE ADB USB phone bridge — photos, files, apps, shell, and NL handler."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class ADBBridge:
    """Full ADB USB phone control (photos, files, apps, shell, NL handler)."""

    def __init__(self, settings=None, brain=None, memory=None) -> None:
        self.settings = settings
        self.brain = brain
        self.memory = memory

    def _bin(self) -> str:
        return shutil.which("adb") or "adb"

    def _run(self, *args: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [self._bin(), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def is_connected(self) -> bool:
        """Return True when at least one ADB device is online."""
        if self.settings and not self.settings.get("adb_enabled", True):
            return False
        try:
            result = self._run("devices", timeout=8)
            lines = [
                line for line in result.stdout.splitlines()[1:]
                if line.strip() and "\tdevice" in line
            ]
            return bool(lines)
        except Exception:
            return False

    def connection_status(self) -> str:
        """HUD badge text for USB ADB state."""
        if self.settings and not self.settings.get("adb_enabled", True):
            return "ADB: DISABLED"
        return "ADB: CONNECTED" if self.is_connected() else "ADB: DISCONNECTED"

    def shell(self, command: str) -> str:
        """Run an adb shell command and return stdout/stderr."""
        try:
            result = self._run("shell", command)
            text = (result.stdout or result.stderr or "").strip()
            return text or "OK"
        except Exception as exc:
            return f"ADB shell failed: {exc}"

    def pull_file(self, remote: str, local: str) -> str:
        """Pull a file from the phone to a local path."""
        dest = Path(local)
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            result = self._run("pull", remote, str(dest), timeout=120)
            if result.returncode == 0:
                if self.memory:
                    self.memory.log_activity(f"ADB pull {remote} -> {dest}")
                return f"Pulled {remote} to {dest}."
            return f"Pull failed: {(result.stderr or result.stdout).strip() or 'unknown error'}"
        except Exception as exc:
            return f"Pull failed: {exc}"

    def push_file(self, local: str, remote: str) -> str:
        """Push a local file to the phone."""
        try:
            result = self._run("push", local, remote, timeout=120)
            if result.returncode == 0:
                return f"Pushed {local} to {remote}."
            return f"Push failed: {(result.stderr or result.stdout).strip() or 'unknown error'}"
        except Exception as exc:
            return f"Push failed: {exc}"

    def pull_photos(self, dest: str | None = None) -> str:
        """Pull DCIM photos from the phone."""
        dest_dir = dest or "data/phone_files/photos"
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
        return self.pull_file("/sdcard/DCIM/", dest_dir)

    def screenshot(self, dest: str | None = None) -> str:
        """Capture a phone screenshot and pull it locally."""
        remote = "/sdcard/cope_screenshot.png"
        local = dest or "data/phone_files/cope_screenshot.png"
        self.shell(f"screencap -p {remote}")
        return self.pull_file(remote, local)

    def battery(self) -> str:
        """Return phone battery level from dumpsys."""
        raw = self.shell("dumpsys battery")
        level = ""
        status = ""
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped.startswith("level:"):
                level = stripped.split(":", 1)[-1].strip()
            elif stripped.startswith("status:"):
                status = stripped.split(":", 1)[-1].strip()
        if level:
            return f"Phone battery: {level}% (status {status or 'unknown'})."
        return raw[:400] or "Could not read phone battery."

    def launch_app(self, package_or_name: str) -> str:
        """Launch an Android package (or a best-effort monkey match)."""
        target = package_or_name.strip()
        if not target:
            return "No app specified."
        if "." in target and " " not in target:
            out = self.shell(f"monkey -p {target} -c android.intent.category.LAUNCHER 1")
            return f"Launch requested for {target}. {out[:200]}"
        listing = self.shell("pm list packages")
        needle = target.lower().replace(" ", "")
        match = next((ln.split(":", 1)[-1] for ln in listing.splitlines() if needle in ln.lower()), "")
        if not match:
            return f"No package matching '{target}'."
        out = self.shell(f"monkey -p {match} -c android.intent.category.LAUNCHER 1")
        return f"Launch requested for {match}. {out[:200]}"

    def backup(self, dest: str | None = None) -> str:
        """Pull a coarse sdcard backup into the configured destination."""
        dest_dir = dest
        if not dest_dir and self.settings:
            dest_dir = self.settings.get("adb_backup_dest", "data/phone_backup")
        dest_dir = dest_dir or "data/phone_backup"
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
        return self.pull_file("/sdcard/", dest_dir)

    def handle(self, text: str) -> str:
        """Natural-language router for USB phone commands."""
        t = text.lower()
        if "photo" in t or "picture" in t or "gallery" in t:
            return self.pull_photos()
        if "screenshot" in t:
            return self.screenshot()
        if "battery" in t:
            return self.battery()
        if "backup" in t:
            return self.backup()
        if "launch" in t or "open app" in t or "open " in t and "on phone" in t:
            words = text.split()
            skip = {"launch", "open", "app", "on", "phone", "the", "please"}
            name = " ".join(w for w in words if w.lower() not in skip)
            return self.launch_app(name)
        if "pull" in t and "file" in t:
            parts = text.split()
            remote = next((p for p in parts if p.startswith("/sdcard")), "/sdcard/")
            local = f"data/phone_files/{Path(remote).name}"
            return self.pull_file(remote, local)
        if self.brain:
            return self.brain.ask(text)
        return "ADB command not recognized."
