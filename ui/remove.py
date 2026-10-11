from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy
from ui import text as T
from ui.ai_tool import AiTool, Prompt
from ui.backgrounds import SIDE, Backgrounds
from ui.settings import combo
from ui.tiles import TILE


class Remove(AiTool):
    def __init__(self, settings):
        super().__init__(settings, 'remove', T.CUTOUT)
        self.sort.hide()  # Each image is saved on its own, so order does not matter.
        self.list.setWrapping(False)  # One row of photos; the description gets the room.
        self.list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.list.setFixedHeight(TILE.height() + 12 + self.list.horizontalScrollBar().sizeHint().height())
        self.layout.setStretchFactor(self.inputs, 0)
        self.layout.setStretchFactor(self.bar, 1)
        self.mode = combo(T.REMOVE_MODES, settings.value('remove/mode', 'background'))
        self.keep = Prompt(T.KEEP_HINT, settings.value('remove/keep', ''))
        self.target = Prompt(T.TARGET_HINT, settings.value('remove/target', ''))
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(QLabel(T.REMOVE_WHAT))
        row.addWidget(self.mode)
        row.addStretch()
        self.options_layout.addLayout(row)
        for box in (self.keep, self.target):
            box.submitted.connect(self.start)
            self.options_layout.addWidget(box, 1)
        self.mode.currentIndexChanged.connect(self.refresh)
        self.target.textChanged.connect(self.update_count)
        self.previews = Backgrounds()  # Results take the photos' place as they arrive.
        self.previews.hide()
        self.previews.save.connect(self.fill)
        self.inputs.layout().addWidget(self.previews)
        self.model.thumbnails.size = 2 * SIDE  # Previews grow with the window.
        self.model.thumbnails.ready.connect(self.previews.fill)
        self.model.changed.connect(lambda: self.show_results(False))  # Adding or removing photos shows them again.
        self.refresh()

    def background(self):
        return self.mode.currentData() == 'background'

    def ready(self):
        """Removing something other than the background needs a description of it."""
        return super().ready() and (self.background() or bool(self.target.toPlainText().strip()))

    def refresh(self):
        self.keep.setVisible(self.background())
        self.target.setVisible(not self.background())
        self.words = T.CUTOUT if self.background() else T.ERASE
        self.update_count()

    def job_options(self):
        for name, box in (('keep', self.keep), ('target', self.target)):
            self.settings.setValue('remove/' + name, box.toPlainText())
        self.settings.setValue('remove/mode', self.mode.currentData())
        return {'mode': self.mode.currentData(),
                'what': (self.keep if self.background() else self.target).toPlainText(), **self.ai_options()}

    def show_results(self, visible):
        for widget in (self.list, self.select_all, self.remove_button):
            widget.setVisible(not visible)
        self.previews.setVisible(visible)
        self.layout.setStretchFactor(self.inputs, int(visible))  # Results get the spare height, not the description.
        self.layout.setStretchFactor(self.bar, int(not visible))
        for box in (self.keep, self.target):
            box.setMaximumHeight(4 * box.fontMetrics().lineSpacing() + 16 if visible else 16777215)

    def start(self):
        super().start()
        if self.jobs.busy:
            self.reset_previews()
            self.previews.row.setVisible(self.background())  # Only cut-outs get a new background.

    def fill(self, color, name):
        """Put every cut-out on a solid colour, as a full-size copy."""
        if not self.jobs.busy:
            self.words = T.FILL
            self.launch(list(self.previews.pictures), {'tool': 'backdrop', 'color': color, 'name': name})

    def on_event(self, kind, data):
        super().on_event(kind, data)
        if kind == 'output' and self.words is not T.FILL:
            self.previews.add(data['path'])
            self.model.thumbnails.request(data['path'])
            self.show_results(True)
        elif kind in ('done', 'failed', 'cancelled'):
            self.refresh()  # Back to this mode's words.

    def reset_previews(self):
        self.previews.clear()
        self.show_results(False)

    def reset(self):
        super().reset()
        self.reset_previews()
