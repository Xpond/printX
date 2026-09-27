import threading
import uuid
from pathlib import Path

import pymupdf
from core.compress import compress
from core.files import JobError


def run(paths, level='recommended', passwords=()):
    events, passwords = [], iter(passwords)

    def progress(kind, data):
        events.append((kind, data))
        return next(passwords) if kind == 'password' else None

    try:
        outputs = compress([str(p) for p in paths], {'token': uuid.uuid4().hex, 'level': level},
                           progress, threading.Event())
    except JobError as error:
        outputs = error.code
    return outputs, events


def test_downsamples_page_by_page_and_reports_sizes(photo_pdf, tmp_path):
    source = photo_pdf()
    (output,), events = run([source])
    assert Path(output).name == 'scan 🖨_compressed.pdf'
    with pymupdf.open(output) as doc:
        assert doc.page_count == 2
        assert doc[0].get_images()[0][2] == 875  # 5.8 inches at 150 DPI.
    saved = next(data for kind, data in events if kind == 'output')
    assert saved['before'] == source.stat().st_size
    assert saved['after'] == Path(output).stat().st_size < saved['before'] / 4
    assert any(data['index'] % 1 for kind, data in events if kind == 'progress')
    assert not list(tmp_path.glob('.printshop-*'))


def test_every_level_keeps_cmyk_and_print_keeps_300_dpi(photo_pdf):
    source = photo_pdf('flyer.pdf', 'CMYK', pages=1)
    widths = {}
    for level in ('smallest', 'recommended', 'print'):
        (output,), _ = run([source], level)
        with pymupdf.open(output) as doc:
            xref, _, widths[level] = doc[0].get_images()[0][:3]
            assert doc.extract_image(xref)['colorspace'] == 4
    assert widths == {'smallest': 583, 'recommended': 875, 'print': 1750}


def test_already_optimized_keeps_the_original(pdf):
    outputs, events = run([pdf], 'print')
    assert outputs == 'no_outputs'
    assert [data['code'] for kind, data in events if kind == 'skipped'] == ['optimized']
    assert list(pdf.parent.glob('*.pdf')) == [pdf]


def test_password_and_skipped_files(photo_pdf, tmp_path):
    locked = tmp_path / 'locked 🖨.pdf'
    with pymupdf.open(photo_pdf()) as doc:
        doc.save(locked, encryption=pymupdf.PDF_ENCRYPT_AES_256, user_pw='secret', owner_pw='owner')
    broken = tmp_path / 'broken.pdf'
    broken.write_bytes(b'not a PDF')
    outputs, events = run([locked, tmp_path / 'notes.txt', broken, tmp_path / 'missing.pdf'],
                          passwords=['wrong', 'secret'])
    assert [kind for kind, _ in events].count('password') == 2
    with pymupdf.open(outputs[0]) as doc:
        assert not doc.needs_pass and doc.page_count == 2
    assert [data['code'] for kind, data in events if kind == 'skipped'] == ['not_pdf', 'corrupt', 'missing']
