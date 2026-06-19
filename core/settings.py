"""Configuration loading for JARVIS."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import ast
import importlib.util

@dataclass
class Settings:
    """Typed wrapper around config.yaml with safe defaults."""
    path: Path = Path('config.yaml')
    values: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        """Load YAML settings from disk and return a mutable dictionary."""
        if self.values is None:
            text = self.path.read_text(encoding='utf-8') if self.path.exists() else ''
            if importlib.util.find_spec('yaml'):
                import yaml
                self.values = yaml.safe_load(text) or {}
            else:
                self.values = _parse_simple_yaml(text)
        return self.values

    def get(self, key: str, default: Any = None) -> Any:
        """Return a setting by key, falling back to default when missing."""
        return self.load().get(key, default)

    def feature_enabled(self, name: str) -> bool:
        """Return whether a feature flag is enabled in config.yaml."""
        return bool(self.load().get('features', {}).get(name, True))

def _parse_scalar(value: str) -> Any:
    """Parse the scalar subset used by the default config file."""
    value = value.strip()
    if value.lower() == 'true': return True
    if value.lower() == 'false': return False
    if value in {'', 'null', 'None'}: return '' if value == '' else None
    try: return ast.literal_eval(value)
    except Exception: pass
    try: return int(value)
    except ValueError: pass
    try: return float(value)
    except ValueError: return value.strip('"\'')

def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse a small YAML subset so JARVIS can boot before dependencies install."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    pending_key: tuple[int, dict[str, Any], str] | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        indent = len(raw) - len(raw.lstrip(' ')); line = raw.strip()
        while stack and indent <= stack[-1][0]: stack.pop()
        parent = stack[-1][1]
        if line.startswith('- '):
            item = _parse_scalar(line[2:])
            if not isinstance(parent, list):
                if pending_key:
                    _, container, key = pending_key; container[key] = []; parent = container[key]; stack.append((indent-2, parent))
            parent.append(item); continue
        key, _, value = line.partition(':')
        key = key.strip(); value = value.strip()
        if value == '':
            container: dict[str, Any] = {}
            parent[key] = container
            pending_key = (indent, parent, key)
            stack.append((indent, container))
        else:
            parent[key] = _parse_scalar(value)
            pending_key = None
    return root
