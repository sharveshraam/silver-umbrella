"""Idle-triggered self-learning engine for JARVIS."""
from __future__ import annotations
from dataclasses import dataclass, field
from threading import Event, Thread
from time import sleep, time
import re
import importlib.util
from urllib.request import urlopen
from xml.etree import ElementTree
psutil = None
if importlib.util.find_spec("psutil"):
    import psutil

@dataclass
class LearnedItem:
    """One summarized item learned during idle time."""
    title: str
    summary: str
    source: str
    tags: str

class SelfLearner:
    """Fetch, summarize, and store knowledge only during natural idle periods."""
    def __init__(self, settings, memory, brain=None, sloth_mode=None) -> None:
        self.settings = settings
        self.memory = memory
        self.brain = brain
        self.sloth_mode = sloth_mode
        self.stop_event = Event()
        self.worker: Thread | None = None
        self.running_workflow = False
        self.learned_since_return: list[LearnedItem] = []

    def should_learn(self, idle_seconds: float) -> bool:
        """Return True when idle learning is allowed by config and system state."""
        if not self.settings.get("self_learning_enabled", True):
            return False
        if self.settings.get("learning_trigger", "idle") != "idle":
            return False
        if self.sloth_mode and self.sloth_mode.is_active():
            return False
        if self.running_workflow:
            return False
        threshold = int(self.settings.get("idle_threshold_minutes", 10)) * 60
        if idle_seconds < threshold:
            return False
        battery = psutil.sensors_battery() if psutil else None
        if battery and not battery.power_plugged and battery.percent < 20:
            return False
        return True

    def tick(self, idle_seconds: float) -> None:
        """Start or stop learning based on the latest idle duration."""
        if self.should_learn(idle_seconds):
            self.start_learning_session()
        else:
            self.stop_learning_session()

    def start_learning_session(self) -> None:
        """Start a non-blocking low-priority learning worker."""
        if self.worker and self.worker.is_alive():
            return
        self.stop_event.clear()
        self.worker = Thread(target=self._learn_loop, name="jarvis-self-learner", daemon=True)
        self.worker.start()

    def stop_learning_session(self) -> None:
        """Request the learning worker to stop immediately."""
        self.stop_event.set()

    def recent_learnings(self, limit: int = 5) -> list[dict[str, str]]:
        """Return recently learned summaries from memory."""
        try:
            return self.memory.search("learned", limit=limit)
        except Exception:
            return []

    def interest_profile(self) -> list[str]:
        """Build a lightweight local interest profile from stored user data."""
        try:
            rows = self.memory.search("idea OR research OR workflow OR command", limit=25)
        except Exception:
            rows = []
        words: dict[str, int] = {}
        for row in rows:
            for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", row.get("content", "").lower()):
                if word not in {"this", "that", "with", "from", "jarvis", "sir"}:
                    words[word] = words.get(word, 0) + 1
        return [word for word, _ in sorted(words.items(), key=lambda kv: kv[1], reverse=True)[:12]]

    def _learn_loop(self) -> None:
        """Fetch RSS sources, summarize first items, and store them locally."""
        sources = self.settings.get("learning_sources", [])
        interests = set(self.interest_profile())
        for source in sources:
            if self.stop_event.is_set():
                break
            for title, link in self._rss_items(source)[:3]:
                if self.stop_event.is_set():
                    break
                summary = self._summarize(title, link, interests)
                item = LearnedItem(title=title, summary=summary, source=link or source, tags="learned,self_learning")
                self.learned_since_return.append(item)
                try:
                    self.memory.remember("learned", f"learned: {title}\n{summary}\nSource: {item.source}", item.tags)
                except Exception:
                    pass
                sleep(0.2)

    def _rss_items(self, url: str) -> list[tuple[str, str]]:
        """Fetch RSS/Atom entries with a short timeout using the stdlib."""
        try:
            with urlopen(url, timeout=6) as response:
                xml = response.read()
            root = ElementTree.fromstring(xml)
            results: list[tuple[str, str]] = []
            for entry in list(root.iter()):
                tag = entry.tag.rsplit('}', 1)[-1].lower()
                if tag not in {'item', 'entry'}:
                    continue
                title = 'Untitled'; link = url
                for child in list(entry):
                    child_tag = child.tag.rsplit('}', 1)[-1].lower()
                    if child_tag == 'title' and child.text:
                        title = child.text.strip()
                    elif child_tag == 'link':
                        link = child.attrib.get('href') or (child.text.strip() if child.text else link)
                results.append((title, link))
            return results
        except Exception:
            return []

    def _summarize(self, title: str, link: str, interests: set[str]) -> str:
        """Summarize with the local brain when present, else use a cheap fallback."""
        relevance = "relevant" if any(word in title.lower() for word in interests) else "possibly useful"
        prompt = f"Summarize this article for the user's Second Brain in 3 bullets. Title: {title}. URL: {link}"
        if self.brain:
            try:
                return self.brain.ask(prompt)[:1200]
            except Exception:
                pass
        return f"{title} appears {relevance}. Review source for details: {link}"
