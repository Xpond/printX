import json
from pathlib import Path
from PySide6.QtCore import QAbstractListModel, QByteArray, QMimeData, QModelIndex, QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QAbstractItemView, QApplication, QListView, QSizePolicy
from ui import text as T
from ui.jobs import Thumbnails


class FileModel(QAbstractListModel):
    changed = Signal()
    mime = 'application/x-printshop-file-rows'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paths = []
        self.cache = {}
        self.thumbnails = Thumbnails(self)
        self.thumbnails.ready.connect(self.thumbnail_ready)

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.paths)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        path = self.paths[index.row()]
        if role == Qt.ItemDataRole.SizeHintRole:
            return QSize(100, 76)
        if role == Qt.ItemDataRole.ToolTipRole:
            return path
        if role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.DecorationRole):
            return None
        if path not in self.cache:
            self.thumbnails.request(path)
        pixmap, detail = self.cache.get(path, (None, T.READING))
        if role == Qt.ItemDataRole.DecorationRole:
            return pixmap
        return f'{Path(path).name}\n{detail}'

    def thumbnail_ready(self, path, result):
        data, kind, value = result
        pixmap = QPixmap()
        if data:
            pixmap.loadFromData(data)
            pixmap = pixmap.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        if kind == 'pages':
            detail = T.PAGES.format(count=value)
        elif kind == 'pixels':
            detail = T.PIXELS.format(width=value[0], height=value[1])
        else:
            detail = T.THUMB[kind]
        self.cache[path] = (pixmap, detail)
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

    def __init__(self, model):
        super().__init__()
        self.setFont(QApplication.font())
        self.setModel(model)
        self.setUniformItemSizes(True)
        self.setIconSize(QSize(56, 56))
        self.setMinimumHeight(92)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDropIndicatorShown(True)
        self.setAccessibleName(T.FILE_COUNT.format(count=0))

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
