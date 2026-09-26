import time
from pathlib import Path
from PySide6.QtCore import QModelIndex, QSettings, QTimer, Qt
from ui.window import Window


def test_ordering_and_remove(qtbot, tmp_path, photo, pdf):
    window = Window(QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat))
    qtbot.addWidget(window)
    model = window.make.model
    model.add([str(photo), str(pdf)])
    mime = model.mimeData([model.index(0)])
    assert model.dropMimeData(mime, Qt.DropAction.MoveAction, 2, 0, QModelIndex())
    assert model.paths == [str(pdf), str(photo)]
    model.remove({0})
    assert model.paths == [str(photo)]


def test_real_worker_success_cancel_and_reuse(qtbot, tmp_path, photo):
    window = Window(QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat))
    qtbot.addWidget(window)
    window.show_screen(window.make)
    window.show()
    screen = window.make
    screen.add_files([str(photo)])
    screen.start()
    qtbot.waitUntil(lambda: not screen.jobs.busy, timeout=30000)
    assert screen.outputs.count() == 1
    assert Path(screen.outputs.currentData()).exists()
    warm_pid = screen.jobs.process.pid
    screen.start()
    assert screen.jobs.process.pid == warm_pid
    qtbot.waitUntil(lambda: not screen.jobs.busy, timeout=30000)
    assert '(2)' in screen.outputs.currentData()
    # A genuine long job: many repeated JPEG pages, submitted directly to the worker.
    beats = []
    timer = QTimer()
    timer.timeout.connect(lambda: beats.append(time.monotonic()))
    timer.start(10)
    screen.jobs.start([str(photo)] * 2000, {'combined': True, 'output_folder': str(tmp_path / 'batch')})
    qtbot.wait(150)
    started = time.monotonic()
    screen.cancel_job()
    qtbot.waitUntil(lambda: not screen.jobs.busy, timeout=3000)
    assert time.monotonic() - started < 1
    assert len(beats) >= 5
    timer.stop()
    assert not list(tmp_path.rglob('.printshop-*'))
    screen.start()
    qtbot.waitUntil(lambda: not screen.jobs.busy, timeout=30000)
    assert screen.outputs.count() == 1
    window.close()


def test_200_files_added_without_reading_them(qtbot, tmp_path):
    window = Window(QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat))
    qtbot.addWidget(window)
    started = time.monotonic()
    window.make.add_files([str(tmp_path / f'{i}.jpg') for i in range(200)])
    assert time.monotonic() - started < .5
    assert window.make.model.rowCount() == 200
    assert window.make.model.thumbnails.process is None
