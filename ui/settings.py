import logging
from PySide6.QtCore import QLocale, Signal
from PySide6.QtWidgets import (QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLineEdit, QRadioButton,
                               QVBoxLayout, QWidget)
from core.openrouter import MODELS
from core.secret import seal
from ui import text as T
from ui.widgets import button, label


def region_defaults():
    locale = QLocale.system()
    units = 'cm' if locale.measurementSystem() == QLocale.MeasurementSystem.MetricSystem else 'in'
    # Windows exposes the user's regional paper preference separately from units.
    paper = 'Letter' if locale.territoryToCode(locale.territory()) in {'US', 'CA', 'MX', 'PH'} else 'A4'
    import sys
    if sys.platform == 'win32':
        import ctypes
        buffer = ctypes.create_unicode_buffer(8)
        if ctypes.windll.kernel32.GetLocaleInfoEx(None, 0x100A, buffer, len(buffer)):
            # LOCALE_IPAPERSIZE uses Windows DMPAPER values: Letter=1, A4=9.
            paper = 'Letter' if buffer.value == '1' else 'A4'
    return units, paper


def combo(entries, selected):
    box = QComboBox()
    for title, value in entries:
        box.addItem(title, value)
    box.setCurrentIndex(max(0, box.findData(selected)))
    return box


class Settings(QWidget):
    saved = Signal()

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        units, paper = region_defaults()
        self.title = T.SETTINGS  # Shown in the window header.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.next = QRadioButton(T.NEXT_ORIGINAL)
        self.fixed = QRadioButton(T.FIXED_FOLDER)
        self.next.setChecked(not settings.value('output_folder', ''))
        self.fixed.setChecked(bool(settings.value('output_folder', '')))
        layout.addWidget(label(T.OUTPUT_FOLDER))
        layout.addWidget(self.next)
        layout.addWidget(self.fixed)
        self.folder = QLineEdit(settings.value('output_folder', ''))
        self.folder.setPlaceholderText(T.FOLDER_HINT)
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.folder, 1)
        folder_row.addWidget(button(T.CHOOSE_FOLDER, self.choose_folder))
        layout.addLayout(folder_row)
        form = QFormLayout()
        form.setSpacing(10)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        self.units = combo(T.UNIT_OPTIONS, settings.value('units', units))
        self.paper = combo(T.PAPERS[:2], settings.value('paper', paper))
        form.addRow(T.UNITS, self.units)
        form.addRow(T.DEFAULT_PAPER, self.paper)
        layout.addLayout(form)
        layout.addWidget(label(T.REGION_NOTE, muted=True))
        layout.addWidget(label(T.APPEARANCE, muted=True))
        layout.addWidget(label(T.AI_TOOLS))
        ai = QFormLayout()
        ai.setSpacing(10)
        self.key = QLineEdit()  # Write-only: a saved key is never loaded back, and password fields refuse copying.
        self.key.setEchoMode(QLineEdit.EchoMode.Password)
        ai.addRow(T.API_KEY, self.key)
        self.models = {}
        for tool, title in T.MODEL_TITLES.items():
            self.models[tool] = QLineEdit(settings.value(f'ai/{tool}_model', '') or MODELS[tool])
            self.models[tool].setPlaceholderText(MODELS[tool])
            ai.addRow(title, self.models[tool])
        layout.addLayout(ai)
        self.show_key_state()
        layout.addStretch()
        bottom = QHBoxLayout()  # The result shows beside the button that was pressed.
        self.message = label('')
        bottom.addWidget(self.message, 1)
        bottom.addWidget(button(T.SAVE_SETTINGS, self.save, primary=True))
        layout.addLayout(bottom)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, T.CHOOSE_FOLDER, self.folder.text())
        if folder:
            self.folder.setText(folder)
            self.fixed.setChecked(True)

    def save(self):
        if self.fixed.isChecked() and not self.folder.text().strip():
            self.message.setText(T.FOLDER_REQUIRED)
            return
        self.settings.setValue('output_folder', self.folder.text().strip() if self.fixed.isChecked() else '')
        self.settings.setValue('units', self.units.currentData())
        self.settings.setValue('paper', self.paper.currentData())
        if self.key.text().strip():
            self.settings.setValue('ai/key', seal(self.key.text().strip()))
            self.key.clear()
            logging.info('OpenRouter API key saved')
        for tool, field in self.models.items():
            model = field.text().strip() or MODELS[tool]
            field.setText(model)
            self.settings.setValue(f'ai/{tool}_model', '' if model == MODELS[tool] else model)  # Follow new defaults.
        self.show_key_state()
        self.settings.sync()
        self.message.setText(T.SETTINGS_SAVED)
        self.saved.emit()

    def show_key_state(self):
        """The empty key box says whether a key is saved, without ever showing it."""
        self.key.setPlaceholderText(T.KEY_SAVED if self.settings.value('ai/key', '') else T.KEY_HINT)
