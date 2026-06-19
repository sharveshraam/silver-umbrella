"""Main frameless HUD window."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton, QHBoxLayout
from ui.animations import ArcReactorWidget
class MainWindow(QMainWindow):
    """Full JARVIS HUD with reactor, panels, controls, and chat log."""
    def __init__(self):
        super().__init__(); self.setWindowTitle('JARVIS'); self.setWindowFlag(Qt.WindowType.FramelessWindowHint); self.resize(1100,720)
        root=QWidget(); layout=QVBoxLayout(root); top=QHBoxLayout(); self.status=QLabel('IDLE | uptime 00:00 | reminders 0');
        for name in ['Mute','Focus Mode','Settings','Minimize to Orb','Close']: top.addWidget(QPushButton(name))
        layout.addLayout(top); self.reactor=ArcReactorWidget(); layout.addWidget(self.reactor,3); self.chat=QTextEdit(); self.chat.setReadOnly(True); layout.addWidget(self.chat,1); layout.addWidget(self.status); self.setCentralWidget(root)
    def add_message(self, who: str, text: str): """Append a chat message."""; self.chat.append(f'<b>{who}:</b> {text}')
