from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette


def setup_theme(app):
    directory = Path(__file__).resolve().parent.parent / 'assets/fonts'
    for path in directory.glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(path))
    app.setFont(QFont('Atkinson Hyperlegible', 12))
    app.setStyle('Fusion')
    app.styleHints().colorSchemeChanged.connect(lambda _: apply_theme(app))
    apply_theme(app)


def apply_theme(app, dark=None):
    if dark is None:
        dark = app.styleHints().colorScheme() == Qt.ColorScheme.Dark
    paper, ink = ('#202225', '#f1f0eb') if dark else ('#f7f6f1', '#202226')
    surface, line = ('#292c30', '#50545a') if dark else ('#ffffff', '#cfcec6')
    muted = '#b8bcc3' if dark else '#5b6065'
    magenta = '#f36fa5' if dark else '#ac1557'
    palette = QPalette()
    for role, color in [(QPalette.Window, paper), (QPalette.WindowText, ink),
                        (QPalette.Base, surface), (QPalette.AlternateBase, paper),
                        (QPalette.Text, ink), (QPalette.Button, surface),
                        (QPalette.ButtonText, ink), (QPalette.Highlight, magenta),
                        (QPalette.HighlightedText, '#202226' if dark else '#ffffff'),
                        (QPalette.ToolTipBase, surface), (QPalette.ToolTipText, ink)]:
        palette.setColor(role, QColor(color))
    app.setPalette(palette)
    app.setStyleSheet(f'''
        QWidget {{ color: {ink}; }}
        QMainWindow, QDialog {{ background: {paper}; }}
        QLabel#title {{ font-size: 32px; font-weight: bold; }}
        QLabel#brand {{ font-weight: bold; font-size: 20px; }}
        QLabel[muted="true"] {{ color: {muted}; }}
        QPushButton {{ background: {surface}; border: 1px solid {line}; padding: 5px 14px; min-height: 20px; }}
        QPushButton:hover {{ border-color: {ink}; }}
        QPushButton:focus, QComboBox:focus {{ border: 2px solid {magenta}; }}
        QPushButton:disabled {{ color: {muted}; background: {paper}; }}
        QPushButton#primary {{ background: {magenta}; color: {'#202226' if dark else 'white'}; border: 0; font-weight: bold; padding: 6px 22px; min-height: 20px; }}
        QPushButton#primary:disabled {{ background: {line}; color: {muted}; }}
        QFrame#tile {{ background: {surface}; border: 1px solid {line}; }}
        QFrame#tile[active="true"] {{ border-left: 4px solid {magenta}; }}
        QComboBox, QLineEdit {{ background: {surface}; border: 1px solid {line}; padding: 4px 8px; min-height: 22px; }}
        QComboBox QAbstractItemView {{ background: {surface}; color: {ink}; selection-background-color: {magenta}; }}
        QListView {{ background: {surface}; border: 1px solid {line}; outline: 0; }}
        QListView::item {{ padding: 8px; border-bottom: 1px solid {line}; }}
        QListView::item:selected {{ background: {line}; color: {ink}; }}
        QListView#files::item {{ padding: 6px; border: 0; border-radius: 6px; }}
        QProgressBar {{ border: 1px solid {line}; background: {surface}; min-height: 12px; text-align: center; }}
        QProgressBar::chunk {{ background: {magenta}; }}
        QCheckBox, QRadioButton {{ spacing: 10px; min-height: 22px; }}
    ''')
