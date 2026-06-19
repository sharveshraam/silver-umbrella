"""Configuration loading for JARVIS."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml

@dataclass
class Settings:
    """Typed wrapper around config.yaml with safe defaults."""
    path: Path = Path('config.yaml')
    values: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        """Load YAML settings from disk and return a mutable dictionary."""
        if self.values is None:
            self.values = yaml.safe_load(self.path.read_text(encoding='utf-8')) if self.path.exists() else {}
        return self.values

    def get(self, key: str, default: Any = None) -> Any:
        """Return a setting by key, falling back to default when missing."""
        return self.load().get(key, default)

    def feature_enabled(self, name: str) -> bool:
        """Return whether a feature flag is enabled in config.yaml."""
        return bool(self.load().get('features', {}).get(name, True))
