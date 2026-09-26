from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QWidget
from core.files import pdf_name
from ui import text as T
from ui.jobs import Jobs
from ui.settings import combo, region_defaults
from ui.tool_screen import ToolScreen


class MakePdf(ToolScreen):
    def __init__(self, settings):
        super().__init__(T.MAKE_TITLE)
        self.settings = settings
        self.jobs = Jobs(self)
        self.jobs.event.connect(self.on_event)
        self.model.changed.connect(self.update_count)
        self.mode = combo([(T.COMBINED, True), (T.SEPARATE, False)],
                          settings.value('make/combined', True, type=bool))
        self.paper = combo(T.PAPERS, settings.value('make/paper', settings.value('paper', region_defaults()[1])))
        self.paper.setToolTip(T.PDF_SIZE_NOTE)
        self.name = QLineEdit()
        self.name.setMaxLength(120)
        self.name.setMinimumWidth(240)
        self.name.setMaximumWidth(480)
        self.name.setAccessibleName(T.NAME)
        self.name_label = QLabel(T.NAME)
        self.name_box = QWidget()
        name_row = QHBoxLayout(self.name_box)
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.setSpacing(4)
        name_row.addWidget(self.name)
        name_row.addWidget(QLabel(T.EXTENSION))
        self.margin = combo(T.MARGINS, settings.value('make/margin', 'small'))
        options = QGridLayout()
        options.setHorizontalSpacing(12)
        options.setColumnStretch(3, 1)
        for row, fields in enumerate([(QLabel(T.OUTPUT), self.mode, self.name_label, self.name_box),
                                      (QLabel(T.IMAGE_SIZE), self.paper, QLabel(T.MARGIN), self.margin)]):
            for column, widget in enumerate(fields):
                options.addWidget(widget, row, column)
        options.setAlignment(self.margin, Qt.AlignmentFlag.AlignLeft)  # Natural width, not the column's.
        self.options_layout.addLayout(options)
        self.paper.currentIndexChanged.connect(lambda: self.margin.setEnabled(self.paper.currentData() != 'image'))
        self.margin.setEnabled(self.paper.currentData() != 'image')
        self.mode.currentIndexChanged.connect(self.update_hint)
        self.run.clicked.connect(self.start)
        self.cancel.clicked.connect(self.cancel_job)
        self.again.clicked.connect(self.reset)
        self.open_button.clicked.connect(lambda: self.open_output(False))
        self.show_button.clicked.connect(lambda: self.open_output(True))
        self.update_count()
        self.update_hint()

    def update_count(self):
        count = len(self.model.paths)
        self.count.setText(T.FILE_COUNT_ONE if count == 1 else T.FILE_COUNT.format(count=count) if count else T.EMPTY_LIST)
        self.run.setText(T.RUN_ONE if count == 1 else T.RUN.format(count=count) if count else T.RUN_EMPTY)
        self.run.setEnabled(bool(count) and not self.jobs.busy)
        if not self.name.isModified() or not self.name.text().strip():
            self.name.setText(pdf_name(self.model.paths) if count else '')  # Follows the first file until typed.
            self.name.setCursorPosition(0)

    def update_hint(self):
        self.name_label.setVisible(bool(self.mode.currentData()))
        self.name_box.setVisible(bool(self.mode.currentData()))
        folder = self.settings.value('output_folder', '')
        self.output_hint.setText(T.SAVED_FIXED.format(folder=folder) if folder else
                                T.SAVED_NEXT if self.mode.currentData() else T.SAVED_EACH)

    def refresh_settings(self):
        self.update_hint()
        if not self.settings.contains('make/paper'):
            self.paper.setCurrentIndex(self.paper.findData(self.settings.value('paper', region_defaults()[1])))

    def add_files(self, paths):
        if not self.jobs.busy:
            super().add_files(paths)

    def start(self):
        if not self.model.paths or self.jobs.busy:
            return
        options = {'combined': self.mode.currentData(), 'paper': self.paper.currentData(),
                   'margin': self.margin.currentData(), 'output_folder': self.settings.value('output_folder', ''),
                   'name': self.name.text()}
        for key in ('combined', 'paper', 'margin'):
            self.settings.setValue('make/' + key, options[key])
        self.messages.clear()
        self.messages.hide()
        self.outputs.clear()
        self.results.hide()
        self.inputs.setEnabled(False)
        self.run.setEnabled(False)
        self.run.setText(T.RUNNING)
        self.progress.setRange(0, len(self.model.paths))
        self.progress.setValue(0)
        self.progress.show()
        self.cancel.setEnabled(True)
        self.cancel.setText(T.CANCEL)
        self.cancel.show()
        self.set_status(T.RUNNING)
        self.jobs.start(list(self.model.paths), options)

    def cancel_job(self):
        self.cancel.setEnabled(False)
        self.cancel.setText(T.CANCELLING)
        self.set_status(T.CANCELLING)
        self.jobs.cancel()

    def on_event(self, kind, data):
        if kind == 'progress':
            self.progress.setValue(data['index'])
            self.set_status(T.FINISHING if data['index'] == data['total'] else T.PROGRESS.format(
                name=Path(data['path']).name, index=data['index'] + 1, total=data['total']))
        elif kind == 'skipped':
            self.message(T.SKIPPED.format(name=Path(data['path']).name, reason=T.ERRORS[data['code']]))
        elif kind == 'password':
            password, accepted = QInputDialog.getText(self, T.PASSWORD_TITLE,
                T.PASSWORD.format(name=Path(data['path']).name), QLineEdit.EchoMode.Password)
            if self.jobs.busy and not self.jobs.cancelling:
                self.jobs.answers.put(password if accepted else None)
        elif kind == 'output':
            self.outputs.addItem(Path(data['path']).name, data['path'])
        elif kind in ('done', 'failed', 'cancelled'):
            self.inputs.setEnabled(True)
            self.cancel.hide()
            self.progress.hide()
            self.update_count()
            if kind == 'done':
                self.set_status(T.SUCCESS_ONE if len(data) == 1 else T.SUCCESS.format(count=len(data)))
            elif kind == 'cancelled':
                self.set_status(T.CANCELLED)
            else:
                self.set_status(T.ERRORS[data])
            self.results.setVisible(self.outputs.count() > 0)

    def reset(self):
        self.model.replace([])
        self.model.cache.clear()
        self.name.setText('')
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
