"""Round colour swatches and a small colour wheel for picking any other colour."""
import math
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QConicalGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QAbstractButton, QFrame, QSlider, QVBoxLayout, QWidget

CHECKER = 6  # Squares of the transparency pattern, in pixels.


def checker(painter, rect):
    """The grey and white squares that mean transparent."""
    painter.fillRect(rect, QColor('#ffffff'))
    for y in range(rect.top(), rect.bottom() + 1, CHECKER):
        for x in range(rect.left() + ((y - rect.top()) // CHECKER % 2) * CHECKER, rect.right() + 1, 2 * CHECKER):
            painter.fillRect(x, y, CHECKER, CHECKER, QColor('#d6d6d6'))


def rainbow(center):
    gradient = QConicalGradient(center, 0)
    for step in range(7):
        gradient.setColorAt(step / 6, QColor.fromHsvF(step / 6 % 1, 1, 1))
    return gradient


class Swatch(QAbstractButton):
    """A round, checkable colour: a colour, None for transparent, or 'wheel' for the picker."""
    def __init__(self, color, tip):
        super().__init__()
        self.color = color
        self.custom = None  # The wheel shows the colour picked with it.
        self.setCheckable(True)
        self.setToolTip(tip)
        self.setAccessibleName(tip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(30, 30)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ink = self.palette().windowText().color()
        if self.isChecked() or self.hasFocus():
            painter.setPen(QPen(ink, 2))
            painter.drawEllipse(self.rect().adjusted(1, 1, -1, -1))
        inner = self.rect().adjusted(5, 5, -5, -5)
        painter.setPen(QPen(QColor(128, 128, 128, 140), 1))
        if self.color == 'wheel':
            painter.setBrush(QBrush(rainbow(QPointF(inner.center()))))
            painter.drawEllipse(inner)
            if self.custom:
                painter.setBrush(QColor(self.custom))
                painter.drawEllipse(inner.adjusted(5, 5, -5, -5))
        elif self.color:
            painter.setBrush(QColor(self.color))
            painter.drawEllipse(inner)
        else:
            painter.save()
            round_part = QPainterPath()
            round_part.addEllipse(QRectF(inner))
            painter.setClipPath(round_part)
            checker(painter, inner)
            painter.restore()
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(inner)


class Wheel(QWidget):
    """Hue around the circle, white in the middle; a slider below sets how dark."""
    picked = Signal(str)

    def __init__(self, side=150):
        super().__init__()
        self.setFixedSize(side, side)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.hue, self.saturation, self.value = 0.0, 0.0, 1.0

    def color(self):
        return QColor.fromHsvF(self.hue, self.saturation, self.value)

    def set_color(self, color):
        color = QColor(color)
        self.hue, self.saturation, self.value = max(color.hsvHueF(), 0), color.hsvSaturationF(), color.valueF()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        circle = self.rect().adjusted(2, 2, -2, -2)
        center = QPointF(circle.center())
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(rainbow(center)))
        painter.drawEllipse(circle)
        white = QRadialGradient(center, circle.width() / 2)
        white.setColorAt(0, QColor(255, 255, 255))
        white.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(white))
        painter.drawEllipse(circle)
        painter.setBrush(QColor(0, 0, 0, round(255 * (1 - self.value))))
        painter.drawEllipse(circle)
        radius = circle.width() / 2 * self.saturation
        angle = self.hue * 2 * math.pi
        dot = QPointF(center.x() + radius * math.cos(angle), center.y() - radius * math.sin(angle))
        painter.setBrush(self.color())
        painter.setPen(QPen(QColor('white'), 2))
        painter.drawEllipse(dot, 6, 6)
        painter.setPen(QPen(QColor('black'), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(dot, 7, 7)

    def pick(self, position):
        center, radius = QPointF(self.rect().center()), self.width() / 2 - 2
        dx, dy = position.x() - center.x(), center.y() - position.y()
        self.hue = math.atan2(dy, dx) / (2 * math.pi) % 1
        self.saturation = min(math.hypot(dx, dy) / radius, 1)
        self.update()
        self.picked.emit(self.color().name())

    def mousePressEvent(self, event):
        self.pick(event.position())

    def mouseMoveEvent(self, event):
        self.pick(event.position())


class WheelPopup(QFrame):
    """Opens under the wheel swatch; every move shows at once, a click outside closes it."""
    picked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setObjectName('popup')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.wheel = Wheel()
        self.wheel.picked.connect(self.picked)
        self.dark = QSlider(Qt.Orientation.Horizontal)
        self.dark.setRange(0, 100)
        self.dark.setValue(100)
        self.dark.valueChanged.connect(self.set_value)
        layout.addWidget(self.wheel)
        layout.addWidget(self.dark)

    def set_value(self, value):
        self.wheel.value = value / 100
        self.wheel.update()
        self.picked.emit(self.wheel.color().name())

    def open(self, color, below):
        self.wheel.set_color(color)
        self.dark.blockSignals(True)
        self.dark.setValue(round(self.wheel.value * 100))
        self.dark.blockSignals(False)
        self.move(below.mapToGlobal(below.rect().bottomLeft()))
        self.show()
