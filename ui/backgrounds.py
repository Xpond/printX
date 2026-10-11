"""Remove background's results: a preview of each, and a solid colour to put behind the cut-outs."""
import math
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QConicalGradient, QPainter, QPixmap, QRadialGradient
from PySide6.QtWidgets import (QAbstractButton, QButtonGroup, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout,
                               QWidget)
from ui import text as T
from ui.widgets import button

SIDE = 300  # Smallest side of a preview; they grow to fill the height they get.


def checkers():
    """Grey and white squares, which mean transparent."""
    tile = QPixmap(12, 12)
    tile.fill(QColor('white'))
    painter = QPainter(tile)
    painter.fillRect(0, 0, 6, 6, QColor('#d6d6d6'))
    painter.fillRect(6, 6, 6, 6, QColor('#d6d6d6'))
    painter.end()
    return QBrush(tile)


def fill(painter, rect, color):
    """A round swatch: a colour, transparency (None), or the colour wheel ('wheel') with white in the middle."""
    if color != 'wheel':
        painter.setBrush(QColor(color) if color else checkers())
        return painter.drawEllipse(rect)
    hues = QConicalGradient(QPointF(rect.center()), 0)
    for step in range(7):
        hues.setColorAt(step / 6, QColor.fromHsvF(step / 6 % 1, 1, 1))
    white = QRadialGradient(QPointF(rect.center()), rect.width() / 2)
    white.setColorAt(0, QColor('white'))
    white.setColorAt(1, QColor(255, 255, 255, 0))
    for brush in (hues, white):
        painter.setBrush(QBrush(brush))
        painter.drawEllipse(rect)


class Swatch(QAbstractButton):
    def __init__(self, color, tip):
        super().__init__()
        self.color = color
        self.setCheckable(True)
        self.setToolTip(tip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(30, 30)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.palette().windowText().color() if self.isChecked() else Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect().adjusted(1, 1, -1, -1))
        painter.setPen(QColor(128, 128, 128, 140))
        fill(painter, self.rect().adjusted(5, 5, -5, -5), self.color)


class Wheel(QWidget):
    """Pops up under the wheel swatch: hue around the circle, paler towards the middle."""
    picked = Signal(str)

    def __init__(self, parent):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setFixedSize(160, 160)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self.palette().base())
        painter.setPen(Qt.PenStyle.NoPen)
        fill(painter, self.rect().adjusted(5, 5, -5, -5), 'wheel')

    def mousePressEvent(self, event):
        x, y = event.position().x() - 80, 80 - event.position().y()
        self.picked.emit(QColor.fromHsvF(math.atan2(y, x) / (2 * math.pi) % 1, min(math.hypot(x, y) / 75, 1), 1).name())

    mouseMoveEvent = mousePressEvent


class Backgrounds(QWidget):
    save = Signal(str, str)  # The colour, and its name for the file.

    def __init__(self):
        super().__init__()
        self.strip = QScrollArea()
        self.strip.setMinimumHeight(SIDE + 24 + self.strip.horizontalScrollBar().sizeHint().height())
        self.strip.setWidgetResizable(True)
        self.strip.setWidget(QWidget())
        self.cards = QHBoxLayout(self.strip.widget())
        self.cards.addStretch()
        self.row = QWidget()  # Only for cut-outs.
        row = QHBoxLayout(self.row)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(QLabel(T.BACKGROUND))
        self.group = QButtonGroup(self)
        self.swatches = [Swatch(color, tip) for color, tip, _ in T.BACKGROUNDS] + [Swatch('wheel', T.OTHER_COLOR)]
        for swatch in self.swatches:
            self.group.addButton(swatch)
            row.addWidget(swatch)
        self.swatches[0].setChecked(True)
        self.wheel = Wheel(self)
        self.wheel.picked.connect(self.pick)
        self.swatches[-1].clicked.connect(lambda: self.wheel.move(self.swatches[-1].mapToGlobal(
            self.swatches[-1].rect().bottomLeft())) or self.wheel.show())
        self.group.buttonClicked.connect(self.paint)
        row.addStretch()
        self.save_button = button(T.SAVE_BACKGROUND, self.request_save, primary=True)
        row.addWidget(self.save_button)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.strip)
        layout.addWidget(self.row)
        self.pictures = {}  # Path: (label, picture or None)
        self.paint()

    def color(self):
        return self.group.checkedButton().color

    def pick(self, color):
        self.swatches[-1].color = color  # The wheel swatch now shows, and saves, the picked colour.
        self.swatches[-1].setChecked(True)
        self.paint()

    def add(self, path):
        image = QLabel(T.READING)
        image.setToolTip(path)
        self.pictures[path] = image, None
        self.cards.insertWidget(self.cards.count() - 1, image)

    def fill(self, path, result):
        """A result's preview arrived: the thumbnail process's (data, kind, pixel size)."""
        picture = QPixmap()
        if path in self.pictures and picture.loadFromData(result[0]):
            self.pictures[path] = self.pictures[path][0], picture
            self.paint()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.paint()

    def paint(self):
        color = self.color() if self.row.isVisibleTo(self) else '#ffffff'
        self.save_button.setEnabled(color not in (None, 'wheel'))
        side = max(SIDE, self.strip.viewport().height() - 24)
        for image, picture in self.pictures.values():
            if picture:
                picture = picture.scaled(side, side, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
                shown = QPixmap(picture.size())
                painter = QPainter(shown)
                painter.fillRect(shown.rect(), QColor(color) if color not in (None, 'wheel') else checkers())
                painter.drawPixmap(0, 0, picture)
                painter.setPen(QColor(128, 128, 128, 110))  # An edge, so white still shows on white.
                painter.drawRect(shown.rect().adjusted(0, 0, -1, -1))
                painter.end()
                image.setPixmap(shown)

    def request_save(self):
        color = self.color()
        self.save.emit(color, {color: name for color, _, name in T.BACKGROUNDS}.get(color, color[1:]))

    def clear(self):
        for image, _ in self.pictures.values():
            image.deleteLater()
        self.pictures = {}
