"""Remove background's results: a preview of each, and a solid background to put behind the cut-outs."""
from pathlib import Path
from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (QButtonGroup, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout,
                               QWidget)
from ui import text as T
from ui.colors import Swatch, WheelPopup, checker
from ui.widgets import button, label

SIDE = 480  # Largest side of a preview; they grow with the window up to this.
SMALLEST = 160


class Previews(QWidget):
    save = Signal(str, str)  # The colour, and its name for the file.

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.strip = QScrollArea()
        self.strip.setObjectName('chat')
        self.strip.setWidgetResizable(True)
        self.strip.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.strip.setMinimumHeight(SMALLEST + 64 + self.strip.horizontalScrollBar().sizeHint().height())
        self.side = SMALLEST
        body = QWidget()
        body.setObjectName('chatbody')
        self.cards = QHBoxLayout(body)
        self.cards.setContentsMargins(12, 12, 12, 12)
        self.cards.setSpacing(12)
        self.cards.addStretch()
        self.strip.setWidget(body)
        layout.addWidget(self.strip)
        self.row = QWidget()  # Only for cut-outs: something else removed has no background to change.
        row = QHBoxLayout(self.row)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(QLabel(T.BACKGROUND))
        self.group = QButtonGroup(self)
        self.swatches = [Swatch(color, tip) for color, tip, _ in T.BACKGROUNDS] + [Swatch('wheel', T.OTHER_COLOR)]
        for swatch in self.swatches:
            self.group.addButton(swatch)
            row.addWidget(swatch)
        self.wheel = self.swatches[-1]
        self.wheel.custom = settings.value('remove/custom', '') or None
        self.wheel.clicked.connect(self.open_wheel)
        self.popup = WheelPopup(self)
        self.popup.picked.connect(self.pick_custom)
        self.group.buttonClicked.connect(self.repaint_all)
        self.note = label('', muted=True)
        row.addSpacing(8)
        row.addWidget(self.note, 1)
        self.save_button = button(T.SAVE_BACKGROUND, self.request_save, primary=True)
        row.addWidget(self.save_button)
        layout.addWidget(self.row)
        chosen = settings.value('remove/background', '')
        known = [swatch for swatch in self.swatches[:-1] if (swatch.color or '') == chosen]
        (known[0] if known else self.wheel if self.wheel.custom == chosen else self.swatches[0]).setChecked(True)
        self.pictures = {}  # Path: (label, caption, picture or None)
        self.repaint_all()

    def color(self):
        swatch = self.group.checkedButton()
        return swatch.custom if swatch is self.wheel else swatch.color

    def open_wheel(self):
        self.popup.open(self.wheel.custom or T.BACKGROUNDS[1][0], self.wheel)
        if not self.wheel.custom:
            self.pick_custom(T.BACKGROUNDS[1][0])

    def pick_custom(self, color):
        self.wheel.custom = color
        self.wheel.setChecked(True)
        self.settings.setValue('remove/custom', color)
        self.repaint_all()

    def repaint_all(self):
        color = self.color()
        self.settings.setValue('remove/background', color or '')
        self.wheel.update()
        self.save_button.setEnabled(bool(color) and bool(self.pictures))
        self.note.setText(T.TRANSPARENT_NOTE if not color else T.BACKGROUND_NOTE)
        for path in self.pictures:
            self.render(path)

    def add(self, path):
        card = QWidget()
        column = QVBoxLayout(card)
        column.setContentsMargins(0, 0, 0, 0)
        image = QLabel(T.READING)
        image.setFixedSize(self.side, self.side)
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.setToolTip(path)
        caption = label('', muted=True)
        caption.setWordWrap(False)
        column.addStretch()  # Pictures stand on one line, names under them.
        column.addWidget(image)
        column.addWidget(caption)
        self.pictures[path] = image, caption, None
        self.cards.insertWidget(self.cards.count() - 1, card)
        self.repaint_all()

    def resizeEvent(self, event):
        """The previews fill the height they are given."""
        super().resizeEvent(event)
        side = max(SMALLEST, min(SIDE, self.strip.viewport().height() - 60))
        if side != self.side:
            self.side = side
            for path in self.pictures:
                self.render(path)

    def fill(self, path, result):
        """A result's preview arrived: the thumbnail process's (data, kind, pixel size)."""
        if path not in self.pictures:
            return
        image, caption, _ = self.pictures[path]
        picture = QPixmap()
        if not picture.loadFromData(result[0]):
            image.setText(T.THUMB['unreadable'])
            return
        self.pictures[path] = image, caption, picture
        self.render(path)

    def render(self, path):
        image, caption, picture = self.pictures[path]
        if picture is None:
            image.setFixedSize(self.side, self.side)
            return
        ratio = self.devicePixelRatioF()
        picture = picture.scaled(round(self.side * ratio), round(self.side * ratio), Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
        shown = QPixmap(picture.size())
        painter = QPainter(shown)
        color = self.color() if self.row.isVisibleTo(self) else '#ffffff'
        if color:
            painter.fillRect(shown.rect(), QColor(color))
        else:
            checker(painter, QRect(0, 0, shown.width(), shown.height()))
        painter.drawPixmap(0, 0, picture)
        painter.setPen(QColor(128, 128, 128, 110))  # An edge, so a white background still shows on white.
        painter.drawRect(shown.rect().adjusted(0, 0, -1, -1))
        painter.end()
        shown.setDevicePixelRatio(ratio)
        image.setPixmap(shown)
        width = round(shown.width() / ratio)
        image.setFixedSize(width, round(shown.height() / ratio))  # Cards as wide as their picture.
        caption.setFixedWidth(width)
        caption.setText(caption.fontMetrics().elidedText(Path(path).name, Qt.TextElideMode.ElideMiddle, width))

    def show_backgrounds(self, visible):
        self.row.setVisible(visible)
        for path in self.pictures:
            self.render(path)

    def request_save(self):
        color = self.color()
        names = {swatch_color: name for swatch_color, _, name in T.BACKGROUNDS}
        self.save.emit(color, names.get(color, color.lstrip('#')))

    def clear(self):
        while self.cards.count() > 1:
            card = self.cards.takeAt(0).widget()
            card.hide()
            card.deleteLater()
        self.pictures = {}
        self.repaint_all()
