from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QWidget


class ToolIcon(QWidget):
    """Small print-tool diagrams, independent of installed symbol fonts."""
    def __init__(self, tool, category):
        super().__init__()
        self.tool, self.category = tool, category
        self.setFixedSize(30, 30)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        dark = self.palette().window().color().lightness() < 128
        color = {'image': ('#007b91', '#69d5e8'), 'pdf': ('#ac1557', '#f36fa5'), 'ai': ('#8a6500', '#ffd84d')}[
            self.category][dark]
        painter.setPen(QPen(QColor(color), 1.8))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.translate(3, 3)
        if self.tool == 'upscale':
            painter.drawRect(2, 12, 10, 10)
            painter.drawLine(10, 14, 22, 2)
            painter.drawLine(14, 2, 22, 2)
            painter.drawLine(22, 2, 22, 10)
        elif self.tool == 'make':
            painter.drawRect(2, 2, 14, 18)
            painter.drawLine(6, 6, 12, 6)
            painter.drawLine(6, 10, 12, 10)
            painter.drawLine(20, 14, 20, 24)
            painter.drawLine(15, 19, 25, 19)
        elif self.tool == 'compress':
            painter.drawRect(5, 8, 14, 8)
            for y, sign in [(1, 1), (23, -1)]:
                painter.drawLine(12, y, 12, y + sign * 5)
                painter.drawLine(9, y + sign * 2, 12, y + sign * 5)
                painter.drawLine(15, y + sign * 2, 12, y + sign * 5)
        elif self.tool == 'split':
            painter.drawRect(4, 2, 16, 7)
            painter.drawRect(4, 15, 16, 7)
            painter.setPen(QPen(QColor(color), 1.4, Qt.PenStyle.DashLine))
            painter.drawLine(0, 12, 24, 12)
        elif self.tool == 'organize':
            for x, y in [(1, 2), (14, 2), (1, 15), (14, 15)]:
                painter.drawRect(x, y, 8, 8)
        elif self.tool == 'render':
            painter.drawRect(1, 3, 22, 18)
            painter.drawEllipse(QRectF(15, 6, 4, 4))
            painter.drawPolyline(QPolygonF([QPointF(2, 20), QPointF(9, 10), QPointF(15, 17), QPointF(19, 13), QPointF(23, 20)]))
        elif self.tool == 'remove':
            painter.setPen(QPen(QColor(color), 1.4, Qt.PenStyle.DashLine))
            painter.drawRect(1, 5, 15, 17)
            painter.setPen(QPen(QColor(color), 1.8))
            painter.drawEllipse(QRectF(10, 9, 7, 7))
            painter.drawArc(QRectF(6, 17, 15, 12), 0, 180 * 16)
            sparkle(painter, 20, 4, 4)
        else:
            sparkle(painter, 10, 14, 9)
            sparkle(painter, 20, 4, 4)


def sparkle(painter, x, y, radius):
    """A four-point star, the common mark for AI."""
    tips = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, -1)]
    path = QPainterPath(QPointF(x, y - radius))
    for (ax, ay), (bx, by) in zip(tips, tips[1:]):  # Sides curve in towards the centre.
        path.quadTo(x + (ax + bx) * radius / 5, y + (ay + by) * radius / 5, x + bx * radius, y + by * radius)
    painter.drawPath(path)
