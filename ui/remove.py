from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit
from ui import text as T
from ui.ai_tool import AiTool
from ui.settings import combo


class Remove(AiTool):
    def __init__(self, settings):
        super().__init__(settings, 'remove', T.CUTOUT)
        self.sort.hide()  # Each image is saved on its own, so order does not matter.
        self.mode = combo(T.REMOVE_MODES, settings.value('remove/mode', 'background'))
        self.keep_label = QLabel(T.KEEP)
        self.keep = QLineEdit(settings.value('remove/keep', ''))
        self.keep.setPlaceholderText(T.KEEP_HINT)
        self.target = QLineEdit(settings.value('remove/target', ''))
        self.target.setPlaceholderText(T.TARGET_HINT)
        row = QHBoxLayout()
        row.setSpacing(12)
        for widget in (QLabel(T.REMOVE_WHAT), self.mode, self.keep_label):
            row.addWidget(widget)
        row.addWidget(self.keep, 1)
        row.addWidget(self.target, 1)
        self.options_layout.addLayout(row)
        self.mode.currentIndexChanged.connect(self.refresh)
        self.target.textChanged.connect(self.update_count)
        self.refresh()

    def background(self):
        return self.mode.currentData() == 'background'

    def ready(self):
        """Removing something other than the background needs a description of it."""
        return super().ready() and (self.background() or bool(self.target.text().strip()))

    def refresh(self):
        for widget in (self.keep_label, self.keep):
            widget.setVisible(self.background())
        self.target.setVisible(not self.background())
        self.words = T.CUTOUT if self.background() else T.ERASE
        self.update_count()

    def job_options(self):
        for name, widget in (('keep', self.keep), ('target', self.target)):
            self.settings.setValue('remove/' + name, widget.text())
        self.settings.setValue('remove/mode', self.mode.currentData())
        return {'mode': self.mode.currentData(), 'what': (self.keep if self.background() else self.target).text(),
                **self.ai_options()}
