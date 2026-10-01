from pathlib import Path
from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QMessageBox, QScrollArea, QStackedWidget, QVBoxLayout,
                               QWidget)
from ui import text as T
from ui.compress import Compress
from ui.home import Home
from ui.make_pdf import MakePdf
from ui.remove import Remove
from ui.settings import Settings
from ui.split import Split
from ui.upscale import Upscale
from ui.widgets import button, label


class Window(QMainWindow):
    def __init__(self, settings=None):
        super().__init__()
        self.setWindowTitle(T.APP)
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parent.parent / 'assets/icon.ico')))
        self.resize(900, 860)
        self.setMinimumSize(680, 480)
        self.settings = settings or QSettings(T.APP, T.APP)
        root = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(root)
        self.setCentralWidget(scroll)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(28, 18, 28, 22)
        layout.setSpacing(16)
        nav = QHBoxLayout()
        self.back = button(T.BACK, self.go_back)
        nav.addWidget(self.back)
        self.title = label(T.APP, 'brand')
        nav.addWidget(self.title)
        self.ai = QLabel(T.AI)
        self.ai.setObjectName('ai')
        nav.addWidget(self.ai, alignment=Qt.AlignmentFlag.AlignVCenter)
        nav.addStretch(1)
        self.settings_button = button(T.SETTINGS, lambda: self.show_screen(self.preferences))
        nav.addWidget(self.settings_button)
        layout.addLayout(nav)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)
        self.remove = Remove(self.settings)
        self.upscale = Upscale(self.settings)
        self.make = MakePdf(self.settings)
        self.compress = Compress(self.settings)
        self.split = Split(self.settings)
        self.tools = {'remove': self.remove, 'upscale': self.upscale, 'make': self.make, 'compress': self.compress,
                      'split': self.split}
        self.home = Home(self.tools)
        self.preferences = Settings(self.settings)
        for widget in (self.home, *self.tools.values(), self.preferences):
            self.stack.addWidget(widget)
        for tool in self.tools.values():
            self.preferences.saved.connect(tool.refresh_settings)
            tool.jobs.event.connect(self.job_changed)
        self.home.selected.connect(lambda key: self.show_screen(self.tools[key]))
        self.show_screen(self.home)
        for sequence, callback in [('Ctrl+O', self.add_files), ('Return', self.run_job), ('Escape', self.go_back)]:
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(callback)

    def busy(self):
        return any(tool.jobs.busy for tool in self.tools.values())

    def current_tool(self):
        screen = self.stack.currentWidget()
        return screen if screen in self.tools.values() else None

    def show_screen(self, screen):
        if self.busy():
            return
        self.stack.setCurrentWidget(screen)
        self.title.setText(getattr(screen, 'title', T.APP))
        self.ai.setVisible(getattr(screen, 'ai', False))
        self.back.setVisible(screen != self.home)
        self.settings_button.setVisible(screen != self.preferences)
        if self.current_tool():
            screen.update_hint()

    def go_back(self):
        if not self.busy():
            self.show_screen(self.home)

    def add_files(self):
        if self.current_tool() and not self.busy():
            self.current_tool().browse()

    def run_job(self):
        if self.current_tool():
            self.current_tool().start()

    def job_changed(self, kind, payload):
        self.back.setEnabled(not self.busy())
        self.settings_button.setEnabled(not self.busy())
        tool = self.current_tool()
        if kind in ('done', 'cancelled', 'failed') and tool and tool.outputs.count():
            QTimer.singleShot(0, lambda: self.centralWidget().ensureWidgetVisible(tool.results, 0, 8))

    def closeEvent(self, event):
        if self.busy():
            box = QMessageBox(self)
            box.setWindowTitle(T.CLOSE_TITLE)
            box.setText(T.CLOSE_MESSAGE)
            yes = box.addButton(T.YES, QMessageBox.ButtonRole.AcceptRole)
            box.addButton(T.NO, QMessageBox.ButtonRole.RejectRole)
            box.exec()
            if box.clickedButton() != yes:
                event.ignore()
                return
        for tool in self.tools.values():
            tool.jobs.shutdown()
            tool.model.thumbnails.shutdown()
        self.settings.sync()
        event.accept()
