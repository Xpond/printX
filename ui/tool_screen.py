from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QFileDialog, QHBoxLayout, QProgressBar,
                               QTextEdit, QVBoxLayout, QWidget)
from ui import text as T
from ui.file_list import FileList, FileModel
from ui.widgets import button, label


class ToolScreen(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title  # Shown in the window header.
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.inputs = QWidget()
        inputs = QVBoxLayout(self.inputs)
        inputs.setContentsMargins(0, 0, 0, 0)
        inputs.setSpacing(10)
        toolbar = QHBoxLayout()
        self.count = label(T.EMPTY_LIST, muted=True)
        toolbar.addWidget(self.count, 1)
        toolbar.addWidget(button(T.ADD, self.browse))
        self.model = FileModel(self)
        self.list = FileList(self.model)
        self.list.files.connect(self.add_files)
        self.list.browse.connect(self.browse)
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
        self.layout.addWidget(self.inputs, 1)
        self.options = QWidget()  # Tools add option rows here; the main button lines up with the last row.
        self.options_layout = QVBoxLayout(self.options)
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.run = button(T.RUN_EMPTY, primary=True)
        self.cancel = button(T.CANCEL)
        self.cancel.hide()
        bar = QHBoxLayout()
        bar.addWidget(self.options, 1)
        for widget in (self.run, self.cancel):
            bar.addWidget(widget, alignment=Qt.AlignmentFlag.AlignBottom)
        self.layout.addLayout(bar)
        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        self.messages.setMaximumHeight(85)
        self.messages.hide()
        self.layout.addWidget(self.messages)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.hide()
        self.layout.addWidget(self.progress)
        self.status = label('')
        self.status.hide()
        self.layout.addWidget(self.status)
        self.output_hint = label(T.SAVED_NEXT, muted=True)
        self.layout.addWidget(self.output_hint)
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
        self.list.viewport().setCursor(Qt.CursorShape.ArrowCursor if count else Qt.CursorShape.PointingHandCursor)
        self.select_all.setEnabled(bool(count))
        self.remove_button.setEnabled(self.list.selectionModel().hasSelection())

    def set_status(self, text):
        """Job progress and results take the place of the save hint."""
        self.status.setText(text)
        self.status.setVisible(bool(text))
        self.output_hint.setVisible(not text)

    def message(self, value):
        self.messages.show()
        self.messages.insertPlainText(value + '\n')
