"""Location, network, and battery adaptation for JARVIS."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess, time
import importlib.util
import json
from urllib.request import urlopen
psutil = None
if importlib.util.find_spec("psutil"):
    import psutil

@dataclass
class LocationContext:
    """Local context detected at startup and stored in memory."""
    city: str = ""
    region: str = ""
    country: str = ""
    country_code: str = ""
    timezone: str = "UTC"
    latitude: float | None = None
    longitude: float | None = None
    offline: bool = False
    ping_ms: float | None = None
    battery_percent: int | None = None
    plugged_in: bool | None = None

class LocationAdapter:
    """Detect local context and recommend performance/workflow changes."""
    def __init__(self, settings, memory=None) -> None:
        self.settings = settings
        self.memory = memory
        self.context = LocationContext()

    def refresh(self) -> LocationContext:
        """Refresh location, network, and power context with short timeouts."""
        manual = self.settings.get("location_manual_override", "")
        if manual:
            self.context.city = manual
        elif self.settings.get("location_adaptive", True):
            self._detect_ip_location()
        if self.settings.get("network_awareness", True):
            self.context.ping_ms = self.ping_ms()
            self.context.offline = self.context.ping_ms is None
        if self.settings.get("battery_awareness", True):
            self._detect_battery()
        self._store_context()
        return self.context

    def local_now(self) -> datetime:
        """Return current time in the detected timezone."""
        try:
            return datetime.now(ZoneInfo(self.context.timezone))
        except Exception:
            return datetime.now()

    def recommendations(self) -> list[str]:
        """Return adaptive recommendations for network and battery state."""
        recs: list[str] = []
        if self.context.offline:
            recs.append("Network appears offline; web workflows should stay disabled and local LLM mode should be preferred.")
        elif self.context.ping_ms and self.context.ping_ms > 250:
            recs.append(f"Connection latency is high ({self.context.ping_ms:.0f} ms); postpone large downloads/uploads or reduce video quality.")
        low = self.settings.get("battery_low_threshold", 20)
        critical = self.settings.get("battery_critical_threshold", 10)
        if self.context.battery_percent is not None and self.context.plugged_in is False:
            if self.context.battery_percent <= critical:
                recs.append("Battery is critical; pause workflows, save state, and alert the user.")
            elif self.context.battery_percent <= low:
                recs.append("Battery is low; enable performance mode and skip heavy learning/video tasks.")
        return recs

    def dialect(self) -> str:
        """Return the language dialect to use for phrasing."""
        configured = self.settings.get("language_dialect", "auto")
        if configured != "auto":
            return configured
        if self.context.country_code:
            return f"en-{self.context.country_code.upper()}"
        return "en-US"

    def _detect_ip_location(self) -> None:
        """Detect coarse location via ip-api.com with a short timeout."""
        try:
            with urlopen("http://ip-api.com/json/?fields=status,city,regionName,country,countryCode,timezone,lat,lon", timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))
            if data.get("status") == "success":
                self.context.city = data.get("city", "")
                self.context.region = data.get("regionName", "")
                self.context.country = data.get("country", "")
                self.context.country_code = data.get("countryCode", "")
                self.context.timezone = data.get("timezone", "UTC")
                self.context.latitude = data.get("lat")
                self.context.longitude = data.get("lon")
        except Exception:
            self.context.offline = True

    def ping_ms(self, host: str = "1.1.1.1") -> float | None:
        """Run a quick one-packet ping and return approximate latency."""
        is_windows = bool(psutil and getattr(psutil, "WINDOWS", False))
        command = ["ping", "-n", "1", host] if is_windows else ["ping", "-c", "1", host]
        start = time.perf_counter()
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3, check=True)
            return (time.perf_counter() - start) * 1000
        except Exception:
            return None

    def _detect_battery(self) -> None:
        """Detect battery percentage and plugged-in state when available."""
        battery = psutil.sensors_battery() if psutil else None
        if battery is not None:
            self.context.battery_percent = int(battery.percent)
            self.context.plugged_in = bool(battery.power_plugged)

    def _store_context(self) -> None:
        """Persist context locally for auditing and adaptation."""
        if not self.memory:
            return
        try:
            self.memory.remember("location_context", str(self.context), "location,adaptive")
        except Exception:
            pass
