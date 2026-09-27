import time
from pathlib import Path
import pytest
from PIL import Image
from PySide6.QtCore import QModelIndex, QSettings, QTimer, Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QApplication, QFileDialog
from ui.compress import size_text
from ui.tiles import BADGE, TILE, two_lines
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


def test_grid_select_all_remove_and_click_to_add(qtbot, tmp_path, monkeypatch):
    window = Window(QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat))
    qtbot.addWidget(window)
    window.resize(1280, 650)
    window.show()
    window.show_screen(window.make)
    screen = window.make
    assert not screen.select_all.isEnabled() and not screen.remove_button.isEnabled()
    screen.add_files([str(tmp_path / f'{i}.jpg') for i in range(6)])
    qtbot.wait(50)
    first, second = (screen.list.visualRect(screen.model.index(i)) for i in range(2))
    assert first.top() == second.top() and screen.list.height() >= TILE.height()  # Tiles wrap in a grid.
    screen.select_all.click()
    assert screen.remove_button.isEnabled()
    screen.remove_button.click()
    assert screen.model.paths == []
    assert not screen.remove_button.isEnabled()
    browsed = []
    monkeypatch.setattr(QFileDialog, 'getOpenFileNames', lambda *args: browsed.append(1) or ([], ''))
    qtbot.mouseClick(screen.list.viewport(), Qt.MouseButton.LeftButton)
    assert browsed  # The empty grid replaces the drop zone: clicking it opens the file picker.
    screen.add_files([str(tmp_path / f'{i}.jpg') for i in range(3)])
    screen.list.setCurrentIndex(screen.model.index(1))
    qtbot.keyClick(screen.list, Qt.Key.Key_Delete)
    assert [Path(p).name for p in screen.model.paths] == ['0.jpg', '2.jpg']


def test_file_name_follows_first_file_until_typed(qtbot, tmp_path, monkeypatch):
    window = Window(QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat))
    qtbot.addWidget(window)
    window.show()
    window.show_screen(window.make)
    screen, model = window.make, window.make.model
    screen.add_files([str(tmp_path / f'{name}.jpg') for name in 'abc'])

    def move_first_to_end():
        model.dropMimeData(model.mimeData([model.index(0)]), Qt.DropAction.MoveAction, 3, 0, QModelIndex())

    assert screen.name.text() == 'a_combined'
    move_first_to_end()
    assert screen.name.text() == 'b_combined'
    screen.name.selectAll()
    qtbot.keyClicks(screen.name, 'Job 42')
    move_first_to_end()
    assert screen.name.text() == 'Job 42'
    started = {}
    monkeypatch.setattr(screen.jobs, 'start', lambda paths, options: started.update(options))
    screen.start()
    assert started['name'] == 'Job 42'
    screen.reset()
    screen.add_files([str(tmp_path / 'd.jpg')])
    assert screen.name.text() == 'd_made'
    screen.mode.setCurrentIndex(screen.mode.findData(False))
    assert not screen.name_box.isVisible()


def test_long_names_wrap_after_a_separator(qapp):
    metrics = QFontMetrics(QApplication.font())
    width = metrics.horizontalAdvance('customer-order-1-fin')
    assert two_lines('customer-order-1-final-version.jpg', metrics, width) == ['customer-order-1-', 'final-version.jpg']
    assert two_lines('short.jpg', metrics, width) == ['short.jpg']


def test_upscale_badges_follow_the_options(qtbot, tmp_path, photo, monkeypatch):
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat)
    settings.setValue('units', 'cm')
    window = Window(settings)
    qtbot.addWidget(window)
    window.show()
    window.home.selected.emit('upscale')
    screen = window.upscale
    assert window.stack.currentWidget() == screen and not screen.sort.isVisibleTo(screen)
    screen.add_files([str(photo)])
    qtbot.waitUntil(lambda: bool(screen.sizes()), timeout=10000)
    index = screen.model.index(0)
    screen.paper.setCurrentIndex(screen.paper.findData('A4'))
    assert index.data(BADGE) == ('5.8× · soft', 'blurry') and not screen.warning.isHidden()
    screen.size.setCurrentIndex(screen.size.findData('2'))
    assert index.data(BADGE) == ('2× · sharp', 'sharp') and screen.warning.isHidden()
    assert not screen.paper.isEnabled()
    screen.hard.setChecked(True)
    assert not screen.sharpen.isEnabled()
    screen.hard.setChecked(False)
    screen.size.setCurrentIndex(screen.size.findData('fit'))
    screen.paper.setCurrentIndex(screen.paper.findData('A6'))
    screen.dpi.setCurrentIndex(screen.dpi.findData(150))
    assert index.data(BADGE) == ('1.5× · sharp', 'sharp')
    assert index.data().endswith('Sharp to 10 × 6.8 cm')
    screen.paper.setCurrentIndex(screen.paper.findData('custom'))
    screen.custom[0].setValue(5)
    screen.custom[1].setValue(5)
    assert index.data(BADGE) == ('Already big enough', 'big')
    started = {}
    monkeypatch.setattr(screen.jobs, 'start', lambda paths, options: started.update(options))
    screen.start()
    assert started['tool'] == 'upscale' and started['paper'] == pytest.approx((5 / 2.54, 5 / 2.54))
    assert settings.value('upscale/paper') == 'custom' and settings.value('upscale/dpi', type=int) == 150


