"""How a file looks in the grid: a centred thumbnail, a two-line name, then its size or pages."""
from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QStyledItemDelegate, QStyleOptionViewItem

ICON = 128
TILE = QSize(ICON + 40, ICON + 80)  # Thumbnail above two name lines and a detail line.
BADGE_TILE = QSize(ICON + 60, ICON + 122)  # Wider for print sizes, plus a second detail line and a badge.
BADGE = Qt.ItemDataRole.UserRole + 1  # (text, grade) painted as a coloured dot and text.
COLORS = {'big': ('#2e7d32', '#7bc67e'), 'sharp': ('#2e7d32', '#7bc67e'),
          'soft': ('#b86e00', '#f2b24c'), 'blurry': ('#c62828', '#f28b82')}  # Light, dark.


def square(data=b''):
    """Centre a thumbnail on a sharp square so tiles line up; a soft placeholder without one."""
    ratio = QApplication.instance().devicePixelRatio()
    side = round(ICON * ratio)
    pixmap = QPixmap(side, side)
    image = QPixmap()
    loaded = bool(data) and image.loadFromData(data)
    pixmap.fill(Qt.GlobalColor.transparent if loaded else QColor(128, 128, 128, 40))
    if loaded:
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

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        badge = index.data(BADGE)
        if not badge:
            return
        text, grade = badge
        metrics = option.fontMetrics
        text = metrics.elidedText(text, Qt.TextElideMode.ElideRight, option.rect.width() - 36)
        left = option.rect.center().x() - (metrics.horizontalAdvance(text) + 14) // 2
        top = option.rect.bottom() - 8 - metrics.height()
        dark = option.palette.window().color().lightness() < 128
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(COLORS[grade][dark]))
        painter.drawEllipse(QRectF(left, top + (metrics.height() - 9) / 2, 9, 9))
        painter.setPen(option.palette.text().color())
        painter.drawText(left + 14, top + metrics.ascent(), text)
        painter.restore()
