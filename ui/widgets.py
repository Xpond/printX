from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton


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
