"""JARVIS desktop entry point."""
import sys
from PyQt6.QtWidgets import QApplication
from core.settings import Settings
from core.memory import MemoryStore
from core.brain import Brain
from core.voice import VoiceEngine
from ui.main_window import MainWindow

def main() -> int:
    """Start JARVIS with lazy-loaded services and the HUD UI."""
    settings=Settings(); memory=MemoryStore(); brain=Brain(settings,memory); voice=VoiceEngine(settings)
    app=QApplication(sys.argv); app.setStyleSheet(open('ui/styles.qss',encoding='utf-8').read())
    win=MainWindow(); win.add_message('JARVIS', f"All systems online. Good to see you again, {settings.get('user_name','Sir')}."); memory.log_activity('JARVIS started')
    win.show(); return app.exec()
if __name__ == '__main__': raise SystemExit(main())
