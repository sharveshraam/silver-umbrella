"""Main frameless HUD window."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton, QHBoxLayout, QLineEdit
from ui.animations import ArcReactorWidget
class MainWindow(QMainWindow):
    """Full JARVIS HUD with reactor, panels, controls, badges, input, and chat log."""
    stealth_toggled = pyqtSignal()
    sloth_toggled = pyqtSignal()
    message_submitted = pyqtSignal(str)
    def __init__(self):
        super().__init__(); self.setWindowTitle('JARVIS'); self.setWindowFlag(Qt.WindowType.FramelessWindowHint); self.resize(1100,720)
        root=QWidget(); layout=QVBoxLayout(root); top=QHBoxLayout(); self.status=QLabel('IDLE | uptime 00:00 | reminders 0'); self.badge=QLabel('[VOICE]')
        top.addWidget(self.badge)
        self.buttons={}
        for name in ['Mute','Focus Mode','Stealth','Settings','Minimize to Orb','Sloth','Close']:
            btn=QPushButton(name); self.buttons[name]=btn; top.addWidget(btn)
        self.buttons['Stealth'].clicked.connect(self.stealth_toggled.emit); self.buttons['Sloth'].clicked.connect(self.sloth_toggled.emit)
        layout.addLayout(top); self.reactor=ArcReactorWidget(); layout.addWidget(self.reactor,3); self.chat=QTextEdit(); self.chat.setReadOnly(True); layout.addWidget(self.chat,1)
        self.input = QLineEdit(); self.input.setPlaceholderText("Talk to JARVIS..."); self.input.returnPressed.connect(self._emit_and_clear); layout.addWidget(self.input)
        layout.addWidget(self.status); self.setCentralWidget(root)
    def add_message(self, who: str, text: str): """Append a chat message."""; self.chat.append(f'<b>{who}:</b> {text}')
    def set_stealth_badge(self, active: bool): """Show stealth/voice mode in the HUD."""; self.badge.setText('[STEALTH]' if active else '[VOICE]')
    def set_sleeping_badge(self, active: bool): """Show sleeping mode in the HUD."""; self.badge.setText('[SLEEPING]' if active else '[VOICE]')
    def _emit_and_clear(self):
        """Emit typed input and clear the main HUD input box."""
        text = self.input.text().strip()
        if text:
            self.message_submitted.emit(text)
            self.input.clear()