def test_upscale_runs_in_the_worker_and_cancels(qtbot, tmp_path, photo):
    window = Window(QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat))
    qtbot.addWidget(window)
    window.show()
    window.show_screen(window.upscale)
    screen = window.upscale
    screen.size.setCurrentIndex(screen.size.findData('2'))
    screen.add_files([str(photo)])
    screen.start()
    qtbot.waitUntil(lambda: not screen.jobs.busy, timeout=30000)
    output = Path(screen.outputs.currentData())
    assert output.name == f'{photo.stem}_upscaled.jpg'
    with Image.open(output) as result:
        assert result.size == (1200, 800)
    big = tmp_path / 'big.jpg'
    Image.effect_noise((2000, 1500), 60).convert('RGB').save(big)
    screen.reset()
    screen.size.setCurrentIndex(screen.size.findData('4'))
    screen.add_files([str(big)])
    screen.start()
    qtbot.wait(150)
    started = time.monotonic()
    screen.cancel_job()
    qtbot.waitUntil(lambda: not screen.jobs.busy, timeout=3000)
    assert time.monotonic() - started < 1
    assert not list(tmp_path.glob('big_upscaled*')) and not list(tmp_path.rglob('.printshop-*'))
    window.close()


def test_compress_shows_sizes_savings_and_cancels(qtbot, tmp_path, pdf, photo_pdf):
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat)
    window = Window(settings)
    qtbot.addWidget(window)
    window.show()
    window.home.selected.emit('compress')
    screen = window.compress
    big = photo_pdf()
    screen.add_files([str(big), str(pdf)])
    first, second = screen.model.index(0), screen.model.index(1)
    assert first.data().endswith(size_text(big.stat().st_size)) and first.data(BADGE) is None
    screen.level.setCurrentIndex(screen.level.findData('print'))
    screen.start()
    qtbot.waitUntil(lambda: not screen.jobs.busy, timeout=30000)
    assert ' → ' in first.data() and first.data(BADGE)[0].endswith('% smaller')
    assert second.data(BADGE) == ('Already optimized', 'big')
    assert screen.status.text().startswith('Compressed 1 PDF · ') and screen.outputs.count() == 1
    assert settings.value('compress/level') == 'print'
    screen.reset()
    screen.add_files([str(photo_pdf('long.pdf', pages=12))])
    screen.start()
    qtbot.waitUntil(lambda: screen.progress.value() > 0, timeout=10000)  # Ghostscript is past page 1.
    started = time.monotonic()
    screen.cancel_job()
    qtbot.waitUntil(lambda: not screen.jobs.busy, timeout=3000)
    assert time.monotonic() - started < 1
    assert not list(tmp_path.glob('long_compressed*')) and not list(tmp_path.rglob('.printshop-*'))
    window.close()


def test_split_checks_ranges_and_saves_a_folder(qtbot, tmp_path, pdf):
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat)
    window = Window(settings)
    qtbot.addWidget(window)
    window.show()
    window.home.selected.emit('split')
    screen = window.split
    screen.add_files([str(pdf)])
    assert screen.run.isEnabled() and not screen.ranges.isVisible() and not screen.every.isVisible()
    screen.mode.setCurrentIndex(screen.mode.findData('ranges'))
    assert screen.ranges.isVisible() and not screen.run.isEnabled()  # Nothing typed yet.
    screen.ranges.setText('1-2, 3')
    assert screen.run.isEnabled()
    screen.start()
    qtbot.waitUntil(lambda: not screen.jobs.busy, timeout=30000)
    assert screen.status.text() == 'Split 1 PDF into 2 PDFs'
    assert Path(screen.outputs.currentData()).name == 'original_split' and screen.open_button.text() == 'Open folder'
    assert settings.value('split/mode') == 'ranges' and settings.value('split/ranges') == '1-2, 3'
    window.close()
