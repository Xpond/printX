import json
from pathlib import Path
from PySide6.QtCore import QAbstractListModel, QByteArray, QMimeData, QModelIndex, QSize, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QAbstractItemView, QApplication, QListView, QSizePolicy
from ui import text as T
from ui.jobs import Thumbnails
from ui.tiles import ICON, TILE, Tiles, square


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


class FileList(QListView):
    files = Signal(list)
    browse = Signal()
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

    def mouseReleaseEvent(self, event):
        if not self.model().rowCount() and event.button() == Qt.MouseButton.LeftButton:
            self.browse.emit()  # The empty grid is the drop zone: drop files or click to choose.
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.model().rowCount():
            painter = QPainter(self.viewport())
            painter.setPen(self.palette().placeholderText().color())
            painter.drawText(self.viewport().rect(), Qt.AlignmentFlag.AlignCenter, T.EMPTY_DROP)
