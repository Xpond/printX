"""Classic enlargement for print: Lanczos with a light unsharp mask, or whole-number nearest neighbour."""
import logging
import math
import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path

from core.files import (IMAGE_EXTENSIONS, Cancelled, JobError, check_cancel, error_code,
                        output_directory, publish, stage_directory)

MM = 1 / 25.4
PAPERS = {  # Inches, in either orientation.
    'A6': (105 * MM, 148 * MM), 'A5': (148 * MM, 210 * MM), 'A4': (210 * MM, 297 * MM),
    'A3': (297 * MM, 420 * MM), 'A2': (420 * MM, 594 * MM), 'A1': (594 * MM, 841 * MM),
    'A0': (841 * MM, 1189 * MM), '4x6': (4, 6), '5x7': (5, 7), '8x10': (8, 10),
    'Letter': (8.5, 11), 'Legal': (8.5, 14), 'Tabloid': (11, 17)}
FORMATS = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.tif': 'TIFF', '.tiff': 'TIFF', '.bmp': 'BMP'}
SAVE = {'JPEG': {'quality': 95, 'subsampling': 0}, 'TIFF': {'compression': 'tiff_lzw'}, 'PNG': {}, 'BMP': {}}
BUDGET = 512 * 2 ** 20  # Bytes of images processed at once; a file needing more runs alone.
STRIP = 256  # Output rows per step, so a huge result needs one full-size buffer instead of three.


def factor(size, options):
    """How much an image of this pixel size grows: a fixed factor, or to fit the paper turned its way."""
    if options['size'] != 'fit':
        return float(options['size'])
    short, long = sorted(options['paper'])
    scale = min(long * options['dpi'] / max(size), short * options['dpi'] / min(size))
    return math.ceil(round(scale, 6)) if options.get('hard') and scale > 1 else scale


def grade(scale, hard=False):
    """Classic upscaling looks nearly identical up to 2×, clean but soft up to 4×, and blurry beyond."""
    if scale <= 1:
        return 'big'
    if hard or round(scale, 1) <= 2:
        return 'sharp'
    return 'soft' if round(scale, 1) <= 4 else 'blurry'


def sharpener(scale, level):
    """A small radius at every scale: wider ones draw halos around edges instead of adding detail."""
    from PIL import ImageFilter
    percent = {'light': 70, 'strong': 140}.get(level)
    return percent and ImageFilter.UnsharpMask(min(0.6 + 0.1 * scale, 1.2), percent, 2)


def prepare(image, hard):
    """Pillow silently uses nearest neighbour for palette and 1-bit images, so convert those first."""
    if hard or image.mode in ('L', 'LA', 'RGB', 'RGBA', 'CMYK'):
        return image
    if image.mode.startswith('I'):  # 16-bit greyscale: convert() would clip it, so scale it to 8 bits.
        return image.convert('I').point(lambda value: value / 257 + .5).convert('L')
    if image.mode == '1':
        return image.convert('L')
    return image.convert('RGBA' if 'A' in image.mode or 'transparency' in image.info else 'RGB')


def output_format(path, image):
    """Match the input; HEIC and WEBP become JPG, which every print app opens. Transparency needs PNG."""
    suffix = Path(path).suffix
    kind = FORMATS.get(suffix.lower())
    if kind in (None, 'JPEG', 'BMP') and ('A' in image.mode or 'transparency' in image.info):
        return 'PNG', '.png'
    return (kind, suffix) if kind else ('JPEG', '.jpg')


def enlarge(image, size, sharpen, report):
    """Lanczos in strips of output rows, like one resize up to rounding; sharpening overlaps the strips."""
    from PIL import Image
    mode = image.mode
    premultiplied = {'RGBA': 'RGBa', 'LA': 'La'}.get(mode)  # Keeps transparent edges free of fringes.
    source = image.convert(premultiplied) if premultiplied else image
    result = Image.new(mode, size)
    margin = math.ceil(3 * sharpen.radius) + 2 if sharpen else 0
    scale = size[1] / image.height
    for top in range(0, size[1], STRIP):
        bottom = min(top + STRIP, size[1])
        first, last = max(top - margin, 0), min(bottom + margin, size[1])
        strip = source.resize((size[0], last - first), Image.LANCZOS,
                              box=(0, first / scale, image.width, last / scale))
        if sharpen:
            strip = strip.filter(sharpen)
        if premultiplied:
            strip = strip.convert(mode)
        result.paste(strip.crop((0, top - first, size[0], bottom - first)), (0, top))
        report(bottom / size[1])
    return result


class Budget:
    """Image memory shared by files processed in parallel; a file bigger than the budget runs alone."""
    def __init__(self, total):
        self.total = self.free = total
        self.changed = threading.Condition()

    @contextmanager
    def hold(self, amount):
        amount = min(amount, self.total)
        with self.changed:
            self.changed.wait_for(lambda: self.free >= amount)
            self.free -= amount
        try:
            yield
        finally:
            with self.changed:
                self.free += amount
                self.changed.notify_all()


def upscale(paths, options, progress, cancel):
    """Upscale images next to their originals, in parallel threads (Pillow releases the GIL)."""
    from PIL import Image, ImageOps
    from core.images import pillow_open
    done, stages, budget = [0.0] * len(paths), set(), Budget(BUDGET)

    def one(index, path, report):
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            raise JobError('not_image')
        with pillow_open(path) as source:
            scale = factor(source.size, options)
            if scale <= 1:
                raise JobError('big_enough')
            with budget.hold(4 * source.width * source.height * (2 + scale * scale)):
                report(0)
                if FORMATS.get(path.suffix.lower()) == 'TIFF' and getattr(source, 'n_frames', 1) > 1:
                    progress('notice', {'path': str(path), 'code': 'first_page'})
                icc = source.info.get('icc_profile')
                ImageOps.exif_transpose(source, in_place=True)
                image = prepare(source, options.get('hard'))
                size = (round(image.width * scale), round(image.height * scale))
                if options.get('hard'):
                    image = image.resize(size, Image.NEAREST)
                else:
                    image = enlarge(image, size, sharpener(scale, options.get('sharpen')), report)
                kind, suffix = output_format(path, image)
                directory = output_directory(path, options)
                stage = stage_directory(directory, options['token'])
                stage.mkdir(parents=True, exist_ok=True)
                stages.add(stage)
                temp = stage / f'{index}{suffix}'
                image.save(temp, kind, dpi=(options['dpi'],) * 2, **SAVE[kind],
                           **({'icc_profile': icc} if icc else {}))
        check_cancel(cancel)
        return publish(temp, directory / f'{path.stem}_upscaled{suffix}')

    def run(index):
        path = Path(paths[index])

        def report(fraction):
            check_cancel(cancel)
            done[index] = fraction
            progress('progress', {'index': sum(done), 'total': len(paths), 'path': str(path)})

        try:
            output = one(index, path, report)
            progress('output', {'path': output})
            return output
        except Cancelled:
            raise
        except Exception as error:
            if not isinstance(error, JobError):
                logging.exception('Could not upscale %s', path)
            progress('skipped', {'path': str(path), 'code': error_code(error)})
        finally:
            done[index] = 1.0

    try:
        with ThreadPoolExecutor(max(1, min((os.cpu_count() or 2) - 1, len(paths)))) as pool:
            outputs = [output for output in pool.map(run, range(len(paths))) if output]
        if not outputs:
            raise JobError('no_outputs')
        return outputs
    finally:
        for stage in stages:
            shutil.rmtree(stage, ignore_errors=True)
