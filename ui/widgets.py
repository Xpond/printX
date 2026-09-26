from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget
from ui import text as T


def label(value, style=None, muted=False):
    result = QLabel(value)
    result.setWordWrap(True)
    if style:
        result.setObjectName(style)
    if muted:
        result.setProperty('muted', True)
    return result


def button(value, callback=None, primary=False):
    result = QPushButton(value)
    result.setCursor(Qt.CursorShape.PointingHandCursor)
    if primary:
        result.setObjectName('primary')
    if callback:
        result.clicked.connect(callback)
    return result


class DropZone(QWidget):
    browse = Signal()
    files = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(126)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(T.DROP + ' ' + T.DROP_HINT)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        self.lines = []
        for value, muted in [(T.DROP, False), (T.DROP_HINT, True), (T.FORMATS, True)]:
            item = label(value, muted=muted)
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(item)
            self.lines.append(item)

    def set_compact(self, compact):
        """Shrink to one line once files are listed, leaving room for the list."""
        self.setMinimumHeight(56 if compact else 126)
        self.lines[0].setText(T.DROP_MORE if compact else T.DROP)
        for item in self.lines[1:]:
            item.setVisible(not compact)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.browse.emit()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return):
            self.browse.emit()
        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.files.emit([url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()])
        event.acceptProposedAction()

    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor('#d74283' if self.palette().window().color().lightness() > 128 else '#f36fa5')
        painter.setPen(QPen(color, 3))
        w, h, inset = self.width(), self.height(), 3
        arm = min(24, h // 3)
        for x, dx in [(inset, 1), (w - inset, -1)]:
            for y, dy in [(inset, 1), (h - inset, -1)]:
                painter.drawLine(x, y, x + dx * arm, y)
                painter.drawLine(x, y, x, y + dy * arm)
