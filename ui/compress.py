import os
from PySide6.QtWidgets import QHBoxLayout, QLabel
from ui import text as T
from ui.settings import combo
from ui.tiles import BADGE_TILE
from ui.tool_screen import ToolScreen
from ui.widgets import label


def size_text(size):
    """Sizes as File Explorer shows them."""
    if size < 1024 ** 2:
        return f'{max(1, round(size / 1024))} KB'
    size /= 1024 ** 2
    return f'{size:.1f} MB' if size < 100 else f'{size:.0f} MB'


def smaller(before, after):
    return max(1, round(100 * (1 - after / before)))


class Compress(ToolScreen):
    def __init__(self, settings):
        super().__init__(settings, 'compress', T.COMPRESS)
        self.sort.hide()  # Each PDF is saved on its own, so order does not matter.
        self.before, self.after = {}, {}  # Bytes by path; after is None when a PDF was already optimized.
        self.level = combo(T.LEVELS, settings.value('compress/level', 'recommended'))
        self.note = label(T.LEVEL_NOTES[self.level.currentData()], muted=True)
        self.level.currentIndexChanged.connect(lambda: self.note.setText(T.LEVEL_NOTES[self.level.currentData()]))
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(QLabel(T.COMPRESSION))
        row.addWidget(self.level)
        row.addWidget(self.note, 1)
        self.options_layout.addLayout(row)
        self.list.setMinimumHeight(BADGE_TILE.height() + 12)
        self.model.tile = BADGE_TILE
        self.model.describe = self.describe
        self.update_count()

    def describe(self, path, size):
        """Each PDF's size; once compressed, its new size and a badge with the saving."""
        if path not in self.before:
            self.before[path] = os.path.getsize(path) if os.path.isfile(path) else 0
        before, after = self.before[path], self.after.get(path)
        if not before:
            return None
        if path not in self.after:
            return size_text(before), None
        if after is None:
            return size_text(before), (T.OPTIMIZED, 'big')
        return (T.SHRUNK.format(before=size_text(before), after=size_text(after)),
                (T.SMALLER.format(percent=smaller(before, after)), 'sharp'))

    def job_options(self):
        self.after.clear()  # A new job replaces the last results.
        self.model.refresh()
        self.settings.setValue('compress/level', self.level.currentData())
        return {'level': self.level.currentData()}

    def on_event(self, kind, data):
        if kind == 'output':
            self.before[data['source']], self.after[data['source']] = data['before'], data['after']
        elif kind == 'skipped' and data['code'] == 'optimized':
            self.after[data['path']] = None
        super().on_event(kind, data)
        if kind in ('output', 'skipped'):
            self.model.refresh()
        elif kind == 'done':
            saved = {path: after for path, after in self.after.items() if after}
            before, after = sum(self.before[path] for path in saved), sum(saved.values())
            self.set_status(T.TOTAL.format(status=self.status.text(), before=size_text(before),
                                           after=size_text(after), percent=smaller(before, after)))

    def reset(self):
        super().reset()
        self.before.clear()
        self.after.clear()
