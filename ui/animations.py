"""QPainter HUD animations."""
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget
class ArcReactorWidget(QWidget):
    """Animated arc reactor ring for idle/listening/thinking states."""
    pulse=pyqtSignal()
    def __init__(self): super().__init__(); self.angle=0; self.mode='idle'; self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(33)
    def set_mode(self, mode: str): """Set visual mode."""; self.mode=mode; self.update()
    def tick(self): """Advance animation frame."""; self.angle=(self.angle+3)%360; self.update()
    def paintEvent(self, _):
        """Paint glowing rings and arcs."""; p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing); c=QColor('#00f0ff' if self.mode!='muted' else '#ff3344'); p.setPen(QPen(c,4)); r=self.rect().adjusted(20,20,-20,-20); p.drawEllipse(r); p.drawArc(r,self.angle*16,110*16)
