"""Always-on-top orb widget."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QMenu
from ui.animations import ArcReactorWidget
class MiniOrb(QWidget):
    """Draggable minimal glowing orb for minimized mode."""
    def __init__(self): super().__init__(); self.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.Tool); self.resize(96,96); self.orb=ArcReactorWidget(); self.orb.setParent(self); self.orb.setGeometry(0,0,96,96)
    def contextMenuEvent(self, event):
        """Show orb context menu."""; menu=QMenu(self); [menu.addAction(x) for x in ['Open','Mute/Unmute','Focus Mode','Exit']]; menu.exec(event.globalPos())
