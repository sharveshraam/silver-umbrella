"""Always-on-top orb widget."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QMenu, QLabel
from ui.animations import ArcReactorWidget
class MiniOrb(QWidget):
    """Draggable minimal glowing orb for minimized, stealth, and sleeping modes."""
    def __init__(self):
        super().__init__(); self.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.Tool); self.resize(96,96)
        self.orb=ArcReactorWidget(); self.orb.setParent(self); self.orb.setGeometry(0,0,96,96)
        self.badge=QLabel('', self); self.badge.setStyleSheet('color:#9ffcff;background:rgba(0,0,0,160);'); self.badge.move(8,72); self.badge.hide()
    def set_badge(self, text: str) -> None:
        """Show a small orb badge such as [STEALTH] or [SLEEPING]."""
        self.badge.setText(text); self.badge.adjustSize(); self.badge.setVisible(bool(text))
    def contextMenuEvent(self, event):
        """Show orb context menu."""; menu=QMenu(self); [menu.addAction(x) for x in ['Open','Mute/Unmute','Focus Mode','Stealth Mode','Sloth Mode','Exit']]; menu.exec(event.globalPos())
