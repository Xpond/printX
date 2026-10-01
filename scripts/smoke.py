"""Exercise the actual GUI and spawned worker, also from a frozen Windows build."""
import json
import time
from pathlib import Path
from PySide6.QtCore import QTimer


def run_smoke(app, window, destination):
    from PIL import Image
    from ui.theme import apply_theme
    destination = Path(destination).absolute()
    destination.mkdir(parents=True, exist_ok=True)
    source = destination / 'café sample 🖨.jpg'
    scan = destination / 'large scan 🖨.pdf'
    page = Image.effect_noise((1500, 1000), 40).convert('RGB')
    page.save(scan, save_all=True, append_images=[page, page], resolution=500, quality=95)  # Three JPEG pages.
    Image.new('RGB', (900, 600), '#288d99').save(source, quality=95, dpi=(300, 300))
    window.settings.setValue('output_folder', str(destination))
    started = time.monotonic()
    beats = []
    heartbeat = QTimer(window)
    heartbeat.setInterval(10)
    heartbeat.timeout.connect(lambda: beats.append(time.monotonic()))
    heartbeat.start()

    def snapshot(name):
        app.processEvents()
        window.grab().save(str(destination / f'{name}.png'))

    def prepare():
        apply_theme(app, False)
        snapshot('01-home-light')
        window.show_screen(window.preferences)
        snapshot('02-settings-light')
        window.show_screen(window.make)
        snapshot('03-make-empty-light')
        window.make.add_files([str(source)])
        QTimer.singleShot(800, begin)

    def begin():
        snapshot('04-make-files-light')
        window.make.start()
        snapshot('05-progress-light')

    def finished(kind, data):
        if kind == 'done':
            QTimer.singleShot(100, verify)
        elif kind == 'failed':
            (destination / 'failure.json').write_text(json.dumps({'error': data}))
            window.close()
            app.exit(1)

    def verify():
        import pymupdf
        output = window.make.outputs.currentData()
        with pymupdf.open(output) as doc:
            assert doc.page_count == 1
            assert doc.extract_image(doc[0].get_images()[0][0])['image'] == source.read_bytes()
        snapshot('06-success-light')
        window.show_screen(window.upscale)
        window.upscale.add_files([str(source)])
        QTimer.singleShot(800, upscale)

    def upscale():
        snapshot('07-upscale-files-light')
        window.upscale.start()

    def upscaled(kind, data):
        if kind == 'done':
            QTimer.singleShot(100, compress)
        elif kind == 'failed':
            finished(kind, data)

    def compress():
        output = window.upscale.outputs.currentData()
        with Image.open(output) as image:
            assert image.width > 3000 and round(image.info['dpi'][0]) == 300
        snapshot('08-upscale-done-light')
        window.show_screen(window.compress)
        window.compress.add_files([str(scan)])
        QTimer.singleShot(800, lambda: (snapshot('09-compress-files-light'), window.compress.start()))

    def compressed(kind, data):
        if kind == 'done':
            QTimer.singleShot(100, split)
        elif kind == 'failed':
            finished(kind, data)

    def split():
        import pymupdf
        output = window.compress.outputs.currentData()
        with pymupdf.open(output) as doc:
            assert doc.page_count == 3 and Path(output).stat().st_size < scan.stat().st_size / 4
        snapshot('10-compress-done-light')
        window.show_screen(window.split)
        window.split.add_files([str(scan)])
        QTimer.singleShot(800, window.split.start)

    def split_finished(kind, data):
        if kind == 'done':
            QTimer.singleShot(100, finish)
        elif kind == 'failed':
            finished(kind, data)

    def finish():
        output = window.split.outputs.currentData()
        assert len(list(Path(output).glob('*_page_*.pdf'))) == 3
        snapshot('11-split-done-light')
        apply_theme(app, True)
        snapshot('12-split-done-dark')
        window.show_screen(window.compress)
        snapshot('13-compress-done-dark')
        window.show_screen(window.upscale)
        snapshot('14-upscale-done-dark')
        window.show_screen(window.make)
        snapshot('15-success-dark')
        window.show_screen(window.home)
        snapshot('16-home-dark')
        window.show_screen(window.preferences)
        snapshot('17-settings-dark')
        window.show_screen(window.remove)
        snapshot('18-remove-dark')
        window.show_screen(window.enhance)
        snapshot('19-enhance-dark')
        report = {'passed': True, 'output': output, 'heartbeat_count': len(beats),
                  'max_heartbeat_gap_seconds': max((b - a for a, b in zip(beats, beats[1:])), default=0),
                  'elapsed_seconds': time.monotonic() - started}
        (destination / 'smoke.json').write_text(json.dumps(report, indent=2))
        window.close()
        app.quit()

    def timeout():
        (destination / 'timeout.txt').write_text('GUI smoke test exceeded 60 seconds.')
        for tool in window.tools.values():
            tool.jobs.shutdown()
            tool.model.thumbnails.shutdown()
        app.exit(1)

    window.make.jobs.event.connect(finished)
    window.upscale.jobs.event.connect(upscaled)
    window.compress.jobs.event.connect(compressed)
    window.split.jobs.event.connect(split_finished)
    QTimer.singleShot(0, prepare)
    QTimer.singleShot(60000, timeout)
