from core.openrouter import MODELS
from core.secret import unseal
from ui import text as T
from ui.tool_screen import ToolScreen


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
