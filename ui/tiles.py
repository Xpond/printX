"""How a file looks in the grid: a centred thumbnail, a two-line name, then its size or pages."""
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QStyledItemDelegate, QStyleOptionViewItem

ICON = 128
TILE = QSize(ICON + 40, ICON + 80)  # Thumbnail above two name lines and a detail line.


def square(data=b''):
    """Centre a thumbnail on a sharp square so tiles line up; a soft placeholder without one."""
    ratio = QApplication.instance().devicePixelRatio()
    side = round(ICON * ratio)
    pixmap = QPixmap(side, side)
    pixmap.fill(QColor(128, 128, 128, 40))
    image = QPixmap()
    if data and image.loadFromData(data):
        pixmap.fill(Qt.GlobalColor.transparent)
        image = image.scaled(side, side, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        x, y = (side - image.width()) // 2, (side - image.height()) // 2
        painter = QPainter(pixmap)
        painter.drawPixmap(x, y, image)
        painter.setPen(QColor(128, 128, 128, 110))
        painter.drawRect(x, y, image.width() - 1, image.height() - 1)  # Keeps white pages visible.
        painter.end()
    pixmap.setDevicePixelRatio(ratio)
    return pixmap


def two_lines(text, metrics, width):
    """A file name on up to two lines; the second elides its middle, like File Explorer."""
    if metrics.horizontalAdvance(text) <= width:
        return [text]
    first = metrics.elidedText(text, Qt.TextElideMode.ElideRight, width).removesuffix('\u2026')
    cut = max(first.rfind(mark) for mark in ' -_.') + 1  # Prefer breaking after a separator.
    first = first[:cut] if cut > len(first) // 2 else first
    return [first, metrics.elidedText(text[len(first):], Qt.TextElideMode.ElideMiddle, width)]


class Tiles(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.decorationPosition = QStyleOptionViewItem.Position.Top
        option.displayAlignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        name, _, detail = option.text.partition('\u2028')  # Views show '\n' as a line separator.
        option.text = '\u2028'.join(two_lines(name, option.fontMetrics, option.rect.width() - 24) + [detail])
