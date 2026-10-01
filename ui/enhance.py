from pathlib import Path
from core.files import IMAGE_EXTENSIONS
from ui import text as T
from ui.ai_tool import AiTool, Prompt
from ui.chat import SIDE, Chat


class Enhance(AiTool):
    """A conversation about one photo: each instruction makes a new version from the highlighted one.

    The file list holds that highlighted version, so the shared job flow sends it with the instruction.
    """
    def __init__(self, settings):
        super().__init__(settings, 'enhance', T.ENHANCE)
        for widget in (self.list, self.sort, self.select_all, self.remove_button):
            widget.hide()
        self.layout.setStretchFactor(self.inputs, 0)
        self.add_button.setText(T.CHOOSE_PHOTO)
        self.again.setText(T.NEW_PHOTO)
        self.original = None
        self.chat = Chat(T.ENHANCE['empty'])
        self.chat.files.connect(self.add_files)
        self.chat.browse.connect(self.browse)
        self.chat.picked.connect(self.pick)
        self.layout.insertWidget(1, self.chat, 3)
        self.layout.setStretchFactor(self.bar, 1)  # A roomy box to write in, under the conversation.
        self.prompt = Prompt(T.PROMPT_HINT)
        self.prompt.submitted.connect(self.start)
        self.prompt.textChanged.connect(self.update_count)
        self.options_layout.addWidget(self.prompt)
        self.model.thumbnails.size = 2 * SIDE  # Sharp in the conversation on high-DPI screens.
        self.model.thumbnails.ready.connect(self.chat.fill)
        self.update_count()

    def ready(self):
        return super().ready() and bool(self.model.paths) and bool(self.prompt.toPlainText().strip())

    def add_files(self, paths):
        """A new photo starts a new conversation."""
        if self.jobs.busy or not paths:
            return
        self.reset()
        photos = [path for path in paths if Path(path).suffix.lower() in IMAGE_EXTENSIONS]
        if not photos:
            self.set_status(T.ERRORS['not_image'])
            return
        self.original = str(Path(photos[0]).absolute())
        self.show_version(self.original)
        self.pick(self.original)

    def show_version(self, path):
        self.chat.picture(path)
        self.model.thumbnails.request(path)

    def pick(self, path):
        if not self.jobs.busy:
            self.model.replace([path])
            self.chat.select(path)

    def job_options(self):
        return {'prompt': self.prompt.toPlainText(), 'original': self.original, **self.ai_options()}

    def start(self):
        prompt = self.prompt.toPlainText().strip()
        super().start()
        if self.jobs.busy:
            self.chat.say(prompt, mine=True)
            self.prompt.clear()

    def on_event(self, kind, data):
        if kind == 'skipped':  # Problems belong in the conversation, under the instruction.
            self.chat.say(T.ERRORS[data['code']])
            return
        super().on_event(kind, data)
        if kind == 'output':
            self.show_version(data['path'])
        elif kind == 'done':
            self.pick(data[-1])
        elif kind == 'cancelled':
            self.chat.say(T.CANCELLED)
        if kind in ('done', 'failed', 'cancelled'):
            self.prompt.setFocus()  # Ready for the next instruction.

    def reset(self):
        super().reset()
        self.chat.clear()
        self.original = None
