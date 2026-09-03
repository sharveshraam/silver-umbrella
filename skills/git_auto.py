"""Git automation skill."""
from git import Repo
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading, time
class _ChangeHandler(FileSystemEventHandler):
    """Debounced watchdog handler for project changes."""
    def __init__(self):
        self._pending = False
    def on_any_event(self, event):
        """Mark a pending change for non-directory, non-pyc files."""
        if not event.is_directory and not event.src_path.endswith(".pyc"):
            self._pending = True
class GitAuto:
    """Stage, commit, and watch local project changes without pushing."""
    def __init__(self, brain=None): self.brain = brain; self._observer = None
    def commit_all(self, repo_path: str, message: str) -> str:
        """Stage all changes and commit with a provided message."""
        repo=Repo(repo_path); repo.git.add(A=True)
        if not repo.index.diff("HEAD") and not repo.untracked_files: return "Nothing to commit."
        repo.index.commit(message); return f"Committed: {message}"
    def auto_message(self, repo_path: str) -> str:
        """Generate a commit message using LLM based on git diff."""
        repo = Repo(repo_path); diff = repo.git.diff("HEAD") or "New files added"
        if self.brain: return self.brain.ask(f"Write a short git commit message (under 72 chars) for this diff:\n{diff[:2000]}")
        return "Auto-commit by JARVIS"
    def start_watching(self, repo_path: str, debounce_seconds: int = 30) -> None:
        """Watch a project folder and auto-commit after debounce period of inactivity."""
        handler = _ChangeHandler(); self._observer = Observer(); self._observer.schedule(handler, repo_path, recursive=True); self._observer.start()
        def _debounce_loop():
            while True:
                time.sleep(debounce_seconds)
                if handler._pending:
                    handler._pending = False; msg = self.auto_message(repo_path); self.commit_all(repo_path, msg)
        threading.Thread(target=_debounce_loop, daemon=True).start()
    def stop_watching(self):
        """Stop watching for changes."""
        if self._observer: self._observer.stop()
