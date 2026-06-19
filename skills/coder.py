"""Coding assistant skill."""
import subprocess
class Coder:
    """Run scripts and save generated code."""
    def run_python(self, path): """Run a Python file and capture output."""; return subprocess.run(['python',path],capture_output=True,text=True,timeout=60)
