from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit
from core.openrouter import MODELS
from core.secret import unseal
from ui import text as T
from ui.settings import combo
from ui.tool_screen import ToolScreen


class Remove(ToolScreen):
    ai = True  # Tagged as AI in the window header.

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
        """A saved key, and a description when removing something other than the background."""
        return bool(self.settings.value('ai/key', '')) and (self.background() or bool(self.target.text().strip()))

    def refresh(self):
        for widget in (self.keep_label, self.keep):
            widget.setVisible(self.background())
        self.target.setVisible(not self.background())
        self.words = T.CUTOUT if self.background() else T.ERASE
        self.update_count()
        self.update_hint()

    def update_count(self):
        super().update_count()
        self.run.setEnabled(self.run.isEnabled() and self.ready())

    def update_hint(self):
        super().update_hint()
        if not self.settings.value('ai/key', ''):
            self.output_hint.setText(T.NEEDS_KEY)

    def refresh_settings(self):
        super().refresh_settings()
        self.update_count()

    def confirm(self):
        return self.ready()

    def job_options(self):
        for name, widget in (('keep', self.keep), ('target', self.target)):
            self.settings.setValue('remove/' + name, widget.text())
        self.settings.setValue('remove/mode', self.mode.currentData())
        return {'mode': self.mode.currentData(), 'what': (self.keep if self.background() else self.target).text(),
                'key': unseal(self.settings.value('ai/key', '')),
                'model': self.settings.value('ai/remove_model', '') or MODELS['remove']}

    def start(self):
        super().start()
        if self.jobs.busy:
            self.progress.setRange(0, 0)  # Each image is one long request: show activity, not a stalled bar.
