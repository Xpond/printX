"""Enhance image: one instruction to the AI image model, applied to one version of a photo."""
from pathlib import Path

from core.files import check_cancel, each_file, output_directory, publish, staging
from core.images import flat_photo
from core.openrouter import edit
from core.upscale import SAVE, output_format

STRETCH = .06  # Muse renders on its own size grid, stretching the whole picture by up to about 3%.


def enhance(paths, options, progress, cancel):
    """Save each new version next to the original, named and formatted after it."""
    from PIL import Image
    original = Path(options['original'])
    prompt = options['prompt'].strip() + '\nKeep everything else exactly as it is.'

    def one(index, path):
        photo, keep = flat_photo(path)
        keep.pop('icc_profile', None)  # The model answers in plain sRGB.
        answer = edit(photo, prompt, options['key'], options['model'])[0].convert('RGB')
        check_cancel(cancel)
        height = round(answer.width * photo.height / photo.width)
        if abs(answer.height / height - 1) < STRETCH:  # Undo the stretch; a bigger change was asked for.
            answer = answer.resize((answer.width, height), Image.LANCZOS)
        kind, suffix = output_format(original, answer)
        temp = staging(path, options) / f'{index}{suffix}'
        answer.save(temp, kind, **SAVE[kind], **keep)
        check_cancel(cancel)
        output = publish(temp, output_directory(path, options) / f'{original.stem}_enhanced{suffix}')
        progress('output', {'path': output})
        return output

    return each_file(paths, options, progress, cancel, one)
