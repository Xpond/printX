import logging
import os
import re
import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.webp', '.heic', '.heif'}
INPUT_EXTENSIONS = IMAGE_EXTENSIONS | {'.pdf'}


class Cancelled(Exception):
    pass


class JobError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def check_cancel(cancel):
    if cancel.is_set():
        raise Cancelled()


def output_directory(path, options):
    return Path(options.get('output_folder') or Path(path).parent)


def pdf_name(paths, typed=''):
    """Name for the combined PDF: the typed name made safe for Windows, else the default."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', typed).strip().rstrip('. ')
    if name.lower().endswith('.pdf'):
        name = name[:-4].rstrip('. ')
    return name or f"{Path(paths[0]).stem}_{'combined' if len(paths) > 1 else 'made'}"


def stage_directory(directory, token):
    return Path(directory) / f'.printshop-{token}'


def staging(path, options):
    """This job's private folder beside the file's output, where results are finished before publishing."""
    stage = stage_directory(output_directory(path, options), options['token'])
    stage.mkdir(parents=True, exist_ok=True)
    return stage


def each_file(paths, options, progress, cancel, one):
    """Run one(index, path) on each file in turn, skipping failures with a message; always removes staging."""
    outputs = []
    try:
        for index, value in enumerate(paths):
            check_cancel(cancel)
            path = Path(value)
            progress('progress', {'index': index, 'total': len(paths), 'path': str(path)})
            try:
                outputs.append(one(index, path))
            except Cancelled:
                raise
            except Exception as error:
                if not isinstance(error, JobError):
                    logging.exception('Could not process %s', path)
                progress('skipped', {'path': str(path), 'code': error_code(error)})
            progress('progress', {'index': index + 1, 'total': len(paths), 'path': str(path)})
        if not outputs:
            raise JobError('no_outputs')
        return outputs
    finally:
        for stage in {stage_directory(output_directory(path, options), options['token']) for path in paths}:
            shutil.rmtree(stage, ignore_errors=True)


def publish(temp, destination):
    """Publish a complete file atomically without replacing an existing name."""
    destination = Path(destination)
    for number in range(1, 100000):
        target = destination if number == 1 else destination.with_stem(f'{destination.stem} ({number})')
        try:
            if os.name == 'nt':
                os.rename(temp, target)  # Windows rename refuses existing destinations.
            else:
                os.link(temp, target)
                Path(temp).unlink()
            return str(target)
        except FileExistsError:
            continue
    raise JobError('names_exhausted')


def publish_folder(temp, destination):
    """Publish a finished folder under a name not yet taken; only another app racing for it could clash."""
    for number in range(1, 100000):
        target = Path(destination if number == 1 else f'{destination} ({number})')
        if not target.exists():
            os.rename(temp, target)
            return str(target)
    raise JobError('names_exhausted')


def error_code(error):
    if isinstance(error, JobError):
        return error.code
    if isinstance(error, MemoryError):
        return 'memory'
    if isinstance(error, PermissionError):
        return 'permission'
    if isinstance(error, FileNotFoundError):
        return 'missing'
    if isinstance(error, OSError) and error.errno == 28:
        return 'disk_full'
    return 'corrupt'
