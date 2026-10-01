from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPlainTextEdit
from core.openrouter import MODELS
from core.secret import unseal
from ui import text as T
from ui.tool_screen import ToolScreen


class Prompt(QPlainTextEdit):
    """Room to tell the AI what to do: Enter runs it, Shift+Enter starts a new line."""
    submitted = Signal()

    def __init__(self, hint, text=''):
        super().__init__(text)
        self.setPlaceholderText(hint)
        self.setTabChangesFocus(True)
        self.setMinimumHeight(4 * self.fontMetrics().lineSpacing() + 16)

    def keyPressEvent(self, event):
        if (event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.submitted.emit()
        else:
            super().keyPressEvent(event)


class AiTool(ToolScreen):
    """A tool that sends images to OpenRouter: it needs a key, and each image is one long request."""
    ai = True  # Tagged as AI in the window header.

    def has_key(self):
        return bool(self.settings.value('ai/key', ''))

    def ready(self):
        """Whether the main button can run; tools add their own conditions."""
        return self.has_key()

    def ai_options(self):
        return {'key': unseal(self.settings.value('ai/key', '')),
                'model': self.settings.value(f'ai/{self.tool}_model', '') or MODELS[self.tool]}

    def update_count(self):
        super().update_count()
        self.run.setEnabled(self.run.isEnabled() and self.ready())

    def update_hint(self):
        super().update_hint()
        if not self.has_key():
            self.output_hint.setText(T.NEEDS_KEY)

    def refresh_settings(self):
        super().refresh_settings()
        self.update_count()

    def confirm(self):
        return self.ready()

    def start(self):
        super().start()
        if self.jobs.busy:
            self.progress.setRange(0, 0)  # One long request per image: show activity, not a stalled bar.
