import multiprocessing


def main():
    import time
    started = time.perf_counter()
    import sys
    from pathlib import Path
    import logging
    from logging_setup import configure_logging
    configure_logging()
    logging.info('Loading desktop interface')
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings, qInstallMessageHandler
    from ui import text as T
    from ui.theme import setup_theme
    from ui.window import Window

    qInstallMessageHandler(lambda mode, context, message: logging.info('Qt: %s', message))
    logging.info('Creating Qt application')
    app = QApplication(sys.argv)
    app.setApplicationName(T.APP)
    app.setOrganizationName(T.APP)
    logging.info('Applying desktop theme')
    setup_theme(app)
    smoke = '--smoke-test' in sys.argv
    if smoke:
        destination = Path(sys.argv[sys.argv.index('--smoke-test') + 1]).absolute()
        destination.mkdir(parents=True, exist_ok=True)
        settings = QSettings(str(destination / 'settings.ini'), QSettings.Format.IniFormat)
    else:
        settings = None
    logging.info('Creating main window')
    window = Window(settings)
    window.show()
    logging.info('Window shown in %.3fs', time.perf_counter() - started)
    if smoke:
        from scripts.smoke import run_smoke
        run_smoke(app, window, destination)
    return app.exec()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    raise SystemExit(main())
