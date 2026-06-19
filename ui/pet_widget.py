"""Animated floating desktop companion pet for JARVIS."""
from __future__ import annotations
from enum import Enum
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush
from PyQt6.QtWidgets import QWidget, QMenu, QLabel

class PetState(str, Enum):
    """Supported companion animation states."""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    WORKING = "working"
    HAPPY = "happy"
    ALERT = "alert"
    SLEEPING = "sleeping"
    STEALTH = "stealth"
    FOCUSED = "focused"
    READING = "reading"

class PetWidget(QWidget):
    """Transparent always-on-top pet rendered with lightweight QPainter."""
    def __init__(self, size: int = 120, speech_bubbles: bool = True) -> None:
        super().__init__()
        self.state = PetState.IDLE
        self.phase = 0
        self.speech_bubbles = speech_bubbles
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(size, size)
        self.bubble = QLabel("", self)
        self.bubble.setStyleSheet("background: rgba(0,10,18,210); color: #9ffcff; border: 1px solid #00d9ff; border-radius: 8px; padding: 4px;")
        self.bubble.hide()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(80)
        self._drag_pos = None

    def set_state(self, state: str | PetState) -> None:
        """Set pet animation state."""
        self.state = PetState(state)
        if self.state == PetState.SLEEPING:
            self.timer.stop()
        elif not self.timer.isActive():
            self.timer.start(80)
        self.update()

    def show_bubble(self, message: str, ms: int = 4000) -> None:
        """Show a short auto-dismissing speech bubble."""
        if not self.speech_bubbles or len(message.split()) > 15:
            return
        self.bubble.setText(message)
        self.bubble.adjustSize()
        self.bubble.move(max(0, (self.width() - self.bubble.width()) // 2), 0)
        self.bubble.show()
        QTimer.singleShot(ms, self.bubble.hide)

    def paintEvent(self, _event) -> None:
        """Paint an animated orb/helmet-like companion face."""
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width(); h = self.height(); bob = 0 if self.state == PetState.SLEEPING else (self.phase % 12) - 6
        center_y = h * 0.55 + bob * 0.4
        color = self._state_color()
        p.setPen(QPen(color, 3))
        p.setBrush(QBrush(QColor(5, 18, 32, 210)))
        p.drawEllipse(QRectF(w*0.15, center_y-h*0.32, w*0.7, h*0.58))
        eye_y = center_y - h*0.08
        if self.state == PetState.SLEEPING:
            p.drawText(int(w*0.62), int(h*0.25), "Zzz")
            p.drawLine(int(w*0.32), int(eye_y), int(w*0.45), int(eye_y))
            p.drawLine(int(w*0.55), int(eye_y), int(w*0.68), int(eye_y))
        else:
            eye_h = h*0.08 if self.state != PetState.ALERT else h*0.13
            p.setBrush(QBrush(color))
            p.drawRoundedRect(QRectF(w*0.31, eye_y, w*0.14, eye_h), 4, 4)
            p.drawRoundedRect(QRectF(w*0.55, eye_y, w*0.14, eye_h), 4, 4)
        if self.state == PetState.WORKING:
            p.drawRect(int(w*0.25), int(h*0.82), int(w*0.5), 5)
            p.fillRect(int(w*0.25), int(h*0.82), int((w*0.5)*(self.phase % 30)/30), 5, color)
        if self.state == PetState.STEALTH:
            p.drawText(int(w*0.38), int(h*0.86), "shh")
        if self.state == PetState.FOCUSED:
            p.drawText(int(w*0.18), int(h*0.88), "DND")
        if self.state == PetState.READING:
            p.drawText(int(w*0.40), int(h*0.88), "▤")

    def contextMenuEvent(self, event) -> None:
        """Show companion context menu."""
        menu = QMenu(self)
        for action in ["Hide Pet", "Open Full Window", "Mute", "Stealth Mode", "Sloth Mode"]:
            menu.addAction(action)
        menu.exec(event.globalPos())

    def mouseDoubleClickEvent(self, event) -> None:
        """Emit a simple bubble on double-click; host app can wire full-window toggling."""
        self.show_bubble("Full window toggle.")
        event.accept()

    def mousePressEvent(self, event) -> None:
        """Start dragging pet."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        """Drag pet window."""
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        """End dragging."""
        self._drag_pos = None

    def _tick(self) -> None:
        """Advance animation frame and repaint."""
        self.phase = (self.phase + 1) % 360
        self.update()

    def _state_color(self) -> QColor:
        """Return glow color for the current state."""
        return {
            PetState.IDLE: QColor("#dffcff"),
            PetState.LISTENING: QColor("#00f0ff"),
            PetState.THINKING: QColor("#9b7cff"),
            PetState.WORKING: QColor("#ff9f1c"),
            PetState.HAPPY: QColor("#52ff8f"),
            PetState.ALERT: QColor("#ff3344"),
            PetState.SLEEPING: QColor("#253447"),
            PetState.STEALTH: QColor("#2f7f88"),
            PetState.FOCUSED: QColor("#ffcc00"),
            PetState.READING: QColor("#6be3ff"),
        }[self.state]
