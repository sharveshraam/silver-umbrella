"""Teaching mode: layered explanations for errors and concepts."""
from __future__ import annotations
from dataclasses import dataclass
import re

ERROR_PATTERNS = {
    "path": ("PATH/environment variables", ["not recognized", "command not found", "No such file or directory"]),
    "git_conflict": ("Git merge conflicts", ["CONFLICT", "merge conflict", "unmerged paths"]),
    "network": ("network connectivity", ["timed out", "DNS", "ConnectionError", "NameResolutionError"]),
    "python_import": ("Python imports and environments", ["ModuleNotFoundError", "ImportError"]),
    "ffmpeg": ("video codecs and FFmpeg", ["ffmpeg", "codec", "Invalid data found"]),
    "bootloader": ("UEFI, Legacy BIOS, and bootloaders", ["bootloader", "no bootable", "UEFI", "Legacy"]),
}

@dataclass
class Teacher:
    """Detect repeated concepts and produce layered teaching responses."""
    memory: object
    depth: str = "medium"
    skip_known: bool = True

    def detect_concept(self, text: str) -> str:
        """Infer the most likely concept from an error or user question."""
        lowered = text.lower()
        for key, (_, needles) in ERROR_PATTERNS.items():
            if any(n.lower() in lowered for n in needles):
                return key
        if re.search(r"what happened|why did|error|failed|traceback", lowered):
            return "general_error"
        return "general_question"

    def has_taught(self, concept: str) -> bool:
        """Return whether the concept was already recorded in memory."""
        try:
            return bool(self.memory.search(f"teaching_{concept}", limit=1))
        except Exception:
            return False

    def explain_error(self, text: str, depth: str | None = None, just_fix: bool = False) -> str:
        """Create a six-part teaching explanation for an error or failure."""
        concept = self.detect_concept(text)
        topic = ERROR_PATTERNS.get(concept, (concept.replace("_", " "), []))[0]
        if just_fix:
            return self._fix_only(topic, text)
        known = self.skip_known and self.has_taught(concept)
        explanation_depth = depth or self.depth
        lines = []
        if known:
            lines.append(f"As you'll remember, Sir — this looks like the same {topic} issue we've covered before. Short version first:")
        lines.extend([
            f"1. What just happened: JARVIS detected a failure related to {topic}. The system tried to complete the task, but one required assumption was not true.",
            f"2. Why it happened: {self._why(topic)}",
            f"3. The deeper knowledge: {self._deeper(topic, explanation_depth)}",
            f"4. How to fix it right now: {self._fix_now(topic)}",
            f"5. How to avoid it next time: {self._avoid(topic)}",
            "6. Want me to go deeper on any of this, Sir?",
        ])
        self._record_teaching(concept, topic)
        return "\n".join(lines)

    def proactive_suggestions(self, concept: str, threshold: int = 3) -> str | None:
        """Suggest a mini-lesson after repeated related failures."""
        try:
            hits = self.memory.search(concept, limit=threshold)
        except Exception:
            hits = []
        if len(hits) >= threshold:
            return f"Sir, you've run into {concept.replace('_', ' ')} issues {len(hits)} times recently. Want a quick 5-minute walkthrough?"
        return None

    def _record_teaching(self, concept: str, topic: str) -> None:
        """Store taught concepts in the Second Brain memory."""
        try:
            self.memory.remember("teaching", f"teaching_{concept}: Explained {topic}", f"teaching,{concept}")
        except Exception:
            pass

    def _why(self, topic: str) -> str:
        return f"The task depends on {topic}; when that layer is misconfigured or unavailable, higher-level automation cannot continue safely."

    def _deeper(self, topic: str, depth: str) -> str:
        if depth == "simple":
            return f"Think of {topic} like a signpost. If the signpost points the wrong way, JARVIS reaches the wrong place."
        if depth == "deep":
            return f"{topic} sits below the visible app layer. JARVIS checks symptoms, maps them to the failing layer, then recommends the least destructive fix first."
        return f"Think of {topic} as infrastructure: invisible when working, but every workflow depends on it being consistent."

    def _fix_now(self, topic: str) -> str:
        return f"Pause the workflow, inspect the exact error text, verify the {topic} setup, then retry the smallest failing step before running the full task again."

    def _avoid(self, topic: str) -> str:
        return f"Keep a known-good setup note for {topic}, validate dependencies before big workflows, and let JARVIS save the lesson to your Second Brain."

    def _fix_only(self, topic: str, text: str) -> str:
        return f"Understood, Sir. I'll skip the lesson: check the {topic} configuration, apply the smallest safe fix, and rerun the failed step."
