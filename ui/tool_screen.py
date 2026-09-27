from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QComboBox, QFileDialog, QHBoxLayout, QInputDialog, QLineEdit, QProgressBar,
                               QTextEdit, QVBoxLayout, QWidget)
from ui import text as T
from ui.file_list import FileList, FileModel
from ui.jobs import Jobs
from ui.widgets import button, label


class ToolScreen(QWidget):
    """Files, the tool's option rows beside its main button, then progress and results."""
    def __init__(self, settings, tool, words):
        super().__init__()
        self.settings, self.tool, self.words = settings, tool, words
        self.title = words['title']  # Shown in the window header.
        self.jobs = Jobs(self)
        self.jobs.event.connect(self.on_event)
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
        self.list = FileList(self.model, words['empty'])
        self.list.files.connect(self.add_files)
        self.list.browse.connect(self.browse)
        self.list.remove_requested.connect(self.remove)
        self.sort = button(T.SORT, self.model.sort)
        toolbar.addWidget(self.sort)
        self.select_all = button(T.SELECT_ALL, self.list.selectAll)
        self.remove_button = button(T.REMOVE, self.remove)
        for widget in (self.select_all, self.remove_button):
            widget.setToolTip(T.REMOVE_TIP)
            toolbar.addWidget(widget)
        self.list.selectionModel().selectionChanged.connect(self.update_selection)
        self.model.changed.connect(self.update_selection)
        self.model.changed.connect(self.update_count)
        inputs.addLayout(toolbar)
        inputs.addWidget(self.list, 1)
        self.layout.addWidget(self.inputs, 1)
        self.options = QWidget()  # Tools add option rows here; the main button lines up with the last row.
        self.options_layout = QVBoxLayout(self.options)
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.run = button(words['run_empty'], self.start, primary=True)
        self.cancel = button(T.CANCEL, self.cancel_job)
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
        self.open_button = button(T.OPEN, lambda: self.open_output(False))
        self.show_button = button(T.SHOW, lambda: self.open_output(True))
        self.again = button(T.AGAIN, self.reset)
        for widget in (self.open_button, self.show_button, self.again):
            result_layout.addWidget(widget)
        self.results.hide()
        self.layout.addWidget(self.results)
        self.update_selection()

    def job_options(self):
        """The tool's options for the next job; tools also remember them for next time."""
        return {}

    def confirm(self):
        """Last chance for a tool to stop a job before it starts."""
        return True

    def update_hint(self):
        folder = self.settings.value('output_folder', '')
        self.output_hint.setText(T.SAVED_FIXED.format(folder=folder) if folder else self.words.get('saved', T.SAVED_EACH))

    def refresh_settings(self):
        self.update_hint()

    def browse(self):
        paths, _ = QFileDialog.getOpenFileNames(self, self.words['browse'], '', self.words['filter'])
        if paths:
            self.add_files(paths)

    def add_files(self, paths):
        if not self.jobs.busy:
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

    def update_count(self):
        count, words = len(self.model.paths), self.words
        self.count.setText(words['count_one'] if count == 1 else words['count'].format(count=count) if count else T.EMPTY_LIST)
        self.run.setText(words['run_one'] if count == 1 else words['run'].format(count=count) if count else words['run_empty'])
        self.run.setEnabled(bool(count) and not self.jobs.busy)

    def set_status(self, text):
        """Job progress and results take the place of the save hint."""
        self.status.setText(text)
        self.status.setVisible(bool(text))
        self.output_hint.setVisible(not text)

    def message(self, value):
        self.messages.show()
        self.messages.insertPlainText(value + '\n')

    def start(self):
        if not self.model.paths or self.jobs.busy or not self.confirm():
            return
        options = dict(self.job_options(), tool=self.tool, output_folder=self.settings.value('output_folder', ''))
        self.messages.clear()
        self.messages.hide()
        self.outputs.clear()
        self.results.hide()
        self.inputs.setEnabled(False)
        self.options.setEnabled(False)
        self.run.setEnabled(False)
        self.run.setText(self.words['running'])
        self.progress.setRange(0, len(self.model.paths) * 100)  # Tools may report fractions of a file.
        self.progress.setValue(0)
        self.progress.show()
        self.cancel.setEnabled(True)
        self.cancel.setText(T.CANCEL)
        self.cancel.show()
        self.set_status(self.words['running'])
        self.jobs.start(list(self.model.paths), options)

    def cancel_job(self):
        self.cancel.setEnabled(False)
        self.cancel.setText(T.CANCELLING)
        self.set_status(T.CANCELLING)
        self.jobs.cancel()

    def on_event(self, kind, data):
        if kind == 'progress':
            self.progress.setValue(round(data['index'] * 100))
            self.set_status(self.words['finishing'] if data['index'] == data['total'] else self.words['progress'].format(
                name=Path(data['path']).name, index=int(data['index']) + 1, total=data['total']))
        elif kind == 'skipped':
            self.message(T.SKIPPED.format(name=Path(data['path']).name, reason=T.ERRORS[data['code']]))
        elif kind == 'notice':
            self.message(T.NOTICES[data['code']].format(name=Path(data['path']).name))
        elif kind == 'password':
            password, accepted = QInputDialog.getText(self, T.PASSWORD_TITLE,
                T.PASSWORD.format(name=Path(data['path']).name), QLineEdit.EchoMode.Password)
            if self.jobs.busy and not self.jobs.cancelling:
                self.jobs.answers.put(password if accepted else None)
        elif kind == 'output':
            self.outputs.addItem(Path(data['path']).name, data['path'])
        elif kind in ('done', 'failed', 'cancelled'):
            self.inputs.setEnabled(True)
            self.options.setEnabled(True)
            self.cancel.hide()
            self.progress.hide()
            self.update_count()
            if kind == 'done':
                count = len(data)
                self.set_status(self.words['success_one'] if count == 1 else self.words['success'].format(count=count))
            else:
                self.set_status(T.CANCELLED if kind == 'cancelled' else T.ERRORS[data])
            self.results.setVisible(self.outputs.count() > 0)

    def reset(self):
        self.model.replace([])
        self.model.cache.clear()
        self.results.hide()
        self.messages.hide()
        self.messages.clear()
        self.set_status('')
        self.outputs.clear()

    def open_output(self, folder):
        path = self.outputs.currentData()
        if path:
            target = str(Path(path).parent) if folder else path
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(target)):
                self.message(T.OUTPUT_FAILED)
