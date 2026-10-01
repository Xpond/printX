"""The Enhance image conversation: the photo, each instruction, and every version the AI made."""
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget
from ui import text as T
from ui.widgets import label

SIDE = 256  # Largest side of a picture in the conversation.


class Chat(QScrollArea):
    files = Signal(list)
    browse = Signal()
    picked = Signal(str)

    def __init__(self, empty):
        super().__init__()
        self.setObjectName('chat')
        self.setWidgetResizable(True)
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        self.setMinimumHeight(SIDE + 60)
        body = QWidget()
        body.setObjectName('chatbody')
        self.lines = QVBoxLayout(body)
        self.lines.setContentsMargins(12, 12, 12, 12)
        self.lines.setSpacing(10)
        self.empty = label(empty, muted=True)  # Until a photo is chosen, the whole area invites one.
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty.setCursor(Qt.CursorShape.PointingHandCursor)
        self.empty.mouseReleaseEvent = lambda event: self.browse.emit()
        self.lines.addWidget(self.empty, 1)
        self.lines.addStretch()
        self.setWidget(body)
        self.rows, self.pictures = [], {}  # Pictures by path: (image, caption).
        bar = self.verticalScrollBar()
        bar.rangeChanged.connect(lambda low, high: bar.setValue(high))  # Keep the newest message in view.

    def add(self, widget, mine=False):
        """Your instructions on the right; the photo, its versions and any problems on the left."""
        row = QWidget()
        line = QHBoxLayout(row)
        line.setContentsMargins(0, 0, 0, 0)
        if mine:  # Stretch, not alignment, so wrapped text gets its full height.
            line.addStretch()
        line.addWidget(widget)
        if not mine:
            line.addStretch()
        self.empty.hide()
        self.rows.append(row)
        self.lines.insertWidget(self.lines.count() - 1, row)

    def say(self, text, mine=False):
        message = label(text, 'mine' if mine else None, muted=not mine)
        message.setWordWrap(False)
        message.ensurePolished()  # Its one-line width, bubble padding included.
        message.setFixedWidth(min(message.sizeHint().width(), 520))
        message.setWordWrap(True)
        self.add(message, mine)

    def picture(self, path):
        """A version of the photo, filled in once its preview is ready; click it to change that one next."""
        box = QWidget()
        column = QVBoxLayout(box)
        column.setContentsMargins(0, 0, 0, 0)
        image = QLabel(T.READING)
        image.setObjectName('version')
        image.setFixedSize(SIDE + 4, SIDE + 4)  # Room for the highlight around the current version.
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.setToolTip(T.PICK_TIP)
        image.setCursor(Qt.CursorShape.PointingHandCursor)
        image.mouseReleaseEvent = lambda event: self.picked.emit(path)
        caption = label(Path(path).name, muted=True)
        caption.setFixedWidth(SIDE + 4)
        column.addWidget(image)
        column.addWidget(caption)
        self.pictures[path] = image, caption
        self.add(box)

    def fill(self, path, result):
        """Show a version's preview: the thumbnail process's (data, kind, pixel size)."""
        if path not in self.pictures:
            return
        (data, _, size), (image, caption) = result, self.pictures[path]
        pixmap, ratio = QPixmap(), self.devicePixelRatioF()
        if not pixmap.loadFromData(data):
            image.setText(T.THUMB['unreadable'])
            return
        pixmap = pixmap.scaled(round(SIDE * ratio), round(SIDE * ratio), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        pixmap.setDevicePixelRatio(ratio)
        image.setPixmap(pixmap)
        caption.setText(f'{Path(path).name}\n{T.PIXELS.format(width=size[0], height=size[1])}')

    def select(self, path):
        for key, (image, _) in self.pictures.items():
            image.setProperty('current', key == path)
            image.style().unpolish(image)  # Restyle for the new property.
            image.style().polish(image)

    def clear(self):
        for row in self.rows:
            row.hide()
            row.deleteLater()
        self.rows, self.pictures = [], {}
        self.empty.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.files.emit([url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()])
        event.acceptProposedAction()
