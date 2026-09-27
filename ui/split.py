from PySide6.QtWidgets import QAbstractSpinBox, QHBoxLayout, QLabel, QLineEdit, QSpinBox
from core.pdf_tools import page_ranges
from ui import text as T
from ui.settings import combo
from ui.tool_screen import ToolScreen
from ui.widgets import label


class Split(ToolScreen):
    def __init__(self, settings):
        super().__init__(settings, 'split', T.SPLIT)
        self.sort.hide()  # Each PDF is split on its own, so order does not matter.
        self.parts = 0
        self.mode = combo(T.SPLIT_MODES, settings.value('split/mode', 'pages'))
        self.ranges = QLineEdit(settings.value('split/ranges', ''))
        self.ranges.setPlaceholderText(T.RANGES_EXAMPLE)
        self.every = QSpinBox()
        self.every.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)  # Compact, like Upscale's sizes.
        self.every.setRange(2, 999)
        self.every.setSuffix(T.PAGES_PER_PDF)
        self.every.setValue(settings.value('split/every', 2, type=int))
        self.note = label('', muted=True)
        row = QHBoxLayout()
        row.setSpacing(12)
        for widget in (QLabel(T.SPLIT_BY), self.mode, self.ranges, self.every):
            row.addWidget(widget)
        row.addWidget(self.note, 1)
        self.options_layout.addLayout(row)
        self.open_button.setText(T.OPEN_FOLDER)  # Results are folders, so Show in folder adds nothing.
        self.show_button.hide()
        self.mode.currentIndexChanged.connect(self.refresh)
        self.ranges.textChanged.connect(self.refresh)
        self.refresh()

    def valid(self):
        return self.mode.currentData() != 'ranges' or page_ranges(self.ranges.text()) is not None

    def refresh(self):
        mode = self.mode.currentData()
        self.ranges.setVisible(mode == 'ranges')
        self.every.setVisible(mode == 'every')
        self.note.setText(T.SPLIT_NOTES[mode] if self.valid() else T.RANGES_HELP)
        self.update_count()

    def update_count(self):
        super().update_count()
        self.run.setEnabled(self.run.isEnabled() and self.valid())

    def confirm(self):
        return self.valid()

    def job_options(self):
        options = {'mode': self.mode.currentData(), 'ranges': self.ranges.text(), 'every': self.every.value()}
        for key, value in options.items():
            self.settings.setValue('split/' + key, value)
        self.parts = 0
        return options

    def on_event(self, kind, data):
        if kind == 'output':
            self.parts += data['parts']
        super().on_event(kind, data)
        if kind == 'done' and self.parts > 1:
            self.set_status(T.PARTS.format(status=self.status.text(), count=self.parts))
