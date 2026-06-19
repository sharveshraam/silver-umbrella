"""Always-on-top orb widget."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QMenu, QLabel
from ui.animations import ArcReactorWidget
class MiniOrb(QWidget):
    """Draggable minimal glowing orb for minimized, stealth, and sleeping modes."""
    def __init__(self):
        super().__init__(); self.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.Tool); self.resize(96,96)
        self.open_requested = None; self.mute_requested = None; self.stealth_requested = None; self.sloth_requested = None
        self.orb=ArcReactorWidget(); self.orb.setParent(self); self.orb.setGeometry(0,0,96,96)
        self.badge=QLabel('', self); self.badge.setStyleSheet('color:#9ffcff;background:rgba(0,0,0,160);'); self.badge.move(8,72); self.badge.hide()
    def set_badge(self, text: str) -> None:
        """Show a small orb badge such as [STEALTH] or [SLEEPING]."""
        self.badge.setText(text); self.badge.adjustSize(); self.badge.setVisible(bool(text))
    def contextMenuEvent(self, event):
        """Show orb context menu and invoke configured callbacks."""
        menu = QMenu(self)
        open_action = menu.addAction("Open")
        mute_action = menu.addAction("Mute/Unmute")
        stealth_action = menu.addAction("Stealth Mode")
        sloth_action = menu.addAction("Sloth Mode")
        exit_action = menu.addAction("Exit")
        chosen = menu.exec(event.globalPos())
        if chosen == open_action and callable(getattr(self, "open_requested", None)):
            self.open_requested()
        elif chosen == mute_action and callable(getattr(self, "mute_requested", None)):
            self.mute_requested()
        elif chosen == stealth_action and callable(getattr(self, "stealth_requested", None)):
            self.stealth_requested()
        elif chosen == sloth_action and callable(getattr(self, "sloth_requested", None)):
            self.sloth_requested()
        elif chosen == exit_action:
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()
