from pathlib import Path
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QScrollArea, QStackedWidget, QVBoxLayout, QWidget
from ui import text as T
from ui.home import Home
from ui.make_pdf import MakePdf
from ui.settings import Settings
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
        nav.addWidget(self.title, 1)
        self.settings_button = button(T.SETTINGS, lambda: self.show_screen(self.preferences))
        nav.addWidget(self.settings_button)
        layout.addLayout(nav)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)
        self.home = Home()
        self.make = MakePdf(self.settings)
        self.preferences = Settings(self.settings)
        self.preferences.saved.connect(self.make.refresh_settings)
        for widget in (self.home, self.make, self.preferences):
            self.stack.addWidget(widget)
        self.home.selected.connect(lambda tool: self.show_screen(self.make))
        self.show_screen(self.home)
        for sequence, callback in [('Ctrl+O', self.add_files), ('Return', self.run_job), ('Escape', self.go_back)]:
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(callback)
        self.make.jobs.event.connect(self.job_changed)

    def show_screen(self, screen):
        if self.make.jobs.busy:
            return
        self.stack.setCurrentWidget(screen)
        self.title.setText(getattr(screen, 'title', T.APP))
        self.back.setVisible(screen != self.home)
        self.settings_button.setVisible(screen != self.preferences)
        if screen == self.make:
            self.make.update_hint()

    def go_back(self):
        if not self.make.jobs.busy:
            self.show_screen(self.home)

    def add_files(self):
        if not self.make.jobs.busy:
            self.show_screen(self.make)
            self.make.browse()

    def run_job(self):
        if self.stack.currentWidget() == self.make:
            self.make.start()

    def job_changed(self, kind, payload):
        self.back.setEnabled(not self.make.jobs.busy)
        self.settings_button.setEnabled(not self.make.jobs.busy)
        if kind in ('done', 'cancelled', 'failed') and self.make.outputs.count():
            QTimer.singleShot(0, lambda: self.centralWidget().ensureWidgetVisible(self.make.results, 0, 8))

    def closeEvent(self, event):
        if self.make.jobs.busy:
            box = QMessageBox(self)
            box.setWindowTitle(T.CLOSE_TITLE)
            box.setText(T.CLOSE_MESSAGE)
            yes = box.addButton(T.YES, QMessageBox.ButtonRole.AcceptRole)
            box.addButton(T.NO, QMessageBox.ButtonRole.RejectRole)
            box.exec()
            if box.clickedButton() != yes:
                event.ignore()
                return
        self.make.jobs.shutdown()
        self.make.model.thumbnails.shutdown()
        self.settings.sync()
        event.accept()
