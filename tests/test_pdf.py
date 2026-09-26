import threading
import uuid
from pathlib import Path

import pymupdf
import pytest
from PIL import Image
from core.files import Cancelled, JobError, publish
from core.pdf_tools import make_pdf


def run(paths, **options):
    return make_pdf(paths, {'token': uuid.uuid4().hex, **options}, lambda *args: None, threading.Event())


def test_combined_order_page_sizes_rotation_and_lossless_jpeg(photo, pdf):
    output, = run([pdf, photo], paper='A4')
    with pymupdf.open(output) as doc:
        assert doc.page_count == 4
        assert 'Original page 1' in doc[0].get_text()
        assert 'Original page 3' in doc[2].get_text()
        assert doc[0].rect.width == 300
        assert doc[1].rotation == 90
        assert doc[-1].rect.width == pytest.approx(841.8898, abs=.1)
        xref = doc[-1].get_images()[0][0]
        assert doc.extract_image(xref)['image'] == photo.read_bytes()


def test_native_image_size_and_margins(photo):
    output, = run([photo], paper='image')
    with pymupdf.open(output) as doc:
        assert doc[0].rect.width == pytest.approx(144, abs=.1)
        assert doc[0].rect.height == pytest.approx(96, abs=.1)
    output, = run([photo], paper='Letter', margin='large')
    with pymupdf.open(output) as doc:
        page = doc[0]
        assert page.rect.width == 792
        rectangle = page.get_image_rects(page.get_images()[0][0])[0]
        assert rectangle.x0 >= 28.3
        assert rectangle.y0 >= 28.3


def test_separate_unique_names_and_fixed_output(photo, pdf, tmp_path):
    folder = tmp_path / 'résultats 🖨'
    first = run([photo, pdf], combined=False, output_folder=str(folder))
    original_bytes = [Path(p).read_bytes() for p in first]
    second = run([photo, pdf], combined=False, output_folder=str(folder))
    assert all('(2)' in p for p in second)
    assert all(Path(p).parent == folder for p in first + second)
    assert [Path(p).read_bytes() for p in first] == original_bytes
    assert not list(folder.glob('.printshop-*'))


def test_typed_combined_name_is_made_safe(photo, pdf):
    output, = run([photo, pdf], name=' Client: Smith.pdf ')
    assert Path(output).name == 'Client Smith.pdf'
    output, = run([photo, pdf], name=' ?* ')
    assert Path(output).name == f'{photo.stem}_combined.pdf'


def test_transparent_palette_multiframe_and_exif(tmp_path):
    rgba = Image.new('RGBA', (80, 40), (255, 0, 0, 0))
    png = tmp_path / 'transparent.png'
    rgba.save(png)
    palette = tmp_path / 'palette.png'
    rgba.convert('P').save(palette)
    tiff = tmp_path / 'two.tiff'
    Image.new('RGB', (40, 80), 'blue').save(tiff, save_all=True,
        append_images=[Image.new('RGB', (60, 80), 'green')])
    exif = Image.Exif()
    exif[274] = 6
    rotated = tmp_path / 'rotated.jpg'
    Image.new('RGB', (80, 40), 'red').save(rotated, exif=exif)
    output, = run([png, palette, tiff, rotated], paper='A4')
    with pymupdf.open(output) as doc:
        assert len(doc) == 5
        assert doc[-1].rect.height > doc[-1].rect.width
        assert len(doc[0].get_pixmap().samples) > 0


def test_heic_and_cmyk(tmp_path):
    from pillow_heif import register_heif_opener
    register_heif_opener()
    heic = tmp_path / 'iphone.heic'
    Image.new('RGB', (100, 70), 'green').save(heic)
    cmyk = tmp_path / 'print.jpg'
    Image.new('CMYK', (100, 70), (120, 50, 0, 0)).save(cmyk)
    output, = run([heic, cmyk])
    with pymupdf.open(output) as doc:
        assert len(doc) == 2
        assert doc[1].get_images()[0][5] == 'DeviceCMYK'


def test_corrupt_and_missing_skipped_without_losing_good_files(photo, tmp_path):
    bad = tmp_path / 'broken.pdf'
    bad.write_bytes(b'not a PDF')
    events = []
    outputs = make_pdf([bad, tmp_path / 'missing.jpg', photo], {'token': 'skip'},
                      lambda *event: events.append(event), threading.Event())
    assert len(outputs) == 1
    assert [payload['code'] for kind, payload in events if kind == 'skipped'] == ['corrupt', 'missing']


def test_password_retry_and_skip(pdf, tmp_path):
    locked = tmp_path / 'locked.pdf'
    with pymupdf.open(pdf) as doc:
        doc.save(locked, encryption=pymupdf.PDF_ENCRYPT_AES_256, user_pw='secret', owner_pw='owner')
    passwords = iter(['wrong', 'secret'])
    outputs = make_pdf([locked], {'token': 'password'},
                      lambda kind, data: next(passwords) if kind == 'password' else None, threading.Event())
    assert len(outputs) == 1
    with pytest.raises(JobError, match='no_outputs'):
        run([locked])


def test_cancel_removes_staging_and_does_not_publish(photo, tmp_path):
    flag = threading.Event()
    def progress(kind, data):
        if kind == 'progress' and data['index'] == 1:
            flag.set()
    with pytest.raises(Cancelled):
        make_pdf([photo], {'token': 'cancel'}, progress, flag)
    assert not list(tmp_path.glob('*_made.pdf'))
    assert not list(tmp_path.glob('.printshop-*'))


def test_atomic_publish_never_overwrites(tmp_path):
    target = tmp_path / 'result.pdf'
    target.write_bytes(b'original')
    temp = tmp_path / 'complete.tmp'
    temp.write_bytes(b'new result')
    output = Path(publish(temp, target))
    assert target.read_bytes() == b'original'
    assert output.name == 'result (2).pdf'
    assert output.read_bytes() == b'new result'


def test_long_paths(photo, tmp_path):
    folder = tmp_path
    for i in range(6):
        folder /= f'folder {i} ' + 'a' * 35
    output, = run([photo], output_folder=str(folder))
    assert len(output) > 260
    assert Path(output).exists()
