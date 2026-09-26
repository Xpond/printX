from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget
from ui import text as T
from ui.widgets import button, label


class Home(QWidget):
    selected = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(label(T.HOME_TITLE, 'title'))
        layout.addWidget(label(T.HOME_DESCRIPTION, muted=True))
        grid = QGridLayout()
        grid.setSpacing(14)
        for row in range(4):
            grid.setRowStretch(row, 1)
        icons = ['↗', '⊕', '↓', '✂', '↻', '▧', '◇']
        for i, (key, title, description, category) in enumerate(T.TOOLS):
            tile = QFrame()
            tile.setObjectName('tile')
            tile.setProperty('active', key == 'make')
            if key == 'make':
                tile.mouseReleaseEvent = lambda event: self.selected.emit('make')
            box = QVBoxLayout(tile)
            box.setContentsMargins(18, 12, 18, 12)
            row = QHBoxLayout()
            icon = label(icons[i])
            icon.setProperty('accent', category)
            icon.setFixedWidth(28)
            row.addWidget(icon)
            pick = button(title, lambda checked=False, value=key: self.selected.emit(value))
            pick.setEnabled(key == 'make')
            if key != 'make':
                pick.setToolTip(T.LATER)
            row.addWidget(pick, 1)
            box.addLayout(row)
            box.addWidget(label(description, muted=True))
            if key != 'make':
                box.addWidget(label(T.LATER, muted=True))
            else:
                box.addStretch()
            grid.addWidget(tile, i // 2, i % 2)
        layout.addLayout(grid, 1)
        layout.addWidget(label(T.OFFLINE, muted=True))
