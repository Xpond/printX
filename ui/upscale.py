from PySide6.QtWidgets import (QAbstractSpinBox, QCheckBox, QDoubleSpinBox, QGridLayout, QHBoxLayout, QLabel,
                               QMessageBox)
from core.upscale import PAPERS, factor, grade
from ui import text as T
from ui.settings import combo, region_defaults
from ui.tiles import BADGE_TILE
from ui.tool_screen import ToolScreen
from ui.widgets import label

CM = 2.54
HUGE_PIXELS = 300e6  # Warn before making a result this big.


def measure(inches, unit):
    value = inches * CM if unit == 'cm' else inches
    return f'{value:.0f}' if value >= 10 else f'{value:.1f}'


def paper_title(title, unit):
    return title if isinstance(title, str) else title[unit == 'in']  # Photo sizes are named by unit.


class Upscale(ToolScreen):
    def __init__(self, settings):
        super().__init__(settings, 'upscale', T.UPSCALE)
        self.sort.hide()  # Each image is saved on its own, so order does not matter.
        units, paper = region_defaults()
        self.unit = settings.value('units', units)
        self.size = combo(T.SIZES, settings.value('upscale/size', 'fit'))
        self.paper = combo([(paper_title(title, self.unit), value) for title, value in T.PRINT_PAPERS],
                           settings.value('upscale/paper', settings.value('paper', paper)))
        self.paper.setToolTip(T.PAPER_TIP)
        self.custom = [QDoubleSpinBox(), QDoubleSpinBox()]  # Width and height in the chosen units.
        for box in self.custom:
            box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)  # Narrow enough for one row.
            box.setDecimals(1)
            box.setRange(1, 500)
        self.by = QLabel(T.BY)
        self.set_custom([settings.value('upscale/custom_width', 30 / CM, type=float),
                         settings.value('upscale/custom_height', 40 / CM, type=float)])
        self.dpi = combo(T.DPIS, settings.value('upscale/dpi', 300, type=int))
        self.dpi.setToolTip(T.DPI_TIP)
        self.sharpen = combo(T.SHARPEN_LEVELS, settings.value('upscale/sharpen', 'light'))
        self.hard = QCheckBox(T.HARD_EDGES)
        self.hard.setToolTip(T.HARD_TIP)
        self.hard.setChecked(settings.value('upscale/hard', False, type=bool))
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setColumnStretch(1, 1)
        rows = [(T.SIZE, [self.size, self.paper, self.custom[0], self.by, self.custom[1], self.dpi]),
                (T.SHARPENING, [self.sharpen, self.hard])]
        for row, (title, widgets) in enumerate(rows):
            grid.addWidget(QLabel(title), row, 0)
            line = QHBoxLayout()
            for widget in widgets:
                line.addWidget(widget)
            line.addStretch()
            grid.addLayout(line, row, 1)
        self.options_layout.addLayout(grid)
        self.warning = label('', muted=True)
        self.inputs.layout().addWidget(self.warning)
        self.list.setMinimumHeight(BADGE_TILE.height() + 12)
        self.model.tile = BADGE_TILE
        self.model.describe = self.describe
        self.model.dataChanged.connect(self.update_warning)
        self.model.changed.connect(self.update_warning)
        for signal in (self.size.currentIndexChanged, self.paper.currentIndexChanged, self.dpi.currentIndexChanged,
                       self.hard.toggled, *(box.valueChanged for box in self.custom)):
            signal.connect(self.refresh)
        self.refresh()
        self.update_count()
        self.update_hint()

    def set_custom(self, inches):
        for box, value in zip(self.custom, inches):
            box.setSuffix(f' {self.unit}')
            box.setValue(value * CM if self.unit == 'cm' else value)

    def custom_inches(self):
        return [box.value() / CM if self.unit == 'cm' else box.value() for box in self.custom]

    def current(self):
        paper = self.paper.currentData()
        return {'size': self.size.currentData(), 'dpi': self.dpi.currentData(), 'hard': self.hard.isChecked(),
                'paper': tuple(self.custom_inches()) if paper == 'custom' else PAPERS[paper],
                'sharpen': self.sharpen.currentData()}

    def job_options(self):
        options = self.current()
        remembered = dict(options, paper=self.paper.currentData(), custom_width=self.custom_inches()[0],
                          custom_height=self.custom_inches()[1])
        for key, value in remembered.items():
            self.settings.setValue('upscale/' + key, value)
        return options

    def sizes(self):
        """Pixel sizes of the images whose previews have loaded."""
        return [entry[2] for entry in map(self.model.cache.get, self.model.paths) if entry and entry[2]]

    def describe(self, path, size):
        """The print size an image is sharp at, and a badge for how it will look once upscaled."""
        if not size:
            return None
        options = self.current()
        scale = factor(size, options)
        level = grade(scale, options['hard'])
        width, height = (measure(pixels / options['dpi'], self.unit) for pixels in size)
        return (T.SHARP_TO.format(width=width, height=height, unit=self.unit),
                (T.GRADES[level].format(scale=f'{round(scale, 1):g}'), level))

    def refresh(self):
        fit, custom = self.size.currentData() == 'fit', self.paper.currentData() == 'custom'
        self.paper.setEnabled(fit)
        for widget in (*self.custom, self.by):
            widget.setVisible(custom)
            widget.setEnabled(fit)
        self.sharpen.setEnabled(not self.hard.isChecked())
        self.model.refresh()
        self.update_warning()

    def update_warning(self):
        options = self.current()
        count = sum(grade(factor(size, options), options['hard']) == 'blurry' for size in self.sizes())
        self.warning.setText(T.BLURRY_ONE if count == 1 else T.BLURRY.format(count=count))
        self.warning.setVisible(bool(count))

    def confirm(self):
        options = self.current()
        largest = max((w * h * factor((w, h), options) ** 2 for w, h in self.sizes()), default=0)
        if largest <= HUGE_PIXELS:
            return True
        box = QMessageBox(self)
        box.setWindowTitle(T.HUGE_TITLE)
        box.setText(T.HUGE.format(megapixels=round(largest / 1e6)))
        upscale = box.addButton(T.HUGE_YES, QMessageBox.ButtonRole.AcceptRole)
        box.addButton(T.HUGE_NO, QMessageBox.ButtonRole.RejectRole)
        box.exec()
        return box.clickedButton() == upscale

    def refresh_settings(self):
        inches = self.custom_inches()
        units, paper = region_defaults()
        self.unit = self.settings.value('units', units)
        self.set_custom(inches)
        for index, (title, _) in enumerate(T.PRINT_PAPERS):
            self.paper.setItemText(index, paper_title(title, self.unit))
        if not self.settings.contains('upscale/paper'):
            self.paper.setCurrentIndex(self.paper.findData(self.settings.value('paper', paper)))
        self.update_hint()
        self.refresh()
