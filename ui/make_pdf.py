from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QLineEdit, QWidget
from core.files import pdf_name
from ui import text as T
from ui.settings import combo, region_defaults
from ui.tool_screen import ToolScreen


class MakePdf(ToolScreen):
    def __init__(self, settings):
        super().__init__(settings, 'make', T.MAKE)
        self.mode = combo([(T.COMBINED, True), (T.SEPARATE, False)],
                          settings.value('make/combined', True, type=bool))
        self.paper = combo(T.PAPERS, settings.value('make/paper', settings.value('paper', region_defaults()[1])))
        self.paper.setToolTip(T.PDF_SIZE_NOTE)
        self.name = QLineEdit()
        self.name.setMaxLength(120)
        self.name.setMinimumWidth(160)
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
        self.update_count()
        self.update_hint()

    def update_count(self):
        super().update_count()
        if not self.name.isModified() or not self.name.text().strip():
            self.name.setText(pdf_name(self.model.paths) if self.model.paths else '')  # Follows the first file until typed.
            self.name.setCursorPosition(0)

    def update_hint(self):
        combined = bool(self.mode.currentData())
        self.name_label.setVisible(combined)
        self.name_box.setVisible(combined)
        folder = self.settings.value('output_folder', '')
        self.output_hint.setText(T.SAVED_FIXED.format(folder=folder) if folder else
                                T.SAVED_NEXT if combined else T.SAVED_EACH)

    def refresh_settings(self):
        self.update_hint()
        if not self.settings.contains('make/paper'):
            self.paper.setCurrentIndex(self.paper.findData(self.settings.value('paper', region_defaults()[1])))

    def job_options(self):
        options = {'combined': self.mode.currentData(), 'paper': self.paper.currentData(),
                   'margin': self.margin.currentData(), 'name': self.name.text()}
        for key in ('combined', 'paper', 'margin'):
            self.settings.setValue('make/' + key, options[key])
        return options

    def reset(self):
        super().reset()
        self.name.setText('')
