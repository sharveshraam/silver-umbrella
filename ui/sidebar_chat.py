"""Stealth mode sidebar chat widget."""
from __future__ import annotations
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QLabel, QSizeGrip

class SidebarChat(QWidget):
    """Always-on-top terminal-style text sidebar for silent JARVIS replies."""
    submitted = pyqtSignal(str)

    def __init__(self, position: str = "right", opacity: float = 0.85) -> None:
        super().__init__()
        self.position = position
        self.setWindowTitle("JARVIS Stealth Chat")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(opacity)
        self.resize(360, 640)
        layout = QVBoxLayout(self)
        self.badge = QLabel("[STEALTH]")
        self.badge.setObjectName("stealthBadge")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type to JARVIS silently...")
        self.input.returnPressed.connect(self._submit)
        layout.addWidget(self.badge)
        layout.addWidget(self.log, 1)
        layout.addWidget(self.input)
        layout.addWidget(QSizeGrip(self), 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self._drag_pos = None

    def append_message(self, text: str) -> None:
        """Append a timestamped sidebar message."""
        self.log.append(text)

    def set_stealth_active(self, active: bool) -> None:
        """Update the visible stealth badge."""
        self.badge.setText("[STEALTH]" if active else "[VOICE]")

    def _submit(self) -> None:
        """Emit typed input and clear the input box."""
        text = self.input.text().strip()
        if text:
            self.submitted.emit(text)
            self.input.clear()

    def mousePressEvent(self, event):
        """Start window drag."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Drag the frameless sidebar."""
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """End window drag."""
        self._drag_pos = None
