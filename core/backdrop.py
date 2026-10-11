"""Put cut-outs on a solid background: the finished picture, at full size, ready to print."""
from core.files import JobError, check_cancel, each_file, output_directory, publish, staging
from core.images import pillow_open
from core.upscale import SAVE


def backdrop(paths, options, progress, cancel):
    """Each path is a transparent cut-out; options give the colour ('#rrggbb') and its name for the file."""
    from PIL import Image

    def one(index, path):
        with pillow_open(path) as source:
            keep = {key: source.info[key] for key in ('dpi', 'icc_profile') if source.info.get(key)}
            cutout = source.convert('RGBA')
        if cutout.getchannel('A').getextrema()[0] == 255:
            raise JobError('not_cutout')
        result = Image.new('RGB', cutout.size, options['color'])
        result.paste(cutout, mask=cutout.getchannel('A'))
        del cutout
        check_cancel(cancel)
        temp = staging(path, options) / f'{index}.jpg'  # Nothing transparent is left: a JPG every print app opens.
        result.save(temp, 'JPEG', **SAVE['JPEG'], **keep)
        check_cancel(cancel)
        stem = path.stem.removesuffix('_no_background')
        output = publish(temp, output_directory(path, options) / f"{stem}_{options['name']}_background.jpg")
        progress('output', {'path': output})
        return output

    return each_file(paths, options, progress, cancel, one)
