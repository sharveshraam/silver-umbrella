"""Coding assistant skill."""
import subprocess
from pathlib import Path
class Coder:
    """Run, write, explain, and fix code with an LLM brain."""
    def __init__(self, brain=None): self.brain = brain
    def run_python(self, path: str) -> str:
        """Run a Python file and return combined stdout + stderr."""; result = subprocess.run(["python", path], capture_output=True, text=True, timeout=60); return (result.stdout + result.stderr).strip()
    def write_code(self, description: str, output_path: str, language: str = "python") -> str:
        """Ask LLM to write code and save it to a file."""
        prompt = f"Write complete {language} code for the following: {description}\nRespond with only the code, no explanation."
        code = self.brain.ask(prompt) if self.brain else "# JARVIS brain unavailable\n"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True); Path(output_path).write_text(code, encoding="utf-8"); return output_path
    def explain_code(self, file_path: str) -> str:
        """Read a file and ask LLM to explain it."""; code = Path(file_path).read_text(encoding="utf-8"); return self.brain.ask(f"Explain this code clearly:\n\n{code[:3000]}") if self.brain else code[:1000]
    def fix_code(self, file_path: str, error: str) -> str:
        """Read a file + error, ask LLM to fix it, save and return."""
        code = Path(file_path).read_text(encoding="utf-8"); prompt = f"Fix this code. Error: {error}\n\nCode:\n{code[:3000]}\n\nRespond with only the corrected code."
        fixed = self.brain.ask(prompt) if self.brain else code; Path(file_path).write_text(fixed, encoding="utf-8"); return f"Fixed and saved to {file_path}."
