import threading
import uuid
from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageCms, ImageDraw, JpegImagePlugin
from core.files import Cancelled, JobError
from core.thumbnails import thumbnail
from core.upscale import PAPERS, Budget, enlarge, factor, grade, sharpener, upscale


def run(paths, events=None, **options):
    options = {'token': uuid.uuid4().hex, 'size': '2', 'paper': PAPERS['A4'], 'dpi': 300, 'sharpen': 'light',
               'hard': False, **options}
    return upscale(paths, options, lambda *event: events is not None and events.append(event), threading.Event())


def test_fit_print_size_turns_the_paper_and_grades():
    options = {'size': 'fit', 'paper': PAPERS['A4'], 'dpi': 300}
    assert factor((1600, 1000), options) == pytest.approx(297 / 25.4 * 300 / 1600)
    assert factor((1000, 1600), options) == factor((1600, 1000), options)
    assert grade(factor((4032, 3024), options)) == 'big'
    assert factor((1200, 1000), dict(options, hard=True)) == 3  # Whole numbers keep pixels square.
    assert factor((600, 400), {'size': '3'}) == 3
    assert [grade(scale) for scale in (1.9, 2.04, 3.5, 4.3)] == ['sharp', 'sharp', 'soft', 'blurry']
    assert grade(6, hard=True) == 'sharp'


def test_jpeg_rotation_quality_dpi_and_color_profile(tmp_path):
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    exif = Image.Exif()
    exif[274] = 6  # Stored sideways; shown upright.
    path = tmp_path / 'phone photo 🖨.jpg'
    Image.new('RGB', (120, 80), '#318ba0').save(path, quality=80, icc_profile=icc, exif=exif)
    assert thumbnail(path)[2] == (80, 120)  # Tiles show the upright size too.
    output, = run([path])
    with Image.open(output) as result:
        assert Path(output).name == 'phone photo 🖨_upscaled.jpg'
        assert result.size == (160, 240)
        assert result.info['dpi'] == pytest.approx((300, 300))
        assert result.info['icc_profile'] == icc
        assert JpegImagePlugin.get_sampling(result) == 0  # 4:4:4, no colour bleeding.
        assert max(result.quantization[0]) <= 13  # Quality 95.
        assert result.getexif().get(274) is None


def test_transparency_palette_and_one_bit_are_smoothed(tmp_path):
    palette = Image.new('P', (40, 40), 0)
    palette.putpalette([255, 255, 255, 200, 0, 60])
    ImageDraw.Draw(palette).ellipse((8, 8, 32, 32), fill=1)
    logo = tmp_path / 'logo.png'
    palette.save(logo, transparency=0)
    mono = tmp_path / 'line art.bmp'
    Image.new('1', (40, 40), 1).save(mono)
    outputs = run([logo, mono], size='4')
    with Image.open(outputs[0]) as result:
        assert result.mode == 'RGBA' and result.getpixel((0, 0))[3] == 0
        assert len(set(result.getchannel('A').get_flattened_data())) > 2  # Smooth, not blocky, edges.
    with Image.open(outputs[1]) as result:
        assert Path(outputs[1]).suffix == '.bmp' and result.mode == 'L' and result.size == (160, 160)


def test_hard_edges_repeat_pixels_and_keep_the_mode(tmp_path):
    code = Image.new('1', (5, 5), 1)
    code.putpixel((1, 2), 0)
    path = tmp_path / 'qr.png'
    code.save(path)
    output, = run([path], size='3', hard=True)
    with Image.open(output) as result:
        assert result.mode == '1' and result.size == (15, 15)
        assert ImageChops.difference(result.convert('L'), code.resize((15, 15)).convert('L')).getbbox() is None


