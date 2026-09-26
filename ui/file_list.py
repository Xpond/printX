import json
from pathlib import Path
from PySide6.QtCore import QAbstractListModel, QByteArray, QMimeData, QModelIndex, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QListView, QSizePolicy,
                               QStyledItemDelegate, QStyleOptionViewItem)
from ui import text as T
from ui.jobs import Thumbnails


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


class FileModel(QAbstractListModel):
    changed = Signal()
    mime = 'application/x-printshop-file-rows'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paths = []
        self.cache = {}
        self.blank = square()
        self.thumbnails = Thumbnails(self)
        self.thumbnails.ready.connect(self.thumbnail_ready)

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.paths)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        path = self.paths[index.row()]
        if role == Qt.ItemDataRole.SizeHintRole:
            return TILE
        if role == Qt.ItemDataRole.ToolTipRole:
            return path
        if role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.DecorationRole):
            return None
        if path not in self.cache:
            self.thumbnails.request(path)
        pixmap, detail = self.cache.get(path, (self.blank, T.READING))
        if role == Qt.ItemDataRole.DecorationRole:
            return pixmap
        return f'{Path(path).name}\n{detail}'

    def thumbnail_ready(self, path, result):
        data, kind, value = result
        if kind == 'pages':
            detail = T.PAGES.format(count=value)
        elif kind == 'pixels':
            detail = T.PIXELS.format(width=value[0], height=value[1])
        else:
            detail = T.THUMB[kind]
        self.cache[path] = (square(data), detail)
        if path in self.paths:
            index = self.index(self.paths.index(path))
            self.dataChanged.emit(index, index)

    def replace(self, paths):
        self.beginResetModel()
        self.paths = paths
        self.endResetModel()
        self.changed.emit()

    def add(self, paths):
        self.replace(list(dict.fromkeys(self.paths + [str(Path(p).absolute()) for p in paths])))

    def remove(self, rows):
        self.replace([p for i, p in enumerate(self.paths) if i not in rows])

    def sort(self, column=0, order=Qt.SortOrder.AscendingOrder):
        self.replace(sorted(self.paths, key=lambda p: Path(p).name.casefold()))

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.ItemIsDropEnabled
        return (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def mimeTypes(self):
        return [self.mime]

    def mimeData(self, indexes):
        data = QMimeData()
        data.setData(self.mime, QByteArray(json.dumps(sorted({i.row() for i in indexes})).encode()))
        return data

    def dropMimeData(self, data, action, row, column, parent):
        if action == Qt.DropAction.IgnoreAction:
            return True
        if not data.hasFormat(self.mime):
            return False
        rows = json.loads(bytes(data.data(self.mime)))
        if row < 0:
            row = parent.row() if parent.isValid() else len(self.paths)
        moving = [self.paths[i] for i in rows]
        rest = [p for i, p in enumerate(self.paths) if i not in rows]
        offset = row - sum(i < row for i in rows)
        self.replace(rest[:offset] + moving + rest[offset:])
        return True


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


class FileList(QListView):
    files = Signal(list)
    remove_requested = Signal()

    def __init__(self, model):
        super().__init__()
        self.setFont(QApplication.font())
        self.setObjectName('files')
        self.setModel(model)
        self.setItemDelegate(Tiles(self))
        # A wrapping left-to-right list, not icon mode, so dragging still reorders the model.
        self.setFlow(QListView.Flow.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setSpacing(4)
        self.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.setUniformItemSizes(True)
        self.setIconSize(QSize(ICON, ICON))
        self.setMinimumHeight(TILE.height() + 12)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDropIndicatorShown(True)
        self.setAccessibleName(T.FILE_COUNT.format(count=0))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace) and self.selectionModel().hasSelection():
            self.remove_requested.emit()
        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            self.files.emit([u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()])
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
