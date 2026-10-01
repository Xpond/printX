from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy
from ui import text as T
from ui.ai_tool import AiTool, Prompt
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
