"""QPainter HUD animations."""
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget

STATE_COLORS = {
    "idle": "#00f0ff",
    "listening": "#00ff88",
    "thinking": "#9b7cff",
    "working": "#ff9f1c",
    "muted": "#ff3344",
    "sleeping": "#1a2a3a",
    "stealth": "#2f7f88",
}

class ArcReactorWidget(QWidget):
    """Animated arc reactor ring for idle/listening/thinking states."""
    pulse=pyqtSignal()
    def __init__(self): super().__init__(); self.angle=0; self.mode='idle'; self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(33)
    def set_mode(self, mode: str):
        """Set visual mode and pause animation when sleeping."""
        self.mode=mode
        if mode == 'sleeping' and self.timer.isActive(): self.timer.stop()
        elif mode != 'sleeping' and not self.timer.isActive(): self.timer.start(33)
        self.update()
    def tick(self):
        """Advance animation frame."""
        speed = 6 if self.mode == 'listening' else 3
        if self.mode != 'sleeping': self.angle=(self.angle+speed)%360
        self.update()
    def paintEvent(self, _):
        """Paint glowing rings and state-aware arcs."""
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing); c=QColor(STATE_COLORS.get(self.mode, '#00f0ff')); p.setPen(QPen(c,4)); r=self.rect().adjusted(20,20,-20,-20); p.drawEllipse(r)
        if self.mode != 'sleeping':
            p.drawArc(r,self.angle*16,110*16)
            if self.mode in ('thinking','working'):
                p.setPen(QPen(c.lighter(130),2)); p.drawArc(r.adjusted(8,8,-8,-8),((-self.angle*2)%360)*16,60*16)
