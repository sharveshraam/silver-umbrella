"""Windows system controls."""
import subprocess, pyperclip
class SystemControl:
    """Control apps, clipboard, screenshots, and power actions."""
    def open_app(self, command: str): """Launch an application command."""; return subprocess.Popen(command, shell=True)
    def clipboard_set(self, text: str): """Set clipboard text."""; pyperclip.copy(text)
    def clipboard_get(self): """Read clipboard text."""; return pyperclip.paste()
    def lock(self): """Lock Windows workstation; requires confirmation before call."""; subprocess.run('rundll32.exe user32.dll,LockWorkStation', shell=True)