def test_cmyk_sixteen_bit_heic_webp_and_tiff_pages(tmp_path):
    from pillow_heif import register_heif_opener
    register_heif_opener()
    cmyk = tmp_path / 'print.tif'
    Image.new('CMYK', (30, 20), (10, 80, 0, 5)).save(cmyk, save_all=True,
                                                     append_images=[Image.new('CMYK', (30, 20))])
    scan = tmp_path / 'scan.png'
    Image.new('I;16', (30, 20), 40000).save(scan)
    heic = tmp_path / 'iphone.heic'
    Image.new('RGB', (30, 20), 'green').save(heic)
    webp = tmp_path / 'web.webp'
    Image.new('RGBA', (30, 20), (255, 0, 0, 128)).save(webp)
    events = []
    outputs = run([cmyk, scan, heic, webp], events)
    assert [Path(p).suffix for p in outputs] == ['.tif', '.png', '.jpg', '.png']
    with Image.open(outputs[0]) as result:
        assert result.mode == 'CMYK' and result.info['compression'] == 'tiff_lzw'
    with Image.open(outputs[1]) as result:
        assert result.mode == 'L' and result.getpixel((10, 10)) == 156  # 40000 / 257, not clipped to 255.
    assert ('notice', {'path': str(cmyk), 'code': 'first_page'}) in events


def test_strips_match_one_resize_without_seams():
    source = Image.effect_mandelbrot((301, 211), (-2, -1.2, 1, 1.2), 100).convert('RGB')
    size, fractions = (903, 633), []
    for sharpen in (None, sharpener(3, 'strong')):
        whole = source.resize(size, Image.LANCZOS)
        whole = whole.filter(sharpen) if sharpen else whole
        values = ImageChops.difference(whole, enlarge(source, size, sharpen, fractions.append)).get_flattened_data()
        # Rounding flips a few pixels; strips sharpened without overlap would differ by 30+ levels at seams.
        assert max(max(pixel) for pixel in values) <= 5
        assert sum(any(pixel) for pixel in values) < len(values) / 1000
    assert fractions[-1] == 1 and len(fractions) == 6


def test_skips_keep_the_batch_going_and_names_never_overwrite(tmp_path, photo):
    big = tmp_path / 'big.jpg'
    Image.new('RGB', (1800, 1200)).save(big)
    broken = tmp_path / 'broken.png'
    broken.write_bytes(b'not an image')
    document = tmp_path / 'document.pdf'
    document.write_bytes(b'%PDF-1.7')
    events = []
    options = {'size': 'fit', 'paper': PAPERS['A6'], 'dpi': 150}
    first, = run([big, broken, document, photo], events, **options)
    skipped = {Path(data['path']).name: data['code'] for kind, data in events if kind == 'skipped'}
    assert skipped == {'big.jpg': 'big_enough', 'broken.png': 'corrupt', 'document.pdf': 'not_image'}
    original = Path(first).read_bytes()
    second, = run([photo], **options)
    assert Path(second).name == f'{photo.stem}_upscaled (2).jpg' and Path(first).read_bytes() == original
    with pytest.raises(JobError, match='no_outputs'):
        run([big], **options)


def test_cancel_removes_staging_and_does_not_publish(tmp_path, photo):
    flag = threading.Event()

    def progress(kind, data):
        if kind == 'progress' and data['index'] > 0:
            flag.set()

    with pytest.raises(Cancelled):
        upscale([photo], {'token': 'cancel', 'size': '4', 'dpi': 300, 'sharpen': 'light'}, progress, flag)
    assert not list(tmp_path.glob('*_upscaled*')) and not list(tmp_path.glob('.printshop-*'))


def test_a_file_bigger_than_the_budget_waits_to_run_alone():
    budget, order = Budget(100), []
    second_done = threading.Event()

    def big():
        with budget.hold(500):
            order.append('big')
        second_done.set()

    with budget.hold(60):
        thread = threading.Thread(target=big)
        thread.start()
        assert not second_done.wait(.1)
        order.append('small')
    assert second_done.wait(2)
    thread.join()
    assert order == ['small', 'big']
