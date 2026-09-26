from PySide6.QtWidgets import (QComboBox, QFileDialog, QHBoxLayout, QProgressBar,
                               QTextEdit, QVBoxLayout, QWidget)
from ui import text as T
from ui.file_list import FileList, FileModel
from ui.widgets import DropZone, button, label


class ToolScreen(QWidget):
    def __init__(self, title, description):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.layout.addWidget(label(title, 'title'))
        self.layout.addWidget(label(description, muted=True))
        self.inputs = QWidget()
        inputs = QVBoxLayout(self.inputs)
        inputs.setContentsMargins(0, 0, 0, 0)
        inputs.setSpacing(10)
        self.drop = DropZone()
        self.drop.browse.connect(self.browse)
        self.drop.files.connect(self.add_files)
        inputs.addWidget(self.drop)
        toolbar = QHBoxLayout()
        self.count = label(T.EMPTY_LIST, muted=True)
        toolbar.addWidget(self.count, 1)
        toolbar.addWidget(button(T.ADD, self.browse))
        self.model = FileModel(self)
        self.list = FileList(self.model)
        self.list.files.connect(self.add_files)
        self.list.remove_requested.connect(self.remove)
        toolbar.addWidget(button(T.SORT, self.model.sort))
        self.select_all = button(T.SELECT_ALL, self.list.selectAll)
        self.remove_button = button(T.REMOVE, self.remove)
        for widget in (self.select_all, self.remove_button):
            widget.setToolTip(T.REMOVE_TIP)
            toolbar.addWidget(widget)
        self.list.selectionModel().selectionChanged.connect(self.update_selection)
        self.model.changed.connect(self.update_selection)
        inputs.addLayout(toolbar)
        inputs.addWidget(self.list, 1)
        self.options_layout = QVBoxLayout()
        inputs.addLayout(self.options_layout)
        self.layout.addWidget(self.inputs, 1)
        self.output_hint = label(T.SAVED_NEXT, muted=True)
        self.layout.addWidget(self.output_hint)
        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        self.messages.setMaximumHeight(85)
        self.messages.hide()
        self.layout.addWidget(self.messages)
        self.status = label('')
        self.layout.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.hide()
        self.layout.addWidget(self.progress)
        controls = QHBoxLayout()
        self.run = button(T.RUN_EMPTY, primary=True)
        self.cancel = button(T.CANCEL)
        self.cancel.hide()
        controls.addWidget(self.run, 1)
        controls.addWidget(self.cancel)
        self.layout.addLayout(controls)
        self.results = QWidget()
        result_layout = QHBoxLayout(self.results)
        result_layout.setContentsMargins(0, 0, 0, 0)
        self.outputs = QComboBox()
        result_layout.addWidget(self.outputs, 1)
        self.open_button = button(T.OPEN)
        self.show_button = button(T.SHOW)
        self.again = button(T.AGAIN)
        for widget in (self.open_button, self.show_button, self.again):
            result_layout.addWidget(widget)
        self.results.hide()
        self.layout.addWidget(self.results)
        self.update_selection()

    def browse(self):
        paths, _ = QFileDialog.getOpenFileNames(self, T.BROWSE, '', T.FILTER)
        if paths:
            self.add_files(paths)

    def add_files(self, paths):
        self.model.add(paths)

    def remove(self):
        rows = {i.row() for i in self.list.selectedIndexes()}
        if rows:
            self.model.remove(rows)

    def update_selection(self):
        count = len(self.model.paths)
        self.drop.set_compact(bool(count))
        self.select_all.setEnabled(bool(count))
        self.remove_button.setEnabled(self.list.selectionModel().hasSelection())

    def message(self, value):
        self.messages.show()
        self.messages.insertPlainText(value + '\n')
