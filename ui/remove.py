from pathlib import Path
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy
from ui import text as T
from ui.ai_tool import AiTool, Prompt
from ui.previews import SIDE, Previews
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
            box.room = box.minimumHeight()  # Its height while results show.
        self.mode.currentIndexChanged.connect(self.refresh)
        self.target.textChanged.connect(self.update_count)
        self.previews = Previews(settings)  # Results take the photos' place, with a background to put behind them.
        self.previews.hide()
        self.previews.save.connect(self.fill)
        self.inputs.layout().addWidget(self.previews)
        self.model.changed.connect(lambda: self.show_results(False))  # Adding or removing photos shows them again.
        self.model.thumbnails.ready.connect(self.previews.fill)
        self.cutouts, self.filling = [], False
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

    def start(self):
        super().start()
        if self.jobs.busy:
            self.previews.clear()
            self.show_results(False)  # The photos, until their results arrive.
            self.previews.show_backgrounds(self.background())
            self.cutouts = []

    def fill(self, color, name):
        """Put the cut-outs on a solid colour, in the same worker; the results join the saved files."""
        if self.jobs.busy or not self.cutouts:
            return
        self.filling = True
        for widget in (self.inputs, self.options, self.previews):
            widget.setEnabled(False)
        self.run.setEnabled(False)
        self.messages.clear()
        self.messages.hide()
        self.progress.setRange(0, 0)
        self.progress.show()
        self.set_status(T.FILLING)
        self.jobs.start(list(self.cutouts), {'tool': 'backdrop', 'color': color, 'name': name,
                                             'output_folder': self.settings.value('output_folder', '')})

    def on_event(self, kind, data):
        if not self.filling:
            super().on_event(kind, data)
            if kind == 'output':
                if self.background():
                    self.cutouts.append(data['path'])
                self.previews.add(data['path'])
                self.show_results(True)
                self.model.thumbnails.request(data['path'], 2 * SIDE)  # Sharp on high-DPI screens.
            return
        if kind == 'output':
            self.outputs.addItem(Path(data['path']).name, data['path'])
            self.outputs.setCurrentIndex(self.outputs.count() - 1)
        elif kind == 'skipped':
            self.message(T.SKIPPED.format(name=Path(data['path']).name, reason=self.reason(data)))
        elif kind in ('done', 'failed', 'cancelled'):
            self.filling = False
            for widget in (self.inputs, self.options, self.previews):
                widget.setEnabled(True)
            self.progress.hide()
            self.update_count()
            self.results.setVisible(self.outputs.count() > 0)
            words = T.FILLED
            self.set_status(T.ERRORS[data] if kind == 'failed' else T.CANCELLED if kind == 'cancelled' else
                            words['success_one'] if len(data) == 1 else words['success'].format(count=len(data)))

    def show_results(self, visible):
        for widget in (self.list, self.select_all, self.remove_button):
            widget.setVisible(not visible)
        self.previews.setVisible(visible)
        self.layout.setStretchFactor(self.inputs, int(visible))  # The previews get the spare height.
        self.layout.setStretchFactor(self.bar, int(not visible))
        for box in (self.keep, self.target):
            box.setMaximumHeight(box.room if visible else 16777215)  # Qt's no limit.

    def reset(self):
        super().reset()
        self.previews.clear()
        self.cutouts = []
