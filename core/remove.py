"""Remove the background, or anything described, with an AI layer model, at the original's full size.

The model splits a photo into a cut-out layer and a filled-in base layer at about one megapixel, lined up
with the original. So only its alpha (the cut-out) or the areas it changed (filled in) touch the original;
every other pixel stays as sharp as it was.
"""
from functools import reduce

from core.files import IMAGE_EXTENSIONS, JobError, check_cancel, each_file, output_directory, publish, staging
from core.openrouter import edit
from core.upscale import SAVE, output_format

LAYERS = 'Number of layers: 2. Layer 1: {first}, with a transparent background. Layer 2: {second}.'


def opacity(layer):
    from PIL import ImageStat
    return ImageStat.Stat(layer.getchannel('A')).mean[0]


def changes(before, after):
    """Where the model changed the picture, widened and softened so the patches blend in."""
    from PIL import ImageChops, ImageFilter
    blur = ImageFilter.GaussianBlur(3)  # Fine texture the model redraws slightly differently is not a change.
    difference = ImageChops.difference(before.filter(blur), after.filter(blur)).convert('L')
    return (difference.point(lambda value: 255 if value > 8 else 0)
            .filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(5)))


def remove(paths, options, progress, cancel):
    from PIL import Image, ImageChops, ImageOps
    from core.images import pillow_open
    what, background = options['what'].strip(), options['mode'] == 'background'
    prompt = (LAYERS.format(first=what or 'the main subject', second='the background') if background else
              LAYERS.format(first=what, second=f'everything except {what}'))

    def one(index, path):
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            raise JobError('not_image')
        with pillow_open(path) as source:
            keep = {key: source.info[key] for key in ('dpi', 'icc_profile') if source.info.get(key)}
            if source.mode not in ('RGB', 'RGBA'):
                keep.pop('icc_profile', None)  # A CMYK or grey profile does not describe RGB pixels.
            image = ImageOps.exif_transpose(source).convert('RGBA')
        photo = Image.new('RGB', image.size, 'white')
        photo.paste(image, mask=image.getchannel('A'))
        layers = sorted((layer.convert('RGBA') for layer in edit(photo, prompt, options['key'], options['model'])),
                        key=opacity)  # The solid base comes last, whatever order the model used.
        check_cancel(cancel)
        if background:
            alpha = reduce(ImageChops.lighter, [layer.getchannel('A') for layer in layers[:-1] or layers])
            counts = alpha.histogram()
            if not .005 < sum(counts[:128]) / sum(counts) < .995:
                raise JobError('ai_nothing')
            result = photo.convert('RGBA')
            result.putalpha(alpha.resize(photo.size, Image.LANCZOS))
            kind, suffix, ending = 'PNG', '.png', 'no_background'
        else:
            base = layers[-1].convert('RGB')
            mask = changes(photo.resize(base.size, Image.LANCZOS), base)
            if not mask.getbbox():
                raise JobError('ai_nothing')
            result = Image.composite(base.resize(photo.size, Image.LANCZOS), photo,
                                     mask.resize(photo.size, Image.LANCZOS))
            (kind, suffix), ending = output_format(path, result), 'edited'
        temp = staging(path, options) / f'{index}{suffix}'
        result.save(temp, kind, **SAVE[kind], **keep)
        check_cancel(cancel)
        output = publish(temp, output_directory(path, options) / f'{path.stem}_{ending}{suffix}')
        progress('output', {'path': output})
        return output

    return each_file(paths, options, progress, cancel, one)
